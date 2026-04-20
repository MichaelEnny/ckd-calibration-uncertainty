"""
Task 3.3 — Hyperparameter Tuning
----------------------------------
For each of the 5 classifiers, perform RandomizedSearchCV (or GridSearchCV
where the grid is small) on the TRAINING fold only, optimising AUROC via
5-fold stratified cross-validation.

Split source : data/processed/uci_splits.json  (70/15/15, random_state=42)
Data source  : data/processed/uci_ckd_clean.csv

Outputs
-------
  tables/t_hyperparams.csv              — best params + CV AUROC per model
  code/02_modeling/saved_models/*.pkl   — 5 fitted model objects
"""

import json
import time
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

warnings.filterwarnings("ignore", category=UserWarning)

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).resolve().parents[2]
DATA_FILE   = ROOT / "data" / "processed" / "uci_ckd_clean.csv"
SPLIT_FILE  = ROOT / "data" / "processed" / "uci_splits.json"
MODELS_DIR  = Path(__file__).parent / "saved_models"
TABLE_DIR   = ROOT / "tables"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
CV_FOLDS     = 5
N_ITER       = 30        # RandomizedSearchCV iterations (where used)

# ── Search spaces ────────────────────────────────────────────────────────────
# Each entry: (estimator, param_dist, use_randomized)
# Pipeline estimators prefix params with step name + "__".

SEARCH_CONFIGS = {
    "LR": (
        Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(solver="lbfgs", max_iter=2000,
                                       random_state=RANDOM_STATE)),
        ]),
        {
            "clf__C": [0.001, 0.01, 0.1, 1, 10, 100],
        },
        False,   # small grid -> GridSearchCV-style exhaustive via n_iter=all
    ),
    "RF": (
        RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
        {
            "n_estimators"     : [100, 200, 300, 500],
            "max_depth"        : [None, 5, 10, 20],
            "min_samples_split": [2, 5, 10],
            "max_features"     : ["sqrt", "log2"],
        },
        True,
    ),
    "XGB": (
        XGBClassifier(eval_metric="logloss", random_state=RANDOM_STATE,
                      n_jobs=-1),
        {
            "n_estimators"    : [100, 200, 300, 500],
            "learning_rate"   : [0.01, 0.05, 0.1, 0.2],
            "max_depth"       : [3, 4, 6, 8],
            "subsample"       : [0.6, 0.8, 1.0],
            "colsample_bytree": [0.6, 0.8, 1.0],
            "gamma"           : [0, 0.1, 0.5],
        },
        True,
    ),
    "SVM": (
        Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(probability=True, random_state=RANDOM_STATE)),
        ]),
        {
            "clf__C"    : [0.1, 1, 10, 100],
            "clf__gamma": ["scale", "auto", 0.001, 0.01, 0.1],
            "clf__kernel": ["rbf", "poly"],
        },
        True,
    ),
    "NB": (
        GaussianNB(),
        {
            "var_smoothing": np.logspace(-11, -7, 20),
        },
        True,
    ),
}


def run_search(name, estimator, param_dist, randomized,
               X_train, y_train):
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True,
                         random_state=RANDOM_STATE)

    n_iter = min(N_ITER, 1)   # will be overridden below
    if randomized:
        # Compute product of grid; cap at N_ITER
        from itertools import product as iproduct
        grid_size = 1
        for v in param_dist.values():
            grid_size *= len(v)
        n_iter = min(N_ITER, grid_size)

        search = RandomizedSearchCV(
            estimator, param_distributions=param_dist,
            n_iter=n_iter, scoring="roc_auc", cv=cv,
            random_state=RANDOM_STATE, n_jobs=-1, refit=True,
        )
    else:
        from sklearn.model_selection import GridSearchCV
        search = GridSearchCV(
            estimator, param_grid=param_dist,
            scoring="roc_auc", cv=cv,
            n_jobs=-1, refit=True,
        )

    t0 = time.time()
    search.fit(X_train, y_train)
    elapsed = time.time() - t0

    return search.best_estimator_, search.best_params_, \
           search.best_score_, elapsed


def flatten_params(params: dict) -> dict:
    """Strip pipeline prefixes (clf__C -> C) for readable table output."""
    return {k.split("__")[-1]: v for k, v in params.items()}


def main():
    print("=" * 65)
    print("Task 3.3 — Hyperparameter Tuning (5-fold CV, metric=AUROC)")
    print("=" * 65)

    # ── 1. Load data and split indices ───────────────────────────
    df = pd.read_csv(DATA_FILE)
    with open(SPLIT_FILE) as f:
        splits = json.load(f)

    feature_cols = [c for c in df.columns if c != "class"]
    X = df[feature_cols].values
    y = df["class"].values

    idx_train = splits["train"]
    X_train, y_train = X[idx_train], y[idx_train]
    print(f"\n[1] Training fold: {len(y_train)} samples  "
          f"(CKD={y_train.sum()}, notCKD={(y_train==0).sum()})")

    # ── 2. Tune each model ───────────────────────────────────────
    print(f"\n[2] Running search (CV={CV_FOLDS} folds, max_iter={N_ITER}) ...\n")
    rows = []
    for name, (estimator, param_dist, randomized) in SEARCH_CONFIGS.items():
        print(f"  {name} ... ", end="", flush=True)
        best_model, best_params, best_cv_auc, elapsed = run_search(
            name, estimator, param_dist, randomized, X_train, y_train
        )
        flat = flatten_params(best_params)
        print(f"CV-AUC={best_cv_auc:.4f}  ({elapsed:.1f}s)")

        # Save model
        out_path = MODELS_DIR / f"{name}.pkl"
        joblib.dump(best_model, out_path)

        rows.append({
            "model"       : name,
            "cv_auc_mean" : round(best_cv_auc, 4),
            "best_params" : str(flat),
            **{f"param_{k}": v for k, v in flat.items()},
        })

    # ── 3. Save hyperparameter table ─────────────────────────────
    summary_cols = ["model", "cv_auc_mean", "best_params"]
    summary = pd.DataFrame(rows)[summary_cols]
    out_csv = TABLE_DIR / "t_hyperparams.csv"
    summary.to_csv(out_csv, index=False)
    print(f"\n[3] Saved hyperparameter table -> tables/t_hyperparams.csv")

    # ── 4. Verify saved models ───────────────────────────────────
    saved = list(MODELS_DIR.glob("*.pkl"))
    print(f"\n[4] Models in saved_models/: {sorted(p.name for p in saved)}")
    assert len(saved) == 5, f"Expected 5 .pkl files, found {len(saved)}"
    print("    [PASS] all 5 model files present")

    # ── 5. Print summary ─────────────────────────────────────────
    print("\n" + "=" * 65)
    print(summary.to_string(index=False))
    print("=" * 65)
    print("\nDONE")


if __name__ == "__main__":
    main()
