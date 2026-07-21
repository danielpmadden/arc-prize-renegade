"""Run the current bounded solver against public synthetic task JSON only."""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
from statistics import median
from time import perf_counter
from .generator import generate_batch
from .laboratory import markdown, prepare_output, write_csv, write_json
from .solver import solve_task
from .tasks import load_task

def _percentile(values: list[float], fraction: float) -> float:
    if not values: return 0.0
    return sorted(values)[min(len(values) - 1, int((len(values) - 1) * fraction))]

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(); p.add_argument("--count", type=int, required=True); p.add_argument("--difficulty", type=int, required=True); p.add_argument("--seed", type=int, required=True); p.add_argument("--output", type=Path, required=True); p.add_argument("--progress-interval", type=int, default=100); p.add_argument("--force", action="store_true"); args = p.parse_args(argv)
    if args.progress_interval < 1: p.error("progress interval must be positive")
    try: prepare_output(args.output, args.force); begin = perf_counter(); generated = generate_batch(args.seed, args.count, difficulty=args.difficulty); generation_time = perf_counter() - begin
    except (ValueError, TypeError, RuntimeError) as error: p.error(str(error))
    rows=[]; failures=[]; solved=[]; unsolved=[]; timings=[]; reasons=Counter(); by_op=Counter(); by_composition=Counter(); by_depth=Counter(); by_size=Counter(); exact_outputs=incorrect_cells=wrong_dimension=exceptions=no_prediction=0
    start = perf_counter()
    for n, item in enumerate(generated, 1):
        # This is the boundary: a new Task is parsed only from public JSON.
        public = load_task(item.public_json(), item.task.identifier, "public synthetic JSON")
        t0 = perf_counter(); result = None; error = None
        try: result = solve_task(public)
        except Exception as caught: error = str(caught)
        elapsed = perf_counter() - t0; timings.append(elapsed)
        expected = [x.raw_grid for x in item.task.expected_outputs if x is not None]; predictions = list(result.predictions) if result else []
        task_correct = True; reason = "exact"
        if error: exceptions += 1; task_correct=False; reason="exception"
        elif not predictions: no_prediction += 1; task_correct=False; reason="no_prediction"
        else:
            for wanted, actual in zip(expected, predictions):
                if len(wanted) != len(actual) or len(wanted[0]) != len(actual[0]): wrong_dimension += 1; task_correct=False; reason="wrong_dimension"; continue
                bad=sum(a != b for ra, rb in zip(wanted, actual) for a, b in zip(ra, rb)); incorrect_cells += bad
                if bad: task_correct=False; reason="incorrect_cells"
                else: exact_outputs += 1
            if len(predictions) != len(expected): task_correct=False; reason="no_prediction"
        comp=" -> ".join(op.kind for op in item.program.operations); size=f"{len(item.task.test_inputs[0].raw_grid)}x{len(item.task.test_inputs[0].raw_grid[0])}"
        row={"task_id": item.task.identifier,"public_hash":item.public_hash,"difficulty":item.difficulty,"composition":comp,"program_depth":len(item.program.operations),"grid_size":size,"status":result.status if result else "exception","exact":task_correct,"exact_program": bool(result and result.selected_program and result.selected_program.canonical == item.program.canonical),"solve_seconds":f"{elapsed:.9f}","failure_reason":reason}; rows.append(row)
        for op in set(x.kind for x in item.program.operations): by_op[(op, "total")] += 1; by_op[(op, "success")] += task_correct
        for bucket, key in ((by_composition, comp), (by_depth, str(len(item.program.operations))), (by_size, size)): bucket[(key,"total")] += 1; bucket[(key,"success")] += task_correct
        if task_correct: solved.append(item.task.identifier)
        else: unsolved.append(item.task.identifier); reasons[reason] += 1; failures.append({**row,"error":error})
        if n % args.progress_interval == 0: print(f"solved {n}/{len(generated)}")
    solve_time=perf_counter()-start; task_correct=len(solved); total_outputs=sum(len(x.task.expected_outputs) for x in generated)
    def success(counter): return {key:{"success":counter[(key,"success")],"total":counter[(key,"total")]} for key,_ in sorted(counter) if _ == "total"}
    recovered = sum(row["exact_program"] for row in rows)
    report={"requested_task_count":args.count,"generated_task_count":len(generated),"exact_test_outputs_solved":exact_outputs,"total_test_outputs":total_outputs,"task_level_all_tests_correct_count":task_correct,"exact_output_percentage":100*exact_outputs/total_outputs if total_outputs else 0,"task_level_percentage":100*task_correct/len(generated) if generated else 0,"generation_time_seconds":generation_time,"solve_time_seconds":solve_time,"median_solve_seconds":median(timings) if timings else 0,"p95_solve_seconds":_percentile(timings,.95),"timeout_count":0,"exception_count":exceptions,"no_prediction_count":no_prediction,"wrong_dimension_count":wrong_dimension,"incorrect_cell_count":incorrect_cells,"exact_ground_truth_program_recovery_count":recovered,"semantically_equivalent_program_count":"unavailable: equivalence is not tested","success_by_difficulty":{str(args.difficulty):{"success":task_correct,"total":len(generated)}},"success_by_operation":success(by_op),"success_by_ordered_composition":success(by_composition),"success_by_program_depth":success(by_depth),"success_by_grid_size":success(by_size),"failure_reason_distribution":dict(sorted(reasons.items()))}
    write_json(args.output/"experiment.json",report); (args.output/"experiment.md").write_text(markdown("Synthetic solver experiment",report),encoding="utf-8"); write_csv(args.output/"results.csv",rows,list(rows[0]) if rows else ["task_id","public_hash","difficulty","composition","program_depth","grid_size","status","exact","exact_program","solve_seconds","failure_reason"])
    with (args.output/"failures.jsonl").open("w",encoding="utf-8") as h:
        for row in failures: h.write(json.dumps(row,sort_keys=True)+"\n")
    (args.output/"solved-task-ids.txt").write_text("\n".join(solved)+("\n" if solved else ""),encoding="utf-8"); (args.output/"unsolved-task-ids.txt").write_text("\n".join(unsolved)+("\n" if unsolved else ""),encoding="utf-8")
    print(f"wrote {args.output / 'experiment.json'}"); return 0
if __name__ == "__main__": raise SystemExit(main())
