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
        with self.assertRaises(ValueError):
            DEFAULT_REGISTRY.expression("related", (scene, unique), {"relation": "nearest"})

    def test_registry_and_curriculum_are_deterministic(self):
        self.assertEqual(validate_registry()["operation_count"], 9)
        first, second = evaluate_curriculum(), evaluate_curriculum()
        self.assertEqual(first, second)
        self.assertEqual(first["solved"], first["case_count"])
        self.assertTrue(all(not row["telemetry"]["truncated"] for row in first["cases"]))

    def test_relation_guided_selection_requires_unique_source_and_fits(self):
        root = DEFAULT_REGISTRY.expression("input")
        scene = DEFAULT_REGISTRY.expression("segment", (root,), {"background": 0, "connectivity": 4})
        objects = DEFAULT_REGISTRY.expression("objects", (scene,))
        source = DEFAULT_REGISTRY.expression("unique", (DEFAULT_REGISTRY.expression("filter", (objects,), {"predicate": "largest"}),))
        related = DEFAULT_REGISTRY.expression("related", (scene, source), {"relation": "left_of"})
        rendered = DEFAULT_REGISTRY.expression("render", (related, DEFAULT_REGISTRY.expression("canvas", (scene,), {"mode": "tight"})))
        self.assertEqual(evaluate(rendered, ((0, 1, 1, 0, 2),)), ((2,),))
        training = (
            (((0, 3, 3, 0, 1, 1, 1, 0, 2, 2, 0),), ((2, 2),)),
            (((0, 6, 6, 0, 4, 4, 4, 0, 5, 5, 0),), ((5, 5),)),
        )
        result = search(training, (((0, 8, 8, 0, 7, 7, 7, 0, 9, 9, 0),),), config=GrammarConfig(max_candidates=512))
        self.assertEqual(result.predictions, (((9, 9),),))
        self.assertIsNotNone(result.program)
        self.assertIn("related", result.program.canonical)
