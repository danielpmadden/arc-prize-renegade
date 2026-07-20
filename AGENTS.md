# Renegade Contributor Guidance

> **Document role: contributor guidance.** This file governs contributor
> workflow and change constraints. It is neither a specification nor evidence
> that a described architectural capability is implemented or verified.

Before changing code, read `README.md`, `CONSTITUTION.md`, `CAPABILITY_CONTRACT.md`, `LIFECYCLE.md`, `LINEAGE.md`, and `EMERGENCE.md`. They govern design decisions; this file only operationalizes them.

- Preserve determinism: do not add hidden randomness, wall-clock-dependent behavior, or unbounded search.
- Keep observations and evidence separate from conclusions, validation, and promotion.
- Preserve provenance, relationships, and lineage for meaningful capabilities, decisions, and memory records.
- Make uncertainty, assumptions, and failures explicit and inspectable; never silently fail.
- Do not add benchmark-specific shortcuts or encode benchmark answers as reasoning.
- Prefer small, verified changes over speculative architecture; add only the structure required by demonstrated behavior.
- Run the relevant tests before reporting success.
- Never claim learning, emergence, transfer, or intelligence unless executable behavior demonstrates it.

Consult the governing documents above for the full contracts, lifecycle expectations, and philosophical rationale.
