"""
Task 4.1 — Pre-Calibration Assessment
---------------------------------------
Evaluates the raw (uncalibrated) probability outputs of all 5 tuned models
on the UCI validation set.  The validation set is used here — NOT the test
set — to mirror the workflow where calibration is diagnosed and tuned before
the test set is ever touched.

Metrics per model
-----------------
  ECE   — Expected Calibration Error  (netcal, 10 equal-width bins)
  MCE   — Maximum Calibration Error   (netcal, 10 equal-width bins)
  Brier — Brier Score                 (sklearn)
  BSS   — Brier Skill Score vs. naive climatology baseline

Outputs
-------
  tables/t_calibration_precal.csv     — metrics table
  figures/reliability_pre_<model>.png — reliability diagram per model
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

# Colour palette — one per model, consistent across the paper
MODEL_COLORS = {
    "LR" : "#2196F3",
    "RF" : "#4CAF50",
    "XGB": "#FF5722",
    "SVM": "#9C27B0",
    "NB" : "#FF9800",
}


def brier_skill_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """BSS = 1 - BS_model / BS_climatology.  Climatology = mean(y_true)."""
    bs_model = brier_score_loss(y_true, y_prob)
    bs_clim  = brier_score_loss(y_true,
                                np.full_like(y_prob, y_true.mean()))
    if bs_clim == 0:
        return 0.0
    return round(1.0 - bs_model / bs_clim, 4)


def compute_calibration_metrics(y_true: np.ndarray,
                                y_prob: np.ndarray,
                                n_bins: int = N_BINS) -> dict:
    ece_obj = ECE(bins=n_bins)
    mce_obj = MCE(bins=n_bins)

    ece_val = float(ece_obj.measure(y_prob, y_true))
    mce_val = float(mce_obj.measure(y_prob, y_true))
    bs      = brier_score_loss(y_true, y_prob)
    bss     = brier_skill_score(y_true, y_prob)

    return {
        "ece"  : round(ece_val, 4),
        "mce"  : round(mce_val, 4),
        "brier": round(bs,      4),
        "bss"  : bss,
    }


def plot_reliability_diagram(name: str,
                              y_true: np.ndarray,
                              y_prob: np.ndarray,
                              metrics: dict,
                              out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(5, 5))

    disp = CalibrationDisplay.from_predictions(
        y_true, y_prob,
        n_bins=N_BINS,
        ax=ax,
        color=MODEL_COLORS.get(name, "#333333"),
        label=name,
        name=name,
    )

    # Perfect calibration reference line already drawn by CalibrationDisplay;
    # add annotation box with metrics
    textstr = (
        f"ECE  = {metrics['ece']:.4f}\n"
        f"MCE  = {metrics['mce']:.4f}\n"
        f"Brier= {metrics['brier']:.4f}\n"
        f"BSS  = {metrics['bss']:.4f}"
    )
    ax.text(
        0.03, 0.97, textstr,
        transform=ax.transAxes,
        fontsize=8,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                  edgecolor="#CCCCCC", alpha=0.9),
    )

    ax.set_title(f"Reliability Diagram — {name} (pre-calibration)",
                 fontsize=11, pad=10)
    ax.set_xlabel("Mean predicted probability", fontsize=9)
    ax.set_ylabel("Fraction of positives", fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(loc="lower right", fontsize=8)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    print("=" * 60)
    print("Task 4.1 — Pre-Calibration Assessment (UCI validation set)")
    print("=" * 60)

    # ── 1. Load data and val indices ─────────────────────────────
    df = pd.read_csv(DATA_FILE)
    with open(SPLIT_FILE) as f:
        splits = json.load(f)

    feature_cols = [c for c in df.columns if c != "class"]
    X = df[feature_cols].values
    y = df["class"].values

    idx_val = splits["val"]
    X_val, y_val = X[idx_val], y[idx_val]
    print(f"\n[1] Validation fold: {len(y_val)} samples  "
          f"(CKD={y_val.sum()}, notCKD={(y_val==0).sum()})")
    print(f"    Prevalence (climatology): {y_val.mean():.4f}")

    # ── 2. Assess each model ─────────────────────────────────────
    print(f"\n[2] Computing calibration metrics ({N_BINS} bins) ...\n")
    rows = []
    for name in MODEL_NAMES:
        model  = joblib.load(MODELS_DIR / f"{name}.pkl")
        y_prob = model.predict_proba(X_val)[:, 1]

        metrics = compute_calibration_metrics(y_val, y_prob)
        print(f"  {name:4s}  ECE={metrics['ece']:.4f}  "
              f"MCE={metrics['mce']:.4f}  "
              f"Brier={metrics['brier']:.4f}  "
              f"BSS={metrics['bss']:.4f}")

        # Reliability diagram
        fig_path = FIGURES_DIR / f"reliability_pre_{name}.png"
        plot_reliability_diagram(name, y_val, y_prob, metrics, fig_path)

        rows.append({"model": name, **metrics})

    # ── 3. Save metrics table ─────────────────────────────────────
    result   = pd.DataFrame(rows)
    out_path = TABLE_DIR / "t_calibration_precal.csv"
    result.to_csv(out_path, index=False)
    print(f"\n[3] Saved metrics -> tables/t_calibration_precal.csv")

    saved_figs = sorted(FIGURES_DIR.glob("reliability_pre_*.png"))
    print(f"[4] Saved {len(saved_figs)} reliability diagrams -> "
          f"{[p.name for p in saved_figs]}")

    # ── 4. Sanity checks ─────────────────────────────────────────
    print("\n[5] Sanity checks:")
    assert len(result) == 5
    assert set(result.columns) == {"model", "ece", "mce", "brier", "bss"}
    assert len(saved_figs) == 5
    print("  [PASS] 5 rows, 4 metric columns, 5 figures")

    # ── 5. Summary table ──────────────────────────────────────────
    print("\n" + "=" * 60)
    print(result.to_string(index=False))
    print("=" * 60)
    print("\nDONE")


if __name__ == "__main__":
    main()
