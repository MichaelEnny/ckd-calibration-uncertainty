"""
Tasks 5.3 + 5.5 — Conformal Prediction on MIMIC + Uncertainty Summary
-----------------------------------------------------------------------
Applies the fitted SplitConformalClassifier objects (from Task 5.2) to
the MIMIC external cohort and produces the uncertainty summary table.

Outputs
-------
  tables/t_conformal_mimic.csv      — MIMIC conformal metrics
  tables/T3_uncertainty_summary.csv — manuscript Table 3 (combined UCI + MIMIC)
"""

import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT        = Path(__file__).resolve().parents[2]
MIMIC_CLEAN = ROOT / "data" / "processed" / "mimic_ckd_clean.csv"
UCI_CLEAN   = ROOT / "data" / "processed" / "uci_ckd_clean.csv"
CP_DIR      = ROOT / "models"
TABLE_DIR   = ROOT / "tables"

TABLE_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES = ["LR", "RF", "XGB", "SVM", "NB"]
CONFIDENCE  = 0.90


def set_metrics(y_true, pred_sets):
    n = len(y_true)
    covered       = np.array([bool(pred_sets[i, y_true[i]]) for i in range(n)])
    set_sizes     = pred_sets.sum(axis=1)
    return {
        "coverage"      : round(float(covered.mean()),           4),
        "avg_set_size"  : round(float(set_sizes.mean()),         4),
        "singleton_rate": round(float((set_sizes == 1).mean()),  4),
        "empty_rate"    : round(float((set_sizes == 0).mean()),  4),
    }


def main():
    print("=" * 65)
    print("Tasks 5.3 + 5.5 - Conformal Prediction on MIMIC + Summary")
    print("=" * 65)

    # ── Load data ─────────────────────────────────────────────────
    uci   = pd.read_csv(UCI_CLEAN)
    mimic = pd.read_csv(MIMIC_CLEAN)
    feat_cols = [c for c in uci.columns if c != "class"]
    X_mimic = mimic[feat_cols].values
    y_mimic = mimic["class"].values
    print(f"\n[1] MIMIC: {len(y_mimic)} samples  "
          f"(CKD={y_mimic.sum()}, notCKD={(y_mimic==0).sum()})")

    # ── Load UCI conformal results for summary ────────────────────
    uci_cp = pd.read_csv(TABLE_DIR / "t_conformal_uci.csv")

    # ── Apply each conformal predictor to MIMIC ───────────────────
    print(f"\n[2] Applying conformal predictors to MIMIC ...\n")
    mimic_rows   = []
    summary_rows = []

    for name in MODEL_NAMES:
        cp = joblib.load(CP_DIR / f"conformal_{name}.pkl")
        _, set_raw = cp.predict_set(X_mimic)
        pred_sets  = set_raw[:, :, 0]

        m_mimic = set_metrics(y_mimic, pred_sets)
        uci_row = uci_cp[uci_cp["model"] == name].iloc[0]
        drift   = round(float(uci_row["coverage"]) - m_mimic["coverage"], 4)

        print(f"  {name:4s}  coverage={m_mimic['coverage']:.4f}  "
              f"avg_size={m_mimic['avg_set_size']:.4f}  "
              f"singleton={m_mimic['singleton_rate']:.4f}  "
              f"coverage_drift={drift:+.4f}")

        mimic_rows.append({"model": name,
                            **{f"mimic_{k}": v for k, v in m_mimic.items()},
                            "coverage_drift": drift})

        summary_rows.append({
            "model"              : name,
            "uci_coverage"       : float(uci_row["coverage"]),
            "uci_avg_set_size"   : float(uci_row["avg_set_size"]),
            "uci_singleton_rate" : float(uci_row["singleton_rate"]),
            "mimic_coverage"     : m_mimic["coverage"],
            "mimic_avg_set_size" : m_mimic["avg_set_size"],
            "mimic_singleton_rate": m_mimic["singleton_rate"],
            "coverage_drift"     : drift,
        })

    # ── Save tables ───────────────────────────────────────────────
    pd.DataFrame(mimic_rows).to_csv(
        TABLE_DIR / "t_conformal_mimic.csv", index=False)
    pd.DataFrame(summary_rows).to_csv(
        TABLE_DIR / "T3_uncertainty_summary.csv", index=False)

    print(f"\n[3] Saved: tables/t_conformal_mimic.csv")
    print(f"[4] Saved: tables/T3_uncertainty_summary.csv")

    print("\n" + "=" * 65)
    print("T3 Uncertainty Summary:")
    print(pd.DataFrame(summary_rows).to_string(index=False))
    print("=" * 65)
    print("\nDONE")


if __name__ == "__main__":
    main()
