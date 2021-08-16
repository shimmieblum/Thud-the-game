
import time
from proj.gameEngine.state import ThudGameState
from .matchStats import MatchStats
from proj.gameEngine.enums import Piece
from proj.userInterfaces.userInterface import UserInterfaceTemplate

"""=== code for a match ==="""

welcome_message = r"""

Welcome to
 ________   _   _   _   _   ____     _
|__    __| | |_| | | | | | |  _ \   | | 
   |  |    |  _  | | |_| | | |_) |  |_|
   |__|    |_| |_| |_____| |____/   (=)
 _______________________________________
|_______________________________________|
By Trevor Truran 
Inspired by Terry Prachett
"""
    

def play_match(total_games, player1, player2, ui: UserInterfaceTemplate, game_length) -> dict:
    """
    play a match of a given number of games, alternating each player each game.
    the winner wins the most games.
    @param best_of: the max number of games to play
    @player1
    @player2
    @ui: the userinterface to use
    @game_length: the number of turns per game
    @return: the dictionary of wins for each player
    """
    
    stats = MatchStats(
        total_games, player1=player1.agentClassName, player2=player2.agentClassName)
    wins = {player1: 0, player2: 0, 'draw': 0}
    ui.start_message(welcome_message)
    dwarf_player = player1
    troll_player = player2
    for game_number in range(1, total_games + 1):
        __play_game(dwarf_player=dwarf_player, troll_player=troll_player, 
                    ui=ui, game_length=game_length, game_number=game_number, 
                    total_games=total_games, wins=wins,  
                    stats=stats)
        dwarf_player, troll_player = troll_player, dwarf_player
    ui.end_of_match(wins, total_games)
    __save_stats(stats)
    return wins


"""=== code for a game ==="""


def __play_game(dwarf_player, troll_player, ui: UserInterfaceTemplate,
                game_length, game_number, total_games, wins, stats: MatchStats):
    """
    play a single game, starting with the dwarf player. 
    each player makes its move and this continues until specified number of moves taken or one type has no pieces left
    @param dwarf_player: the dwarf player
    @param troll_player
    @param ui
    @param game_length: number of turns in the game
    @param game_number: total number of games played so far
    @param total_games: the number of games to be played
    @param wins: win dictionary
    """
    # initial state
    state = ThudGameState(turns_per_game=game_length)
    # create players dictionary
    players = {Piece.DWARF: dwarf_player,
               Piece.TROLL: troll_player, 'draw': 'draw'}
    ui.new_game(dwarf_player, troll_player, game_length, game_number, wins)
    action = None
    # play game alternatinde players until no more turns remain
    while not state.game_over():
        start_time = time.time()
        ui.begin_turn(state=state, turn_number=state.turn_number,
                      game_length=game_length, game_number=game_number,
                      best_of=total_games, wins=wins, dwarf_player=dwarf_player,
                      troll_player=troll_player, prev_action=action)
        player = players[state.turn]
        action = player.act(state, game_number, wins, stats)
        if action not in state.valid_actions(): 
            # if this action is invalid, don't allow the action to take place. 
            # instead continue, requiring a new action to be taken. 
            ui.display_invalid_action(action)
            continue
        time_taken = time.time() - start_time
        # update time for the turn for the correct type
        stats.update_stats(player_name=player.name,
                           add_time=time_taken, add_move=1)
        # generate new state
        state = state.take_action(action)

    winning_piece = state.winner()

    stats.update_stats(players[Piece.DWARF].name, add_score=state.score(Piece.DWARF),
                       add_wins_dwarf=1 if winning_piece == Piece.DWARF else 0)
    stats.update_stats(players[Piece.TROLL].name, add_score=state.score(Piece.TROLL),
                       add_wins_troll=1 if winning_piece == Piece.TROLL else 0)

    winner = players[winning_piece]
    wins[winner] += 1
    ui.end_game(wins, winning_piece)


def __save_stats(stats):
    with open('results.txt', 'a') as o:
        o.write('\n\n        =================================\n\n')
        o.write(repr(stats))

