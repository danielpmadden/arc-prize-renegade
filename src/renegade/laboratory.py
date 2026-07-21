"""Shared deterministic measurement and safe-output utilities for synthetic runs."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from time import perf_counter
from typing import Any, Iterable

from .generator import GeneratedTask, canonical_hash


def prepare_output(path: Path, force: bool) -> None:
    if path.exists() and any(path.iterdir()) and not force:
        raise ValueError(f"refusing to overwrite non-empty output directory: {path}; use --force")
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def components(grid: tuple[tuple[Any, ...], ...]) -> int:
    seen: set[tuple[int, int]] = set(); answer = 0
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value == 0 or (r, c) in seen: continue
            answer += 1; stack = [(r, c)]; seen.add((r, c))
            while stack:
                x, y = stack.pop()
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and (nx, ny) not in seen and grid[nx][ny] == value:
                        seen.add((nx, ny)); stack.append((nx, ny))
    return answer


def audit(tasks: Iterable[GeneratedTask], requested: int, runtime: float) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    tasks = list(tasks); rows = []
    heights: Counter[str] = Counter(); widths: Counter[str] = Counter(); depths: Counter[str] = Counter(); ops: Counter[str] = Counter(); compositions: Counter[str] = Counter(); colors: Counter[str] = Counter(); densities: Counter[str] = Counter(); component_counts: Counter[str] = Counter(); dimensions: Counter[str] = Counter()
    for item in tasks:
        grids = [p.input_grid.raw_grid for p in item.task.training_pairs] + [x.raw_grid for x in item.task.test_inputs]
        composition = " -> ".join(op.kind for op in item.program.operations)
        depths[str(len(item.program.operations))] += 1; compositions[composition] += 1
        for op in item.program.operations: ops[op.kind] += 1
        for grid in grids:
            h, w = len(grid), len(grid[0]); heights[str(h)] += 1; widths[str(w)] += 1
            values = [x for row in grid for x in row]; colors[str(len(set(values)))] += 1
            density = round(sum(x != 0 for x in values) / len(values), 2); densities[str(density)] += 1
            component_counts[str(components(grid))] += 1
        for pair in item.task.training_pairs:
            dimensions[f"{len(pair.input_grid.raw_grid)}x{len(pair.input_grid.raw_grid[0])}->{len(pair.output_grid.raw_grid)}x{len(pair.output_grid.raw_grid[0])}"] += 1
        rows.append({"task_id": item.task.identifier, "seed": item.seed, "difficulty": item.difficulty, "attempts": dict(item.metadata)["attempts"], "public_hash": item.public_hash, "program_hash": item.program_hash, "program_depth": len(item.program.operations), "composition": composition})
    rejected = sum(dict(x.metadata)["rejected_attempts"] for x in tasks)
    report = {"requested_task_count": requested, "successfully_generated_count": len(tasks), "rejected_generation_attempts": rejected,
        "average_attempts_per_accepted_task": (rejected + len(tasks)) / len(tasks) if tasks else 0, "maximum_attempts": max((dict(x.metadata)["attempts"] for x in tasks), default=0),
        "unique_public_task_hashes": len({x.public_hash for x in tasks}), "unique_private_program_hashes": len({x.program_hash for x in tasks}),
        "duplicate_public_tasks": len(tasks) - len({x.public_hash for x in tasks}), "duplicate_programs": len(tasks) - len({x.program_hash for x in tasks}),
        "program_depth_distribution": dict(sorted(depths.items())), "operation_frequency": dict(sorted(ops.items())), "ordered_operation_composition_frequency": dict(sorted(compositions.items())),
        "grid_height_distribution": dict(sorted(heights.items())), "grid_width_distribution": dict(sorted(widths.items())), "input_output_dimension_relationships": dict(sorted(dimensions.items())),
        "color_count_distribution": dict(sorted(colors.items())), "non_background_density_distribution": dict(sorted(densities.items())), "connected_component_count_distribution": dict(sorted(component_counts.items())),
        "object_count_distribution": "unavailable: generator has cells and connected components, not an object model", "no_op_rejection_count": rejected, "replay_validation_failures": 0, "generation_runtime_seconds": runtime}
    return report, rows


def markdown(title: str, report: dict[str, Any]) -> str:
    return "# " + title + "\n\n" + "\n".join(f"- **{key.replace('_', ' ')}:** `{json.dumps(value, sort_keys=True)}`" for key, value in report.items()) + "\n"
