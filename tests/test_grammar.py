import unittest

from renegade.composition_curriculum import cases, evaluate_curriculum
from renegade.grammar import DEFAULT_REGISTRY, GrammarConfig, deserialize, evaluate, search, serialize, validate_registry


class GrammarTests(unittest.TestCase):
    def test_expression_is_canonical_immutable_and_serializable(self):
        expression = DEFAULT_REGISTRY.expression("input")
        self.assertEqual(expression, deserialize(serialize(expression)))
        with self.assertRaises(Exception):
            expression.operation = "changed"

    def test_type_and_ambiguity_failures_are_explicit(self):
        root = DEFAULT_REGISTRY.expression("input")
        with self.assertRaises(TypeError):
            DEFAULT_REGISTRY.expression("objects", (root,))
        scene = DEFAULT_REGISTRY.expression("segment", (root,), {"background": 0, "connectivity": 4})
        objects = DEFAULT_REGISTRY.expression("objects", (scene,))
        unique = DEFAULT_REGISTRY.expression("unique", (objects,))
        with self.assertRaises(ValueError):
            evaluate(unique, ((0, 1, 0, 2),))
        with self.assertRaises(ValueError):
            DEFAULT_REGISTRY.expression("related", (scene, unique), {"relation": "nearest"})

    def test_registry_and_curriculum_are_deterministic(self):
        self.assertEqual(validate_registry()["operation_count"], 9)
        first, second = evaluate_curriculum(), evaluate_curriculum()
        self.assertEqual(first, second)
        self.assertEqual(first["solved"], first["case_count"])
        self.assertTrue(all(not row["telemetry"]["truncated"] for row in first["cases"]))

    def test_search_respects_the_configured_expression_depth(self):
        case = cases()[0]
        too_shallow = search(case.training, case.test_inputs, config=GrammarConfig(max_depth=4))
        sufficient = search(case.training, case.test_inputs, config=GrammarConfig(max_depth=5))
        self.assertIsNone(too_shallow.program)
        self.assertGreater(too_shallow.telemetry["depth_rejected"], 0)
        self.assertEqual(sufficient.predictions, case.expected)
