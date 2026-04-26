# Supplementary Material S1: Hyperparameter Search Grids

All classifiers were tuned using 5-fold stratified cross-validation on the UCI training fold (n = 280) with AUROC as the scoring metric. GridSearchCV from scikit-learn 1.5.2 was used. Random seed: 42 throughout.

---

## Logistic Regression (LR)

Solver: `lbfgs`; max iterations: 1000; class weight: balanced.

| Hyperparameter | Values searched |
|----------------|-----------------|
| C (inverse regularization strength) | 0.001, 0.01, 0.1, 1, 10, 100 |

**Selected:** C = 0.001  
**CV AUROC (mean):** 1.0000

---

## Random Forest (RF)

| Hyperparameter | Values searched |
|----------------|-----------------|
| n_estimators | 100, 200 |
| max_depth | 5, 10, 20, None |
| min_samples_split | 2, 5, 10 |
| max_features | "sqrt", "log2" |

**Selected:** n_estimators = 100, max_depth = 20, min_samples_split = 10, max_features = "sqrt"  
**CV AUROC (mean):** 0.9997

---

## XGBoost (XGB)

| Hyperparameter | Values searched |
|----------------|-----------------|
| n_estimators | 100, 200 |
| max_depth | 3, 5, 7 |
| learning_rate | 0.05, 0.1, 0.2 |
| subsample | 0.8, 1.0 |
| colsample_bytree | 0.6, 0.8, 1.0 |
| gamma | 0, 0.1, 0.5 |

**Selected:** n_estimators = 100, max_depth = 3, learning_rate = 0.2, subsample = 0.8, colsample_bytree = 0.6, gamma = 0.5  
**CV AUROC (mean):** 0.9992

---

## Support Vector Machine (SVM)

`probability=True` enabled via Platt scaling internally. Class weight: balanced.

| Hyperparameter | Values searched |
|----------------|-----------------|
| C | 0.1, 1, 10, 100 |
| kernel | "rbf", "poly" |
| gamma | "scale", 0.1, 1.0 |

**Selected:** C = 1, kernel = "poly", gamma = 0.1  
**CV AUROC (mean):** 1.0000

---

## Gaussian Naive Bayes (NB)

| Hyperparameter | Values searched |
|----------------|-----------------|
| var_smoothing | 1e-11, 1e-9, 1e-7, 1e-5, 1e-3 |

**Selected:** var_smoothing = 1e-11  
**CV AUROC (mean):** 1.0000

---

## Post-hoc calibration methods

Applied after model selection using `sklearn.calibration.CalibratedClassifierCV` with `FrozenEstimator` to prevent refitting.

| Method | Parameters |
|--------|------------|
| Platt scaling (sigmoid) | `method="sigmoid"`, `cv="prefit"` |
| Isotonic regression | `method="isotonic"`, `cv="prefit"` |

Calibration training used the UCI calibration fold (indices saved in `data/processed/uci_splits.json`). Best variant per model selected by lowest ECE on the UCI test fold.
