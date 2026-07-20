# 0004: Deterministic Observations

> **Document role: engineering journal.** This records Pass 4 design choices, not an assertion of official or merged status.

## Decision

Observation is a sensory ledger, not interpretation. An `Observation` has an explicit `StableIdentifier`; equality and hashing use that identity alone. Payload equality, description, source, and concept references never dedupe or make two observations equivalent. The legacy `name=` constructor remains as a compatibility path and deterministically maps to `observation:<name>:1`.

Values are deliberately narrow: `None`, booleans, integers, finite floats, strings, bytes, tuples of supported values, and mappings with string keys. Mappings are recursively normalized into ordered immutable mappings. Lists, sets, non-finite floats, executable objects, and opaque resources are rejected.

Frames are non-empty immutable ordered tuples and reject duplicate observation identities. The registry stores observations by exact identity in insertion order and returns tuples. It filters only by recording kind and explicit concept-reference identity.

## Boundaries and execution

Concept references are caller-supplied identifiers, preserve order, and reject duplicates. They do not assert that a concept applies. Evidence references are preserved without truth, confidence, validation, lifecycle, or promotion effects. Conflicting observations may coexist; no winner is selected.

Execution receives a frame explicitly. Its trace records frame receipt and registration in supplied order before retrieval and execution. Failure never fabricates extra observations. The workspace has its own registry; no persistence, global cache, or graph is introduced.

## Deliberately deferred

No perception, feature extraction, classification, object extraction, spatial reasoning, relationship inference, validation, conflict resolution, concept learning, planning, reasoning, persistence, or ARC task handling was added. Rejected alternatives were payload-based deduplication, arbitrary-object serialization, an event-sourcing framework, and a global mutable workspace.
