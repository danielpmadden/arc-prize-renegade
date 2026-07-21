from dataclasses import FrozenInstanceError
import unittest
from renegade import (Percept, PerceptKind, PerceptRegistry, PerceptSet, StableIdentifier,
                      form_connected_regions, inspect_grid)

def identity(category, name): return StableIdentifier(category, name, 1)

class PerceptTests(unittest.TestCase):
    def test_identity_set_and_registry(self):
        first = Percept(identity("percept", "one"), PerceptKind.REGION, "test", (identity("observation", "one"),))
        same = Percept(identity("percept", "one"), PerceptKind.FRAME, "other", (identity("observation", "two"),))
        self.assertEqual(first, same)
        with self.assertRaises(FrozenInstanceError): first.kind = PerceptKind.FRAME
        collection = PerceptSet(identity("percept-set", "one"), (first,), "test")
        self.assertEqual(tuple(collection), (first,))
        registry = PerceptRegistry(); registry.register(first)
        self.assertEqual(registry.by_kind(PerceptKind.REGION), (first,))
        self.assertEqual(registry.by_capability("test"), (first,))
        self.assertEqual(registry.by_observation(identity("observation", "one")), (first,))
        with self.assertRaisesRegex(ValueError, "already registered"): registry.register(same)

    def test_regions_are_complete_ordered_and_orthogonal(self):
        result = inspect_grid([[1, 0, 1], [0, 0, 0], [1, 0, 1]])
        self.assertEqual(len(result.region_percepts), 5)
        self.assertEqual([len(item.observation_references) for item in result.region_percepts], [1, 5, 1, 1, 1])
        self.assertEqual(sum(len(item.observation_references) for item in result.region_percepts), 9)
        checkerboard = inspect_grid([[1, 0, 1], [0, 1, 0], [1, 0, 1]])
        self.assertEqual(len(checkerboard.region_percepts), 9)
        self.assertEqual(inspect_grid((("a", "a"), ("b", "b"))).grid, (("a", "a"), ("b", "b")))

    def test_invalid_grid_is_explicit(self):
        for value in ([], [[]], [[1], [1, 2]], {"x": 1}):
            with self.assertRaises((TypeError, ValueError)): inspect_grid(value)

    def test_pipeline_layers_and_events(self):
        result = inspect_grid([[1]])
        self.assertEqual(len(result.observations), 1); self.assertEqual(len(result.measurements), 3)
        self.assertEqual(len(result.region_percepts), 1)
        self.assertIn("percept.created", [event.kind.value for event in result.trace])

if __name__ == "__main__": unittest.main()
