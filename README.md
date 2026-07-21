# ARC Prize Renegade

> *Build the spine before teaching the body to move.*

Renegade is an early-stage experiment in a deterministic, symbolic
architecture. It is **not an ARC solver**: the repository contains no ARC
tasks, ARC-specific representations, handcrafted ARC rules, or solver.

## Current repository status

This checkout implements a deliberately small foundation through measurement:

- immutable, identified `Observation` values and ordered `ObservationFrame` groups;
- exact, insertion-ordered observation registration without payload deduplication;
- immutable identity-based measurements, exact measurement registration, and small deterministic property-measurement capabilities;
- explicitly registered `Capability` callables;
- execution of one explicitly requested capability by `Executive`;
- structured, ordered attempt traces and append-only in-memory execution
  records; and
- immutable `Concept` values and categories for explicit references only; and
- a small set of identity, evidence-reference, lifecycle-transition, and
  lineage-edge value primitives in `renegade.foundation`.

The runnable example records a tiny supplied structured grid in a frame and executes an explicit dimension-measurement capability. It demonstrates receipt and measured properties, not recognition, validation, reasoning, promotion, learning, or ARC solving.

The current test suite verifies the public execution, observation,
measurement, concept-value, and foundation-primitive behavior. Concepts and
foundation values remain standalone primitives; references do not change
lifecycle or evidence semantics.

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
| `src/renegade/observations.py` | Immutable observations, frames, supported-value normalization, and exact ordered registry. |
| `src/renegade/measurements.py` | Immutable measurements, sets, provenance, exact registry, and small property capabilities. |
| `src/renegade/core.py` | Execution foundation: capabilities, workspace traces, in-memory records, and frame handling. |
| `src/renegade/concepts.py` | Minimal immutable concepts used only for explicit observation references. |
| `src/renegade/foundation.py` | Implemented immutable primitives for identifiers, evidence references, lifecycle transition decisions, and lineage edges. |
| `src/renegade/__main__.py` | The runnable deterministic example. |
| `src/renegade/__init__.py` | Current public API for the foundation through measurement. |
| `tests/test_core.py` | Unit tests for execution behavior, the public API, and the module entry point. |
| `tests/test_observations.py` | Focused tests for observation values, frames, registry boundaries, and execution integration. |
| `tests/test_measurements.py` | Focused tests for measurements, measurement capabilities, registries, and execution integration. |
| `tests/test_foundation.py` | Focused tests for identity, evidence, lifecycle-transition, and lineage primitives. |
| `pyproject.toml` | Packaging metadata and the `renegade` console-script declaration. |

## Public API summary

`renegade` exports the execution API (`Capability`, `Memory`, `Executive`,
`Workspace`, `Outcome`, `EventKind`, `ExecutionEvent`, `MemoryEvent`, and
`double_number`); the observation API (`Observation`, `ObservationKind`,
`ObservationFrame`, and `ObservationRegistry`); the measurement API
(`Measurement`, `MeasurementKind`, `MeasurementSet`, `MeasurementRegistry`,
`measure_dimensions`, `measure_bounds`, and `measure_observation_count`); and
the reference-value API (`Concept`, `ConceptCategory`, `StableIdentifier`,
`EvidenceKind`, and `EvidenceReference`). Together, they support registering a
named callable and executing that explicitly requested callable against an
observation or observation frame with an inspectable trace. Measurements
compute reproducible properties. `Concept` values can be created explicitly,
but there is no concept registry, extraction, or interpretation. Observation
equality is identity-only; equal values are not deduplicated. The API does not
provide perception, automatic capability selection, reasoning, validation,
lifecycle management, or learning.

## Architectural roadmap

**Implemented**

- ✓ Repository Foundation
- ✓ Identity
- ✓ Lifecycle primitives
- ✓ Evidence references
- ✓ Concepts as immutable values
- ✓ Execution
- ✓ Observation
- ✓ Measurement
- ✓ Repository reconciliation / documentation audit

**Next architectural work**

- Perception and percepts

**Future work**

- Semantic relationships and interpretation
- Hypothesis generation and reasoning
- Reflection and learning
- ARC adapter

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
| [CONCEPTS.md](CONCEPTS.md) | Specification | Intended concept model beyond the current immutable `Concept` value and category. |
| [MILESTONES.md](MILESTONES.md) | Verified-history record | Append-only milestone history and its current-tree audit correction; not a roadmap or current implementation reference by itself. |
| [CHANGELOG.md](CHANGELOG.md) | Change record | Concise release-facing changes; it does not duplicate milestone evidence. |
| [LICENSE](LICENSE) | Legal notice | All-rights-reserved terms and permission requirements. |
| [NOTICE.md](NOTICE.md) | Repository notice | Why the repository is public and how contributions are reviewed. |
| [PRIVACY.md](PRIVACY.md) | Privacy statement | Repository data-collection and telemetry position. |
| [SECURITY.md](SECURITY.md) | Security policy | Responsible vulnerability reporting guidance and scope. |

`docs/architecture/overview.md` describes current implementation boundaries;
the engineering journals record the Pass 4 and Pass 5 design choices.

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

- perception, percepts, a concept registry, concept extraction, or
  interpretation;
- planning or general reasoning;
- automatic capability retrieval, applicability ranking, or graph traversal;
- validation, promotion, transfer, learning, or emergence detection;
- persistence, probabilistic inference, neural computation; and
- ARC-specific data, representations, or solving.

The in-memory `Memory` class is an execution record and manually populated
capability registry. It is not persistent memory or learning.

## Repository Status and Licensing

Renegade is source-available and **not open source**. Copyright remains with
Daniel Madden. Reuse requires explicit written permission from the copyright
holder. See [LICENSE](LICENSE) for details.

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
