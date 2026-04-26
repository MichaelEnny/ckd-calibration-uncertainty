## Figure Captions

**Figure 1. Reliability diagrams for all five classifiers before and after post-hoc calibration on the UCI test set.**
Each panel shows three curves: the uncalibrated model (grey), Platt scaling (pink), and isotonic regression (teal). The diagonal represents perfect calibration. Annotation boxes display ECE, MCE, Brier Score, and Brier Skill Score for each variant. LR shows the largest pre-calibration deviation; isotonic regression achieves the greatest improvement across the suite. Note that Platt scaling worsened SVM calibration on this dataset, a result discussed in section 4.2.

**Figure 2. Reliability diagrams for the best-calibrated variant of each classifier applied to the MIMIC-IV external cohort.**
The best variant for each model was selected by lowest ECE on the UCI test set (isotonic for LR, RF, XGB, SVM; base for NB). All curves fall below the diagonal, consistent with models assigning probabilities calibrated to a 62.5% CKD prevalence population (UCI training) but applied to a 23.7% prevalence cohort (MIMIC). ECE ranged from 0.680 (XGB) to 0.761 (LR).

**Figure 3. Conformal prediction set size distributions and individual-level uncertainty display.**
Left panel: bar charts showing prediction set size (0=empty, 1=singleton, 2=ambiguous) for each model on the UCI test set. NB and NB-adjacent models produce the fewest ambiguous predictions. Right panel: horizontal bar chart for the top 50 test cases from the NB model sorted by descending predicted probability. Bar colour reflects the prediction set label (red=CKD, blue=Not-CKD, yellow=Ambiguous). True labels are indicated by star markers (CKD) and circle markers (not-CKD). Coverage target is 0.90.

**Figure 4. Deployment readiness heatmap for all five classifiers.**
Rows represent models; columns represent the eight deployment readiness criteria. Cell colour indicates score: green=PASS, orange=MARGINAL, red=FAIL. Numbers on the right show total score out of 16. All models score 2-4 out of 16. The only passing criteria across the suite are prediction interpretability (singleton rate above 0.70 on UCI for LR, RF, SVM, NB) and transparency (code publicly available). All external validation criteria fail for every model.
