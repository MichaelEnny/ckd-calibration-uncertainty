"""
Task 5.2 — Fit Conformal Predictors (UCI)
-------------------------------------------
Uses Split Conformal Prediction (MAPIE 1.3 SplitConformalClassifier) to wrap
each of the 5 tuned base models.  The UCI validation set is used as the
conformalization set; the UCI test set is the evaluation fold.

Method    : Split CP, conformity score = 'lac' (1 - p_hat(y|x))
Coverage  : 1 - alpha = 0.90
Library   : MAPIE 1.3.0

Inputs : data/processed/uci_ckd_clean.csv
         data/processed/uci_splits.json
         code/02_modeling/saved_models/*.pkl  (5 base models)

Outputs: tables/t_conformal_uci.csv
         models/conformal_*.pkl              — fitted SplitConformalClassifier objects
"""

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from mapie.classification import SplitConformalClassifier

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).resolve().parents[2]
DATA_FILE   = ROOT / "data" / "processed" / "uci_ckd_clean.csv"
SPLIT_FILE  = ROOT / "data" / "processed" / "uci_splits.json"
MODELS_DIR  = ROOT / "code" / "02_modeling" / "saved_models"
CP_DIR      = ROOT / "models"
TABLE_DIR   = ROOT / "tables"

CP_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES    = ["LR", "RF", "XGB", "SVM", "NB"]
CONFIDENCE     = 0.90   # 1 - alpha
RANDOM_STATE   = 42


def prediction_set_metrics(y_true: np.ndarray,
                            pred_sets: np.ndarray) -> dict:
    """
    pred_sets : bool array of shape (n_samples, n_classes)
                pred_sets[i, c] = True means class c is in the set for sample i
    """
    n = len(y_true)

    # Empirical coverage: true label is inside the prediction set
    covered = np.array([
        bool(pred_sets[i, y_true[i]])
        for i in range(n)
    ])
    coverage = covered.mean()

    # Average prediction set size
    set_sizes = pred_sets.sum(axis=1)
    avg_size  = set_sizes.mean()

    # Singleton rate: exactly one class in the set
    singleton_rate = (set_sizes == 1).mean()

    # Empty set rate (should be near 0)
    empty_rate = (set_sizes == 0).mean()

    return {
        "coverage"      : round(float(coverage),       4),
        "avg_set_size"  : round(float(avg_size),        4),
        "singleton_rate": round(float(singleton_rate),  4),
        "empty_rate"    : round(float(empty_rate),      4),
    }


def main():
    print("=" * 65)
    print("Task 5.2 — Split Conformal Prediction (UCI)")
    print(f"           confidence_level={CONFIDENCE}  (alpha={1-CONFIDENCE:.2f})")
    print("=" * 65)

    # ── 1. Load data and indices ─────────────────────────────────
    df = pd.read_csv(DATA_FILE)
    with open(SPLIT_FILE) as f:
        splits = json.load(f)

    feature_cols = [c for c in df.columns if c != "class"]
    X = df[feature_cols].values
    y = df["class"].values

    idx_val  = splits["val"]
    idx_test = splits["test"]

    X_val,  y_val  = X[idx_val],  y[idx_val]
    X_test, y_test = X[idx_test], y[idx_test]

    print(f"\n[1] Val  fold : {len(y_val)} samples  "
          f"(CKD={y_val.sum()}, notCKD={(y_val==0).sum()})")
    print(f"    Test fold : {len(y_test)} samples  "
          f"(CKD={y_test.sum()}, notCKD={(y_test==0).sum()})")

    # ── 2. Fit and evaluate each model ───────────────────────────
    print(f"\n[2] Fitting conformal wrappers and predicting ...\n")
    rows = []

    for name in MODEL_NAMES:
        base = joblib.load(MODELS_DIR / f"{name}.pkl")

        # prefit=True: base model already fitted; conformalize() uses val set
        cp = SplitConformalClassifier(
            estimator=base,
            confidence_level=CONFIDENCE,
            conformity_score="lac",
            prefit=True,
            random_state=RANDOM_STATE,
        )
        cp.conformalize(X_val, y_val)

        # predict_set returns (point_preds, set_array)
        # set_array shape: (n_samples, n_classes, n_confidence_levels)
        _, set_raw = cp.predict_set(X_test)
        pred_sets = set_raw[:, :, 0]   # squeeze confidence-level dim -> (n, 2)

        metrics = prediction_set_metrics(y_test, pred_sets)

        # Point predictions for reference
        y_pred = base.predict(X_test)
        point_acc = (y_pred == y_test).mean()

        print(f"  {name:4s}  coverage={metrics['coverage']:.4f}  "
              f"avg_size={metrics['avg_set_size']:.4f}  "
              f"singleton={metrics['singleton_rate']:.4f}  "
              f"empty={metrics['empty_rate']:.4f}  "
              f"(point_acc={point_acc:.4f})")

        # Save conformal model
        joblib.dump(cp, CP_DIR / f"conformal_{name}.pkl")

        rows.append({"model": name, **metrics})

    # ── 3. Save results table ─────────────────────────────────────
    result   = pd.DataFrame(rows)
    out_path = TABLE_DIR / "t_conformal_uci.csv"
    result.to_csv(out_path, index=False)
    print(f"\n[3] Saved -> tables/t_conformal_uci.csv")

    cp_files = sorted(CP_DIR.glob("conformal_*.pkl"))
    print(f"[4] Saved {len(cp_files)} conformal models -> "
          f"{[p.name for p in cp_files]}")

    # ── 4. Sanity checks ─────────────────────────────────────────
    print("\n[5] Sanity checks:")
    below_coverage = result[result["coverage"] < CONFIDENCE]
    if len(below_coverage):
        print(f"  [WARN] Models below {CONFIDENCE} coverage: "
              f"{below_coverage['model'].tolist()}")
    else:
        print(f"  [PASS] All models achieve coverage >= {CONFIDENCE}")
    assert len(result) == 5
    assert len(cp_files) == 5
    print(f"  [PASS] 5 rows in table, 5 conformal model files saved")

    # ── 5. Summary ────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print(result.to_string(index=False))
    print("=" * 65)
    print("\nDONE")


if __name__ == "__main__":
    main()
