# Supplementary Material S3: Subgroup Calibration on MIMIC-IV External Cohort

Subgroup-level ECE was computed on the MIMIC-IV external cohort (n = 97) for three stratification variables: age group, diabetes mellitus (DM) status, and hypertension (HTN) status. ECE used 5 equal-width bins (rather than the primary analysis 10 bins) to ensure stable estimates in small subgroups. Groups with fewer than 10 patients were excluded and are marked with "—".

Best-calibrated model variant used per classifier (same as primary analysis): isotonic regression for LR, RF, XGB, SVM; base model for NB.

---

## Subgroup ECE Values

| Model | Age < 65 (n = 39) | Age >= 65 (n = 58) | DM = Yes | DM = No (n = 97) | HTN = Yes | HTN = No (n = 97) | Overall (n = 97) |
|-------|-------------------|---------------------|----------|-------------------|-----------|-------------------|------------------|
| LR | 0.8516 | 0.6429 | — | 0.7871 | — | 0.7481 | 0.7612 |
| RF | 0.8364 | 0.6429 | — | 0.7778 | — | 0.7386 | 0.7526 |
| XGB | 0.7536 | 0.6053 | — | 0.6997 | — | 0.6587 | 0.6801 |
| SVM | 0.8442 | 0.6391 | — | 0.7808 | — | 0.7417 | 0.7554 |
| NB | 0.8182 | 0.6667 | — | 0.7778 | — | 0.7386 | 0.7526 |

**Note:** The DM = Yes and HTN = Yes subgroups each fell below the 10-patient minimum threshold after MIMIC cohort construction and are excluded from ECE computation.

---

## Subgroup ECE Gap (criterion 7)

The subgroup equity criterion in the deployment checklist scores max ECE gap <= 0.05 as PASS. The gap is computed as max(subgroup ECE) - min(subgroup ECE) across all valid subgroups for a given model.

| Model | Max ECE | Min ECE | Gap | Criterion 7 |
|-------|---------|---------|-----|-------------|
| LR | 0.8516 | 0.6429 | 0.2087 | FAIL |
| RF | 0.8364 | 0.6429 | 0.1935 | FAIL |
| XGB | 0.7536 | 0.6053 | 0.1483 | FAIL |
| SVM | 0.8442 | 0.6391 | 0.2051 | FAIL |
| NB | 0.8182 | 0.6053 | 0.2129 | FAIL |

All models fail the subgroup equity criterion. Younger patients (age < 65) show systematically worse calibration than older patients across all five models, with ECE gaps of 0.15-0.21. This pattern is consistent with the overall calibration collapse: models consistently overestimate CKD probability for all patients, and this overestimation is more pronounced in younger patients who have lower true CKD prevalence in the MIMIC cohort.

---

## Interpretation

The subgroup ECE differences are secondary to the primary calibration failure. Even the best-performing subgroup (age >= 65, ECE ~0.64) remains far above the acceptable threshold of ECE <= 0.10. Subgroup equity analysis in this context confirms that the calibration problem is systematic and not limited to a specific demographic subgroup.
