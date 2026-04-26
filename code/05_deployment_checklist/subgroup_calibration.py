"""
Task 6.2 — Subgroup Calibration Analysis (MIMIC)
--------------------------------------------------
Stratifies the MIMIC cohort by Age, Diabetes, and Hypertension, then
computes ECE per subgroup per model (best-calibrated variant).

Note: Sex subgroup omitted — MIMIC demo does not retain gender in the
      harmonized schema (UCI has no sex feature; gender was used only
      for eGFR computation and was dropped).

Outputs
-------
  tables/t_subgroup_calibration.csv
"""

import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from netcal.metrics import ECE

warnings.filterwarnings("ignore")

ROOT        = Path(__file__).resolve().parents[2]
MIMIC_CLEAN = ROOT / "data" / "processed" / "mimic_ckd_clean.csv"
UCI_CLEAN   = ROOT / "data" / "processed" / "uci_ckd_clean.csv"
MODELS_DIR  = ROOT / "code" / "02_modeling" / "saved_models"
T2_PATH     = ROOT / "tables" / "T2_calibration_summary.csv"
TABLE_DIR   = ROOT / "tables"

TABLE_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES = ["LR", "RF", "XGB", "SVM", "NB"]
N_BINS      = 5   # fewer bins for small subgroups


def get_best_variant(name):
    """Return the calibration method with lowest UCI ECE from T2."""
    t2 = pd.read_csv(T2_PATH)
    row = t2[t2["model"] == name].iloc[0]
    variant = row["calibration_method"]
    if variant == "base":
        return joblib.load(MODELS_DIR / f"{name}.pkl")
    return joblib.load(MODELS_DIR / f"{variant}_{name}.pkl")


def ece_for_group(y_true, y_prob, n_bins=N_BINS):
    if len(y_true) < 10:
        return np.nan
    try:
        return round(float(ECE(bins=n_bins).measure(y_prob, y_true)), 4)
    except Exception:
        return np.nan


def main():
    print("=" * 65)
    print("Task 6.2 - Subgroup Calibration Analysis (MIMIC)")
    print("=" * 65)

    mimic = pd.read_csv(MIMIC_CLEAN)
    uci   = pd.read_csv(UCI_CLEAN)
    feat_cols = [c for c in uci.columns if c != "class"]
    X = mimic[feat_cols].values
    y = mimic["class"].values

    # Define subgroups using MIMIC features
    subgroups = {
        "age_lt65" : mimic["age"] <  65,
        "age_ge65" : mimic["age"] >= 65,
        "dm_yes"   : mimic["dm"]  == 1,
        "dm_no"    : mimic["dm"]  == 0,
        "htn_yes"  : mimic["htn"] == 1,
        "htn_no"   : mimic["htn"] == 0,
        "overall"  : pd.Series([True] * len(mimic)),
    }

    print(f"\n[1] MIMIC: {len(mimic)} samples")
    for sg_name, mask in subgroups.items():
        n = int(mask.sum())
        if n < 10:
            print(f"    {sg_name:12s}: n={n}  [WARNING: too small for ECE]")
        else:
            ckd_n = int(y[mask.values].sum())
            print(f"    {sg_name:12s}: n={n}  CKD={ckd_n}")

    print(f"\n[2] Computing ECE per subgroup per model ...\n")
    rows = []
    for name in MODEL_NAMES:
        model = get_best_variant(name)
        probs = model.predict_proba(X)[:, 1]
        row   = {"model": name}
        for sg_name, mask in subgroups.items():
            m = mask.values
            ece_val = ece_for_group(y[m], probs[m])
            row[sg_name] = ece_val
        rows.append(row)
        print(f"  {name}  " + "  ".join(
            f"{k}={v:.4f}" if not np.isnan(v) else f"{k}=NaN"
            for k, v in row.items() if k != "model"
        ))

    result = pd.DataFrame(rows)
    result.to_csv(TABLE_DIR / "t_subgroup_calibration.csv", index=False)
    print(f"\n[3] Saved: tables/t_subgroup_calibration.csv")

    # Max subgroup gap per model (excluding overall and NaN)
    sg_cols = [c for c in result.columns
               if c not in ("model", "overall") and not result[c].isna().all()]
    if sg_cols:
        result["max_subgroup_ece_gap"] = (
            result[sg_cols].max(axis=1) - result[sg_cols].min(axis=1)
        ).round(4)
        print("\n  Max subgroup ECE gap per model:")
        print(result[["model", "max_subgroup_ece_gap"]].to_string(index=False))

    print("\n" + "=" * 65)
    print(result.to_string(index=False))
    print("=" * 65)
    print("\nDONE")


if __name__ == "__main__":
    main()
