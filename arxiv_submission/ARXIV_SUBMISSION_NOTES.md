# arXiv Submission Notes
**Paper:** Calibration, Uncertainty Communication, and Deployment Readiness in CKD Risk Prediction: A Framework Evaluation Study  
**Author:** Michael Eniolade — University of the Cumberlands  
**Prepared:** 2026-05-20  
**Target category:** cs.LG (Machine Learning) with cross-list to stat.ML and q-bio.QM

---

## What Is in This Package

```
arxiv_submission/
├── main.tex                  ← Master LaTeX file (figure path updated for arXiv)
├── main.bbl                  ← Pre-compiled bibliography (arXiv uses this directly)
├── refs.bib                  ← BibTeX source (included for completeness)
├── supplementary.tex         ← Supplementary materials as standalone LaTeX
├── sections/
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── methods.tex
│   ├── results.tex
│   ├── discussion.tex
│   └── conclusion.tex
├── figures/                  ← All 13 figures used in the manuscript (300 DPI PNG)
│   ├── reliability_compare_LR.png
│   ├── reliability_compare_RF.png
│   ├── reliability_compare_XGB.png
│   ├── reliability_compare_SVM.png
│   ├── reliability_compare_NB.png
│   ├── reliability_mimic_LR.png
│   ├── reliability_mimic_RF.png
│   ├── reliability_mimic_XGB.png
│   ├── reliability_mimic_SVM.png
│   ├── reliability_mimic_NB.png
│   ├── conformal_setsize_uci.png
│   ├── conformal_sample_uci.png
│   └── F4_deployment_heatmap.png
├── ARXIV_SUBMISSION_NOTES.md ← This file (do NOT upload to arXiv)
└── arxiv_submission.zip      ← Ready-to-upload archive
```

---

## What Changed vs. the JAMIA Submission

The only modification made to the LaTeX source is the figure path in `main.tex`:

| File | Original | arXiv version |
|------|----------|---------------|
| `main.tex` line 22 | `\graphicspath{{../figures/}}` | `\graphicspath{{figures/}}` |

All section `.tex` files, `refs.bib`, and figure files are identical to the JAMIA submission source.

---

## How to Submit to arXiv

### Step 1 — Create an arXiv account
Go to https://arxiv.org and create an account if you don't have one.  
You will need an institutional email or an endorser in your field (cs.LG).

### Step 2 — Start a new submission
- Go to https://arxiv.org/submit
- Click **"Start new submission"**
- Select primary category: **cs.LG** (Computer Science — Machine Learning)

### Step 3 — Recommended cross-list categories
Add these as cross-lists when prompted:
- `stat.ML` — Statistics: Machine Learning
- `q-bio.QM` — Quantitative Methods (appropriate for clinical informatics)

### Step 4 — Upload the source files

Upload **`arxiv_submission.zip`** directly. arXiv will unpack it automatically.

> **Critical:** Do NOT upload `ARXIV_SUBMISSION_NOTES.md` or any other non-source file.
> The zip already excludes it — the zip only contains the files arXiv needs.

arXiv expects:
- The main `.tex` file at the root of the archive — ✅ (`main.tex`)
- A pre-compiled `.bbl` file with the same base name — ✅ (`main.bbl`)
- All figures accessible relative to `main.tex` — ✅ (`figures/`)
- Bibliography style file OR pre-compiled `.bbl` — ✅ (`.bbl` provided; `vancouver.bst` is in TeX Live)

### Step 5 — Supplementary materials

arXiv handles supplementary in two ways:

**Option A (Recommended): Upload `supplementary.tex` as an ancillary file**
- During upload, arXiv will ask if you have "ancillary files"
- Upload `supplementary.tex` as an ancillary file
- arXiv will compile it separately and link it alongside the main paper

**Option B: Merge into main paper as an appendix**
- Add `\appendix` after the conclusion, then `\input{supplementary_appendix}` 
- Requires reformatting `supplementary.tex` slightly — contact if you want this done

### Step 6 — Fill in the submission metadata

**Title:**
```
Calibration, Uncertainty Communication, and Deployment Readiness in CKD Risk Prediction: A Framework Evaluation Study
```

**Authors:**
```
Michael Eniolade
```

**Abstract:** Copy from the manuscript (250 words, structured):
```
Background: Machine learning models for chronic kidney disease risk prediction regularly 
achieve strong discrimination on internal test sets. Calibration assessment and uncertainty 
quantification are far less common, leaving clinicians without reliable information about 
whether probability outputs are trustworthy. No published study has jointly evaluated all 
three dimensions (calibration, uncertainty, and structured deployment readiness) on a common 
model suite with external clinical validation.

Objective: To evaluate five classifiers across calibration quality, conformal prediction 
coverage, and an eight-criterion deployment readiness framework on both internal and 
external data.

Methods: Five classifiers (logistic regression, random forest, XGBoost, support vector 
machine with Platt scaling, Gaussian naive Bayes) were trained on the UCI CKD dataset 
(400 patients, 62.5% CKD). A distributional stress-test used the open-access MIMIC-IV demo 
cohort (97 patients, 23.7% CKD) to evaluate model behaviour under prevalence shift and 
feature missingness. Calibration was assessed before and after Platt scaling and isotonic 
regression, quantified by Expected Calibration Error and Brier Score. Predictive uncertainty 
was measured through split conformal prediction targeting 90% marginal coverage. An 
eight-criterion deployment readiness framework evaluated discrimination, calibration 
stability, coverage transfer, subgroup equity, and reproducibility.

Results: All five models achieved AUROC 1.00 on the UCI test set. Post-isotonic ECE fell 
to 0.000-0.022 internally. On MIMIC-IV, AUROC dropped to 0.48-0.58, ECE rose to 0.68-0.76, 
and conformal coverage collapsed from 0.80-0.98 (UCI) to 0.21-0.25, well below the 90% 
target. No model passed the deployment checklist; scores ranged from 2 to 4 out of 16.

Conclusion: Near-perfect internal performance did not survive distributional shift. 
Calibration stability and conformal coverage transfer should be evaluated before any 
clinical ML model moves toward deployment, even when internal metrics appear strong.
```

**Comments field (optional):**
```
27 pages, 6 figures, 4 tables. Supplementary materials (S1-S4) included.
Submitted to JAMIA Open.
```

**Keywords / MSC codes:** Leave blank (arXiv uses category codes, not keywords for cs.LG)

### Step 7 — License

Select: **CC BY 4.0** (Creative Commons Attribution 4.0 International)  
This matches the JAMIA Open open-access license.

### Step 8 — Review and submit

arXiv will show you a preview of the compiled PDF. Check:
- [ ] Title and author display correctly on page 1
- [ ] Email appears on title page
- [ ] All 6 figures render (F1a, F1b, F2, F3a, F3b, F4)
- [ ] Tables T1–T4 are present
- [ ] References are numbered 1–30
- [ ] No "figure not found" errors in the log

If there are compilation errors, download the arXiv log from the preview page
and compare to the known-good build.

---

## Why a Pre-compiled .bbl Is Included

arXiv does not always run BibTeX automatically when compiling submissions.
Including `main.bbl` (the pre-compiled bibliography list generated from
`refs.bib` + `vancouver.bst`) ensures the reference list appears correctly
regardless of arXiv's BibTeX configuration.

The `.bbl` file was generated from the current `refs.bib` and is in sync
with the 30 citations in the manuscript. Do not edit it manually.

---

## Checklist Before Uploading

- [ ] `main.tex` has `\graphicspath{{figures/}}` (not `../figures/`)
- [ ] All 13 figures are present in `figures/`
- [ ] `main.bbl` is present and matches the current refs.bib
- [ ] `arxiv_submission.zip` contains only source files (no NOTES.md)
- [ ] arXiv submission metadata matches the manuscript title/abstract exactly
- [ ] License set to CC BY 4.0
- [ ] Cross-lists added: stat.ML, q-bio.QM

---

## After arXiv Submission

1. You will receive an arXiv ID (e.g., `arXiv:2026.XXXXX`)
2. The paper becomes publicly accessible after the next arXiv processing cycle (usually 1 business day)
3. Include the arXiv URL in the JAMIA Open cover letter update if submitting both simultaneously
4. Add the arXiv DOI link to your ORCID profile

---

## Notes on JAMIA Open vs. arXiv Simultaneous Submission

JAMIA Open allows preprint posting on arXiv (confirmed in their author guidelines).
Post on arXiv first if you want a public timestamp before the JAMIA review completes.
If JAMIA accepts and requests changes, update the arXiv version with the revised manuscript.
