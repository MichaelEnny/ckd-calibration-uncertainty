# Supplementary Material S2: Reliability Diagrams

Reliability diagrams (calibration curves) are provided for all model-dataset combinations. Each diagram plots mean predicted probability (x-axis) against fraction of positive cases per bin (y-axis), with a perfectly calibrated model following the diagonal. Bins: 10 equal-width bins. Figures generated at 300 DPI.

---

## UCI Internal Test Set — Pre-calibration (base models)

Figures located in `figures/`:

| File | Description |
|------|-------------|
| `reliability_base_LR.png` | Logistic Regression, no post-hoc calibration |
| `reliability_base_RF.png` | Random Forest, no post-hoc calibration |
| `reliability_base_XGB.png` | XGBoost, no post-hoc calibration |
| `reliability_base_SVM.png` | SVM (probability=True), no post-hoc calibration |
| `reliability_base_NB.png` | Gaussian Naive Bayes, no post-hoc calibration |

---

## UCI Internal Test Set — After Platt Scaling

| File | Description |
|------|-------------|
| `reliability_platt_LR.png` | Logistic Regression + Platt scaling |
| `reliability_platt_RF.png` | Random Forest + Platt scaling |
| `reliability_platt_XGB.png` | XGBoost + Platt scaling |
| `reliability_platt_SVM.png` | SVM + Platt scaling |
| `reliability_platt_NB.png` | Gaussian Naive Bayes + Platt scaling |

---

## UCI Internal Test Set — After Isotonic Regression

| File | Description |
|------|-------------|
| `reliability_isotonic_LR.png` | Logistic Regression + isotonic regression |
| `reliability_isotonic_RF.png` | Random Forest + isotonic regression |
| `reliability_isotonic_XGB.png` | XGBoost + isotonic regression |
| `reliability_isotonic_SVM.png` | SVM + isotonic regression |
| `reliability_isotonic_NB.png` | Gaussian Naive Bayes + isotonic regression |

---

## MIMIC-IV External Validation — Best Calibrated Variant

Each diagram shows the best-calibrated variant per model (selected by lowest ECE on UCI test set). All four models other than NB use isotonic regression as the best variant; NB uses the base model.

| File | Model | Best variant | MIMIC ECE |
|------|-------|-------------|-----------|
| `reliability_mimic_LR.png` | Logistic Regression | isotonic | 0.7612 |
| `reliability_mimic_RF.png` | Random Forest | isotonic | 0.7526 |
| `reliability_mimic_XGB.png` | XGBoost | isotonic | 0.6801 |
| `reliability_mimic_SVM.png` | SVM | isotonic | 0.7554 |
| `reliability_mimic_NB.png` | Gaussian Naive Bayes | base | 0.7526 |

All MIMIC reliability diagrams show severe deviation from the diagonal, reflecting the calibration collapse documented in Table 2. Points cluster at high predicted probability values despite the MIMIC cohort having only 23.7% CKD prevalence, consistent with models trained on a 62.5% prevalence dataset.

---

## Key metric annotation

Each reliability diagram figure includes an inset text box reporting ECE, MCE, Brier Score, and AUROC for that model-dataset-variant combination.
