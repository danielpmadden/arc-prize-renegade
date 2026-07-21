import unittest

from renegade.composition_curriculum import evaluate_curriculum
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

    def test_registry_and_curriculum_are_deterministic(self):
        self.assertEqual(validate_registry()["operation_count"], 8)
        first, second = evaluate_curriculum(), evaluate_curriculum()
        self.assertEqual(first, second)
        self.assertEqual(first["solved"], first["case_count"])
        self.assertTrue(all(not row["telemetry"]["truncated"] for row in first["cases"]))

    def test_search_composes_existing_selection_operations(self):
        # The globally smallest object is a border distractor.  The desired
        # object can only be reached by composing interior then smallest.
        training = (
            (((1, 0, 0, 0, 0), (0, 2, 2, 0, 0), (0, 2, 0, 3, 0), (0, 0, 0, 0, 0)), ((3,),)),
            (((4, 0, 0, 0, 0), (0, 5, 5, 0, 0), (0, 5, 0, 6, 0), (0, 0, 0, 0, 0)), ((6,),)),
        )
        result = search(training, (((7, 0, 0, 0, 0), (0, 8, 8, 0, 0), (0, 8, 0, 9, 0), (0, 0, 0, 0, 0)),))
        self.assertIsNotNone(result.program)
        self.assertEqual(result.predictions, (((9,),),))
        self.assertIn("predicate='interior'", result.program.canonical)
        self.assertIn("predicate='smallest'", result.program.canonical)
