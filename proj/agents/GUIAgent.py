from proj.model.match import GameStats
import pygame as pg
import sys
import enum
from pygame.constants import K_RETURN
from setuptools.namespaces import flatten


from proj.model.enums import Piece
from proj.model.state import Action, ThudGameState, MoveType
from .template import ThudAgentTemplate
from ..userInterfaces.GUI import GUI


class State(enum.Enum):
    FROM_LOC = 1
    TO_LOC = 2
    CAPTURE_LIST = 3
    COMPLETE = 4


class GUIAgent(ThudAgentTemplate):
    '''
    This Agent is a user Agent.
    Using 
    '''

    def __init__(self, name, agentClassName) -> None:
        self.state = State.FROM_LOC
        super().__init__(name, agentClassName)

    def set_gui(self, gui: GUI):
        self.gui = gui

    def act(self, state: ThudGameState, game_number: int,
            wins: dict, game_stats: GameStats) -> Action:
        """ select an action according to the gameState and return it """
        state_dictionary = {
            State.FROM_LOC: self.from_loc,
            State.TO_LOC: self.to_loc,
            State.CAPTURE_LIST: self.capture_list
        }

        action = Action(None, None, set(), None)
        event = None
        turn_over = False
        self.change_state(action, State.FROM_LOC, state)
        while not turn_over:
            for event in pg.event.get():
                args = (action, state, game_number, wins, event)
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if self.state == State.COMPLETE:
                    turn_over = True
                elif event != None:
                    fn = state_dictionary[self.state]
                    action = fn(*args)
        return action

    def from_loc(self, action: Action, game_state: ThudGameState,
                 game_number, wins, event) -> Action:
        if event.type != pg.MOUSEBUTTONUP:
            return action
        mouse_position = pg.mouse.get_pos()
        x, y = self.gui.get_coordinates(mouse_position)
        if game_state.grid.get_piece(x, y) == game_state.turn:
            action.from_loc = x, y
            self.change_state(action, State.TO_LOC, game_state)
        return action

    def to_loc(self, action: Action, game_state: ThudGameState,
               game_number, wins, event) -> Action:
        fx, fy = action.from_loc
        acceptable_moves = game_state.acceptable_moves(fx, fy)
        if event.type != pg.MOUSEBUTTONUP:
            return action
        mouse_position = pg.mouse.get_pos()
        x, y = self.gui.get_coordinates(mouse_position)
        if (fx, fy) == (x, y):
            action.from_loc = None
            self.change_state(action, State.FROM_LOC, game_state)
        elif (x, y) in [p.to_loc for p in acceptable_moves]:
            action.to_loc = x, y
            equiv_action = list(
                filter(lambda p: p.to_loc == (x, y), acceptable_moves))

            action.movetype = equiv_action[0].movetype
            if action.movetype == MoveType.DWARF_HURL:
                action.capture.add((x, y))
            self.change_state(action, State.CAPTURE_LIST, game_state)
        return action

    def capture_list(self, action: Action, game_state: ThudGameState,
                     game_number, wins, event) -> Action:

        if event.type == pg.KEYDOWN and event.key == K_RETURN:
            self.change_state(action, State.COMPLETE, game_state)
        if event.type != pg.MOUSEBUTTONUP and event.type:
            return action
        mouse_position = pg.mouse.get_pos()
        if self.gui.ok_button(mouse_position):
            self.change_state(action, State.COMPLETE, game_state)
        else:
            x, y = self.gui.get_coordinates(mouse_position)
            if (x, y) == action.from_loc:
                action.from_loc = action.to_loc = None
                action.capture = set()
                self.change_state(action, State.FROM_LOC, game_state)
            elif (x, y) == action.to_loc:
                action.to_loc = None
                action.capture = set()
                self.change_state(action, State.TO_LOC, game_state)
            elif (x, y) in action.capture:
                action.capture.remove((x, y))
                self.change_state(action, State.CAPTURE_LIST, game_state)
            else:
                full_capture_set = set(action.capture)
                full_capture_set.add((x, y))
                all_sets = game_state.get_capture_sets(
                    action.to_loc, action.movetype)
                if full_capture_set in all_sets:
                    action.capture = full_capture_set
                elif {(x, y)} in all_sets:
                    action.capture = {(x, y)}
                self.change_state(action, State.CAPTURE_LIST, game_state)
        return action

    def change_state(self, action: Action, new_state, game_state: ThudGameState):
        '''
        change state and display appropriate new display
        '''

        self.state = new_state
        if new_state == State.FROM_LOC:
            all_locs = game_state.get_locations(game_state.turn)
            self.gui.display_grid(game_state)
            self.gui.highlight_squares(all_locs, (176, 173, 5))
        elif new_state == State.TO_LOC:
            fx, fy = action.from_loc
            acceptable_moves = game_state.acceptable_moves(fx, fy)
            self.gui.display_grid(game_state)
            self.gui.highlight_squares(
                [x.to_loc for x in acceptable_moves], ((176, 173, 5)))
            self.gui.highlight_squares([action.from_loc], (176, 0, 5))
        elif new_state == State.CAPTURE_LIST:
            fx, fy = action.from_loc
            tx, ty = action.to_loc
            movetype = action.movetype
            capture_sets = game_state.get_capture_sets((tx, ty), movetype)
            self.gui.display_grid(game_state)
            self.gui.highlight_squares(
                [(fx, fy), (tx, ty)], (176, 0, 5))  # highlight to and from
            self.gui.highlight_squares(
                set(flatten(capture_sets)), ((176, 173, 5)))
            # highlight locs in capture list
            self.gui.highlight_squares(
                [loc for loc in action.capture], (0, 0, 0))
            self.gui.add_ok_button()
