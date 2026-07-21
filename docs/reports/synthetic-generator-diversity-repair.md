# Synthetic generator diversity repair

This experimental branch repairs a demonstrated generator defect; it does not establish ARC transfer, learning, or general intelligence.

## Inventory

`src/renegade/operations.py` is the executable inventory. Solver-supported and generator-supported operations are recolor, rotate, reflect, and translate. Identity is solver-supported but excluded because it cannot be effective. Crop, fill, and outline are solver-supported but generator-unsupported: their constructive composition constraints are not implemented, rather than silently being treated as recolor.

## Semantics and validation

Difficulty 1 is one effective operation. Difficulty 2 is an eligible ordered recolor/geometry pair. Difficulty 3 is two effective recolors plus one geometry stage in all eligible orders. Each stage must change its immediate input on every example; full output must differ from input; and removing any stage must alter at least one labelled output. Exact global minimality is unavailable and is not claimed.

`balanced` is the default for capability measurement; `natural` uses deterministic seeded slot selection. Entropy uses base-2 Shannon bits, returning zero for empty/singleton distributions. Audit reports raw frequency, coverage, concentration, hashes, and rejections.

## Historical before/after

Before: level 2 was fixed `recolor -> recolor`, so composition coverage was 1/1 within its defective declared space. After: the repaired eligible level-2 space has six slots and balanced batches of at least six cover all six; recolor→recolor has zero eligible and observed share.

## Commands

```powershell
python -m pip install --editable .
python -m unittest tests.test_generator tests.test_generate -v
python -m renegade.audit_generation --count 100 --difficulty 2 --sampling balanced --seed 42 --output experiments\audit-d2
python -m renegade.experiment --count 100 --difficulty 2 --sampling balanced --seed 42 --output experiments\experiment-d2
python -m renegade.inspect_generation --count 20 --difficulty 2 --sampling balanced --seed 42 --output experiments\inspect-d2
```

The unchanged solver remains bounded to depth two. Any measured results are generator-native and cannot establish transfer to official ARC.
