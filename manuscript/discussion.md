## 4. Discussion

### 4.1 The Gap Between Internal Performance and External Readiness

Every model in this study achieved AUROC 1.00 on the internal UCI test set. By the standard evaluation metrics that dominate published clinical ML literature, all five would be described as performing excellently. Yet when the same models were applied to real hospital data from MIMIC-IV, AUROC fell to values indistinguishable from chance (0.48 to 0.58), ECE exceeded 0.68 for every model, and conformal coverage dropped from near-target to 0.21-0.25. No model crossed a single external-validation threshold on the deployment checklist.

This gap is the central finding. It is not a sign that these algorithms are poorly designed. It reflects something more fundamental: the UCI CKD dataset, while widely used in classification benchmarks, does not represent the distributional complexity of real clinical data. The UCI cohort was collected from a single referral hospital, carries a 62.5% CKD prevalence, and features clean clinical measurements that in practice are rarely all available at once. The MIMIC-IV cohort represents a broader, noisier hospital population with a 23.7% CKD prevalence and seven features completely absent from the routine EHR. Isotonic calibration that achieved ECE 0.000 internally did not survive the shift.

The pattern here is consistent with findings from systematic reviews. Echouffo-Tcheugui and Kengne identified that external calibration validation is the exception rather than the norm in the CKD prediction literature [10]. This study provides a concrete illustration of why that gap matters: a model that looks ready is not ready.

### 4.2 What Drove the External Failure

Three factors contributed to the calibration collapse. First, the prevalence shift. A model trained and calibrated on a 62.5% CKD population will assign probabilities near the training prevalence. The MIMIC cohort sits at 23.7% CKD, so those probability estimates are systematically too high, producing calibration curves that fall well above the diagonal at every predicted probability level. This is the most direct driver of high ECE on external data.

Second, feature missingness. Seven of the 24 features in the UCI schema are not routinely recorded in MIMIC. Urine-specific gravity, urine sugar, pus cells, pus cell clumps, bacteria, appetite, and pedal edema were all imputed using UCI training-set medians and modes. Those imputed values carry no information about individual MIMIC patients. From the model's perspective, seven features are effectively noise columns on the external cohort. The MIMIC patients are being evaluated on features that describe the UCI training population, not themselves.

Third, dataset saturation. AUROC 1.00 on a 61-patient test set, with near-perfect cross-validation scores, signals that the UCI benchmark does not offer a realistic discrimination challenge. The learned decision boundaries are sharp enough to separate every patient in the training domain perfectly. Those boundaries do not generalize to a population with different disease severity distribution and measurement patterns.

XGB was the least poor performer externally (AUROC 0.579, ECE 0.680). That small margin is worth noting: gradient boosting with regularization appears to learn slightly more transferable representations than the simpler ensemble (RF) or parametric models (LR, NB) in this setting.

### 4.3 Conformal Prediction as a Diagnostic Tool

The conformal coverage collapse offers something the calibration numbers alone do not: a direct, interpretable signal of distribution shift. The theoretical guarantee of split conformal prediction holds when calibration and test data come from the same distribution [17]. Coverage of 0.22-0.25 on MIMIC, against a 0.90 target, is a quantitative statement that the MIMIC population is not exchangeable with the UCI validation set. A clinician or system operator who sees conformal coverage fall from 0.97 to 0.22 knows immediately that the model is operating outside its valid domain.

This is the practical value of including conformal prediction in a deployment readiness framework, separate from its theoretical properties. It provides a coverage audit trail. If the conformal coverage on a new deployment site sits above 0.85, the uncertainty estimates are likely reliable. If it drops to 0.22, the model should not be used.

NB and LR showed the highest MIMIC singleton rates (0.990 and 1.000 respectively), meaning most of their prediction sets contain exactly one class label, which appears interpretable. It is not: when coverage is only 0.24, a singleton prediction is simply a confident wrong answer for three quarters of patients. Singleton rate without coverage is not a useful interpretability metric.

### 4.4 Comparison to Published CKD Models

The eight externally-validated CKD models identified by Echouffo-Tcheugui and Kengne reported a range of calibration outcomes, but calibration was assessed informally in most cases, often through visual inspection of calibration plots without ECE or Brier Score computation [10]. More recent models, including the KFRE validated by Tangri and colleagues [6] and its UK validation by Major and colleagues [7], achieve strong external discrimination (C-statistic 0.80-0.90) in proper prospective cohort studies. Those studies use purpose-built cohorts with consistent feature ascertainment, not retrospective harmonization of missing features.

The AUROC values seen on MIMIC in this study (0.48-0.58) are not comparable to published KFRE or ML model results, because those studies used cohorts where the input features were actually measured. The comparison instead reinforces the point: a deployed clinical model needs external validation on data that reflects the deployment environment, not on a cleaned academic benchmark.

### 4.5 Limitations

Several limitations should be acknowledged directly. The MIMIC external cohort used in this study is the 100-patient public demonstration subset, not the full MIMIC-IV database. The small sample size (97 patients after filtering) means calibration metrics, particularly ECE with 10 bins, are estimated with wide uncertainty. Bootstrap confidence intervals for MIMIC ECE span ranges as large as 0.18 for some models. These results should be treated as illustrative of the analytic framework rather than definitive evidence about model performance in clinical deployment.

Feature harmonization introduced information leakage between the UCI domain and the MIMIC feature set. The seven imputed features were filled using UCI training statistics, which means the MIMIC cohort's representation of those features is simply an echo of the UCI training population. This is an inherent limitation of cross-dataset harmonization when features are domain-specific.

The UCI dataset is collected from a single hospital in India. MIMIC-IV reflects a tertiary care academic medical center in the United States. These are not just different populations; they represent different healthcare contexts, referral patterns, and measurement standards. External validation across such different settings is useful for stress-testing, but the results do not directly estimate deployment performance in any specific clinical setting.

Subgroup analysis was limited. DM and HTN subgroups each contained fewer than 10 patients, making ECE estimation unreliable. Age subgroups (below 65: n=55; 65 and above: n=42) were sufficiently sized but still small. A properly powered subgroup calibration analysis would require several hundred external patients per stratum.

### 4.6 Future Directions

Three areas warrant follow-on work. First, the full MIMIC-IV database, accessed through a PhysioNet credentialed account, would provide several thousand patients with CKD-relevant laboratory data, allowing both larger-scale calibration assessment and properly powered subgroup analysis. The extraction pipeline developed for this study is directly applicable to the full database with no code changes.

Second, the deployment readiness framework developed here is intentionally simple. Criteria are binary and thresholds are set a priori without formal sample size consideration. Extending the framework to account for uncertainty in threshold exceedance, for example by using bootstrap p-values for each criterion, would make the checklist scores more principled and harder to game through threshold manipulation.

Third, patient-facing uncertainty display is an open design problem. Conformal prediction sets at the individual level (CKD / not-CKD / ambiguous) are clinically interpretable labels. How clinicians and patients respond to ambiguous predictions in a real consultation, and whether explicit uncertainty communication changes treatment decisions compared to point probability outputs, remains untested in CKD care.
