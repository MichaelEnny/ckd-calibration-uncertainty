"""
Tasks 4.4 + 4.5 — External Calibration Validation (MIMIC) + Summary Table
---------------------------------------------------------------------------
Applies the best-calibrated model variant for each classifier to the MIMIC
cohort and computes ECE, MCE, Brier Score on both UCI test and MIMIC.

Best variant selection rule: lowest ECE on UCI test set.
  Candidates per model: base | platt | isotonic

Produces
--------
  tables/t_calibration_mimic.csv          — MIMIC calibration metrics
  figures/reliability_mimic_<model>.png   — MIMIC reliability diagrams
  tables/T2_calibration_summary.csv       — manuscript Table 2 (combined)
"""

import json
import warnings
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from netcal.metrics import ECE, MCE
from sklearn.calibration import CalibrationDisplay
from sklearn.metrics import brier_score_loss, roc_auc_score

warnings.filterwarnings("ignore")

ROOT        = Path(__file__).resolve().parents[2]
UCI_CLEAN   = ROOT / "data" / "processed" / "uci_ckd_clean.csv"
MIMIC_CLEAN = ROOT / "data" / "processed" / "mimic_ckd_clean.csv"
SPLIT_FILE  = ROOT / "data" / "processed" / "uci_splits.json"
MODELS_DIR  = ROOT / "code" / "02_modeling" / "saved_models"
TABLE_DIR   = ROOT / "tables"
FIGURES_DIR = ROOT / "figures"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES = ["LR", "RF", "XGB", "SVM", "NB"]
N_BINS      = 10

MODEL_COLORS = {
    "LR": "#2196F3", "RF": "#4CAF50", "XGB": "#FF5722",
    "SVM": "#9C27B0", "NB": "#FF9800",
}


def cal_metrics(y_true, y_prob):
    ece = float(ECE(bins=N_BINS).measure(y_prob, y_true))
    mce = float(MCE(bins=N_BINS).measure(y_prob, y_true))
    bs  = float(brier_score_loss(y_true, y_prob))
    auc = float(roc_auc_score(y_true, y_prob))
    return {"ece": round(ece,4), "mce": round(mce,4),
            "brier": round(bs,4), "auroc": round(auc,4)}


def best_variant(name, X_test, y_test):
    """Return (variant_label, model, metrics) with lowest ECE on UCI test."""
    candidates = {}
    for tag, path in [("base",     MODELS_DIR / f"{name}.pkl"),
                      ("platt",    MODELS_DIR / f"platt_{name}.pkl"),
                      ("isotonic", MODELS_DIR / f"isotonic_{name}.pkl")]:
        m = joblib.load(path)
        p = m.predict_proba(X_test)[:, 1]
        candidates[tag] = (m, p, cal_metrics(y_test, p))
    best_tag = min(candidates, key=lambda t: candidates[t][2]["ece"])
    return best_tag, *candidates[best_tag]


def plot_reliability(name, variant, y_true, y_prob, metrics, out_path):
    fig, ax = plt.subplots(figsize=(5, 5))
    CalibrationDisplay.from_predictions(
        y_true, y_prob, n_bins=N_BINS, ax=ax,
        color=MODEL_COLORS.get(name, "#333"), label=f"{name} ({variant})",
        name=f"{name} ({variant})")
    txt = (f"ECE  ={metrics['ece']:.4f}\n"
           f"MCE  ={metrics['mce']:.4f}\n"
           f"Brier={metrics['brier']:.4f}\n"
           f"AUROC={metrics['auroc']:.4f}")
    ax.text(0.03, 0.97, txt, transform=ax.transAxes, fontsize=8,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor="#CCCCCC", alpha=0.9))
    ax.set_title(f"Reliability — {name} [{variant}] (MIMIC external)",
                 fontsize=11, pad=8)
    ax.set_xlabel("Mean predicted probability", fontsize=9)
    ax.set_ylabel("Fraction of positives", fontsize=9)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    print("=" * 65)
    print("Tasks 4.4 + 4.5 - External Calibration (MIMIC) + Summary")
    print("=" * 65)

    # ── 1. Load UCI test data ─────────────────────────────────────
    uci = pd.read_csv(UCI_CLEAN)
    with open(SPLIT_FILE) as f:
        splits = json.load(f)
    feat_cols = [c for c in uci.columns if c != "class"]
    X_uci = uci[feat_cols].values
    y_uci = uci["class"].values
    idx_test = splits["test"]
    X_test, y_test = X_uci[idx_test], y_uci[idx_test]
    print(f"\n[1] UCI test: {len(y_test)} samples  "
          f"(CKD={y_test.sum()}, notCKD={(y_test==0).sum()})")

    # ── 2. Load MIMIC ─────────────────────────────────────────────
    mimic = pd.read_csv(MIMIC_CLEAN)
    X_mimic = mimic[feat_cols].values
    y_mimic = mimic["class"].values
    print(f"[2] MIMIC   : {len(y_mimic)} samples  "
          f"(CKD={y_mimic.sum()}, notCKD={(y_mimic==0).sum()})")

    # ── 3. Evaluate best variant per model ────────────────────────
    print("\n[3] Selecting best-calibrated variant per model (by UCI ECE) ...\n")
    mimic_rows   = []
    summary_rows = []

    for name in MODEL_NAMES:
        variant, model, p_uci, m_uci = best_variant(name, X_test, y_test)
        p_mimic = model.predict_proba(X_mimic)[:, 1]
        m_mimic = cal_metrics(y_mimic, p_mimic)

        drift_ece   = round(m_mimic["ece"]   - m_uci["ece"],   4)
        drift_brier = round(m_mimic["brier"] - m_uci["brier"], 4)

        print(f"  {name} [{variant}]")
        print(f"    UCI  : ECE={m_uci['ece']:.4f}  Brier={m_uci['brier']:.4f}  "
              f"AUROC={m_uci['auroc']:.4f}")
        print(f"    MIMIC: ECE={m_mimic['ece']:.4f}  Brier={m_mimic['brier']:.4f}  "
              f"AUROC={m_mimic['auroc']:.4f}  "
              f"DELTA_ECE={drift_ece:+.4f}")

        # Reliability diagram for MIMIC
        plot_reliability(name, variant, y_mimic, p_mimic, m_mimic,
                         FIGURES_DIR / f"reliability_mimic_{name}.png")

        mimic_rows.append({
            "model": name, "calibration_method": variant,
            **{f"mimic_{k}": v for k, v in m_mimic.items()},
            "delta_ece": drift_ece,
        })
        summary_rows.append({
            "model"             : name,
            "calibration_method": variant,
            "uci_ece"           : m_uci["ece"],
            "uci_brier"         : m_uci["brier"],
            "uci_auroc"         : m_uci["auroc"],
            "mimic_ece"         : m_mimic["ece"],
            "mimic_brier"       : m_mimic["brier"],
            "mimic_auroc"       : m_mimic["auroc"],
            "calibration_drift" : drift_ece,
        })

    # ── 4. Save tables ────────────────────────────────────────────
    pd.DataFrame(mimic_rows).to_csv(
        TABLE_DIR / "t_calibration_mimic.csv", index=False)
    pd.DataFrame(summary_rows).to_csv(
        TABLE_DIR / "T2_calibration_summary.csv", index=False)

    figs = sorted(FIGURES_DIR.glob("reliability_mimic_*.png"))
    print(f"\n[4] Saved tables:")
    print(f"    tables/t_calibration_mimic.csv")
    print(f"    tables/T2_calibration_summary.csv")
    print(f"[5] Saved {len(figs)} MIMIC reliability diagrams")

    print("\n" + "=" * 65)
    print("T2 Calibration Summary:")
    print(pd.DataFrame(summary_rows).to_string(index=False))
    print("=" * 65)
    print("\nDONE")


if __name__ == "__main__":
    main()
