# Synthetic Solver Baseline

## Conditions

This bounded local baseline was run from commit `d364bd6` before this reporting
change was committed, using the actual current solver and the experiment
runner's public-JSON boundary. Private metadata and hidden test outputs were
retained only for scoring. Commands:

```text
python -m renegade.audit_generation --count 100 --difficulty {1,2,3} --seed {101,102,103} --output /tmp/renegade-audits/d{1,2,3}
python -m renegade.experiment --count 100 --difficulty {1,2,3} --seed {101,102,103} --output /tmp/renegade-baseline/d{1,2,3} --progress-interval 100
```

Environment: CPython 3.12.13 in the provided Linux container. No optional
analytics packages were used. Timings are local observations, not portable
performance claims.

## Generator observations

Each level accepted all 100 requested tasks, had zero replay-validation
failures, zero no-op rejections, and 100 unique public hashes. Level 1 had 10
unique program hashes (28 recolor, 20 reflect, 26 rotate, and 26 translate);
level 2 had one (`recolor -> recolor`); level 3 had two (`recolor -> recolor
-> reflect`). Observed generation times were 0.0598 s, 0.0635 s, and 0.0810 s
for levels 1--3 respectively. These counts expose deliberately limited program
diversity at higher levels rather than concealing it.

## Solver observations

| difficulty | seed | exact outputs / total | all-test tasks / total | median solve s | p95 solve s | total solve s | failures |
|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 101 | 100 / 100 | 100 / 100 | 0.1191 | 0.4090 | 15.5192 | none |
| 2 | 102 | 100 / 100 | 100 / 100 | 0.3143 | 0.8926 | 42.5385 | none |
| 3 | 103 | 0 / 100 | 0 / 100 | 0.6307 | 2.4884 | 89.4426 | 100 no-prediction |

At level 1 the operation-level result was 100% for recolor (28 tasks), reflect
(20), rotate (26), and translate (26). At level 2, `recolor -> recolor` was
100/100. At level 3, `recolor -> recolor -> reflect` was 0/100. There were no
exceptions, timeouts, wrong dimensions, or incorrect predicted cells in these
runs; level-3 failures made no predictions because the current solver search
is bounded to depth two.

The original run did not preserve syntactic program-recovery comparisons; that
metric is therefore not reported here. The current experiment implementation
now measures it when comparable. Semantic equivalence was not tested.

## Limitations and next measurement

The generator uses a small whole-grid language and fixed higher-level
compositions. Success on these generator-native tasks does not show transfer to
official ARC. The immediate next experiment should add *measured*, effective
alternative level-2/3 compositions only after extending or independently
evaluating the bounded solver search budget; retain the public/private boundary
and compare the resulting composition-level table.
