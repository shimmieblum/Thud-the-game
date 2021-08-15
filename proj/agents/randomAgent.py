
from ..gameEngine.state import GameStateTemplate, Action
from ..agents.template import AgentTemplate

import random


class RandomAgent(AgentTemplate):
    """
    This Agent will chose a random move from the list of valid actions
    """

    def __init__(self, name, agentClassName) -> None:
        super().__init__(name, agentClassName)

    def act(self, state: GameStateTemplate, game_number: int,
            wins: dict, stats) -> Action:
        actions = state.valid_actions()
        # time.sleep(0.5)
        return random.choice(actions)


class BetterRandomAgent(AgentTemplate):
    """
    This Agent will select the move that will capture the most opponents.
    If no opponents can be captured a random choice is made 
    """

    def __init__(self, name, agentClassName) -> None:
        super().__init__(name, agentClassName)

    def act(self, state: GameStateTemplate, game_number: int,
            wins: dict, stats) -> Action:
        # time.sleep(0.5)

        actions = state.valid_actions()
        best_action = max(actions, key=lambda x: len(x.capture))
        # if best action doesn't do any capturing, choose a random choice instead
        if len(best_action.capture) == 0:
            return random.choice(actions)
        else:
            return best_action
