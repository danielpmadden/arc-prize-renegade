"""Authoritative deterministic synthetic ARC-shaped task generator.

Private provenance is deliberately separate from :meth:`public_json`; callers
must explicitly request private metadata or hidden labels for evaluation.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from random import Random
from typing import Any

from .solver import Grid, Operation, Program, execute
from .tasks import Task, load_task

DIFFICULTIES = {
    1: {"depth": 1, "families": ("recolor", "rotate", "reflect", "translate"), "size": (4, 7)},
    2: {"depth": 2, "families": ("recolor",), "size": (5, 8)},
    3: {"depth": 3, "families": ("recolor", "reflect"), "size": (6, 9)},
}


def canonical_hash(value: Any) -> str:
    """SHA-256 over canonical JSON, used only as a reproducible corpus key."""
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _json_grid(grid: Grid) -> list[list[Any]]:
    return [list(row) for row in grid]


@dataclass(frozen=True)
class GeneratedTask:
    """A generated task, private program, and bounded-generation evidence."""
    task: Task
    seed: int
    difficulty: int
    program: Program
    metadata: tuple[tuple[str, Any], ...]

    def public_json(self) -> dict[str, Any]:
        """Canonical public ARC JSON. Test labels and all provenance are absent."""
        return {"train": [{"input": _json_grid(p.input_grid.raw_grid), "output": _json_grid(p.output_grid.raw_grid)} for p in self.task.training_pairs],
                "test": [{"input": _json_grid(g.raw_grid)} for g in self.task.test_inputs]}

    def task_json(self) -> dict[str, Any]:
        """Backward-compatible alias for the public serialization."""
        return self.public_json()

    def private_json(self) -> dict[str, Any]:
        """Private sidecar including hidden labels; never pass this to a solver."""
        return {"task_id": self.task.identifier, "seed": self.seed, "difficulty": self.difficulty,
                "program": self.program.canonical, "hidden_test_outputs": [_json_grid(g.raw_grid) for g in self.task.expected_outputs if g is not None],
                **dict(self.metadata)}

    def metadata_json(self) -> dict[str, Any]:
        """Compatibility name for private sidecar serialization."""
        return self.private_json()

    @property
    def public_hash(self) -> str: return canonical_hash(self.public_json())
    @property
    def program_hash(self) -> str: return canonical_hash({"program": self.program.canonical})


def difficulty_spec(level: int) -> dict[str, Any]:
    if level not in DIFFICULTIES:
        raise ValueError(f"unsupported difficulty {level}; supported values are 1, 2, 3")
    return dict(DIFFICULTIES[level])


def _world(random: Random, level: int) -> Grid:
    low, high = DIFFICULTIES[level]["size"]
    height, width = random.randint(low, high), random.randint(low, high)
    grid = [[0] * width for _ in range(height)]
    # 1 is mandatory so both recolors in composed programs are effective.
    grid[random.randrange(height)][random.randrange(width)] = 1
    for _ in range(random.randint(level + 2, max(level + 2, height * width // 3))):
        r, c = random.randrange(height), random.randrange(width)
        grid[r][c] = random.choice((1, 1, 1, 4, 5, 6))
    return tuple(tuple(row) for row in grid)


def _program(random: Random, level: int) -> Program:
    if level == 1:
        choice = random.choice(("recolor", "rotate", "reflect", "translate"))
        if choice == "recolor": return Program((Operation.make("recolor", mapping=((1, 2),)),))
        if choice == "rotate": return Program((Operation.make("rotate", turns=random.choice((1, 2, 3))),))
        if choice == "reflect": return Program((Operation.make("reflect", axis=random.choice(("horizontal", "vertical"))),))
        return Program((Operation.make("translate", offset=random.choice(((0, 1), (1, 0), (0, -1), (-1, 0))), background=0),))
    operations = [Operation.make("recolor", mapping=((1, 2),)), Operation.make("recolor", mapping=((2, 3),))]
    if level == 3: operations.append(Operation.make("reflect", axis=random.choice(("horizontal", "vertical"))))
    return Program(tuple(operations))


def _effective(program: Program, grid: Grid) -> bool:
    current = grid
    for operation in program.operations:
        following = execute(Program((operation,)), current)
        if following == current: return False
        current = following
    return True


def validate_generated(generated: GeneratedTask) -> None:
    """Verify replay and effective-operation invariants for every stored label."""
    for index, pair in enumerate(generated.task.training_pairs, 1):
        if execute(generated.program, pair.input_grid.raw_grid) != pair.output_grid.raw_grid:
            raise ValueError(f"generated program does not reproduce training pair {index}")
    for index, (source, expected) in enumerate(zip(generated.task.test_inputs, generated.task.expected_outputs), 1):
        if expected is None or execute(generated.program, source.raw_grid) != expected.raw_grid:
            raise ValueError(f"generated program does not reproduce test output {index}")


def generate_task(seed: int, *, difficulty: int = 1, training_pairs: int = 2, test_pairs: int = 1, max_attempts: int = 100) -> GeneratedTask:
    if not isinstance(seed, int): raise TypeError("seed must be an integer")
    difficulty_spec(difficulty)
    if training_pairs < 2 or test_pairs < 1: raise ValueError("generation requires at least two training and one test pair")
    if max_attempts < 1: raise ValueError("max_attempts must be positive")
    random = Random(seed)
    for attempt in range(1, max_attempts + 1):
        program = _program(random, difficulty)
        inputs = [_world(random, difficulty) for _ in range(training_pairs + test_pairs)]
        if not all(_effective(program, grid) for grid in inputs): continue
        data = {"train": [{"input": _json_grid(x), "output": _json_grid(execute(program, x))} for x in inputs[:training_pairs]],
                "test": [{"input": _json_grid(x), "output": _json_grid(execute(program, x))} for x in inputs[training_pairs:]]}
        generated = GeneratedTask(load_task(data, f"synthetic-{seed}-{difficulty}", "synthetic program-first generator"), seed, difficulty, program,
            (("program_depth", len(program.operations)), ("operations", tuple(x.kind for x in program.operations)),
             ("attempts", attempt), ("rejected_attempts", attempt - 1), ("training_pair_count", training_pairs), ("test_pair_count", test_pairs)))
        validate_generated(generated)
        return generated
    raise RuntimeError(f"generation exhausted {max_attempts} attempts without an effective task")


def generate_batch(seed: int, count: int, *, difficulty: int = 1, **configuration: Any) -> tuple[GeneratedTask, ...]:
    """Generate an ordered seeded batch. Seed ``seed + index`` identifies each task."""
    difficulty_spec(difficulty)
    if count < 0: raise ValueError("count must be non-negative")
    return tuple(generate_task(seed + index, difficulty=difficulty, **configuration) for index in range(count))
