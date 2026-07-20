# 0005: Deterministic Measurements

> **Document role: engineering journal.** This records Pass 5 design choices, not an assertion of official or merged status.

## Decision

Measurement is an instrument layer above observation: it computes a reproducible property without declaring what the observed material is. A measurement has an explicit identity, a small property-kind vocabulary, a constrained immutable value, and explicit production provenance. Equality is identity-only, so identical values never merge independently produced records.

The value boundary deliberately reuses the observation normalization policy: scalar primitives, finite floats, tuples, and string-keyed mappings normalized to immutable sorted mappings are accepted. Mutable containers and opaque runtime objects are rejected.

## Boundaries and execution

Measurements retain explicit observation identifiers, a producing capability name, evidence references, and optional concept references. References are provenance only: they do not imply meaning, truth, or validation. Measurement sets are ordered immutable groups that assert only common production context. Registries perform exact lookup only.

Three deliberately small capabilities measure tuple-grid dimensions, its inclusive supplied coordinate bounds, and frame observation count. `Executive` records creation and workspace registration only when a capability returns a measurement value. No feature extraction, connected components, object identification, symmetry, scene graph, classification, or inference was introduced.
