"""Deterministic local benchmarking for standalone and aggregate ARC tasks."""
from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any, Iterable

from .arc_corpus import ArcCorpusTask, load_official_corpus
from .solver import SearchConfig, SolverResult, solve_task
from .tasks import Task, load_task


def _shape(grid: tuple[tuple[Any, ...], ...]) -> tuple[int, int]: return len(grid), len(grid[0])


def evaluate_predictions(predictions: tuple[Any, ...], expected: tuple[Any, ...]) -> dict[str, Any]:
    """Evaluate only after solve; cardinality is part of task-level exactness."""
    missing_expected = any(item is None for item in expected)
    exact_outputs = wrong_dimensions = incorrect_cells = 0
    for predicted, wanted in zip(predictions, expected):
        if wanted is None:
            continue
        if _shape(predicted) != _shape(wanted):
            wrong_dimensions += 1
        else:
            bad = sum(a != b for left, right in zip(predicted, wanted) for a, b in zip(left, right))
            incorrect_cells += bad
            exact_outputs += int(bad == 0)
    complete = bool(expected) and len(predictions) == len(expected) and not missing_expected
    return {"expected_outputs": len(expected), "predicted_outputs": len(predictions),
            "individual_exact_outputs": exact_outputs, "wrong_dimension_outputs": wrong_dimensions,
            "incorrect_cells": incorrect_cells, "complete_prediction_set": complete,
            "task_exact": complete and exact_outputs == len(expected)}


def _filter(records: Iterable[ArcCorpusTask], name: str) -> list[ArcCorpusTask]:
    def relation(record: ArcCorpusTask) -> str:
        pairs = record.public_task.training_pairs
        signs = {(_shape(p.output_grid.raw_grid) > _shape(p.input_grid.raw_grid)) - (_shape(p.output_grid.raw_grid) < _shape(p.input_grid.raw_grid)) for p in pairs}
        return "dimension-preserving" if signs == {0} else "output-smaller" if signs == {-1} else "output-larger" if signs == {1} else "mixed"
    accepted = {"all", "dimension-preserving", "output-smaller", "output-larger", "dimension-changing"}
    if name not in accepted: raise ValueError(f"unknown filter: {name}")
    return [record for record in records if name == "all" or (relation(record) != "dimension-preserving" if name == "dimension-changing" else relation(record) == name)]


def _result_row(task_id: str, result: SolverResult, expected: tuple[Any, ...], seconds: float) -> dict[str, Any]:
    score = evaluate_predictions(result.predictions, expected)
    return {"task_id": task_id, "internal_name": result.task_identifier, "status": result.status,
            "failure_reason": result.failure_reason, "candidates_explored": result.candidates_explored,
            "solve_seconds": seconds, "selected_program": result.selected_program.canonical if result.selected_program else None,
            "program_depth": result.selected_program.depth if result.selected_program else None,
            "operation_families": list(result.selected_program.families) if result.selected_program else [],
            "telemetry": result.telemetry, **score}


def run_official(records: Iterable[ArcCorpusTask], config: SearchConfig, *, include_rejections: bool = False, progress: bool = False, fail_fast: bool = False) -> dict[str, Any]:
    """Solve public tasks and evaluate private records only after return."""
    rows: list[dict[str, Any]] = []
    for position, record in enumerate(records, 1):
        start = perf_counter()
        try:
            # Deliberately pass exactly the public task, not a merged task.
            result = solve_task(record.public_task, config=config)
            row = _result_row(record.external_id, result, record.evaluation.expected_outputs, perf_counter() - start)
            if include_rejections:
                row["rejections"] = [{"program": item.program.canonical, "reason": item.reason, "pair": item.pair_index} for item in result.rejected]
        except Exception as error:  # Benchmark records failures rather than hiding them.
            row = {"task_id": record.external_id, "internal_name": record.internal_name, "status": "exception", "failure_reason": str(error), "solve_seconds": perf_counter() - start, "candidates_explored": 0, "expected_outputs": len(record.evaluation.expected_outputs), "predicted_outputs": 0, "individual_exact_outputs": 0, "wrong_dimension_outputs": 0, "incorrect_cells": 0, "complete_prediction_set": False, "task_exact": False, "selected_program": None, "program_depth": None, "operation_families": []}
            if fail_fast: raise
        rows.append(row)
        if progress: print(f"[{position}] {record.external_id}: {row['status']}")
    return _report(rows, config)


def _report(rows: list[dict[str, Any]], config: SearchConfig) -> dict[str, Any]:
    statuses, failures = Counter(row["status"] for row in rows), Counter(row.get("failure_reason") or "none" for row in rows)
    times, candidates = [row["solve_seconds"] for row in rows], [row["candidates_explored"] for row in rows]
    expected, predicted, exact = (sum(row[key] for row in rows) for key in ("expected_outputs", "predicted_outputs", "individual_exact_outputs"))
    summary = {"tasks_discovered": len(rows), "tasks_attempted": len(rows), "valid_tasks": len(rows) - statuses["exception"] - statuses["invalid"], "invalid_tasks": statuses["invalid"], "tasks_with_prediction": sum(row["predicted_outputs"] > 0 for row in rows), "tasks_with_complete_prediction_sets": sum(row["complete_prediction_set"] for row in rows), "task_level_exact_solves": sum(row["task_exact"] for row in rows), "individual_test_outputs_expected": expected, "individual_test_outputs_predicted": predicted, "individual_exact_test_outputs": exact, "no_prediction_tasks": sum(row["predicted_outputs"] == 0 for row in rows), "incomplete_prediction_tasks": sum(row["predicted_outputs"] != row["expected_outputs"] for row in rows), "wrong_dimension_outputs": sum(row["wrong_dimension_outputs"] for row in rows), "incorrect_cell_outputs": sum(row["incorrect_cells"] > 0 for row in rows), "timeout_count": 0, "exception_count": statuses["exception"], "task_level_exact_percentage": 100 * sum(row["task_exact"] for row in rows) / len(rows) if rows else 0.0, "individual_exact_output_percentage": 100 * exact / expected if expected else 0.0, "status_distribution": dict(sorted(statuses.items())), "failure_reason_distribution": dict(sorted(failures.items())), "program_depth_distribution": dict(sorted(Counter(str(row["program_depth"]) for row in rows if row["program_depth"] is not None).items())), "selected_program_distribution": dict(sorted(Counter(" -> ".join(row["operation_families"]) for row in rows if row["operation_families"]).items())), "candidate_count_statistics": {"total": sum(candidates), "mean": mean(candidates) if candidates else 0, "max": max(candidates, default=0)}, "solve_time_statistics": {"total_seconds": sum(times), "mean_seconds": mean(times) if times else 0, "max_seconds": max(times, default=0)}, "ambiguity_statistics": {"multiple_exact_hypotheses": statuses["multiple_exact_hypotheses"]}, "effective_search_config": config.__dict__}
    # Legacy name now has its literal meaning, individual outputs, not tasks.
    summary["exact_test_outputs"] = exact
    # Top-level alias preserves the original machine-readable entry point;
    # unlike the former implementation it now literally counts outputs.
    return {"schema_version": 2, "summary": summary, "tasks": rows, "exact_test_outputs": exact}


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str), encoding="utf-8")
    os.replace(temporary, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark public ARC tasks without exposing evaluator labels to the solver.")
    parser.add_argument("path", nargs="?", help="Standalone task JSON or directory (legacy mode).")
    parser.add_argument("--challenges", type=Path); parser.add_argument("--solutions", type=Path)
    parser.add_argument("--validate-only", action="store_true"); parser.add_argument("--max-depth", type=int, default=2); parser.add_argument("--max-candidates", type=int, default=512); parser.add_argument("--max-prefix-states", type=int, default=128); parser.add_argument("--max-displacement", type=int, default=2)
    parser.add_argument("--limit", type=int); parser.add_argument("--task-id", action="append", default=[]); parser.add_argument("--filter", default="all"); parser.add_argument("--include-rejections", "--show-rejections", action="store_true"); parser.add_argument("--fail-fast", action="store_true"); parser.add_argument("--progress", action="store_true"); parser.add_argument("--quiet", action="store_true"); parser.add_argument("--json", action="store_true"); parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if bool(args.challenges) != bool(args.solutions): parser.error("--challenges and --solutions must be supplied together")
    config = SearchConfig(args.max_depth, args.max_candidates, args.max_prefix_states, args.max_displacement)
    if args.challenges:
        records = _filter(load_official_corpus(args.challenges, args.solutions), args.filter)
        if args.task_id: records = [record for record in records if record.external_id in set(args.task_id)]
        if args.limit is not None: records = records[:args.limit]
        if args.validate_only:
            payload = {"valid": True, "tasks": len(records)}
        else: payload = run_official(records, config, include_rejections=args.include_rejections, progress=args.progress, fail_fast=args.fail_fast)
    elif args.path:
        files = [Path(args.path)] if Path(args.path).is_file() else sorted(Path(args.path).rglob("*.json"))
        rows=[]
        for file in files:
            data = json.loads(file.read_text(encoding="utf-8"))
            labelled = load_task(data, file.stem, str(file)); expected = tuple(x.raw_grid for x in labelled.expected_outputs if x is not None)
            public_data = {"train": data["train"], "test": [{"input": item["input"]} for item in data["test"]]}
            result = solve_task(load_task(public_data, file.stem, str(file)), config=config)
            rows.append(_result_row(str(file), result, expected, 0.0))
        payload = _report(rows, config)
    else: parser.error("provide PATH or both --challenges and --solutions")
    if args.output: _atomic_json(args.output, payload)
    if not args.quiet: print(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str) if args.json else json.dumps(payload.get("summary", payload), indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__": raise SystemExit(main())
