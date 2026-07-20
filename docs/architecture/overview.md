# Architecture Overview

> **Document role: implementation overview.** It describes the current source tree and does not promote this branch to official status.

The observation substrate is the boundary between supplied input and later perception. `Observation` records an explicit stable identity, recording kind, supported immutable payload, source, and optional evidence or concept references. Equality and hashing use `StableIdentifier` only: equal payloads, labels, or sources do not merge observations.

`ObservationFrame` is a non-empty ordered tuple of distinct observation identities recorded together. Its order is insertion order only; membership does not assert time, space, causality, consistency, objecthood, or semantic similarity. `ObservationRegistry` owns exact identity lookup and insertion order. It has no fuzzy lookup, validation, or inference.

`Executive.solve` accepts one observation (for the prior public API) or a frame. A frame emits `observation.frame.received`, then one `observation.registered` event per supplied observation, before capability retrieval. The workspace owns a fresh registry for that execution.

Concept references are identifiers chosen by the caller. They neither prove membership nor create, mutate, validate, or promote a concept. Evidence references remain pointers to material that may support later evaluation; they do not establish truth or confidence.
