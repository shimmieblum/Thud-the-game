from abc import abstractmethod
from asyncio.subprocess import PIPE
import math
import time

from proj.agents.template import ThudAgentTemplate
from proj.model.enums import Piece
from proj.model.state import Action, GameState


class MCTSNode:
    def __init__(self, action, state: GameState, depth, parent) -> None:
        '''
        Node class for MCTS. 
        @action: the action taken to reach this node
        @param state: the state this node represents
        @paramm value_fn: the evaluation function used to evaluate the node, takes a node as argument
        @param depth: the depth of this node 
        @param parent: this nodes parent node
        '''

        self.action = action
        self.state = state
        self.parent = parent
        # results are the score for each side after the rollout
        self.results = {Piece.DWARF: 0, Piece.TROLL: 0}
        self.d = depth
        self.children = []
        self.N = 0

    def value(self, piece):
        '''
        Return the value of this node for each piece based on the simulations performed
        @param piece: the current turns piece type
        '''
        if self.N == 0:
            return 0
        else:
            offset = 1 if piece == Piece.DWARF else -1
            return offset * (self.results[Piece.DWARF] - self.results[Piece.TROLL])

    def expand_node(self):
        if self.is_leaf():
            self.children = [MCTSNode(action=action, state=state, depth=self.d + 1, parent=self) for state, action in
                             self.state.get_subsequent_states()]

    def is_leaf(self):
        return len(self.children) == 0

    def back_propogate_results(self, troll_score, dwarf_score):
        '''
        increment visits to this node and increase scores by the new scores found
        '''
        self.N += 1
        self.results[Piece.TROLL] += troll_score
        self.results[Piece.DWARF] += dwarf_score
        if self.parent: self.parent.back_propogate_results(troll_score, dwarf_score)


from queue import Queue


class MCTSTree:
    def __init__(self, state, simulation_fn, simulations_per_turn, max_time) -> None:
        '''
        Tree for MCTS 
        @param state: the starting state for the root node
        @param simulation_fn: function taking an MCTS node as parameter and returning a tuple: (dwarf_score, troll_score)
        @param simulations_per_turn: how many simulations should take place in a turn
        @param max_time: max time in seconds for a turn 
        '''
        self.root = MCTSNode(None, state=state, depth=0, parent=None)
        self.max_simulations = simulations_per_turn
        self.turn = state.turn
        self.simulate = simulation_fn
        self.max_time = max_time
        self.depth_offset = 0

    def reroot(self, actions):
        ''''
        reroot tree after series of actions are taken
        @param actions: list of actions that have been taken
        '''
        for action in actions:
            self.root.expand_node()
            if self.root.is_leaf():
                break  # no subsequent states avaialable
            else:
                self.root = filter(lambda x: x.action == action, self.children)[0]

        self.turn = self.root.state.turn

    def reroot_from_state(self, state):
        '''
        search through all children of the root for this state and set as root
        allows the same tree to be used throughout the game
        '''
        queue = Queue()
        if self.root.state == state: return
        self.root.expand_node()
        for child in self.root.children:
            if state == child.state:
                self.root = child
                self.turn = state.turn
                break
        self.depth_offset += 1

    def best_child(self):
        return max(self.root.children, key=lambda x: x.value(self.turn))

    def run_simulations(self):
        '''
        run simulations in the tree until max simulations have been performed or time has run out
        '''
        simulation_number = 0
        start_time = time.time()
        while simulation_number < self.max_simulations and time.time() - start_time < self.max_time:
            current_node = self.select_child(self.root)
            current_node.expand_node()
            # current_node = random.choice(current_node.children)
            dwarf_score, troll_score = self.simulate(current_node)
            current_node.back_propogate_results(troll_score=troll_score, dwarf_score=dwarf_score)
            simulation_number += 1
        print(simulation_number)

    def select_child(self, node: MCTSNode) -> MCTSNode:
        if node.is_leaf():
            return node
        else:
            return self.select_child(max(node.children, key=lambda child: self.UCB1(parent_node=node, node=child)))

    def UCB1(self, parent_node, node) -> float:
        # try catch to cope with parent not being expanded yet
        # try: 
        if node.N == 0:
            return math.inf
        else:
            return node.value(self.turn) + 2 * math.sqrt(math.log(node.N) / parent_node.N)
    # except ZeroDivisionError: return math.inf


import random


class MCTSAgent(ThudAgentTemplate):
    def __init__(self, name, agentClassName) -> None:
        super().__init__(name, agentClassName)
        self.MAX_TIME = 30
        self.simulation_time = 0
        self.depth_reached = 0
    
    def simulate(self, node: MCTSNode) -> 'tuple[float, float]':
        self.depth_reached = max(self.depth_reached, node.d-self.tree.depth_offset)
        start = time.time()
        sim_state = node.state.deepcopy()
        while not sim_state.game_over():
            actions = sim_state.valid_actions()
            # random.shuffle(actions)
            # action = max(actions, key=lambda action: len(action.capture))
            action = random.choice(actions)
            sim_state.act_on_state(action)
        results = sim_state.dwarf_score(), sim_state.troll_score()
        self.simulation_time += time.time() - start
        return results

    def act(self, state: GameState, game_number: int, wins: dict) -> Action:
        self.simulation_time = 0
        # if this is one of the first turns, create a new tree. otherwise reroot the old one based on the new state. 
        if state.turn_number < 3:
            self.tree = MCTSTree(state, self.simulate, simulations_per_turn=math.inf, max_time=self.MAX_TIME)
        else:
            self.tree.reroot_from_state(state)
        assert state == self.tree.root.state
        self.tree.run_simulations()
        print(f' simulation time = {self.simulation_time}s')
        print(f'best depth reached = {self.depth_reached}')
        child = self.tree.best_child()
        # reroot with the chosen state so the root matches the next players state
        self.tree.reroot_from_state(child.state)
        return child.action
    
    
# class DirtyMCTSAgent(MCTSAgent):
#     def __init__(self, name, agentClassName) -> None:
#         super().__init__(name, agentClassName)
        
#     def simulate(self, node: MCTSNode) -> 'tuple[float, float]':
#         start = time.time()
#         sim_state = node.state.deepcopy()
#         while not sim_state.game_over():
#             if sim_state.turn == Piece.DWARF
#             # random.shuffle(actions)
#             # action = max(actions, key=lambda action: len(action.capture))
#             action = random.choice(actions)
#             sim_state.act_on_state(action)
#         results = sim_state.dwarf_score(), sim_state.troll_score()
#         print(time.time() - start)
#         return results    
    
