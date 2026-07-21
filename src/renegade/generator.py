"""Program-first, deterministic synthetic symbolic-task generation.

Generated inputs are new grids sampled from a seeded local PRNG.  Outputs are
always executions of :mod:`renegade.solver` programs; no ARC data is read,
embedded, or required.
"""
from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Any

from .solver import Grid, Operation, Program, execute
from .tasks import Task, load_task


@dataclass(frozen=True)
class GeneratedTask:
    """A canonical task plus private generation provenance and ground truth."""

    task: Task
    seed: int
    difficulty: int
    program: Program
    metadata: tuple[tuple[str, Any], ...]

    def task_json(self) -> dict[str, Any]:
        """Return canonical ARC-shaped data; it deliberately excludes metadata."""
        return {
            "train": [
                {"input": _json_grid(pair.input_grid.raw_grid), "output": _json_grid(pair.output_grid.raw_grid)}
                for pair in self.task.training_pairs
            ],
            "test": [
                {"input": _json_grid(grid.raw_grid), "output": _json_grid(expected.raw_grid)}
                for grid, expected in zip(self.task.test_inputs, self.task.expected_outputs)
            ],
        }

    def metadata_json(self) -> dict[str, Any]:
        """Return private provenance suitable for a sidecar file, never solver input."""
        return {
            "task_id": self.task.identifier,
            "seed": self.seed,
            "difficulty": self.difficulty,
            "program": self.program.canonical,
            **dict(self.metadata),
        }


def _json_grid(grid: Grid) -> list[list[Any]]:
    return [list(row) for row in grid]


def _world(random: Random, *, minimum_size: int = 4, background: int | None = None, required_color: int | None = None) -> Grid:
    """Make a non-degenerate rectangular grid with a variable background."""
    height, width = random.randint(minimum_size, 7), random.randint(minimum_size, 7)
    background = random.randrange(4) if background is None else background
    grid = [[background for _ in range(width)] for _ in range(height)]
    # At least two non-background cells avoids identity-only sparse worlds.
    color = (background + random.randint(1, 8)) % 10
    for _ in range(random.randint(2, max(2, height * width // 3))):
        row, column = random.randrange(height), random.randrange(width)
        grid[row][column] = color if random.random() < 0.75 else random.randrange(10)
    if required_color is not None:
        grid[random.randrange(height)][random.randrange(width)] = required_color
    return tuple(tuple(row) for row in grid)


def _recolor_program(random: Random, grid: Grid) -> Program:
    colors = sorted({cell for row in grid for cell in row}, key=repr)
    source = next((color for color in colors if color != grid[0][0]), colors[0])
    target = (int(source) + random.randint(1, 8)) % 10 if isinstance(source, int) else source
    return Program((Operation.make("recolor", mapping=((source, target),)),))


def _single_program(random: Random, grid: Grid) -> Program:
    """Choose only operations that can execute on every generated rectangular world."""
    choice = random.choice(("recolor", "rotate", "reflect", "translate"))
    if choice == "recolor":
        return _recolor_program(random, grid)
    if choice == "rotate":
        return Program((Operation.make("rotate", turns=random.choice((1, 2, 3))),))
    if choice == "reflect":
        return Program((Operation.make("reflect", axis=random.choice(("horizontal", "vertical"))),))
    background = max((cell for row in grid for cell in row), key=lambda value: sum(row.count(value) for row in grid))
    return Program((Operation.make("translate", offset=random.choice(((0, 1), (1, 0), (0, -1), (-1, 0))), background=background),))


def _program(random: Random, grid: Grid, difficulty: int) -> Program:
    depth = 1 if difficulty == 1 else min(difficulty, 3)
    operations: list[Operation] = []
    current = grid
    for _ in range(depth):
        operation = _single_program(random, current).operations[0]
        operations.append(operation)
        current = execute(Program((operation,)), current)
    return Program(tuple(operations))


def validate_generated(generated: GeneratedTask) -> None:
    """Fail explicitly if the private program cannot replay every stored example."""
    for index, pair in enumerate(generated.task.training_pairs, 1):
        if execute(generated.program, pair.input_grid.raw_grid) != pair.output_grid.raw_grid:
            raise ValueError(f"generated program does not reproduce training pair {index}")
    for index, (input_grid, output_grid) in enumerate(zip(generated.task.test_inputs, generated.task.expected_outputs), 1):
        if output_grid is None or execute(generated.program, input_grid.raw_grid) != output_grid.raw_grid:
            raise ValueError(f"generated program does not reproduce test output {index}")


def generate_task(seed: int, *, difficulty: int = 1, training_pairs: int = 2, test_pairs: int = 1) -> GeneratedTask:
    """Generate one reproducible program-first task with at least two examples."""
    if not isinstance(seed, int):
        raise TypeError("seed must be an integer")
    if not 1 <= difficulty <= 3:
        raise ValueError("difficulty must be between 1 and 3 in the current generator")
    if training_pairs < 2 or test_pairs < 1:
        raise ValueError("generation requires at least two training and one test pair")
    random = Random(seed)
    # Fix generation context first so every sampled world is compatible with the
    # same program rather than accidentally making later examples identity cases.
    mode = random.choice(("recolor", "rotate", "reflect", "translate"))
    if mode == "recolor":
        program = Program((Operation.make("recolor", mapping=((1, 2),)),))
        world_options = {"background": 0, "required_color": 1}
    elif mode == "translate":
        program = Program((Operation.make("translate", offset=random.choice(((0, 1), (1, 0), (0, -1), (-1, 0))), background=0),))
        world_options = {"background": 0, "required_color": 1}
    elif mode == "rotate":
        program = Program((Operation.make("rotate", turns=random.choice((1, 2, 3))),))
        world_options = {}
    else:
        program = Program((Operation.make("reflect", axis=random.choice(("horizontal", "vertical"))),))
        world_options = {}
    if difficulty > 1:
        # A compatible recolor makes a deterministic composition without a
        # second language or per-example parameter mutation.
        program = Program(program.operations + (Operation.make("recolor", mapping=((2, 3),)),))
        world_options = {**world_options, "required_color": 1}
    if difficulty > 2:
        program = Program(program.operations + (Operation.make("reflect", axis="vertical"),))
    inputs = [_world(random, **world_options) for _ in range(training_pairs + test_pairs)]
    data = {
        "train": [{"input": _json_grid(grid), "output": _json_grid(execute(program, grid))} for grid in inputs[:training_pairs]],
        "test": [{"input": _json_grid(grid), "output": _json_grid(execute(program, grid))} for grid in inputs[training_pairs:]],
    }
    operation_names = tuple(operation.kind for operation in program.operations)
    generated = GeneratedTask(
        task=load_task(data, f"synthetic-{seed}-{difficulty}", "synthetic program-first generator"), seed=seed,
        difficulty=difficulty, program=program,
        metadata=(("program_depth", len(program.operations)), ("operations", operation_names),
                  ("training_pair_count", training_pairs), ("test_pair_count", test_pairs),
                  ("grid_sizes", tuple((len(grid), len(grid[0])) for grid in inputs)),
                  ("color_count", len({cell for grid in inputs for row in grid for cell in row}))),
    )
    validate_generated(generated)
    return generated

def generate_batch(seed: int, count: int, *, difficulty: int = 1) -> tuple[GeneratedTask, ...]:
    """Generate deterministic unique-seed tasks without global generator state."""
    if count < 1:
        raise ValueError("count must be positive")
    return tuple(generate_task(seed + offset, difficulty=difficulty) for offset in range(count))
