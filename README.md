# ARC Prize Renegade

> *Build the spine before teaching the body to move.*

Renegade is an early-stage experiment in a deterministic, symbolic architecture
for general reasoning. It is **not an ARC solver**: the repository contains no
ARC tasks, ARC-specific representations, handcrafted ARC rules, or solver.

## Current repository status

This checkout implements a deliberately small execution foundation:

- named `Observation` values;
- explicitly registered `Capability` callables;
- execution of one explicitly requested capability by `Executive`;
- structured, ordered attempt traces and append-only in-memory execution
  records; and
- a small set of identity, evidence-reference, lifecycle-transition, and
  lineage-edge value primitives in `renegade.foundation`.

The runnable example registers `double_number` and executes it for the value
`4`. It demonstrates the execution substrate; it does not demonstrate
reasoning, validation, promotion, learning, or ARC solving.

The current test suite verifies the execution foundation. The foundation value
primitives are implemented but do not yet have dedicated tests in this checkout.
For the exact boundaries, read [What is not implemented](#what-is-not-implemented)
and the repository audit in [MILESTONES.md](MILESTONES.md).

## Install

Renegade requires Python 3.11 or later and has no third-party runtime
dependencies. From the repository root:

```bash
python -m pip install --editable .
```

## Run

Run the deterministic demonstration:

```bash
python -m renegade
```

The installed console-script equivalent is:

```bash
renegade
```

## Test and check

Run the complete current unit-test suite:

```bash
python -m unittest discover -s tests -v
```

Check that all Python sources and tests compile:

```bash
python -m compileall -q src tests
```

Check the working-tree patch for whitespace errors:

```bash
git diff --check
```

## Package layout

| Path | Role |
| --- | --- |
| `src/renegade/core.py` | Implemented execution foundation: observations, capabilities, workspace traces, in-memory records, and the executive. |
| `src/renegade/foundation.py` | Implemented immutable primitives for identifiers, evidence references, lifecycle transition decisions, and lineage edges. |
| `src/renegade/__main__.py` | The runnable deterministic example. |
| `src/renegade/__init__.py` | Current public API for the execution foundation. |
| `tests/test_core.py` | Unit tests for the current public execution behavior and module entry point. |
| `pyproject.toml` | Packaging metadata and the `renegade` console-script declaration. |

## Documentation map

Read documents by their role, not as a claim that every described idea is
implemented.

| Document | Role | Use it for |
| --- | --- | --- |
| [AGENTS.md](AGENTS.md) | Contributor guidance | Required contributor workflow and implementation constraints. |
| [CONSTITUTION.md](CONSTITUTION.md) | Specification | The project’s enduring design principles and intended spine. |
| [CAPABILITY_CONTRACT.md](CAPABILITY_CONTRACT.md) | Specification | Requirements that a future capability must satisfy. It is not a description of the current `Capability` dataclass. |
| [LIFECYCLE.md](LIFECYCLE.md) | Specification | Intended lifecycle policy; only explicit transition-decision primitives currently exist. |
| [LINEAGE.md](LINEAGE.md) | Specification | Intended provenance and ancestry policy; only lineage-edge primitives currently exist. |
| [EMERGENCE.md](EMERGENCE.md) | Design rationale / historical narrative | A candidate architectural idea, not implemented emergence detection. |
| [CONCEPTS.md](CONCEPTS.md) | Specification | Intended concept model. No `Concept` implementation exists in this checkout. |
| [MILESTONES.md](MILESTONES.md) | Verified-history record | Append-only milestone history and its current-tree audit correction. |
| [CHANGELOG.md](CHANGELOG.md) | Change record | Concise release-facing changes; it does not duplicate milestone evidence. |

There is currently no `docs/` directory. The top-level documents above are the
complete documentation set.

## Verified history and current truth

`MILESTONES.md` is the repository’s verified architectural-history record; it
is not a roadmap. Its audit correction distinguishes claims preserved as
historical text from what can be reproduced from the current source and tests.
`CHANGELOG.md` is deliberately brief and points to milestones rather than
repeating their evidence.

When a document and executable code appear to disagree, inspect the source and
tests first, then record the discrepancy rather than silently treating a
specification as implementation. The current source tree is the operative
description of implemented behavior.

## What is not implemented

The following are intentionally absent from this checkout:

- concepts or a concept registry;
- interpretation, planning, or general reasoning;
- automatic capability retrieval, applicability ranking, or graph traversal;
- validation, promotion, transfer, learning, or emergence detection;
- persistence, probabilistic inference, neural computation; and
- ARC-specific data, representations, or solving.

The in-memory `Memory` class is an execution record and manually populated
capability registry. It is not persistent memory or learning.

## Contributor navigation

1. Start here for current status and commands.
2. Read [AGENTS.md](AGENTS.md), then the governing specifications listed there,
   before changing code.
3. Read the relevant source module and its tests before changing behavior.
4. Use [MILESTONES.md](MILESTONES.md) for verified history, and
   [CHANGELOG.md](CHANGELOG.md) for concise change-oriented context.
5. Keep specifications, implementation, evidence, validation, and historical
   records distinct. Do not infer unimplemented behavior from an aspirational
   document.

The project’s long-term ambition is described by the specifications. The
current implementation remains intentionally much smaller.
