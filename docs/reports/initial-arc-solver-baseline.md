# Initial ARC Solver Baseline

> **Status:** experimental implementation evidence. This report is not a claim
> of official capability or a general ARC score.

## Implemented

The bounded solver supports identity, recolor, rotation, reflection, crop,
translation, enclosed fill, outline, and depth-two composition. Training input
and output regions are matched only by explicit normalized-shape/cell-count
evidence; unmatched and ambiguous regions are retained in change summaries.
Exact validation requires full grid equality for every training pair.

## Verified synthetic coverage

Unit coverage exercises recolor, rotation, crop, fill, translation, rejection
of inconsistent pairs, deterministic operation execution, CLI JSON, and local
benchmark evaluation. The benchmark counts training hypotheses separately from
post-prediction exact test equality.

## Unsupported and next work

Copy, deletion predicates, tiling, scale, richer object selectors, and general
multi-step object programs are unsupported. The next highest-value capability
is deterministic object selection plus copy/delete actions, while retaining
exact cross-training validation and ambiguity reporting.

## Synthetic generator addendum

The local program-first generator is verified by replay and deterministic-seed
tests. It creates new solver-language tasks and is not an ARC dataset or a
claim of performance on ARC. Its immediate regression role is to expose solver
failures by operation family and composition depth.
