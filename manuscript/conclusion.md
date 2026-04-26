## 5. Conclusion

Five classifiers achieved perfect discrimination on the UCI CKD benchmark, then failed every external validation criterion when applied to MIMIC-IV hospital data. Isotonic recalibration reduced internal ECE to near zero but did not prevent calibration drift exceeding 0.67 on the external cohort. Conformal coverage fell from 0.967 or higher internally to 0.21-0.25 on MIMIC. No model scored above 4 out of 16 on the deployment readiness checklist.

A complete evaluation requires, at minimum, calibration on external data from a different clinical setting, coverage-guaranteed uncertainty estimates, and an explicit check that both transfer across the distributional shift. Discrimination on a held-out internal test set is not sufficient evidence. The 8-criterion framework introduced here offers one structured approach to operationalizing those requirements before a model reaches clinical use.
