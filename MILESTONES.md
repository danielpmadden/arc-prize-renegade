# MILESTONES.md

# Renegade Verified Milestones

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

# Current Verified Architecture

The current architecture consists of the following verified layers.

Execution

Identity

Lifecycle

Evidence

Lineage

Concepts

Each layer depends only upon previously verified layers.

No verified layer may regress without explicit architectural approval.

---

# Current Verified Non-Capabilities

Renegade intentionally does not yet implement:

Observation

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

Knowledge graphs

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
