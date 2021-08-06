from typing import Generator

import numpy as np

from .enums import Piece

'''
Hexagonal grid for game of thud
grid is a 15x15 array
grid has accessor methods for the board
'''


class Grid:
    def __init__(self, **kwargs) -> None:
        """
        possible args are:
        "board", "pieces", "dimensions"
        """
        if len(kwargs) < 1:
            self.board = []
            self.pieces = {
                Piece.DWARF: [],
                Piece.TROLL: [],
                Piece.EMPTY: [],

                Piece.NON_PLAYABLE: []
            }

            self.dimensions = 0
        else:
            self.init_args(**kwargs)

    def init_args(self, **kwargs) -> None:

        self.board = kwargs['board']
        self.pieces = kwargs['pieces']
        self.dimensions = kwargs['dimensions']

    def get_representation(self) -> np.ndarray:
        dx, dy = self.dimensions
        dwarves = [[1 if (x, y) in self.pieces[Piece.DWARF] else 0 for x in range(dx)] for y in range(dy)]
        trolls = [[1 if (x, y) in self.pieces[Piece.TROLL] else 0 for x in range(dx)] for y in range(dy)]
        return [dwarves, trolls]

    def create_start_standard_board(self):
        """ set up a standard board"""
        board = [
            [-1, -1, -1, -1, -1, 1, 1, 0, 1, 1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, 1, 0, 0, 0, 0, 0, 1, -1, -1, -1, -1],
            [-1, -1, -1, 1, 0, 0, 0, 0, 0, 0, 0, 1, -1, -1, -1],
            [-1, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1, -1],
            [-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 2, -1, 2, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1],
            [-1, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1, -1],
            [-1, -1, -1, 1, 0, 0, 0, 0, 0, 0, 0, 1, -1, -1, -1],
            [-1, -1, -1, -1, 1, 0, 0, 0, 0, 0, 1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, 1, 1, 0, 1, 1, -1, -1, -1, -1, -1],
        ]

        self.board = list(map(lambda row: list(map(lambda s: Piece(s), row)), board))

        for x, row in enumerate(self.board):
            for y, content in enumerate(row):
                self.pieces[content].append((x + 1, y + 1))
        self.dimensions = (len(self.board), len(self.board[0]))

    def board_from_template(self, template):
        self.pieces = self.pieces = {
            Piece.DWARF: [],
            Piece.TROLL: [],
            Piece.EMPTY: [],
            Piece.NON_PLAYABLE: []
        }
        '''
        create a grid with input board 
        board = N*M array containing pieces in given location
        '''
        self.board = template
        self.dimensions = len(template), len(template[0])
        for x, row in enumerate(self.board):
            for y, content in enumerate(row):
                self.pieces[content].append((x + 1, y + 1))

    def __normalise(self, x, y):
        """ return normalised 0-indexed x & y """
        return (x - 1, y - 1)

    def get_piece(self, x, y):
        """
        normalise x, y (ie 0 index it) and return the piece
        if x, y not on the board, return NON_PLAYABLE type
        """
        x, y = self.__normalise(x, y)
        x_dimension, y_dimension = self.dimensions
        if x < 0 or x >= x_dimension or y < 0 or y >= y_dimension:
            return Piece.NON_PLAYABLE
        else:
            return self.board[x][y]

    def get_adj(self, x, y) -> Generator:
        return ((x + ix, y + iy) for ix in (1, 0, -1) for iy in (1, 0, -1) if (ix, iy) != (0, 0))

    def set_piece(self, x, y, piece):
        """
        Normalise x & y and set the piece at location to the input piece.
        If (x,y) isn't on the board or the piece is the non_playable piece, return NON_PLAYABLE
        Add the relevant pieces to the dictionary
        @return the replaced piece
        """
        if piece == Piece.NON_PLAYABLE: return Piece.NON_PLAYABLE
        returnPiece = self.get_piece(x, y)
        if returnPiece == Piece.NON_PLAYABLE:
            return returnPiece
        else:
            nx, ny = self.__normalise(x, y)
            self.pieces[returnPiece].remove((x, y))
            self.board[nx][ny] = piece
            self.pieces[piece].append((x, y))
            return returnPiece

    def remove_piece(self, x, y):
        """ replace piece at x,y with empty and return piece.
        if x,y is not playable, return NON_PLAYABLE piece """
        return self.set_piece(x, y, Piece.EMPTY)

    def move_piece(self, from_x, from_y, to_x, to_y) -> Piece:
        """
        Move piece at (from_x, from_y) to (to_x, to_y)
        Provided both are valid locations and theres a piece to move
        If the move is invalid, return NON_PLAYABLE piece
        @return the old piece at to_x, to_Y
        """
        move_piece = self.get_piece(from_x, from_y)
        return_piece = self.get_piece(to_x, to_y)
        if move_piece == Piece.EMPTY or move_piece == Piece.NON_PLAYABLE or return_piece == Piece.NON_PLAYABLE:
            return Piece.NON_PLAYABLE
        self.set_piece(to_x, to_y, move_piece)
        self.remove_piece(from_x, from_y)
        return return_piece

    def get_piece_list(self, piece):
        return self.pieces[piece]

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Grid):
            return False
        else:
            return (self.board == o.board and
                    self.dimensions == o.dimensions and
                    self.pieces == o.pieces)

    def deepcopy(self) -> 'Grid':
        new_board = [x[:] for x in self.board]
        new_pieces = {x: y[:] for x, y in self.pieces.items()}
        new_dimensions = tuple(self.dimensions)
        return Grid(board=new_board, pieces=new_pieces, dimensions=new_dimensions)


class AlternativeGrid(Grid):
    def __init__(self, **kwargs) -> None:
        """
        possible args are:
        1) "pieces"
        2) "dimensions"
        """
        if len(kwargs) < 1:
            self.pieces = {
                Piece.DWARF: [],
                Piece.TROLL: [],
                Piece.EMPTY: [],
                Piece.NON_PLAYABLE: []
            }

            self.dimensions = 0
        else:
            self.init_args(**kwargs)

    def init_args(self, **kwargs) -> None:
        self.pieces = kwargs['pieces']
        self.dimensions = kwargs['dimensions']

    def get_representation(self) -> np.ndarray:
        dx, dy = self.dimensions
        dwarves = [[1 if (x, y) in self.pieces[Piece.DWARF] else 0 for x in range(dx)] for y in range(dy)]
        trolls = [[1 if (x, y) in self.pieces[Piece.TROLL] else 0 for x in range(dx)] for y in range(dy)]
        return [dwarves, trolls]

    def create_start_standard_board(self):
        """ set up a standard board"""
        board = [
            [-1, -1, -1, -1, -1, 1, 1, 0, 1, 1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, 1, 0, 0, 0, 0, 0, 1, -1, -1, -1, -1],
            [-1, -1, -1, 1, 0, 0, 0, 0, 0, 0, 0, 1, -1, -1, -1],
            [-1, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1, -1],
            [-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 2, -1, 2, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [-1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1],
            [-1, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1, -1],
            [-1, -1, -1, 1, 0, 0, 0, 0, 0, 0, 0, 1, -1, -1, -1],
            [-1, -1, -1, -1, 1, 0, 0, 0, 0, 0, 1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, 1, 1, 0, 1, 1, -1, -1, -1, -1, -1],
        ]

        board = list(map(lambda row: list(map(lambda s: Piece(s), row)), board))

        for x, row in enumerate(board):
            for y, content in enumerate(row):
                self.pieces[content].append((x + 1, y + 1))
        self.dimensions = (len(board), len(board[0]))

    def board_from_template(self, template):
        self.pieces = self.pieces = {
            Piece.DWARF: [],
            Piece.TROLL: [],
            Piece.EMPTY: [],
            Piece.NON_PLAYABLE: []
        }
        '''
        create a grid with input board 
        board = N*M array containing pieces in given location
        '''
        self.board = template
        self.dimensions = len(template), len(template[0])
        for x, row in enumerate(self.board):
            for y, content in enumerate(row):
                self.pieces[content].append((x + 1, y + 1))

    def __normalise(self, x, y):
        """ return normalised 0-indexed x & y """
        return (x - 1, y - 1)

    def get_piece(self, x, y):
        """
        normalise x, y (ie 0 index it) and return the piece
        if x, y not on the board, return NON_PLAYABLE type
        """
        x, y = self.__normalise(x, y)
        x_dimension, y_dimension = self.dimensions
        if x < 0 or x >= x_dimension or y < 0 or y >= y_dimension:
            return Piece.NON_PLAYABLE
        else:
            return self.board[x][y]

    def get_adj(self, x, y) -> set:
        return {(x + ix, y + iy) for ix in (1, 0, -1) for iy in (1, 0, -1) if (ix, iy) != (0, 0)}

    def set_piece(self, x, y, piece):
        """
        Normalise x & y and set the piece at location to the input piece.
        If (x,y) isn't on the board or the piece is the non_playable piece, return NON_PLAYABLE
        Add the relevant pieces to the dictionary
        @return the replaced piece
        """
        if piece == Piece.NON_PLAYABLE: return Piece.NON_PLAYABLE
        returnPiece = self.get_piece(x, y)
        if returnPiece == Piece.NON_PLAYABLE:
            return returnPiece
        else:
            nx, ny = self.__normalise(x, y)
            self.pieces[returnPiece].remove((x, y))
            self.board[nx][ny] = piece
            self.pieces[piece].append((x, y))
            return returnPiece

    def remove_piece(self, x, y):
        """
        replace piece at x,y with empty and return piece.
        if x,y is not playable, return NON_PLAYABLE piece """
        return self.set_piece(x, y, Piece.EMPTY)

    def move_piece(self, from_x, from_y, to_x, to_y) -> Piece:
        """
        Move piece at (from_x, from_y) to (to_x, to_y)
        Provided both are valid locations and theres a piece to move
        If the move is invalid, return NON_PLAYABLE piece
        @return the old piece at to_x, to_Y
        """
        move_piece = self.get_piece(from_x, from_y)
        return_piece = self.get_piece(to_x, to_y)
        if move_piece == Piece.EMPTY or move_piece == Piece.NON_PLAYABLE or return_piece == Piece.NON_PLAYABLE:
            return Piece.NON_PLAYABLE
        self.set_piece(to_x, to_y, move_piece)
        self.remove_piece(from_x, from_y)
        return return_piece

    def get_piece_list(self, piece):
        return self.pieces[piece]

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Grid):
            return False
        else:
            return (self.board == o.board and
                    self.dimensions == o.dimensions and
                    self.pieces == o.pieces)

    def deepcopy(self) -> 'Grid':
        new_board = [x[:] for x in self.board]
        new_pieces = {x: y[:] for x, y in self.pieces.items()}
        new_dimensions = tuple(self.dimensions)
        return Grid(board=new_board, pieces=new_pieces, dimensions=new_dimensions)
