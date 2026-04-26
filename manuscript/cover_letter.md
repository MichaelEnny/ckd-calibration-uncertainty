---
To: JAMIA Open Editorial Office
From: Michael Eniolade
Date: April 26, 2026
Re: Original Research Submission
---

# Cover Letter

Dear Editor,

I am submitting the manuscript titled **"Calibration, Uncertainty Communication, and Deployment Readiness in CKD Risk Prediction: A Framework Evaluation Study"** for consideration as an Original Research article in *JAMIA Open*.

## Why this paper fits JAMIA Open's scope

JAMIA Open publishes applied informatics research that advances the use of health data and clinical decision support. This paper addresses a documented gap at the intersection of clinical machine learning and deployment practice: models for chronic kidney disease (CKD) risk stratification consistently report strong internal discrimination but rarely undergo calibration assessment, uncertainty quantification, or structured readiness evaluation before deployment consideration. We benchmark five widely used classifiers against all three dimensions simultaneously, with external validation on MIMIC-IV hospital data, and introduce a reusable eight-criterion deployment checklist. The study is methodologically grounded, the datasets are publicly accessible, and the framework is directly applicable to any clinical prediction problem.

## Summary of novel contributions

1. First joint evaluation of calibration quality, conformal prediction coverage, and structured deployment readiness for CKD classifiers on an external clinical cohort.
2. Quantitative demonstration that post-hoc calibration methods (Platt scaling, isotonic regression) that eliminate internal calibration error do not prevent severe calibration drift on external data (ECE drift 0.67-0.75).
3. Empirical evidence that split conformal prediction coverage guarantees do not transfer under distributional shift: UCI coverage 0.80-0.98 collapsed to 0.21-0.25 on MIMIC-IV.
4. An eight-criterion deployment readiness checklist with explicit thresholds and a reproducible scoring protocol; no model in this study scored above 4 of 16.

## Data availability and ethics

The UCI CKD dataset (Soundarapandian and Srinivasan, 2015) is publicly available from the UCI Machine Learning Repository under a Creative Commons license and requires no ethics approval. MIMIC-IV Clinical Database Demo v2.2 is a de-identified, publicly available subset of MIMIC-IV released by PhysioNet under a Creative Commons Attribution 4.0 International license. Both datasets are entirely de-identified; no IRB approval is required for their use.

## Compliance statements

- **Word count:** approximately 4,200 words (abstract through conclusion, excluding references and captions) — within JAMIA Open's 5,000-word limit for Original Research.
- **Structured abstract:** 250 words; Background / Objective / Methods / Results / Conclusion format.
- **References:** Vancouver numbered style, 21 citations.
- **Figures:** 4 primary figures, 300 DPI PNG, all generated programmatically and fully reproducible.
- **Tables:** 4 manuscript tables embedded in results; complete results in supplementary materials.
- **Author contributions:** CRediT taxonomy statement provided below.
- **Conflicts of interest:** None to declare.
- **Funding:** No external funding.

## CRediT Author Contribution Statement

**Michael Eniolade:** Conceptualization, Methodology, Software, Formal analysis, Data curation, Writing — original draft, Writing — review and editing, Visualization, Project administration.

## Confirmation

This manuscript has not been published previously, is not under consideration elsewhere, and all authors (sole author) have approved this submission.

Sincerely,

Michael Eniolade
University of the Cumberlands
michael.eniolade@theosyntra.com
