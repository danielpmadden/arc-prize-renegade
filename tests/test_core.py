"""Tests for the deterministic explicit Renegade execution cycle."""

from __future__ import annotations

import subprocess
import sys
import unittest

import renegade

from renegade import (
    Capability,
    EventKind,
    Executive,
    Memory,
    Observation,
    Outcome,
    double_number,
)


class RenegadeCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.memory = Memory()
        self.capability = Capability(
            name="double_number",
            description="Multiply an integer by two.",
            function=double_number,
        )
        self.memory.remember_capability(self.capability)
        self.executive = Executive(self.memory)

    def test_capability_registration_preserves_identity(self) -> None:
        self.assertIs(self.memory.capabilities["double_number"], self.capability)
        self.assertEqual(self.capability.version, "0.1.0")
        self.assertEqual(self.capability.source, "foundational primitive")

    def test_public_api_has_the_documented_intentional_surface(self) -> None:
        expected = {
            "Capability", "Concept", "ConceptCategory", "EvidenceKind",
            "EvidenceReference", "EventKind", "ExecutionEvent", "Executive",
            "Measurement", "MeasurementKind", "MeasurementRegistry", "MeasurementSet",
            "Memory", "MemoryEvent", "Observation", "ObservationFrame",
            "ObservationKind", "ObservationRegistry", "Outcome", "StableIdentifier",
            "Workspace", "double_number", "measure_bounds", "measure_dimensions",
            "measure_observation_count",
            "Percept", "PerceptKind", "PerceptRegistry", "PerceptSet", "PerceptPipelineResult",
            "form_connected_regions", "form_frame_percept", "inspect_grid",
            "PerceptGraph", "RelationshipDirection", "RelationshipKind", "RelationshipRegistry",
            "RelationshipSet", "StructuralRelationship", "derive_relationships",
            "derive_topological_relationships", "derive_spatial_relationships", "derive_alignment_relationships",
            "derive_exact_comparison_relationships", "derive_frame_relationships",
            "Invariant", "InvariantKind", "InvariantRegistry", "InvariantSet", "derive_invariants",
            "derive_same_value_groups", "derive_same_shape_groups", "derive_same_cell_count_groups",
            "derive_same_bounds_groups", "derive_translation_families",
        }
        self.assertEqual(set(renegade.__all__), expected)
        self.assertTrue(all(hasattr(renegade, name) for name in renegade.__all__))

    def test_successful_execution_records_result_and_memory(self) -> None:
        workspace = self.executive.solve(
            Observation(name="test_number", value=5), "double_number"
        )

        self.assertEqual(workspace.outcome, Outcome.SUCCEEDED)
        self.assertEqual(workspace.result, 10)
        self.assertIsNone(workspace.failure_reason)
        self.assertEqual(self.memory.history[0].capability_name, "double_number")
        self.assertEqual(self.memory.history[0].observation_name, "test_number")
        self.assertEqual(self.memory.history[0].outcome, Outcome.SUCCEEDED)

    def test_missing_capability_produces_inspectable_failure(self) -> None:
        workspace = self.executive.solve(
            Observation(name="test_number", value=5), "unknown_capability"
        )

        self.assertEqual(workspace.outcome, Outcome.FAILED)
        self.assertIsNone(workspace.result)
        self.assertEqual(workspace.failure_reason, "Capability not found: unknown_capability")
        self.assertEqual(
            [event.kind for event in workspace.trace],
            [EventKind.OBSERVATION_RECORDED, EventKind.CAPABILITY_MISSING],
        )
        self.assertEqual(self.memory.history, [])

    def test_invalid_capability_input_produces_inspectable_failure(self) -> None:
        workspace = self.executive.solve(
            Observation(name="invalid_value", value="five"), "double_number"
        )

        self.assertEqual(workspace.outcome, Outcome.FAILED)
        self.assertEqual(workspace.failure_reason, "double_number requires an integer")
        self.assertEqual(workspace.trace[2].kind, EventKind.EXECUTION_FAILED)
        self.assertEqual(dict(workspace.trace[2].details)["error_type"], "TypeError")
        self.assertEqual(self.memory.history[0].outcome, Outcome.FAILED)

    def test_invalid_request_objects_raise_documented_exceptions(self) -> None:
        with self.assertRaisesRegex(TypeError, "observation must be an Observation"):
            self.executive.solve("not an observation", "double_number")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "capability_name must be a non-empty string"):
            self.executive.solve(Observation(name="valid", value=1), "")

    def test_repeated_execution_has_equivalent_trace(self) -> None:
        observation = Observation(name="repeatable_number", value=8)
        first_run = self.executive.solve(observation, "double_number")
        second_run = self.executive.solve(observation, "double_number")

        self.assertEqual(first_run.result, second_run.result)
        self.assertEqual(first_run.outcome, second_run.outcome)
        self.assertEqual(first_run.trace, second_run.trace)

    def test_trace_has_ordered_structured_events(self) -> None:
        workspace = self.executive.solve(
            Observation(name="ordered_number", value=3), "double_number"
        )

        self.assertEqual([event.sequence for event in workspace.trace], [1, 2, 3, 4])
        self.assertEqual(
            [event.kind for event in workspace.trace],
            [
                EventKind.OBSERVATION_RECORDED,
                EventKind.CAPABILITY_RETRIEVED,
                EventKind.EXECUTION_SUCCEEDED,
                EventKind.MEMORY_RECORDED,
            ],
        )
        self.assertEqual(dict(workspace.trace[0].details)["observation_name"], "ordered_number")

    def test_package_entry_point_execution(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "renegade"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("ARC Prize Renegade", completed.stdout)
        self.assertIn("[measurement.created]", completed.stdout)
        self.assertIn("Measurement: FrozenValueMapping(entries=(('height', 2), ('width', 2)))", completed.stdout)


if __name__ == "__main__":
    unittest.main()
