from typing import NoReturn

import time
from .state import Action, GameState
from .enums import Piece
from ..userInterfaces.userInterface import UserInterfaceTemplate

'''=== code for a match ==='''

def play_match(best_of, player1, player2, ui:UserInterfaceTemplate, game_length, delay) -> dict:
    '''
    play a match of a given number of games, alternating each player each game.
    the winner wins the most games.
    @param best_of: the max number of games to play
    @player1
    @player2
    @ui: the userinterface to use
    @game_length: the number of turns per game
    @return: the dictionary of wins for each player
    '''
    
    wins = {player1: 0, player2: 0, 'draw': 0}
    ui.start_message()
    dwarf_player = player1
    troll_player = player2
    for game_number in range(1,best_of + 1):
        if ui.quit: break
        __play_game(dwarf_player,troll_player, ui, game_length, game_number, best_of, wins, delay)
        if __match_over(wins, best_of):
            break
        else: 
            dwarf_player,troll_player = troll_player, dwarf_player
    ui.end_of_match(wins,best_of)
    return wins
    
def __match_over(wins, num_games)-> bool:
    ''' check if one player has won the match according the the total match length 
    @param wins: the win dictionary
    @param num_games: total number of games to be played
    @return: whether the match is over or not
    '''
    games = num_games - wins['draw']
    for player, num_wins in wins.items():
        if player != 'draw' and num_wins > games/2: return True
    else: return False
            
'''=== code for a game ==='''


def __play_game(dwarf_player, troll_player, ui:UserInterfaceTemplate, game_length, game_number, best_of, wins, delay):
    '''
    play a single game, starting with the dwarf player. 
    each player makes its move and this continues until specified number of moves taken or one type has no pieces left
    @param dwarf_player: the dwarf player
    @param troll_player
    @param ui
    @param game_length: number of turns in the game
    @param game_number: total number of games played so far
    @param total_games: the number of games to be played
    @param wins: win dictionary
    '''
    state = GameState()
    players = {Piece.DWARF: dwarf_player, Piece.TROLL: troll_player, 'draw':'draw'}
    ui.new_game(dwarf_player, troll_player, game_length, game_number, wins)
    action = None
    for turn_number in range(1,game_length+1):
        st = time.time()
        ui.begin_turn(state, turn_number, game_length, game_number, best_of , wins, dwarf_player, troll_player, action)
        action = players[state.turn].act(state, game_number, wins)
        state = __perform_action(state, action)
        while(time.time() - st < delay): ... 
        if __game_over(state): break
    winning_piece = __winner(state)
    winner = players[winning_piece]
    wins[winner] += 1
    ui.end_game(wins, winning_piece)


def __perform_action(state, action:Action) -> GameState:
    next_state = GameState(grid=state.grid.deepcopy(), turn_number=state.turn_number, previous_state=state, captured=state.captured.copy())
    
    (from_x, from_y), (to_x, to_y), capture = action.from_loc, action.to_loc, action.capture
    
    for x,y in capture: 
        captured_piece = next_state.grid.remove_piece(x,y)
        if captured_piece in [Piece.TROLL, Piece.DWARF]: 
            next_state.captured[captured_piece] += 1
        
    next_state.grid.move_piece(from_x, from_y, to_x, to_y)
    next_state.next_move()
    return next_state

def __game_over(state:GameState)-> bool:
    '''
    check if no more pieces of a specific type remaining
    '''
    return len(state.trolls()) == 0 or len(state.dwarves()) == 0

def __winner(state:GameState) -> '(Piece | str)':
    ''' 
    check who the winner is
    @return: 
        dwarf winner => Piece.DWARF  || 
        troll win => Piece.TROLL || 
        draw => 'draw' 
    '''
    if len(state.trolls()) * 4 > len(state.dwarves()): return Piece.TROLL
    elif len(state.trolls()) * 4 < len(state.dwarves()): return Piece.DWARF
    else: return 'draw'