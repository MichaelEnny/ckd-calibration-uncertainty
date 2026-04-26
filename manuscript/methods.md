## 2. Methods

### 2.1 Datasets

Two datasets were used. The UCI CKD dataset served as the primary training and internal validation source [15]. It contains 400 patient records collected from a hospital in Vellore, India, each described by 24 clinical and laboratory features alongside a binary CKD label. Of the 400 patients, 250 (62.5%) carry a positive CKD diagnosis. The mean patient age was 51.6 years (SD 17.0). Features span continuous measurements including serum creatinine, blood urea, hemoglobin, sodium, potassium, and packed cell volume, alongside categorical variables for comorbidities (hypertension, diabetes, coronary artery disease) and urinary findings (red blood cell morphology, pus cells, bacteria).

The MIMIC-IV Clinical Database (version 2.2) provided the external validation cohort [16]. MIMIC-IV is a freely accessible, de-identified electronic health record dataset from the Beth Israel Deaconess Medical Center in Boston, Massachusetts. The study used the 100-patient public demonstration subset. From this cohort, patients were included if serum creatinine was available on their first hospital admission, yielding 97 patients. A binary CKD label was derived using the CKD-EPI 2021 race-free equation: eGFR below 60 mL/min/1.73m2 classified a patient as CKD-positive, giving 23 CKD cases (23.7%) and 74 controls. Mean age in the MIMIC cohort was 61.7 years (SD 16.3).

MIMIC-IV data were accessed under a PhysioNet credentialed license. The dataset is de-identified and its use for research requires completion of CITI human subjects training, which was completed prior to data access. No new patient contact occurred and no institutional review was required.

### 2.2 Preprocessing and Feature Harmonization

UCI preprocessing followed a standard pipeline. String values in all categorical columns were stripped of whitespace before encoding. Categorical features (red blood cell morphology, pus cell appearance, pus cell clumps, bacteria, hypertension, diabetes mellitus, coronary artery disease, appetite, pedal edema, anemia) were mapped to binary 0/1 values. The target label was encoded as CKD=1, notCKD=0. Missing values in continuous features were filled with the column median; missing values in categorical features were filled with the column mode. After imputation, zero missing values remained across all 400 records and 25 columns (24 features plus label).

MIMIC harmonization used imputation statistics derived exclusively from the UCI training fold to prevent information leakage. Seven features present in the UCI dataset are not routinely recorded in MIMIC: urine-specific gravity, urine sugar, pus cells (categorical), pus cell clumps, bacteria, appetite, and pedal edema. These columns were imputed using the UCI training-set median or mode as appropriate. Blood pressure was extracted from ICU chartevents (MIMIC item IDs 220179 and 220050, systolic range 60-250 mmHg) and, where that was unavailable, from the MIMIC outpatient medical record table. This two-source approach resolved blood pressure for 94 of 97 patients. Serum creatinine, blood urea nitrogen, hemoglobin, albumin, potassium, sodium, glucose, hematocrit, WBC count, and RBC count were extracted from the MIMIC laboratory events table using established item IDs, averaged across each patient's first admission. Comorbidity flags for hypertension, diabetes, and coronary artery disease were derived from ICD-10 diagnosis codes (I10, E11.x, I25.x respectively). Anemia was defined as hemoglobin below 12 g/dL for female patients and below 13.5 g/dL for male patients.

After harmonization, the MIMIC dataset was aligned to the identical 25-column schema as the processed UCI dataset. No test-set information was used at any stage of imputation.

### 2.3 Model Suite and Training

The UCI dataset was split into training (70%, n=279), validation (15%, n=60), and test (15%, n=61) subsets using stratified random sampling to preserve the CKD prevalence in each fold (random_state=42). The MIMIC cohort was reserved entirely as an external test set. No MIMIC records appeared in any training or validation fold.

Five classifier families were selected to represent the range of calibration behaviors reported in the clinical ML literature. Logistic regression with L2 regularization serves as a well-calibrated linear baseline. Random forest is an ensemble learner known to produce overconfident probabilities. XGBoost is a gradient-boosted tree model that achieves strong discrimination but is typically miscalibrated. The support vector machine was fitted with probability=True, which applies internal Platt scaling during training. Gaussian naive Bayes produces class-conditional probability estimates and is often considered naturally calibrated for binary problems.

Hyperparameter tuning used five-fold stratified cross-validation on the training fold, optimizing AUROC. Logistic regression C was tuned by grid search over {0.001, 0.01, 0.1, 1, 10, 100}. Random forest, XGBoost, and SVM used randomized search with a maximum of 30 iterations over defined parameter grids. All fitted models were saved using joblib for use in subsequent calibration and uncertainty pipelines. All random seeds were set to 42 throughout.

Software: Python 3.13, scikit-learn, XGBoost, MAPIE 1.3, netcal, pandas, numpy, matplotlib, seaborn, joblib. Full version specifications are listed in requirements.txt in the project repository.

### 2.4 Calibration Evaluation

Pre-calibration assessment was performed on the UCI validation set. For each model, predicted probabilities were obtained and four metrics computed: Expected Calibration Error (ECE) using 10 equal-width bins, Maximum Calibration Error (MCE) using the same binning, Brier Score, and Brier Skill Score relative to a naive climatology baseline equal to the validation-set prevalence. Reliability diagrams were generated using CalibrationDisplay from scikit-learn. ECE and MCE were computed using the netcal library.

Post-hoc recalibration was applied through two methods fitted exclusively on the validation set. Platt scaling fits a logistic regression layer on the base model's raw scores, implemented via CalibratedClassifierCV with method='sigmoid' and cv='prefit'. Isotonic regression fits a piecewise-constant monotone function on the raw scores, implemented via CalibratedClassifierCV with method='isotonic' and cv='prefit'. In both cases, FrozenEstimator from scikit-learn was used to prevent refitting of the base model. The test set was never used during calibration fitting.

Post-calibration metrics were computed on the UCI test set for the base, Platt-scaled, and isotonic-scaled variants of each model. For external validation, the best-calibrated variant per model (selected by lowest ECE on the UCI test set) was applied to the MIMIC cohort, and ECE, MCE, Brier Score, and AUROC were computed. Calibration drift was defined as MIMIC ECE minus UCI ECE for the selected variant.

### 2.5 Uncertainty Quantification

Predictive uncertainty was quantified through split conformal prediction using the MAPIE library (SplitConformalClassifier, version 1.3). Split conformal prediction is a distribution-free method that provides a finite-sample marginal coverage guarantee: with probability at least 1-alpha over the calibration set, the true label appears in the predicted set for at least 1-alpha fraction of test cases [17].

For each of the five base models, a conformal predictor was fitted using the UCI validation set as the conformalization set (n=60). The conformity score was the least ambiguous class (LAC) score, defined as one minus the predicted probability of the most likely class. The target confidence level was 0.90 (alpha=0.10), meaning the prediction set for each patient should contain the true label at least 90% of the time.

Three metrics were computed on both the UCI test set and the MIMIC cohort: empirical coverage rate (proportion of test cases where the true label falls in the prediction set), average prediction set size (0=empty, 1=definitive, 2=ambiguous), and singleton rate (proportion of cases with exactly one class in the set). Coverage drift was defined as UCI coverage minus MIMIC coverage.

### 2.6 Deployment Readiness Framework

Eight criteria were defined a priori. Each criterion was scored as PASS (value meets threshold), MARGINAL (value within 20% of threshold), or FAIL.

Criterion 1: Discrimination adequacy. AUROC at or above 0.85 on the external cohort.
Criterion 2: Calibration adequacy. ECE at or below 0.10 on the external cohort.
Criterion 3: Calibration stability. Absolute calibration drift (MIMIC ECE minus UCI ECE) at or below 0.05.
Criterion 4: Uncertainty coverage. Conformal coverage at or above 0.90 on the external cohort.
Criterion 5: Coverage stability. Absolute coverage drift at or below 0.05.
Criterion 6: Prediction interpretability. Singleton rate at or above 0.70 on the external cohort.
Criterion 7: Subgroup calibration equity. Maximum ECE gap across age and comorbidity subgroups at or below 0.05.
Criterion 8: Transparency and reproducibility. Full code and data pipeline publicly available.

Subgroup analysis stratified the MIMIC cohort by age (below 65 vs. 65 and above), diabetes status, and hypertension status. Subgroups with fewer than 10 patients were excluded from ECE computation due to bin instability. Total deployment readiness scores ranged from 0 to 16.

### 2.7 Statistical Analysis

All metrics are reported as point estimates on the held-out test sets. Bootstrap confidence intervals (95%, 1000 resamples with replacement, random_state=42) were computed for AUROC and ECE on both the UCI test set and the MIMIC cohort using a dedicated bootstrap script. Confidence intervals are reported in Table 2. No hypothesis testing was performed; this study is descriptive and evaluative in design.
