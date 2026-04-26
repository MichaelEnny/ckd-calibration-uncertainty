"""
Task 7.4 - Bootstrap Confidence Intervals
------------------------------------------
Computes 95% bootstrap CIs (1000 resamples) for AUROC and ECE on:
  - UCI test set (best variant per model)
  - MIMIC cohort (same best variant)

Outputs: tables/T2_calibration_summary.csv updated with CI columns
         tables/t_bootstrap_ci.csv (standalone CI table)
"""

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from netcal.metrics import ECE
from sklearn.metrics import roc_auc_score
from sklearn.utils import resample

warnings.filterwarnings("ignore")

ROOT        = Path(__file__).resolve().parents[2]
UCI_CLEAN   = ROOT / "data" / "processed" / "uci_ckd_clean.csv"
MIMIC_CLEAN = ROOT / "data" / "processed" / "mimic_ckd_clean.csv"
SPLIT_FILE  = ROOT / "data" / "processed" / "uci_splits.json"
MODELS_DIR  = ROOT / "code" / "02_modeling" / "saved_models"
T2_PATH     = ROOT / "tables" / "T2_calibration_summary.csv"
TABLE_DIR   = ROOT / "tables"

N_BOOT      = 1000
ALPHA       = 0.05
RANDOM_STATE = 42
N_BINS      = 10
MODEL_NAMES = ["LR", "RF", "XGB", "SVM", "NB"]


def bootstrap_ci(y_true, y_prob, n_boot=N_BOOT, seed=RANDOM_STATE):
    rng = np.random.default_rng(seed)
    auroc_boot, ece_boot = [], []
    for _ in range(n_boot):
        idx = rng.integers(0, len(y_true), len(y_true))
        yt, yp = y_true[idx], y_prob[idx]
        if len(np.unique(yt)) < 2:
            continue
        try:
            auroc_boot.append(roc_auc_score(yt, yp))
            ece_boot.append(float(ECE(bins=N_BINS).measure(yp, yt)))
        except Exception:
            continue
    lo_a, hi_a = np.percentile(auroc_boot, [2.5, 97.5])
    lo_e, hi_e = np.percentile(ece_boot,   [2.5, 97.5])
    return {
        "auroc_ci_lo": round(lo_a, 4), "auroc_ci_hi": round(hi_a, 4),
        "ece_ci_lo":   round(lo_e, 4), "ece_ci_hi":   round(hi_e, 4),
    }


def load_model(name, variant):
    if variant == "base":
        return joblib.load(MODELS_DIR / f"{name}.pkl")
    return joblib.load(MODELS_DIR / f"{variant}_{name}.pkl")


def main():
    print("=" * 60)
    print("Task 7.4 - Bootstrap Confidence Intervals (n=1000)")
    print("=" * 60)

    uci = pd.read_csv(UCI_CLEAN)
    with open(SPLIT_FILE) as f:
        splits = json.load(f)
    feat_cols = [c for c in uci.columns if c != "class"]
    X_uci = uci[feat_cols].values
    y_uci = uci["class"].values
    X_test = X_uci[splits["test"]]
    y_test = y_uci[splits["test"]]

    mimic = pd.read_csv(MIMIC_CLEAN)
    X_mimic = mimic[feat_cols].values
    y_mimic = mimic["class"].values

    t2 = pd.read_csv(T2_PATH)
    rows = []
    print(f"\n{'Model':5s} {'Variant':10s} {'UCI AUROC 95%CI':22s} {'UCI ECE 95%CI':22s} {'MIMIC AUROC 95%CI':22s} {'MIMIC ECE 95%CI':22s}")
    print("-" * 105)

    for name in MODEL_NAMES:
        variant = t2[t2["model"] == name]["calibration_method"].values[0]
        model   = load_model(name, variant)

        p_uci   = model.predict_proba(X_test)[:, 1]
        p_mimic = model.predict_proba(X_mimic)[:, 1]

        ci_uci   = bootstrap_ci(y_test, p_uci)
        ci_mimic = bootstrap_ci(y_mimic, p_mimic)

        print(f"{name:5s} {variant:10s} "
              f"[{ci_uci['auroc_ci_lo']:.3f}, {ci_uci['auroc_ci_hi']:.3f}]       "
              f"[{ci_uci['ece_ci_lo']:.3f}, {ci_uci['ece_ci_hi']:.3f}]       "
              f"[{ci_mimic['auroc_ci_lo']:.3f}, {ci_mimic['auroc_ci_hi']:.3f}]       "
              f"[{ci_mimic['ece_ci_lo']:.3f}, {ci_mimic['ece_ci_hi']:.3f}]")

        rows.append({
            "model": name, "calibration_method": variant,
            "uci_auroc_ci_lo":   ci_uci["auroc_ci_lo"],
            "uci_auroc_ci_hi":   ci_uci["auroc_ci_hi"],
            "uci_ece_ci_lo":     ci_uci["ece_ci_lo"],
            "uci_ece_ci_hi":     ci_uci["ece_ci_hi"],
            "mimic_auroc_ci_lo": ci_mimic["auroc_ci_lo"],
            "mimic_auroc_ci_hi": ci_mimic["auroc_ci_hi"],
            "mimic_ece_ci_lo":   ci_mimic["ece_ci_lo"],
            "mimic_ece_ci_hi":   ci_mimic["ece_ci_hi"],
        })

    ci_df = pd.DataFrame(rows)
    ci_df.to_csv(TABLE_DIR / "t_bootstrap_ci.csv", index=False)
    print(f"\nSaved: tables/t_bootstrap_ci.csv")

    # Merge into T2
    t2_updated = t2.merge(ci_df, on=["model", "calibration_method"], how="left")
    t2_updated.to_csv(T2_PATH, index=False)
    print(f"Updated: tables/T2_calibration_summary.csv (CI columns added)")
    print("\nDONE")


if __name__ == "__main__":
    main()
