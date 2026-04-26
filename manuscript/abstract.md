## Abstract

**Background:** Machine learning models for chronic kidney disease risk prediction regularly report strong discrimination but seldom undergo calibration assessment or uncertainty quantification before deployment consideration. No published study has jointly evaluated all three dimensions, calibration, uncertainty, and structured deployment readiness, on a common model suite with external clinical validation.

**Objective:** To evaluate five classifiers across calibration quality, conformal prediction coverage, and an eight-criterion deployment readiness framework on both internal and external data.

**Methods:** Five classifiers (logistic regression, random forest, XGBoost, support vector machine with Platt scaling, Gaussian naive Bayes) were trained on the UCI CKD dataset (400 patients, 62.5% CKD). External validation used a 97-patient MIMIC-IV cohort (23.7% CKD). Calibration was assessed before and after Platt scaling and isotonic regression, quantified by Expected Calibration Error and Brier Score. Predictive uncertainty was measured through split conformal prediction targeting 90% marginal coverage. An eight-criterion deployment readiness checklist assessed discrimination, calibration stability, coverage transfer, subgroup equity, and reproducibility.

**Results:** All five models achieved AUROC 1.00 on the UCI test set. Post-isotonic ECE fell to 0.000-0.022 internally. On MIMIC-IV, AUROC dropped to 0.48-0.58, ECE rose to 0.68-0.76, and conformal coverage collapsed from 0.80-0.98 (UCI) to 0.21-0.25, well below the 90% target. No model passed the deployment checklist; scores ranged from 2 to 4 out of 16.

**Conclusion:** Near-perfect internal performance did not predict external readiness. Calibration stability and conformal coverage transfer should be standard requirements before any clinical ML model is considered for deployment.

**Keywords:** chronic kidney disease, machine learning, probability calibration, conformal prediction, deployment readiness, external validation
