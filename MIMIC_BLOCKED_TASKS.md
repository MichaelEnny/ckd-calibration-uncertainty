# MIMIC-Blocked Tasks

Tasks in this list cannot be started until MIMIC-IV data is acquired and
harmonized (Tasks 2.2 and 2.4).  They are separated here to keep the main
task document focused on work that can proceed right now.

**Blocker chain:**
1. Task 2.2 — acquire `data/external/mimic_ckd_cohort.csv` (PhysioNet access required)
2. Task 2.4 — produce `data/processed/mimic_ckd_clean.csv` (harmonize to UCI schema)
3. Everything below unblocks once those two files exist

---

## Phase 2 — Data

### Task 2.2 — Acquire MIMIC-IV subset for external validation
- Access MIMIC-IV via PhysioNet (requires CITI training + credentialed account).
- Extract patients with ICD-10 codes N18.x (CKD stages) and relevant labs:
  serum creatinine, BUN, eGFR, hemoglobin, albumin, potassium, sodium,
  blood pressure, diabetes flag, hypertension flag, age, sex.
- Target cohort: ≥ 500 patients; binary CKD label (eGFR < 60 mL/min/1.73m²).
- Save as `data/external/mimic_ckd_cohort.csv`.
- **Done when:** File exists, missingness report generated, cohort size
  documented in `data/external/README.md`.

### Task 2.4 — MIMIC data harmonization (`01_data_prep/harmonize_mimic.py`)
- Align MIMIC feature names and encoding to match UCI processed schema exactly.
- Handle features missing in MIMIC vs. UCI via mean imputation + indicator column.
- Save as `data/processed/mimic_ckd_clean.csv`.
- **Done when:** Both processed files share identical column names;
  `data/processed/schema_comparison.csv` documents feature alignment.

---

## Phase 4 — Calibration Analysis

### Task 4.4 — External calibration validation (MIMIC-IV)
- Apply the best-calibrated version of each model (per ECE on UCI test) to MIMIC.
- Compute ECE, MCE, Brier Score, AUROC on MIMIC.
- Produce reliability diagrams for MIMIC.
- Save to `tables/t_calibration_mimic.csv` and `figures/reliability_mimic_*.png`.
- **Done when:** Calibration drift (ΔECE = MIMIC ECE − UCI ECE) computed per model.

### Task 4.5 — Calibration summary table (manuscript-ready)
- Combine UCI and MIMIC calibration results into `tables/T2_calibration_summary.csv`.
- Columns: Model | Calibration Method | UCI ECE | UCI Brier | MIMIC ECE |
  MIMIC Brier | Calibration Drift.
- **Done when:** Table clean, formatted, and reviewed for accuracy.

---

## Phase 5 — Uncertainty Quantification

### Task 5.3 — Apply conformal predictors to MIMIC (external)
- Apply conformal predictors trained on UCI validation to MIMIC cohort.
- Compute coverage rate, average set size, singleton rate on MIMIC.
- Document coverage degradation (ΔCoverage = UCI − MIMIC) per model.
- Save to `tables/t_conformal_mimic.csv`.
- **Done when:** Results show whether conformal coverage transfers across datasets.

### Task 5.4 — Uncertainty visualization (MIMIC component)
- Plot prediction set size distribution (histogram) for MIMIC for the best model.
- Save to `figures/conformal_setsize_mimic.png`.
- *Note: the UCI-only part of Task 5.4 can proceed without MIMIC.*

### Task 5.5 — Uncertainty summary table
- Compile `tables/T3_uncertainty_summary.csv`:
  Model | UCI Coverage | UCI Avg Set Size | UCI Singleton Rate |
  MIMIC Coverage | MIMIC Avg Set Size | Coverage Drift.
- **Done when:** Table complete and consistent with Task 5.2 and 5.3 results.

---

## Phase 6 — Deployment Readiness

### Task 6.2 — Subgroup calibration analysis (`05_deployment_checklist/subgroup_calibration.py`)
- On MIMIC cohort, stratify by: Age (< 65 vs. ≥ 65), Sex (M vs. F),
  Diabetes status (yes/no), Hypertension status (yes/no).
- Compute ECE per subgroup per model.
- Save to `tables/t_subgroup_calibration.csv`.
- **Done when:** All subgroup ECEs computed; max ECE gap identified per model.

### Task 6.3 — Score deployment checklist (`05_deployment_checklist/score_checklist.py`)
- Criteria 1–7 all require MIMIC results (external AUROC, MIMIC ECE, coverage
  on MIMIC, subgroup ECE equity).
- Score each model PASS / MARGINAL / FAIL; save `tables/T4_deployment_checklist.csv`.
- **Done when:** All 5 models scored; at least one passes and at least one fails.

### Task 6.4 — Deployment readiness heatmap
- Produce heatmap: rows = models, columns = criteria, cells = PASS/MARGINAL/FAIL.
- Save to `figures/F4_deployment_heatmap.png` (300 DPI, publication quality).
- **Done when:** Figure reviewed and captions written.

---

## Phase 7 — Manuscript (MIMIC-dependent sections)

### Task 7.4 — Bootstrap confidence intervals (`03_calibration/bootstrap_ci.py`)
- Compute 95% bootstrap CIs (1,000 resamples) for AUROC and ECE on both
  UCI test and MIMIC.
- Add CI columns to `tables/T2_calibration_summary.csv`.
- **Done when:** All CIs present; AUROC CIs do not cross zero.

### Task 7.5 — Write Results
- Section 3.4 (external MIMIC calibration) and 3.6 (deployment readiness)
  both require MIMIC results.
- *Sections 3.1–3.3 and 3.5 can be drafted from UCI results alone.*

### Task 7.6 — Write Discussion
- Section 4.2 (calibration degrades on external data) requires MIMIC drift numbers.
- *Sections 4.1, 4.3, 4.4 can be drafted from UCI results.*

### Task 7.9 — Assemble Tables 1–4
- T1 (demographics) and T2 (calibration summary) both include MIMIC columns.

### Task 7.10 — Assemble Figures 1–4
- F2 (MIMIC reliability diagrams) is fully blocked.

---

## What can proceed RIGHT NOW (no MIMIC needed)

| Task | Description |
|------|-------------|
| 5.1 | Conformal prediction background & method selection |
| 5.2 | Fit conformal predictors on UCI; evaluate on UCI test set |
| 5.4 | UCI-only uncertainty visualizations |
| 6.1 | Define deployment readiness criteria (text/design only) |
| 7.1 | Write Abstract (placeholder MIMIC numbers) |
| 7.2 | Write Introduction |
| 7.3 | Write Methods |
| 7.7 | Write Conclusion |
| 7.8 | Compile reference list |
| 8.2 | JAMIA Open compliance checklist |
| 8.3 | Supplement S1, S2, S4 |
