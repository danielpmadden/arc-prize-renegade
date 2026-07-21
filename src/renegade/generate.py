"""CLI for deterministic program-first synthetic tasks."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .generator import generate_batch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--difficulty", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        generated = generate_batch(args.seed, args.count, difficulty=args.difficulty)
    except (TypeError, ValueError) as error:
        parser.error(str(error))
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
        for item in generated:
            (args.output / f"{item.task.identifier}.json").write_text(json.dumps(item.task_json(), sort_keys=True), encoding="utf-8")
            (args.output / f"{item.task.identifier}.meta.json").write_text(json.dumps(item.metadata_json(), sort_keys=True), encoding="utf-8")
    payload = [{"task": item.task_json(), "metadata": item.metadata_json()} for item in generated]
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    else:
        for item in generated:
            print(f"{item.task.identifier}: {item.program.canonical} ({len(item.task.training_pairs)} training pairs)")
    return 0


if __name__ == "__main__":
    main()
