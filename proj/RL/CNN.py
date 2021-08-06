import imp
import math
from operator import index

from tensorflow.python.ops.gen_nn_ops import DataFormatDimMap
from proj.userInterfaces.GUI import GUI
from proj.agents.randomAgent import BetterRandomAgent, RandomAgent
from proj.model.enums import Piece
import random

from proj.agents.template import ThudAgentTemplate
import tensorflow as tf
import numpy as np
from tensorflow.keras import layers
from tensorflow.python.keras import callbacks, models
from tensorflow.python.keras.engine.input_layer import InputLayer
from tensorflow.python.ops.gen_array_ops import shape
from ..model.state import Action, GameState
from pandas import DataFrame
from ..model import match

def get_dataset(num_games, states_per_game, agent1, agent2):
    data = []
    print(f'''creating dataset: 
{num_games} games
{states_per_game} states per game
player1: {agent1},
player2: {agent2}
''')
    dwarf_player, troll_player = agent1, agent2
    for _ in range(num_games):
        data = game(dwarf_player, troll_player, states_per_game, data)
        dwarf_player, troll_player = troll_player,dwarf_player
        
    dataframe = DataFrame(data, columns=['x','y'])
    
    print(f'''final dataframe shape: {dataframe.shape}''')
    return dataframe

        
def game(dwarf_agent:ThudAgentTemplate, troll_agent:ThudAgentTemplate, states_per_game, data:list):
    piece_values = {Piece.DWARF:1, Piece.TROLL: -1, 'draw':0}
    print('playing game')
    states = []
    state = GameState()
    
    # game is 70 turns long
    player, other = dwarf_agent, troll_agent
    # select whihch states to be recorded between 1 & 70
    states_to_save = random.choices(range(1, 70), k=states_per_game) 
    print(states_to_save)
    for g in range(70):
        print(g)
        # append representation of states chosen
        if g in states_to_save: states.append(state.get_representation())
        action = player.act(state=state, game_number=1, wins={dwarf_agent:0, troll_agent:0, 'draw':0})
        state = state.take_action(action)
        player,other = other, player
        if state.game_over(): break
    winner = state.winner()
    # save the states and their results in the dataframe
    for state in states: data.append((state, piece_values[ winner]))
    return data



# class Model:
#     ''' 
    
#     1) create CNN model
#     2) allow input of a state in correct format
#     3) output of a valuation of the state
    
#     '''
    
    
    
    
def _model(example_state:GameState, conv_depth):
    '''
    x_in = last 3 states
    each state = list 3 arrays:
       1) array with dwarf locations
       2) array with troll locations 
       3) array representing who's turn it is:
            - 0's for dwarf turn
            - 1's for trolls turn
            
    ''' 
    print('building model...')
    input_shape = example_state.get_representation().shape
    input_layer = layers.Input(shape=input_shape)
    x = layers.Conv2D(filters=10, kernel_size=3, padding='same', data_format='channels_first')(input_layer)
    x = layers.BatchNormalization()(x)
    previous = x
    for _ in range(conv_depth):
        x = layers.Activation('relu')(x)
        x = layers.Conv2D(filters=10, kernel_size=3, padding='same', data_format='channels_first')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Add()([x, previous])
        x = layers.Activation('relu')(x)
    x = layers.Flatten()(x)
    x = layers.Dense(1, 'sigmoid')(x)
    
    return models.Model(inputs=input_layer, outputs=x)



def train_model(dataset:DataFrame) -> models.Model:
    '''
    1) create/load model
    2) run training proceedure
    3) record the training process
    4) return the trained model
    '''
    model = _model(GameState(), 2)
    x_train, y_train = dataset.pop('x'), dataset.pop('y')
    y_train = np.asarray(y_train / abs(y_train).max() / 2 + 0.5, dtype=np.float32)
    
    model.compile(optimizer=tf.keras.optimizers.Adam(5e-4), loss='mean_squared_error')
    model.summary()
    print('training model...')
    # TODO: sort out x & y structures so the model can train on them
     
    model.fit(x_train, y_train,
          batch_size=2048,
          epochs=1000,
          verbose=1,
          validation_split=0.1,
          callbacks=[callbacks.ReduceLROnPlateau(monitor='loss', patience=10),
                     callbacks.EarlyStopping(monitor='loss', patience=15, min_delta=1e-4)])

    model.save('model.h5')
    return model

class CNNAgent(ThudAgentTemplate):
    def __init__(self, name, agentClassName) -> None:
        super().__init__(name, agentClassName)
        self.model = train_model(get_dataset(30, 10, BetterRandomAgent('player1', 'BetterRandomAgent'), BetterRandomAgent('player2', 'BetterRandomAgent')))
        
    def act(self, state: GameState, game_number: int, wins: dict) -> Action:
        '''
        
        Offset will normalise the prediction so highest is always better.
        For each move: 
            1) get all subsequent states
            2) evaluate with the CNN model
            3) return the action leading to the highest valued state
        '''
        offset = 1 if state.turn == Piece.DWARF else -1
        best_value, best_action = -math.inf, Action((), (), set(), None)
        for subs_state, action in state.get_subsequent_states():
            x = subs_state.get_representation()
            prediction = offset * self.model.predict([x])    
            if prediction > best_value: best_action = action
        return best_action
    
def run():
    cnn_agent = CNNAgent('player1', 'CNNAgent')
    results = match.play_match(5,  player1= cnn_agent, player2= RandomAgent('player2', 'RandomAgent'), ui=GUI(), game_length=70, delay=0)
    print(results)