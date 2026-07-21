import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from renegade.generate import generate_task, main, serialize_generated, validate_generated
from renegade.solver import execute, solve_task


class SyntheticGeneratorTests(unittest.TestCase):
    def test_seed_is_reproducible_and_program_replays_every_label(self):
        first = generate_task(seed=42, difficulty=3)
        second = generate_task(seed=42, difficulty=3)
        self.assertEqual(serialize_generated(first), serialize_generated(second))
        validate_generated(first.task, first.program)
        for pair in first.task.training_pairs:
            self.assertEqual(execute(first.program, pair.input_grid.raw_grid), pair.output_grid.raw_grid)
        self.assertEqual(execute(first.program, first.task.test_input.raw_grid), first.task.expected_output.raw_grid)

    def test_difficulty_controls_shared_program_depth_and_rejects_invalid_values(self):
        self.assertEqual(len(generate_task(seed=3, difficulty=1).program.operations), 1)
        self.assertEqual(len(generate_task(seed=3, difficulty=3).program.operations), 3)
        self.assertEqual(len(generate_task(seed=3, difficulty=7).program.operations), 3)
        with self.assertRaises(ValueError):
            generate_task(seed=1, difficulty=0)

    def test_serialization_and_cli_export_are_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(main(["--count", "2", "--difficulty", "2", "--seed", "8", "--output", directory]), 0)
            files = sorted(Path(directory).glob("*.json"))
            self.assertEqual(len(files), 2)
            data = json.loads(files[0].read_text())
            self.assertIn("metadata", data)
            self.assertEqual(data["metadata"]["generator"], "renegade.generate")
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["--seed", "5"]), 0)
        self.assertEqual(json.loads(out.getvalue())[0], serialize_generated(generate_task(seed=5)))

    def test_task_uses_the_shared_solver_language(self):
        generated = generate_task(seed=0, difficulty=1)
        self.assertTrue(all(operation.kind in {"rotate", "reflect", "recolor", "translate"} for operation in generated.program.operations))
        result = solve_task(generated.task)
        self.assertEqual(result.predictions[0], generated.task.expected_output.raw_grid)


if __name__ == "__main__":
    unittest.main()
