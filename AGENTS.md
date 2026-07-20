# Renegade Contributor Guidance

> **Document role: contributor guidance.** This file operationalizes the
> governing documents. It is not an implementation specification, historical
> evidence, or a claim that a described capability exists.

Before changing the repository, read `README.md`, `EPISTEMOLOGY.md`,
`CONSTITUTION.md`, `CAPABILITY_CONTRACT.md`, `CONCEPTS.md`, `LIFECYCLE.md`,
`LINEAGE.md`, `EMERGENCE.md`, and `MILESTONES.md`.

- Distinguish current implementation, specification, verified history,
  experimental branch work, and speculation. Do not treat prompt assertions or
  conversation memory as repository facts.
- Verify claims against the files, code, and tests available in the task. When
  required evidence is unavailable, report the uncertainty explicitly.
- Do not call branch work official merely because it works or passes tests;
  official status requires the merged repository state and accepted governing
  documents.
- Specifications define requirements; they must not masquerade as implemented
  behavior. Preserve verified behavior and its tests when changing code.
- Preserve historical records. Add explicit corrections or addenda rather than
  rewriting history to hide a contradiction.
- Preserve determinism: do not add hidden randomness, wall-clock-dependent
  behavior, or unbounded search.
- Keep observations and evidence separate from conclusions, validation, and
  promotion. Preserve provenance, relationships, and lineage where meaningful.
- Make uncertainty, assumptions, and failures explicit and inspectable; never
  silently fail. Do not add benchmark-specific shortcuts or encode benchmark
  answers as reasoning.
- Prefer small, verified changes over speculative architecture; run relevant
  tests before reporting success. Do not claim learning, emergence, transfer,
  or intelligence unless executable behavior demonstrates it.
