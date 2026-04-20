# Reference Completion Plan for JAMIA Open Submission

Project: Calibration, Uncertainty Communication, and Deployment Readiness in CKD Risk Prediction

Created: 2026-04-20

## JAMIA Open Reference Expectation

JAMIA Open lists references as unlimited for Research and Applications articles. The practical target for this paper should therefore be relevance and coverage, not a fixed count. For a 4000-word original research manuscript, a defensible working range is 30-45 references.

Current library: 14 PDF papers + 1 dataset citation.

Recommended completed library target: 35-40 total references.

Priority principle: add recent peer-reviewed papers that strengthen (1) prediction-model reporting, (2) calibration and external validation methodology, (3) uncertainty/conformal prediction in clinical AI, (4) CKD/KFRE external validation and recalibration, and (5) clinical AI deployment readiness.

## Highest Priority Additions

These should be cited in the main manuscript if space allows.

| Priority | Citation | Why this matters | Status |
|---|---|---|---|
| 1 | Collins GS, Moons KGM, Dhiman P, Riley RD, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ. 2024;385:e078378. doi:10.1136/bmj-2023-078378 | Current reporting standard for clinical prediction models using regression or ML. Essential for JAMIA-style rigor. | Add PDF if available; cite in Methods/reporting |
| 2 | Moons KGM, Damen JAA, Kaul T, Hooft L, Navarro CA, Dhiman P, et al. PROBAST+AI: an updated quality, risk of bias, and applicability assessment tool for prediction models using regression or artificial intelligence methods. BMJ. 2025;388:e082505. doi:10.1136/bmj-2024-082505 | Newest risk-of-bias/applicability standard for prediction models and AI models. Useful for deployment-readiness rationale. | Add PDF if available; cite in Methods/Discussion |
| 3 | Collins GS, Dhiman P, Ma J, Schlussel MM, Archer L, Van Calster B, et al. Evaluation of clinical prediction models (part 1): from development to external validation. BMJ. 2024;384:e074819. doi:10.1136/bmj-2023-074819 | Strong recent source for why validation must assess discrimination, calibration, fairness, and generalizability. | Add PDF if available; cite in Introduction/Methods |
| 4 | Riley RD, Archer L, Snell KIE, Ensor J, Dhiman P, Martin GP, et al. Evaluation of clinical prediction models (part 2): how to undertake an external validation study. BMJ. 2024;384:e074820. doi:10.1136/bmj-2023-074820 | Directly supports the MIMIC-IV external validation design and interpretation. | Add PDF if available; cite in Methods |
| 5 | Riley RD, Snell KIE, Archer L, Ensor J, Debray TPA, Van Calster B, et al. Evaluation of clinical prediction models (part 3): calculating the sample size required for an external validation study. BMJ. 2024;384:e074821. doi:10.1136/bmj-2023-074821 | Useful for explaining precision limitations, especially if MIMIC subgroup samples are small. | Optional PDF; cite if discussing sample size |
| 6 | Efthimiou O, Seo M, Chalkou K, Debray T, Egger M, Salanti G. Developing clinical prediction models: a step-by-step guide. BMJ. 2024;386:e078276. doi:10.1136/bmj-2023-078276 | Recent practical prediction-model development/evaluation guidance; complements TRIPOD+AI. | Add PDF if available |
| 7 | Van Calster B, McLernon DJ, van Smeden M, Wynants L, Steyerberg EW. Calibration: the Achilles heel of predictive analytics. BMC Med. 2019;17:230. doi:10.1186/s12916-019-1466-7 | Still one of the clearest clinical calibration papers. Not recent, but foundational and directly aligned with the paper's thesis. | Add PDF |
| 8 | Austin PC, Steyerberg EW. The Integrated Calibration Index (ICI) and related metrics for quantifying the calibration of logistic regression models. Stat Med. 2019;38(21):4051-4065. doi:10.1002/sim.8281 | Supports calibration quantification beyond ECE/Brier when discussing calibration plots and summary metrics. | Optional PDF |
| 9 | Liou L, Scott E, Parchure P, Freeman R, Timsina P, Kia A, et al. Assessing calibration and bias of a deployed machine learning malnutrition prediction model within a large healthcare system. npj Digit Med. 2024;7:149. doi:10.1038/s41746-024-01141-5 | Recent deployed-healthcare example showing calibration drift, subgroup bias, monitoring, and recalibration. Strong deployment-readiness support. | Add PDF |
| 10 | Banerji CRS, Chakraborti T, Harbron C, et al. Clinical AI tools must convey predictive uncertainty for each individual patient. Nat Med. 2023;29:2996-2998. doi:10.1038/s41591-023-02562-7 | Direct support for individual-level uncertainty communication in clinical AI. | Add PDF if accessible |
| 11 | Vazquez J, Facelli JC. Conformal Prediction in Clinical Medical Sciences. J Healthc Inform Res. 2022;6:241-252. doi:10.1007/s41666-021-00113-8 | Clinical conformal prediction review; directly supports uncertainty methods. | Add PDF |
| 12 | Sreenivasan AP, Vaivade A, Noui Y, Emami Khoonsari P, Burman J, Spjuth O, et al. Conformal prediction enables disease course prediction and allows individualized diagnostic uncertainty in multiple sclerosis. npj Digit Med. 2025;8:224. doi:10.1038/s41746-025-01616-z | Recent clinical EHR conformal prediction example with individualized uncertainty. | Add PDF |
| 13 | Vasey B, Nagendran M, Campbell B, Clifton DA, Collins GS, Denaxas S, et al. Reporting guideline for the early stage clinical evaluation of decision support systems driven by artificial intelligence: DECIDE-AI. BMJ. 2022;377:e070904. doi:10.1136/bmj-2022-070904 | Supports deployment-readiness and clinical evaluation framing. | Add PDF |
| 14 | Sounderajah V, Guni A, Liu X, Collins GS, Karthikesalingam A, Markar SR, et al. The STARD-AI reporting guideline for diagnostic accuracy studies using artificial intelligence. Nat Med. 2025;31:3283-3289. doi:10.1038/s41591-025-03953-8 | Newest AI diagnostic reporting standard. Use selectively because this paper is framed as risk prediction, not purely diagnostic accuracy. | Optional citation |
| 15 | Park Y, Jackson GP, Foreman MA, Gruen D, Hu J, Das AK. Evaluating artificial intelligence in medicine: phases of clinical research. JAMIA Open. 2020;3(3):326-331. doi:10.1093/jamiaopen/ooaa033 | Especially useful for a JAMIA Open audience; supports staged evaluation before deployment. | Add PDF |

## CKD and Kidney Risk Context Additions

These strengthen clinical relevance and show that the paper is grounded in current nephrology literature, not only ML literature.

| Priority | Citation | Why this matters | Status |
|---|---|---|---|
| 16 | Kidney Disease: Improving Global Outcomes (KDIGO) CKD Work Group. KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease. Kidney Int. 2024;105(4S):S117-S314. doi:10.1016/j.kint.2023.10.018 | Current CKD clinical guideline; supports CKD definition, risk assessment, and clinical relevance. | Add PDF |
| 17 | Levin A, Ahmed SB, Carrero JJ, Foster B, Francis A, Hall RK, et al. Executive summary of the KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease: known knowns and known unknowns. Kidney Int. 2024;105(4):684-701. doi:10.1016/j.kint.2023.10.016 | Shorter guideline citation for manuscript background if full guideline is too large. | Optional PDF |
| 18 | Francis A, Harhay MN, Ong ACM, Tummalapalli SL, Ortiz A, Fogo AB, et al. Chronic kidney disease and the global public health agenda: an international consensus. Nat Rev Nephrol. 2024;20:473-485. doi:10.1038/s41581-024-00820-6 | Recent high-impact burden/significance citation for the Introduction. | Add PDF if accessible |

## Recent CKD/KFRE External Validation and Calibration Additions

These are the most important clinical comparator papers because they focus on external validity, recalibration, and clinical utility.

| Priority | Citation | Why this matters | Status |
|---|---|---|---|
| 19 | Pan L, Wang J, Deng Y, Sun Y, Nie Z, Sun X, et al. External Validation of the Kidney Failure Risk Equation Among Urban Community-Based Chinese Patients With CKD. Kidney Med. 2024;6(5):100817. doi:10.1016/j.xkme.2024.100817 | Recent external validation with calibration and decision curve analysis in an Asian CKD cohort. | Add PDF |
| 20 | Larrarte C, Vesga J, Ardila F, Aldana A, Perea D, Sanabria M. Validation of the Kidney Failure Risk Equation in the Colombian Population. Int J Nephrol. 2024;2024:1282664. doi:10.1155/2024/1282664 | Recent Latin American KFRE validation; useful for geographic transportability discussion. | Add PDF |
| 21 | Bravo-Zuniga JI, Soto-Becerra P, Coila-Paricahua EJ, Chavez-Gomez R, Perez-Tejada E, Pardo-Villafranca AV, et al. External validation, recalibration, and clinical utility of the kidney failure risk equation in patients with advanced CKD: a nationwide retrospective cohort analysis in Peru. BMC Nephrol. 2025;26:688. doi:10.1186/s12882-025-04357-z | Very recent and highly aligned: external validation, recalibration, calibration slope/intercept, and decision curve analysis. | Add PDF |
| 22 | Li J, Du X, Zhang R, Li X, Xu J, Song X, et al. Machine learning models for predicting short-term progression in patients with stage 4 chronic kidney disease: a multi-center validation study. Sci Rep. 2025;15:39285. doi:10.1038/s41598-025-23037-4 | Recent ML CKD progression model with validation; useful comparator for current ML literature. | Add PDF |
| 23 | Tran DNT, Ducher M, Fouque D, Fauvel JP. External validation of a 2-year all-cause mortality prediction tool developed using machine learning in patients with stage 4-5 chronic kidney disease. J Nephrol. 2024;37(8):2267-2274. doi:10.1007/s40620-024-02011-9 | Recent external validation of an ML tool in advanced CKD; supports deployment caution. | Add PDF if accessible |
| 24 | Nelson RG, et al. Development and External Validation of a Machine Learning Model for Progression of CKD. Kidney Int Rep. 2022. | Large CKD progression ML study with external validation and calibration plots. Complete citation should be verified before final manuscript use. | Verify citation; add PDF |

## Recent CKD AI Review Additions

Use one or two of these, not all, to avoid overloading the Introduction.

| Priority | Citation | Why this matters | Status |
|---|---|---|---|
| 25 | Sabanayagam C, Banu R, Lim C, Tham YC, Cheng CY, Tan G, et al. Artificial intelligence in chronic kidney disease management: a scoping review. Theranostics. 2025;15(10):4566-4578. doi:10.7150/thno.108552 | Broad, recent CKD AI management review with nephrology relevance. | Add PDF |
| 26 | Pan Q, Tong M. Artificial intelligence in predicting chronic kidney disease prognosis. A systematic review and meta-analysis. Ren Fail. 2024;46(2):2435483. doi:10.1080/0886022X.2024.2435483 | Recent systematic review/meta-analysis for AI prognosis in CKD. | Add PDF |
| 27 | Chen L, Shao X, Yu P. Machine learning prediction models for diabetic kidney disease: systematic review and meta-analysis. Endocrine. 2024;84(3):890-902. doi:10.1007/s12020-023-03637-8 | Useful if diabetic kidney disease is discussed as a related high-risk subgroup. | Optional |
| 28 | Gogoi P, Valan JA. Machine learning approaches for predicting and diagnosing chronic kidney disease: current trends, challenges, solutions, and future directions. Int Urol Nephrol. 2025;57(4):1245-1268. doi:10.1007/s11255-024-04281-5 | Recent review of CKD ML trends and limitations. Use if manuscript needs more ML-background support. | Optional |

## Recommended Final Reference Mix

Aim for about 35-40 total references:

- 5-7 CKD burden/guideline/risk-model context references
- 6-8 CKD prediction/KFRE validation references
- 6-8 calibration and prediction-model evaluation references
- 4-6 uncertainty/conformal prediction references
- 4-6 clinical AI deployment/reporting/fairness references
- 2-3 dataset/software references

## Do Not Over-Cite

Avoid adding many recent UCI-only CKD classifier papers unless they contribute something beyond high accuracy on the small UCI dataset. JAMIA reviewers are more likely to value external validation, calibration, uncertainty, clinical utility, reporting quality, and deployment monitoring than another single-dataset classifier comparison.

## Acquisition Notes

- Prefer publisher PDFs or PubMed Central PDFs when open access.
- If a paper is paywalled, keep a DOI-only citation and obtain it through the University of the Cumberlands library portal.
- Do not upload or redistribute paywalled PDFs unless institutional access permits local research use.
- Keep the final manuscript references in citation order, not alphabetical order, per JAMIA/JAMIA Open style.

