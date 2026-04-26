## Introduction

Roughly 850 million people worldwide are estimated to have chronic kidney disease, and the global prevalence grew by 33% between 1990 and 2017 [1]. Among people with diabetes, as many as 1 in 3 are affected; among those with hypertension in high-income settings, the proportion reaches approximately 1 in 5 [1]. By 2040, CKD is projected to rank fifth among leading causes of years of life lost globally [1]. Those numbers create genuine pressure on health systems to identify high-risk patients early, before irreversible loss of kidney function closes off the best treatment options.

Machine learning has been proposed as a practical answer to this challenge. Models trained on electronic health records, biomarker panels, and demographic variables have reported AUROC values above 0.95 in national cohort studies [2,3,4,5]. Established risk equations like the Kidney Failure Risk Equation have been validated across populations in North America, the United Kingdom, and Latin America, confirming algorithmic CKD risk prediction is technically achievable [6,7,8]. The field has not struggled to build models. The struggle is with what happens after the model is built.

Discrimination metrics like AUROC measure whether a model ranks patients correctly relative to each other. They say nothing about whether the assigned probability scores are trustworthy in absolute terms. A model posting AUROC 0.97 assigns a 65% risk score to patients whose true event rate sits near 20%, and clinicians making treatment decisions from those numbers are working from miscalibrated information. Van Calster and colleagues identified calibration as the Achilles heel of predictive analytics, noting poor calibration regularly persists even when discrimination appears strong [9]. A systematic review of CKD risk models by Echouffo-Tcheugui and Kengne found calibration is assessed less commonly than discrimination across the published literature; of all the models reviewed, only eight for CKD occurrence and five for CKD progression had been externally validated for calibration [10]. The models exist. The evidence for trusting their probability outputs largely does not.

The problem runs deeper than calibration alone. Campagner and colleagues reviewed machine learning studies in healthcare and found fewer than 4% address uncertainty quantification explicitly [11]. A model outputting a probability without any indication of how much to trust the number puts clinicians in a difficult position. Banerji and colleagues put this plainly: clinical AI tools must communicate predictive uncertainty at the level of the individual patient, not purely in aggregate performance statistics [12]. A predicted CKD risk of 78% warrants a different clinical response when the model's uncertainty is narrow than when high uncertainty renders the output practically unreliable.

A 2023 systematic review commissioned to support CDC prevention guidelines reached a pointed conclusion: CKD risk prediction models need to be better calibrated and externally validated before incorporation into clinical guidelines [13]. No published study in the CKD literature has operationalized all three of these demands together. No existing work has jointly evaluated calibration across multiple post-hoc correction methods, quantified uncertainty through a coverage-guaranteed conformal framework, and assessed deployment readiness through a structured multi-criterion checklist, all on the same model suite and across an independent external cohort.

This study addresses the gap. Using the UCI CKD dataset for model development and MIMIC-IV as an external validation cohort, we trained five classifiers spanning the range commonly used in clinical prediction: logistic regression, random forest, gradient boosting via XGBoost, a support vector machine with Platt-scaled probabilities, and Gaussian naive Bayes. Each model was evaluated across three dimensions: calibration before and after post-hoc recalibration using Platt scaling and isotonic regression; predictive uncertainty through split conformal prediction with a formal 90% marginal coverage guarantee; and a structured eight-criterion deployment readiness framework grounded in current reporting standards including TRIPOD+AI [14].

The study has three objectives:

1. Quantify pre- and post-calibration error for five CKD classifiers on both the internal UCI test set and the external MIMIC-IV cohort.
2. Apply split conformal prediction to generate prediction sets with a 90% coverage guarantee and determine whether the guarantee holds on external data.
3. Score each model against an eight-criterion deployment readiness checklist and identify which, if any, meet the threshold for responsible clinical use.


References (this section)
[1] Francis A, et al. Chronic kidney disease and the global public health agenda: an international consensus. Nat Rev Nephrol. 2024;20:473-485.
[2] Krishnamurthy S, et al. Machine learning prediction models for chronic kidney disease using national health insurance claim data in Taiwan. Healthcare (Basel). 2021;9(5):546.
[3] Bai Q, et al. Machine learning to predict end stage kidney disease in chronic kidney disease. Sci Rep. 2022;12:8377.
[4] Li J, et al. Machine learning models for predicting short-term progression in patients with stage 4 chronic kidney disease: a multi-center validation study. Sci Rep. 2025;15:39285.
[5] Sabanayagam C, et al. Artificial intelligence in chronic kidney disease management: a scoping review. Theranostics. 2025;15(10):4566-4578.
[6] Tangri N, et al. Multinational assessment of accuracy of equations for predicting risk of kidney failure: a meta-analysis. JAMA. 2016;315(2):164-174.
[7] Major RW, et al. The Kidney Failure Risk Equation for prediction of end stage renal disease in UK primary care. PLOS Medicine. 2019;16(11):e1002955.
[8] Bravo-Zuniga JI, et al. External validation, recalibration, and clinical utility of the kidney failure risk equation in patients with advanced CKD. BMC Nephrology. 2025;26:688.
[9] Van Calster B, et al. Calibration: the Achilles heel of predictive analytics. BMC Medicine. 2019;17:230.
[10] Echouffo-Tcheugui JB, Kengne AP. Risk models to predict chronic kidney disease and its progression: a systematic review. PLOS Medicine. 2012;9(11):e1001344.
[11] Campagner A, et al. Modeling unknowns: A vision for uncertainty-aware machine learning in healthcare. Int J Med Inform. 2025;203:106014.
[12] Banerji CRS, et al. Clinical AI tools must convey predictive uncertainty for each individual patient. Nat Med. 2023;29:2996-2998.
[13] Gonzalez-Rocha A, et al. Risk prediction score for chronic kidney disease in healthy adults and adults with type 2 diabetes: systematic review. Prev Chronic Dis. 2023;20:220380.
[14] Collins GS, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ. 2024;385:e078378.
