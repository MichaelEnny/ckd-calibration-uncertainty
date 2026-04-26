"""
Task 2.4 — MIMIC Data Harmonization
-------------------------------------
Aligns mimic_ckd_cohort.csv to the UCI processed schema exactly:
  - Encodes categorical strings to 0/1
  - Imputes missing values using UCI TRAINING-set statistics only
    (no information from MIMIC itself used for imputation, avoiding leakage)
  - Drops egfr (derived reference column, not a model feature)
  - Saves schema_comparison.csv documenting alignment

Inputs : data/external/mimic_ckd_cohort.csv
         data/processed/uci_ckd_clean.csv
         data/processed/uci_splits.json
Outputs: data/processed/mimic_ckd_clean.csv
         data/processed/schema_comparison.csv
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT        = Path(__file__).resolve().parents[2]
MIMIC_RAW   = ROOT / "data" / "external" / "mimic_ckd_cohort.csv"
UCI_CLEAN   = ROOT / "data" / "processed" / "uci_ckd_clean.csv"
SPLIT_FILE  = ROOT / "data" / "processed" / "uci_splits.json"
OUT_MIMIC   = ROOT / "data" / "processed" / "mimic_ckd_clean.csv"
OUT_SCHEMA  = ROOT / "data" / "processed" / "schema_comparison.csv"

OUT_MIMIC.parent.mkdir(parents=True, exist_ok=True)

# Same categorical encoding as clean_uci.py
CAT_MAPS = {
    "rbc"  : {"normal": 1, "abnormal": 0},
    "pc"   : {"normal": 1, "abnormal": 0},
    "pcc"  : {"present": 1, "notpresent": 0},
    "ba"   : {"present": 1, "notpresent": 0},
    "htn"  : {"yes": 1, "no": 0},
    "dm"   : {"yes": 1, "no": 0},
    "cad"  : {"yes": 1, "no": 0},
    "appet": {"good": 1, "poor": 0},
    "pe"   : {"yes": 1, "no": 0},
    "ane"  : {"yes": 1, "no": 0},
}
LABEL_MAP  = {"ckd": 1, "notckd": 0}
CONTINUOUS = ["age", "bp", "sg", "al", "su", "bgr", "bu", "sc",
              "sod", "pot", "hemo", "pcv", "wbcc", "rbcc"]


def main():
    print("=" * 60)
    print("Task 2.4 - MIMIC Data Harmonization")
    print("=" * 60)

    # ── 1. Load MIMIC cohort ──────────────────────────────────────
    mimic = pd.read_csv(MIMIC_RAW)
    print(f"\n[1] Loaded MIMIC cohort: {mimic.shape[0]} rows x {mimic.shape[1]} cols")
    print(f"    Missing before harmonization:")
    miss_pre = mimic.isnull().sum()
    print(miss_pre[miss_pre > 0].to_string())

    # ── 2. Encode target label ────────────────────────────────────
    mimic["class"] = mimic["class"].map(LABEL_MAP)
    print(f"\n[2] Label encoded: CKD={int((mimic['class']==1).sum())}  "
          f"notCKD={int((mimic['class']==0).sum())}")

    # ── 3. Encode categorical columns ─────────────────────────────
    for col, mapping in CAT_MAPS.items():
        if col in mimic.columns:
            mimic[col] = mimic[col].map(mapping)
    print(f"[3] Categorical columns encoded to 0/1")

    # ── 4. Compute UCI TRAINING-set imputation statistics ─────────
    uci  = pd.read_csv(UCI_CLEAN)
    with open(SPLIT_FILE) as f:
        splits = json.load(f)
    uci_train = uci.iloc[splits["train"]]

    impute_stats = {}
    for col in CONTINUOUS:
        impute_stats[col] = ("median", uci_train[col].median())
    for col in CAT_MAPS:
        mode_val = uci_train[col].mode()
        impute_stats[col] = ("mode", float(mode_val[0]) if len(mode_val) else 0.0)

    print(f"[4] Imputation statistics from UCI training set "
          f"({len(uci_train)} rows)")

    # ── 5. Apply imputation ───────────────────────────────────────
    imputed_cols = []
    for col, (method, value) in impute_stats.items():
        if col not in mimic.columns:
            mimic[col] = np.nan
        n_missing = int(mimic[col].isnull().sum())
        if n_missing > 0:
            mimic[col] = mimic[col].fillna(value)
            imputed_cols.append((col, method, value, n_missing))

    print(f"[5] Imputed {len(imputed_cols)} columns:")
    for col, method, value, n in imputed_cols:
        pct = n / len(mimic) * 100
        print(f"    {col:8s}: {n} cells ({pct:.1f}%)  {method}={value:.4g}")

    # ── 6. Drop egfr (reference only, not a model feature) ────────
    if "egfr" in mimic.columns:
        mimic = mimic.drop(columns=["egfr"])
        print(f"\n[6] Dropped 'egfr' column (reference only)")

    # ── 7. Align column order to UCI ──────────────────────────────
    uci_feature_cols = [c for c in uci.columns]   # includes 'class'
    mimic = mimic[uci_feature_cols]
    print(f"[7] Columns reordered to match UCI schema ({len(uci_feature_cols)} cols)")

    # ── 8. Final dtype tidy ───────────────────────────────────────
    for col in CONTINUOUS:
        mimic[col] = pd.to_numeric(mimic[col], errors="coerce")
    for col in CAT_MAPS:
        mimic[col] = mimic[col].astype(int)
    mimic["class"] = mimic["class"].astype(int)

    # ── 9. Verify zero missing ────────────────────────────────────
    remaining = int(mimic.isnull().sum().sum())
    print(f"\n[8] Missing after harmonization: {remaining}")
    assert remaining == 0, f"FAIL: {remaining} missing values remain"
    print("    PASS - zero missing values")

    # ── 10. Save processed MIMIC file ─────────────────────────────
    mimic.to_csv(OUT_MIMIC, index=False)
    print(f"\n[9] Saved: {OUT_MIMIC}")

    # ── 11. Schema comparison CSV ─────────────────────────────────
    rows = []
    for col in uci_feature_cols:
        in_uci   = col in uci.columns
        in_mimic = col in pd.read_csv(MIMIC_RAW).columns
        imputed  = any(c == col for c, *_ in imputed_cols)
        if imputed:
            _, method, value, n = next(
                (c, m, v, n) for c, m, v, n in imputed_cols if c == col)
            notes = f"{method}={value:.4g} from UCI train ({n} cells)"
        else:
            notes = "available directly"
        rows.append({
            "column"         : col,
            "in_uci_clean"   : in_uci,
            "in_mimic_raw"   : in_mimic,
            "imputed"        : imputed,
            "imputation_note": notes,
        })
    schema_df = pd.DataFrame(rows)
    schema_df.to_csv(OUT_SCHEMA, index=False)
    print(f"[10] Saved schema comparison: {OUT_SCHEMA}")

    print("\n" + "=" * 60)
    print("DONE")
    print(f"  Rows  : {len(mimic)}")
    print(f"  Cols  : {len(mimic.columns)}")
    print(f"  CKD   : {int((mimic['class']==1).sum())}  "
          f"({(mimic['class']==1).mean()*100:.1f}%)")
    print(f"  notCKD: {int((mimic['class']==0).sum())}  "
          f"({(mimic['class']==0).mean()*100:.1f}%)")
    print("=" * 60)


if __name__ == "__main__":
    main()
