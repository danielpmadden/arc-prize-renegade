"""Tests for deterministic structural invariant grouping."""
from dataclasses import FrozenInstanceError
import unittest
from renegade import Invariant, InvariantKind, InvariantRegistry, StableIdentifier, inspect_grid

class InvariantTests(unittest.TestCase):
 def test_pipeline_forms_all_group_kinds(self):
  result=inspect_grid([[1,0,1],[0,0,0],[1,0,1]])
  kinds={item.kind for item in result.invariants}
  self.assertTrue({InvariantKind.SAME_VALUE_GROUP,InvariantKind.SAME_SHAPE_GROUP,InvariantKind.SAME_CELL_COUNT_GROUP,InvariantKind.SAME_BOUNDS_GROUP,InvariantKind.TRANSLATION_FAMILY} <= kinds)
  self.assertIn("invariant.created",[event.kind.value for event in result.trace])
 def test_invariant_identity_immutability_and_registry(self):
  result=inspect_grid([[1,1,1],[2,2,2]])
  item=result.invariants[0]
  with self.assertRaises(FrozenInstanceError): item.kind=InvariantKind.SAME_VALUE_GROUP
  registry=InvariantRegistry(); registry.register(item)
  self.assertEqual(registry.by_member(item.member_percepts[0]),(item,))
  with self.assertRaisesRegex(ValueError,"already registered"): registry.register(item)
 def test_playground_section(self):
  from renegade.playground import render
  self.assertIn("INVARIANTS",render(inspect_grid([[1,0],[0,1]])))
