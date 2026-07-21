# Synthetic Laboratory: local PowerShell runbook

This laboratory measures generator-native synthetic tasks. It neither evaluates
official ARC nor establishes transfer, ARC equivalence, or general intelligence.

```powershell
py -m pip install --editable .
py -m unittest discover -s tests -v
# Generate one public task and private `.meta.json` sidecar.
py -m renegade.generate --count 10 --difficulty 1 --seed 42 --output experiments\smoke
# Replay is covered by the deterministic generator tests.
py -m unittest tests.test_generator -v
py -m renegade.audit_generation --count 10 --difficulty 1 --seed 42 --output experiments\audit-smoke
py -m renegade.audit_generation --count 100 --difficulty 1 --seed 42 --output experiments\audit-d1
py -m renegade.audit_generation --count 100 --difficulty 2 --seed 42 --output experiments\audit-d2
py -m renegade.audit_generation --count 100 --difficulty 3 --seed 42 --output experiments\audit-d3
py -m renegade.experiment --count 100 --difficulty 2 --seed 42 --output experiments\solve-100
py -m renegade.experiment --count 1000 --difficulty 3 --seed 42 --output experiments\solve-1000 --progress-interval 100
py -m renegade.experiment --count 10000 --difficulty 3 --seed 42 --output experiments\solve-10000 --progress-interval 250
```

Each output directory must be new or empty. Use `--force` only when deliberate
replacement is intended. Progress is emitted at `--progress-interval`; output
files are written after the bounded run completes, so interruption leaves a
directory that the next run refuses to overwrite unless `--force` is supplied.

`audit.json` and `audit.md` summarize task diversity; CSVs provide one task,
operation, and composition row. `experiment.json` and `.md` report exact
hidden-output scoring, timing, and failures. `results.csv` is one task per row;
`failures.jsonl` contains only failures; the two ID files partition solved and
unsolved tasks. “Object count” is explicitly unavailable because this generator
does not define an object model. Exact program recovery is only syntactic
comparison to the selected solver program; semantic equivalence is unavailable
unless a future implementation actually tests it.
