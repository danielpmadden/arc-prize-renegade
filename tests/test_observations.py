"""Focused tests for the deterministic observation substrate."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

from renegade import (
    Capability, Concept, ConceptCategory, EvidenceKind, EvidenceReference, Executive,
    Memory, Observation, ObservationFrame, ObservationKind, ObservationRegistry,
    StableIdentifier,
)


def identifier(category: str, name: str) -> StableIdentifier:
    return StableIdentifier(category, name, 1)


class ObservationTests(unittest.TestCase):
    def test_construction_identity_equality_and_payload_boundary(self) -> None:
        first = Observation(3, identifier("observation", "first"), ObservationKind.RAW)
        second = Observation(3, identifier("observation", "second"), ObservationKind.RAW)
        same_identity = Observation("different", identifier("observation", "first"))
        self.assertNotEqual(first, second)
        self.assertEqual(first, same_identity)
        self.assertEqual(hash(first), hash(same_identity))

    def test_rejects_malformed_kind_and_unsupported_values(self) -> None:
        with self.assertRaisesRegex(TypeError, "kind"):
            Observation(1, identifier("observation", "bad"), "raw")  # type: ignore[arg-type]
        with self.assertRaisesRegex(TypeError, "immutable supported"):
            Observation([], identifier("observation", "list"))
        with self.assertRaisesRegex(ValueError, "finite"):
            Observation(float("nan"), identifier("observation", "nan"))

    def test_values_are_normalized_to_immutable_deterministic_structures(self) -> None:
        observation = Observation({"b": (2, None), "a": True}, identifier("observation", "map"))
        self.assertEqual(tuple(observation.value), ("a", "b"))
        with self.assertRaises(FrozenInstanceError):
            observation.value = 1  # type: ignore[misc]

    def test_explicit_concept_and_evidence_references_are_preserved(self) -> None:
        concept_id = identifier("concept", "color")
        evidence = EvidenceReference(EvidenceKind.MANUAL_SOURCE, "input")
        observation = Observation(
            "red", identifier("observation", "color"), concept_references=(concept_id,), evidence=(evidence,)
        )
        self.assertEqual(observation.concept_references, (concept_id,))
        self.assertEqual(observation.evidence, (evidence,))
        with self.assertRaisesRegex(ValueError, "duplicates"):
            Observation("red", identifier("observation", "duplicate"), concept_references=(concept_id, concept_id))

    def test_concept_reference_does_not_change_concept_or_claim_membership(self) -> None:
        concept = Concept(identifier("concept", "color"), ConceptCategory.PROPERTY, "Color")
        first = Observation("red", identifier("observation", "one"), concept_references=(concept.identity,))
        second = Observation("red", identifier("observation", "two"), concept_references=(concept.identity,))
        self.assertEqual(concept.name, "Color")
        self.assertNotEqual(first, second)


class FrameAndRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.first = Observation("left", identifier("observation", "left"))
        self.second = Observation("right", identifier("observation", "right"), ObservationKind.STATE)

    def test_frame_is_nonempty_ordered_and_rejects_duplicate_identity(self) -> None:
        frame = ObservationFrame(identifier("frame", "pair"), (self.second, self.first))
        self.assertEqual(tuple(frame), (self.second, self.first))
        with self.assertRaisesRegex(ValueError, "non-empty"):
            ObservationFrame(identifier("frame", "empty"), ())
        with self.assertRaisesRegex(ValueError, "duplicate"):
            ObservationFrame(identifier("frame", "duplicate"), (self.first, self.first))

    def test_grouping_does_not_add_relationships(self) -> None:
        frame = ObservationFrame(identifier("frame", "independent"), (self.first, self.second))
        self.assertEqual(frame.concept_references, ())
        self.assertEqual(self.first.concept_references, ())

    def test_registry_exact_ordered_immutable_queries_and_conflicts(self) -> None:
        registry = ObservationRegistry()
        registry.register(self.first)
        registry.register(self.second)
        conflict = Observation("different", identifier("observation", "conflict"))
        registry.register(conflict)
        self.assertEqual(registry.get(self.second.identity), self.second)
        self.assertEqual(registry.all(), (self.first, self.second, conflict))
        self.assertEqual(registry.by_kind(ObservationKind.STATE), (self.second,))
        with self.assertRaisesRegex(ValueError, "already registered"):
            registry.register(self.first)


class ObservationExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.memory = Memory()
        self.memory.remember_capability(Capability("count_frame", "Count supplied observations.", lambda frame: len(frame.observations)))
        self.frame = ObservationFrame(
            identifier("frame", "execution"),
            (Observation(("red",), identifier("observation", "grid"), ObservationKind.STRUCTURED),),
        )

    def test_frame_execution_registers_before_execution_with_repeatable_trace(self) -> None:
        executive = Executive(self.memory)
        first = executive.solve(self.frame, "count_frame")
        second = executive.solve(self.frame, "count_frame")
        self.assertEqual(first.result, 1)
        self.assertEqual(first.trace, second.trace)
        self.assertEqual([event.kind.value for event in first.trace], [
            "observation.frame.received", "observation.registered", "capability.retrieved",
            "execution.succeeded", "memory.recorded",
        ])
        self.assertEqual(first.observations.all(), self.frame.observations)

    def test_failed_frame_execution_registers_only_supplied_observation(self) -> None:
        self.memory.remember_capability(Capability("fail", "Fail explicitly.", lambda frame: (_ for _ in ()).throw(ValueError("no"))))
        workspace = Executive(self.memory).solve(self.frame, "fail")
        self.assertEqual(workspace.observations.all(), self.frame.observations)
        self.assertEqual(workspace.trace[-2].kind.value, "execution.failed")


if __name__ == "__main__":
    unittest.main()

class ObservationBoundaryTests(unittest.TestCase):
    def test_observation_can_have_no_concept_reference(self) -> None:
        observation = Observation("supplied", identifier("observation", "unclassified"))
        self.assertEqual(observation.concept_references, ())

    def test_registry_retrieves_explicit_concept_references_in_insertion_order(self) -> None:
        concept_id = identifier("concept", "shared")
        registry = ObservationRegistry()
        first = Observation(1, identifier("observation", "first-ref"), concept_references=(concept_id,))
        second = Observation(2, identifier("observation", "second-ref"), concept_references=(concept_id,))
        registry.register(first)
        registry.register(second)
        self.assertEqual(registry.by_concept(concept_id), (first, second))

    def test_evidence_and_conflict_do_not_select_truth_or_lifecycle(self) -> None:
        evidence = EvidenceReference(EvidenceKind.MANUAL_SOURCE, "source-a")
        registry = ObservationRegistry()
        left = Observation("yes", identifier("observation", "claim-a"), evidence=(evidence,))
        right = Observation("no", identifier("observation", "claim-b"))
        registry.register(left)
        registry.register(right)
        self.assertEqual(registry.all(), (left, right))
        self.assertEqual(left.evidence, (evidence,))
