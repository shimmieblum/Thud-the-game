from enum import Enum

import numpy as np
from Powerset import powerset

from .enums import Piece
from .grid import Grid


class MoveType(Enum):
    DWARF_MOVE = 1
    DWARF_HURL = 2
    TROLL_MOVE = 3
    TROLL_SHOVE = 4


from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class Action:
    from_loc: tuple
    to_loc: tuple
    capture: set
    movetype: MoveType

    def __str__(self) -> str:
        return f'{self.movetype}: {self.from_loc} -> {self.to_loc}  cap={self.capture}'

    def __repr__(self) -> str:
        return str(self)


class GameState:
    def __init__(self, grid=None, turn_number=1, previous_state=None, captured=None, turns_per_game=70,
                 prev_action=None) -> None:
        ''' 
        the turn_number fixes which side is to move 
        if no grid is input, a new one is created using a normal template
        alternatively, the input grid will be used
        '''
        if grid == None:
            self.grid = Grid()
            self.grid.create_start_standard_board()
        else:
            self.grid = grid
        self.previous_state = previous_state
        self.turn_number = turn_number
        self.turn = Piece.DWARF if self.turn_number % 2 > 0 else Piece.TROLL
        self.turns_per_game = turns_per_game
        self.captured = {Piece.DWARF: 0, Piece.TROLL: 0} if captured == None else captured
        self.prev_action = prev_action

    def get_captured(self, piece) -> int:
        ''' returned all the captured pieces '''
        return self.captured[piece]

    def valid_actions(self) -> 'tuple(tuple, tuple, set, MoveType)':
        ''' each action is a quadruple: 
        ((start location), (end location), {capture locations}, move_type)
        '''
        return self.get_dwarf_actions() if self.turn == Piece.DWARF else self.get_troll_actions()

    def next_move(self):
        ''' increment turn number and change turn '''
        self.turn_number += 1
        self.turn = self.turn = Piece.DWARF if self.turn_number % 2 > 0 else Piece.TROLL

    def deepcopy(self):
        ''' return deepcopy of this state '''
        return GameState(grid=self.grid.deepcopy(), turn_number=self.turn_number,
                         previous_state=self.previous_state, captured=self.captured.copy())

    def act_on_state(self, action: Action) -> None:
        ''' act directly on a state and return None'''
        (from_x, from_y), (to_x, to_y), capture = action.from_loc, action.to_loc, action.capture
        for x, y in capture:
            captured_piece = self.grid.remove_piece(x, y)
            if captured_piece in [Piece.TROLL, Piece.DWARF]:
                self.captured[captured_piece] += 1
        self.grid.move_piece(from_x, from_y, to_x, to_y)
        self.next_move()
        self.prev_action = action

    def take_action(self, action: 'Action') -> 'GameState':
        '''
        Perform this action on a new state and return new state
        @param: action as triple: ((start loc), (end loc), capture list)
        '''
        next_state = self.deepcopy()
        next_state.previous_state = self
        next_state.act_on_state(action)
        next_state.prev_action = action
        return next_state

    def dwarf_moves(self, x, y) -> 'list[Action]':
        ''' 
        dwarf 'normal move'
        dwarf 'normal moves' in straight lines when unobstructed
        dwarf cant capture in 'normal move', only hurl
        '''
        return_list = []
        increments = [(x, y) for x in [1, 0, -1] for y in [1, 0, -1] if (x, y) != (0, 0)]
        for ix, iy in increments:
            nx, ny = x + ix, y + iy
            piece = self.grid.get_piece(nx, ny)
            while piece == Piece.EMPTY:
                return_list.append(Action((x, y), (nx, ny), set(), MoveType.DWARF_MOVE))
                nx, ny = nx + ix, ny + iy
                piece = self.grid.get_piece(nx, ny)
        return return_list

    def dwarf_hurls(self, x, y) -> 'list[Action]':
        '''
        dwarf 'hurls'
        'hurl' = the front dwarf of a line of dwarves can be hurled the length of the line behind it. 
        a 'hurl can only be completed if the dwarf captures a troll by landing on it
        the 'hurled' dwarf is included in the line
        '''
        return_list = []
        increments = [(x, y) for x in [1, 0, -1] for y in [1, 0, -1] if (x, y) != (0, 0)]
        for ix, iy in increments:
            line_ix, line_iy = -ix, -iy
            length = self.get_line_length(x, y, line_ix, line_iy, Piece.DWARF)
            nx, ny = x, y
            for _ in range(length):
                nx, ny = nx + ix, ny + iy
                piece = self.grid.get_piece(nx, ny)
                if piece == Piece.TROLL:
                    return_list.append(Action((x, y), (nx, ny), {(nx, ny)}, MoveType.DWARF_HURL))
                    break
                elif piece != Piece.EMPTY:
                    break
        return return_list

    def get_dwarf_actions(self) -> 'list[Action]':
        start_locations = self.grid.get_piece_list(Piece.DWARF)
        return_list = []
        for x, y in start_locations:
            return_list.extend(self.dwarf_moves(x, y))
            return_list.extend(self.dwarf_hurls(x, y))
        return return_list

    def get_line_length(self, x, y, ix, iy, piece_type):
        if piece_type in (Piece.EMPTY, Piece.NON_PLAYABLE) or self.grid.get_piece(x, y) != piece_type: return 0
        if (ix, iy) == (0, 0): return 0
        length = 0
        piece = piece_type
        while piece == piece_type:
            length += 1
            x, y = x + ix, y + iy
            piece = self.grid.get_piece(x, y)
        return length

    def dwarves(self):
        return self.grid.get_piece_list(Piece.DWARF)

    def trolls(self):
        return self.grid.get_piece_list(Piece.TROLL)

    def troll_moves(self, x, y) -> 'list[Action]':
        ''' 
        get troll 'normal moves' - ie one step in any direction.
        the troll can capture one dwarf on its move if the dwarf is adjacent to the start location 
        '''
        incremenents = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1] if (x, y) != (0, 0)]
        return_list = []
        for ix, iy in incremenents:
            nx, ny = x + ix, y + iy
            piece = self.grid.get_piece(nx, ny)
            if piece == Piece.EMPTY:
                # can chose not to capture anything
                return_list.append(Action((x, y), (nx, ny), set(), MoveType.TROLL_MOVE))
                capture_list = ((a, b) for (a, b)
                                in self.grid.get_adj(nx, ny)
                                if self.grid.get_piece(a, b) == Piece.DWARF)
                for capture in capture_list:
                    return_list.append(Action((x, y), (nx, ny), {capture}, MoveType.TROLL_MOVE))
        return return_list

    def troll_hurls(self, x, y) -> 'list[Action]':
        '''
        get the trolls 'shove moves'
        to shove, the trolls require a line of trolls behind
        trolls can capture 1+ adjacent dwarves when performing a shove
        '''
        incremenents = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1] if (x, y) != (0, 0)]
        return_list = []
        for ix, iy in incremenents:
            line_length = self.get_line_length(x, y, -ix, -iy, Piece.TROLL)
            if line_length < 2: continue
            nx, ny = x, y
            for _ in range(line_length):
                nx, ny = nx + ix, ny + iy
                loc_piece = self.grid.get_piece(nx, ny)
                if loc_piece == Piece.EMPTY:
                    capture_list = [
                        (a, b) for (a, b)
                        in self.grid.get_adj(nx, ny)
                        if self.grid.get_piece(a, b) == Piece.DWARF]
                    if len(capture_list) > 0:
                        for capture in powerset(capture_list):
                            if capture == []: continue
                            return_list.append(Action((x, y), (nx, ny), set(capture), MoveType.TROLL_SHOVE))
                else:
                    break
        return return_list

    def dwarf_score(self) -> int:
        return len(self.dwarves())

    def troll_score(self) -> int:
        return len(self.trolls()) * 4

    def get_troll_actions(self) -> 'list[Action]':
        starts = self.grid.get_piece_list(Piece.TROLL)
        incremenents = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1] if (x, y) != (0, 0)]
        return_list = []

        for x, y in starts:
            return_list.extend(self.troll_moves(x, y))
            return_list.extend(self.troll_hurls(x, y))

        return return_list

    def get_subsequent_states(self):
        # TODO yield new boards without creating new states or grids
        # TODO ie detach data structures from the logic
        # for action in self.valid_actions():
        for action in self.valid_actions():
            yield self.take_action(action), action

    def acceptable_moves(self, x, y) -> 'list[Action]':
        ''' return a dictionary of acceptable end points as keys and movetype as value '''
        if self.grid.get_piece(x, y) == Piece.DWARF:
            full_list = self.dwarf_moves(x, y)
            full_list.extend(self.dwarf_hurls(x, y))
        else:
            full_list = self.troll_moves(x, y)
            full_list.extend(self.troll_hurls(x, y))
        return full_list

    def get_capture_sets(self, end_loc, movetype) -> 'list[set]':
        if movetype == MoveType.DWARF_MOVE:
            return [set()]
        elif movetype == MoveType.DWARF_HURL:
            return [{end_loc}]
        elif movetype == MoveType.TROLL_MOVE:
            x, y = end_loc
            return [{(a, b)} for (a, b) in self.grid.get_adj(x, y) if self.grid.get_piece(a, b) == Piece.DWARF]
        elif movetype == MoveType.TROLL_SHOVE:
            x, y = end_loc
            full_set = powerset(
                [(a, b) for (a, b) in self.grid.get_adj(x, y) if self.grid.get_piece(a, b) == Piece.DWARF])
            full_set.remove([])
            return [set(capture_list) for capture_list in full_set]

    def game_over(self) -> bool:
        '''
        If all pieces of one type are taken the game is over.
        If all the game turns have been used up the game is over.
        @return: True if one piece has no more pieces. Else False
        '''

        return self.turn_number > self.turns_per_game or len(self.dwarves()) == 0 or len(self.trolls()) == 0

    def winner(self) -> Piece:
        '''
        @return: the Piece with the highest score. 
        In case of a draw return 'draw'.
        '''
        d_score = self.dwarf_score()
        t_score = self.troll_score()
        return Piece.DWARF if d_score > t_score else Piece.TROLL if t_score > d_score else 'draw'

    def get_representation(self):
        ''' 
        Return representation of this state as a 3d np array.
        1) 15x15 grid representing dwarf locations
        2) 15x15 grid representing troll locations
        3) 15x15 grid representing who's turn it si
        '''
        val = 1 if self.turn == Piece.DWARF else 0
        dx, dy = self.grid.dimensions
        pieces_arrays = self.grid.get_representation()
        pieces_arrays.append([[val for x in range(dx)] for _ in range(dy)])
        final_array = np.array(pieces_arrays)
        final_array = np.expand_dims(final_array, 0)
        return final_array

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, GameState):
            return False
        else:
            return (o.grid == self.grid and
                    self.captured == o.captured and
                    self.turn == o.turn and
                    self.turn_number == o.turn_number)
