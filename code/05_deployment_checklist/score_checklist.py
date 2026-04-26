"""
Tasks 6.3 + 6.4 — Deployment Readiness Scoring + Heatmap
----------------------------------------------------------
Scores each model's best-calibrated variant against the 8 deployment
readiness criteria defined in the task document.

Criteria and thresholds
-----------------------
  1  Discrimination adequacy   AUROC >= 0.85  (MIMIC)
  2  Calibration adequacy      ECE   <= 0.10  (MIMIC)
  3  Calibration stability     delta_ECE <= 0.05  (MIMIC - UCI)
  4  Uncertainty coverage      conformal coverage >= 0.90  (MIMIC)
  5  Coverage stability        delta_coverage <= 0.05  (UCI - MIMIC)
  6  Prediction interpretability singleton_rate >= 0.70  (MIMIC)
  7  Subgroup calibration equity max_subgroup_ECE_gap <= 0.05
  8  Transparency              always PASS (code repo exists)

Scores: PASS=2 | MARGINAL=1 | FAIL=0
MARGINAL = within 20% of threshold (e.g. AUROC 0.80-0.85)

Outputs
-------
  tables/T4_deployment_checklist.csv
  figures/F4_deployment_heatmap.png
"""

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT        = Path(__file__).resolve().parents[2]
TABLE_DIR   = ROOT / "tables"
FIGURES_DIR = ROOT / "figures"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES = ["LR", "RF", "XGB", "SVM", "NB"]

THRESHOLDS = {
    "auroc_mimic"       : (0.85, "ge"),   # >= threshold
    "ece_mimic"         : (0.10, "le"),   # <= threshold
    "delta_ece"         : (0.05, "le_abs"),
    "coverage_mimic"    : (0.90, "ge"),
    "delta_coverage"    : (0.05, "le_abs"),
    "singleton_mimic"   : (0.70, "ge"),
    "subgroup_gap"      : (0.05, "le"),
}

CRITERIA_LABELS = [
    "1. Discrimination\n(AUROC>=0.85)",
    "2. Calibration\n(ECE<=0.10)",
    "3. Calib Stability\n(dECE<=0.05)",
    "4. CP Coverage\n(>=0.90)",
    "5. Cover Stability\n(dCov<=0.05)",
    "6. Interpretability\n(Singleton>=0.70)",
    "7. Subgroup Equity\n(Gap<=0.05)",
    "8. Transparency\n(Code public)",
]


def score(value, threshold, direction):
    """Return 2=PASS, 1=MARGINAL, 0=FAIL."""
    if np.isnan(value):
        return 0
    if direction == "ge":
        if value >= threshold:          return 2
        if value >= threshold * 0.80:   return 1
        return 0
    elif direction == "le":
        if value <= threshold:          return 2
        if value <= threshold * 1.20:   return 1
        return 0
    elif direction == "le_abs":
        av = abs(value)
        if av <= threshold:             return 2
        if av <= threshold * 1.20:      return 1
        return 0
    return 0


def score_label(s):
    return {2: "PASS", 1: "MARGINAL", 0: "FAIL"}[s]


def main():
    print("=" * 65)
    print("Tasks 6.3 + 6.4 - Deployment Readiness Scoring + Heatmap")
    print("=" * 65)

    # ── Load source tables ────────────────────────────────────────
    t2 = pd.read_csv(TABLE_DIR / "T2_calibration_summary.csv")
    t3 = pd.read_csv(TABLE_DIR / "T3_uncertainty_summary.csv")
    sg = pd.read_csv(TABLE_DIR / "t_subgroup_calibration.csv")

    # compute max subgroup ECE gap
    sg_cols = [c for c in sg.columns if c not in ("model", "overall")]
    sg["max_gap"] = sg[sg_cols].max(axis=1) - sg[sg_cols].min(axis=1)

    rows       = []
    score_grid = []   # 5 models x 8 criteria

    print(f"\n[1] Scoring models ...\n")
    for name in MODEL_NAMES:
        r2 = t2[t2["model"] == name].iloc[0]
        r3 = t3[t3["model"] == name].iloc[0]
        rs = sg[sg["model"] == name].iloc[0]

        vals = {
            "auroc_mimic"    : float(r2["mimic_auroc"]),
            "ece_mimic"      : float(r2["mimic_ece"]),
            "delta_ece"      : float(r2["calibration_drift"]),
            "coverage_mimic" : float(r3["mimic_coverage"]),
            "delta_coverage" : float(r3["coverage_drift"]),
            "singleton_mimic": float(r3["mimic_singleton_rate"]),
            "subgroup_gap"   : float(rs["max_gap"]) if not np.isnan(rs["max_gap"]) else np.nan,
        }

        scores = [score(vals[k], *THRESHOLDS[k]) for k in THRESHOLDS]
        scores.append(2)   # criterion 8 always PASS
        score_grid.append(scores)

        total = sum(scores)
        labels = [score_label(s) for s in scores]

        print(f"  {name}  [{' | '.join(f'{l[:4]}' for l in labels)}]  "
              f"total={total}/16")

        rows.append({
            "model"                 : name,
            "calibration_method"    : r2["calibration_method"],
            "c1_discrimination"     : score_label(scores[0]),
            "c2_calibration"        : score_label(scores[1]),
            "c3_calib_stability"    : score_label(scores[2]),
            "c4_cp_coverage"        : score_label(scores[3]),
            "c5_cover_stability"    : score_label(scores[4]),
            "c6_interpretability"   : score_label(scores[5]),
            "c7_subgroup_equity"    : score_label(scores[6]),
            "c8_transparency"       : score_label(scores[7]),
            "total_score"           : total,
            "max_possible"          : 16,
        })

    result = pd.DataFrame(rows)
    result.to_csv(TABLE_DIR / "T4_deployment_checklist.csv", index=False)
    print(f"\n[2] Saved: tables/T4_deployment_checklist.csv")

    # ── Heatmap ───────────────────────────────────────────────────
    grid = np.array(score_grid, dtype=float)   # (5, 8)

    COLOR_MAP = {0: "#EF5350", 1: "#FFA726", 2: "#66BB6A"}
    fig, ax = plt.subplots(figsize=(11, 4))

    for i, model in enumerate(MODEL_NAMES):
        for j in range(8):
            s = int(grid[i, j])
            ax.add_patch(plt.Rectangle(
                (j, len(MODEL_NAMES) - 1 - i), 1, 1,
                color=COLOR_MAP[s], linewidth=0.5, edgecolor="white"))
            ax.text(j + 0.5, len(MODEL_NAMES) - 0.5 - i,
                    score_label(s), ha="center", va="center",
                    fontsize=8.5, fontweight="bold",
                    color="white" if s in (0, 2) else "black")

    ax.set_xlim(0, 8)
    ax.set_ylim(0, len(MODEL_NAMES))
    ax.set_xticks(np.arange(8) + 0.5)
    ax.set_xticklabels(CRITERIA_LABELS, fontsize=7.5, ha="center")
    ax.set_yticks(np.arange(len(MODEL_NAMES)) + 0.5)
    ax.set_yticklabels(MODEL_NAMES[::-1], fontsize=9)
    ax.set_title("Deployment Readiness Heatmap", fontsize=12, pad=10)
    ax.tick_params(length=0)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#66BB6A", label="PASS"),
        Patch(facecolor="#FFA726", label="MARGINAL"),
        Patch(facecolor="#EF5350", label="FAIL"),
    ]
    ax.legend(handles=legend_elements, loc="lower right",
              bbox_to_anchor=(1.0, -0.22), ncol=3, fontsize=9,
              framealpha=0.9)

    # Total scores on right
    ax2 = ax.twinx()
    ax2.set_ylim(0, len(MODEL_NAMES))
    ax2.set_yticks(np.arange(len(MODEL_NAMES)) + 0.5)
    totals = result["total_score"].values[::-1]
    ax2.set_yticklabels([f"{t}/16" for t in totals], fontsize=8)
    ax2.tick_params(length=0)

    fig.tight_layout()
    out_path = FIGURES_DIR / "F4_deployment_heatmap.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[3] Saved: figures/F4_deployment_heatmap.png")

    print("\n" + "=" * 65)
    cols_show = ["model", "calibration_method", "total_score",
                 "c1_discrimination", "c2_calibration",
                 "c3_calib_stability", "c4_cp_coverage"]
    print(result[cols_show].to_string(index=False))
    print("=" * 65)
    print("\nDONE")


if __name__ == "__main__":
    main()
