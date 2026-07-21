"""Deterministically characterize the existing structural pipeline; derive nothing."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Any

from .corpus import GOLDEN_GRIDS
from .diagnostics import summarize_pipeline
from .pipeline import inspect_grid
from .arc_corpus import load_official_corpus

BOUNDARY_CASES: tuple[tuple[str, object], ...] = (
    ("one_row", ((1, 0, 1, 0, 1),)),
    ("one_column", ((1,), (0,), (1,), (0,), (1,))),
    ("diagonal_contact", ((1, 0), (0, 2))),
    ("ragged_rows", ((1,), (1, 2))),
)


def normalized_snapshot(result: Any) -> dict[str, object]:
    """Return stable structural data already present in one pipeline result."""
    summary = asdict(summarize_pipeline(result))
    return {
        "grid": result.grid,
        "counts": summary,
        "percepts": [(item.kind.value, len(item.observation_references)) for item in (result.frame_percept,) + result.region_percepts],
        "relationships": [item.kind.value for item in result.relationships],
        "invariants": [item.kind.value for item in result.invariants],
        "archetypes": [item.kind.value for item in result.archetypes],
    }


def characterize_case(name: str, grid: object) -> dict[str, object]:
    """Execute and inspect one input, recording a deterministic failure if rejected."""
    dimensions = [len(grid), len(grid[0])] if isinstance(grid, tuple) and grid and isinstance(grid[0], tuple) else None
    try:
        result = inspect_grid(grid, name)
    except (TypeError, ValueError) as error:
        return {"case": name, "dimensions": dimensions, "status": "failed", "failure_reason": str(error)}
    counts = asdict(summarize_pipeline(result))
    return {
        "case": name, "dimensions": [len(result.grid), len(result.grid[0])], "status": "completed",
        **counts,
        "invariant_compression_ratio": round(counts["relationship_count"] / counts["invariant_count"], 6) if counts["invariant_count"] else None,
        "archetype_compression_ratio": round(counts["invariant_count"] / counts["archetype_count"], 6) if counts["archetype_count"] else None,
        "frame_associated": all(item.parent_frame == result.frame.identity for item in (result.frame_percept,) + result.region_percepts),
    }


def characterize() -> tuple[dict[str, object], ...]:
    cases = [(item.name, item.grid) for item in GOLDEN_GRIDS] + list(BOUNDARY_CASES)
    return tuple(characterize_case(name, grid) for name, grid in cases)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Characterize Renegade's implemented structural pipeline.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    parser.add_argument("--challenges", help="Official aggregate challenges JSON.")
    parser.add_argument("--solutions", help="Official aggregate solutions JSON (validation only).")
    parser.add_argument("--output", help="Optional JSON output path.")
    args = parser.parse_args(argv)
    if bool(args.challenges) != bool(args.solutions): parser.error("--challenges and --solutions must be supplied together")
    if args.challenges:
        corpus = load_official_corpus(args.challenges, args.solutions)
        relationships = []
        for item in corpus:
            signs = set()
            for pair in item.public_task.training_pairs:
                source, target = pair.input_grid.raw_grid, pair.output_grid.raw_grid
                output_shape, input_shape = (len(target), len(target[0])), (len(source), len(source[0]))
                signs.add(1 if output_shape > input_shape else -1 if output_shape < input_shape else 0)
            relationships.append("same" if signs == {0} else "smaller" if signs == {-1} else "larger" if signs == {1} else "mixed")
        records = {"task_count": len(corpus), "train_pair_count": sum(len(x.public_task.training_pairs) for x in corpus), "test_input_count": sum(len(x.public_task.test_inputs) for x in corpus), "multiple_test_input_tasks": sum(len(x.public_task.test_inputs) > 1 for x in corpus), "dimension_relationship_distribution": {name: relationships.count(name) for name in ("same", "smaller", "larger", "mixed")}, "dimension_preserving_tasks": relationships.count("same"), "consistently_shrinking_tasks": relationships.count("smaller"), "consistently_growing_tasks": relationships.count("larger"), "mixed_dimension_tasks": relationships.count("mixed")}
    else:
        records = characterize()
    if args.output:
        from pathlib import Path
        output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(records, sort_keys=True, separators=(",", ":"), default=list), encoding="utf-8")
    if args.json:
        print(json.dumps(records, sort_keys=True, separators=(",", ":"), default=list))
    else:
        for record in records:
            if record["status"] == "failed":
                print(f"{record['case']}: failed — {record['failure_reason']}")
            else:
                print("{case}: {dimensions}; observations={observation_count} measurements={measurement_count} percepts={percept_count} relationships={relationship_count} invariants={invariant_count} archetypes={archetype_count} events={execution_event_count} invariant_ratio={invariant_compression_ratio} archetype_ratio={archetype_compression_ratio}".format(**record))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
