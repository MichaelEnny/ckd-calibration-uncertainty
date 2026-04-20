# Paper 1 — Task Document
## Calibration, Uncertainty Communication, and Deployment Readiness in CKD Risk Prediction: A Framework Evaluation Study

**Target Venue:** JAMIA Open (primary) | Journal of Biomedical Informatics (backup)  
**Paper Type:** Calibration + uncertainty quantification evaluation  
**Created:** 2026-04-18  

---

## Overview

This document is the authoritative step-by-step task guide for completing Paper 1 from data acquisition through final submission. Tasks are grouped into seven phases. Each task includes what to do, what artifact to produce, and what "done" looks like.

---

## Phase 1 — Environment & Repository Setup

### Task 1.1 — Create project directory structure
- Create the following folders inside `first_paper/`:
  ```
  first_paper/
  ├── code/
  │   ├── 01_data_prep/
  │   ├── 02_modeling/
  │   ├── 03_calibration/
  │   ├── 04_uncertainty/
  │   ├── 05_deployment_checklist/
  │   └── utils/
  ├── data/
  │   ├── raw/
  │   ├── processed/
  │   └── external/
  ├── figures/
  ├── tables/
  ├── manuscript/
  └── supplementary/
  ```
- **Done when:** All directories exist and a `README.md` is present at the root of `first_paper/`.

### Task 1.2 — Set up Python environment
- Create a `requirements.txt` (or `environment.yml` for Conda) pinning all library versions.
- Required libraries: `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, `scipy`, `xgboost`, `lightgbm`, `imbalanced-learn`, `mapie` (for conformal prediction), `netcal` (calibration metrics), `shap`, `jupyter`, `pyarrow`.
- **Done when:** `pip install -r requirements.txt` completes without errors in a clean environment and `python -c "import mapie, netcal, shap"` succeeds.

### Task 1.3 — Version control
- Ensure the `first_paper/` folder is tracked by the existing git repo.
- Add a `.gitignore` that excludes `data/raw/`, `data/external/`, and any MIMIC credential files.
- **Done when:** `git status` shows only tracked files; no PHI-adjacent files are staged.

---

## Phase 2 — Data Acquisition & Preprocessing

### Task 2.1 — Acquire UCI CKD Dataset
- Source: UCI Machine Learning Repository — "Chronic_Kidney_Disease" dataset (400 instances, 24 features + 1 binary label).
- Download `chronic_kidney_disease.arff` (or `.csv` equivalent).
- Place raw file in `data/raw/uci_ckd.csv`.
- **Done when:** File is present, row count matches 400, column count matches 25.

### Task 2.2 — Acquire MIMIC-IV subset for external validation
- Access MIMIC-IV via PhysioNet (requires CITI training + credentialed account).
- Extract patients with ICD-10 codes N18.x (CKD stages) and relevant labs: serum creatinine, BUN, eGFR, hemoglobin, albumin, potassium, sodium, blood pressure, diabetes flag, hypertension flag, age, sex.
- Target a cohort of ≥500 patients with binary CKD label (eGFR < 60 mL/min/1.73m² = CKD positive).
- Save as `data/external/mimic_ckd_cohort.csv` with same column schema as UCI dataset after harmonization.
- **Done when:** File exists, missingness report generated, cohort size documented in a `data/external/README.md`.

### Task 2.3 — UCI data cleaning (script: `01_data_prep/clean_uci.py`)
- Handle missing values: use median imputation for continuous variables; mode imputation for categorical.
- Encode categorical variables (e.g., `rbc`, `pc`, `pcc`, `ba`, `htn`, `dm`, `cad`, `appet`, `pe`, `ane`) as binary 0/1.
- Map `ckd`/`notckd` label to 1/0.
- Save cleaned file as `data/processed/uci_ckd_clean.csv`.
- Output a missingness table before and after imputation.
- **Done when:** Zero missing values in processed file; missingness table saved to `tables/t_uci_missingness.csv`.

### Task 2.4 — MIMIC data harmonization (script: `01_data_prep/harmonize_mimic.py`)
- Align MIMIC feature names and encoding to match UCI processed schema exactly.
- Document any features missing in MIMIC vs. UCI and handle via mean imputation flagged with an indicator column.
- Save as `data/processed/mimic_ckd_clean.csv`.
- **Done when:** Both processed files have identical column names; a `data/processed/schema_comparison.csv` is produced showing feature alignment.

### Task 2.5 — Exploratory Data Analysis (script: `01_data_prep/eda.ipynb`)
- Produce: class distribution bar charts for both datasets, feature correlation heatmap, box plots of top 10 features by importance (use preliminary RF importance), demographic summary table.
- **Done when:** Notebook runs end-to-end without errors; all EDA figures saved to `figures/eda_*.png`.

---

## Phase 3 — Model Training & Selection

### Task 3.1 — Define model suite
Train the following five classifiers on UCI CKD data (these represent the breadth needed for calibration comparison):
1. Logistic Regression (LR) — well-calibrated baseline
2. Random Forest (RF) — ensemble, typically overconfident
3. Gradient Boosting (XGBoost) — high performance, typically miscalibrated
4. Support Vector Machine with probability=True (SVM-Platt) — Platt scaling built in
5. Naive Bayes (NB) — often well-calibrated for binary tasks

### Task 3.2 — Train/validation/test split
- UCI: 70% train, 15% validation (calibration tuning), 15% test. Use stratified split.
- MIMIC: used entirely as external test set — no training.
- Set `random_state=42` throughout for reproducibility.
- Save split indices as `data/processed/uci_splits.json`.
- **Done when:** Split sizes documented; no data leakage verified by checking index disjointness.

### Task 3.3 — Hyperparameter tuning (script: `02_modeling/train_models.py`)
- Use 5-fold stratified cross-validation on the training fold.
- Tune via `GridSearchCV` or `RandomizedSearchCV`; optimize for AUROC.
- Save best hyperparameters for each model to `tables/t_hyperparams.csv`.
- Save fitted model objects to `code/02_modeling/saved_models/` as `.pkl` files.
- **Done when:** All 5 models trained, best params logged, `saved_models/` contains 5 `.pkl` files.

### Task 3.4 — Baseline discrimination metrics (script: `02_modeling/evaluate_baseline.py`)
- On UCI test set: compute AUROC, AUPRC, F1, Accuracy, Sensitivity, Specificity for each model.
- Save to `tables/t_baseline_discrimination.csv`.
- **Done when:** Table exists with 5 rows (one per model) and 6 metric columns; values look reasonable (AUROC > 0.85 for top models given UCI's well-structured data).

---

## Phase 4 — Calibration Analysis (Core Contribution)

### Task 4.1 — Pre-calibration assessment (script: `03_calibration/calibration_prepost.py`)
- For each of the 5 models, on the UCI validation set:
  - Plot reliability diagrams (10 bins) using `sklearn.calibration.CalibrationDisplay`.
  - Compute Expected Calibration Error (ECE) using `netcal` library.
  - Compute Maximum Calibration Error (MCE).
  - Compute Brier Score using `sklearn.metrics.brier_score_loss`.
  - Compute Brier Skill Score (BSS) relative to a naive climatology baseline.
- Save all metrics to `tables/t_calibration_precal.csv`.
- Save all reliability diagram figures to `figures/reliability_pre_*.png`.
- **Done when:** All metrics present for all 5 models; reliability diagrams visually reviewed.

### Task 4.2 — Apply post-hoc calibration methods
Apply two calibration methods to all 5 models using the validation set:

**Method A — Platt Scaling** (Logistic Regression on raw scores):
- Fit `CalibratedClassifierCV(method='sigmoid', cv='prefit')` on validation set.
- Save recalibrated models to `saved_models/platt_*.pkl`.

**Method B — Isotonic Regression**:
- Fit `CalibratedClassifierCV(method='isotonic', cv='prefit')` on validation set.
- Save recalibrated models to `saved_models/isotonic_*.pkl`.

- **Done when:** 10 additional `.pkl` files saved (5 models × 2 methods); no data from test set used in fitting.

### Task 4.3 — Post-calibration metrics
- Re-run Task 4.1 metrics for Platt-scaled and Isotonic-scaled versions on UCI test set.
- Save to `tables/t_calibration_postcal_platt.csv` and `tables/t_calibration_postcal_isotonic.csv`.
- Produce side-by-side reliability diagrams (pre vs. post) for each model.
- Save figures to `figures/reliability_compare_*.png`.
- **Done when:** All metrics tables complete; ECE reduction quantified in a summary column.

### Task 4.4 — External calibration validation (MIMIC-IV)
- Apply the best-calibrated version of each model (per ECE on UCI test) to MIMIC cohort.
- Compute ECE, MCE, Brier Score, AUROC on MIMIC.
- Produce reliability diagrams for MIMIC.
- Save to `tables/t_calibration_mimic.csv` and `figures/reliability_mimic_*.png`.
- **Done when:** MIMIC calibration results documented; calibration drift (ΔECE = MIMIC ECE − UCI ECE) computed per model.

### Task 4.5 — Calibration summary table (manuscript-ready)
- Combine UCI and MIMIC calibration results into one master table: `tables/T2_calibration_summary.csv`.
- Columns: Model | Calibration Method | UCI ECE | UCI Brier | MIMIC ECE | MIMIC Brier | Calibration Drift.
- **Done when:** Table is clean, formatted, and reviewed for accuracy.

---

## Phase 5 — Uncertainty Quantification via Conformal Prediction

### Task 5.1 — Background and method selection
- Use **Split Conformal Prediction** (inductive conformal prediction) via the `MAPIE` library.
- Use the UCI validation set as the calibration set for conformal scores.
- Target coverage level: α = 0.10 (90% prediction sets).

### Task 5.2 — Fit conformal predictors (script: `04_uncertainty/conformal_prediction.py`)
- For each of the 5 base models, fit `MapieClassifier` with `method='score'` using the validation set.
- Predict on UCI test set: produce prediction sets (each instance gets a set of classes with coverage guarantee).
- Compute: empirical coverage rate, average prediction set size, singleton rate (unambiguous predictions).
- Save results to `tables/t_conformal_uci.csv`.
- **Done when:** Coverage ≥ 0.90 on UCI test set for all models; table complete.

### Task 5.3 — Apply conformal predictors to MIMIC (external)
- Apply conformal predictors trained on UCI validation to MIMIC cohort.
- Compute coverage rate, average set size, singleton rate on MIMIC.
- Document coverage degradation (ΔCoverage = UCI − MIMIC) per model.
- Save to `tables/t_conformal_mimic.csv`.
- **Done when:** Results show whether conformal coverage transfers across datasets.

### Task 5.4 — Uncertainty visualization
- Plot prediction set size distribution (histogram) for UCI and MIMIC for the best model.
- Plot a sample of 50 test cases showing predicted probability + prediction set label (CKD / Not-CKD / Ambiguous) as a horizontal bar chart.
- Save to `figures/conformal_setsize_*.png` and `figures/conformal_sample_*.png`.
- **Done when:** Figures are legible, clinically interpretable, and saved.

### Task 5.5 — Uncertainty summary table
- Compile `tables/T3_uncertainty_summary.csv`: Model | UCI Coverage | UCI Avg Set Size | UCI Singleton Rate | MIMIC Coverage | MIMIC Avg Set Size | Coverage Drift.
- **Done when:** Table complete and consistent with raw results.

---

## Phase 6 — Deployment Readiness Framework

### Task 6.1 — Define deployment readiness criteria
Develop a checklist of deployment readiness dimensions. Use these 8 criteria (justify each in the paper):

| # | Criterion | Measurement |
|---|-----------|-------------|
| 1 | Discrimination adequacy | AUROC ≥ 0.85 on external set |
| 2 | Calibration adequacy | ECE ≤ 0.10 on external set |
| 3 | Calibration stability | ΔECE (internal→external) ≤ 0.05 |
| 4 | Uncertainty coverage | Conformal coverage ≥ 0.90 on external set |
| 5 | Coverage stability | ΔCoverage ≤ 0.05 across datasets |
| 6 | Prediction set interpretability | Singleton rate ≥ 0.70 |
| 7 | Subgroup calibration equity | ECE difference across age/sex subgroups ≤ 0.05 |
| 8 | Transparency & reproducibility | Full code + data pipeline publicly reproducible |

### Task 6.2 — Subgroup calibration analysis (script: `05_deployment_checklist/subgroup_calibration.py`)
- On MIMIC cohort, stratify by: Age (< 65 vs. ≥ 65), Sex (M vs. F), Diabetes status (yes/no), Hypertension status (yes/no).
- Compute ECE per subgroup per model.
- Save to `tables/t_subgroup_calibration.csv`.
- **Done when:** All subgroup ECEs computed; maximum subgroup ECE gap identified per model.

### Task 6.3 — Score each model against deployment checklist (script: `05_deployment_checklist/score_checklist.py`)
- For each model and its best calibration variant:
  - Score each of the 8 criteria as PASS / MARGINAL / FAIL based on defined thresholds.
  - Compute total readiness score (out of 8).
- Save to `tables/T4_deployment_checklist.csv`.
- **Done when:** All 5 models scored; at least one passes and at least one fails (validates discriminative power of checklist).

### Task 6.4 — Deployment readiness figure
- Produce a heatmap of deployment readiness scores: rows = models, columns = criteria, cells = PASS (green) / MARGINAL (yellow) / FAIL (red).
- Save to `figures/F4_deployment_heatmap.png`.
- **Done when:** Figure is publication-quality (300 DPI, readable labels, legend included).

---

## Phase 7 — Manuscript Writing

### Task 7.1 — Write Abstract (≤ 250 words)
Structure: Background (2 sentences on the gap) | Objective | Methods (dataset, models, metrics) | Results (key numbers) | Conclusion (deployment readiness implication).
- File: `manuscript/abstract.md`
- **Done when:** Word count ≤ 250; all key metrics cited with exact numbers.

### Task 7.2 — Write Introduction (target: 600–800 words)
Sections:
1. Clinical burden of CKD (2–3 sentences, cite CDC stats).
2. Role of ML in CKD risk prediction (existing models).
3. The calibration gap — cite the systematic review finding ("less commonly assessed").
4. The uncertainty communication gap — cite the < 4% statistic.
5. The CDC recommendation for better calibration before guideline integration.
6. Statement of the gap: no single study has jointly evaluated calibration + uncertainty + deployment readiness for CKD.
7. Objectives of this study (numbered list).
- File: `manuscript/introduction.md`
- **Done when:** All 5 cited papers included in reference list draft; word count 600–800.

### Task 7.3 — Write Methods (target: 1,000–1,200 words)
Sub-sections:
- 2.1 Datasets (UCI CKD + MIMIC-IV; ethical statement for MIMIC).
- 2.2 Preprocessing and feature harmonization.
- 2.3 Model suite and training procedure.
- 2.4 Calibration evaluation (ECE, Brier, reliability diagrams; post-hoc recalibration).
- 2.5 Uncertainty quantification (split conformal prediction; coverage guarantee derivation).
- 2.6 Deployment readiness framework (define each criterion with threshold).
- 2.7 Statistical analysis (bootstrap 95% CIs for ECE and AUROC using 1,000 resamples).
- File: `manuscript/methods.md`
- **Done when:** Methods are fully reproducible from text alone; all hyperparameters, random seeds, and software versions stated.

### Task 7.4 — Compute bootstrap confidence intervals (script: `03_calibration/bootstrap_ci.py`)
- For each model: compute 95% bootstrap CIs (1,000 resamples) for AUROC and ECE on UCI test and MIMIC.
- Add CI columns to `tables/T2_calibration_summary.csv`.
- **Done when:** All CIs present; none cross zero for AUROC; some ECE CIs overlap (expected).

### Task 7.5 — Write Results (target: 800–1,000 words)
Structure:
- 3.1 Cohort characteristics (reference demographic table).
- 3.2 Baseline discrimination (reference T1).
- 3.3 Calibration results pre- and post-recalibration (reference T2, reliability diagram figures).
- 3.4 External calibration on MIMIC (reference MIMIC reliability diagrams).
- 3.5 Conformal prediction coverage and set sizes (reference T3).
- 3.6 Deployment readiness scoring (reference T4, heatmap figure).
- File: `manuscript/results.md`
- **Done when:** Every table and figure cited in text; no interpretation (saved for Discussion).

### Task 7.6 — Write Discussion (target: 800–1,000 words)
Structure:
- 4.1 Key finding 1: which models are deployment-ready and why.
- 4.2 Key finding 2: calibration degrades on external data — implications for clinical use.
- 4.3 Key finding 3: conformal prediction as a practical tool for uncertainty communication.
- 4.4 Comparison to prior work (how your ECE/Brier results compare to the 8 externally-validated CKD models).
- 4.5 Limitations (UCI dataset size, MIMIC cohort selection, single external validation site).
- 4.6 Future directions (prospective validation, patient-facing uncertainty display, federated calibration).
- File: `manuscript/discussion.md`
- **Done when:** Each point references specific result numbers; limitations are honest.

### Task 7.7 — Write Conclusion (≤ 150 words)
- One paragraph stating the main contribution, the deployment readiness takeaway, and the call to action for the field.
- File: `manuscript/conclusion.md`

### Task 7.8 — Compile reference list
- Minimum required citations:
  1. Systematic review finding calibration "less commonly assessed" in CKD models.
  2. ScienceDirect 2025 vision paper on < 4% uncertainty reporting in clinical AI.
  3. 2023 CDC systematic review of CKD risk prediction models.
  4. Original MAPIE / conformal prediction paper.
  5. ECE/reliability diagram methodology paper (Guo et al., 2017 or Niculescu-Mizil & Caruana, 2005).
  6. UCI CKD dataset paper.
  7. MIMIC-IV dataset paper (Johnson et al.).
  8. Platt scaling paper.
  9. Isotonic regression calibration paper.
  10. At least 3 primary CKD ML model papers (e.g., Tangri et al., Kanda et al.).
- Use JAMIA Open citation style (Vancouver/numbered).
- File: `manuscript/references.bib`
- **Done when:** All 10+ references located, DOIs verified, and BibTeX entries complete.

### Task 7.9 — Assemble Tables 1–4 in manuscript format
| Table | Content | Source file |
|-------|---------|-------------|
| T1 | Cohort demographics (UCI vs. MIMIC) | `tables/T1_demographics.csv` |
| T2 | Calibration summary (pre/post + MIMIC) | `tables/T2_calibration_summary.csv` |
| T3 | Uncertainty quantification summary | `tables/T3_uncertainty_summary.csv` |
| T4 | Deployment readiness checklist scores | `tables/T4_deployment_checklist.csv` |

- Format each as a clean `.docx` or `.tex` table suitable for submission.
- **Done when:** All 4 tables formatted, reviewed, and consistent with text.

### Task 7.10 — Assemble Figures 1–4 in manuscript format
| Figure | Content | Source file |
|--------|---------|-------------|
| F1 | Reliability diagrams — pre vs. post calibration (3×2 panel) | `figures/reliability_compare_*.png` |
| F2 | Reliability diagrams — MIMIC external validation | `figures/reliability_mimic_*.png` |
| F3 | Conformal prediction set size distributions + sample case display | `figures/conformal_*.png` |
| F4 | Deployment readiness heatmap | `figures/F4_deployment_heatmap.png` |

- All figures: 300 DPI, max 3.5 inches wide (single column) or 7 inches (double column), sans-serif font.
- **Done when:** All 4 figures exported at publication quality; captions written in `manuscript/figure_captions.md`.

### Task 7.11 — Full manuscript assembly
- Compile all sections into `manuscript/manuscript_v1.docx` (or `.tex`).
- Order: Title page | Abstract | Keywords | Introduction | Methods | Results | Discussion | Conclusion | References | Tables | Figures.
- Target word count: 3,500–4,500 words (body only, excluding abstract, references, tables, figures).
- **Done when:** Word count verified; all sections present; one full read-through completed for internal consistency.

---

## Phase 8 — Pre-Submission Checks

### Task 8.1 — Reproducibility audit
- Delete all processed data files and re-run the full pipeline from raw data.
- Confirm all tables and figures regenerate identically (within floating-point tolerance).
- **Done when:** End-to-end re-run completes without errors; key metrics match to 3 decimal places.

### Task 8.2 — JAMIA Open author guidelines compliance check
- Verify: word limits, structured abstract format, reference style, figure formats, data availability statement, ethical statement for MIMIC, author contribution statement (CRediT taxonomy).
- Prepare a cover letter (`manuscript/cover_letter.md`) stating why this paper fits JAMIA Open's scope.
- **Done when:** Checklist against JAMIA Open submission guidelines complete with all items marked.

### Task 8.3 — Supplementary materials
- Supplement S1: Full hyperparameter grids tested.
- Supplement S2: All reliability diagrams (not just selected ones in main text).
- Supplement S3: Subgroup calibration tables (full detail).
- Supplement S4: Reproducibility instructions and software environment.
- File: `supplementary/supplementary_v1.docx`
- **Done when:** All 4 supplements complete and cross-referenced from main text.

### Task 8.4 — Code and data release
- Upload code to GitHub (public repo or Zenodo DOI for reproducibility).
- Add a `code/README.md` with: installation instructions, step-by-step run order, expected outputs.
- Note: MIMIC data cannot be redistributed — provide extraction SQL query instead.
- **Done when:** Repo is public (or Zenodo DOI obtained); data availability statement in manuscript points to it.

---

## Milestone Checklist

| Milestone | Phase | Target |
|-----------|-------|--------|
| Environment ready | 1 | Day 1–2 |
| UCI data cleaned | 2 | Day 3–4 |
| MIMIC cohort extracted | 2 | Day 5–10 |
| All 5 models trained | 3 | Day 11–12 |
| Pre-calibration analysis complete | 4 | Day 13–14 |
| Post-calibration analysis complete | 4 | Day 15–16 |
| MIMIC external calibration complete | 4 | Day 17–18 |
| Conformal prediction complete | 5 | Day 19–21 |
| Deployment checklist scored | 6 | Day 22–23 |
| Full manuscript draft | 7 | Day 24–30 |
| Reproducibility audit passed | 8 | Day 31–32 |
| Submission-ready | 8 | Day 33–35 |

---

## Key Design Decisions (Rationale)

| Decision | Rationale |
|----------|-----------|
| UCI as primary, MIMIC as external | UCI is small but clean and well-labeled; MIMIC provides real clinical heterogeneity for transfer testing |
| 5 model types | Covers the overconfident (RF, XGBoost), naturally calibrated (LR, NB), and auto-calibrated (SVM-Platt) spectrum |
| Split conformal prediction via MAPIE | Provides distribution-free coverage guarantee with no parametric assumptions; directly applicable to clinical use |
| 8-criterion deployment checklist | Mirrors emerging regulatory thinking (FDA AI/ML guidance) and TRIPOD+AI reporting guidelines |
| Bootstrap CIs for ECE | ECE has no closed-form CI; bootstrap is the accepted approach |
| JAMIA Open target | Open-access, strong informatics audience, clinical AI focus; backup JBI has similar scope but higher bar |
