from proj.agents.statemachine import CompleteState, FromLocState
import pygame as pg
import sys
import enum
from pygame.constants import K_RETURN
from setuptools.namespaces import flatten


from proj.gameEngine.state import Action, GameStateTemplate, MoveType
from .template import AgentTemplate
from ..userInterfaces.GUI import GUI


class State(enum.Enum):
    FROM_LOC = 1
    TO_LOC = 2
    CAPTURE_LIST = 3
    COMPLETE = 4


class GUIAgent(AgentTemplate):
    """
    This Agent is a user Agent.
    Using 
    """

    def __init__(self, name, agentClassName) -> None:
        self.state = State.FROM_LOC
        super().__init__(name, agentClassName)

    def set_gui(self, gui: GUI):
        self.gui = gui

    def act(self, game_state: GameStateTemplate, game_number: int,
            wins: dict, game_stats) -> Action:
        """ select an action according to the gameState and return it """

        action = Action(None, None, set(), None)
        state = FromLocState()
        state.init_state(action, game_state, self.gui)
        event = None
        turn_over = False
        while not turn_over:
            for event in pg.event.get():
                args = (action, game_state, game_number, wins, event)
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if isinstance(state, CompleteState):
                    turn_over = True
                elif event != None:
                    action, state = state.act_on_event(action, game_state, self.gui, event)
        return action