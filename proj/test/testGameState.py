
import unittest

from ..model.enums import Piece
from ..model.state import Action, GameState, MoveType

class TestGameState(unittest.TestCase):
    
    def setUp(self) -> None:
        self.state = GameState()
        
    def test_new_state(self):
        self.assertEqual(self.state.turn_number, 1, 'first turn = 1')
        self.assertEqual(self.state.turn, Piece.DWARF, 'first move dwarf')
        self.assertEqual(self.state.grid.get_piece(7,1), Piece.DWARF, 'grid created correctly')
        self.assertEqual(self.state.get_captured(Piece.TROLL), 0, 'no pieces captured')
    
    def test_line_length(self):
        self.state.grid.board_from_template([
            [Piece.EMPTY, Piece.EMPTY, Piece.EMPTY],
            [Piece.DWARF, Piece.DWARF, Piece.TROLL],
            [Piece.TROLL, Piece.EMPTY, Piece.EMPTY]
            ])
        expected = [
            (1,1,0,1,Piece.EMPTY,0 , 'empty => 0'),
            (1,1,0,1,Piece.DWARF,0, 'wrong piece => 0'),
            (2,1,1,0,Piece.DWARF,1, '1 piece => 1'),
            (2,1,0,1,Piece.DWARF,2, 'dwarf line of 2 => 2'),
            (2,1,1,0,Piece.TROLL,0, 'incorrect piece => 0'),
            (2,3,0,1,Piece.TROLL,1, 'troll piece => 1'),
            (2,3,0,0, Piece.TROLL,0, 'increments = (0,0) => 0')
        ]
        for x,y,ix,iy,piece, ex_result, description in expected:
            self.assertEqual(
                self.state.get_line_length(x,y,ix,iy,piece), 
                ex_result,
                description)
        
    def test_valid_dwarf_actions_simple_board(self): 
        self.state.grid.board_from_template([
            [Piece.DWARF, Piece.EMPTY, Piece.EMPTY, Piece.TROLL,Piece.TROLL],
            [Piece.DWARF, Piece.DWARF, Piece.TROLL, Piece.DWARF, Piece.TROLL],
            [Piece.EMPTY, Piece.EMPTY, Piece.EMPTY, Piece.EMPTY, Piece.EMPTY],
            [Piece.TROLL, Piece.TROLL, Piece.EMPTY, Piece.NON_PLAYABLE, Piece.DWARF]
            ])
        
        valid_actions = [
            (Action((1,1), (1,2), set(), MoveType.DWARF_MOVE), 'move one space'),
            (Action((1,1), (1,3), set(), MoveType.DWARF_MOVE), 'move 2 spacess'),
            (Action((2,2), (2,3), {(2,3)}, MoveType.DWARF_HURL), 'hurl 1 space'),
            (Action((2,2), (3,2), set(), MoveType.DWARF_MOVE), 'move one space'),
            (Action((2,2), (3,3), set(), MoveType.DWARF_MOVE), 'move diagonally'),
            (Action((2,1), (4,1), {(4,1)}, MoveType.DWARF_HURL), 'hurl 2 spaces'),
            (Action((2,1), (3,2), set(),MoveType.DWARF_MOVE), 'move 1 space'),
            (Action((4,5), (3,5), set(), MoveType.DWARF_MOVE), 'move 1 space') 
        ]
        
        
        all_valid_actions = self.state.get_dwarf_actions()
        
        for action, descr in valid_actions: self.assertIn(action,all_valid_actions,descr)
        
    def test_invalid_dwarf_actions_simple_board(self):
        self.state.grid.board_from_template([
            [Piece.DWARF, Piece.EMPTY, Piece.EMPTY, Piece.TROLL,Piece.TROLL],
            [Piece.DWARF, Piece.DWARF, Piece.TROLL, Piece.DWARF, Piece.TROLL],
            [Piece.EMPTY, Piece.EMPTY, Piece.EMPTY, Piece.EMPTY, Piece.EMPTY],
            [Piece.TROLL, Piece.TROLL, Piece.EMPTY, Piece.NON_PLAYABLE, Piece.DWARF]
            ])
        
        invalid_actions = [
            Action((1,2), (2,2), set(), MoveType.DWARF_MOVE),
            Action((1,1), (0,1), set(), MoveType.DWARF_MOVE),
            Action((1,1), (1,4), {(1,4)}, MoveType.DWARF_HURL),
            Action((2,1), (3,1), set(), MoveType.DWARF_HURL),
            Action((2,1), (3,1), {(3,1)}, MoveType.DWARF_HURL),
            Action((2,1), (4,1), {(4,1)}, MoveType.DWARF_MOVE),
            Action((1,4), (1,3), set(), MoveType.DWARF_MOVE)
        ]
        
        all_valid_actions = self.state.get_dwarf_actions()
        
        for action in invalid_actions: self.assertNotIn(action,all_valid_actions, action)
    
    def test_valid_troll_actions_simple_board(self):
        self.state.grid.board_from_template([
            [Piece.DWARF, Piece.EMPTY, Piece.EMPTY, Piece.TROLL,Piece.TROLL],
            [Piece.DWARF, Piece.DWARF, Piece.TROLL, Piece.DWARF, Piece.TROLL],
            [Piece.EMPTY, Piece.EMPTY, Piece.EMPTY, Piece.EMPTY, Piece.EMPTY],
            [Piece.TROLL, Piece.TROLL, Piece.EMPTY, Piece.NON_PLAYABLE, Piece.DWARF]
        ])
        
        valid_actions = [
            Action((1,4), (1,3), {(2,2)}, MoveType.TROLL_MOVE),
            Action((1,4), (1,3), {(2,4)}, MoveType.TROLL_MOVE),
            Action((1,4), (1,3), {(2,2),(2,4)}, MoveType.TROLL_SHOVE),
            Action((1,4), (1,2), {(1,1), (2,2), (2,1)}, MoveType.TROLL_SHOVE),
            Action((2,3), (3,3), {(2,4)}, MoveType.TROLL_MOVE),
            Action((2,3), (3,3), {(2,2)}, MoveType.TROLL_MOVE),
            Action((2,3), (3,3), {(2,2), (2,4)}, MoveType.TROLL_SHOVE),
            Action((4,2), (4,3), set(), MoveType.TROLL_MOVE),
            Action((4,2), (3,3), {(2,2)}, MoveType.TROLL_MOVE),
            Action((4,2), (3,3), {(2,4)}, MoveType.TROLL_MOVE),
            Action((4,2), (3,3), {(2,4),(2,2)}, MoveType.TROLL_SHOVE),
            Action((4,2), (3,2), {(2,1)}, MoveType.TROLL_MOVE),
            Action((4,2), (3,2), {(2,2)}, MoveType.TROLL_MOVE),
            Action((4,2), (3,2), {(2,1),(2,2)}, MoveType.TROLL_SHOVE),
            Action((4,2), (3,2), {(2,2)}, MoveType.TROLL_SHOVE),
            Action((4,2), (3,1), {(2,1)}, MoveType.TROLL_MOVE),
            Action((4,2), (3,1), {(2,2)}, MoveType.TROLL_MOVE),
            Action((4,2), (3,1), {(2,1),(2,2)}, MoveType.TROLL_SHOVE),
            Action((4,2), (3,1), {(2,1)}, MoveType.TROLL_SHOVE)
            ]
        valid_troll_actions = self.state.get_troll_actions()
        
        for action in valid_actions:
            self.assertIn(action, valid_troll_actions)
    
    def test_all_actions_valid(self):
        '''check capture lists and action types match and correct action types for given pieces'''
        dwarf_actions = self.state.get_dwarf_actions()
        troll_actions = self.state.get_troll_actions()
        for action in dwarf_actions:
            valid = (action.movetype not in (MoveType.TROLL_MOVE, MoveType.TROLL_SHOVE) and 
                ((len(action.capture) == 0 and action.movetype == MoveType.DWARF_MOVE) or
                 (len(action.capture) == 1 and action.movetype == MoveType.DWARF_HURL)))
            self.assertTrue(valid)
        for action in troll_actions:
            valid = (action.movetype not in (MoveType.DWARF_HURL, MoveType.DWARF_MOVE) and
                     ((len(action.capture) in (0,1) and action.movetype == MoveType.TROLL_MOVE) or 
                      (len(action.capture) > 0 and action.movetype == MoveType.TROLL_SHOVE) ))
            self.assertTrue(valid)
        
    def test_invalid_troll_actions_simple_board(self):
       self.state.grid.board_from_template([
            [Piece.DWARF, Piece.EMPTY, Piece.EMPTY, Piece.TROLL,Piece.TROLL],
            [Piece.DWARF, Piece.DWARF, Piece.TROLL, Piece.DWARF, Piece.TROLL],
            [Piece.EMPTY, Piece.EMPTY, Piece.EMPTY, Piece.EMPTY, Piece.EMPTY],
            [Piece.TROLL, Piece.TROLL, Piece.EMPTY, Piece.NON_PLAYABLE, Piece.DWARF]
        ])
       
       invalid_actions = [
            Action((1,4), (1,3), {(3,4)}, MoveType.TROLL_MOVE), # can't capture that far
            Action((1,4), (1,2), {(2,2)}, MoveType.TROLL_MOVE), # can't move that far
            Action((2,3), (3,3), {(3,2)}, MoveType.TROLL_MOVE), # empty location
            Action((4,2), (4,3), set(), MoveType.TROLL_SHOVE),
            Action((4,2), (4,2), set(), MoveType.TROLL_MOVE),
            Action((2,5), (2,4), {(2,3)}, MoveType.TROLL_MOVE), # try to move onto troll
            Action((2,3), (2,2), {(2,2)}, MoveType.TROLL_MOVE), # try to move onto dwarf
            Action((2,3), (2,2), {(2,2)}, MoveType.TROLL_SHOVE)
            ]
       
       valid_actions = self.state.get_troll_actions()
       for action in invalid_actions:
           self.assertNotIn(action, valid_actions, action)
           
    def test_dwarf_actions_full_board(self):
        moves = [
            ((10,1), (7,4)),
            ((2,11), (2,9)),
            ((3,12), (3,9)),
            ((4,13), (4,9))
        ]
        
        valid_actions = [
                Action((6,15), (6,8), set(), MoveType.DWARF_MOVE),
                Action((6,15), (6,13), set(), MoveType.DWARF_MOVE),
                Action((4,9), (7,9), {(7,9)}, MoveType.DWARF_HURL),
                Action((9,1), (14,6), set(), MoveType.DWARF_MOVE),
            ]
        
        invalid_actions = [
            Action((6,15), (6,8), set(), MoveType.DWARF_HURL),
            Action((6,15), (6,13), {(6,13)}, MoveType.DWARF_HURL),
            Action((4,9), (7,9), {(7,9)}, MoveType.DWARF_MOVE),
            Action((3,9), (7,9), {(7,9)}, MoveType.DWARF_HURL),
            Action((4,9), (8,9), {(8,9)}, MoveType.DWARF_HURL),
            Action((13,4), (6,11), set(), MoveType.DWARF_MOVE),
            Action((9,1), (10,4), set(), MoveType.DWARF_MOVE)
        ]
        
        for (sx,sy), (tx,ty) in moves: self.state.grid.move_piece(sx,sy,tx,ty)
        
        all_valid = self.state.get_dwarf_actions()
        
        for valid in valid_actions: self.assertIn(valid, all_valid)
        for invalid in invalid_actions: self.assertNotIn(invalid, all_valid)
        
            
    def test_troll_actions_full_board(self):
        for (fx,fy), (tx,ty) in [
            ((8,9), (6,9)),
            ((9,9), (5,9)),
            ((9,7), (7,6))]:
            self.state.grid.move_piece(fx,fy,tx,ty)
            
        valid_actions = [
            Action((5,9), (2,9), {(1,9), (1,10)}, MoveType.TROLL_SHOVE),
            Action((7,8), (6,8), set(), MoveType.TROLL_MOVE),
            Action((7,6), (5,4), {(4,3)}, MoveType.TROLL_SHOVE),
            Action((9,8), (9,9), set(), MoveType.TROLL_MOVE),
            Action((9,8), (9,7), set(), MoveType.TROLL_MOVE),
            Action((9,8), (10,8), set(), MoveType.TROLL_MOVE),
            Action((9,8), (10,9), set(), MoveType.TROLL_MOVE),
            Action((9,8), (8,9), set(), MoveType.TROLL_MOVE),
            Action((9,8), (10,7), set(), MoveType.TROLL_MOVE)
        ]
        
        invalid_actions = [
            Action((9,8), (8,7), set(), MoveType.TROLL_MOVE),
            Action((9,8), (11,7), set(), MoveType.TROLL_MOVE),
            Action((9,8),(8,8), set(), MoveType.TROLL_MOVE),
            Action((9,8), (10,7), set(), MoveType.TROLL_SHOVE),
            Action((12,7), (11,7), set(), MoveType.TROLL_MOVE),
            Action((7,6), (4,3), {(4,3)}, MoveType.TROLL_SHOVE)
        ]
        
        all_valid = self.state.get_troll_actions()
        
        for valid in valid_actions: self.assertIn(valid, all_valid)
        for invalid in invalid_actions: self.assertNotIn(invalid, all_valid)
        
        
    
    def test_next_turn(self):
        self.assertTrue(self.state.turn == Piece.DWARF and self.state.turn_number == 1)
        self.state.next_move()
        self.assertTrue(self.state.turn == Piece.TROLL and self.state.turn_number == 2)
        
        
    def test_take_action(self):
        action = Action((7,1), (7,7), {(7,7)}, MoveType.DWARF_HURL)
        new_state = self.state.take_action(action)
        self.assertEqual(new_state.grid.get_piece(7,7), Piece.DWARF)
        self.assertEqual(new_state.get_captured(Piece.TROLL), 1)
        
    # def test_make_move(self):
    #     accepted = self.state.act_and_modify(Action( (5,2), (5,6), set(), MoveType.DWARF_MOVE ))
    #     self.assertTrue(accepted)
    #     self.assertEqual(self.state.grid.get_piece(5,6), Piece.DWARF)
    #     self.assertNotEqual(self.state.grid.get_piece(5,2), Piece.DWARF)
        
        
        
        