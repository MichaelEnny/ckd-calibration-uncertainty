"""
Task 3.4 — Baseline Discrimination Metrics
--------------------------------------------
Loads the 5 tuned models from saved_models/ and evaluates each on the
UCI test set (held-out 15%, never seen during training or calibration).

Metrics: AUROC, AUPRC, F1, Accuracy, Sensitivity (Recall), Specificity

Inputs : data/processed/uci_ckd_clean.csv
         data/processed/uci_splits.json
         code/02_modeling/saved_models/*.pkl

Outputs: tables/t_baseline_discrimination.csv
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parents[2]
DATA_FILE  = ROOT / "data" / "processed" / "uci_ckd_clean.csv"
SPLIT_FILE = ROOT / "data" / "processed" / "uci_splits.json"
MODELS_DIR = Path(__file__).parent / "saved_models"
TABLE_DIR  = ROOT / "tables"

TABLE_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES = ["LR", "RF", "XGB", "SVM", "NB"]


def compute_metrics(y_true, y_pred, y_prob) -> dict:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    return {
        "auroc"      : round(roc_auc_score(y_true, y_prob), 4),
        "auprc"      : round(average_precision_score(y_true, y_prob), 4),
        "f1"         : round(f1_score(y_true, y_pred), 4),
        "accuracy"   : round(accuracy_score(y_true, y_pred), 4),
        "sensitivity": round(sensitivity, 4),
        "specificity": round(specificity, 4),
    }


def main():
    print("=" * 60)
    print("Task 3.4 — Baseline Discrimination Metrics (UCI test set)")
    print("=" * 60)

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

    # ── 2. Evaluate each model ───────────────────────────────────
    print(f"\n[2] Evaluating {len(MODEL_NAMES)} models ...\n")
    rows = []
    for name in MODEL_NAMES:
        model = joblib.load(MODELS_DIR / f"{name}.pkl")
        y_prob = model.predict_proba(X_test)[:, 1]
        y_pred = model.predict(X_test)
        metrics = compute_metrics(y_test, y_pred, y_prob)
        print(f"  {name:4s}  AUROC={metrics['auroc']:.4f}  "
              f"AUPRC={metrics['auprc']:.4f}  "
              f"F1={metrics['f1']:.4f}  "
              f"Acc={metrics['accuracy']:.4f}  "
              f"Sens={metrics['sensitivity']:.4f}  "
              f"Spec={metrics['specificity']:.4f}")
        rows.append({"model": name, **metrics})

    # ── 3. Save table ─────────────────────────────────────────────
    result = pd.DataFrame(rows)
    out_path = TABLE_DIR / "t_baseline_discrimination.csv"
    result.to_csv(out_path, index=False)
    print(f"\n[3] Saved -> tables/t_baseline_discrimination.csv")

    # ── 4. Sanity checks ─────────────────────────────────────────
    print("\n[4] Sanity checks:")
    assert len(result) == 5, f"Expected 5 rows, got {len(result)}"
    assert set(result.columns) == {
        "model", "auroc", "auprc", "f1", "accuracy", "sensitivity", "specificity"
    }
    below_threshold = result[result["auroc"] < 0.85]
    if len(below_threshold):
        print(f"  [WARN] Models below AUROC 0.85: "
              f"{below_threshold['model'].tolist()}")
    else:
        print(f"  [PASS] All models AUROC >= 0.85")
    print(f"  [PASS] Table has {len(result)} rows and "
          f"{len(result.columns)-1} metric columns")

    # ── 5. Print final table ──────────────────────────────────────
    print("\n" + "=" * 60)
    print(result.to_string(index=False))
    print("=" * 60)
    print("\nDONE")


if __name__ == "__main__":
    main()
