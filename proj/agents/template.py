from abc import abstractmethod
from ..model.state import GameState, Action

class ThudAgentTemplate:
    def __init__(self, name, agentClassName) -> None:
        self.name = name
        self.agentClassName = agentClassName
    
    def __str__(self) -> str:
        return f'{self.name} ({self.agentClassName})'
    
    def __repr__(self) -> str:
        return str(self)
    
    
    @abstractmethod
    def act(self, state: GameState, game_number:int, wins:dict)-> Action:
        ''' select an action according to the gameState and return it '''
        pass

