"""Deterministic, program-first synthetic grid-task generation.

The generator deliberately has no dependency on ARC task files.  It samples a
bounded program from :mod:`renegade.solver`, constructs compatible symbolic
worlds, and executes that program to create every label.  Consequently the
stored solution is replayable rather than inferred from random I/O examples.
"""
from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .solver import Operation, Program, execute
from .tasks import Task, load_task

Grid = tuple[tuple[int, ...], ...]
_COLORS = tuple(range(1, 10))


@dataclass(frozen=True)
class GeneratedTask:
    """A generated task, its executable source program, and deterministic facts."""

    task: Task
    program: Program
    seed: int
    difficulty: int
    attempts: int


def _grid_json(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _world(rng: random.Random, difficulty: int, background: int) -> Grid:
    """Create a non-empty bounded scene with rectangular/cellular objects."""
    height = rng.randint(4, min(12, 6 + difficulty))
    width = rng.randint(4, min(12, 6 + difficulty))
    canvas = [[background for _ in range(width)] for _ in range(height)]
    object_count = rng.randint(1, min(1 + difficulty, 5))
    palette = [color for color in _COLORS if color != background]
    placed = 0
    for _ in range(object_count * 3):
        if placed >= object_count:
            break
        color = rng.choice(palette)
        object_height, object_width = rng.randint(1, min(3, height)), rng.randint(1, min(3, width))
        top, left = rng.randrange(height - object_height + 1), rng.randrange(width - object_width + 1)
        cells = [(r, c) for r in range(top, top + object_height) for c in range(left, left + object_width)]
        if any(canvas[r][c] != background for r, c in cells):
            continue
        # Sparse single-cell objects and filled rectangles are both intentional symbolic worlds.
        for r, c in cells:
            canvas[r][c] = color
        placed += 1
    if not placed:
        canvas[height // 2][width // 2] = palette[0]
    return tuple(tuple(row) for row in canvas)


def _program(rng: random.Random, difficulty: int, background: int) -> Program:
    """Sample a bounded composition from the solver's shared operation language."""
    depth = min(max(difficulty, 1), 3)
    choices = ("rotate", "reflect", "recolor", "translate")
    operations: list[Operation] = []
    for index in range(depth):
        kind = choices[(rng.randrange(len(choices)) + index) % len(choices)]
        if kind == "rotate":
            operations.append(Operation.make("rotate", turns=rng.choice((1, 2, 3))))
        elif kind == "reflect":
            operations.append(Operation.make("reflect", axis=rng.choice(("horizontal", "vertical"))))
        elif kind == "recolor":
            palette = [c for c in _COLORS if c != background]
            # Recolour every possible foreground value, so every non-empty world
            # demonstrates this step without encoding a world-specific answer.
            mapping = tuple((source, palette[(position + 1) % len(palette)]) for position, source in enumerate(palette))
            operations.append(Operation.make("recolor", mapping=mapping))
        else:
            operations.append(Operation.make("translate", offset=rng.choice(((-1, 0), (0, 1), (1, 0), (0, -1))), background=background))
    return Program(tuple(operations))


def _object_count(grid: Grid, background: int) -> int:
    """Count four-connected non-background components for descriptive metadata."""
    seen: set[tuple[int, int]] = set()
    count = 0
    for row, values in enumerate(grid):
        for column, value in enumerate(values):
            if value == background or (row, column) in seen:
                continue
            count += 1
            frontier = [(row, column)]
            seen.add((row, column))
            while frontier:
                current_row, current_column = frontier.pop()
                for next_row, next_column in ((current_row - 1, current_column), (current_row + 1, current_column), (current_row, current_column - 1), (current_row, current_column + 1)):
                    if 0 <= next_row < len(grid) and 0 <= next_column < len(grid[0]) and grid[next_row][next_column] != background and (next_row, next_column) not in seen:
                        seen.add((next_row, next_column))
                        frontier.append((next_row, next_column))
    return count


def validate_generated(task: Task, program: Program) -> None:
    """Raise if a task's labels do not exactly replay from its source program."""
    for index, pair in enumerate(task.training_pairs, 1):
        if execute(program, pair.input_grid.raw_grid) != pair.output_grid.raw_grid:
            raise ValueError(f"training pair {index} does not replay")
    for index, (source, expected) in enumerate(zip(task.test_inputs, task.expected_outputs), 1):
        if expected is None or execute(program, source.raw_grid) != expected.raw_grid:
            raise ValueError(f"test output {index} does not replay")


def generate_task(*, seed: int, difficulty: int = 1, training_count: int = 2) -> GeneratedTask:
    """Generate one reproducible task; rejection is bounded and explicit."""
    if not 1 <= difficulty <= 7:
        raise ValueError("difficulty must be in the inclusive range 1..7")
    if not 2 <= training_count <= 4:
        raise ValueError("training_count must be in the inclusive range 2..4")
    rng = random.Random(seed)
    for attempt in range(1, 65):
        background = rng.choice((0, 0, 0, rng.choice(_COLORS)))
        worlds = tuple(_world(rng, difficulty, background) for _ in range(training_count + 1))
        program = _program(rng, difficulty, background)
        outputs = tuple(execute(program, world) for world in worlds)
        # Avoid no-op samples: each demonstrated example must communicate a change.
        if any(source == result for source, result in zip(worlds, outputs)):
            continue
        identifier = f"synthetic-{seed:016x}-d{difficulty}"
        payload: dict[str, Any] = {
            "train": [{"input": _grid_json(source), "output": _grid_json(result)} for source, result in zip(worlds[:-1], outputs[:-1])],
            "test": [{"input": _grid_json(worlds[-1]), "output": _grid_json(outputs[-1])}],
        }
        task = load_task(payload, identifier, "renegade synthetic generator")
        input_colors = tuple(sorted({color for world in worlds for row in world for color in row}))
        grid_sizes = tuple((len(world), len(world[0])) for world in worlds)
        metadata = (("generator", "renegade.generate"), ("seed", seed), ("difficulty", difficulty),
                    ("program_depth", len(program.operations)), ("operations", tuple(op.kind for op in program.operations)),
                    ("program", program.canonical), ("training_count", training_count), ("object_count", tuple(_object_count(world, background) for world in worlds)),
                    ("grid_sizes", grid_sizes), ("color_count", len(input_colors)), ("generation_attempt", attempt))
        task = Task(task.identifier, task.provenance, task.training_pairs, task.test_inputs, task.expected_outputs, metadata)
        validate_generated(task, program)
        return GeneratedTask(task, program, seed, difficulty, attempt)
    raise RuntimeError("unable to generate a non-degenerate task within 64 attempts")


def serialize_generated(generated: GeneratedTask) -> dict[str, Any]:
    """Return stable JSON-ready data, including provenance-only generator metadata."""
    task = generated.task
    def json_value(value: Any) -> Any:
        if isinstance(value, tuple):
            return [json_value(item) for item in value]
        return value
    return {"train": [{"input": _grid_json(pair.input_grid.raw_grid), "output": _grid_json(pair.output_grid.raw_grid)} for pair in task.training_pairs],
            "test": [{"input": _grid_json(grid.raw_grid), "output": _grid_json(expected.raw_grid)} for grid, expected in zip(task.test_inputs, task.expected_outputs) if expected is not None],
            "metadata": {key: json_value(value) for key, value in task.metadata}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic synthetic symbolic grid tasks.")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--difficulty", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.count < 1:
        parser.error("--count must be positive")
    try:
        generated = [generate_task(seed=args.seed + index, difficulty=args.difficulty) for index in range(args.count)]
    except (ValueError, RuntimeError) as error:
        parser.error(str(error))
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
        for item in generated:
            (args.output / f"{item.task.identifier}.json").write_text(json.dumps(serialize_generated(item), sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    else:
        print(json.dumps([serialize_generated(item) for item in generated], sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
