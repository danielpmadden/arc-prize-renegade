# Architecture Overview

> **Document role: implementation overview.** It describes the current source tree and does not by itself establish official status.

```
Environment
    ↓
Observation
    ↓
Measurement
    ↓
Concepts (explicit values only)
    ↓
Future Perception
```

`Observation` records supplied input. `Measurement` computes one reproducible property from explicit observation references. `Measurement` is immutable and identity-based: equality and hashing use `StableIdentifier`, not a matching payload or provenance. Its value follows the observation supported-value policy, and its explicit provenance records the producing capability, source observations, evidence references, and optional caller-supplied concept references. None of those references assigns meaning or establishes truth.

`MeasurementSet` is a non-empty immutable ordered group with a common producing capability and source observations. It rejects duplicate measurement identities; grouping adds no semantic relationship. `MeasurementRegistry` is exact and insertion-ordered. It retrieves only by identity, kind, producing capability, or source observation—never by ranking, similarity, or traversal.

Small registered capabilities `measure_dimensions`, `measure_bounds`, and `measure_observation_count` report tuple-grid dimensions, supplied-grid bounds, and frame observation count. They do not identify objects or features. When an explicitly requested capability returns a `Measurement` or `MeasurementSet`, `Executive` emits `measurement.created` and `measurement.recorded` events and registers results in the workspace's separate measurement registry.

The workspace preserves observations and measurements separately. `Concept` is
an immutable explicit value with a category, name, description, and evidence;
it has no registry, relationship model, extraction, or interpretation behavior.
Caller-supplied concept references neither prove membership nor create, mutate,
validate, or promote a concept. Perception and percepts are future work;
reasoning, planning, learning, object extraction, and scene graphs are also
absent. Evidence references remain pointers to material that may support later
evaluation; they do not establish truth or confidence.
