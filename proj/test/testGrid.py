import unittest
from ..gameEngine.grid import Grid
from ..gameEngine.enums import Piece

class TestGrid(unittest.TestCase):

    def setUp(self) -> None:

        self.grid = Grid()
        self.grid.create_start_standard_board()

    def test_standard_grid_dimensions(self):
        self.assertEqual(self.grid.dimensions, (15, 15))

    def test_get_pieces(self):
        """ test pieces are correct when creating board """
        expected = {
            (0, 0): Piece.NON_PLAYABLE,
            (10, 10): Piece.EMPTY,
            (9, 9): Piece.TROLL,
            (8, 8): Piece.NON_PLAYABLE,
            (4, 3): Piece.DWARF,
            (4, 13): Piece.DWARF,
            (6, 15): Piece.DWARF,
            (5, 15): Piece.NON_PLAYABLE,
            (-1, -1): Piece.NON_PLAYABLE,
            (16, 4): Piece.NON_PLAYABLE
        }

        for (x, y), expected_result in expected.items():
            self.assertEqual(self.grid.get_piece(x, y), expected_result)

    def test_set_piece(self):
        """ check pieces set correctly """
        expected = [
            ((4, 3), (Piece.EMPTY, Piece.EMPTY, Piece.DWARF)),
            ((1, 1), (Piece.DWARF, Piece.NON_PLAYABLE, Piece.NON_PLAYABLE)),
            ((-1, -2), (Piece.DWARF, Piece.NON_PLAYABLE, Piece.NON_PLAYABLE)),
            ((3, 6), (Piece.DWARF, Piece.DWARF, Piece.EMPTY)),
            ((8, 7), (Piece.EMPTY, Piece.EMPTY, Piece.TROLL))
        ]

        for (x, y), (input_piece, e_piece, e_return_piece) in expected:
            ret_piece = self.grid.set_piece(x, y, input_piece)
            self.assertEqual(e_piece, self.grid.get_piece(
                x, y), f'new piece {(x,y)}')
            self.assertEqual(ret_piece, e_return_piece, f'ret piece {(x,y)}')

    def test_remove_piece(self):
        """ check remove pieces works correctly """
        expected = [
            ((5, 2), (Piece.DWARF, Piece.EMPTY)),
            ((5, 2), (Piece.EMPTY, Piece.EMPTY)),
            ((4, 2), (Piece.NON_PLAYABLE, Piece.NON_PLAYABLE)),
            ((7, 4), (Piece.EMPTY, Piece.EMPTY)),
            ((9, 7), (Piece.TROLL, Piece.EMPTY)),
            ((9, 7), (Piece.EMPTY, Piece.EMPTY)),
        ]

        for (x, y), (e_old, e_new) in expected:

            old = self.grid.remove_piece(x, y)
            new = self.grid.get_piece(x, y)
            self.assertEqual(old, e_old, str((x, y)))
            self.assertEqual(new, e_new, str((x, y)))

    def test_move_piece(self):
        """ check pieces moved all work """

        expected = [
            ((1, 10), (2, 10), (Piece.EMPTY, Piece.DWARF, Piece.EMPTY)),
            ((1, 9), (9, 7), (Piece.EMPTY, Piece.DWARF, Piece.TROLL)),
            ((8, 7), (1, 8), (Piece.EMPTY, Piece.TROLL, Piece.EMPTY)),
            ((7, 7), (1, 1), (Piece.TROLL, Piece.NON_PLAYABLE, Piece.NON_PLAYABLE)),
            ((2, 2), (7, 6), (Piece.NON_PLAYABLE, Piece.EMPTY, Piece.NON_PLAYABLE))
        ]

        for (from_x, from_y), (to_x, to_y), (e_from, e_to, e_return) in expected:
            ret_piece = self.grid.move_piece(from_x, from_y, to_x, to_y)
            from_piece = self.grid.get_piece(from_x, from_y)
            to_piece = self.grid.get_piece(to_x, to_y)
            self.assertEqual(from_piece, e_from,
                             f'from piece: {(from_x, from_y)} -> {to_x, to_y}')
            self.assertEqual(
                to_piece, e_to,  f'to piece: {(from_x, from_y)} -> {to_x, to_y}')
            self.assertEqual(ret_piece, e_return,
                             f'return piece: {(from_x, from_y)} -> {to_x, to_y}')

    def test_piecelist_simple(self):
        self.grid.board_from_template([
            [Piece.EMPTY, Piece.DWARF, Piece.TROLL],
            [Piece.TROLL, Piece.DWARF, Piece.EMPTY],
            [Piece.NON_PLAYABLE, Piece.NON_PLAYABLE, Piece.DWARF]
        ])

        dwarves = self.grid.get_piece_list(Piece.DWARF)
        trolls = self.grid.get_piece_list(Piece.TROLL)
        empty = self.grid.get_piece_list(Piece.EMPTY)
        non_playable = self.grid.get_piece_list(Piece.NON_PLAYABLE)
        expected_len = [
            (dwarves, 3),
            (trolls, 2),
            (empty, 2),
            (non_playable, 2)]

        for pieces, exp in expected_len:
            self.assertEqual(len(pieces), exp)

        some_locations = [
            (dwarves,  [(1, 2), (2, 2), (3, 3)]),
            (trolls,  [(1, 3), (2, 1)]),
            (empty,  [(1, 1), (2, 3)]),
            (non_playable, [(3, 1), (3, 2)])
        ]
        for pieces, locs in some_locations:
            for loc in locs:
                self.assertIn(loc, pieces)

    def test_pieces_list(self):
        """ === check pieces before changes === """

        expected = [
            (Piece.TROLL, [(7, 7), (7, 8), (9, 7)]),
            (Piece.EMPTY, [(8, 4), (12, 12), (13, 6)]),
            (Piece.DWARF, [(6, 1), (11, 2), (11, 14), (9, 15)]),
            (Piece.NON_PLAYABLE, [(8, 8), (1, 1), (15, 2)])
        ]

        for piece, e_locations in expected:
            locs = self.grid.pieces[piece]
            for loc in e_locations:
                self.assertIn(loc, locs, f'{loc} in {piece} list')

        """=== check pieces after setting piece ==="""

    def test_all_pieces_lists(self):
        dwarves = [x for x in self.grid.pieces[Piece.DWARF]]
        trolls = [x for x in self.grid.pieces[Piece.TROLL]]
        for x, y in dwarves:
            self.grid.remove_piece(x, y)
        for x, y in trolls:
            self.grid.remove_piece(x, y)
        self.assertEqual(len(self.grid.get_piece_list(
            Piece.DWARF)), 0, 'all DWARF pieces removed')
        self.assertEqual(len(self.grid.get_piece_list(
            Piece.TROLL)), 0, 'all TROLL pieces removed')

        max_x, max_y = self.grid.dimensions
        bad = [Piece.TROLL, Piece.DWARF]
        for x in range(1, max_x+1):
            for y in range(1, max_y+1):
                self.assertNotIn(self.grid.get_piece(x, y), bad,
                                 f'check board is clear at {(x,y)}')

    def test_copy(self):
        new_grid = self.grid.deepcopy()
        self.assertEqual(self.grid.pieces, new_grid.pieces,
                         'pieces are the same')
        new_grid.set_piece(10, 10, Piece.DWARF)
        self.assertNotEqual(self.grid.get_piece(10, 10), new_grid.get_piece(
            10, 10), 'change in one not in other')

    def test_grid_from_template(self):
        template = [
            [Piece.EMPTY, Piece.EMPTY, Piece.EMPTY],
            [Piece.DWARF, Piece.EMPTY, Piece.TROLL],
            [Piece.TROLL, Piece.EMPTY, Piece.EMPTY]
        ]
        self.grid.board_from_template(template)
        self.assertEqual(self.grid.dimensions, (3, 3),
                         'dimensions are correct')
        self.assertEqual(len(self.grid.pieces[Piece.DWARF]), 1, 'only 1 dwarf')
        self.assertEqual(len(self.grid.pieces[Piece.TROLL]), 2, '2 trolls')
        self.assertEqual(self.grid.get_piece(
            1, 1), Piece.EMPTY, 'template correct')
        self.assertEqual(self.grid.get_piece(2, 2), Piece.EMPTY)
