import unittest
from pathlib import Path
from renegade.knowledge import CapabilityRecord, ConceptRecord, Maturity, load_knowledge, maturity_transition_allowed, validate_knowledge
from renegade.introspection import EvidenceState, GapKind, observe_grid, semantic_near_miss
class KnowledgeTests(unittest.TestCase):
 def test_seed_bank_validates(self):
  concepts,caps=load_knowledge(); self.assertGreaterEqual(len(concepts),10); self.assertGreaterEqual(len(caps),3)
 def test_bad_references_and_cycles_rejected(self):
  a=ConceptRecord('a','a','x','x',Maturity.SEEDED,prerequisites=('missing',))
  with self.assertRaises(ValueError): validate_knowledge((a,),())
  a=ConceptRecord('a','a','x','x',Maturity.SEEDED,prerequisites=('b',)); b=ConceptRecord('b','b','x','x',Maturity.SEEDED,prerequisites=('a',))
  with self.assertRaises(ValueError): validate_knowledge((a,b),())
 def test_maturity_is_one_way(self):
  self.assertTrue(maturity_transition_allowed(Maturity.SEEDED,Maturity.EXECUTABLE)); self.assertFalse(maturity_transition_allowed(Maturity.EXECUTABLE,Maturity.SEEDED))
 def test_observers_and_private_near_miss_are_separate(self):
  evidence=observe_grid(((1,1),(1,1))); self.assertEqual(evidence[0].state,EvidenceState.POSSIBLE)
  result=semantic_near_miss(((1,),),((2,),)); self.assertFalse(result['exact']); self.assertEqual(result['provenance'],'evaluator_private_post_prediction')
if __name__=='__main__': unittest.main()
