from os import stat
from dataclasses import dataclass
from typing import NoReturn

import time
from .state import Action, GameState
from .enums import Piece
from ..userInterfaces.userInterface import UserInterfaceTemplate

'''=== code for a match ==='''


def play_match(best_of, player1, player2, ui: UserInterfaceTemplate, game_length, delay) -> dict:
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
    for game_number in range(1, best_of + 1):
        if ui.quit:
            break
        __play_game(dwarf_player, troll_player, ui, game_length,
                    game_number, best_of, wins, delay)
        if __match_over(wins, best_of):
            break
        else:
            dwarf_player, troll_player = troll_player, dwarf_player
    ui.end_of_match(wins, best_of)
    return wins


def __match_over(wins, num_games) -> bool:
    ''' check if one player has won the match according the the total match length 
    @param wins: the win dictionary
    @param num_games: total number of games to be played
    @return: whether the match is over or not
    '''
    games = num_games - wins['draw']
    for player, num_wins in wins.items():
        if player != 'draw' and num_wins > games/2:
            return True
    else:
        return False


'''=== code for a game ==='''


def __play_game(dwarf_player, troll_player, ui: UserInterfaceTemplate,
                game_length, game_number, best_of, wins, delay):
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
    # initial state
    state = GameState(turns_per_game=game_length)
    # init stats
    stats = GameStats(game_num=game_number, total_games=best_of,
                      troll_agent=troll_player.agentClassName,
                      dwarf_agent=dwarf_player.agentClassName,
                      total_turns=game_length)
    # create players dicrtionary
    players = {Piece.DWARF: dwarf_player,
               Piece.TROLL: troll_player, 'draw': 'draw'}
    ui.new_game(dwarf_player, troll_player, game_length, game_number, wins)
    action = None
    # play game alternatinde players until no more turns remain
    while not state.game_over():
        start_time = time.time()
        piece = state.turn
        ui.begin_turn(state=state, turn_number=state.turn_number,
                      game_length=game_length, game_number=game_number,
                      best_of=best_of, wins=wins, dwarf_player=dwarf_player,
                      troll_player=troll_player, action=action)
        action = players[state.turn].act(state, game_number, wins, stats)
        end_time = time.time() - start_time
        # update time for the turn for the correct type
        if piece == Piece.DWARF:
            stats.dwarf_time_total += end_time
        else:
            stats.troll_time_total += end_time
        # generate new state
        state = state.take_action(action)
        
    stats.troll_score = state.troll_score()
    stats.dwarf_score = state.dwarf_score()
    winning_piece = state.winner()

    winner = players[winning_piece]
    wins[winner] += 1
    ui.end_game(wins, winning_piece)

    with open('results.txt', 'a') as o:
        o.write('\n')
        o.write(repr(stats))

@dataclass
class GameStats:

    """
    This class is used to store the following stats about a game which is then saved to a designated text file:

    - game_num (int)
    - total_games (int)
    - nodes_searched (int)
    - time_per_move (float)
    - agent_type (str)
    - opponent_type (str)
    - agent_piece (Piece)
    - score (int)
    - opponent_score (int)
    """
    game_num: int
    total_games: int
    troll_agent: str
    dwarf_agent: str
    total_turns: int

    dwarf_score: int = 0
    troll_score: int = 0

    total_nodes_searched_dwarf: int = 0
    total_nodes_searched_troll: int = 0
    dwarf_time_total: float = 0
    troll_time_total: float = 0

    def __init__(self, game_num: int, total_games: int, troll_agent: str, dwarf_agent: str, total_turns: int) -> None:
        self.game_num = game_num
        self.total_games = total_games
        self.troll_agent = troll_agent
        self.dwarf_agent = dwarf_agent
        self.total_turns = total_turns

    def dwarf_nodes_searched_per_move(self) -> float:
        return self.total_nodes_searched_dwarf / (self.total_turns / 2)

    def troll_nodes_searched_per_move(self) -> float:
        return self.total_nodes_searched_troll / (self.total_turns / 2)

    def dwarf_time_per_move(self) -> float:
        return self.dwarf_time_total / (self.total_turns / 2)

    def troll_time_per_move(self) -> float:
        return self.troll_time_total / (self.total_turns / 2)
