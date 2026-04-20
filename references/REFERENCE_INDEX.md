# Paper 1 — Reference Library
## Calibration, Uncertainty Communication, and Deployment Readiness in CKD Risk Prediction

Downloaded: 2026-04-20 | **31 PDFs + 1 DOI-only citation**

Reference expansion plan: see `REFERENCE_COMPLETION_PLAN.md` for the prioritized JAMIA Open-oriented additions.

---

## Core Gap Papers (cited in Introduction)

| # | File | Citation | Role in Paper |
|---|------|----------|---------------|
| 1 | `Echouffo-Tcheugui_Kengne_2012_CKD_Risk_Models_Systematic_Review_PLOS.pdf` | Echouffo-Tcheugui JB, Kengne AP. Risk models to predict chronic kidney disease and its progression: a systematic review. *PLOS Medicine*. 2012;9(11):e1001344. | **Primary gap citation** — "calibration is less commonly assessed"; only 8 CKD occurrence and 5 CKD progression models externally validated for calibration |
| 2 | `Campagner_2025_Modeling_Unknowns_Uncertainty_Aware_ML_Healthcare.pdf` | Campagner A, et al. Modeling unknowns: A vision for uncertainty-aware machine learning in healthcare. *Int J Medical Informatics*. 2025;203:106014. | **< 4% of clinical AI studies address uncertainty** gap citation |
| 3 | `Gonzalez-Rocha_2023_CDC_CKD_Risk_Prediction_Systematic_Review.pdf` | González-Rocha A, Colli VA, Denova-Gutiérrez E. Risk prediction score for chronic kidney disease in healthy adults and adults with type 2 diabetes: systematic review. *Prev Chronic Dis*. 2023;20:220380. | **CDC recommendation** — "models need to be better calibrated and externally validated before incorporation into guidelines" |

---

## Calibration Methodology Papers

| # | File | Citation | Role in Paper |
|---|------|----------|---------------|
| 4 | `Guo_et_al_2017_On_Calibration_of_Modern_Neural_Networks.pdf` | Guo C, Pleiss G, Sun Y, Weinberger KQ. On calibration of modern neural networks. *ICML*. 2017. arXiv:1706.04599. | ECE definition, reliability diagrams, temperature scaling — primary calibration methods citation |
| 5 | `Niculescu-Mizil_Caruana_2005_Predicting_Good_Probabilities.pdf` | Niculescu-Mizil A, Caruana R. Predicting good probabilities with supervised learning. *ICML*. 2005:625–632. | Which classifiers are miscalibrated and why (RF/boosting overconfident, NB extreme) |
| 6 | `Platt_1999_Probabilistic_Outputs_SVM_Platt_Scaling.pdf` | Platt J. Probabilistic outputs for support vector machines. In: *Advances in Large Margin Classifiers*. MIT Press; 1999:61–74. | Platt scaling (sigmoid calibration) methodology |
| 7 | `Zadrozny_Elkan_2002_Transforming_Classifier_Scores_Isotonic_Regression.pdf` | Zadrozny B, Elkan C. Transforming classifier scores into accurate multiclass probability estimates. *KDD*. 2002:694–699. | Isotonic regression calibration methodology |
| 8 | `VanCalster_2019_Calibration_Achilles_Heel_BMC.pdf` | Van Calster B, McLernon DJ, van Smeden M, Wynants L, Steyerberg EW. Calibration: the Achilles heel of predictive analytics. *BMC Medicine*. 2019;17:230. DOI:10.1186/s12916-019-1466-7. | Foundational clinical calibration paper — directly supports the paper's thesis |

---

## Uncertainty Quantification Papers

| # | File | Citation | Role in Paper |
|---|------|----------|---------------|
| 9 | `Angelopoulos_Bates_2022_Gentle_Introduction_Conformal_Prediction.pdf` | Angelopoulos AN, Bates S. A gentle introduction to conformal prediction and distribution-free uncertainty quantification. arXiv:2107.07511. 2022. | Theoretical foundation for conformal prediction / coverage guarantee |
| 10 | `Taquet_2022_MAPIE_Conformal_Prediction_Library.pdf` | Taquet V, et al. MAPIE: an open-source library for distribution-free uncertainty quantification. arXiv:2207.12274. 2022. | Software citation for MAPIE implementation |
| 11 | `Vazquez_2022_Conformal_Prediction_Clinical_JHealthcInformRes.pdf` | Vazquez J, Facelli JC. Conformal prediction in clinical medical sciences. *J Healthc Inform Res*. 2022;6:241–252. DOI:10.1007/s41666-021-00113-8. | Clinical conformal prediction review — directly supports uncertainty methods |
| 12 | `Sreenivasan_2025_Conformal_Prediction_MS_npjDigMed.pdf` | Sreenivasan AP, et al. Conformal prediction enables disease course prediction and allows individualized diagnostic uncertainty in multiple sclerosis. *npj Digital Medicine*. 2025;8:224. DOI:10.1038/s41746-025-01616-z. | Recent clinical EHR conformal prediction example with individualized uncertainty |
| 13 | `Banerji_2023_Clinical_AI_Uncertainty_NatMed.pdf` | Banerji CRS, Chakraborti T, Harbron C, et al. Clinical AI tools must convey predictive uncertainty for each individual patient. *Nature Medicine*. 2023;29:2996–2998. DOI:10.1038/s41591-023-02562-7. | Direct support for individual-level uncertainty communication in clinical AI |

---

## CKD Prediction Model Papers

| # | File | Citation | Role in Paper |
|---|------|----------|---------------|
| 14 | `Tangri_2016_KFRE_Multinational_Validation_JAMA.pdf` | Tangri N, Grams ME, Levey AS, et al. Multinational assessment of accuracy of equations for predicting risk of kidney failure: a meta-analysis. *JAMA*. 2016;315(2):164–174. | Primary CKD risk model — KFRE external validation showing calibration drift across populations |
| 15 | `Johnson_2023_MIMIC-IV_Freely_Accessible_EHR_Dataset.pdf` | Johnson AEW, Bulgarelli L, Shen L, et al. MIMIC-IV, a freely accessible electronic health record dataset. *Sci Data*. 2023;10:1. DOI:10.1038/s41597-022-01899-x. | Dataset citation for external validation cohort |
| 16 | `Major_2019_KFRE_UK_External_Validation_PLOS.pdf` | Major RW, Shepherd D, Medcalf JF, Xu G, Gray LJ, Brunskill NJ. The Kidney Failure Risk Equation for prediction of end stage renal disease in UK primary care: an external validation and clinical impact projection cohort study. *PLOS Medicine*. 2019;16(11):e1002955. DOI:10.1371/journal.pmed.1002955. | KFRE external validation — recalibration needed; calibration drift across populations |
| 17 | `Krishnamurthy_2021_ML_CKD_Prediction_Taiwan_NHI.pdf` | Krishnamurthy S, et al. Machine learning prediction models for chronic kidney disease using national health insurance claim data in Taiwan. *Healthcare (Basel)*. 2021;9(5):546. DOI:10.3390/healthcare9050546. | ML CKD prediction (CNN, AUROC 0.957) using population claims data — ML model breadth citation |
| 18 | `Bai_2022_ML_Predict_ESKD_Scientific_Reports.pdf` | Bai Q, Su C, Tang W, Li Y. Machine learning to predict end stage kidney disease in chronic kidney disease. *Scientific Reports*. 2022;12:8377. DOI:10.1038/s41598-022-12316-z. | ML-based ESKD prediction using routine labs — complements KFRE with a data-driven approach |
| 19 | `BravoZuniga_2025_KFRE_Peru_BMCNephrol.pdf` | Bravo-Zuniga JI, et al. External validation, recalibration, and clinical utility of the kidney failure risk equation in patients with advanced CKD: a nationwide retrospective cohort analysis in Peru. *BMC Nephrology*. 2025;26:688. DOI:10.1186/s12882-025-04357-z. | External validation + recalibration + decision curve analysis — directly aligned with this paper |
| 20 | `Li_2025_ML_CKD_Stage4_SciRep.pdf` | Li J, et al. Machine learning models for predicting short-term progression in patients with stage 4 chronic kidney disease: a multi-center validation study. *Scientific Reports*. 2025;15:39285. DOI:10.1038/s41598-025-23037-4. | Recent ML CKD progression model with multi-center validation |
| 21 | `Sabanayagam_2025_AI_CKD_Theranostics.pdf` | Sabanayagam C, et al. Artificial intelligence in chronic kidney disease management: a scoping review. *Theranostics*. 2025;15(10):4566–4578. DOI:10.7150/thno.108552. | Broad, recent CKD AI management review with nephrology relevance |

---

## Clinical Prediction Model Reporting and Evaluation

| # | File | Citation | Role in Paper |
|---|------|----------|---------------|
| 22 | `Collins_2024_TRIPOD_AI_BMJ.pdf` | Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ*. 2024;385:e078378. DOI:10.1136/bmj-2023-078378. | Current reporting standard for clinical prediction models using ML — essential for JAMIA-style rigor |
| 23 | `Collins_2024_Eval_CPM_Part1_BMJ.pdf` | Collins GS, Dhiman P, Ma J, et al. Evaluation of clinical prediction models (part 1): from development to external validation. *BMJ*. 2024;384:e074819. DOI:10.1136/bmj-2023-074819. | Why validation must assess discrimination, calibration, fairness, and generalizability |
| 24 | `Riley_2024_Eval_CPM_Part2_BMJ.pdf` | Riley RD, Archer L, Snell KIE, et al. Evaluation of clinical prediction models (part 2): how to undertake an external validation study. *BMJ*. 2024;384:e074820. DOI:10.1136/bmj-2023-074820. | Supports MIMIC-IV external validation design and interpretation |
| 25 | `Riley_2024_Eval_CPM_Part3_BMJ.pdf` | Riley RD, Snell KIE, Archer L, et al. Evaluation of clinical prediction models (part 3): calculating the sample size required for an external validation study. *BMJ*. 2024;384:e074821. DOI:10.1136/bmj-2023-074821. | Useful for explaining precision limitations in small MIMIC subgroups |
| 26 | `Vasey_2022_DECIDE_AI_BMJ.pdf` | Vasey B, Nagendran M, Campbell B, et al. Reporting guideline for the early stage clinical evaluation of decision support systems driven by artificial intelligence: DECIDE-AI. *BMJ*. 2022;377:e070904. DOI:10.1136/bmj-2022-070904. | Supports deployment-readiness and clinical evaluation framing |
| 27 | `Sounderajah_2025_STARD_AI_NatMed.pdf` | Sounderajah V, et al. The STARD-AI reporting guideline for diagnostic accuracy studies using artificial intelligence. *Nature Medicine*. 2025;31:3283–3289. DOI:10.1038/s41591-025-03953-8. | Newest AI diagnostic reporting standard (use selectively — paper is risk prediction, not purely diagnostic) |

---

## Calibration and Deployment in Clinical AI

| # | File | Citation | Role in Paper |
|---|------|----------|---------------|
| 28 | `Liou_2024_Calibration_Drift_Deployed_ML_npjDigMed.pdf` | Liou L, et al. Assessing calibration and bias of a deployed machine learning malnutrition prediction model within a large healthcare system. *npj Digital Medicine*. 2024;7:149. DOI:10.1038/s41746-024-01141-5. | Real deployed-healthcare example of calibration drift, subgroup bias, monitoring, and recalibration |

---

## CKD Clinical Guidelines

| # | File | Citation | Role in Paper |
|---|------|----------|---------------|
| 29 | `KDIGO_2024_CKD_Full_Guideline.pdf` | Kidney Disease: Improving Global Outcomes (KDIGO) CKD Work Group. KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease. *Kidney Int*. 2024;105(4S):S117–S314. DOI:10.1016/j.kint.2023.10.018. | Current CKD clinical guideline — supports CKD definition, risk assessment, and clinical relevance |
| 30 | `KDIGO_2024_CKD_Executive_Summary.pdf` | Levin A, et al. Executive summary of the KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease. *Kidney Int*. 2024;105(4):684–701. DOI:10.1016/j.kint.2023.10.016. | Shorter guideline citation for manuscript background |
| 31 | `Francis_2024_CKD_Global_Public_Health_NatRevNephrol.pdf` | Francis A, Harhay MN, Ong ACM, et al. Chronic kidney disease and the global public health agenda: an international consensus. *Nature Reviews Nephrology*. 2024;20:473–485. DOI:10.1038/s41581-024-00820-6. | High-impact burden/significance citation for the Introduction |

---

## DOI-Only Citations (no PDF required)

| Citation | Role in Paper |
|----------|---------------|
| Rubini L, Soundarapandian P, Eswaran P. *Chronic Kidney Disease* [Dataset]. UCI Machine Learning Repository. 2015. DOI:10.24432/C5G020. | Primary training dataset citation |

---

## Still Needed — Manual Download Required

These are all open-access papers but block automated download (require browser JavaScript rendering). Download manually via the URLs below and save to this folder.

| # | Filename to use | Citation | Open-Access URL |
|---|-----------------|----------|-----------------|
| A | `Efthimiou_2024_Developing_CPM_BMJ.pdf` | Efthimiou O, et al. Developing clinical prediction models: a step-by-step guide. *BMJ*. 2024;386:e078276. DOI:10.1136/bmj-2023-078276. | https://www.bmj.com/content/bmj/386/bmj-2023-078276.full.pdf |
| B | `Moons_2025_PROBAST_AI_BMJ.pdf` | Moons KGM, et al. PROBAST+AI: an updated quality, risk of bias, and applicability assessment tool for prediction models using regression or artificial intelligence methods. *BMJ*. 2025;388:e082505. DOI:10.1136/bmj-2024-082505. | https://www.bmj.com/content/bmj/388/bmj-2024-082505.full.pdf |
| C | `Austin_Steyerberg_2019_ICI_Calibration_StatMed.pdf` | Austin PC, Steyerberg EW. The Integrated Calibration Index (ICI) and related metrics for quantifying the calibration of logistic regression models. *Stat Med*. 2019;38(21):4051–4065. DOI:10.1002/sim.8281. | https://pmc.ncbi.nlm.nih.gov/articles/PMC6771733/ |
| D | `Larrarte_2024_KFRE_Colombia_IntJNephrol.pdf` | Larrarte C, et al. Validation of the Kidney Failure Risk Equation in the Colombian Population. *Int J Nephrol*. 2024;2024:1282664. DOI:10.1155/2024/1282664. | https://pmc.ncbi.nlm.nih.gov/articles/PMC10894049/ |
| E | `Pan_2024_KFRE_China_KidneyMed.pdf` | Pan L, et al. External validation of the Kidney Failure Risk Equation among urban community-based Chinese patients with CKD. *Kidney Medicine*. 2024;6(5):100817. DOI:10.1016/j.xkme.2024.100817. | https://pmc.ncbi.nlm.nih.gov/articles/PMC11059393/ |
| F | `Park_2020_AI_Evaluation_Phases_JAMIAOpen.pdf` | Park Y, Jackson GP, Foreman MA, et al. Evaluating artificial intelligence in medicine: phases of clinical research. *JAMIA Open*. 2020;3(3):326–331. DOI:10.1093/jamiaopen/ooaa033. | https://pmc.ncbi.nlm.nih.gov/articles/PMC7660958/ |

---

## Paywalled — Obtain via University of the Cumberlands Library

| Paper | Why needed | Where to get |
|-------|-----------|--------------|
| Tangri N et al. *JAMA*. 2011;305(15):1553–9. "A predictive model for progression of CKD to kidney failure." | Original KFRE paper — primary CKD model citation | University library portal → JAMA Network |

---

## Notes
- All 31 PDFs are open-access (arXiv, PMC, PLOS, BMC, BMJ, Nature OA, MDPI, Springer OA, Theranostics, KDIGO)
- 6 additional OA papers need browser-based download (listed above with direct URLs)
- Tangri 2011 (original KFRE) is paywalled — obtain via University of the Cumberlands library portal
- UCI dataset requires DOI citation only (no PDF)
- Task 7.8 requirement of "≥3 primary CKD ML model papers" is satisfied (#14–21)
- Target library size: 31 PDF + 6 manual + 1 library + 1 DOI = **39 total** — within the 35–40 JAMIA Open target
