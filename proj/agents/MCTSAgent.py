import random
import math
from typing import Callable

from dataclasses import dataclass
from proj.model.match import GameStats
from random import random
import time

from abc import abstractmethod, abstractproperty
from proj.agents.template import ThudAgentTemplate
from proj.model.enums import Piece
from proj.model.state import Action, GameStateTemplate


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

    def __init__(self, max_time, max_depth, rollout_policy: Callable[[GameStateTemplate], GameStateTemplate]) -> None:
        """
        @param max_time: maximum time allowed per simulation
        @param max_depth: maximum depth to be sampled
        @param rollout_policy: rollout function taking a state 
        as an argument and returning the next state

        """

        self.max_time = max_time
        self.max_depth = max_depth
        self.rollout_policy = rollout_policy

    def search(self, root):
        """
        @param root: the root node to search from
        """
        start_time = time.time()
        while time.time() - start_time < self.max_time:
            node = self.traverse(root, self.max_depth)
            results = self.simulate(node)
            self.back_propogate_results(results, node)

        return self.select_best_child(root)

    def traverse(self, node):
        while node.is_fully_expanded and node.depth < self.max_depth:
            node = self.best_child(node)

        return self.select_unvisited(node) if len(node.children) > 0 else node

    def best_child(self, node):
        try:
            return max(node.children, key=lambda child: self.ucb(child))
        except:
            return node

    def simulate(self, node):
        state = node.state.deepcopy()
        while not state.game_over():
            state = self.rollout_policy(state)
        return state.results()

    def select_unvisited(self, node):
        child = node.visit_univisited_node()
        return child

    def back_propogate_results(self, result, node):
        while not node.is_root():
            node.upate_stats(result)
            node = node.parent

    def select_best_child(self, root):
        if root.is_root():
            return max(root.children, lambda child: child.n)


class MCTNodeTemplate:

    def __init__(self, state: GameStateTemplate, action, depth, parent) -> None:
        self.children = []
        self.state = state
        self.action = action
        self.parent = parent
        self.unvisited_nodes = [MCTNodeTemplate(state=None, action=action,
                                                depth=self.stats.depth + 1, parent=self)
                                for action in random.shuffle(state.valid_actions())]
        self.stats = MCTSStats(depth)

    def visit_unvisited_node(self) -> 'MCTNodeTemplate':
        child = self.unvisited_nodes.pop()
        child._initialise_state()
        self.children.append(child)
        return child

    def _initialise_state(self):
        self.state = self.parent.state.take_action(self.action)

    @property
    def is_fully_expanded(self):
        return self.unvisited_nodes is []

    def is_root(self):
        return self.depth == 0

    def update_stats(self, result):
        self.stats.update(result)
        
    @property
    def n(self): return self.stats.n
    
    @property
    def depth(self): return self.stats.depth
    
    @property
    def q(self): return self.stats.q


@dataclass
class MCTSStats:
    # TODO create stats class with n, depth, q and a setter method update_stats
    n:int
    depth: int
    total_results: int
    
    def __init__(self, depth) -> None:
        self.depth = depth
    
    def update_stats(self, result):
        self.n += 1
        self.q += result

    @property
    def q(self):
        """
        Return avg score over n simulations
        """
        return self.q / self.n
        


class MCTSNodeTemplate:

    @abstractmethod
    def __init__(self, action, state: GameStateTemplate, depth, parent) -> None:
        pass

    @abstractmethod
    def value(self, piece):
        pass

    @abstractmethod
    def get_state(self):
        pass

    @abstractmethod
    def select_random_child(self) -> 'MCTSNode':
        pass

    @abstractmethod
    def expand_node(self) -> int:
        pass

    @abstractmethod
    def is_leaf(self):
        pass

    @abstractmethod
    def update_and_back_propogate(self, troll_score, dwarf_score):
        pass


class MCTSTreeTemplate:

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def chose_best_node(self):
        pass

    @abstractmethod
    def run_simulations(self):
        pass

    @abstractmethod
    def find_leaf(self, node: 'MCTSNode') -> 'MCTSNode':
        pass

    @abstractmethod
    def UCB1(self, parent_node, node) -> float:
        pass


class MCTSNode:
    def __init__(self, action, state: GameStateTemplate, depth, parent) -> None:
        """
        Node class for MCTS. 
        Nodes are created without a state and they are generated when needed
        @action: the action taken to reach this node
        @param state: the state this node represents
        @paramm value_fn: the evaluation function used to evaluate the node, takes a node as argument
        @param depth: the depth of this node 
        @param parent: this nodes parent node
        """

        self.action = action
        self.__state = state
        self.parent = parent
        # results are the score for each side after the rollout
        self.results = {Piece.DWARF: 0, Piece.TROLL: 0}
        self.d = depth
        # self.unexplored_actions = random.shuffle(list(state.valid_actions()))
        self.children = []
        self.N = 0

    def value(self, piece):
        """
        Return the value of this node for each piece based on the simulations performed
        @param piece: the current turns piece type
        """
        if self.N == 0:
            return 0
        else:
            offset = 1 if piece == Piece.DWARF else -1
            return offset * (self.results[Piece.DWARF] - self.results[Piece.TROLL])

    def get_state(self):
        """
        Initialise the state achieved by the action and return.
        """
        if self.__state == None:
            self.__state = self.parent.get_state().take_action(self.action)
        return self.__state

    def select_random_child(self) -> 'MCTSNode':
        """
        Select a random child, initiate the state and return
        @return: a random child
        """
        node = random.choice(self.children)
        node.get_state()
        return node

    def expand_node(self) -> int:
        """
        Expand node with a new child for each possible action
        @return: the number of new nodes added
        """
        state = self.get_state()
        if self.is_leaf():
            self.children = [MCTSNode(action=action, state=None, depth=self.d+1, parent=self)
                             for action in state.valid_actions()]
        return len(self.children)

    def is_leaf(self):
        return len(self.children) == 0

    def update_and_back_propogate(self, troll_score, dwarf_score):
        """
        increment visits to this node and increase scores by the new scores found
        """
        self.N += 1
        self.results[Piece.TROLL] += troll_score
        self.results[Piece.DWARF] += dwarf_score
        if self.parent:
            self.parent.update_and_back_propogate(troll_score, dwarf_score)


class MCTSTree:
    def __init__(self, state, simulation_fn,
                 simulations_per_turn, max_time) -> None:
        """
        Tree for MCTS 
        @param state: the starting state for the root node
        @param simulation_fn: function taking an MCTS node as parameter and returning a tuple: (dwarf_score, troll_score)
        @param simulations_per_turn: how many simulations should take place in a turn
        @param max_time: max time in seconds for a turn 
        """
        self.root = MCTSNode(None, state=state, depth=0, parent=None)
        self.simulate = simulation_fn
        self.max_simulations = simulations_per_turn
        self.turn = state.turn
        self.max_time = max_time
        self.size = 1

    def chose_best_node(self):
        """
        Select the best child from the root - used to select the final action to take
        """
        return max(self.root.children, key=lambda x: x.N)

    def run_simulations(self):
        """
        Run simulations in the tree until max simulations have been performed or time has run out
        """
        simulation_number = 0
        start_time = time.time()
        # Continue simulations until time is used up or max simulations have been completed
        while simulation_number < self.max_simulations and time.time() - start_time < self.max_time:
            # Allow the root to find the best child node
            current_node = self.find_leaf(self.root)
            # print(current_node.d)
            # print(current_node.N)
            # If this node has been rolled out before, expand, select a child at random and simulate on that
            if current_node.N > 0:
                self.size += current_node.expand_node()
                current_node = current_node.select_random_child()
            dwarf_score, troll_score = self.simulate(current_node)
            current_node.update_and_back_propogate(
                dwarf_score=dwarf_score, troll_score=troll_score)
            # print(current_node.N)
            simulation_number += 1
        print(f'simulatiions run = {simulation_number}')

    def find_leaf(self, node: MCTSNode) -> MCTSNode:
        """
        Branch out from this node selecting the best child nodes until a leaf is reached
        @param node: root node to search from
        @return: the leaf found 
        """
        if node.is_leaf():
            return node
        else:
            return self.find_leaf(max(node.children, key=lambda child: self.UCB1(parent_node=node, node=child)))

    def UCB1(self, parent_node, node) -> float:
        if node.N == 0:
            return math.inf
        else:
            return node.value(self.turn) + 2 * math.sqrt(math.log(node.N) / parent_node.N)


class MCTSAgent(ThudAgentTemplate):
    def __init__(self, name, agentClassName) -> None:
        super().__init__(name, agentClassName)
        self.MAX_TIME = 10
        self.depth_reached = 0
        self.simulation_time = 0

    def simulate(self, node: MCTSNode) -> 'tuple[float, float]':
        self.nodes_simulated += 1
        self.depth_reached = max(self.depth_reached, node.d)
        start = time.time()
        sim_state = node.get_state().deepcopy()
        while not sim_state.game_over():
            actions = sim_state.valid_actions()
            action = random.choice(actions)
            sim_state.take_action_on_state(action)
        results = sim_state.score(Piece.DWARF), sim_state.score(Piece.TROLL)

        self.simulation_time += time.time() - start
        return results

    def act(self, state: GameStateTemplate, game_number:
            int, wins: dict, stats: GameStats) -> Action:
        turn = state.turn
        self.nodes_simulated = 0
        self.simulation_time = 0
        self.tree = MCTSTree(
            state, self.simulate, simulations_per_turn=math.inf, max_time=self.MAX_TIME)
        self.tree.run_simulations()
        child = self.tree.chose_best_node()
        print(f'tree size = {self.tree.size}')
        print(f'total simulation time = {self.simulation_time}')
        print(f'best depth reached = {self.depth_reached}')

        if turn == Piece.DWARF:
            stats.total_nodes_searched_dwarf += self.nodes_simulated
        else:
            stats.total_nodes_searched_troll += self.nodes_simulated

        # # reroot with the chosen state so the root matches the next players state
        # self.tree.reroot_from_state(child.state)
        return child.action


class UnfairMCTSAgent(MCTSAgent):
    def __init__(self, name, agentClassName) -> None:
        super().__init__(name, agentClassName)

    def simulate(self, node: MCTSNode) -> 'tuple[float, float]':
        self.depth_reached = max(self.depth_reached, node.d)
        self.nodes_simulated += 1
        start = time.time()
        sim_state = node.get_state().deepcopy()
        start = time.time()
        while not sim_state.game_over():
            actions = []
            while actions == []:
                x, y = random.choice(sim_state.get_locations(sim_state.turn))
                actions = sim_state.__get_actions_from_loc(x, y)
            action = random.choice(actions)
            sim_state.take_action_on_state(action)
        # print(time.time()-start)
        results = sim_state.score(Piece.DWARF), sim_state.score(Piece.TROLL)
        self.simulation_time += time.time() - start
        return results
