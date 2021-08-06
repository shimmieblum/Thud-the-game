
from typing import Generator
from proj.model.enums import Piece
from proj.model.state import Action, GameState
from proj.agents.template import ThudAgentTemplate

import math, time

# from dataclasses import dataclass


class MiniMaxAgent(ThudAgentTemplate):
    def __init__(self, name, agentClassName) -> None:
        super().__init__(name, agentClassName)
        
    def act(self, state: GameState, game_number: int, wins: dict) -> Action:
        offset = 1 if state.turn == Piece.DWARF else -1
        def value_fn(state:GameState):
            return offset * (state.dwarf_score() - state.troll_score())
            
        tree = Tree(value_fn=value_fn, state=state, max_depth=4, max_time=10, optimisation=[], display_process=False)
        return tree.get_best_action()
    

class MiniMaxABAgent(ThudAgentTemplate):
    def __init__(self, name, agentClassName) -> None:
        super().__init__(name, agentClassName)
        
    def act(self, state: GameState, game_number: int, wins: dict) -> Action:
        offset = 1 if state.turn == Piece.DWARF else -1
        def value_fn(state:GameState):
            return offset * (state.dwarf_score() - state.troll_score())
            
        tree = Tree(value_fn=value_fn, state=state, max_depth=2, max_time=10, optimisation=['AlphaBeta'], display_process=False)
        return tree.get_best_action()
    
class Node:
    def __init__(self, value_fn, action, state:GameState, depth) -> None:
        self.value_fn = value_fn
        self.action = action
        self.state = state
        self.depth = depth
        self.__children = self.state.get_subsequent_states()
        
    
    def get_children(self)-> 'Generator[Node]':
        for state, action in self.__children:
            yield Node(value_fn=self.value_fn, action=action, state=state, depth=self.depth+1)
    
    def get_val(self) -> float:
        return self.value_fn(self.state)
        
    def is_leaf(self) -> bool:
        return self.state.game_over()



class Tree:
    def __init__(self, value_fn, state, max_depth, max_time, optimisation, display_process=False) -> None:
        '''
        Optimisation methods available: 
            1. 'AlphaBeta' (default enabled)
            2. 
        
        @param value_fn: function taking state as a parameter to evaluate the value of the state and returning float
        @param state: the state acting as root
        @param max_depth: max depth to dig into tree
        @param max_time: max time to spent searching tree
        @param optimisation: list of optimisation techniques to use.
        
        '''
        self.root = Node(value_fn=value_fn, state=state, action=None, depth=0)
        self.max_depth = max_depth
        self.max_time = max_time
        self.optimisation = optimisation
        self.display_process = display_process
        self.ab_pruning = 'AlphaBeta' in optimisation 
        
        
    def get_best_action(self, )-> Action:
        self.nodes_visited = 0
        self.pruned = 0
        self.start = time.time()
        self.timeout = False
        _, node = self.get_maxi(self.root, alpha=-math.inf,beta=math.inf)
        print(f'timeout = {self.timeout}')
        print(f'nodes visited = {self.nodes_visited}')
        print(f'pruned = {self.pruned}')
        return node.action
        
    def get_mini(self, node:Node, alpha, beta)-> 'tuple[float, Node]':
        self.nodes_visited +=1
        if time.time()-self.start > self.max_time: 
            self.timeout = True
            return node.get_val(), node
            
        if node.depth == self.max_depth or node.is_leaf(): 
            return node.get_val(), node
        else:
            children = node.get_children()
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
                        self.pruned +=1
                        break
            if self.display_process: Display.display_mini(node, mini_value, mini_child)
            return mini_value, mini_child
    
    def get_maxi(self, node:Node, alpha, beta)-> 'tuple[float, Node]':
        self.nodes_visited +=1
        if time.time()-self.start > self.max_time: 
            self.timeout = True
            return node.get_val(), node
            
        if node.depth == self.max_depth or node.is_leaf(): 
            return node.get_val(), node
        else:
            children = node.get_children()
            maxi_value = -math.inf
            maxi_child = node
            for child in children:
                child_value,_ = self.get_mini(child, alpha=alpha, beta=beta)
                if child_value > maxi_value:
                    maxi_value = child_value
                    maxi_child = child
                if self.ab_pruning: 
                    alpha = max(alpha, child_value)
                    if alpha >= beta: 
                        self.pruned +=1
                        break
                
            if self.display_process: Display.display_maxi(node, maxi_value, maxi_child)
        return maxi_value, maxi_child
    
    
class Display:
    def display_maxi(node, maxi_value, maxi_child):
        Display.display(node,maxi_value, maxi_child, 'maxival')
        
    def display_mini(node, mini_value, mini_child):
        Display.display(node, mini_value, mini_child, 'minival')

    
    def display(node, c_val, child, stringterm):
        string = (f'''d: {node.depth}, {stringterm}: {c_val}''')
        print(string)
        # if c_val >=0: input(' ')
