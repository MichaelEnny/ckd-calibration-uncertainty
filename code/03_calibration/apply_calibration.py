"""
Task 4.2 — Apply Post-Hoc Calibration Methods
------------------------------------------------
Wraps each of the 5 tuned base models with two post-hoc calibration methods
fitted exclusively on the UCI validation set.  The test set is never touched.

Method A — Platt Scaling  : CalibratedClassifierCV(method='sigmoid',  cv='prefit')
Method B — Isotonic Reg.  : CalibratedClassifierCV(method='isotonic', cv='prefit')

cv='prefit' means the base estimator is already fitted; the wrapper fits only
the calibration layer on the data passed to .fit() — here the val set.

Inputs : data/processed/uci_ckd_clean.csv
         data/processed/uci_splits.json
         code/02_modeling/saved_models/*.pkl   (5 base models)

Outputs: code/02_modeling/saved_models/platt_<model>.pkl    (5 files)
         code/02_modeling/saved_models/isotonic_<model>.pkl (5 files)
"""

import json
import warnings
from pathlib import Path

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parents[2]
DATA_FILE  = ROOT / "data" / "processed" / "uci_ckd_clean.csv"
SPLIT_FILE = ROOT / "data" / "processed" / "uci_splits.json"
MODELS_DIR = ROOT / "code" / "02_modeling" / "saved_models"

MODEL_NAMES = ["LR", "RF", "XGB", "SVM", "NB"]
METHODS     = [("platt", "sigmoid"), ("isotonic", "isotonic")]


def main():
    print("=" * 60)
    print("Task 4.2 — Post-Hoc Calibration (Platt + Isotonic)")
    print("=" * 60)

    # ── 1. Load data and val indices ─────────────────────────────
    df = pd.read_csv(DATA_FILE)
    with open(SPLIT_FILE) as f:
        splits = json.load(f)

    feature_cols = [c for c in df.columns if c != "class"]
    X = df[feature_cols].values
    y = df["class"].values

    idx_val  = splits["val"]
    idx_test = splits["test"]
    X_val, y_val = X[idx_val], y[idx_val]

    # Confirm test indices never touch calibration fitting
    assert not set(idx_val) & set(idx_test), \
        "LEAKAGE: val and test indices overlap"
    print(f"\n[1] Val fold : {len(y_val)} samples  "
          f"(CKD={y_val.sum()}, notCKD={(y_val==0).sum()})")
    print(f"    Test fold: {len(idx_test)} samples — NOT used in this script")

    # ── 2. Fit calibration wrappers ───────────────────────────────
    print(f"\n[2] Fitting calibration wrappers ...\n")
    saved = []
    for method_name, sklearn_method in METHODS:
        print(f"  [{method_name.upper()}]")
        for model_name in MODEL_NAMES:
            base = joblib.load(MODELS_DIR / f"{model_name}.pkl")

            # FrozenEstimator freezes the fitted base so CalibratedClassifierCV
            # uses all of X_val purely for calibration fitting (sklearn >= 1.4).
            cal_model = CalibratedClassifierCV(
                estimator=FrozenEstimator(base),
                method=sklearn_method,
            )
            cal_model.fit(X_val, y_val)

            out_path = MODELS_DIR / f"{method_name}_{model_name}.pkl"
            joblib.dump(cal_model, out_path)
            saved.append(out_path.name)
            print(f"    {model_name} -> saved_models/{out_path.name}")

        print()

    # ── 3. Verify outputs ─────────────────────────────────────────
    print(f"[3] Verifying saved files ...")
    platt_files    = sorted(MODELS_DIR.glob("platt_*.pkl"))
    isotonic_files = sorted(MODELS_DIR.glob("isotonic_*.pkl"))
    total_new      = len(platt_files) + len(isotonic_files)

    assert len(platt_files)    == 5, f"Expected 5 platt files, got {len(platt_files)}"
    assert len(isotonic_files) == 5, f"Expected 5 isotonic files, got {len(isotonic_files)}"
    print(f"    Platt files    : {[p.name for p in platt_files]}")
    print(f"    Isotonic files : {[p.name for p in isotonic_files]}")
    print(f"    [PASS] {total_new} calibrated model files saved")
    print(f"    [PASS] test set not used in any .fit() call")

    print("\nDONE")


if __name__ == "__main__":
    main()
