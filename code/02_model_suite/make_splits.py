"""
Task 3.2 — Train / Validation / Test Split
-------------------------------------------
Splits UCI CKD data into three non-overlapping, stratified partitions:
  - train : 70%  (model fitting)
  - val   : 15%  (calibration tuning / post-hoc calibration fitting)
  - test  : 15%  (final held-out evaluation — touched only once)

MIMIC-IV is reserved as an external test set (no training, no split needed here).

Inputs : data/processed/uci_ckd_clean.csv
Outputs: data/processed/uci_splits.json   — row indices for each partition
         tables/t_split_summary.csv       — split size and class-balance table

Leakage check: asserts that train ∩ val = ∅, train ∩ test = ∅, val ∩ test = ∅.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parents[2]
DATA_FILE  = ROOT / "data" / "processed" / "uci_ckd_clean.csv"
SPLIT_FILE = ROOT / "data" / "processed" / "uci_splits.json"
TABLE_FILE = ROOT / "tables"             / "t_split_summary.csv"

TABLE_FILE.parent.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42


def stratified_three_way_split(indices: np.ndarray, labels: np.ndarray,
                                train_frac=0.70, val_frac=0.15,
                                random_state=42):
    """Return (train_idx, val_idx, test_idx) with stratification preserved."""
    # Step 1: carve off train (70%)
    idx_train, idx_temp, _, y_temp = train_test_split(
        indices, labels,
        test_size=(1.0 - train_frac),
        stratify=labels,
        random_state=random_state,
    )
    # Step 2: split remainder evenly → val (15%) and test (15%)
    # val_frac as fraction of temp = 0.15 / 0.30 = 0.50
    val_frac_of_temp = val_frac / (1.0 - train_frac)
    idx_val, idx_test = train_test_split(
        idx_temp,
        test_size=(1.0 - val_frac_of_temp),
        stratify=y_temp,
        random_state=random_state,
    )
    return idx_train, idx_val, idx_test


def split_summary(df: pd.DataFrame, splits: dict) -> pd.DataFrame:
    rows = []
    total = len(df)
    for name, indices in splits.items():
        sub = df.iloc[indices]
        n   = len(sub)
        n_ckd    = int((sub["class"] == 1).sum())
        n_notckd = int((sub["class"] == 0).sum())
        rows.append({
            "split"        : name,
            "n"            : n,
            "pct_of_total" : round(n / total * 100, 1),
            "n_ckd"        : n_ckd,
            "pct_ckd"      : round(n_ckd / n * 100, 1),
            "n_notckd"     : n_notckd,
            "pct_notckd"   : round(n_notckd / n * 100, 1),
        })
    return pd.DataFrame(rows)


def verify_no_leakage(idx_train, idx_val, idx_test):
    train_set = set(idx_train)
    val_set   = set(idx_val)
    test_set  = set(idx_test)

    tv = train_set & val_set
    tt = train_set & test_set
    vt = val_set   & test_set

    assert len(tv) == 0, f"LEAKAGE: {len(tv)} indices shared between train and val"
    assert len(tt) == 0, f"LEAKAGE: {len(tt)} indices shared between train and test"
    assert len(vt) == 0, f"LEAKAGE: {len(vt)} indices shared between val and test"
    print("  [PASS] train & val  = empty")
    print("  [PASS] train & test = empty")
    print("  [PASS] val  & test  = empty")

    total_unique = len(train_set | val_set | test_set)
    return total_unique


def main():
    print("=" * 60)
    print("Task 3.2 — Train / Validation / Test Split")
    print("=" * 60)

    # ── 1. Load ──────────────────────────────────────────────────
    df = pd.read_csv(DATA_FILE)
    n_total = len(df)
    labels  = df["class"].values
    indices = np.arange(n_total)
    print(f"\n[1] Loaded {n_total} samples")
    print(f"    CKD={labels.sum()} ({labels.mean()*100:.1f}%)  "
          f"notCKD={n_total - labels.sum()}")

    # ── 2. Split ─────────────────────────────────────────────────
    idx_train, idx_val, idx_test = stratified_three_way_split(
        indices, labels,
        train_frac=0.70, val_frac=0.15,
        random_state=RANDOM_STATE,
    )
    print(f"\n[2] Split complete (random_state={RANDOM_STATE})")
    print(f"    train : {len(idx_train):3d}  ({len(idx_train)/n_total*100:.1f}%)")
    print(f"    val   : {len(idx_val):3d}  ({len(idx_val)/n_total*100:.1f}%)")
    print(f"    test  : {len(idx_test):3d}  ({len(idx_test)/n_total*100:.1f}%)")

    # ── 3. Leakage check ─────────────────────────────────────────
    print("\n[3] Leakage checks:")
    total_unique = verify_no_leakage(idx_train, idx_val, idx_test)
    assert total_unique == n_total, \
        f"FAIL: {n_total - total_unique} rows not assigned to any split"
    print(f"  [PASS] all {n_total} rows assigned exactly once")

    # ── 4. Save JSON split indices ────────────────────────────────
    split_dict = {
        "random_state"  : RANDOM_STATE,
        "n_total"       : n_total,
        "train"         : sorted(idx_train.tolist()),
        "val"           : sorted(idx_val.tolist()),
        "test"          : sorted(idx_test.tolist()),
        "note_mimic"    : (
            "MIMIC-IV is reserved as external test set only. "
            "No MIMIC rows appear in train or val."
        ),
    }
    with open(SPLIT_FILE, "w") as f:
        json.dump(split_dict, f, indent=2)
    print(f"\n[4] Saved split indices -> data/processed/uci_splits.json")

    # ── 5. Summary table ──────────────────────────────────────────
    splits = {"train": idx_train, "val": idx_val, "test": idx_test}
    summary = split_summary(df, splits)
    summary.to_csv(TABLE_FILE, index=False)
    print(f"\n[5] Saved summary table -> tables/t_split_summary.csv")

    # ── 6. Print summary ──────────────────────────────────────────
    print("\n" + "=" * 60)
    print(summary.to_string(index=False))
    print("=" * 60)
    print("\nDONE")


if __name__ == "__main__":
    main()
