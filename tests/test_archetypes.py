"""Tests for deterministic structural archetypes."""
from dataclasses import FrozenInstanceError
import unittest
from renegade import (Archetype, ArchetypeKind, ArchetypeRegistry, Invariant,
 InvariantKind, StableIdentifier, derive_archetypes, inspect_grid)

FRAME = StableIdentifier("frame", "test", 1)
def invariant(name, **data):
 return Invariant(StableIdentifier("invariant", name, 1), InvariantKind.SAME_SHAPE_GROUP,
  (StableIdentifier("percept", name + "-a", 1), StableIdentifier("percept", name + "-b", 1)),
  (StableIdentifier("relationship", name, 1),), "test", FRAME, derivation=tuple(data.items()))

class ArchetypeTests(unittest.TestCase):
 def test_exact_vocabulary_recognition(self):
  cases = (("single", {"cell_count": 1}, ArchetypeKind.SINGLE_CELL),
   ("horizontal", {"height": 1, "width": 3, "cell_count": 3}, ArchetypeKind.HORIZONTAL_LINE),
   ("vertical", {"height": 3, "width": 1, "cell_count": 3}, ArchetypeKind.VERTICAL_LINE),
   ("filled", {"height": 2, "width": 3, "cell_count": 6}, ArchetypeKind.FILLED_RECTANGLE),
   ("hollow", {"height": 3, "width": 4, "cell_count": 10}, ArchetypeKind.HOLLOW_RECTANGLE),
   ("square", {"height": 3, "width": 3}, ArchetypeKind.SQUARE),
   ("checker", {"checkerboard": 1}, ArchetypeKind.CHECKERBOARD))
  for name, data, expected in cases:
   with self.subTest(expected=expected): self.assertIn(expected, {item.kind for item in derive_archetypes((invariant(name, **data),), FRAME)})
  family = Invariant(StableIdentifier("invariant", "family", 1), InvariantKind.TRANSLATION_FAMILY,
   tuple(StableIdentifier("percept", f"p-{n}", 1) for n in range(3)),
   (StableIdentifier("relationship", "family", 1),), "test", FRAME)
  kinds = {item.kind for item in derive_archetypes((family,), FRAME)}
  self.assertTrue({ArchetypeKind.LINEAR_CHAIN, ArchetypeKind.TRANSLATION_ARRAY} <= kinds)
 def test_identity_registry_and_duplicate_rejection(self):
  item = derive_archetypes((invariant("one", cell_count=1),), FRAME)[0]
  self.assertEqual(item, item); self.assertIsNot(item, Archetype(item.identity, item.kind, item.invariant_references, item.producing_capability, item.parent_frame, item.evidence, item.derivation))
  with self.assertRaises(FrozenInstanceError): item.kind = ArchetypeKind.SQUARE
  registry = ArchetypeRegistry(); registry.register(item)
  self.assertEqual(registry.by_invariant(item.invariant_references[0]), (item,))
  with self.assertRaisesRegex(ValueError, "already registered"): registry.register(item)
  with self.assertRaisesRegex(ValueError, "duplicate canonical"): registry.register(Archetype(StableIdentifier("archetype", "other", 1), item.kind, item.invariant_references, item.producing_capability, item.parent_frame, item.evidence, item.derivation))
 def test_pipeline_workspace_events_and_playground(self):
  result = inspect_grid([[1,0,1],[0,0,0],[1,0,1]])
  self.assertEqual(result.archetypes, derive_archetypes(result.invariants, result.frame.identity))
  self.assertIn("archetype.created", [event.kind.value for event in result.trace]) if result.archetypes else self.assertNotIn("archetype.created", [event.kind.value for event in result.trace])
  from renegade.playground import render
  self.assertIn("ARCHETYPES", render(result))
