import unittest
from renegade import Operation, Program, execute, load_task, solve_task
from renegade.scene import ObjectPredicate, PredicateKind, RelationKind, Scene
from renegade.solver import SearchConfig

class ObjectProgramTests(unittest.TestCase):
    def test_predicate_sets_ambiguity_and_eight_connectivity(self):
        grid=((1,0,2),(0,1,0),(3,0,3))
        four=Scene.from_grid(grid, 0); eight=Scene.from_grid(grid,0,8)
        self.assertEqual(len(four.objects), 5); self.assertEqual(len(eight.objects),4)
        self.assertEqual(len(four.select(ObjectPredicate(PredicateKind.BORDER))),4)
        self.assertEqual(four.render(four.select(ObjectPredicate(PredicateKind.INTERIOR)),rebase=True),((1,),))

    def test_relation_query_and_constructive_render(self):
        grid=((0,1,0,2,0),(0,1,0,2,0))
        scene=Scene.from_grid(grid,0); left=scene.objects[0]
        self.assertEqual(scene.related(left, RelationKind.RIGHT_OF), ())
        self.assertEqual(len(scene.related(left, RelationKind.LEFT_OF)), 1)
        program=Program((Operation.make('render_related',background=0,reference='leftmost',relation='left_of',canvas='bbox'),))
        self.assertEqual(execute(program,grid),((2,),(2,)))

    def test_object_map_and_count_driven_repeat_execution(self):
        grid=((0,1,0,2,0,3),(0,1,0,0,0,0))
        recolor=Program((Operation.make('recolor_objects',background=0,predicate='border',color=8),))
        self.assertEqual(execute(recolor,grid),((0,8,0,8,0,8),(0,8,0,0,0,0)))
        repeat=Program((Operation.make('repeat_object',background=0,predicate='tallest',count='object_count',axis='horizontal',gap=1),))
        self.assertEqual(execute(repeat,grid),((1,0,1,0,1),(1,0,1,0,1)))

    def test_solver_fits_multi_object_render_and_conditional_map(self):
        task=load_task({'train':[{'input':[[0,1,0,2,0],[0,1,0,0,0]],'output':[[1,0,2],[1,0,0]]}], 'test':[{'input':[[0,3,0,4,0],[0,3,0,0,0]]}]}, 'objects')
        result=solve_task(task,config=SearchConfig(max_depth=1,max_candidates=512))
        self.assertEqual(result.predictions,(((3,0,4),(3,0,0)),))
        self.assertIsNotNone(result.selected_program)
        task=load_task({'train':[{'input':[[0,1,0,2],[0,1,0,0]],'output':[[0,9,0,2],[0,9,0,0]]}], 'test':[{'input':[[0,3,0,4],[0,3,0,0]]}]}, 'map')
        result=solve_task(task,config=SearchConfig(max_depth=1,max_candidates=512))
        self.assertEqual(result.predictions,(((0,9,0,4),(0,9,0,0)),))
        self.assertIn('recolor_objects', result.selected_program.canonical)
if __name__ == '__main__': unittest.main()
