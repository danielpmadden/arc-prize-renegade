# Renegade Verified Milestones

> **Document role: verified-history record.** This append-only record preserves
> milestone claims and later audit corrections. It is not a roadmap or, by
> itself, a description of the current implementation; consult the
> **Current-Tree Audit Correction** and `README.md` for current status.

This document records the verified architectural evolution of Renegade.

A milestone is not a roadmap item.

A milestone represents a permanent architectural capability that has been:

- designed,
- implemented,
- verified,
- tested,
- documented,
- and (when appropriate) audited.

Milestones are append-only.

Once verified, they become part of the permanent architectural history of the repository.

If a milestone later requires correction, clarification, or expansion, that work is recorded through a later audit or milestone rather than rewriting history.

Regression of a verified milestone is considered an architectural defect unless explicitly documented and intentionally approved.

---

# Milestone 0.1

## Deterministic Execution Foundation

Status

Verified

Implementation Pass

Pass 1

Purpose

Establish the smallest deterministic execution substrate upon which every future architectural layer can depend.

Verified Capabilities

- Installable Python package
- Deterministic execution cycle
- Explicit execution outcomes
- Structured execution events
- Append-only execution memory
- Deterministic execution ordering
- Public package entry point
- Deterministic test suite

Architectural Principles Established

- Determinism before intelligence
- Explicit outcomes instead of hidden state
- Inspectable execution history
- Small public surface
- Simple execution semantics

Verified Non-Capabilities

This milestone intentionally does not provide:

- concepts
- identity
- lifecycle
- lineage
- evidence
- planning
- reasoning
- learning
- ARC solving

Verification

- deterministic execution verified
- unit tests passed
- package installation verified
- entry point verified

---

# Milestone 0.2

## Stable Identity and Lifecycle

Status

Verified

Implementation Pass

Pass 2

Purpose

Introduce persistent architectural identity independent of execution.

Verified Capabilities

- StableIdentifier
- Immutable identifiers
- Lifecycle states
- Explicit lifecycle transitions
- Lifecycle history
- Evidence references
- Lineage primitives
- Capability eligibility
- Deterministic capability identity

Architectural Principles Established

- Identity is permanent
- Lifecycle is explicit
- History is preserved
- Evidence is referenced
- Lineage records ancestry
- Execution eligibility depends upon lifecycle

Verified Non-Capabilities

This milestone intentionally does not provide:

- automatic promotion
- automatic validation
- automatic lifecycle transitions
- planning
- reasoning
- concept systems
- graph traversal
- learning

Verification

- lifecycle transitions verified
- identity stability verified
- lineage verified
- execution restrictions verified
- deterministic behavior verified

---

# Milestone 0.3

## Deterministic Concept Substrate

Status

Verified

Implementation Pass

Pass 3

Audit

Pass 3 Corrective Audit

Purpose

Introduce first-class symbolic concepts as deterministic architectural primitives.

Verified Capabilities

- Immutable Concept objects
- Stable concept identities
- Typed concept categories
- Typed concept relationships
- Deterministic ConceptRegistry
- Explicit concept registration
- Exact identity lookup
- Exact name lookup
- Duplicate-name support
- Duplicate-identity rejection
- Capability concept declarations
- Observation concept references
- Workspace concept storage
- Concept execution events

Architectural Principles Established

- Concepts are first-class entities
- Concepts are not strings
- Identity is independent of naming
- Concepts are explicitly created
- Relationships are semantic
- Registration is deterministic
- Capability semantics are explicit
- Workspace carries concepts without interpretation

Concept Equality Policy

Concept equality is determined exclusively by StableIdentifier.

Matching names do not imply identity.

Matching descriptions do not imply identity.

Matching categories do not imply identity.

Matching provenance does not imply identity.

Matching evidence does not imply identity.

Different identities always represent different concepts.

Evidence Policy

EvidenceReference records supporting material.

EvidenceReference does not imply:

- truth
- correctness
- validation
- confidence
- promotion
- trusted status

Relationship Policy

LineageEdge records historical ancestry.

ConceptRelationship records semantic relationships.

These are intentionally different architectural primitives.

Neither substitutes for the other.

Verified Non-Capabilities

This milestone intentionally does not provide:

- concept extraction
- graph construction
- graph traversal
- semantic search
- automatic abstraction
- planning
- reasoning
- transfer
- learning
- ARC solving

Verification

Pass 3 implementation completed.

Corrective audit restored all Pass 2 behavioral contracts.

Twenty-five deterministic unit tests passed.

Public API verified.

Documentation synchronized.

Regression eliminated before merge.

---

# Current-Tree Audit Correction

This append-only correction describes what is reproducible from the current
repository tree. It does not assert whether historical verification runs
occurred outside this tree; it corrects claims that are not supported by the
currently tracked implementation and tests.

- Milestone 0.2 overstates the current implementation. The tree provides
  `StableIdentifier`, `EvidenceReference`, lifecycle states and explicit
  transition decisions, plus lineage primitives. It does not provide lifecycle
  history, capability eligibility, deterministic capability identity, or
  execution restrictions. The current test suite has no dedicated tests for
  these foundation primitives.
- Milestone 0.3 is not implemented in the current tree. `docs/foundations/CONCEPTS.md` is a
  specification, but there are no `Concept`, `ConceptRegistry`, or concept
  relationship implementation files or tests. Its claimed verification must
  not be treated as current executable behavior.
- The current implementation does provide `Observation`; therefore listing
  observation as a current non-capability was inaccurate.

Future work may establish additional verified milestones only after the
implementation, tests, and documentation required by this file’s policy are
present in the repository.

---

# Current Implemented Architecture

The current tree implements an execution foundation and a set of standalone
foundation value primitives:

- execution: observations, explicitly registered capabilities, one requested
  capability execution, structured traces, and append-only in-memory execution
  records;
- identity: `StableIdentifier`;
- evidence references: `EvidenceReference`;
- lifecycle: states and explicit transition decisions; and
- lineage: `LineageEdge` relationships.

Only the execution foundation has dedicated tests in the current suite. The
foundation primitives are implemented but are not currently covered by
dedicated tests. These facts describe the present tree; they do not promote any
future architectural layer.

---

# Current Verified Non-Capabilities

Renegade intentionally does not yet implement:

Representation

Interpretation

Planning

Reasoning

Transfer

Learning

Emergence detection

Automatic validation

Automatic promotion

Graph traversal

Knowledge graphs or concept registries

Persistence

Probabilistic inference

Neural computation

ARC-specific representations

ARC-specific solving

These omissions are intentional architectural boundaries rather than missing features.

---

# Milestone Policy

Every implementation pass must preserve all verified milestones.

New milestones may only be created after:

- implementation,
- verification,
- testing,
- documentation,
- and (when appropriate) audit.

Milestones are historical records.

They are never rewritten.

Future milestones extend this document.

They do not replace earlier milestones.

The architectural history of Renegade is append-only.

---

# Milestone 0.4

## Deterministic Observation Substrate

Status

Implementation Pass 4 — pending human review

This append-only entry records the implemented observation substrate in this
checkout. It is not a claim that branch work is merged or official.

Implemented scope includes immutable identity-based observations, constrained
immutable values, ordered frames, exact insertion-ordered registration, and
explicit frame-receipt/registration execution events. Observation recording
does not interpret payloads, validate them, resolve conflicts, create or alter
concepts, or perform ARC solving. Verification commands and test evidence are
recorded with the implementation change for human review.

---

# Milestone 0.5

## Deterministic Measurement Substrate

Status

Implementation Pass 5 — pending human review

This append-only entry records the measurement substrate implemented in this
checkout. It is not a claim that branch work is merged or official.

Implemented scope includes immutable identity-based measurements, constrained
immutable measurement values, explicit observation/capability/evidence
provenance, immutable ordered measurement sets, exact in-memory registry
lookup, workspace storage, measurement execution events, and small property
measurement capabilities. Measurements report dimensions, bounds, or counts;
they do not identify, classify, validate, or interpret supplied material.

---

# Reconciliation Pass 5.5

## Current-Tree Documentation Audit

Status

Documentation reconciliation — pending human review

This append-only audit records the state reproducible from this checkout after
the observation and measurement passes. It does not promote branch work to
official status and does not revise earlier historical claims.

The current tree implements repository foundation, identity, explicit
lifecycle-transition decisions, evidence references, lineage edges, immutable
concept values, execution, observation, and measurement. `Concept` and
`ConceptCategory` exist as explicit immutable values, but no concept registry,
relationship model, extraction, interpretation, or concept-execution subsystem
exists.

The architectural boundary after measurement is future perception. Percepts,
object extraction, scene graphs, semantic relationships, interpretation,
reasoning, planning, reflection, learning, transformation search, and ARC
solving remain intentionally absent.

This correction supersedes only the current-tree portion of the earlier audit
that said no `Concept` implementation existed. The preserved Milestone 0.3
claims about a concept registry and relationships remain unsupported by the
current tree.

---

# Post-Merge Status Addendum

This append-only addendum records the status change after the preserved
pre-merge entries above.

- Milestone 0.4 / Pass 4 was merged into main.
- Milestone 0.5 / Pass 5 was merged into main.
- Reconciliation Pass 5.5 was merged into main.
- Observation and measurement are now part of the current official repository.
- Perception remains the next unimplemented architectural layer.

---

# Milestone 0.6

## Deterministic Percept Formation and Playground

Status: Implementation Pass 6 — pending human review.

Implemented immutable identity-based percepts with provenance, ordered sets,
exact registries, whole-frame formation, deterministic four-directional
same-value region formation, workspace separation, trace events, and the
`python -m renegade.playground` JSON-grid inspection tool. Verification uses
the documented unit, compilation, module, and diff checks. Semantic
interpretation, reasoning, learning, and ARC solving remain absent.

## Pass 7 — Deterministic structural relationships and percept graph (experimental branch)
Implemented immutable identity-based structural relationship records, bounded exact pairwise derivation, a relationship registry, and a read-only percept graph. Symmetric endpoints are canonicalized; directional facts emit explicit inverse records. The pipeline and playground now expose relationship records and graph counts. Verification: `python -m unittest discover -s tests -v`, `python -m compileall -q src tests`, and playground examples. Concept association, interpretation, hypotheses, reasoning, reflection, learning, and ARC solving remain absent.

## Pass 8 — Structural invariants (experimental branch)
Added immutable, identity-based invariant records that compress connected SAME_VALUE, SAME_COORDINATE_SHAPE, SAME_CELL_COUNT, SAME_BOUNDS_SIZE, and TRANSLATED_COPY relationship groups. The pipeline records invariants after relationships and the playground reports them. Invariants are structural regularities, not concepts, interpretations, hypotheses, reasoning, learning, or ARC solving.

## Pass 9 — Structural archetypes (experimental branch)

Added immutable, identity-based structural archetypes derived exclusively from
structural invariant records. The exact vocabulary comprises SingleCell,
HorizontalLine, VerticalLine, FilledRectangle, HollowRectangle, Square,
LinearChain, TranslationArray, and Checkerboard. Archetypes retain invariant
provenance and frame context, are recorded separately in the workspace, and do
not introduce concepts, semantic association, interpretation, hypotheses,
reasoning, learning, prediction, or ARC solving.

---

# Pass 10 — Repository topology and capability characterization

Status: Implementation pass — pending human review.

This append-only entry records branch evidence only. It reorganizes current,
governing, legal, roadmap, and research documentation; adds a deterministic
characterization harness; and adds corpus, exhaustive tiny-grid, boundary, and
integrity tests for the existing observation-through-archetype pipeline. It
does not add concept association, interpretation, reasoning, learning, or ARC
solving. The accompanying baseline report records observed recognitions,
rejections, and performance limits without promoting this branch to official
status.

---

# Pass 11 — Deterministic ARC task representation

Status: Implementation pass — pending human review.

This append-only entry records branch evidence only. Immutable task,
training-pair, and role-labelled grid records parse canonical ARC JSON and
inspect each grid independently through the existing structural pipeline.
Ordered task events and count-only diagnostics preserve provenance and order.
This does not compare grids, discover transformations, introduce hypotheses,
reason, or solve ARC.

## Experimental implementation addendum — Passes 12–17 solver vertical slice

The current tree contains an experimental bounded deterministic ARC solver
vertical slice. It is not a retroactive claim about prior passes or official
promotion. Its exact training validation, test-output construction, CLI, and
local-only benchmark behavior are documented by the current source and tests.
