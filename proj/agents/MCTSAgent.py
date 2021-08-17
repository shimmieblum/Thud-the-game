from abc import abstractmethod
import math
from optparse import OptionParser
import time
from typing import Callable
import random
from proj.agents.helper_files.gameTreeNode import GameTreeNode
from dataclasses import dataclass

from proj.agents.template import AgentTemplate
from proj.gameEngine.state import Action, GameStateTemplate, ThudGameState



class MCTS:
    """
    Monte-Carlo Tree Search. Provides methods to build and then traverse tree from a root node.
    Rollout policy is implemented by the user and passed as a parameter to the MCTS for greater flexibility.
    General process is: 
    1) SELECT: select a leaf node (or a node with unvisited children) 
    2) EXPAND: add a new child of that leaf node to the tree
    3) SIMULATE: using the rollout policy defined, simulate a game and record the results
    4) BACK-PROPOGATE: back propogate the results up the tree
    """

    def __init__(self, max_time, simulation_policy: Callable[[GameStateTemplate], GameStateTemplate], UCB_CONSTANT, max_depth=math.inf) -> None:
        """
        @param max_time: maximum time allowed per simulation
        @param max_depth: maximum depth to be sampled
        @param rollout_policy: rollout function taking a state 
        as an argument and returning the next state
        @param UCB_CONSTANT: constant in the UCB calculation
        """
        self.max_time = max_time
        self.max_depth = max_depth
        self.simulation_policy = simulation_policy
        self.UCB_CONSTANT = UCB_CONSTANT
        self.depth_offset = 0
        print(self.max_time)

    def search(self, root) -> 'GameTreeNode':
        """
        Search the tree according to the parameters set for the MCTS. After the search the best node will be returned 

        - after this method, the root node is the root of the tree which has been built. 

        @param root: the root node to search from
        @return: the best child node
        """
        self.stats = SearchStats()
        start_search = time.time()
        while time.time() - start_search < self.max_time:
            node = self.traverse(root)
            start_simulation = time.time()
            results = self.simulate(node)
            self.stats.update(simulation_time=time.time()
                              - start_simulation, depth=node.depth)
            self.back_propogate_results(results, node)

        self.stats.update(search_time=time.time()
                          - start_search)
        self.save_stats_to_file()
        return self.select_best_child(root)

    @property
    def nodes_searched(self):
        return self.stats.iterations

    def traverse(self, node):
        while node.is_fully_expanded and node.depth < self.max_depth + self.depth_offset:
            node = self.best_child(node)

        return self.select_unvisited(node) if len(node.unvisited_actions) > 0 else node

    def best_child(self, node):
        try:
            return max(node.children, key=lambda child: self.ucb(child))
        except:
            return node

    def ucb(self, node: 'GameTreeNode'):
        return node.q + self.UCB_CONSTANT * math.sqrt(math.log(node.parent.n) / node.n)

    def simulate(self, node):
        state = self.simulation_policy(node.state.deepcopy())
        return state.results(node.state.turn)

    def select_unvisited(self, node: 'GameTreeNode'):
        child = node.expand_new_node()
        return child

    def back_propogate_results(self, result, node):
        while True:
            node.update_stats(result)
            # break at the root
            if node.parent == None:
                break
            # print(node)
            node = node.parent

    def select_best_child(self, root):
        if root.is_root():
            return max(root.children, key=lambda child: child.n)

    def save_stats_to_file(self):
        with open('mctsData.txt', 'a') as o:
            o.write('\n'+repr(self.stats))




@dataclass(init=False)
class SearchStats:
    iterations: int = 0
    tree_size: int = 0
    simulation_time: float = 0
    best_depth_reached: int = 0
    total_search_time: float = 0

    def update(self, simulation_time=0, depth=0, search_time=0):
        self.iterations += 1
        self.simulation_time += simulation_time
        self.best_depth_reached = max(depth, self.best_depth_reached)
        self.total_search_time += search_time
    
        
    def __repr__(self) -> str:
        return ', '.join((
                str(self.iterations),
                str(round(self.total_search_time,2)),
                str(round(self.simulation_time,2))
                ))




class MCTSAgentTemplate(AgentTemplate):
    def __init__(self, name, agentClassName, max_time=10, max_depth=math.inf) -> None:
        super().__init__(name, agentClassName)
        self.MCTS = MCTS(max_time=max_time, max_depth=max_depth,
                         simulation_policy=self.simulation_policy, UCB_CONSTANT=2)
        self.root = None

    @abstractmethod
    def simulation_policy(self, state: GameStateTemplate) -> GameStateTemplate:
        """
        @param state: A clean state (ie not one in the game tree) to run simulation on.
        @return: the end state after running a simulation of a game.
        """
        pass

    def act(self, state: GameStateTemplate, game_number: int, wins: dict, stats) -> Action:
        # currently, a new root is created each calll.
        # this can be improved by saving the root as a class variable
        # and finding the new node each time an action is taken
        # if self.root == None:
        self.root = GameTreeNode(state=state, action=None, depth=0, parent=None)
        best_child = self.MCTS.search(self.root)
        nodes_searched = self.MCTS.nodes_searched
        stats.update_stats(self.name, add_nodes=nodes_searched)
        # self.root = self.root.find_node(best_child.action)
        return best_child.action


class MCTSRandAgent(MCTSAgentTemplate):
    def __init__(self, name, agentClassName, max_time=10, max_depth=math.inf) -> None:
        super().__init__(name, agentClassName, max_time=max_time, max_depth=max_depth)

    def simulation_policy(self, state: GameStateTemplate) -> GameStateTemplate:
        while not state.game_over():
            state = state.take_action_on_state(
                random.choice(state.valid_actions()))
        return state


class MCTSUnequalAgent(MCTSAgentTemplate):
    def __init__(self, name, agentClassName, max_time=10, max_depth=math.inf) -> None:
        super().__init__(name, agentClassName, max_time=max_time, max_depth=max_depth)

    def simulation_policy(self, state: GameStateTemplate) -> Action:
        while not state.game_over():
            actions = []
            while(actions == []):
                actions = state.get_actions_from_loc(
                    *random.choice(state.get_locations(state.turn)))
            state = state.take_action_on_state(random.choice(actions))
        return state
