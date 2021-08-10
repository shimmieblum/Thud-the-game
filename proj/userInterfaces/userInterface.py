from abc import ABCMeta, abstractmethod
from pygame import color, mouse

from pygame.constants import KEYDOWN, MOUSEBUTTONDOWN, QUIT
from pygame.draw import line
from ..model.enums import Piece
from ..model.state import Action, GameState
from pprint import pprint


class UserInterfaceTemplate:

    def __init__(self) -> None:
        self.quit = False

    @abstractmethod
    def start_message(self):
        pass

    @abstractmethod
    def end_of_match(self, wins, best_of):
        pass

    @abstractmethod
    def end_of_game(self, wins, best_of):
        pass

    @abstractmethod
    def new_game(self, dwarf_player, troll_player, game_length, game_number, wins):
        pass

    @abstractmethod
    def begin_turn(self, state, turn_number, game_length, game_number, best_of, wins, dwarf_player, troll_player, prev_action):
        pass

    @abstractmethod
    def end_game(self, wins, winner):
        pass


class TerminalUI(UserInterfaceTemplate):
    '''
    Terminal UI for thud'''

    def end_game(self, wins, winner):
        pass

    def start_message(self):
        print('''hello''')

    def end_of_match(self, wins, best_of):
        print(f'''
match over: {wins}
best of: {best_of}''')

    def new_game(self, dwarf_player, troll_player, game_length, game_number, wins):
        print(f'''
start game
dwarf: {dwarf_player}
trolls: {troll_player}''')

    def begin_turn(self, state: GameState, turn_number, game_length, game_number, best_of, wins, dwarf_player, troll_player, prev_action):
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
        print(f'dwarves = {len(dwarves)}, trolls = {len(trolls)}')
        print(f'captured = {state.captured}')
        print('\n'.join(' '.join(d[x] for x in y) for y in state.grid.board))

    def end_game(self, wins, winner):
        print(f'winner is {winner}')
        print('end of game')
        pass


class QuietUI(UserInterfaceTemplate):

    def start_message(self):
        pass

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

    def begin_turn(self, state, turn_number, game_length, game_number, best_of, wins, dwarf_player, troll_player, prev_action):
        pass
