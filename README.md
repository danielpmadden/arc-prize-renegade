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
They are available as standalone values; they are not integrated into execution.

This is the current-tree status, not a claim about every idea named in the
repository. For exact boundaries, read [What is not implemented](#what-is-not-implemented)
and the current-tree audit in [MILESTONES.md](MILESTONES.md). For the rules
used to distinguish current status, history, and architecture, read
[EPISTEMOLOGY.md](EPISTEMOLOGY.md).

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

Run the commands from the repository root, in the order shown if you are
checking a fresh change. There are no additional runtime dependencies or build
steps beyond editable installation.

## Package layout

| Path | Role |
| --- | --- |
| `src/renegade/core.py` | Implemented execution foundation: observations, capabilities, workspace traces, in-memory records, and the executive. |
| `src/renegade/foundation.py` | Implemented immutable primitives for identifiers, evidence references, lifecycle transition decisions, and lineage edges. |
| `src/renegade/__main__.py` | The runnable deterministic example. |
| `src/renegade/__init__.py` | Current public API for the execution foundation. |
| `tests/test_core.py` | Unit tests for the current public execution behavior and module entry point; no dedicated foundation-primitive tests exist yet. |
| `pyproject.toml` | Packaging metadata and the `renegade` console-script declaration. |

## Public API summary

`renegade` currently exports `Observation`, `Capability`, `Memory`,
`Executive`, `Workspace`, `Outcome`, `EventKind`, `ExecutionEvent`,
`MemoryEvent`, and `double_number`. Together, they support registering a named
callable and executing that explicitly requested callable against one
observation with an inspectable trace. They do not provide automatic capability
selection, reasoning, validation, lifecycle management, or learning.

## Documentation guide

Read documents by their role, not as a claim that every described idea is
implemented.

| Status label | Meaning |
| --- | --- |
| **Implementation** | Behavior present in the tracked source tree. The source and its tests are the operative evidence. |
| **Verified history** | An append-only account of milestones, with current-tree audit corrections where historical claims cannot be reproduced from this checkout. |
| **Specification** | Intended requirements or architecture. It is not implemented merely because it is documented. |
| **Design rationale / historical narrative** | Context and candidate direction; it does not establish a feature or its verification. |
| **Contributor guidance** | Instructions for changing the repository; it does not extend the public API or verify behavior. |

| Document | Role | Use it for |
| --- | --- | --- |
| [AGENTS.md](AGENTS.md) | Contributor guidance | Required contributor workflow and implementation constraints. |
| [EPISTEMOLOGY.md](EPISTEMOLOGY.md) | Epistemic governance | How to distinguish official state, experiments, specifications, history, speculation, and evidence. |
| [CONSTITUTION.md](CONSTITUTION.md) | Specification | The project’s enduring design principles and intended spine. |
| [CAPABILITY_CONTRACT.md](CAPABILITY_CONTRACT.md) | Specification | Requirements that a future capability must satisfy. It is not a description of the current `Capability` dataclass. |
| [LIFECYCLE.md](LIFECYCLE.md) | Specification | Intended lifecycle policy; only explicit transition-decision primitives currently exist. |
| [LINEAGE.md](LINEAGE.md) | Specification | Intended provenance and ancestry policy; only lineage-edge primitives currently exist. |
| [EMERGENCE.md](EMERGENCE.md) | Design rationale / historical narrative | A candidate architectural idea, not implemented emergence detection. |
| [CONCEPTS.md](CONCEPTS.md) | Specification | Intended concept model. No `Concept` implementation exists in this checkout. |
| [MILESTONES.md](MILESTONES.md) | Verified-history record | Append-only milestone history and its current-tree audit correction; not a roadmap or current implementation reference by itself. |
| [CHANGELOG.md](CHANGELOG.md) | Change record | Concise release-facing changes; it does not duplicate milestone evidence. |

There is currently no `docs/` directory. The top-level documents above are the
complete documentation set. `README.md` is an implementation-status guide,
not a separate architecture specification.

## Verified history and current truth

`MILESTONES.md` is the repository’s verified architectural-history record; it
is not a roadmap. Its current-tree audit distinguishes claims preserved as
historical text from what can be reproduced from the current source and tests.
`CHANGELOG.md` is deliberately brief and reports change-oriented context rather
than repeating milestone evidence.

To resolve an apparent disagreement, use this order: (1) the tracked source
and relevant tests for implemented behavior, (2) the README for the current
status summary, (3) the milestone audit for historical claims, and (4) the
specifications for intended future requirements. Record a discrepancy rather
than silently treating a specification or narrative as implementation.

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

## Recommended reading order

1. Start here for current status and commands.
2. Read [EPISTEMOLOGY.md](EPISTEMOLOGY.md) to interpret status claims.
3. Read [AGENTS.md](AGENTS.md), then the governing specifications listed
   there, before changing code.
4. Use [MILESTONES.md](MILESTONES.md) for verified history and its audit, and
   [CHANGELOG.md](CHANGELOG.md) for concise change-oriented context.
5. Use the [package layout](#package-layout) to find the relevant source module
   and its tests before changing behavior.
6. Keep specifications, implementation, evidence, validation, and historical
   records distinct. Do not infer unimplemented behavior from an aspirational
   document.

The project’s long-term ambition is described by the specifications. The
current implementation remains intentionally much smaller.
