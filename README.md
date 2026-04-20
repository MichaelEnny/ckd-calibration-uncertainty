# Paper 1: Calibration, Uncertainty Communication, and Deployment Readiness in CKD Risk Prediction

**Author:** Michael Eniolade  
**Institution:** University of the Cumberlands  
**Target Venue:** JAMIA Open (primary) | Journal of Biomedical Informatics (backup)  
**Created:** 2026-04-18  

---

## Project Structure

```
first_paper/
├── code/
│   ├── 01_data_prep/         # Data cleaning and harmonization scripts
│   ├── 02_modeling/          # Model training, tuning, and baseline evaluation
│   ├── 03_calibration/       # Calibration analysis (ECE, Brier, reliability diagrams)
│   ├── 04_uncertainty/       # Conformal prediction and uncertainty quantification
│   ├── 05_deployment_checklist/  # Deployment readiness scoring and subgroup analysis
│   └── utils/                # Shared helper functions
├── data/
│   ├── raw/                  # Original unmodified datasets (not committed to git)
│   ├── processed/            # Cleaned and harmonized datasets
│   └── external/             # MIMIC-IV external validation cohort (not committed to git)
├── figures/                  # All generated figures (PNG, 300 DPI)
├── tables/                   # All generated tables (CSV)
├── manuscript/               # Manuscript sections and final compiled document
├── supplementary/            # Supplementary materials
├── README.md                 # This file
└── TASK_DOCUMENT.md          # Step-by-step task guide for completing the paper
```

---

## Datasets

| Dataset | Role | Source |
|---------|------|--------|
| UCI CKD (400 instances, 24 features) | Primary training + internal test | UCI ML Repository |
| MIMIC-IV (CKD cohort, ≥500 patients) | External validation | PhysioNet (credentialed access) |

---

## Models Evaluated

1. Logistic Regression (LR)
2. Random Forest (RF)
3. XGBoost
4. SVM with Platt scaling
5. Naive Bayes (NB)

---

## Key Metrics

- **Discrimination:** AUROC, AUPRC, F1, Sensitivity, Specificity
- **Calibration:** ECE, MCE, Brier Score, Brier Skill Score, Reliability Diagrams
- **Uncertainty:** Conformal prediction coverage, average set size, singleton rate
- **Deployment:** 8-criterion deployment readiness checklist

---

## Reproducibility

See `TASK_DOCUMENT.md` for full task list and `code/README.md` (created in Task 1.2) for run instructions.  
All random seeds set to `42`. Python environment pinned in `requirements.txt`.

---

## Ethics

MIMIC-IV data used under PhysioNet credentialed access agreement. No raw MIMIC data is committed to this repository. See `data/external/README.md` for cohort extraction details.
