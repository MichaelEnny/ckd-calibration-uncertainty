"""
Task 4.3 — Post-Calibration Metrics
--------------------------------------
Evaluates the Platt-scaled and Isotonic-scaled models on the UCI TEST set
(first and only use of the test set in the calibration pipeline).

For each model the base (pre-calibration) probabilities are also recomputed
on the test set so that pre/post comparisons are on the same held-out fold.

Metrics: ECE, MCE, Brier Score, BSS, + ECE reduction vs. base

Outputs
-------
  tables/t_calibration_postcal_platt.csv
  tables/t_calibration_postcal_isotonic.csv
  figures/reliability_compare_<model>.png   — 1×3 panel per model
                                              (pre | platt | isotonic)
"""

import json
import warnings
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
from netcal.metrics import ECE, MCE
from sklearn.calibration import CalibrationDisplay
from sklearn.metrics import brier_score_loss

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).resolve().parents[2]
DATA_FILE   = ROOT / "data" / "processed" / "uci_ckd_clean.csv"
SPLIT_FILE  = ROOT / "data" / "processed" / "uci_splits.json"
MODELS_DIR  = ROOT / "code" / "02_modeling" / "saved_models"
TABLE_DIR   = ROOT / "tables"
FIGURES_DIR = ROOT / "figures"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES = ["LR", "RF", "XGB", "SVM", "NB"]
N_BINS      = 10

MODEL_COLORS = {
    "LR" : "#2196F3",
    "RF" : "#4CAF50",
    "XGB": "#FF5722",
    "SVM": "#9C27B0",
    "NB" : "#FF9800",
}

METHOD_COLORS = {
    "pre"      : "#888888",
    "platt"    : "#E91E63",
    "isotonic" : "#009688",
}


# ── Metric helpers ────────────────────────────────────────────────────────────

def brier_skill_score(y_true, y_prob):
    bs_model = brier_score_loss(y_true, y_prob)
    bs_clim  = brier_score_loss(y_true, np.full_like(y_prob, y_true.mean()))
    return round(1.0 - bs_model / bs_clim, 4) if bs_clim != 0 else 0.0


def calibration_metrics(y_true, y_prob):
    ece = float(ECE(bins=N_BINS).measure(y_prob, y_true))
    mce = float(MCE(bins=N_BINS).measure(y_prob, y_true))
    bs  = brier_score_loss(y_true, y_prob)
    bss = brier_skill_score(y_true, y_prob)
    return {
        "ece"  : round(ece, 4),
        "mce"  : round(mce, 4),
        "brier": round(bs,  4),
        "bss"  : bss,
    }


# ── Figure helper ─────────────────────────────────────────────────────────────

def _add_panel(ax, y_true, y_prob, label, color, metrics):
    CalibrationDisplay.from_predictions(
        y_true, y_prob,
        n_bins=N_BINS, ax=ax,
        color=color, label=label, name=label,
    )
    txt = (
        f"ECE  ={metrics['ece']:.4f}\n"
        f"MCE  ={metrics['mce']:.4f}\n"
        f"Brier={metrics['brier']:.4f}\n"
        f"BSS  ={metrics['bss']:.4f}"
    )
    ax.text(0.03, 0.97, txt, transform=ax.transAxes, fontsize=7.5,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                      edgecolor="#CCCCCC", alpha=0.9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Mean predicted probability", fontsize=8)
    ax.set_ylabel("Fraction of positives", fontsize=8)
    ax.legend(loc="lower right", fontsize=7)


def plot_compare(model_name, y_true,
                 probs: dict,      # {"pre": arr, "platt": arr, "isotonic": arr}
                 metrics: dict,    # same keys -> metric dicts
                 out_path: Path):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), sharey=True)

    panels = [("pre", "Pre-calibration"),
              ("platt", "Post — Platt"),
              ("isotonic", "Post — Isotonic")]

    for ax, (key, title) in zip(axes, panels):
        _add_panel(ax, y_true, probs[key],
                   label=f"{model_name} ({key})",
                   color=METHOD_COLORS[key],
                   metrics=metrics[key])
        ax.set_title(title, fontsize=10, pad=6)

    fig.suptitle(
        f"Reliability Diagrams — {model_name}  (UCI test set, pre vs. post-calibration)",
        fontsize=11, y=1.01,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("Task 4.3 — Post-Calibration Metrics (UCI test set)")
    print("=" * 65)

    # ── 1. Load data and test indices ────────────────────────────
    df = pd.read_csv(DATA_FILE)
    with open(SPLIT_FILE) as f:
        splits = json.load(f)

    feature_cols = [c for c in df.columns if c != "class"]
    X = df[feature_cols].values
    y = df["class"].values

    idx_test = splits["test"]
    X_test, y_test = X[idx_test], y[idx_test]
    print(f"\n[1] Test fold: {len(y_test)} samples  "
          f"(CKD={y_test.sum()}, notCKD={(y_test==0).sum()})")

    # ── 2. Collect probabilities and metrics for all variants ────
    print(f"\n[2] Scoring models on test set ...\n")

    rows_platt    = []
    rows_isotonic = []

    for name in MODEL_NAMES:
        base     = joblib.load(MODELS_DIR / f"{name}.pkl")
        platt    = joblib.load(MODELS_DIR / f"platt_{name}.pkl")
        isotonic = joblib.load(MODELS_DIR / f"isotonic_{name}.pkl")

        prob_pre      = base.predict_proba(X_test)[:, 1]
        prob_platt    = platt.predict_proba(X_test)[:, 1]
        prob_isotonic = isotonic.predict_proba(X_test)[:, 1]

        m_pre      = calibration_metrics(y_test, prob_pre)
        m_platt    = calibration_metrics(y_test, prob_platt)
        m_isotonic = calibration_metrics(y_test, prob_isotonic)

        # ECE reduction (positive = improvement)
        ece_red_platt    = round(m_pre["ece"] - m_platt["ece"],    4)
        ece_red_isotonic = round(m_pre["ece"] - m_isotonic["ece"], 4)

        print(f"  {name}")
        print(f"    pre      : ECE={m_pre['ece']:.4f}  "
              f"Brier={m_pre['brier']:.4f}")
        print(f"    platt    : ECE={m_platt['ece']:.4f}  "
              f"Brier={m_platt['brier']:.4f}  "
              f"ECE_red={ece_red_platt:+.4f}")
        print(f"    isotonic : ECE={m_isotonic['ece']:.4f}  "
              f"Brier={m_isotonic['brier']:.4f}  "
              f"ECE_red={ece_red_isotonic:+.4f}")

        rows_platt.append({
            "model"        : name,
            "ece_pre"      : m_pre["ece"],
            "ece_post"     : m_platt["ece"],
            "ece_reduction": ece_red_platt,
            "mce_post"     : m_platt["mce"],
            "brier_pre"    : m_pre["brier"],
            "brier_post"   : m_platt["brier"],
            "bss_post"     : m_platt["bss"],
        })
        rows_isotonic.append({
            "model"        : name,
            "ece_pre"      : m_pre["ece"],
            "ece_post"     : m_isotonic["ece"],
            "ece_reduction": ece_red_isotonic,
            "mce_post"     : m_isotonic["mce"],
            "brier_pre"    : m_pre["brier"],
            "brier_post"   : m_isotonic["brier"],
            "bss_post"     : m_isotonic["bss"],
        })

        # Reliability diagram
        plot_compare(
            name, y_test,
            probs  ={"pre": prob_pre, "platt": prob_platt,
                     "isotonic": prob_isotonic},
            metrics={"pre": m_pre,   "platt": m_platt,
                     "isotonic": m_isotonic},
            out_path=FIGURES_DIR / f"reliability_compare_{name}.png",
        )

    # ── 3. Save tables ────────────────────────────────────────────
    df_platt    = pd.DataFrame(rows_platt)
    df_isotonic = pd.DataFrame(rows_isotonic)

    df_platt.to_csv(TABLE_DIR / "t_calibration_postcal_platt.csv",
                    index=False)
    df_isotonic.to_csv(TABLE_DIR / "t_calibration_postcal_isotonic.csv",
                       index=False)
    print(f"\n[3] Saved tables:")
    print(f"    tables/t_calibration_postcal_platt.csv")
    print(f"    tables/t_calibration_postcal_isotonic.csv")

    figs = sorted(FIGURES_DIR.glob("reliability_compare_*.png"))
    print(f"[4] Saved {len(figs)} comparison figures: "
          f"{[p.name for p in figs]}")

    # ── 4. Sanity checks ─────────────────────────────────────────
    print("\n[5] Sanity checks:")
    assert len(df_platt)    == 5
    assert len(df_isotonic) == 5
    assert "ece_reduction" in df_platt.columns
    assert "ece_reduction" in df_isotonic.columns
    assert len(figs) == 5
    print("  [PASS] both tables have 5 rows with ece_reduction column")
    print("  [PASS] 5 comparison figures saved")

    # ── 5. Summary ────────────────────────────────────────────────
    print("\n--- Platt ---")
    print(df_platt[["model","ece_pre","ece_post",
                     "ece_reduction","brier_post"]].to_string(index=False))
    print("\n--- Isotonic ---")
    print(df_isotonic[["model","ece_pre","ece_post",
                        "ece_reduction","brier_post"]].to_string(index=False))
    print("\nDONE")


if __name__ == "__main__":
    main()
