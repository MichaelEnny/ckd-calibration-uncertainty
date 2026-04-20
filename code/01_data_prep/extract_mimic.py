"""
MIMIC-IV CKD Cohort Extraction
-------------------------------
Pulls a CKD cohort from MIMIC-IV via Google BigQuery and saves it to
data/external/mimic_ckd_cohort.csv with the same column schema as the
UCI CKD processed dataset.

Requirements
------------
1. PhysioNet credentialed account with MIMIC-IV access granted
2. Google Cloud project with BigQuery API enabled
3. BigQuery access to physionet-data granted (request at PhysioNet)
4. Application Default Credentials set up:
       gcloud auth application-default login
   OR service account key at path set in GOOGLE_APPLICATION_CREDENTIALS

Usage
-----
    python extract_mimic.py --project YOUR_GCP_PROJECT_ID

Column mapping (UCI → MIMIC)
-----------------------------
age    ← patients.anchor_age
bp     ← avg systolic blood pressure (chartevents)
sg     ← NOT available in MIMIC → imputed as NaN
al     ← albumin (labevents itemid 50862)
su     ← glucose (labevents itemid 50931) as proxy
rbc    ← NOT available as categorical → derived from rbcc threshold
pc     ← NOT available in MIMIC → NaN
pcc    ← NOT available in MIMIC → NaN
ba     ← NOT available in MIMIC → NaN
bgr    ← blood glucose (labevents itemid 50931)
bu     ← BUN (labevents itemid 51006)
sc     ← serum creatinine (labevents itemid 50912)
sod    ← sodium (labevents itemid 50983)
pot    ← potassium (labevents itemid 50971)
hemo   ← hemoglobin (labevents itemid 51222)
pcv    ← hematocrit (labevents itemid 51221) as proxy
wbcc   ← WBC (labevents itemid 51301)
rbcc   ← RBC count (labevents itemid 51279)
htn    ← ICD-10 I10 diagnosis flag
dm     ← ICD-10 E11.x diagnosis flag
cad    ← ICD-10 I25.x diagnosis flag
appet  ← NOT available in MIMIC → NaN
pe     ← pedal edema: NOT available → NaN
ane    ← anemia flag: hemoglobin < 12 (F) or < 13.5 (M) g/dL
class  ← eGFR < 60 mL/min/1.73m² = 'ckd', else 'notckd'
         eGFR computed via CKD-EPI equation from creatinine + age + sex
"""

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
import numpy as np

# ── Paths ──────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_FILE  = REPO_ROOT / "data" / "external" / "mimic_ckd_cohort.csv"
README    = REPO_ROOT / "data" / "external" / "README.md"

# ── BigQuery SQL ───────────────────────────────────────────────────────────
SQL = """
WITH

-- 1. Patients with any CKD diagnosis (N18.x) in MIMIC-IV
ckd_patients AS (
  SELECT DISTINCT subject_id
  FROM `physionet-data.mimiciv_hosp.diagnoses_icd`
  WHERE icd_version = 10
    AND REGEXP_CONTAINS(icd_code, r'^N18')
),

-- 2. First hospital admission per patient
first_admit AS (
  SELECT
    p.subject_id,
    a.hadm_id,
    p.gender,
    p.anchor_age                         AS age,
    a.admittime
  FROM `physionet-data.mimiciv_hosp.patients`  p
  JOIN `physionet-data.mimiciv_hosp.admissions` a
    ON p.subject_id = a.subject_id
  JOIN ckd_patients cp
    ON p.subject_id = cp.subject_id
  QUALIFY ROW_NUMBER() OVER (PARTITION BY p.subject_id ORDER BY a.admittime) = 1
),

-- 3. Key lab values (median across the admission)
labs AS (
  SELECT
    l.subject_id,
    l.hadm_id,
    AVG(CASE WHEN l.itemid = 50912 THEN l.valuenum END) AS sc,      -- creatinine
    AVG(CASE WHEN l.itemid = 51006 THEN l.valuenum END) AS bu,      -- BUN
    AVG(CASE WHEN l.itemid = 51222 THEN l.valuenum END) AS hemo,    -- hemoglobin
    AVG(CASE WHEN l.itemid = 50862 THEN l.valuenum END) AS al,      -- albumin
    AVG(CASE WHEN l.itemid = 50971 THEN l.valuenum END) AS pot,     -- potassium
    AVG(CASE WHEN l.itemid = 50983 THEN l.valuenum END) AS sod,     -- sodium
    AVG(CASE WHEN l.itemid = 50931 THEN l.valuenum END) AS bgr,     -- glucose
    AVG(CASE WHEN l.itemid = 51221 THEN l.valuenum END) AS pcv,     -- hematocrit
    AVG(CASE WHEN l.itemid = 51301 THEN l.valuenum END) AS wbcc,    -- WBC
    AVG(CASE WHEN l.itemid = 51279 THEN l.valuenum END) AS rbcc     -- RBC count
  FROM `physionet-data.mimiciv_hosp.labevents` l
  JOIN first_admit fa
    ON l.subject_id = fa.subject_id AND l.hadm_id = fa.hadm_id
  WHERE l.itemid IN (50912, 51006, 51222, 50862, 50971, 50983, 50931, 51221, 51301, 51279)
    AND l.valuenum IS NOT NULL
    AND l.valuenum > 0
  GROUP BY l.subject_id, l.hadm_id
),

-- 4. Blood pressure (systolic avg from chartevents)
bp_vals AS (
  SELECT
    c.subject_id,
    c.hadm_id,
    AVG(c.valuenum) AS bp
  FROM `physionet-data.mimiciv_icu.chartevents` c
  JOIN first_admit fa
    ON c.subject_id = fa.subject_id AND c.hadm_id = fa.hadm_id
  WHERE c.itemid IN (220179, 220050)   -- non-invasive & arterial systolic BP
    AND c.valuenum BETWEEN 60 AND 250
  GROUP BY c.subject_id, c.hadm_id
),

-- 5. Comorbidity flags (hypertension, diabetes, CAD)
comorbidities AS (
  SELECT
    subject_id,
    hadm_id,
    MAX(CASE WHEN REGEXP_CONTAINS(icd_code, r'^I10')  THEN 1 ELSE 0 END) AS htn,
    MAX(CASE WHEN REGEXP_CONTAINS(icd_code, r'^E11')  THEN 1 ELSE 0 END) AS dm,
    MAX(CASE WHEN REGEXP_CONTAINS(icd_code, r'^I25')  THEN 1 ELSE 0 END) AS cad
  FROM `physionet-data.mimiciv_hosp.diagnoses_icd`
  WHERE icd_version = 10
  GROUP BY subject_id, hadm_id
)

-- Final join
SELECT
  fa.subject_id,
  fa.age,
  fa.gender,
  bp.bp,
  l.al,
  l.bgr,
  l.bu,
  l.sc,
  l.sod,
  l.pot,
  l.hemo,
  l.pcv,
  l.wbcc,
  l.rbcc,
  COALESCE(c.htn, 0) AS htn,
  COALESCE(c.dm,  0) AS dm,
  COALESCE(c.cad, 0) AS cad
FROM first_admit fa
LEFT JOIN labs         l  ON fa.subject_id = l.subject_id  AND fa.hadm_id = l.hadm_id
LEFT JOIN bp_vals      bp ON fa.subject_id = bp.subject_id AND fa.hadm_id = bp.hadm_id
LEFT JOIN comorbidities c ON fa.subject_id = c.subject_id  AND fa.hadm_id = c.hadm_id
WHERE l.sc IS NOT NULL   -- must have creatinine to compute eGFR
"""


def ckd_epi_egfr(creatinine: pd.Series, age: pd.Series, sex: pd.Series) -> pd.Series:
    """CKD-EPI 2021 equation (race-free). Returns eGFR mL/min/1.73m²."""
    kappa = np.where(sex.str.upper() == 'F', 0.7, 0.9)
    alpha = np.where(sex.str.upper() == 'F', -0.241, -0.302)
    ratio = creatinine / kappa
    egfr = (
        142
        * np.minimum(ratio, 1) ** alpha
        * np.maximum(ratio, 1) ** (-1.200)
        * 0.9938 ** age
        * np.where(sex.str.upper() == 'F', 1.012, 1.0)
    )
    return pd.Series(egfr, index=creatinine.index)


def harmonize_to_uci_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Map MIMIC columns to UCI CKD column names and encoding."""
    out = pd.DataFrame()

    out['age']   = df['age']
    out['bp']    = df['bp']
    out['sg']    = np.nan                          # not available in MIMIC
    out['al']    = df['al']
    out['su']    = np.nan                          # no urine sugar in MIMIC labs
    out['rbc']   = np.where(df['rbcc'] >= 3.8, 'normal', 'abnormal')  # rough threshold
    out['pc']    = np.nan
    out['pcc']   = np.nan
    out['ba']    = np.nan
    out['bgr']   = df['bgr']
    out['bu']    = df['bu']
    out['sc']    = df['sc']
    out['sod']   = df['sod']
    out['pot']   = df['pot']
    out['hemo']  = df['hemo']
    out['pcv']   = df['pcv']
    out['wbcc']  = df['wbcc']
    out['rbcc']  = df['rbcc']
    out['htn']   = df['htn'].map({1: 'yes', 0: 'no'})
    out['dm']    = df['dm'].map({1: 'yes',  0: 'no'})
    out['cad']   = df['cad'].map({1: 'yes', 0: 'no'})
    out['appet'] = np.nan
    out['pe']    = np.nan
    # Anemia flag: Hgb < 12 for F, < 13.5 for M
    anemia_thresh = np.where(df['gender'].str.upper() == 'F', 12.0, 13.5)
    out['ane']   = np.where(df['hemo'] < anemia_thresh, 'yes', 'no')

    # Compute eGFR and assign binary CKD label
    egfr = ckd_epi_egfr(df['sc'], df['age'], df['gender'])
    out['egfr']  = egfr.round(1)               # keep for reference, not in UCI schema
    out['class'] = np.where(egfr < 60, 'ckd', 'notckd')

    return out


def generate_missingness_report(df: pd.DataFrame) -> pd.DataFrame:
    report = pd.DataFrame({
        'column': df.columns,
        'n_missing': df.isnull().sum().values,
        'pct_missing': (df.isnull().mean() * 100).round(1).values,
        'dtype': df.dtypes.astype(str).values
    })
    return report


def write_readme(df: pd.DataFrame, report: pd.DataFrame, project: str):
    ckd_n     = (df['class'] == 'ckd').sum()
    notckd_n  = (df['class'] == 'notckd').sum()
    total     = len(df)
    README.write_text(f"""# MIMIC-IV CKD Cohort — External Validation Set

Generated : {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
GCP Project: {project}
Source     : physionet-data.mimiciv_hosp + mimiciv_icu (BigQuery)

## Cohort Definition
- Inclusion: any ICD-10 N18.x (CKD stages 1–5) diagnosis during hospitalization
- Index event: first hospital admission
- Exclusion: no serum creatinine measurement

## Size
| Split    | N      |
|----------|--------|
| CKD      | {ckd_n:,}   |
| Not CKD  | {notckd_n:,}  |
| **Total**| **{total:,}** |

## CKD Label
Binary label derived from CKD-EPI 2021 eGFR equation (race-free):
- **CKD** : eGFR < 60 mL/min/1.73m²
- **Not CKD**: eGFR ≥ 60 mL/min/1.73m²

## Schema Alignment with UCI CKD
Columns match UCI processed schema (25 cols). Columns unavailable in
MIMIC (sg, su, pc, pcc, ba, appet, pe) are retained as NaN and handled
by imputation in Task 2.4.

## Missingness Summary
{report.to_markdown(index=False)}

## Ethics
MIMIC-IV data used under PhysioNet credentialed access agreement.
Raw data not redistributed. Extraction SQL in code/01_data_prep/extract_mimic.py.
""")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True,
                        help='Google Cloud project ID for BigQuery billing')
    args = parser.parse_args()

    print(f"[1/4] Connecting to BigQuery (project={args.project}) ...")
    from google.cloud import bigquery
    client = bigquery.Client(project=args.project)

    print("[2/4] Running extraction query (may take 1–3 min) ...")
    df_raw = client.query(SQL).to_dataframe()
    print(f"      Raw rows returned: {len(df_raw):,}")

    if len(df_raw) < 500:
        print(f"WARNING: only {len(df_raw)} rows returned — expected ≥500. "
              "Check that MIMIC-IV access is granted on PhysioNet.")

    print("[3/4] Harmonizing to UCI schema and computing eGFR labels ...")
    df = harmonize_to_uci_schema(df_raw)
    print(f"      CKD : {(df['class']=='ckd').sum()}")
    print(f"      Not CKD: {(df['class']=='notckd').sum()}")

    print("[4/4] Saving outputs ...")
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)
    print(f"      Saved cohort → {OUT_FILE}")

    report = generate_missingness_report(df)
    report.to_csv(OUT_FILE.parent / "mimic_missingness_report.csv", index=False)
    print(f"      Saved missingness report → {OUT_FILE.parent / 'mimic_missingness_report.csv'}")

    write_readme(df, report, args.project)
    print(f"      Saved README → {README}")

    print("\nDone.")
    print(f"  Rows  : {len(df)}")
    print(f"  Cols  : {len(df.columns)}")
    assert len(df) >= 500, "Cohort smaller than 500 — review inclusion criteria"
    assert OUT_FILE.exists()


if __name__ == "__main__":
    main()
