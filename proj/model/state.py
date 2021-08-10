from dataclasses import dataclass
from enum import Enum
from abc import abstractmethod
import numpy as np
from Powerset import powerset

from .enums import Piece
from .grid import Grid


class MoveType(Enum):
    """
    There are 4 types of move, each has an enum:
    - DWARF_MOVE
    - DWARF_HURL
    - TROLL_MOVE
    - TROLL_SHOVE
    """
    DWARF_MOVE = 1
    DWARF_HURL = 2
    TROLL_MOVE = 3
    TROLL_SHOVE = 4


@dataclass(unsafe_hash=True)
class Action:
    """
    An action consists of:
    - start locations: (x,y)
    - end location: (x,y)
    - capture set: set of locations that can be captured this turn
    - move type

    """
    from_loc: tuple
    to_loc: tuple
    capture: set
    movetype: MoveType

    def __str__(self) -> str:
        return f'{self.movetype}: {self.from_loc} -> {self.to_loc}  cap={self.capture}'

    def __repr__(self) -> str:
        return str(self)

class GameStateTemplate:
    
    def __init__(self, grid=None, turn_number=1, previous_state=None, turns_per_game=70,
                 prev_action=None) -> None:
        pass
    
    @abstractmethod
    def valid_actions(self) -> 'list[Action]':
        pass
    
    @abstractmethod
    def get_subsequent_states(self):
        pass
    
    
    @abstractmethod
    def take_action_on_state(self, action: Action) -> None:
        pass
    
    @abstractmethod
    def take_action(self, action: 'Action') -> 'GameState':
        pass
    
    @abstractmethod
    def deepcopy(self):
        pass
    
    @abstractmethod
    def score(self, piece)-> int:
        pass
    
    @abstractmethod
    def game_over(self) -> bool:
        pass
    
    @abstractmethod
    def winner(self) -> Piece:
        pass
    
    @abstractmethod
    def get_representation(self):
        pass
    
    
class GameState:
    """
    A gameState object represents the game at the certain point. information contained:
    - the turn number
    - which piece is to move
    - the current state of the grid
    - the previous state in the game

    Additionally, methods are provided to access:
    - all valid actions
    - all states reachable from this one
    - the currrent score for each piece
    - whether the game is over or not

    Finally, the game state has a method to perform an action on the state and therefore reach
    a subsequent state.
    """

    def __init__(self, grid=None, turn_number=1, previous_state=None, turns_per_game=70,
                 prev_action=None) -> None:
        """
        @param grid: the grid of this state. by default a new thud start grid is created
        @param turn_number: what turn game is up to. default=1
        @param previous_state
        @param captured: dictionary of how many pieces have been captured
        @param turns_per_game: the total turns to be played
        @param prev_action: the action taken to reach this state
        """
        if grid == None:
            self.grid = Grid()
            self.grid.create_start_standard_board()
        else:
            self.grid = grid
        self.previous_state = previous_state
        self.turn_number = turn_number
        self.turn = Piece.DWARF if self.turn_number % 2 > 0 else Piece.TROLL
        self.turns_per_game = turns_per_game
        self.prev_action = prev_action

    def valid_actions(self) -> 'list[Action]':
        """
        Return all valid actions for this state.
        - Action = ((start location), (end location), {capture locations}, move_type)
        @return: list of Actions
        """
        ret_list = []
        starts = self.dwarves() if self.turn is Piece.DWARF else self.trolls()
        for x, y in starts:
            ret_list.extend(self.__get_actions_from_loc(x, y))
        return ret_list

    def get_subsequent_states(self):
        # TODO yield new boards without creating new states or grids
        # TODO ie detach data structures from the logic
        # for action in self.valid_actions():
        for action in self.valid_actions():
            yield self.take_action(action), action

    def __get_actions_from_loc(self, x, y):
        """
        Get all actions from a given location
        @param x
        @param ym
        """
        if self.grid.get_piece(x, y) == Piece.DWARF:
            return self.__get_dwarf_actions_from_loc(x, y)
        elif self.grid.get_piece(x, y) == Piece.TROLL:
            return self.__get_troll_actions_from_loc(x, y)
        else:
            return []

    def __get_dwarf_actions_from_loc(self, x, y):
        """
        @return: list of all dwarf actions from location (x,y)
        """
        return_list = self.__dwarf_moves_from_location(x, y)
        if len(return_list) > 0:
            return_list.extend(self.__dwarf_hurls_from_location(x, y))
        return return_list

    def __get_troll_actions_from_loc(self, x, y):
        """
        @return: list of all troll actions from location (x,y)
        """
        return_list = self.__troll_moves_from_location(x, y)
        if len(return_list) > 0:
            return_list.extend(self.__troll_hurls_from_location(x, y))
        return return_list

    def __dwarf_moves_from_location(self, x, y) -> 'list[Action]':
        """
        - dwarf 'normal move': a straight lines when unobstructed.
        - dwarf can't capture in 'normal move', only in  a hurl

        @return: a list of 'move' actions from location (x,y)
        """

        return_list = []
        increments = [(x, y) for x in [1, 0, -1]
                      for y in [1, 0, -1] if (x, y) != (0, 0)]
        # in each direction, add increment until non-empty location is found
        for ix, iy in increments:
            nx, ny = x + ix, y + iy
            piece = self.grid.get_piece(nx, ny)
            while piece == Piece.EMPTY:
                return_list.append(
                    Action((x, y), (nx, ny), set(), MoveType.DWARF_MOVE))
                nx, ny = nx + ix, ny + iy
                piece = self.grid.get_piece(nx, ny)
        return return_list

    def __dwarf_hurls_from_location(self, x, y) -> 'list[Action]':
        """
        - dwarf 'hurls': the front dwarf of a line of dwarves can be hurled the length of the line behind it.
        - a 'hurl can only be completed if the dwarf captures a troll by landing on it
        - the 'hurled' dwarf is included in the line

        @return: the list of 'hurl actions from location (x,y)
        """

        return_list = []
        increments = [(x, y) for x in [1, 0, -1]
                      for y in [1, 0, -1] if (x, y) != (0, 0)]
        for ix, iy in increments:
            line_ix, line_iy = -ix, -iy
            length = self.__get_line_length(x, y, line_ix, line_iy, Piece.DWARF)
            nx, ny = x, y
            for _ in range(length):
                nx, ny = nx + ix, ny + iy
                piece = self.grid.get_piece(nx, ny)
                if piece == Piece.TROLL:
                    return_list.append(
                        Action((x, y), (nx, ny), {(nx, ny)}, MoveType.DWARF_HURL))
                    break
                elif piece != Piece.EMPTY:
                    break
        return return_list

    def __troll_moves_from_location(self, x, y) -> 'list[Action]':
        """
        get troll 'normal moves' - ie one step in any direction.
        the troll can capture one dwarf on its move if the dwarf is adjacent to the start location
        """
        incremenents = [(x, y) for x in [-1, 0, 1]
                        for y in [-1, 0, 1] if (x, y) != (0, 0)]
        return_list = []
        for ix, iy in incremenents:
            nx, ny = x + ix, y + iy
            if self.grid.get_piece(nx, ny) == Piece.EMPTY:
                return_list.extend(
                    (Action((x, y), (nx, ny), {(a, b)}, MoveType.TROLL_MOVE)
                     for (a, b) in self.grid.get_adj(nx,ny)
                     if self.grid.get_piece(a, b) == Piece.DWARF))
                # can chose not to capture anything
                return_list.append(
                    Action((x, y), (nx, ny), set(), MoveType.TROLL_MOVE))

        return return_list

    def __troll_hurls_from_location(self, x, y) -> 'list[Action]':
        '''
        get the trolls 'shove moves'
        to shove, the trolls require a line of trolls behind
        trolls can capture 1+ adjacent dwarves when performing a shove
        '''
        incremenents = [(x, y) for x in [-1, 0, 1]
                        for y in [-1, 0, 1] if (x, y) != (0, 0)]
        return_list = []
        for ix, iy in incremenents:
            line_length = self.__get_line_length(x, y, -ix, -iy, Piece.TROLL)
            if line_length < 2:
                # Don't allow hurls of a single troll
                continue
            nx, ny = x, y
            for _ in range(line_length):
                nx, ny = nx + ix, ny + iy
                piece = self.grid.get_piece(nx, ny)
                if piece != Piece.EMPTY:
                    break
                else:
                    adj_dwarves = [
                        (a, b) for (a, b)
                        in self.grid.get_adj(nx, ny)
                        if self.grid.get_piece(a, b) == Piece.DWARF]
                    if len(adj_dwarves) > 0:
                        return_list.extend((
                            Action((x, y), (nx, ny), set(
                                capture), MoveType.TROLL_SHOVE)
                            for capture in powerset(adj_dwarves)
                            if capture is not []))
        return return_list

    def __get_line_length(self, x, y, ix, iy, piece_type) -> int:
        """
        Calculates the strength of the line begind the piece at x,y
        @(x, y): start location
        @(ix, iy): increment
        @piece_type: type of piece at location (x,y)
        @return length of line as an integer
        """
        if (piece_type in (Piece.EMPTY, Piece.NON_PLAYABLE)
                or self.grid.get_piece(x, y) != piece_type or (ix, iy) == (0, 0)):
            return 0
        length = 0
        piece = piece_type
        while piece == piece_type:
            length += 1
            x, y = x + ix, y + iy

            piece = self.grid.get_piece(x, y)
        return length

    def take_action_on_state(self, action: Action) -> None:
        """
        Act directly on a state and return None
        """
        from_x, from_y = action.from_loc
        to_x, to_y = action.to_loc
        capture = action.capture
        for x, y in capture:
            self.grid.remove_piece(x, y)
        self.grid.move_piece(from_x, from_y, to_x, to_y)
        self.__next_move()
        self.prev_action = action

    def take_action(self, action: 'Action') -> 'GameState':
        """
        Perform this action on a new state and return new state
        @param: action as triple: ((start loc), (end loc), capture list)
        """
        next_state = self.deepcopy()
        next_state.previous_state = self
        next_state.take_action_on_state(action)
        next_state.prev_action = action
        return next_state

    def __next_move(self):
        """
        Increment turn number and change turn
        """
        self.turn_number += 1
        self.turn = self.turn = Piece.DWARF if self.turn_number % 2 > 0 else Piece.TROLL

    def deepcopy(self):
        """
        Return deepcopy of this state
        """
        return GameState(grid=self.grid.deepcopy(), turn_number=self.turn_number,
                         previous_state=self.previous_state)

    def get_locations(self, piece_type):
        """
        Get list of locations a given piece can be found at
        """

    def dwarves(self):
        """
        @return: list of all locations containing dwarves
        """
        return self.grid.get_piece_list(Piece.DWARF)

    def trolls(self):
        """
        @return: list of all locations containing trolls
        """
        return self.grid.get_piece_list(Piece.TROLL)

    def dwarf_score(self) -> int:
        """
        @return: the dwarf score
        """
        return len(self.dwarves())

    def troll_score(self) -> int:
        """
        @return: the troll score
        """
        return len(self.trolls()) * 4

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
                    self.turn == o.turn and
                    self.turn_number == o.turn_number)
