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

## Diversity-repair commands

`balanced` is the default and is the appropriate mode for capability measurement;
`natural` is deterministic seeded sampling for distribution observation.

```powershell
python -m pip install --editable .
python -m unittest tests.test_generator tests.test_generate -v
python -m unittest discover -s tests -v
python -m renegade.audit_generation --count 100 --difficulty 2 --sampling balanced --seed 42 --output experiments\audit-smoke
python -m renegade.audit_generation --count 1000 --difficulty 1 --sampling balanced --seed 101 --output experiments\audit-d1
python -m renegade.audit_generation --count 1000 --difficulty 2 --sampling balanced --seed 102 --output experiments\audit-d2
python -m renegade.audit_generation --count 1000 --difficulty 3 --sampling balanced --seed 103 --output experiments\audit-d3
python -m renegade.experiment --count 1000 --difficulty 1 --sampling balanced --seed 101 --output experiments\experiment-d1 --progress-interval 100
python -m renegade.experiment --count 1000 --difficulty 2 --sampling balanced --seed 102 --output experiments\experiment-d2 --progress-interval 100
python -m renegade.experiment --count 1000 --difficulty 3 --sampling balanced --seed 103 --output experiments\experiment-d3 --progress-interval 100
1..5 | ForEach-Object { python -m renegade.experiment --count 200 --difficulty 2 --sampling balanced --seed $_ --output ("experiments\\d2-seed-" + $_) }
python -m renegade.inspect_generation --count 20 --difficulty 2 --sampling balanced --seed 42 --output experiments\inspect-d2
Get-Content experiments\audit-d2\audit.json | Select-String 'ordered_operation_composition_frequency'
Get-Content experiments\audit-d2\audit.json | Select-String 'rejected'
```

The inventory is embedded in `audit.json`; audit and experiment reports remain
under the requested output directory. Entropy is Shannon entropy in bits (base
2), with zero for empty or singleton distributions.
