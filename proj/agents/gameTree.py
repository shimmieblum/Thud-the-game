from typing import Generator
from proj.model.state import Action, GameState

 
class Node:
    def __init__(self, value_fn, action, state:GameState, depth) -> None:
        '''
        Node class for a game tree
        @param value_fn: function takes a node as a parameter and evaluates that node
        @param action: the action taken to reach this node
        @param state: the state reached at this node
        @param depth: the level this node is in the tree
        '''
        self.value_fn = value_fn
        self.action = action
        self.state = state
        self.depth = depth
        self.__children = self.state.get_subsequent_states()
        

    def get_children(self)-> 'Generator[Node]':
        '''
        Generator yielding Nodes for each subsequent state from this one.
        The value functions are taken from the parent
        '''
        for state, action in self.__children:
            yield Node(value_fn=self.value_fn, action=action, state=state, depth=self.depth+1)
    
    def get_val(self) -> float:
        return self.value_fn(self)
        
    def is_leaf(self) -> bool:
        return self.state.game_over()
    
from abc import abstractmethod 

class Tree:
    def __init__(self, state, value_fn) -> None:
        '''
        General Tree class.
        Children can overide get_best_action() method to search the tree and get the best results   
        @param state: the state for the root node
        @param value_fn: a function used to evaluate each node. Takes a Node as a parameter 
        '''
        self.value_fn = value_fn
        self.root = Node(value_fn=value_fn, state=state, action=None, depth=0)
        
    def reroot(self, action_path):
        '''
        Follow path of actions from the root to a new node and reroot at the new node
        @param action_path: list of actions to follow
        '''
        for action in action_path:
            self.root = filter(lambda x: x.action == action, self.root.__children)[0]
            
            
    @abstractmethod
    def get_best_action(self, **args)-> Action:
        '''
        Implement this method to search the tree
        '''
        pass
