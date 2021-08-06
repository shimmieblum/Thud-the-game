import unittest
from ..agents.heuristicAgent import HeuristicAgent
from ..model.state import GameState, Action
from ..model.grid import Grid
from ..model.enums import Piece

class TestHeuristicAgent(unittest.TestCase):
    
    def setUp(self) -> None:
        self.agent = HeuristicAgent('player 1', 'HeuristicAgent')
        self.state = GameState()
        self.state.grid.board_from_template([
                [Piece.TROLL, Piece.TROLL, Piece.DWARF, Piece.DWARF],
                [Piece.EMPTY, Piece.EMPTY, Piece.EMPTY, Piece.EMPTY],
                [Piece.DWARF, Piece.TROLL, Piece.EMPTY, Piece.EMPTY],
                [Piece.DWARF, Piece.EMPTY, Piece.EMPTY, Piece.EMPTY]
            ])
    
    def test_eucledian_distance(self):
        points = [
            ((1,2), (5,6), 5.66),
            ((17,3), (4,4), 13.04),
            ((18,3,4), (12,11,9), 11.18)
        ]
        
        for a,b,exp in points:
            self.assertEqual(self.agent.euclidean_distance(a,b), exp)
            
    def test_error_eucledian_distance(self):
        with self.assertRaises(Exception): self.agent.euclidean_distance((1,2,3), (2,4))
                    
                    
    def test_mean(self):
        case = [
            ([(1,2), (7,9), (-1,-1), (0,0), (5,4), (-4,8)], (1.33, 3.67)),
            ([(3,4,7), (7,-1,-1), (8,5,8), (2,3,2)], (5, 2.75, 4)) 
            ]
        for points, exp_mean in case:
            self.assertEqual(self.agent.mean(points), exp_mean)
            
    def test_clusters(self):
        import unittest.mock as mock
        def first_n(points, choices):
            return [points[i] for i in range(choices)] 
        
        cases = [
            ([(1,2), (10,11), (4,5),(8,6), (-1,-1), (6,7), (13,0), (2,-1)], 2, 
            {
                (1.5,1.25):[(1,2), (4,5), (-1,-1), (2,-1)], 
                (9.25,6):[(10,11), (8,6), (6,7), (13,0)]
            }),
            ([(1,2), (4,5), (8,6), (10,11), (-1,-1), (6,7), (13,0), (2,-1)], 2,
            {
                (0.67,0): [(1,2), (-1,-1), (2,-1)],
                (8.2,5.8): [(4,5), (8,6), (10,11), (6,7), (13,0)]
            })   
        ]
        
        with mock.patch('random.choices', lambda points,choices: first_n(points, choices)):
            
            for points, n, exp_clusters in cases:
                clusters = self.agent.clusters(points, n)
                self.assertDictEqual(clusters, exp_clusters)    
            
        
    def test_sihouette_calculation(self):
        cluster_cases = [
            ({
                (3.86, 4.57): [(2,4), (3,3), (3,6), (4,5), (4,6), (5,3), (6,5)],
                (1.62, -1.12): [(1,1), (2,1), (1,-1), (2,-1), (3,0), (1,-2), (1,-4), (2,-3)]
            }, 0.58)
        # ,({
        #     (-0.4, -1.2): [(-1, -2), (-1, 0), (3, -3), (-4, -2), (1, 1)],
        #     (2.25, 4.88): [(1, 4), (6, 7), (4, 8), (2, 2), (2, 5), (-5, 6), (8, 0), (0, 7)]
        # },
        # {
        #     (1.11, 2.56): [(1, 4), (6, 7), (-1, -2), (4, 8), (-1, 0), (2, 2), (2, 5), (-4, -2), (1, 1)], 
        #     (5.5, -1.5): [(3, -3), (8, 0)], 
        #     (-2.5, 6.5): [(-5, 6), (0, 7)]
        # },
        # {
        #     (0.5, -1.0): [(-1, -2), (-1, 0), (3, -3), (1, 1)], 
        #     (3.83, 4.33): [(1, 4), (6, 7), (4, 8), (2, 2), (2, 5), (8, 0)], 
        #     (-4.0, -2.0): [(-4, -2)],
        #     (-2.5, 6.5): [(-5, 6), (0, 7)]
        # })
        ]
        
        
        for clusters,exp_sil in cluster_cases:
            self.assertEqual( self.agent.silhouette(clusters), exp_sil)
            
    def test_silhouette_per_point(self):
        cases = [
            ((1,3), [(1,3), (4,4), (5,7), (9,3)], [(10,11), (30,0), (-1,21)], 0.72),
            ((1,3), [(4,4), (8,8), (10,2), (9,3), (1,3)], [(2,2), (3,5), (-1,-1), (-2,0), (-3,4), (4,2)],-0.53)
            ]
        for i, cluster, nearest, exp in cases: 
            self.assertEqual(self.agent.silhouette_of_point(i, cluster, nearest), exp)
        