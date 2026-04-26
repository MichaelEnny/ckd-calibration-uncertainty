# Code — CKD Calibration & Deployment Readiness Study

Reproduces all results in: **"Calibration, Uncertainty Communication, and Deployment Readiness in CKD Risk Prediction: A Framework Evaluation Study"**

---

## Requirements

Python 3.11 or higher. Install all dependencies:

```
pip install -r requirements.txt
```

Key packages: scikit-learn 1.5+, xgboost 2+, netcal 1.3+, mapie 0.8+, pandas 2.2+.

---

## Data setup

### UCI CKD dataset

Download `chronic_kidney_disease_full.arff` from the UCI Machine Learning Repository and place it in `../data/raw/`.

### MIMIC-IV Demo

Download MIMIC-IV Clinical Database Demo v2.2 from PhysioNet (free account, no credentialing). Extract the archive to any local directory. Open `01_data_prep/extract_mimic_local.py` and set the `DEMO_DIR` variable at the top of the file to that directory path.

---

## Run order

Run scripts from the `first_paper/` directory (one level above this `code/` folder). All scripts resolve paths relative to the project root automatically.

### Phase 1 — Data preparation

```
python code/01_data_prep/clean_uci.py
python code/01_data_prep/extract_mimic_local.py
python code/01_data_prep/harmonize_mimic.py
```

Outputs: `data/processed/uci_ckd_clean.csv`, `data/processed/uci_splits.json`, `data/processed/mimic_ckd_cohort.csv`, `data/processed/mimic_ckd_clean.csv`

### Phase 2 — Model training

```
python code/02_modeling/train_models.py
```

Outputs: `code/02_modeling/saved_models/{LR,RF,XGB,SVM,NB}.pkl`, `tables/t_hyperparams.csv`, `tables/t_baseline_discrimination.csv`

### Phase 3 — Calibration

```
python code/03_calibration/calibration_prepost.py
python code/03_calibration/external_calibration.py
python code/03_calibration/bootstrap_ci.py
```

Outputs: calibrated model pkl files, `tables/T2_calibration_summary.csv` (with bootstrap CIs), `tables/t_calibration_mimic.csv`, `figures/reliability_*.png` (18 figures, 300 DPI)

### Phase 4 — Uncertainty quantification

```
python code/04_uncertainty/conformal_prediction.py
python code/04_uncertainty/mimic_conformal.py
```

Outputs: conformal model pkl files, `tables/T3_uncertainty_summary.csv`, `figures/F3_conformal_*.png`

### Phase 5 — Deployment readiness

```
python code/05_deployment_checklist/subgroup_calibration.py
python code/05_deployment_checklist/score_checklist.py
```

Outputs: `tables/t_subgroup_calibration.csv`, `tables/T4_deployment_checklist.csv`, `figures/F4_deployment_heatmap.png`

---

## Directory structure

```
first_paper/
  code/
    01_data_prep/
      clean_uci.py              — cleans UCI ARFF, creates splits
      extract_mimic_local.py    — extracts MIMIC cohort from demo gzipped CSVs
      harmonize_mimic.py        — aligns MIMIC to UCI schema, imputes missing features
    02_modeling/
      train_models.py           — hyperparameter search + saves 5 base classifiers
      saved_models/             — pkl files (base + calibrated variants)
    03_calibration/
      calibration_prepost.py    — internal calibration before/after scaling
      external_calibration.py   — applies best variant to MIMIC, produces T2
      bootstrap_ci.py           — 1000-resample bootstrap CIs for ECE and AUROC
    04_uncertainty/
      conformal_prediction.py   — split conformal on UCI (train + eval)
      mimic_conformal.py        — applies fitted conformal models to MIMIC, T3
    05_deployment_checklist/
      subgroup_calibration.py   — stratified ECE on MIMIC by age/DM/HTN
      score_checklist.py        — 8-criterion scoring + heatmap (T4, F4)
  data/
    raw/                        — original downloads (not tracked in git)
    processed/                  — cleaned CSVs and split indices
  tables/                       — all CSV outputs
  figures/                      — all PNG figures (300 DPI)
  manuscript/                   — section markdown files + BibTeX
  supplementary/                — S1-S4 supplementary documents
```

---

## Reproducibility notes

- All random operations use `random_state=42`.
- Feature imputation statistics (means/modes) are computed from the UCI training fold only and applied to MIMIC — no data leakage across the train/test boundary.
- The pipeline is deterministic: identical outputs are produced on every run given the same input files and package versions.
- Expected MIMIC AUROC range after full pipeline: 0.48-0.58. Expected MIMIC ECE range: 0.68-0.76. These values reflect genuine distributional shift, not errors.

---

## Figures produced

| Figure | File | Script |
|--------|------|--------|
| F1: Pre/post calibration reliability (UCI) | `figures/reliability_*.png` (15 files) | `calibration_prepost.py` |
| F2: Bootstrap CI forest plot | `figures/F2_bootstrap_ci.png` | `bootstrap_ci.py` |
| F3: Conformal prediction set sizes | `figures/F3_conformal_*.png` | `uncertainty_viz.py` |
| F4: Deployment readiness heatmap | `figures/F4_deployment_heatmap.png` | `score_checklist.py` |
| Supplementary: MIMIC reliability diagrams | `figures/reliability_mimic_*.png` | `external_calibration.py` |

---

## License

Code released under MIT License. Data governed by respective source licenses (UCI CC BY 4.0; MIMIC-IV Demo CC BY 4.0).
