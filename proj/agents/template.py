
from abc import abstractmethod

from ..gameEngine.state import GameStateTemplate, Action


class AgentTemplate:
    # agents_filename = "agents.txt"

    def __init__(self, name, agentClassName) -> None:
        self.name = name
        self.agentClassName = agentClassName

        # with open(ThudAgentTemplate.agents_filename, "r") as file:
        #     agents = file.read()

        # if self.agentClassName not in agents:
        #     with open(ThudAgentTemplate.agents_filename, "a" if os.path.isfile(ThudAgentTemplate.agents_filename) else "w") as file:
        #         file.write(self.agentClassName)

    def __str__(self) -> str:
        return f'{self.name} ({self.agentClassName})'

    def __repr__(self) -> str:
        return str(self)

    @abstractmethod
    def act(self, state: GameStateTemplate, game_number: int,
            wins: dict, stats) -> Action:
        """ select an action according to the gameState and return it """
        pass
