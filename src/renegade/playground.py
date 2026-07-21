"""Plain deterministic command-line inspection of the percept pipeline."""
from __future__ import annotations
import argparse, json, sys
from .pipeline import inspect_grid

DEFAULT_GRID = ((1, 1, 0), (1, 0, 0), (2, 2, 2))
def _load(args: argparse.Namespace):
    modes = sum(value is not None and value is not False for value in (args.grid, args.file, args.stdin))
    if modes > 1: raise ValueError("choose only one input mode")
    if args.grid is not None: return json.loads(args.grid)
    if args.file is not None:
        with open(args.file, encoding="utf-8") as handle: return json.load(handle)
    if args.stdin: return json.load(sys.stdin)
    return DEFAULT_GRID
def render(result) -> str:
    lines = []
    def section(name): lines.extend((name, "─" * 28))
    section("INPUT"); lines.extend(" ".join(str(cell) for cell in row) for row in result.grid)
    section("OBSERVATIONS"); lines.extend((f"frame: {result.frame.identity}", f"cells: {len(result.observations)}"))
    section("MEASUREMENTS"); lines.extend(f"{item.identity.local_name}: {item.value}" for item in result.measurements)
    section("PERCEPTS"); lines.append(f"frame percept: {result.frame_percept.identity}")
    for number, percept in enumerate(result.region_percepts, 1): lines.append(f"region {number}: {percept.identity} cells: {len(percept.observation_references)}")
    section("EXECUTION TRACE"); lines.extend(f"{item.sequence}. [{item.kind.value}] {item.message}" for item in result.trace)
    section("SUMMARY"); lines.extend((f"observations: {len(result.observations)}", f"measurements: {len(result.measurements)}", f"percepts: {1 + len(result.region_percepts)}", f"regions: {len(result.region_percepts)}"))
    return "\n".join(lines)
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Inspect a deterministic supplied grid."); group = parser.add_argument_group("input")
    group.add_argument("--grid"); group.add_argument("--file"); group.add_argument("--stdin", action="store_true")
    try: print(render(inspect_grid(_load(parser.parse_args(argv))))); return 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error: print(f"error: {error}", file=sys.stderr); return 2
if __name__ == "__main__": raise SystemExit(main())
