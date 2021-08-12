
import random
import math
from typing import Callable, Generator

from dataclasses import dataclass

import time
from proj.model.state import Action, GameStateTemplate

class GameTreeNode:

    def __init__(self, state: GameStateTemplate, action, depth, parent) -> None:
        self.children = []
        self.state = state
        self.action = action
        self.parent = parent
        self.unvisited_actions = state.valid_actions()
        random.shuffle(self.unvisited_actions)
        self.stats = NodeStats(depth)
        # print(self.depth)

    def expand_new_node(self) -> 'GameTreeNode':
        action = self.unvisited_actions.pop()
        child = GameTreeNode(state=self.state.take_action(action), action=action,
                        depth=self.depth+1, parent=self)
        self.children.append(child)
        return child 
    
    def is_terminal(self)->bool:
        return self.state.game_over()
    
    def get_all_children_gen(self) -> 'Generator[GameTreeNode]':
        for action in self.state.valid_actions():
            yield GameTreeNode(state=self.state.take_action(action), action=action, depth=self.depth+1, parent=self)
        
        

    def set_as_root(self):
        self.parent == None

    @property
    def is_fully_expanded(self):
        return self.unvisited_actions == []

    def is_root(self):
        return self.depth == 0

    def update_stats(self, result):
        self.stats.update(result)

    # def find_node(self, action):
    #     nodes = list(filter(lambda x: x.action == action, self.children))
    #     if len(nodes) > 1:
    #         raise Exception(
    #             f'more than one child node with action {action} found')
    #     elif len(nodes) == 1:
    #         return nodes[0]

    #     nodes = list(filter(lambda x: x == action, self.unvisited_actions))

    #     if len(nodes) > 1:
    #         raise Exception(
    #             f'more than one child node with action {action} found')
    #     elif len(nodes) == 1:
    #         node = nodes[0]
    #         node._initialise_state()
    #         return node
    #     else:
    #         raise Exception(f'no child node found with action {action}')

    @property
    def n(self): return self.stats.n

    @property
    def depth(self): return self.stats.depth

    @property
    def q(self): return self.stats.q


@dataclass
class NodeStats:
    # TODO create stats class with n, depth, q and a setter method update_stats
    n: int = 0
    depth: int = 0
    total_results: int = 0

    def __init__(self, depth) -> None:
        self.depth = depth

    def update(self, result):
        self.n += 1
        self.total_results += result

    @property
    def q(self):
        """
        Return avg score over n simulations
        """
        return self.total_results / self.n

