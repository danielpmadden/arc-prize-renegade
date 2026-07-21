"""Compare two deterministic benchmark JSON reports."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare two Renegade benchmark reports.")
    parser.add_argument("before", type=Path); parser.add_argument("after", type=Path); parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    left, right = (json.loads(path.read_text(encoding="utf-8")) for path in (args.before, args.after))
    a, b = {x["task_id"]: x for x in left["tasks"]}, {x["task_id"]: x for x in right["tasks"]}
    common = sorted(set(a) & set(b))
    payload = {"task_level_exact_delta": right["summary"]["task_level_exact_solves"] - left["summary"]["task_level_exact_solves"], "individual_exact_output_delta": right["summary"]["individual_exact_test_outputs"] - left["summary"]["individual_exact_test_outputs"], "newly_solved_task_ids": [key for key in common if not a[key]["task_exact"] and b[key]["task_exact"]], "regressed_task_ids": [key for key in common if a[key]["task_exact"] and not b[key]["task_exact"]], "newly_predicted_incorrect_task_ids": [key for key in common if a[key]["predicted_outputs"] == 0 and b[key]["predicted_outputs"] and not b[key]["task_exact"]], "changed_selected_program_task_ids": [key for key in common if a[key]["selected_program"] != b[key]["selected_program"]], "runtime_delta_seconds": right["summary"]["solve_time_statistics"]["total_seconds"] - left["summary"]["solve_time_statistics"]["total_seconds"], "candidate_count_delta": right["summary"]["candidate_count_statistics"]["total"] - left["summary"]["candidate_count_statistics"]["total"], "status_distribution_before": left["summary"]["status_distribution"], "status_distribution_after": right["summary"]["status_distribution"]}
    print(json.dumps(payload, sort_keys=True) if args.json else json.dumps(payload, indent=2, sort_keys=True)); return 0
if __name__ == "__main__": raise SystemExit(main())
