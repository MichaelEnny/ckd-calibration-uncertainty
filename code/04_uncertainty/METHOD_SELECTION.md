# Task 5.1 — Conformal Prediction Method Selection

## Method chosen: Split Conformal Prediction (Inductive CP)

**Library:** MAPIE 1.3.0 (`SplitConformalClassifier`)

**Rationale for split CP over cross-conformal:**
- Single fit of the base model; calibration layer uses the held-out validation
  set only — no additional model refitting required.
- Computationally cheap: O(n_cal log n_cal) for threshold estimation.
- Provides a finite-sample, distribution-free marginal coverage guarantee:
  P(Y ∈ C(X)) ≥ 1 − α for any α ∈ (0,1), regardless of the true data
  distribution (Venn-Abers / conformal guarantee per Angelopoulos & Bates 2022).

**Conformity score:** `lac` (Least Ambiguous set-valued Classifier)
- Computes 1 − p̂(y|x) as the non-conformity score.
- Equivalent to the standard "softmax score" method; interpretable and
  well-studied for binary classification.

**Calibration set:** UCI validation fold (60 samples, indices from uci_splits.json)
- Kept separate from training fold to avoid data leakage.
- Same validation set used for post-hoc calibration (Tasks 4.2) — acceptable
  because conformal calibration is non-parametric and does not affect model weights.

**Target coverage level:** 1 − α = 0.90  (α = 0.10)
- 90% marginal coverage: over repeated samples, ≥ 90% of prediction sets
  will contain the true label.
- Chosen to match common clinical decision-support thresholds where a 1-in-10
  miss rate is the accepted operating point.

**Prediction set semantics for binary CKD task:**
| Set returned | Interpretation |
|---|---|
| {1} | Unambiguously CKD — singleton, high confidence |
| {0} | Unambiguously not-CKD — singleton, high confidence |
| {0, 1} | Ambiguous — model uncertain, clinician should seek more information |
| {} | Empty set (rare; indicates score threshold exceeded) |

**Key metrics to report (Task 5.2):**
- Empirical coverage rate (should be ≥ 0.90)
- Average prediction set size (lower = more informative)
- Singleton rate = fraction of test samples with a size-1 prediction set
