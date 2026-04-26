## 3. Results

### 3.1 Cohort Characteristics

The UCI CKD dataset included 400 patients with a mean age of 51.6 years (SD 17.0). CKD prevalence was 62.5% (n=250). The dataset contained 14 continuous features and 10 binary categorical features. After preprocessing, zero missing values remained. The 70/15/15 stratified split produced 279 training, 60 validation, and 61 test patients, each with CKD prevalence within 1 percentage point of the full dataset.

The MIMIC-IV external cohort comprised 97 patients from the de-identified clinical database demonstration subset. Mean age was 61.7 years (SD 16.3). CKD prevalence was substantially lower at 23.7% (n=23), reflecting the broader hospital population from which the cohort was drawn. Seven of the 24 model features (urine specific gravity, urine sugar, pus cells, pus cell clumps, bacteria, appetite, and pedal edema) were not available in MIMIC and were imputed using UCI training-set statistics. Blood pressure was resolved through a combination of ICU chartevents and outpatient medical record data, achieving 94.8% coverage.

### 3.2 Baseline Discrimination (Table 1)

All five models achieved AUROC 1.00 on the UCI test set, indicating the dataset offers essentially no discrimination challenge once models are fitted. RF and SVM achieved perfect F1, accuracy, sensitivity, and specificity. LR performed noticeably below the ensemble models on accuracy (0.77) and specificity (0.39), suggesting it assigned CKD-positive probabilities to most patients regardless of feature values, a pattern consistent with a miscalibrated intercept. XGB and NB achieved F1 of 0.987. Cross-validation AUROC during tuning was 0.999-1.000 across all models, confirming the UCI benchmark is close to saturated.

### 3.3 Pre-Calibration Assessment

On the UCI validation set, calibration quality varied considerably across models before any post-hoc correction was applied. LR showed the weakest calibration by a wide margin: ECE 0.2631, MCE 0.4829, Brier Score 0.1637, Brier Skill Score 0.2949. The three tree-based and kernel-based models performed substantially better. XGB produced the lowest pre-calibration ECE (0.0307) and Brier Score (0.0053), with a Brier Skill Score of 0.977 indicating near-ideal probability accuracy relative to the climatology baseline. RF, SVM, and NB fell between XGB and LR, with ECE values of 0.0529, 0.0418, and 0.0500 respectively. Reliability diagrams confirmed that LR systematically underestimated CKD probability at low predicted values and overestimated at the high end, while XGB and SVM showed much tighter alignment with the diagonal.

### 3.4 Post-Calibration Results (Table 2)

Isotonic regression produced the largest ECE reductions across the suite. On the UCI test set, isotonic calibration reduced LR's ECE from 0.345 to 0.022 (95% CI: 0.002, 0.050), a reduction of 0.323. RF reached ECE 0.000 after isotonic calibration, meaning its probability outputs were essentially perfectly aligned with observed frequencies on the test set. XGB improved from 0.019 to 0.007 (95% CI: 0.000, 0.021). SVM improved from 0.031 to 0.015 (95% CI: 0.000, 0.037). For NB, the uncalibrated model produced lower ECE (0.016, 95% CI: 0.000, 0.049) than either post-hoc method, so the base variant was selected as the best for NB. Platt scaling produced mixed results: it improved LR substantially but worsened SVM considerably, raising its ECE from 0.031 to 0.307, likely due to the non-monotone relationship between SVM decision scores and true probabilities in this dataset.

### 3.5 External Calibration on MIMIC-IV (Table 2)

When the best-calibrated variant of each model was applied to the MIMIC-IV cohort, calibration deteriorated sharply across the board. AUROC fell to 0.485 (LR), 0.507 (RF), 0.579 (XGB), 0.483 (SVM), and 0.477 (NB). All values are near or below chance. ECE on MIMIC reached 0.761 (LR, 95% CI: 0.673, 0.844), 0.753 (RF, 95% CI: 0.660, 0.835), 0.680 (XGB, 95% CI: 0.594, 0.777), 0.755 (SVM, 95% CI: 0.667, 0.837), and 0.753 (NB, 95% CI: 0.660, 0.835). Calibration drift ranged from 0.673 (XGB) to 0.753 (RF), far exceeding the 0.05 acceptable threshold defined in the deployment framework. Reliability diagrams for the MIMIC cohort showed all models assigning probabilities in a narrow band well below 0.5, reflecting the difference in prevalence between the UCI training population (62.5% CKD) and the MIMIC cohort (23.7% CKD). XGB performed least poorly across both AUROC and ECE on external data.

### 3.6 Conformal Prediction Coverage (Table 3)

On the UCI test set, four of five models met the 90% coverage target. NB achieved the highest coverage (0.984) with a singleton rate of 1.00, meaning every test case received a definitive prediction. RF and XGB both reached 0.967 coverage with singleton rates of 0.967. SVM achieved 0.918 coverage. LR failed to meet the target with coverage of 0.803, consistent with its miscalibrated probabilities producing unreliable conformity scores.

Coverage collapsed when conformal predictors trained on the UCI validation set were applied to the MIMIC cohort. NB reached the highest MIMIC coverage at 0.247; the others ranged from 0.206 to 0.237. All five models fell below 0.30, against a 0.90 target. Coverage drift ranged from 0.566 (LR) to 0.761 (RF). The conformal guarantee, which is valid only when calibration and test distributions are exchangeable, clearly did not transfer across the data shift between these two cohorts.

### 3.7 Deployment Readiness Scores (Table 4)

No model passed the deployment readiness checklist. Scores ranged from 2 out of 16 (XGB) to 4 out of 16 (LR, RF, SVM, NB). The only criteria any model passed were prediction interpretability on UCI (singleton rate above 0.70) and transparency (code and pipeline are publicly reproducible). All five models failed discrimination adequacy on MIMIC, calibration adequacy on MIMIC, calibration stability, conformal coverage on MIMIC, coverage stability, and subgroup calibration equity. Subgroup ECE gaps ranged from 0.148 to 0.209 across age and comorbidity strata, all far above the 0.05 equity threshold. XGB received the lowest score (2/16) because its MIMIC singleton rate of 0.474 also failed the interpretability criterion, while the other four models passed that criterion on UCI but not on MIMIC.
