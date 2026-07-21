import unittest

from renegade.scene import ObjectSelector, RelationKind, Scene, SelectorKind
from renegade.solver import SearchConfig, solve_task
from renegade.tasks import load_task


class SceneTests(unittest.TestCase):
    def test_components_descriptors_relations_and_render_are_deterministic(self):
        grid = ((0, 1, 1, 0, 2), (0, 1, 0, 0, 2), (0, 0, 0, 0, 2))
        scene = Scene.from_grid(grid)
        self.assertEqual(scene.render(), grid)
        self.assertEqual([obj.cell_count for obj in scene.objects], [3, 3])
        self.assertIsNone(ObjectSelector(SelectorKind.LARGEST).select(scene))
        self.assertEqual(ObjectSelector(SelectorKind.LEFTMOST).select(scene).color, 1)
        self.assertIn(RelationKind.LEFT_OF, [item.kind for item in scene.relations])

    def test_unique_object_extraction_is_fitted_and_composable(self):
        source = ((0, 1, 1, 0, 2), (0, 1, 0, 0, 2), (0, 0, 0, 0, 0))
        target = ((1, 1), (1, 0))
        task = load_task({"train": [{"input": source, "output": target}], "test": [{"input": source}]}, "object-extract")
        result = solve_task(task, config=SearchConfig(max_depth=2, max_candidates=512))
        self.assertEqual(result.predictions, (target,))
        self.assertIsNotNone(result.selected_program)
        self.assertIn("extract_object", result.selected_program.canonical)

if __name__ == "__main__":
    unittest.main()
