"""Focused public-data tests for bounded compositional symbolic search."""
import unittest

from renegade.generator import generate_task
from renegade.solver import Operation, Program, SearchConfig, execute, solve_task
from renegade.tasks import load_task


class CompositionalSearchTests(unittest.TestCase):
    def public_result(self, item, *, depth=2):
        public = load_task(item.public_json(), item.task.identifier, "reparsed public test data")
        return solve_task(public, config=SearchConfig(max_depth=depth, max_candidates=512))

    def test_all_generator_depth_two_slots_construct_public_programs(self):
        slots = (
            ("recolor", "reflect"), ("recolor", "rotate"), ("recolor", "translate"),
            ("reflect", "recolor"), ("rotate", "recolor"), ("translate", "recolor"),
        )
        for seed, slot in enumerate(slots, 301):
            with self.subTest(slot=slot):
                item = generate_task(seed, difficulty=2, program_kinds=slot)
                result = self.public_result(item)
                self.assertTrue(result.predictions)
                self.assertEqual(result.predictions[0], item.task.expected_outputs[0].raw_grid)
                self.assertGreater(result.telemetry["depth_2_complete_programs_attempted"], 0)
                self.assertIsNotNone(result.selected_program)

    def test_depth_one_never_returns_composed_program(self):
        item = generate_task(401, difficulty=2, program_kinds=("recolor", "rotate"))
        result = self.public_result(item, depth=1)
        self.assertTrue(all(program.depth == 1 for program in result.validations))

    def test_non_generator_geometry_pairs_are_searched(self):
        # These direct public fixtures are not eligible generator templates.
        source = ((0, 0, 0, 0, 0), (0, 1, 2, 0, 0), (0, 3, 4, 0, 0), (0, 0, 0, 0, 0))
        cases = [
            ("translate-rotate", Program((Operation.make("translate", offset=(0, 1), background=0), Operation.make("rotate", turns=1)))),
            ("rotate-translate", Program((Operation.make("rotate", turns=1), Operation.make("translate", offset=(1, 0), background=0)))),
        ]
        for name, program in cases:
            with self.subTest(name=name):
                expected = execute(program, source)
                task = load_task({"train":[{"input":source,"output":expected}],"test":[{"input":source}]}, name)
                result = solve_task(task, max_depth=2)
                self.assertEqual(result.predictions[0], tuple(tuple(row) for row in expected))
                self.assertGreater(result.telemetry["depth_2_complete_programs_attempted"], 0)

    def test_depth_three_is_bounded_and_explicit(self):
        item = generate_task(501, difficulty=3, program_kinds=("recolor", "rotate", "recolor"))
        result = self.public_result(item, depth=3)
        self.assertLessEqual(result.candidates_explored, 512)
        self.assertGreater(result.telemetry["depth_3_prefixes_attempted"], 0)
        self.assertTrue(result.predictions)


if __name__ == "__main__":
    unittest.main()
