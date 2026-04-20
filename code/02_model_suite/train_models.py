"""
Task 3.1 — Define and Train Model Suite
-----------------------------------------
Five classifiers trained on UCI CKD data to provide breadth for calibration
comparison in subsequent tasks.

  1. Logistic Regression (LR)      — well-calibrated baseline
  2. Random Forest (RF)            — ensemble, typically overconfident
  3. XGBoost (XGB)                 — high performance, typically miscalibrated
  4. SVM with Platt scaling (SVM)  — Platt scaling built in via probability=True
  5. Gaussian Naive Bayes (NB)     — often well-calibrated on binary tasks

Inputs : data/processed/uci_ckd_clean.csv
Outputs: models/<model>.pkl          — fitted model objects
         models/split_indices.pkl    — train/test indices (seed=42, 80/20)
         tables/t_model_suite.csv    — discriminative performance summary
"""

from pathlib import Path
import numpy as np
import pandas as pd
import joblib

from sklearn.linear_model    import LogisticRegression
from sklearn.ensemble        import RandomForestClassifier
from sklearn.svm             import SVC
from sklearn.naive_bayes     import GaussianNB
from sklearn.preprocessing   import StandardScaler
from sklearn.pipeline        import Pipeline
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics         import (roc_auc_score, accuracy_score,
                                     brier_score_loss, log_loss)
from xgboost import XGBClassifier

# ── Paths ───────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parents[2]
DATA_FILE  = ROOT / "data" / "processed" / "uci_ckd_clean.csv"
MODELS_DIR = ROOT / "models"
TABLE_DIR  = ROOT / "tables"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
TEST_SIZE    = 0.20

# ── Model definitions ────────────────────────────────────────────────────────
# LR and SVM use StandardScaler pipelines; tree-based / NB do not need scaling.
MODELS = {
    "LR": Pipeline([
        ("scaler", StandardScaler()),
        ("clf",    LogisticRegression(max_iter=2000, solver="lbfgs",
                                      random_state=RANDOM_STATE)),
    ]),
    "RF": RandomForestClassifier(
        n_estimators=300, max_features="sqrt",
        random_state=RANDOM_STATE, n_jobs=-1,
    ),
    "XGB": XGBClassifier(
        n_estimators=300, learning_rate=0.05, max_depth=6,
        subsample=0.8, colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=RANDOM_STATE, n_jobs=-1,
    ),
    "SVM": Pipeline([
        ("scaler", StandardScaler()),
        ("clf",    SVC(probability=True, kernel="rbf", C=1.0,
                       random_state=RANDOM_STATE)),
    ]),
    "NB": GaussianNB(),
}


def evaluate(name: str, model, X_train, X_test, y_train, y_test) -> dict:
    model.fit(X_train, y_train)
    prob_test  = model.predict_proba(X_test)[:, 1]
    pred_test  = model.predict(X_test)

    row = {
        "model"      : name,
        "acc_test"   : round(accuracy_score(y_test, pred_test),  4),
        "auc_test"   : round(roc_auc_score(y_test, prob_test),   4),
        "brier_test" : round(brier_score_loss(y_test, prob_test), 4),
        "logloss_test": round(log_loss(y_test, prob_test),        4),
    }

    # 5-fold CV AUC on the full dataset as a stability check
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    X_all = np.vstack([X_train, X_test])
    y_all = np.concatenate([y_train, y_test])
    cv_aucs = cross_val_score(model, X_all, y_all, cv=cv,
                               scoring="roc_auc", n_jobs=-1)
    row["auc_cv_mean"] = round(cv_aucs.mean(), 4)
    row["auc_cv_std"]  = round(cv_aucs.std(),  4)
    return row


def main():
    print("=" * 60)
    print("Task 3.1 — Model Suite Training")
    print("=" * 60)

    # ── 1. Load data ─────────────────────────────────────────────
    df = pd.read_csv(DATA_FILE)
    feature_cols = [c for c in df.columns if c != "class"]
    X = df[feature_cols].values
    y = df["class"].values
    print(f"\n[1] Data loaded: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"    Class balance: CKD={y.sum()} ({y.mean()*100:.1f}%)  "
          f"notCKD={len(y)-y.sum()}")

    # ── 2. Train / test split (stratified, 80/20) ────────────────
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, np.arange(len(y)),
        test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE,
    )
    print(f"\n[2] Split: train={len(y_train)}, test={len(y_test)}")

    joblib.dump({"train": idx_train, "test": idx_test,
                 "feature_cols": feature_cols},
                MODELS_DIR / "split_indices.pkl")
    print(f"    Saved split indices -> models/split_indices.pkl")

    # ── 3. Train, evaluate, save ──────────────────────────────────
    print(f"\n[3] Training {len(MODELS)} classifiers ...\n")
    rows = []
    for name, model in MODELS.items():
        print(f"  {name} ...", end=" ", flush=True)
        row = evaluate(name, model, X_train, X_test, y_train, y_test)
        rows.append(row)
        joblib.dump(model, MODELS_DIR / f"{name}.pkl")
        print(f"AUC={row['auc_test']:.4f}  Brier={row['brier_test']:.4f}  "
              f"CV-AUC={row['auc_cv_mean']:.4f}±{row['auc_cv_std']:.4f}")

    # ── 4. Summary table ──────────────────────────────────────────
    summary = pd.DataFrame(rows)
    out_path = TABLE_DIR / "t_model_suite.csv"
    summary.to_csv(out_path, index=False)
    print(f"\n[4] Saved summary -> tables/t_model_suite.csv")

    # ── 5. Print table ────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(summary.to_string(index=False))
    print("=" * 60)
    print("\nDONE — all models saved to models/")


if __name__ == "__main__":
    main()
