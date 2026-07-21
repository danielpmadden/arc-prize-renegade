import unittest

from renegade.composition_curriculum import evaluate_curriculum
from renegade.grammar import DEFAULT_REGISTRY, GrammarConfig, deserialize, evaluate, serialize, validate_registry


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

    def test_registry_and_curriculum_are_deterministic(self):
        self.assertEqual(validate_registry()["operation_count"], 8)
        first, second = evaluate_curriculum(), evaluate_curriculum()
        self.assertEqual(first, second)
        self.assertEqual(first["solved"], first["case_count"])
        self.assertTrue(all(not row["telemetry"]["truncated"] for row in first["cases"]))

