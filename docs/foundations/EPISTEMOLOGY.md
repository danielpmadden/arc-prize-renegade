# Repository Epistemology

> **Document role: epistemic governance.** This document defines how to state
> repository status and evaluate claims; it does not define architectural
> requirements or claim implementation.

Use these terms precisely:

- **Official:** the merged repository state and accepted governing documents.
- **Experimental:** branch work that has not been merged.
- **Specification:** requirements or architectural definitions that may extend
  beyond the current implementation.
- **Historical:** preserved records of what happened or was verified at a
  particular stage.
- **Speculative:** possible future work that has not been implemented or
  accepted.
- **Evidence:** material supporting a claim. Evidence does not automatically
  establish truth, validation, promotion, correctness, or official status.

## Working rules

- Prompts and conversation memory are not repository evidence.
- Branch implementation is not official merely because it works or passes
  tests.
- Specifications must not masquerade as implemented behavior.
- Historical records must not be silently rewritten; add a correction or
  addendum when needed.
- Current repository state and historical repository state are different.
- When required evidence is unavailable, report uncertainty instead of
  inventing an answer.
- A fresh contributor's reasonable confusion is a documentation problem worth
  examining.

For current implementation, inspect tracked source and tests. For historical
claims, consult `docs/roadmap/MILESTONES.md`. For intended architecture, consult the
specifications. When these sources disagree, record the discrepancy rather
than silently resolving it by assumption.
