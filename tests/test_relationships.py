"""Tests for exact deterministic structural relationships."""
import unittest
from dataclasses import FrozenInstanceError
from renegade import RelationshipDirection, RelationshipKind, inspect_grid

class RelationshipTests(unittest.TestCase):
 def test_separated_regions_are_canonical_and_exact(self):
  result=inspect_grid([[1,0,1],[0,0,0],[1,0,1]])
  facts=result.relationships
  self.assertTrue(any(x.kind is RelationshipKind.SAME_VALUE for x in facts))
  self.assertTrue(any(x.kind is RelationshipKind.TRANSLATED_COPY for x in facts))
  self.assertTrue(all(not(x.direction is RelationshipDirection.SYMMETRIC and x.source > x.target) for x in facts))
  with self.assertRaises(FrozenInstanceError): facts[0].kind=RelationshipKind.DISJOINT
 def test_bands_have_strict_inverses_and_graph(self):
  result=inspect_grid([[1,1,1],[2,2,2],[3,3,3]])
  kinds={x.kind for x in result.relationships}
  self.assertIn(RelationshipKind.ABOVE,kinds); self.assertIn(RelationshipKind.BELOW,kinds)
  self.assertIn(RelationshipKind.ORTHOGONALLY_ADJACENT,kinds)
  self.assertEqual(result.percept_graph.relationships,result.relationships)
 def test_checkerboard_has_nine_regions(self):
  result=inspect_grid([[1,0,1],[0,1,0],[1,0,1]])
  self.assertEqual(len(result.region_percepts),9)
  self.assertTrue(any(x.kind is RelationshipKind.DIAGONALLY_ADJACENT for x in result.relationships))
