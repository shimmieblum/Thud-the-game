
from pygame.constants import K_RETURN
from proj.gameEngine.state import Action, GameStateTemplate, MoveType
import pygame as pg 
from setuptools.namespaces import flatten

class State:
    def __init__(self, action, game_state, gui) -> None:
        self.init_state(action, game_state, gui)
    
    def act_on_event(self, action, game_state, gui, event) -> 'tuple[Action, State]':
        """
        Select an action as this state
        """
        pass
    
    
    def init_state(self, action, game_state, gui):
        """
        initialise this state on the ui
        """
        pass
    
    
class FromLocState(State):
    def act_on_event(self, action, game_state, gui, event) -> 'tuple[Action, State]':
        state  = self
        if event.type != pg.MOUSEBUTTONUP:
            return action, state
        mouse_position = pg.mouse.get_pos()
        x, y = gui.get_coordinates(mouse_position)
        if game_state.grid.get_piece(x, y) == game_state.turn:
            action.from_loc = x, y
            state =  ToLocState(action, game_state, gui)
        return action, state
        
    def init_state(self, action, game_state, gui):
        all_locs = game_state.get_locations(game_state.turn)
        gui.display_grid(game_state)
        gui.highlight_squares(all_locs, (176, 173, 5))
        
    
class ToLocState(State):
    def act_on_event(self, action, game_state, gui, event):
        valid_actions = game_state.valid_actions()
        state = self
        fx, fy = action.from_loc
        acceptable_moves = [a for a in filter(lambda action: action.from_loc == (fx, fy), valid_actions)]
        if event.type != pg.MOUSEBUTTONUP:
            return action, state
        mouse_position = pg.mouse.get_pos()
        x, y = gui.get_coordinates(mouse_position)
        if (fx, fy) == (x, y):
            action.from_loc = None
            state = FromLocState(action, game_state, gui)
        elif (x, y) in [p.to_loc for p in acceptable_moves]:
            action.to_loc = x, y
            equiv_action = list(
                filter(lambda p: p.to_loc == (x, y), acceptable_moves))
            action.movetype = equiv_action[0].movetype
            if action.movetype == MoveType.DWARF_HURL:
                action.capture.add((x, y))
            state = CaptureListState(action, game_state, gui)
        return action, state
    
        
    def init_state(self, action, game_state, gui):
        valid_actions = game_state.valid_actions()
        fx, fy = action.from_loc
        acceptable_moves = (a for a in filter(lambda action: action.from_loc == (fx,fy), valid_actions))
        gui.display_grid(game_state)
        gui.highlight_squares(
            [x.to_loc for x in acceptable_moves], ((176, 173, 5)))
        gui.highlight_squares([action.from_loc], (176, 0, 5))


class CaptureListState(State):
    def act_on_event(self, action, game_state, gui, event):
        state = self
        if event.type == pg.KEYDOWN and event.key == K_RETURN:
            state = CompleteState(action, game_state, gui)
            return action, state
        if event.type != pg.MOUSEBUTTONUP and event.type:
            return action, state
        mouse_position = pg.mouse.get_pos()
        if gui.ok_button_click(mouse_position):
            state = CompleteState(action, game_state, gui)
        else:
            x, y = gui.get_coordinates(mouse_position)
            if (x, y) == action.from_loc:
                action.from_loc = action.to_loc = None
                action.capture = set()
                state = FromLocState(action, game_state, gui)
            elif (x, y) == action.to_loc:
                action.to_loc = None
                action.capture = set()
                state = ToLocState(action, game_state, gui)
            elif (x, y) in action.capture:
                action.capture.remove((x, y))
                state = CaptureListState(action, game_state, gui)
            else:
                full_capture_set = set(action.capture)
                full_capture_set.add((x, y))
                all_sets = game_state.get_capture_sets(
                    action.to_loc, action.movetype)
                if full_capture_set in all_sets:
                    action.capture = full_capture_set
                elif {(x, y)} in all_sets:
                    action.capture = {(x, y)}
                state = CaptureListState(action, game_state, gui)
        return action, state
        
    def init_state(self, action, game_state, gui):
        fx, fy = action.from_loc
        tx, ty = action.to_loc
        movetype = action.movetype
        capture_sets = game_state.get_capture_sets((tx, ty), movetype)
        gui.display_grid(game_state)
        gui.highlight_squares(
            [(fx, fy), (tx, ty)], (176, 0, 5))  # highlight to and from
        gui.highlight_squares(
            set(flatten(capture_sets)), ((176, 173, 5)))
        # highlight locs in capture list
        gui.highlight_squares(
            [loc for loc in action.capture], (0, 0, 0))
        gui.add_ok_button()

class CompleteState(State):
    def act_on_event(self, action, game_state, gui, event):
        return super().act_on_event(action, game_state, gui, event)
    
    
    def init_state(self, action, game_state, gui):
        return super().init_state(action, game_state, gui)
    
    

