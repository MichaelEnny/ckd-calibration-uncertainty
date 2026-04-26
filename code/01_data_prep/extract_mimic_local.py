"""
Task 2.2 (Demo Mode) — MIMIC-IV Local CSV Extraction
-----------------------------------------------------
Reads the MIMIC-IV Clinical Database Demo (v2.2) directly from local
gzipped CSV files instead of BigQuery. Produces the same output schema
as extract_mimic.py so all downstream code is identical.

Usage
-----
    python extract_mimic_local.py [--demo-dir PATH]

Default demo-dir: data/external/mimic-iv-clinical-database-demo-2.2

Column mapping (UCI → MIMIC)
-----------------------------
age    ← patients.anchor_age
bp     ← avg systolic BP (chartevents itemids 220179, 220050)
sg     ← NOT available → NaN
al     ← albumin       (labevents itemid 50862)
su     ← NOT available (no urine sugar) → NaN
rbc    ← derived from rbcc threshold
pc     ← NOT available → NaN
pcc    ← NOT available → NaN
ba     ← NOT available → NaN
bgr    ← blood glucose (labevents itemid 50931)
bu     ← BUN           (labevents itemid 51006)
sc     ← creatinine    (labevents itemid 50912)
sod    ← sodium        (labevents itemid 50983)
pot    ← potassium     (labevents itemid 50971)
hemo   ← hemoglobin    (labevents itemid 51222)
pcv    ← hematocrit    (labevents itemid 51221)
wbcc   ← WBC           (labevents itemid 51301)
rbcc   ← RBC count     (labevents itemid 51279)
htn    ← ICD-10 I10 flag
dm     ← ICD-10 E11.x flag
cad    ← ICD-10 I25.x flag
appet  ← NOT available → NaN
pe     ← NOT available → NaN
ane    ← derived: Hgb < 12 (F) or < 13.5 (M)
class  ← eGFR < 60 = 'ckd', else 'notckd'  (CKD-EPI 2021, race-free)

Note on cohort strategy
-----------------------
Unlike extract_mimic.py (which filters on N18.x ICD codes first), this
script labels ALL patients whose creatinine is available using the
eGFR threshold. This maximises the demo cohort to 97 patients
(23 CKD / 74 not-CKD) rather than the 15 who carry an N18.x code.
This is intentional: the paper uses eGFR as the ground-truth CKD
definition, not administrative coding.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).resolve().parents[2]
DEFAULT_DEMO = REPO_ROOT / "data" / "external" / "mimic-iv-clinical-database-demo-2.2"
OUT_FILE     = REPO_ROOT / "data" / "external" / "mimic_ckd_cohort.csv"
README_FILE  = REPO_ROOT / "data" / "external" / "README.md"

# Lab item IDs (MIMIC-IV standard)
LAB_ITEMS = {
    50912: 'sc',    # creatinine
    51006: 'bu',    # BUN
    51222: 'hemo',  # hemoglobin
    50862: 'al',    # albumin
    50971: 'pot',   # potassium
    50983: 'sod',   # sodium
    50931: 'bgr',   # glucose
    51221: 'pcv',   # hematocrit
    51301: 'wbcc',  # WBC
    51279: 'rbcc',  # RBC count
}

BP_ITEM_IDS = [220179, 220050]   # non-invasive + arterial systolic BP


# ── CKD-EPI 2021 (race-free) ───────────────────────────────────────────────
def ckd_epi_egfr(sc: pd.Series, age: pd.Series, sex: pd.Series) -> pd.Series:
    """Returns eGFR mL/min/1.73m² using CKD-EPI 2021 equation."""
    kappa = np.where(sex.str.upper() == 'F', 0.7, 0.9)
    alpha = np.where(sex.str.upper() == 'F', -0.241, -0.302)
    ratio = sc.values / kappa
    egfr = (
        142
        * np.minimum(ratio, 1) ** alpha
        * np.maximum(ratio, 1) ** (-1.200)
        * 0.9938 ** age.values
        * np.where(sex.str.upper() == 'F', 1.012, 1.0)
    )
    return pd.Series(egfr, index=sc.index)


# ── Extraction helpers ─────────────────────────────────────────────────────
def load_first_admissions(demo_dir: Path) -> pd.DataFrame:
    patients = pd.read_csv(demo_dir / "hosp" / "patients.csv.gz",
                           usecols=['subject_id', 'gender', 'anchor_age'])
    patients = patients.rename(columns={'anchor_age': 'age'})
    admissions = pd.read_csv(demo_dir / "hosp" / "admissions.csv.gz",
                             usecols=['subject_id', 'hadm_id', 'admittime'])
    admissions['admittime'] = pd.to_datetime(admissions['admittime'])
    first = (admissions.sort_values('admittime')
                        .groupby('subject_id')
                        .first()
                        .reset_index()[['subject_id', 'hadm_id']])
    return first.merge(patients, on='subject_id')


def load_labs(demo_dir: Path, hadm_ids: pd.Series) -> pd.DataFrame:
    labs = pd.read_csv(demo_dir / "hosp" / "labevents.csv.gz",
                       usecols=['subject_id', 'hadm_id', 'itemid', 'valuenum'])
    labs = labs[
        labs['itemid'].isin(LAB_ITEMS.keys()) &
        labs['hadm_id'].isin(hadm_ids) &
        labs['valuenum'].notna() &
        (labs['valuenum'] > 0)
    ]
    # Average per patient-admission
    pivot = (labs.groupby(['subject_id', 'hadm_id', 'itemid'])['valuenum']
                 .mean()
                 .reset_index()
                 .pivot_table(index=['subject_id', 'hadm_id'],
                              columns='itemid', values='valuenum')
                 .reset_index())
    pivot.columns = (['subject_id', 'hadm_id'] +
                     [LAB_ITEMS[c] for c in pivot.columns[2:]])
    return pivot


def load_bp(demo_dir: Path, hadm_ids: pd.Series, subject_ids: pd.Series) -> pd.DataFrame:
    # Primary source: ICU chartevents (inpatient systolic BP)
    chart = pd.read_csv(demo_dir / "icu" / "chartevents.csv.gz",
                        usecols=['subject_id', 'hadm_id', 'itemid', 'valuenum'])
    bp_icu = (chart[
        chart['itemid'].isin(BP_ITEM_IDS) &
        chart['hadm_id'].isin(hadm_ids) &
        chart['valuenum'].between(60, 250)
    ].groupby('subject_id')['valuenum'].mean()
     .reset_index()
     .rename(columns={'valuenum': 'bp_icu'}))

    # Fallback: OMR outpatient BP (stored as "120/80" strings, parse systolic)
    omr = pd.read_csv(demo_dir / "hosp" / "omr.csv.gz",
                      usecols=['subject_id', 'result_name', 'result_value'])
    omr_bp = omr[omr['result_name'] == 'Blood Pressure'].copy()
    omr_bp['systolic'] = (omr_bp['result_value']
                          .str.split('/').str[0]
                          .apply(pd.to_numeric, errors='coerce'))
    omr_bp = (omr_bp[omr_bp['systolic'].between(60, 250) &
                     omr_bp['subject_id'].isin(subject_ids)]
              .groupby('subject_id')['systolic'].mean()
              .reset_index()
              .rename(columns={'systolic': 'bp_omr'}))

    # Merge: prefer ICU, fill with OMR
    bp = (pd.DataFrame({'subject_id': subject_ids})
          .merge(bp_icu, on='subject_id', how='left')
          .merge(omr_bp, on='subject_id', how='left'))
    bp['bp'] = bp['bp_icu'].combine_first(bp['bp_omr'])
    return bp[['subject_id', 'bp']]


def load_comorbidities(demo_dir: Path, hadm_ids: pd.Series) -> pd.DataFrame:
    dx = pd.read_csv(demo_dir / "hosp" / "diagnoses_icd.csv.gz",
                     usecols=['subject_id', 'hadm_id', 'icd_code', 'icd_version'])
    dx = dx[dx['hadm_id'].isin(hadm_ids) & (dx['icd_version'] == 10)]
    dx['icd_code'] = dx['icd_code'].astype(str)
    result = dx.groupby(['subject_id', 'hadm_id']).apply(
        lambda g: pd.Series({
            'htn': int(g['icd_code'].str.startswith('I10').any()),
            'dm':  int(g['icd_code'].str.startswith('E11').any()),
            'cad': int(g['icd_code'].str.startswith('I25').any()),
        }),
        include_groups=False
    ).reset_index()
    return result


# ── Schema harmonisation ───────────────────────────────────────────────────
def harmonize_to_uci_schema(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out['age']   = df['age']
    out['bp']    = df.get('bp', np.nan)
    out['sg']    = np.nan
    out['al']    = df.get('al', np.nan)
    out['su']    = np.nan
    # rbc: normal if RBC count ≥ 3.8 × 10^6/µL
    rbcc = df.get('rbcc', pd.Series(np.nan, index=df.index))
    out['rbc']   = np.where(rbcc >= 3.8, 'normal', 'abnormal')
    out['pc']    = np.nan
    out['pcc']   = np.nan
    out['ba']    = np.nan
    out['bgr']   = df.get('bgr', np.nan)
    out['bu']    = df.get('bu', np.nan)
    out['sc']    = df['sc']
    out['sod']   = df.get('sod', np.nan)
    out['pot']   = df.get('pot', np.nan)
    out['hemo']  = df.get('hemo', np.nan)
    out['pcv']   = df.get('pcv', np.nan)
    out['wbcc']  = df.get('wbcc', np.nan)
    out['rbcc']  = df.get('rbcc', np.nan)
    out['htn']   = df.get('htn', 0).map({1: 'yes', 0: 'no'}).fillna('no')
    out['dm']    = df.get('dm',  0).map({1: 'yes', 0: 'no'}).fillna('no')
    out['cad']   = df.get('cad', 0).map({1: 'yes', 0: 'no'}).fillna('no')
    out['appet'] = np.nan
    out['pe']    = np.nan
    # anemia: Hgb < 12 (F) or < 13.5 (M)
    thresh = np.where(df['gender'].str.upper() == 'F', 12.0, 13.5)
    hemo   = df.get('hemo', pd.Series(np.nan, index=df.index))
    out['ane']   = np.where(hemo < thresh, 'yes', 'no')
    # eGFR + label
    egfr = ckd_epi_egfr(df['sc'], df['age'], df['gender'])
    out['egfr']  = egfr.round(1)
    out['class'] = np.where(egfr < 60, 'ckd', 'notckd')
    return out


def missingness_report(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        'column':      df.columns,
        'n_missing':   df.isnull().sum().values,
        'pct_missing': (df.isnull().mean() * 100).round(1).values,
        'dtype':       df.dtypes.astype(str).values,
    })


def write_readme(df: pd.DataFrame, report: pd.DataFrame, demo_dir: Path):
    ckd_n    = (df['class'] == 'ckd').sum()
    notckd_n = (df['class'] == 'notckd').sum()
    total    = len(df)
    README_FILE.write_text(f"""# MIMIC-IV CKD Cohort — Pipeline Development Set

Generated  : {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
Source     : MIMIC-IV Clinical Database Demo v2.2 (local CSV)
Demo dir   : {demo_dir}

## ⚠️ Development Dataset — NOT for Final Paper

This cohort was extracted from the 100-patient MIMIC-IV demo.
It is used to develop and validate the extraction + analysis pipeline.
The final paper requires full MIMIC-IV access (≥500 CKD patients).

## Cohort Definition

- Population : all patients in the demo with serum creatinine on first admission
- CKD label  : eGFR < 60 mL/min/1.73m² (CKD-EPI 2021, race-free)
- Strategy   : eGFR-based (not ICD code filtered) to maximise demo cohort size

## Size

| Group    | N      |
|----------|--------|
| CKD      | {ckd_n}  |
| Not CKD  | {notckd_n}  |
| **Total**| **{total}** |

## Schema Alignment with UCI CKD

25 columns matching UCI processed schema. Unavailable columns
(sg, su, pc, pcc, ba, appet, pe) retained as NaN.

## Missingness Summary

{report.to_csv(index=False)}

## Ethics

MIMIC-IV demo data is publicly available under the PhysioNet
Credentialed Health Data License. No raw data is committed to git.
""", encoding='utf-8')


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Extract MIMIC-IV demo cohort from local CSV files")
    parser.add_argument('--demo-dir', default=str(DEFAULT_DEMO),
                        help='Path to mimic-iv-clinical-database-demo-2.2/')
    args = parser.parse_args()
    demo_dir = Path(args.demo_dir)

    print("=" * 60)
    print("MIMIC-IV Demo - Local CSV Extraction")
    print("=" * 60)

    print(f"\n[1/5] Loading patients + first admissions from {demo_dir.name} ...")
    base = load_first_admissions(demo_dir)
    print(f"      Patients with first admission: {len(base)}")

    print("[2/5] Loading lab values ...")
    labs = load_labs(demo_dir, base['hadm_id'])
    # Keep only patients with creatinine (required for eGFR)
    labs = labs[labs['sc'].notna()]
    print(f"      Patients with creatinine: {len(labs)}")

    print("[3/5] Loading blood pressure (ICU chartevents + OMR fallback) ...")
    bp = load_bp(demo_dir, base['hadm_id'], base['subject_id'])
    n_icu = bp['bp'].notna().sum()
    print(f"      Patients with BP resolved: {n_icu} / {len(bp)}")

    print("[4/5] Loading comorbidity flags ...")
    comorbid = load_comorbidities(demo_dir, base['hadm_id'])

    # Merge everything (bp joins on subject_id only — spans both ICU and OMR)
    df = (base
          .merge(labs,     on=['subject_id', 'hadm_id'], how='inner')
          .merge(bp,       on='subject_id',              how='left')
          .merge(comorbid, on=['subject_id', 'hadm_id'], how='left'))
    df[['htn', 'dm', 'cad']] = df[['htn', 'dm', 'cad']].fillna(0).astype(int)

    print("[5/5] Harmonising to UCI schema and computing eGFR labels ...")
    out = harmonize_to_uci_schema(df)
    ckd_n    = (out['class'] == 'ckd').sum()
    notckd_n = (out['class'] == 'notckd').sum()
    print(f"      CKD (eGFR < 60) : {ckd_n}")
    print(f"      Not CKD         : {notckd_n}")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_FILE, index=False)
    print(f"\n      Saved cohort         : {OUT_FILE}")

    report = missingness_report(out)
    report.to_csv(OUT_FILE.parent / "mimic_missingness_report.csv", index=False)
    print(f"      Saved missingness    : {OUT_FILE.parent / 'mimic_missingness_report.csv'}")

    write_readme(out, report, demo_dir)
    print(f"      Saved README         : {README_FILE}")

    print("\n" + "=" * 60)
    print("DONE")
    print(f"  Rows   : {len(out)}")
    print(f"  Cols   : {len(out.columns)}")
    print(f"  CKD    : {ckd_n}  ({ckd_n/len(out)*100:.1f}%)")
    print(f"  Not CKD: {notckd_n}  ({notckd_n/len(out)*100:.1f}%)")
    print("=" * 60)
    print("\nREMINDER: This is a 97-patient demo cohort.")
    print("Results are for pipeline testing only - not for publication.")
    print("Apply for full MIMIC-IV at https://physionet.org/")


if __name__ == "__main__":
    main()
