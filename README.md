# Renegade

Renegade is a deterministic, inspectable symbolic-architecture research
project.  This checkout provides a stable structural pipeline for recording a
supplied grid and deriving exact, provenance-preserving structural records from
it. It is **not an ARC solver**.

## Vision

Renegade explores a symbolic architecture in which each layer is explicit,
bounded, and inspectable. The current implementation records structural facts;
it does not assign semantic meaning or choose solutions. ARC is a useful
proving ground, not the project's target or an implemented capability.

## Philosophy

- **Determinism:** identical supplied inputs produce identical records and
  event order.
- **Interpretability:** records, provenance, and execution traces are exposed
  rather than hidden behind a score.
- **Identity:** architecture values use stable identities; identity is not
  inferred from a display name.
- **Provenance:** derived records retain their source frame and supporting
  records where applicable.
- **Append-only knowledge:** execution memory and historical milestones retain
  their past records; corrections are addenda rather than rewritten history.
- **Layered cognition:** each implemented layer has a deliberately narrow
  structural role. Future semantic layers must not be implied by today's
  geometry.

## Current Cognitive Pipeline

```
Reality (supplied grid)
        ↓
Observation
        ↓
Measurement
        ↓
Percept
        ↓
Relationship
        ↓
Invariant
        ↓
Archetype

Future: Concept Association → Interpretation → Hypothesis → Reasoning
        → Reflection → Learning
```

The implemented layers are structural only. An archetype is an exact motif
derived from invariants, not an object label, interpretation, or prediction.

## Repository Structure

- `src/renegade/` — installable package and deterministic pipeline.
- `tests/` — unit, integration, corpus, and deterministic stress tests.
- `tests/golden_corpus.py` — reusable representative grid corpus.
- `docs/architecture/` — canonical implementation-oriented architecture guide.
- `docs/research/` — preserved pass journals and rationale; these are not the
  current implementation reference.
- Root governance documents — project principles, epistemic rules, capability
  contract, and append-only milestone history.

See [the documentation index](docs/README.md) for a map and document roles.

## Quick Start

Requires Python 3.11 or newer.

```bash
python -m pip install --editable .
python -m renegade
python -m renegade.playground
python -m renegade.playground --grid '[[1,0,1],[0,0,0],[1,0,1]]'
python -m unittest discover -s tests -v
```

The playground accepts `--grid`, `--file`, or `--stdin` and renders a
deterministic inspection report. For a concise programmatic report, use
`renegade.diagnostics.summarize_pipeline`.

## Current Capabilities

- Immutable observations and ordered observation frames.
- Exact dimensions, bounds, and observation-count measurements.
- A whole-frame percept plus four-directionally connected, same-value region
  percepts.
- Bounded pairwise geometric relationships and a read-only percept graph.
- Structural invariants that group exact relationship regularities.
- Exact structural archetypes: single cells, lines, rectangles, squares,
  linear/translation arrays, and checkerboards when supported by invariant
  metadata.
- Explicit workspace registries and ordered execution events throughout the
  grid pipeline.
- A command-line playground and lightweight deterministic diagnostics summary.

## Current Limitations

The repository intentionally does **not** implement concept association,
semantic interpretation, hypotheses, reasoning, reflection, learning, search,
ARC task loading, ARC evaluation, ARC solving, neural methods, or machine
learning. Relationships and archetypes make no semantic inference.

## Roadmap

Future work is governed by the architecture and capability documents. It may
add carefully validated layers above structural archetypes, but this checkout
does not claim those layers exist. Consult `MILESTONES.md` for verified history
and current-tree audit corrections, not for a forward plan.

## Contributing

Read `AGENTS.md` and the governing documents named there before changing code.
Keep changes deterministic, bounded, provenance-aware, and covered by relevant
tests. Distinguish current implementation from specification, history, and
speculation in both code and documentation.

## License

See [LICENSE](LICENSE). Notices, privacy, and security information are in
`NOTICE.md`, `PRIVACY.md`, and `SECURITY.md`.
