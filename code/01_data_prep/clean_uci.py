"""
Task 2.3 — UCI CKD Data Cleaning
---------------------------------
Inputs : data/raw/uci_ckd.csv
Outputs: data/processed/uci_ckd_clean.csv
         tables/t_uci_missingness.csv
"""

from pathlib import Path
import pandas as pd
import numpy as np

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parents[2]
RAW_FILE  = ROOT / "data" / "raw"       / "uci_ckd.csv"
OUT_FILE  = ROOT / "data" / "processed" / "uci_ckd_clean.csv"
MISS_FILE = ROOT / "tables"             / "t_uci_missingness.csv"

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
MISS_FILE.parent.mkdir(parents=True, exist_ok=True)

# ── Column definitions ─────────────────────────────────────────────────────
CONTINUOUS = ['age', 'bp', 'sg', 'al', 'su', 'bgr', 'bu', 'sc',
              'sod', 'pot', 'hemo', 'pcv', 'wbcc', 'rbcc']

# Maps categorical values -> 1/0; positive/presence = 1
CAT_MAPS = {
    'rbc'  : {'normal': 1,    'abnormal': 0},
    'pc'   : {'normal': 1,    'abnormal': 0},
    'pcc'  : {'present': 1,   'notpresent': 0},
    'ba'   : {'present': 1,   'notpresent': 0},
    'htn'  : {'yes': 1,       'no': 0},
    'dm'   : {'yes': 1,       'no': 0},
    'cad'  : {'yes': 1,       'no': 0},
    'appet': {'good': 1,      'poor': 0},
    'pe'   : {'yes': 1,       'no': 0},
    'ane'  : {'yes': 1,       'no': 0},
}

LABEL_MAP = {'ckd': 1, 'notckd': 0}


def missingness_snapshot(df: pd.DataFrame, stage: str) -> pd.DataFrame:
    return pd.DataFrame({
        'column'     : df.columns,
        'stage'      : stage,
        'n_missing'  : df.isnull().sum().values,
        'pct_missing': (df.isnull().mean() * 100).round(2).values,
    })


def main():
    print("=" * 55)
    print("UCI CKD Data Cleaning")
    print("=" * 55)

    # ── 1. Load ────────────────────────────────────────────────
    df = pd.read_csv(RAW_FILE)
    print(f"\n[1] Loaded  -> {df.shape[0]} rows x {df.shape[1]} cols")

    snap_before = missingness_snapshot(df, "before_imputation")
    total_missing_before = df.isnull().sum().sum()
    print(f"    Total missing cells : {total_missing_before}")

    # ── 2. Strip whitespace from all string columns ────────────
    str_cols = df.select_dtypes(include='object').columns
    for col in str_cols:
        df[col] = df[col].str.strip()
    print(f"\n[2] Stripped whitespace from {len(str_cols)} string columns")
    print(f"    dm unique after strip: {sorted(df['dm'].dropna().unique())}")

    # ── 3. Encode categorical columns ─────────────────────────
    for col, mapping in CAT_MAPS.items():
        df[col] = df[col].map(mapping)   # unmapped -> NaN preserved for imputation
    print(f"\n[3] Encoded {len(CAT_MAPS)} categorical columns to 0/1")

    # ── 4. Encode target label ─────────────────────────────────
    df['class'] = df['class'].map(LABEL_MAP)
    print(f"    class distribution -> {df['class'].value_counts().to_dict()}")

    # ── 5. Impute continuous -> median ─────────────────────────
    for col in CONTINUOUS:
        median = df[col].median()
        n_filled = df[col].isnull().sum()
        df[col] = df[col].fillna(median)
        if n_filled:
            print(f"    Continuous impute  {col:6s}: {n_filled} cells -> median={median:.4g}")

    # ── 6. Impute categorical -> mode ──────────────────────────
    for col in CAT_MAPS:
        mode_val = df[col].mode()[0]
        n_filled = df[col].isnull().sum()
        df[col] = df[col].fillna(mode_val)
        if n_filled:
            print(f"    Categorical impute {col:6s}: {n_filled} cells -> mode={mode_val}")

    # ── 7. Final dtype tidy — everything should be numeric ────
    for col in CONTINUOUS:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    for col in CAT_MAPS:
        df[col] = df[col].astype(int)
    df['class'] = df['class'].astype(int)

    # ── 8. Verify zero missing ─────────────────────────────────
    snap_after = missingness_snapshot(df, "after_imputation")
    remaining  = df.isnull().sum().sum()
    print(f"\n[4] Missing cells after imputation: {remaining}")
    assert remaining == 0, f"FAIL — {remaining} missing values remain"
    print("    PASS — zero missing values")

    # ── 9. Save processed file ─────────────────────────────────
    df.to_csv(OUT_FILE, index=False)
    print(f"\n[5] Saved cleaned data -> {OUT_FILE}")
    print(f"    Shape: {df.shape[0]} rows x {df.shape[1]} cols")

    # ── 10. Save missingness report ────────────────────────────
    miss_report = pd.concat([snap_before, snap_after], ignore_index=True)
    miss_report.to_csv(MISS_FILE, index=False)
    print(f"\n[6] Saved missingness report -> {MISS_FILE}")

    # ── 11. Summary ───────────────────────────────────────────
    print("\n" + "=" * 55)
    print("DONE")
    print(f"  Rows              : {len(df)}")
    print(f"  Columns           : {len(df.columns)}")
    print(f"  CKD positive (1)  : {(df['class']==1).sum()}")
    print(f"  CKD negative (0)  : {(df['class']==0).sum()}")
    print(f"  Missing before    : {total_missing_before}")
    print(f"  Missing after     : {remaining}")
    print("=" * 55)


if __name__ == "__main__":
    main()
