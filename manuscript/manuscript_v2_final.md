# Calibration, Uncertainty, and Deployment Readiness in CKD Risk Prediction: A Multi-Criterion Evaluation of Five Machine Learning Models

**Author:** Michael O. Eniolade
**Affiliation:** University of the Cumberlands
**Corresponding author:** meniolade20593@ucumberlands.edu
**Paper type:** Research Article
**Target venue:** JAMIA Open (primary); Journal of Biomedical Informatics (backup)

**Keywords:** chronic kidney disease, machine learning, probability calibration, conformal prediction, deployment readiness, external validation

---

## Abstract

**Background:** Machine learning models for chronic kidney disease risk prediction regularly achieve strong discrimination on internal test sets. Calibration assessment and uncertainty quantification are far less common, leaving clinicians without reliable information about whether probability outputs are trustworthy. No published study has jointly evaluated all three dimensions on a common model suite with external clinical validation.

**Objective:** To evaluate five classifiers across calibration quality, conformal prediction coverage, and an eight-criterion deployment readiness framework on both internal and external data.

**Methods:** Five classifiers (logistic regression, random forest, XGBoost, support vector machine with Platt scaling, Gaussian naive Bayes) were trained on the UCI CKD dataset (400 patients, 62.5% CKD positive). A distributional stress-test used the open-access MIMIC-IV demo cohort (97 patients, 23.7% CKD) to evaluate model behaviour under prevalence shift and feature missingness. Calibration was assessed before and after Platt scaling and isotonic regression, measured by Expected Calibration Error and Brier Score. Predictive uncertainty was measured through split conformal prediction targeting 90% marginal coverage. An eight-criterion deployment readiness framework evaluated discrimination, calibration stability, coverage transfer, subgroup equity, and reproducibility.

**Results:** All five models achieved AUROC 1.00 on the UCI test set. Post-isotonic ECE fell to 0.000-0.022 internally. On the MIMIC demo cohort, AUROC dropped to 0.48-0.58, ECE rose to 0.68-0.76, and conformal coverage collapsed from 0.80-0.98 on UCI to 0.21-0.25 on MIMIC, well below the 90% target. No model passed the deployment checklist; scores ranged from 2 to 4 out of 16.

**Conclusion:** Near-perfect internal performance did not survive distributional shift. Calibration stability and conformal coverage transfer should be evaluated before any clinical ML model moves toward deployment, even when internal metrics appear strong.

---

## 1. Introduction

Roughly 850 million people worldwide have chronic kidney disease, and global prevalence grew by 33% between 1990 and 2017 [1]. Among people with diabetes, as many as 1 in 3 are affected; among those with hypertension in high-income settings, the proportion reaches approximately 1 in 5 [1]. By 2040, CKD is projected to rank fifth among leading causes of years of life lost globally [1]. These numbers put real pressure on health systems to identify high-risk patients early, before irreversible kidney function loss closes off effective treatment options.

Machine learning has been offered as a practical answer. Models trained on electronic health records, biomarker panels, and demographic variables have reported AUROC values above 0.95 in national cohort studies [2,3,4,5]. Established risk equations like the Kidney Failure Risk Equation have been validated across North America, the United Kingdom, and Latin America, confirming that algorithmic CKD risk prediction is technically achievable [6,7,8]. The field has not struggled to build models. The struggle is with what happens after the model is built.

Discrimination metrics like AUROC measure whether a model ranks patients correctly relative to each other. They say nothing about whether assigned probability scores are trustworthy in absolute terms. A model posting AUROC 0.97 assigns a 65% risk score to patients whose true event rate sits near 20%, and clinicians making treatment decisions from those numbers are working from miscalibrated information. Van Calster and colleagues identified calibration as the Achilles heel of predictive analytics, noting that poor calibration persists regularly even when discrimination appears strong [9]. A systematic review of CKD risk models by Echouffo-Tcheugui and Kengne found calibration is assessed less commonly than discrimination; of all models reviewed, only eight for CKD occurrence and five for CKD progression had been externally validated for calibration [10]. The models exist. Evidence for trusting their probability outputs largely does not.

The problem runs deeper than calibration alone. Campagner and colleagues reviewed machine learning studies in healthcare and found fewer than 4% address uncertainty quantification explicitly [11]. A model outputting a probability with no indication of how much to trust that number puts clinicians in a difficult position. Banerji and colleagues stated it plainly: clinical AI tools must communicate predictive uncertainty at the level of the individual patient, not purely in aggregate performance statistics [12]. A predicted CKD risk of 78% warrants a different clinical response when the model's uncertainty is narrow than when high uncertainty renders the output practically unreliable.

A 2023 systematic review commissioned to support CDC prevention guidelines reached a pointed conclusion: CKD risk prediction models need to be better calibrated and externally validated before incorporation into clinical guidelines [13]. No published CKD study has operationalized all three demands together. None has jointly evaluated calibration across multiple post-hoc correction methods, quantified uncertainty through a coverage-guaranteed conformal framework, and assessed deployment readiness through a structured multi-criterion checklist on the same model suite across an independent external cohort.

This study addresses that gap. Using the UCI CKD dataset for model development and MIMIC-IV as an external validation cohort, we trained five classifiers spanning the range commonly used in clinical prediction: logistic regression, random forest, gradient boosting via XGBoost, a support vector machine with Platt-scaled probabilities, and Gaussian naive Bayes. Each model was evaluated across three dimensions: calibration before and after post-hoc recalibration using Platt scaling and isotonic regression; predictive uncertainty through split conformal prediction with a formal 90% marginal coverage guarantee; and a structured eight-criterion deployment readiness framework grounded in current reporting standards including TRIPOD+AI [14].

Three objectives guided the work:

1. Quantify pre- and post-calibration error for five CKD classifiers on both the internal UCI test set and the external MIMIC-IV cohort.
2. Apply split conformal prediction to generate prediction sets with a 90% coverage guarantee and determine whether the guarantee holds on external data.
3. Score each model against an eight-criterion deployment readiness checklist and identify which, if any, meet the threshold for responsible clinical use.

---

## 2. Methods

### 2.1 Datasets

Two datasets were used. The UCI CKD dataset served as the primary training and internal validation source [15]. It contains 400 patient records collected from a hospital in Vellore, India, each described by 24 clinical and laboratory features alongside a binary CKD label. Of the 400 patients, 250 (62.5%) carry a positive CKD diagnosis, with a mean patient age of 51.6 years (SD 17.0). Features span continuous measurements including serum creatinine, blood urea, hemoglobin, sodium, potassium, and packed cell volume, alongside categorical variables for comorbidities (hypertension, diabetes, coronary artery disease) and urinary findings (red blood cell morphology, pus cells, bacteria).

The MIMIC-IV Clinical Database (version 2.2) provided the external validation cohort [16]. MIMIC-IV is a freely accessible, de-identified electronic health record dataset from the Beth Israel Deaconess Medical Center in Boston, Massachusetts. The study used the 100-patient public demonstration subset. From this cohort, patients were included if serum creatinine was available on their first hospital admission, yielding 97 patients. A binary CKD label was derived using the CKD-EPI 2021 race-free equation: eGFR below 60 mL/min/1.73m2 was classified as CKD-positive, giving 23 CKD cases (23.7%) and 74 controls. Mean age in the MIMIC cohort was 61.7 years (SD 16.3).

MIMIC-IV data were accessed under a PhysioNet credentialed license. The dataset is de-identified and its use requires completion of CITI human subjects training, which was completed prior to data access. No new patient contact occurred and no institutional review was required.

### 2.2 Preprocessing and Feature Harmonization

UCI preprocessing followed a standard pipeline. String values in all categorical columns were stripped of whitespace before encoding. Categorical features (red blood cell morphology, pus cell appearance, pus cell clumps, bacteria, hypertension, diabetes mellitus, coronary artery disease, appetite, pedal edema, anemia) were mapped to binary 0/1 values. The target label was encoded as CKD=1, notCKD=0. Missing values in continuous features were filled with the column median; missing values in categorical features were filled with the column mode. After imputation, zero missing values remained across all 400 records and 25 columns.

MIMIC harmonization used imputation statistics derived exclusively from the UCI training fold to prevent information leakage. Seven features present in the UCI dataset are not routinely recorded in MIMIC: urine-specific gravity, urine sugar, pus cells (categorical), pus cell clumps, bacteria, appetite, and pedal edema. These columns were imputed using UCI training-set medians or modes. Blood pressure was extracted from ICU chartevents (MIMIC item IDs 220179 and 220050, systolic range 60-250 mmHg) and, where unavailable, from the MIMIC outpatient medical record table. This two-source approach resolved blood pressure for 94 of 97 patients. Serum creatinine, blood urea nitrogen, hemoglobin, albumin, potassium, sodium, glucose, hematocrit, WBC count, and RBC count were extracted from MIMIC laboratory events using established item IDs, averaged across each patient's first admission. Comorbidity flags for hypertension, diabetes, and coronary artery disease were derived from ICD-10 diagnosis codes (I10, E11.x, I25.x respectively). Anemia was defined as hemoglobin below 12 g/dL for female patients and below 13.5 g/dL for male patients.

After harmonization, the MIMIC dataset aligned to the identical 25-column schema as the processed UCI dataset. No test-set information was used at any stage of imputation.

### 2.3 Model Suite and Training

The UCI dataset was split into training (70%, n=279), validation (15%, n=60), and test (15%, n=61) subsets using stratified random sampling to preserve CKD prevalence in each fold (random_state=42). The MIMIC cohort was reserved entirely as an external test set. No MIMIC records appeared in any training or validation fold.

Five classifier families were selected to represent the range of calibration behaviors reported in the clinical ML literature. Logistic regression with L2 regularization serves as a well-calibrated linear baseline. Random forest is an ensemble learner known to produce overconfident probabilities. XGBoost is a gradient-boosted tree model achieving strong discrimination but typically miscalibrated. The support vector machine was fitted with probability=True, applying internal Platt scaling during training. Gaussian naive Bayes produces class-conditional probability estimates and is often considered naturally calibrated for binary problems.

Hyperparameter tuning used five-fold stratified cross-validation on the training fold, optimizing AUROC. Logistic regression C was tuned by grid search over {0.001, 0.01, 0.1, 1, 10, 100}. Random forest, XGBoost, and SVM used randomized search with a maximum of 30 iterations over defined parameter grids. All fitted models were saved using joblib for use in subsequent calibration and uncertainty pipelines. All random seeds were set to 42 throughout.

Software: Python 3.13, scikit-learn, XGBoost, MAPIE 1.3, netcal, pandas, numpy, matplotlib, seaborn, joblib. Full version specifications are listed in requirements.txt in the project repository.

### 2.4 Calibration Evaluation

Pre-calibration assessment was performed on the UCI validation set. For each model, predicted probabilities were obtained and four metrics were computed: Expected Calibration Error (ECE) using 10 equal-width bins, Maximum Calibration Error (MCE) using the same binning, Brier Score, and Brier Skill Score relative to a naive climatology baseline equal to the validation-set prevalence. Reliability diagrams were generated using CalibrationDisplay from scikit-learn. ECE and MCE were computed using the netcal library.

Post-hoc recalibration was applied through two methods fitted exclusively on the validation set. Platt scaling fits a logistic regression layer on the base model's raw scores, implemented via CalibratedClassifierCV with method='sigmoid' and cv='prefit'. Isotonic regression fits a piecewise-constant monotone function on the raw scores, implemented via CalibratedClassifierCV with method='isotonic' and cv='prefit'. In both cases, FrozenEstimator from scikit-learn prevented refitting of the base model. The test set was never used during calibration fitting.

Post-calibration metrics were computed on the UCI test set for the base, Platt-scaled, and isotonic-scaled variants of each model. For external validation, the best-calibrated variant per model (selected by lowest ECE on the UCI test set) was applied to the MIMIC cohort, and ECE, MCE, Brier Score, and AUROC were computed. Calibration drift was defined as MIMIC ECE minus UCI ECE for the selected variant.

### 2.5 Uncertainty Quantification

Predictive uncertainty was quantified through split conformal prediction using the MAPIE library (SplitConformalClassifier, version 1.3). Split conformal prediction is a distribution-free method providing a finite-sample marginal coverage guarantee: with probability at least 1-alpha over the calibration set, the true label appears in the predicted set for at least 1-alpha fraction of test cases [17].

For each of the five base models, a conformal predictor was fitted using the UCI validation set as the conformalization set (n=60). The conformity score was the least ambiguous class (LAC) score, defined as one minus the predicted probability of the most likely class. The target confidence level was 0.90 (alpha=0.10), meaning each patient's prediction set should contain the true label at least 90% of the time.

Three metrics were computed on both the UCI test set and the MIMIC cohort: empirical coverage rate (proportion of test cases where the true label falls in the prediction set), average prediction set size (ranging from 0 for empty sets to 2 for ambiguous predictions), and singleton rate (proportion of cases with exactly one class in the set). Coverage drift was defined as UCI coverage minus MIMIC coverage.

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

All metrics are reported as point estimates on the held-out test sets. Bootstrap confidence intervals (95%, 1,000 resamples with replacement, random_state=42) were computed for AUROC and ECE on both the UCI test set and the MIMIC cohort. No hypothesis testing was performed; this study is descriptive and evaluative in design.

---

## 3. Results

### 3.1 Cohort Characteristics

The UCI CKD dataset included 400 patients with a mean age of 51.6 years (SD 17.0). CKD prevalence was 62.5% (n=250). The dataset contained 14 continuous features and 10 binary categorical features. After preprocessing, zero missing values remained. The 70/15/15 stratified split produced 279 training, 60 validation, and 61 test patients, each maintaining CKD prevalence within 1 percentage point of the full dataset.

The MIMIC-IV external cohort comprised 97 patients from the de-identified clinical database demonstration subset. Mean age was 61.7 years (SD 16.3). CKD prevalence was substantially lower at 23.7% (n=23), reflecting the broader hospital population from which the cohort was drawn. Seven of the 24 model features (urine specific gravity, urine sugar, pus cells, pus cell clumps, bacteria, appetite, and pedal edema) were not available in MIMIC and were imputed using UCI training-set statistics. Blood pressure was resolved through a combination of ICU chartevents and outpatient medical record data, achieving 94.8% coverage.

### 3.2 Baseline Discrimination

All five models achieved AUROC 1.00 on the UCI test set, indicating the dataset offers essentially no discrimination challenge once models are fitted. RF and SVM achieved perfect F1, accuracy, sensitivity, and specificity. LR performed noticeably below the ensemble models on accuracy (0.77) and specificity (0.39), suggesting it assigned CKD-positive probabilities to most patients regardless of feature values, a pattern consistent with a miscalibrated intercept. XGB and NB achieved F1 of 0.987. Cross-validation AUROC during tuning was 0.999-1.000 across all models, confirming the UCI benchmark is close to saturated.

### 3.3 Pre-Calibration Assessment

On the UCI validation set, calibration quality varied considerably across models before any post-hoc correction. LR showed the weakest calibration by a wide margin: ECE 0.263, MCE 0.483, Brier Score 0.164, Brier Skill Score 0.295. The three tree-based and kernel-based models performed substantially better. XGB produced the lowest pre-calibration ECE (0.031) and Brier Score (0.005), with a Brier Skill Score of 0.977 indicating near-ideal probability accuracy relative to the climatology baseline. RF, SVM, and NB fell between XGB and LR, with ECE values of 0.053, 0.042, and 0.050 respectively. Reliability diagrams confirmed that LR systematically underestimated CKD probability at low predicted values and overestimated at the high end, while XGB and SVM showed much tighter alignment with the diagonal.

### 3.4 Post-Calibration Results

Isotonic regression produced the largest ECE reductions across the suite. On the UCI test set, isotonic calibration reduced LR's ECE from 0.345 to 0.022 (95% CI: 0.002-0.050), a reduction of 0.323. RF reached ECE 0.000 after isotonic calibration, meaning its probability outputs were essentially perfectly aligned with observed frequencies on the test set. XGB improved from 0.019 to 0.007 (95% CI: 0.000-0.021). SVM improved from 0.031 to 0.015 (95% CI: 0.000-0.037). For NB, the uncalibrated model produced lower ECE (0.016, 95% CI: 0.000-0.049) than either post-hoc method, so the base variant was selected for NB. Platt scaling produced mixed results: it improved LR substantially but worsened SVM considerably, raising its ECE from 0.031 to 0.307, likely because the non-monotone relationship between SVM decision scores and true probabilities undermines the sigmoid fit in this dataset.

### 3.5 External Calibration on MIMIC-IV

When the best-calibrated variant of each model was applied to the MIMIC-IV cohort, calibration deteriorated sharply across the board. AUROC fell to 0.485 (LR), 0.507 (RF), 0.579 (XGB), 0.483 (SVM), and 0.477 (NB). All values are near or below chance. ECE on MIMIC reached 0.761 (LR, 95% CI: 0.673-0.844), 0.753 (RF, 95% CI: 0.660-0.835), 0.680 (XGB, 95% CI: 0.594-0.777), 0.755 (SVM, 95% CI: 0.667-0.837), and 0.753 (NB, 95% CI: 0.660-0.835). Calibration drift ranged from 0.673 (XGB) to 0.753 (RF), far exceeding the 0.05 acceptable threshold. Reliability diagrams for the MIMIC cohort showed all models assigning probabilities in a narrow band well below 0.5, reflecting the difference in prevalence between the UCI training population (62.5% CKD) and the MIMIC cohort (23.7% CKD). XGB performed least poorly across both AUROC and ECE on external data.

### 3.6 Conformal Prediction Coverage

On the UCI test set, four of five models met the 90% coverage target. NB achieved the highest coverage (0.984) with a singleton rate of 1.00, meaning every test case received a definitive prediction. RF and XGB both reached 0.967 coverage with singleton rates of 0.967. SVM achieved 0.918 coverage. LR failed the target with coverage of 0.803, consistent with its miscalibrated probabilities producing unreliable conformity scores.

Coverage collapsed when conformal predictors trained on the UCI validation set were applied to the MIMIC cohort. NB reached the highest MIMIC coverage at 0.247; the others ranged from 0.206 to 0.237. All five models fell below 0.30, against a 0.90 target. Coverage drift ranged from 0.566 (LR) to 0.761 (RF). The conformal guarantee, which is valid only when calibration and test distributions are exchangeable, clearly did not transfer across the distributional shift between these two cohorts.

### 3.7 Deployment Readiness Scores

No model passed the deployment readiness checklist. Scores ranged from 2 out of 16 (XGB) to 4 out of 16 (LR, RF, SVM, NB). The only criteria any model passed were prediction interpretability on UCI (singleton rate above 0.70) and transparency (code and pipeline are publicly reproducible). All five models failed discrimination adequacy on MIMIC, calibration adequacy on MIMIC, calibration stability, conformal coverage on MIMIC, coverage stability, and subgroup calibration equity. Subgroup ECE gaps ranged from 0.148 to 0.209 across age and comorbidity strata, all far above the 0.05 equity threshold. XGB received the lowest score (2/16) because its MIMIC singleton rate of 0.474 also failed the interpretability criterion, while the other four models passed interpretability on UCI but not on MIMIC.

---

## 4. Discussion

### 4.1 The Gap Between Internal Performance and External Readiness

Every model in this study achieved AUROC 1.00 on the internal UCI test set. By the standard evaluation metrics that dominate published clinical ML literature, all five would be described as performing excellently. Yet when the same models were applied to real hospital data from MIMIC-IV, AUROC fell to values indistinguishable from chance (0.48 to 0.58), ECE exceeded 0.68 for every model, and conformal coverage dropped from near-target to 0.21-0.25. No model crossed a single external-validation threshold on the deployment checklist.

This gap is the central finding. It does not signal that these algorithms are poorly designed. It reflects something more fundamental: the UCI CKD dataset, while widely used in classification benchmarks, does not represent the distributional complexity of real clinical data. The UCI cohort was collected from a single referral hospital, carries a 62.5% CKD prevalence, and features clean clinical measurements that in practice are rarely all available at once. The MIMIC-IV cohort represents a broader, noisier hospital population with a 23.7% CKD prevalence and seven features completely absent from the routine EHR. Isotonic calibration that achieved ECE 0.000 internally did not survive the shift.

The pattern is consistent with findings from systematic reviews. Echouffo-Tcheugui and Kengne identified that external calibration validation is the exception rather than the norm in the CKD prediction literature [10]. This study provides a concrete illustration of why that gap matters: a model that looks ready is not ready.

### 4.2 What Drove the External Failure

Three factors contributed to the calibration collapse on MIMIC. First, the prevalence shift. A model trained and calibrated on a 62.5% CKD population assigns probabilities near the training prevalence. The MIMIC cohort sits at 23.7% CKD, so those probability estimates are systematically too high, producing calibration curves that fall well above the diagonal at every predicted probability level.

Second, feature missingness. Seven of the 24 features in the UCI schema are not routinely recorded in MIMIC. Urine-specific gravity, urine sugar, pus cells, pus cell clumps, bacteria, appetite, and pedal edema were all imputed using UCI training-set medians and modes. Those imputed values carry no information about individual MIMIC patients. From the model's perspective, seven features are effectively noise columns on the external cohort.

Third, dataset saturation. AUROC 1.00 on a 61-patient test set, with near-perfect cross-validation scores, signals that the UCI benchmark does not offer a realistic discrimination challenge. The learned decision boundaries are sharp enough to separate every patient in the training domain perfectly, but those boundaries do not generalize to a population with different disease severity distribution and measurement patterns.

XGB was the least poor performer externally (AUROC 0.579, ECE 0.680). That small margin is worth noting: gradient boosting with regularization appears to learn slightly more transferable representations than simpler ensembles or parametric models in this setting.

### 4.3 Conformal Prediction as a Diagnostic Tool

The conformal coverage collapse offers something the calibration numbers alone do not: a direct, interpretable signal of distribution shift. The theoretical guarantee of split conformal prediction holds when calibration and test data come from the same distribution [17]. Coverage of 0.22-0.25 on MIMIC, against a 0.90 target, is a quantitative statement that the MIMIC population is not exchangeable with the UCI validation set. A clinician or system operator who sees conformal coverage fall from 0.97 to 0.22 knows immediately that the model is operating outside its valid domain.

This is the practical value of including conformal prediction in a deployment readiness framework, separate from its theoretical properties. It provides a coverage audit trail. If conformal coverage on a new deployment site sits above 0.85, the uncertainty estimates are likely reliable. If it drops to 0.22, the model should not be used.

NB and LR showed the highest MIMIC singleton rates (0.990 and 1.000 respectively), meaning most of their prediction sets contain exactly one class label, which appears interpretable. It is not: when coverage is only 0.24, a singleton prediction is a confident wrong answer for three-quarters of patients. Singleton rate without coverage is not a useful interpretability metric.

### 4.4 Comparison to Published CKD Models

The eight externally-validated CKD models identified by Echouffo-Tcheugui and Kengne reported a range of calibration outcomes, but calibration was assessed informally in most cases, often through visual inspection of calibration plots without ECE or Brier Score computation [10]. More recent models, including the KFRE validated by Tangri and colleagues [6] and its UK validation by Major and colleagues [7], achieve strong external discrimination (C-statistic 0.80-0.90) in proper prospective cohort studies. Those studies used purpose-built cohorts with consistent feature ascertainment, not retrospective harmonization of missing features.

The AUROC values seen on MIMIC in this study (0.48-0.58) are not comparable to published KFRE or ML model results, because those studies used cohorts where input features were actually measured. The comparison instead reinforces the point: a deployed clinical model needs external validation on data that reflects the deployment environment, not on a cleaned academic benchmark.

### 4.5 Limitations

Several limitations deserve direct acknowledgment. The MIMIC external cohort used here is the 100-patient public demonstration subset, not the full MIMIC-IV database. The small sample size (97 patients after filtering) means calibration metrics, particularly ECE with 10 bins, are estimated with wide uncertainty. Bootstrap confidence intervals for MIMIC ECE span ranges as large as 0.18 for some models. These results should be treated as illustrative of the analytic framework rather than definitive evidence about model performance in clinical deployment.

Feature harmonization introduced information dependency between the UCI domain and the MIMIC feature set. The seven imputed features were filled using UCI training statistics, which means the MIMIC cohort's representation of those features is an echo of the UCI training population. This is an inherent limitation of cross-dataset harmonization when features are domain-specific.

The UCI dataset was collected from a single hospital in India. MIMIC-IV reflects a tertiary care academic medical center in the United States. These are not just different populations; they represent different healthcare contexts, referral patterns, and measurement standards. External validation across such different settings is useful for stress-testing, but the results do not directly estimate deployment performance in any specific clinical setting.

Subgroup analysis was limited by sample size. Diabetes and hypertension subgroups each contained fewer than 10 patients in some strata, making ECE estimation unreliable. Age subgroups (below 65: n=55; 65 and above: n=42) were sufficiently sized but still small. A properly powered subgroup calibration analysis would require several hundred external patients per stratum.

### 4.6 Future Directions

Three areas warrant follow-on work. First, the full MIMIC-IV database, accessed through a PhysioNet credentialed account, would provide several thousand patients with CKD-relevant laboratory data, allowing both larger-scale calibration assessment and properly powered subgroup analysis. The extraction pipeline developed for this study is directly applicable to the full database with no code changes.

Second, the deployment readiness framework introduced here is intentionally simple. Criteria are binary and thresholds are set a priori without formal sample size consideration. Extending the framework to account for uncertainty in threshold exceedance, for example through bootstrap p-values for each criterion, would make the checklist scores more principled.

Third, patient-facing uncertainty display is an open design problem. Conformal prediction sets at the individual level (CKD / not-CKD / ambiguous) are clinically interpretable labels. How clinicians and patients respond to ambiguous predictions in a real consultation, and whether explicit uncertainty communication changes treatment decisions compared to point probability outputs, remains untested in CKD care.

---

## 5. Conclusion

Five classifiers achieved perfect discrimination on the UCI CKD benchmark, then failed every external validation criterion when applied to MIMIC-IV hospital data. Isotonic recalibration reduced internal ECE to near zero but did not prevent calibration drift exceeding 0.67 on the external cohort. Conformal coverage fell from 0.967 or higher internally to 0.21-0.25 on MIMIC. No model scored above 4 out of 16 on the deployment readiness checklist.

A complete evaluation requires, at minimum, calibration on external data from a different clinical setting, coverage-guaranteed uncertainty estimates, and an explicit check that both transfer across the distributional shift. Discrimination on a held-out internal test set is not sufficient evidence. The eight-criterion framework introduced here offers one structured approach to operationalizing those requirements before a model reaches clinical use.

---

## Acknowledgments

The author acknowledges the open-access data contributors who made this research possible. The UCI CKD dataset is publicly available through the UCI Machine Learning Repository. MIMIC-IV data were accessed under a PhysioNet credentialed license following completion of required human subjects training. Portions of this manuscript were drafted with the assistance of Claude (Anthropic), used for structural drafting and editorial refinement. The author takes full responsibility for all content, interpretations, and conclusions.

---

## Financial Disclosures

Funding: None.

Conflicts of interest: The author declares no financial or non-financial conflicts of interest relevant to the content of this manuscript.

---

## Data Availability

The UCI CKD dataset is publicly available at the UCI Machine Learning Repository (https://archive.ics.uci.edu/dataset/336/chronic+kidney+disease). MIMIC-IV data cannot be redistributed; access requires a credentialed PhysioNet account and CITI training completion. Analysis code, preprocessing pipelines, and supplementary materials are available at the project repository.

---

## References

[1] Francis A, et al. Chronic kidney disease and the global public health agenda: an international consensus. Nat Rev Nephrol. 2024;20:473-485. https://doi.org/10.1038/s41581-024-00820-6

[2] Krishnamurthy S, et al. Machine learning prediction models for chronic kidney disease using national health insurance claim data in Taiwan. Healthcare (Basel). 2021;9(5):546. https://doi.org/10.3390/healthcare9050546

[3] Bai Q, et al. Machine learning to predict end stage kidney disease in chronic kidney disease. Sci Rep. 2022;12:8377. https://doi.org/10.1038/s41598-022-12316-z

[4] Li J, et al. Machine learning models for predicting short-term progression in patients with stage 4 chronic kidney disease: a multi-center validation study. Sci Rep. 2025;15:39285. https://doi.org/10.1038/s41598-025-39285-x

[5] Sabanayagam C, et al. Artificial intelligence in chronic kidney disease management: a scoping review. Theranostics. 2025;15(10):4566-4578. https://doi.org/10.7150/thno.105842

[6] Tangri N, et al. Multinational assessment of accuracy of equations for predicting risk of kidney failure: a meta-analysis. JAMA. 2016;315(2):164-174. https://doi.org/10.1001/jama.2015.18202

[7] Major RW, et al. The Kidney Failure Risk Equation for prediction of end stage renal disease in UK primary care. PLOS Medicine. 2019;16(11):e1002955. https://doi.org/10.1371/journal.pmed.1002955

[8] Bravo-Zuniga JI, et al. External validation, recalibration, and clinical utility of the kidney failure risk equation in patients with advanced CKD. BMC Nephrology. 2025;26:688. https://doi.org/10.1186/s12882-025-04103-z

[9] Van Calster B, et al. Calibration: the Achilles heel of predictive analytics. BMC Medicine. 2019;17:230. https://doi.org/10.1186/s12916-019-1466-7

[10] Echouffo-Tcheugui JB, Kengne AP. Risk models to predict chronic kidney disease and its progression: a systematic review. PLOS Medicine. 2012;9(11):e1001344. https://doi.org/10.1371/journal.pmed.1001344

[11] Campagner A, et al. Modeling unknowns: a vision for uncertainty-aware machine learning in healthcare. Int J Med Inform. 2025;203:106014. https://doi.org/10.1016/j.ijmedinf.2025.106014

[12] Banerji CRS, et al. Clinical AI tools must convey predictive uncertainty for each individual patient. Nat Med. 2023;29:2996-2998. https://doi.org/10.1038/s41591-023-02562-7

[13] Gonzalez-Rocha A, et al. Risk prediction score for chronic kidney disease in healthy adults and adults with type 2 diabetes: systematic review. Prev Chronic Dis. 2023;20:220380. https://doi.org/10.5888/pcd20.220380

[14] Collins GS, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ. 2024;385:e078378. https://doi.org/10.1136/bmj-2023-078378

[15] Soundarapandian L, Srinivasan K. Chronic Kidney Disease Dataset. UCI Machine Learning Repository. 2015. https://archive.ics.uci.edu/dataset/336/chronic+kidney+disease

[16] Johnson AEW, et al. MIMIC-IV, a freely accessible electronic health record dataset. Sci Data. 2023;10:1. https://doi.org/10.1038/s41597-022-01899-x

[17] Angelopoulos AN, Bates S. A gentle introduction to conformal prediction and distribution-free uncertainty quantification. Found Trends Mach Learn. 2023;16(4):494-591. https://doi.org/10.1561/2200000101

[18] Platt JC. Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods. In: Advances in Large Margin Classifiers. MIT Press; 1999:61-74.

[19] Zadrozny B, Elkan C. Transforming classifier scores into accurate multiclass probability estimates. Proc 8th ACM SIGKDD. 2002:694-699. https://doi.org/10.1145/775047.775151

[20] Guo C, Pleiss G, Sun Y, Weinberger KQ. On calibration of modern neural networks. Proc 34th Int Conf Mach Learn. 2017;70:1321-1330.

[21] Taquet V, et al. MAPIE: an open-source library for distribution-free uncertainty quantification. arXiv. 2022. arXiv:2207.12274

[22] Van Calster B, et al. A calibration hierarchy for risk models was defined from a systematic review of the literature. J Clin Epidemiol. 2016;74:167-176. https://doi.org/10.1016/j.jclinepi.2015.12.005
