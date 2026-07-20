"""Tests for the deterministic measurement substrate."""
from dataclasses import FrozenInstanceError
import unittest

from renegade import (Capability, EvidenceKind, EvidenceReference, Executive, Measurement,
    MeasurementKind, MeasurementRegistry, MeasurementSet, Memory, Observation,
    ObservationFrame, ObservationKind, StableIdentifier, measure_bounds, measure_dimensions,
    measure_observation_count)


def identifier(category, name): return StableIdentifier(category, name, 1)


class MeasurementTests(unittest.TestCase):
    def setUp(self):
        self.observation = Observation(((1, 2, 3), (4, 5, 6)), identifier("observation", "grid"), ObservationKind.STRUCTURED)
        self.frame = ObservationFrame(identifier("frame", "grid"), (self.observation,))

    def test_construction_identity_immutability_and_value_policy(self):
        first = Measurement(identifier("measurement", "one"), MeasurementKind.COUNT, {"b": 2, "a": 1}, (self.observation.identity,), "counter")
        same = Measurement(identifier("measurement", "one"), MeasurementKind.BOUND, 9, (self.observation.identity,), "other")
        self.assertEqual(first, same)
        self.assertEqual(tuple(first.value), ("a", "b"))
        with self.assertRaises(FrozenInstanceError): first.value = 1
        with self.assertRaisesRegex(TypeError, "immutable supported"):
            Measurement(identifier("measurement", "bad"), MeasurementKind.COUNT, [], (self.observation.identity,), "counter")

    def test_provenance_and_set_duplicate_rejection(self):
        evidence = EvidenceReference(EvidenceKind.MANUAL_SOURCE, "input")
        measurement = Measurement(identifier("measurement", "count"), MeasurementKind.COUNT, 1, (self.observation.identity,), "counter", (evidence,))
        self.assertEqual(measurement.evidence, (evidence,))
        self.assertEqual(measurement.observation_references, (self.observation.identity,))
        second = Measurement(identifier("measurement", "second"), MeasurementKind.ATTRIBUTE, "x", (self.observation.identity,), "counter")
        measurement_set = MeasurementSet(identifier("measurement-set", "ordered"), (second, measurement), (self.observation.identity,), "counter")
        self.assertEqual(tuple(measurement_set), (second, measurement))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            MeasurementSet(identifier("measurement-set", "bad"), (measurement, measurement), (self.observation.identity,), "counter")

    def test_registry_is_exact_and_insertion_ordered(self):
        dimensions = measure_dimensions(self.frame); bounds = measure_bounds(self.frame)
        registry = MeasurementRegistry(); registry.register(bounds); registry.register(dimensions)
        self.assertEqual(registry.all(), (bounds, dimensions))
        self.assertEqual(registry.get(dimensions.identity), dimensions)
        self.assertEqual(registry.by_kind(MeasurementKind.BOUND), (bounds,))
        self.assertEqual(registry.by_capability("measure_dimensions"), (dimensions,))
        self.assertEqual(registry.by_observation(self.observation.identity), (bounds, dimensions))
        with self.assertRaisesRegex(ValueError, "already registered"): registry.register(bounds)

    def test_capabilities_compute_properties_and_execution_records_them(self):
        self.assertEqual(measure_dimensions(self.frame).value["width"], 3)
        self.assertEqual(measure_dimensions(self.frame).value["height"], 2)
        self.assertEqual(measure_bounds(self.frame).value["row_max"], 1)
        self.assertEqual(measure_observation_count(self.frame).value, 1)
        memory = Memory(); memory.remember_capability(Capability("measure_dimensions", "Measure dimensions.", measure_dimensions))
        workspace = Executive(memory).solve(self.frame, "measure_dimensions")
        self.assertEqual(workspace.measurements.all(), (workspace.result,))
        self.assertEqual([event.kind.value for event in workspace.trace], [
            "observation.frame.received", "observation.registered", "capability.retrieved",
            "measurement.created", "measurement.recorded", "execution.succeeded", "memory.recorded"])


if __name__ == "__main__": unittest.main()
