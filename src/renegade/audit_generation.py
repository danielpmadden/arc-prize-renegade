"""Generate and measure a deterministic synthetic corpus."""
from __future__ import annotations
import argparse
from pathlib import Path
from time import perf_counter
from .generator import generate_batch
from .laboratory import audit, markdown, prepare_output, write_csv, write_json

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--count", type=int, required=True); parser.add_argument("--difficulty", type=int, required=True); parser.add_argument("--seed", type=int, required=True); parser.add_argument("--output", type=Path, required=True); parser.add_argument("--progress-interval", type=int, default=100); parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.progress_interval < 1: parser.error("progress interval must be positive")
    try: prepare_output(args.output, args.force); start = perf_counter(); tasks = generate_batch(args.seed, args.count, difficulty=args.difficulty); elapsed = perf_counter() - start
    except (ValueError, TypeError, RuntimeError) as error: parser.error(str(error))
    for index in range(args.progress_interval, len(tasks) + 1, args.progress_interval): print(f"generated {index}/{len(tasks)}")
    report, rows = audit(tasks, args.count, elapsed); write_json(args.output / "audit.json", report); (args.output / "audit.md").write_text(markdown("Synthetic generation audit", report), encoding="utf-8")
    write_csv(args.output / "tasks.csv", rows, ["task_id", "seed", "difficulty", "attempts", "public_hash", "program_hash", "program_depth", "composition"])
    write_csv(args.output / "operations.csv", [{"operation": k, "count": v} for k, v in report["operation_frequency"].items()], ["operation", "count"])
    write_csv(args.output / "compositions.csv", [{"composition": k, "count": v} for k, v in report["ordered_operation_composition_frequency"].items()], ["composition", "count"])
    print(f"wrote {args.output / 'audit.json'}"); return 0
if __name__ == "__main__": raise SystemExit(main())
