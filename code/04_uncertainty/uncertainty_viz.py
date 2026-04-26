"""
Task 5.4 — Uncertainty Visualization (UCI component)
------------------------------------------------------
Produces two figures for the UCI test set using the fitted conformal predictors.

Figure 1 — Set-size distribution histogram (all 5 models, 1 panel each)
  figures/conformal_setsize_uci.png

Figure 2 — Sample case display (best model only: NB)
  50 test cases as a horizontal bar chart showing:
    - predicted probability (bar length)
    - prediction set label: CKD / Not-CKD / Ambiguous (colour)
    - true label marker
  figures/conformal_sample_uci.png

Best model selection: NB (highest coverage=0.984, singleton_rate=1.0, Task 5.2)

MIMIC component (conformal_setsize_mimic.png) is deferred until MIMIC data
is available (see MIMIC_BLOCKED_TASKS.md).
"""

import json
import warnings
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).resolve().parents[2]
DATA_FILE   = ROOT / "data" / "processed" / "uci_ckd_clean.csv"
SPLIT_FILE  = ROOT / "data" / "processed" / "uci_splits.json"
MODELS_DIR  = ROOT / "code" / "02_modeling" / "saved_models"
CP_DIR      = ROOT / "models"
FIGURES_DIR = ROOT / "figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES  = ["LR", "RF", "XGB", "SVM", "NB"]
BEST_MODEL   = "NB"
CONFIDENCE   = 0.90
N_SAMPLE     = 50          # cases to show in Figure 2

MODEL_COLORS = {
    "LR" : "#2196F3",
    "RF" : "#4CAF50",
    "XGB": "#FF5722",
    "SVM": "#9C27B0",
    "NB" : "#FF9800",
}

SET_COLORS = {
    "CKD"      : "#E53935",   # red
    "Not-CKD"  : "#1E88E5",   # blue
    "Ambiguous": "#FDD835",   # yellow
    "Empty"    : "#9E9E9E",   # grey
}


def get_pred_sets(cp, X):
    """Return bool array (n, 2) from SplitConformalClassifier.predict_set."""
    _, raw = cp.predict_set(X)
    return raw[:, :, 0]


def set_label(row: np.ndarray) -> str:
    """Convert a 2-element bool row to a human-readable label."""
    ckd, notckd = row[1], row[0]
    if ckd and not notckd:
        return "CKD"
    if notckd and not ckd:
        return "Not-CKD"
    if ckd and notckd:
        return "Ambiguous"
    return "Empty"


# ── Figure 1 — Set-size histograms ───────────────────────────────────────────

def plot_setsize_histograms(X_test, y_test, out_path: Path):
    fig, axes = plt.subplots(1, 5, figsize=(16, 3.8), sharey=False)

    for ax, name in zip(axes, MODEL_NAMES):
        cp        = joblib.load(CP_DIR / f"conformal_{name}.pkl")
        pred_sets = get_pred_sets(cp, X_test)
        sizes     = pred_sets.sum(axis=1)

        counts = {s: int((sizes == s).sum()) for s in [0, 1, 2]}
        bars   = ax.bar(
            [0, 1, 2],
            [counts[0], counts[1], counts[2]],
            color=[SET_COLORS["Empty"],
                   MODEL_COLORS[name],
                   SET_COLORS["Ambiguous"]],
            edgecolor="white", linewidth=0.8,
        )

        coverage = float((pred_sets[np.arange(len(y_test)), y_test]).mean())
        singleton = float((sizes == 1).mean())

        ax.set_title(name, fontsize=11, fontweight="bold",
                     color=MODEL_COLORS[name])
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(["Empty\n(0)", "Singleton\n(1)", "Ambiguous\n(2)"],
                           fontsize=8)
        ax.set_xlabel("Prediction set size", fontsize=8)
        ax.set_ylabel("Count" if name == "LR" else "", fontsize=8)

        info = f"Cov={coverage:.3f}\nSing={singleton:.3f}"
        ax.text(0.97, 0.97, info, transform=ax.transAxes, fontsize=7.5,
                ha="right", va="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor="#CCCCCC", alpha=0.9))

        # Annotate bar counts
        for bar, cnt in zip(bars, [counts[0], counts[1], counts[2]]):
            if cnt > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.3, str(cnt),
                        ha="center", va="bottom", fontsize=8)

    fig.suptitle(
        f"Conformal Prediction Set Size Distribution — UCI Test Set "
        f"(n={len(y_test)}, coverage target={CONFIDENCE})",
        fontsize=11, y=1.02,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved -> {out_path.name}")


# ── Figure 2 — Sample case display ──────────────────────────────────────────

def plot_sample_cases(X_test, y_test, out_path: Path,
                      model_name: str = BEST_MODEL,
                      n: int = N_SAMPLE):
    base = joblib.load(MODELS_DIR / f"{model_name}.pkl")
    cp   = joblib.load(CP_DIR / f"conformal_{model_name}.pkl")

    probs     = base.predict_proba(X_test)[:, 1]
    pred_sets = get_pred_sets(cp, X_test)
    labels    = [set_label(pred_sets[i]) for i in range(len(y_test))]

    # Sort by predicted probability descending; take first n
    order  = np.argsort(probs)[::-1][:n]
    probs_s  = probs[order]
    labels_s = [labels[i] for i in order]
    true_s   = y_test[order]

    fig, ax = plt.subplots(figsize=(9, n * 0.28 + 1.5))

    y_pos = np.arange(n)
    bar_colors = [SET_COLORS[l] for l in labels_s]

    bars = ax.barh(y_pos, probs_s, color=bar_colors,
                   edgecolor="white", linewidth=0.5, height=0.75)

    # True-label markers
    for i, (prob, true_label) in enumerate(zip(probs_s, true_s)):
        marker = "★" if true_label == 1 else "○"
        color  = "#B71C1C" if true_label == 1 else "#0D47A1"
        ax.text(prob + 0.01, i, marker, va="center", ha="left",
                fontsize=7, color=color)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(
        [f"#{order[i]+1}  (true={'CKD' if true_s[i]==1 else 'notCKD'})"
         for i in range(n)],
        fontsize=6.5,
    )
    ax.invert_yaxis()
    ax.set_xlim(0, 1.15)
    ax.set_xlabel("Predicted probability of CKD", fontsize=9)
    ax.axvline(0.5, color="#555555", linestyle="--", linewidth=0.8,
               label="Decision threshold (0.5)")

    # Legend
    patches = [mpatches.Patch(color=SET_COLORS[k], label=k)
               for k in ["CKD", "Not-CKD", "Ambiguous", "Empty"]]
    patches += [mpatches.Patch(color="white", label="★ = true CKD"),
                mpatches.Patch(color="white", label="○ = true Not-CKD")]
    ax.legend(handles=patches, loc="lower right", fontsize=7,
              framealpha=0.9, ncol=2)

    ax.set_title(
        f"Conformal Prediction Sets — {model_name} on UCI Test Set "
        f"(top {n} by predicted probability, sorted descending)\n"
        f"Bar colour = prediction set label  |  coverage target = {CONFIDENCE}",
        fontsize=9, pad=8,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved -> {out_path.name}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Task 5.4 — Uncertainty Visualization (UCI)")
    print("=" * 60)

    df = pd.read_csv(DATA_FILE)
    with open(SPLIT_FILE) as f:
        splits = json.load(f)

    feature_cols = [c for c in df.columns if c != "class"]
    X = df[feature_cols].values
    y = df["class"].values

    idx_test        = splits["test"]
    X_test, y_test  = X[idx_test], y[idx_test]
    print(f"\n[1] Test fold: {len(y_test)} samples")

    print(f"\n[2] Figure 1 — set-size histograms (all 5 models):")
    plot_setsize_histograms(
        X_test, y_test,
        FIGURES_DIR / "conformal_setsize_uci.png",
    )

    print(f"\n[3] Figure 2 — sample case display (best model: {BEST_MODEL}):")
    plot_sample_cases(
        X_test, y_test,
        FIGURES_DIR / "conformal_sample_uci.png",
    )

    print("\n[4] MIMIC figures deferred -> see MIMIC_BLOCKED_TASKS.md")

    figs = sorted(FIGURES_DIR.glob("conformal_*.png"))
    print(f"\n[5] Conformal figures saved: {[p.name for p in figs]}")
    print("\nDONE")


if __name__ == "__main__":
    main()
