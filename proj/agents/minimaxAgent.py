
from proj.agents.gameTreeNode import GameTreeNode
from proj.model.matchStats import MatchStats
from typing import Generator
from proj.model.enums import Piece
from proj.model.state import Action, GameStateTemplate
from proj.agents.template import ThudAgentTemplate

import math
import time


class MiniMaxAgent(ThudAgentTemplate):
    def __init__(self, name, agentClassName) -> None:
        super().__init__(name, agentClassName)

    def act(self, state: GameStateTemplate, game_number: int,
            wins: dict, stats: MatchStats) -> Action:
        piece = state.turn
        offset = 1 if state.turn == Piece.DWARF else -1

        def value_fn(state: GameStateTemplate):
            return offset * (state.score(Piece.DWARF) - state.score(Piece.TROLL))

        tree = MiniMaxSearch(value_fn=value_fn, state=state, max_depth=4,
                    max_time=10, optimisation=[], display_process=False)
        action = tree.get_best_action()
        if piece == Piece.DWARF:
            stats.total_nodes_searched_dwarf += tree.nodes_visited
        else:
            stats.total_nodes_searched_troll += tree.nodes_visited
        return action


class MiniMaxABAgent(ThudAgentTemplate):
    def __init__(self, name, agentClassName) -> None:
        super().__init__(name, agentClassName)

    def act(self, state: GameStateTemplate, game_number: int,
            wins: dict, stats: MatchStats) -> Action:
        piece = state.turn
        offset = 1 if state.turn == Piece.DWARF else -1

        def value_fn(state: GameStateTemplate):
            return offset * (state.score(Piece.DWARF) - state.score(Piece.TROLL))

        tree = MiniMaxSearch(value_fn=value_fn, state=state, max_depth=2,
                    max_time=10, optimisation=['AlphaBeta'], display_process=False)
        action = tree.get_best_action()
        stats.update_stats(self.name, add_nodes=tree.nodes_visited)
        return action


# class Node:
#     def __init__(self, value_fn, action, state: GameStateTemplate
#                  , depth) -> None:
#         self.value_fn = value_fn
#         self.action = action
#         self.state = state
#         self.depth = depth
#         self.__children = self.state.get_subsequent_states()

#     def get_children(self) -> 'Generator[Node]':
#         for state, action in self.__children:
#             yield Node(value_fn=self.value_fn, action=action, state=state, depth=self.depth+1)

#     def get_val(self) -> float:
#         return self.value_fn(self.state)

#     def is_terminal(self) -> bool:
#         return self.state.game_over()


class MiniMaxSearch:
    def __init__(self, value_fn, state, max_depth, max_time,
                 optimisation, display_process=False) -> None:
        """
        Optimisation methods available: 
            1. 'AlphaBeta' (default enabled)
            2. 

        @param value_fn: function taking state as a parameter to evaluate the value of the state and returning float
        @param state: the state acting as root
        @param max_depth: max depth to dig into tree
        @param max_time: max time to spent searching tree
        @param optimisation: list of optimisation techniques to use.

        """
        self.root = GameTreeNode(state=state, action=None, depth=0, parent=None)
        self.value_fn = value_fn
        self.max_depth = max_depth
        self.max_time = max_time
        self.optimisation = optimisation
        self.display_process = display_process
        self.ab_pruning = 'AlphaBeta' in optimisation

    def get_best_action(self, ) -> Action:
        self.nodes_visited = 0
        self.pruned = 0
        self.start = time.time()
        self.timeout = False
        _, node = self.get_maxi(self.root, alpha=-math.inf, beta=math.inf)
        print(f'timeout = {self.timeout}')
        print(f'nodes visited = {self.nodes_visited}')
        print(f'pruned = {self.pruned}')
        return node.action

    def get_mini(self, node: GameTreeNode, alpha, beta) -> 'tuple[float, GameTreeNode]':
        self.nodes_visited += 1
        if time.time()-self.start > self.max_time:
            self.timeout = True
            return self.value_fn(node.state), node

        if node.depth == self.max_depth or node.is_terminal():
            return self.value_fn(node.state), node
        else:
            children = node.get_all_children_gen()
            mini_value = math.inf
            mini_child = node
            for child in children:
                child_value, _ = self.get_maxi(child,  alpha=alpha, beta=beta)
                if child_value < mini_value:
                    mini_value = child_value
                    mini_child = child
                if self.ab_pruning:
                    beta = min(beta, child_value)
                    if alpha >= beta:
                        self.pruned += 1
                        break
            return mini_value, mini_child

    def get_maxi(self, node: GameTreeNode, alpha, beta) -> 'tuple[float, GameTreeNode]':
        self.nodes_visited += 1
        if time.time()-self.start > self.max_time:
            self.timeout = True
            return self.value_fn(node.state), node

        if node.depth == self.max_depth or node.is_terminal():
            return self.value_fn(node.state), node
        else:
            children = node.get_all_children_gen()
            maxi_value = -math.inf
            maxi_child = node
            for child in children:
                child_value, _ = self.get_mini(child, alpha=alpha, beta=beta)
                if child_value > maxi_value:
                    maxi_value = child_value
                    maxi_child = child
                if self.ab_pruning:
                    alpha = max(alpha, child_value)
                    if alpha >= beta:
                        self.pruned += 1
                        break
        return maxi_value, maxi_child


class Display:
    def display_maxi(node, maxi_value, maxi_child):
        Display.display(node, maxi_value, maxi_child, 'maxival')

    def display_mini(node, mini_value, mini_child):
        Display.display(node, mini_value, mini_child, 'minival')

    def display(node, c_val, child, stringterm):
        string = (f"""d: {node.depth}, {stringterm}: {c_val}""")
        print(string)
        # if c_val >=0: input(' ')
