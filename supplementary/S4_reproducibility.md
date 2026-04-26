# Supplementary Material S4: Reproducibility Instructions

This document provides full instructions for reproducing all results in the manuscript from raw data. The complete pipeline runs in approximately 5-10 minutes on a standard laptop.

---

## Software environment

| Package | Version |
|---------|---------|
| Python | 3.11+ |
| scikit-learn | 1.5.2 |
| xgboost | 2.1.1 |
| imbalanced-learn | 0.12.4 |
| netcal | 1.3.5 |
| mapie | 0.8.6 |
| pandas | 2.2+ |
| numpy | 1.26+ |
| matplotlib | 3.9+ |
| joblib | 1.4+ |

Install all dependencies:

```
pip install -r requirements.txt
```

---

## Data acquisition

### UCI CKD dataset

Download from the UCI Machine Learning Repository (no account required):

URL: https://archive.ics.uci.edu/dataset/336/chronic+kidney+disease

Place the file `chronic_kidney_disease_full.arff` in:

```
first_paper/data/raw/
```

### MIMIC-IV Clinical Database Demo v2.2

Download from PhysioNet (free account required; no credentialing needed for the demo):

URL: https://physionet.org/content/mimic-iv-demo/2.2/

Download the full archive and extract to any local directory. Set the path in the extraction script (see Step 3 below).

---

## Reproduction steps

Run each script in order from the `first_paper/` directory. All paths are relative to that directory.

### Step 1: Clean UCI data

```
python code/01_data_prep/clean_uci.py
```

Output: `data/processed/uci_ckd_clean.csv`, `data/processed/uci_splits.json`

### Step 2: Extract MIMIC cohort

Edit the `DEMO_DIR` variable at the top of `code/01_data_prep/extract_mimic_local.py` to point to your MIMIC-IV demo directory, then run:

```
python code/01_data_prep/extract_mimic_local.py
```

Output: `data/processed/mimic_ckd_cohort.csv`

### Step 3: Harmonize MIMIC to UCI schema

```
python code/01_data_prep/harmonize_mimic.py
```

Output: `data/processed/mimic_ckd_clean.csv`, `data/processed/schema_comparison.csv`

### Step 4: Train classifiers

```
python code/02_modeling/train_models.py
```

Output: `code/02_modeling/saved_models/LR.pkl`, `RF.pkl`, `XGB.pkl`, `SVM.pkl`, `NB.pkl`; `tables/t_hyperparams.csv`, `tables/t_split_summary.csv`, `tables/t_baseline_discrimination.csv`

### Step 5: Internal calibration analysis

```
python code/03_calibration/calibrate_models.py
```

Output: calibrated model pkl files (platt_*.pkl, isotonic_*.pkl); `tables/t_calibration_pre*.csv`, reliability diagram figures

### Step 6: External calibration (MIMIC)

```
python code/03_calibration/external_calibration.py
```

Output: `tables/T2_calibration_summary.csv`, `tables/t_calibration_mimic.csv`, `figures/reliability_mimic_*.png`

### Step 7: Bootstrap confidence intervals

```
python code/03_calibration/bootstrap_ci.py
```

Output: `tables/t_bootstrap_ci.csv` (CI columns merged into T2_calibration_summary.csv)

### Step 8: Internal conformal prediction

```
python code/04_uncertainty/conformal_uci.py
```

Output: conformal model pkl files; `tables/t_conformal_uci.csv`, `figures/F3_conformal_*.png`

### Step 9: External conformal prediction (MIMIC)

```
python code/04_uncertainty/mimic_conformal.py
```

Output: `tables/t_conformal_mimic.csv`, `tables/T3_uncertainty_summary.csv`

### Step 10: Subgroup calibration

```
python code/05_deployment_checklist/subgroup_calibration.py
```

Output: `tables/t_subgroup_calibration.csv`

### Step 11: Deployment readiness scoring

```
python code/05_deployment_checklist/score_checklist.py
```

Output: `tables/T4_deployment_checklist.csv`, `figures/F4_deployment_heatmap.png`

---

## Expected outputs — key metrics

After running all steps the following values should be present in `tables/T2_calibration_summary.csv`:

| Model | UCI ECE | UCI AUROC | MIMIC ECE | MIMIC AUROC | Drift |
|-------|---------|-----------|-----------|-------------|-------|
| LR | 0.0222 | 1.0 | 0.7612 | 0.4853 | 0.7390 |
| RF | 0.0000 | 1.0 | 0.7526 | 0.5068 | 0.7526 |
| XGB | 0.0070 | 1.0 | 0.6801 | 0.5793 | 0.6731 |
| SVM | 0.0152 | 1.0 | 0.7554 | 0.4830 | 0.7402 |
| NB | 0.0164 | 1.0 | 0.7526 | 0.4774 | 0.7362 |

From `tables/T3_uncertainty_summary.csv`:

| Model | UCI Coverage | MIMIC Coverage |
|-------|-------------|----------------|
| LR | 0.8033 | 0.2371 |
| RF | 0.9672 | 0.2062 |
| XGB | 0.9672 | 0.2268 |
| SVM | 0.9180 | 0.2165 |
| NB | 0.9836 | 0.2474 |

---

## Random seeds

All stochastic operations use `random_state=42`. This includes train/test splitting, cross-validation folds, Random Forest, XGBoost, and bootstrap resampling. Results should be bit-for-bit identical across runs on the same machine and Python/package versions.

---

## File structure after full pipeline run

```
first_paper/
  data/
    raw/            — original downloaded files (not committed to git)
    processed/      — cleaned CSVs and split indices
  code/
    01_data_prep/   — UCI and MIMIC preparation scripts
    02_modeling/    — training, saved_models/
    03_calibration/ — calibration + bootstrap CI scripts
    04_uncertainty/ — conformal prediction scripts
    05_deployment_checklist/ — subgroup + scoring scripts
  tables/           — all CSV outputs (T1-T4 manuscript tables + supplementary)
  figures/          — all PNG figures (300 DPI)
  manuscript/       — section markdown files + references.bib
  supplementary/    — S1-S4 supplementary documents
```
