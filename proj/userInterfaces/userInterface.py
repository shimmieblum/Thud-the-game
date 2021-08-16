from abc import abstractmethod

from ..gameEngine.enums import Piece
from ..gameEngine.state import GameStateTemplate


class UserInterfaceTemplate:

    def __init__(self) -> None:
        self.quit = False

    @abstractmethod
    def start_message(self, welcome_message):
        """ Display the message when the match is first begun"""
        pass

    @abstractmethod
    def display_invalid_action(self, action):
        """ Display the information that an invalid action has been tried """
        pass

    @abstractmethod
    def end_of_match(self, wins, best_of):
        """ Display information at the end of the match """
        pass

    @abstractmethod
    def end_of_game(self, wins, best_of):
        """ 
        Display information at the end of a game
        @param wins: win dicionary
        @param best_of total number of games to play
        """
        pass

    @abstractmethod
    def new_game(self, dwarf_player, troll_player, game_length, game_number, wins):
        """ Display information at the begining of a new game """
        pass

    @abstractmethod
    def begin_turn(self, state, turn_number, game_length, game_number,
                   best_of, wins, dwarf_player, troll_player, prev_action):
        """ 
        Display information at the begining of each turn such as an illustration of the current state

        @param state: current game state  
        @param turn_number: this turn number
        @param game_length:  total number of turns in game
        @param game_number: which game number this is
        @param best_of: how many total games to play
        @param wins: win dictionary until this point
        @param dwarf_player: the dwarf player agent
        @param troll_player: troll player agent
        @param prev_action: previous action taken
        """
        pass

    @abstractmethod
    def end_game(self, wins, winner):
        """ 
        Display information at the end of a game
        
        @param wins: the current win dictionary
        @param winner: the winning piece of the game
        """
        pass


class TerminalUI(UserInterfaceTemplate):
    """
    Terminal UI for thud"""

    def start_message(self, welcome_message):
        print(welcome_message)

    def end_game(self, wins, winner):
        pass

    def start_message(self):
        print("""hello""")

    def end_of_match(self, wins, best_of):
        print(f"""
match over: {wins}
best of: {best_of}""")

    def new_game(self, dwarf_player, troll_player, game_length, game_number, wins):
        print(f"""
start game
dwarf: {dwarf_player}
trolls: {troll_player}""")

    def begin_turn(self, state: GameStateTemplate, turn_number, game_length, game_number, 
                   best_of, wins, dwarf_player, troll_player, prev_action):
        d = {Piece.DWARF: ' d ',
             Piece.TROLL: ' t ',
             Piece.EMPTY: ' - ',
             Piece.NON_PLAYABLE: '###'}

        print('')
        print(
            f'game number {game_number}: turn {turn_number}/{game_length}, {state.turn} turn')
        dwarves = state.get_locations(Piece.DWARF)
        trolls = state.get_locations(Piece.TROLL)
        print(prev_action)
        print(
            f'dwarf score = {state.score(Piece.DWARF)}, troll score = {state.score(Piece.TROLL)}')
        print('\n'.join(' '.join(d[x] for x in y) for y in state.grid.board))

    def end_game(self, wins, winner):
        print(f'winner is {winner}')
        print('end of game')
        pass

    def display_invalid_action(self, action):
        print(f'Invalid action {action}. chose a new action')


class QuietUI(UserInterfaceTemplate):

    def start_message(self, welcome_message):
        print(welcome_message)

    def end_game(self, wins, winner):
        print('game over')
        print(f'winner = {winner}')

    def end_of_match(self, wins, best_of):
        print('end of matches')
        print(f'best of {best_of}')
        print(wins)

    def new_game(self, dwarf_player, troll_player, game_length, game_number, wins):
        print('\n================\n')
        print(f'game number {game_number}')

    def display_invalid_action(self, action):
        print(f'invalid action {action} chosen, new action will be taken')

    def begin_turn(self, state, turn_number, game_length, game_number, 
                   best_of, wins, dwarf_player, troll_player, prev_action):
        pass
