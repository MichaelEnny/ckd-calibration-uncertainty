# Paper 1: Calibration, Uncertainty Communication, and Deployment Readiness in CKD Risk Prediction

**Author:** Michael Eniolade  
**Email:** meniolade20593@ucumberlands.edu  
**Institution:** University of the Cumberlands  
**Target Venue:** JAMIA Open (primary) | Journal of Biomedical Informatics (backup)  
**Created:** 2026-04-18  
**Current manuscript:** v9 — 27 pages, 30 references, 6 figures

---

## Project Structure

```
first_paper/
├── code/
│   ├── 01_data_prep/             # Data cleaning and harmonization scripts
│   ├── 02_modeling/              # Model training, tuning, and baseline evaluation
│   ├── 03_calibration/           # Calibration analysis (ECE, Brier, reliability diagrams)
│   ├── 04_uncertainty/           # Conformal prediction and uncertainty quantification
│   ├── 05_deployment_checklist/  # Deployment readiness scoring and subgroup analysis
│   └── utils/                    # Shared helper functions
├── data/
│   ├── raw/                      # Original unmodified datasets (not committed to git)
│   ├── processed/                # Cleaned and harmonized datasets
│   └── external/                 # MIMIC-IV stress-test cohort (not committed to git)
├── figures/                      # All generated figures (PNG, 300 DPI)
├── tables/                       # All generated tables (CSV)
├── latek/                        # LaTeX source files
│   ├── main.tex                  # Master document
│   ├── refs.bib                  # BibTeX bibliography (30 entries)
│   └── sections/                 # Individual section .tex files
├── manuscript/                   # Compiled manuscript and submission materials
│   ├── cover_letter.md
│   ├── jamia_compliance_checklist.md
│   └── figure_captions.md
├── references/                   # Source PDFs for all 30 cited works (31 files)
├── supplementary/                # Supplementary materials (S1–S4)
└── README.md                     # This file
```

---

## Datasets

| Dataset | Role | Source | Access |
|---------|------|--------|--------|
| UCI CKD (400 instances, 24 features) | Primary training + internal test | UCI ML Repository | Open (CC license) |
| MIMIC-IV Clinical Database Demo v2.2 (97 patients: 23 CKD, 74 not-CKD) | Distributional stress-test cohort | PhysioNet | Open-access, no credentialing required |

The MIMIC-IV Demo cohort is used as a **deliberate distributional stress-test**, not a formal external validation. Key distributional differences from UCI: 23.7% CKD prevalence (vs. 62.5%), 7 of 24 features entirely absent.

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
- **Deployment:** 8-criterion deployment readiness checklist (max score 16; no model exceeded 4)

---

## Figures

Six figures are embedded in the manuscript using forced in-section placement (`[H]`):

| Label | Content |
|-------|---------|
| F1a | UCI reliability diagrams — LR, RF, XGB |
| F1b | UCI reliability diagrams — SVM, NB |
| F2 | MIMIC-IV reliability diagrams — all 5 classifiers |
| F3a | Conformal set-size distribution (UCI) |
| F3b | Conformal coverage by sample size (UCI) |
| F4 | Deployment readiness heatmap |

All figures generated at 300 DPI PNG; colorblind-safe palettes used throughout.

---

## Reproducibility

See `code/README.md` for run instructions.  
All random seeds set to `42`. Python environment pinned in `requirements.txt`.  
Supplementary materials S1–S4 document hyperparameter grids, all reliability diagrams, subgroup calibration tables, and full install/run instructions.

---

## Ethics

Both datasets are fully de-identified and publicly available; no IRB approval is required.

- **UCI CKD dataset:** publicly available from UCI ML Repository under a Creative Commons license.
- **MIMIC-IV Clinical Database Demo v2.2:** de-identified open-access subset of MIMIC-IV released by PhysioNet under CC-BY 4.0. No credentialing or PhysioNet data use agreement is required for the demo release.

No raw data from either dataset is committed to this repository.
