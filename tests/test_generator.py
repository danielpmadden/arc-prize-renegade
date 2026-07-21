import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from renegade import execute, generate_batch, generate_task, solve_task, validate_generated
from renegade.generate import main

class GeneratorTests(unittest.TestCase):
    def test_seed_replay_and_program_replay(self):
        first, second = generate_task(42, difficulty=2), generate_task(42, difficulty=2)
        self.assertEqual(first, second)
        validate_generated(first)
        for pair in first.task.training_pairs:
            self.assertEqual(execute(first.program, pair.input_grid.raw_grid), pair.output_grid.raw_grid)
        self.assertEqual(first.metadata_json()["program_depth"], 2)

    def test_difficulty_batch_and_canonical_task_serialization(self):
        batch = generate_batch(9, 4, difficulty=3)
        self.assertEqual([item.seed for item in batch], [9, 10, 11, 12])
        self.assertTrue(all(len(item.program.operations) == 3 for item in batch))
        payload = batch[0].task_json()
        self.assertEqual(set(payload), {"train", "test"})
        self.assertEqual(len(payload["train"]), 2)
        self.assertNotIn("output", payload["test"][0])

    def test_cli_writes_reproducible_task_and_private_sidecar(self):
        with tempfile.TemporaryDirectory() as directory:
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["--seed", "3", "--count", "2", "--difficulty", "2", "--output", directory, "--json"]), 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(len(payload), 2)
            files = sorted(Path(directory).glob("*.json"))
            self.assertEqual(len(files), 4)
            self.assertNotIn("metadata", json.loads(Path(directory, "synthetic-3-2.json").read_text()))

    def test_level_one_recolor_is_solver_compatible(self):
        generated = generate_task(2)
        result = solve_task(generated.task)
        self.assertTrue(result.predictions)
        self.assertEqual(result.predictions[0], generated.task.expected_outputs[0].raw_grid)

    def test_invalid_arguments_are_rejected(self):
        with self.assertRaises(ValueError): generate_task(1, difficulty=4)
        self.assertEqual(generate_batch(1, 0), ())

class DiversityRegressionTests(unittest.TestCase):
    def test_balanced_coverage_prevents_recolor_collapse(self):
        from renegade.generator import eligible_program_kinds
        one = generate_batch(42, 12, difficulty=1, sampling="balanced")
        self.assertEqual({x.program.operations[0].kind for x in one}, {x[0] for x in eligible_program_kinds(1)})
        two = generate_batch(42, 24, difficulty=2, sampling="balanced")
        compositions = {tuple(op.kind for op in x.program.operations) for x in two}
        self.assertEqual(compositions, set(eligible_program_kinds(2)))
        self.assertTrue(any(a != b for a,b in compositions))
        self.assertTrue(all(len(x.program.operations) == 2 for x in two))
    def test_three_stage_programs_are_effective(self):
        for item in generate_batch(11, 9, difficulty=3, sampling="balanced"):
            validate_generated(item)
            self.assertEqual(len(item.program.operations), 3)
