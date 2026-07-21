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

## ARC Task Representation

The checkout can parse canonical ARC JSON and represent ordered training
input/output grids and one or more test inputs. `inspect_task` runs the
existing structural pipeline independently for every grid and retains
task-level provenance, identities, and ordered events. It does **not** compare
grids, discover transformations, reason, or solve ARC.

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
ARC evaluation, ARC solving, neural methods, or machine
learning. Relationships and archetypes make no semantic inference.

## Roadmap

Future work is governed by the architecture and capability documents. It may
add carefully validated layers above structural archetypes, but this checkout
does not claim those layers exist. Consult `docs/roadmap/MILESTONES.md` for verified history
and current-tree audit corrections, not for a forward plan.

## Contributing

Read `AGENTS.md` and the governing documents named there before changing code.
Keep changes deterministic, bounded, provenance-aware, and covered by relevant
tests. Distinguish current implementation from specification, history, and
speculation in both code and documentation.

## License

See [LICENSE](LICENSE). Notices, privacy, and security information are in
`NOTICE.md`, `docs/legal/PRIVACY.md`, and `.github/SECURITY.md`.

## Characterization

Pass 10 adds a deterministic empirical characterization suite for the current
structural layers. Run it in readable or machine-readable form:

```bash
python -m renegade.characterize
python -m renegade.characterize --json
```

The suite executes the 19-case golden corpus, targeted boundary cases, exact
normalized snapshots, and 107 exhaustive binary/ternary tiny grids. It checks
repeatability, event ordering, registry-equivalent uniqueness, provenance and
frame references, graph/result agreement, and diagnostics non-mutation. See
the [capability baseline](docs/reports/pass-10-capability-baseline.md) for
observed limits and non-promotional findings.

## Deterministic ARC Solver Vertical Slice

This checkout now includes an experimental, bounded end-to-end ARC solver. It
uses the structural inspection pipeline for task grids, derives deterministic
cross-grid region correspondences and change summaries, then validates compact
whole-grid symbolic programs exactly on every training pair. It never uses test
outputs to infer a program.

```bash
python -m renegade.solve path/to/task.json --show-rejections
python -m renegade.solve path/to/task.json --json
python -m renegade.benchmark path/to/local/tasks --json
```

Implemented program operations are identity, global recoloring, rotation,
reflection, non-background crop, bounded translation, enclosed-region fill,
and outline. Short deterministic compositions are enumerated at depth two.
A prediction is not called test-correct unless a separately available expected
test output is compared after solving.

## Program-first synthetic task generator

Generate new, reproducible symbolic tasks without downloading or embedding ARC
data. Each task is sampled from a seeded compatible world and executed by the
same solver program representation; expected outputs are private ground truth.

```bash
python -m renegade.generate --seed 42 --difficulty 2 --count 100 --output synthetic_tasks
python -m renegade.generate --seed 42 --difficulty 2 --json
```

The current generator supports difficulties 1–3 (one to three composed
whole-grid operations), at least two training pairs, and a hidden labeled test
pair. Public task JSON is canonical ARC-shaped data; generation provenance and
the symbolic program are written only to a separate `.meta.json` sidecar.
