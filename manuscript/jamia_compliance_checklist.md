# JAMIA Open Submission Compliance Checklist
Last verified: 2026-04-26

## Manuscript format

| Item | Requirement | Status | Notes |
|------|-------------|--------|-------|
| Article type | Original Research | PASS | Manuscript labeled as such |
| Word limit | 5,000 words (body) | PASS | ~4,200 words abstract through conclusion |
| Abstract word limit | 250-300 words | PASS | 250 words |
| Abstract structure | Background / Objective / Methods / Results / Conclusion | PASS | All five sections present |
| Keywords | 3-6 terms | PASS | 6 keywords listed |
| Line spacing | Double-spaced | ACTION | Apply when formatting final Word/PDF |
| Font | Times New Roman or Arial 12pt | ACTION | Apply when formatting final Word/PDF |
| Page numbers | Required | ACTION | Apply when formatting final Word/PDF |

## References

| Item | Requirement | Status | Notes |
|------|-------------|--------|-------|
| Citation style | Vancouver (numbered) | PASS | refs.bib with 30 entries; all cited |
| Citation order | Consecutive by appearance | PASS | Ordered 1-30 in manuscript |
| DOIs | Required where available | PASS | All journal/preprint entries include DOI; 3 older conference proceedings (Guo 2017, Niculescu-Mizil 2005, Platt 1999, Zadrozny 2002) predate standard DOI assignment |
| URL references | Allowed with access date | PASS | Access date 2025-12-01 added to UCIDataset entry; entry changed to @article type to resolve BibTeX warnings |

## Figures

| Item | Requirement | Status | Notes |
|------|-------------|--------|-------|
| Resolution | 300 DPI minimum | PASS | All 18 figures regenerated at 300 DPI |
| Format | TIFF or EPS preferred; PNG acceptable | PASS | PNG at 300 DPI |
| Number of figures | 4 primary manuscript figures | PASS | F1-F4 |
| Captions | Standalone (readable without paper) | PASS | figure_captions.md covers F1-F4 |
| Color figures | Allowed; consider grayscale accessibility | NOTE | Color used; all figures use colorblind-safe palettes |

## Tables

| Item | Requirement | Status | Notes |
|------|-------------|--------|-------|
| Number of tables | 4 manuscript tables | PASS | T1-T4 |
| Table titles | Above table, descriptive | ACTION | Add titles when building Word doc |
| Footnotes | Below table for abbreviations | ACTION | Add abbreviation footnotes |

## Ethics and data

| Item | Requirement | Status | Notes |
|------|-------------|--------|-------|
| Ethics statement | Required; exemption acceptable | PASS | Both datasets publicly available, de-identified |
| IRB waiver | Needed for human data | PASS | MIMIC-IV Clinical Database Demo v2.2 is open-access, no credentialing required; stated explicitly in methods as distributional stress-test, not formal external validation |
| Data availability | Must state where data can be obtained | PASS | Stated in cover letter (stress-test framing), methods, and limitations |
| MIMIC PhysioNet terms | Cite Johnson et al. 2023 | PASS | Reference 17 in bibliography |

## Supplementary materials

| Item | Requirement | Status | Notes |
|------|-------------|--------|-------|
| S1 Hyperparameter grids | Full search spaces | PASS | supplementary/S1_hyperparameter_grids.md |
| S2 Reliability diagrams | All UCI + MIMIC figures | PASS | supplementary/S2_reliability_diagrams.md |
| S3 Subgroup calibration | Full subgroup ECE table | PASS | supplementary/S3_subgroup_calibration.md |
| S4 Reproducibility | Install + run instructions | PASS | supplementary/S4_reproducibility.md |

## Author information

| Item | Requirement | Status | Notes |
|------|-------------|--------|-------|
| CRediT taxonomy | Required | PASS | In cover letter |
| Conflict of interest | Required | PASS | None declared |
| Funding statement | Required | PASS | No external funding |
| Corresponding author | Email required | PASS | michael.eniolade@theosyntra.com |

## Open access

| Item | Requirement | Status | Notes |
|------|-------------|--------|-------|
| License | CC BY 4.0 (JAMIA Open default) | PASS | Accepted |
| Code availability | Encouraged | PASS | Full pipeline in code/ with README |

## Pre-submission actions remaining

1. Format manuscript body as Word document (.docx) with double spacing, 12pt font, page numbers.
2. Add table titles and abbreviation footnotes to T1-T4.
3. Convert figure_captions.md into embedded captions in the Word document.
4. Confirm author affiliation text matches institutional format required by JAMIA Open.

## Completed

- BibTeX warnings resolved: UCIDataset entry converted to @article type, access date added, `natbib[numbers,sort&compress]` option added to match Vancouver numbered style.
- MIMIC-IV stress-test reframing applied across all sections (methods, results, discussion, conclusion, abstract, cover letter). Credentialing language removed.
