"""Validated, evaluator-private loading of official aggregate ARC corpora.

The public task passed to the solver deliberately has no expected outputs.
Evaluation labels remain in :class:`ArcEvaluationRecord` until after solving.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .tasks import Task, load_task

_LOCAL_NAME = re.compile(r"^[a-z][a-z0-9_-]*$")


def internal_name(external_id: str) -> str:
    """Return a deterministic valid local name without changing ARC provenance."""
    if not isinstance(external_id, str) or not external_id:
        raise ValueError("ARC task ID must be a non-empty string")
    candidate = re.sub(r"[^a-z0-9_-]", "_", external_id.lower())
    if _LOCAL_NAME.fullmatch(candidate):
        return candidate
    # ARC IDs are normally hexadecimal, but encoding makes this boundary safe
    # for all non-empty external identifiers and avoids normalization collisions.
    # Prefixing is reversible for the ARC-style numeric IDs and makes the
    # local-name boundary explicit.  Escaping is retained only for unusual
    # external punctuation, so valid local names are never weakened.
    return "arc_" + candidate


@dataclass(frozen=True)
class ArcEvaluationRecord:
    """Private expected outputs, never embedded in the public :class:`Task`."""

    external_id: str
    expected_outputs: tuple[tuple[tuple[int, ...], ...], ...]


@dataclass(frozen=True)
class ArcCorpusTask:
    """One public solve task and its separate evaluator-private record."""

    external_id: str
    internal_name: str
    public_task: Task
    evaluation: ArcEvaluationRecord


def _read_mapping(path: str | Path) -> Mapping[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must contain an object mapping task IDs")
    return value


def _grid(value: Any, label: str) -> tuple[tuple[int, ...], ...]:
    if not isinstance(value, list) or not value or not all(isinstance(row, list) and row for row in value):
        raise ValueError(f"{label} must be a non-empty rectangular grid")
    width = len(value[0])
    if any(len(row) != width for row in value):
        raise ValueError(f"{label} must be rectangular")
    if any(not isinstance(cell, int) or not 0 <= cell <= 9 for row in value for cell in row):
        raise ValueError(f"{label} contains a non-ARC color")
    return tuple(tuple(row) for row in value)


def load_official_corpus(challenges_path: str | Path, solutions_path: str | Path) -> tuple[ArcCorpusTask, ...]:
    """Load aggregate files, validate them, and return deterministic ID order."""
    challenges, solutions = _read_mapping(challenges_path), _read_mapping(solutions_path)
    challenge_ids, solution_ids = set(challenges), set(solutions)
    if challenge_ids != solution_ids:
        missing, extra = sorted(challenge_ids - solution_ids), sorted(solution_ids - challenge_ids)
        raise ValueError(f"challenge/solution task ID mismatch; missing solutions={missing}; extra solutions={extra}")
    records: list[ArcCorpusTask] = []
    for external_id in sorted(challenge_ids):
        data, labels = challenges[external_id], solutions[external_id]
        if not isinstance(data, Mapping) or set(data) != {"train", "test"}:
            raise ValueError(f"{external_id}: challenge must contain exactly train and test")
        if not isinstance(labels, list):
            raise ValueError(f"{external_id}: solutions must be an array")
        if len(data["test"]) != len(labels):
            raise ValueError(f"{external_id}: test-input/test-output count mismatch")
        for group in ("train", "test"):
            if not isinstance(data[group], list) or not data[group]:
                raise ValueError(f"{external_id}: {group} must be a non-empty array")
        for index, pair in enumerate(data["train"]):
            if not isinstance(pair, Mapping) or set(pair) != {"input", "output"}:
                raise ValueError(f"{external_id}: malformed train[{index}]")
            _grid(pair["input"], f"{external_id} train[{index}] input")
            _grid(pair["output"], f"{external_id} train[{index}] output")
        for index, item in enumerate(data["test"]):
            if not isinstance(item, Mapping) or set(item) != {"input"}:
                raise ValueError(f"{external_id}: malformed test[{index}]")
            _grid(item["input"], f"{external_id} test[{index}] input")
        expected = tuple(_grid(grid, f"{external_id} solution[{index}]") for index, grid in enumerate(labels))
        name = internal_name(external_id)
        public = load_task(data, name, f"official ARC challenges: {challenges_path}")
        records.append(ArcCorpusTask(external_id, name, public, ArcEvaluationRecord(external_id, expected)))
    return tuple(records)
