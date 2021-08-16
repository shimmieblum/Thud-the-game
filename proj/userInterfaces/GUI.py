import enum
import sys
from proj.agents.gameTree import Tree

import pygame as pg
from pygame.constants import KEYDOWN, K_KP_ENTER, K_RETURN, QUIT

from proj.gameEngine.enums import Piece
from proj.gameEngine.state import GameStateTemplate
from .userInterface import UserInterfaceTemplate


class Alignment(enum.Enum):
    TOP = 1
    MIDDLE = 2
    BOTTOM = 3

    CENTRE = 1
    LEFT = 2
    RIGHT = 3


class GUI(UserInterfaceTemplate):
    """ 
    Pygame UI for thud
    """

    DWARF_COLOUR = BLUE = (0, 0, 255)
    TROLL_COLOUR = RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BROWN = (139, 69, 19)
    YELLOW = (255, 255, 0)
    GREY = (140, 140, 140)

    def __init__(self) -> None:
        super().__init__()
        pg.init()
        self.surface = pg.display.set_mode((750, 750))
        pg.display.flip()
        self.game_num = 0
        self.highlights = []
        self.info_text = ''

    def start_message(self, message):
        width, height = pg.display.get_window_size()
        img = pg.image.load(r'proj\userInterfaces\THUD logo.png')
        self.surface.blit(pg.transform.smoothscale(
            img, (width-40, 300)), dest=(20, 20))
        text = ('By Trevor Truran\nInspired by Terry Prachett\nPress Enter to Continue')
        self.add_text_box(
            text=text,
            top_left=(20, 320),
            width=width-40,
            height=100,
            box_fill=GUI.WHITE,
            text_colour=GUI.RED,
            text_size=40
        )
        pg.display.flip()
        carry_on = False
        while not carry_on:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit()
                elif event.type == pg.KEYDOWN and event.key == K_RETURN:
                    carry_on = True

    def end_of_match(self, wins, best_of):
        self.surface.fill((0, 0, 0))
        winstr = '\n'.join((str(x) for x in wins.items()))
        winner = max(wins.keys(), key=lambda x: wins[x])
        text = f"\nEnd of Match!!\n{winstr}\nMATCH OUT OF: {best_of}\nwinner is: {winner}\nPress enter to continue"
        w, h = pg.display.get_window_size()
        self.render_text(text, (255, 255, 255), (20, h // 2 - 50), 50, 50)
        pg.display.flip()
        wait = True
        while wait:
            for event in pg.event.get():
                if event.type == QUIT:
                    pg.quit()
                if event.type == KEYDOWN and event.key == K_RETURN:
                    wait = False

    def end_game(self, wins, winner):
        self.surface.fill((0, 0, 0))
        winstr = '\n'.join((str(x) for x in wins.items()))
        text = f"\nGAME OVER!!\nwinner was {winner}\n{winstr}\nPress enter to continue"
        w, h = pg.display.get_window_size()
        self.render_text(text, (255, 255, 255), (20, h // 2 - 50), 50, 50)
        pg.display.flip()
        wait = True
        while wait:
            for event in pg.event.get():
                if event.type == QUIT:
                    pg.quit()
                if event.type == KEYDOWN and event.key == pg.K_RETURN:
                    wait = False

    def new_game(self, dwarf_player, troll_player, game_length, game_number, wins):
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                input(' asdff ')

        self.game_num += 1
        self.surface.fill((0, 0, 0))
        font = pg.font.SysFont(None, 24)
        img = font.render(f'new game {self.game_num}', True, (0, 0, 255))
        self.surface.blit(img, (20, 20))
        pg.display.flip()

    def update_info(self, game_number, best_of, wins, dwarf_player, troll_player, 
                    turn_number, game_length, prev_action):
        self.dwarf_name = dwarf_player.name
        self.dwarf_agent_type = dwarf_player.agentClassName
        self.dwarf_wins = wins[dwarf_player]

        self.troll_name = troll_player.name
        self.troll_agent_type = troll_player.agentClassName
        self.troll_wins = wins[troll_player]

        self.prev_action = prev_action

        self.game_number = game_number
        self.game_length = game_length
        self.best_of = best_of
        self.turn_number = turn_number

    def display_details_panel(self, state: GameStateTemplate):

        w, h = pg.display.get_window_size()
        dwarf_text = f'DWARVES\n{self.dwarf_name}\n{self.dwarf_agent_type}\n wins: {self.dwarf_wins}'

        self.add_text_box(dwarf_text, (20, 20), 250, 100, box_fill=GUI.DWARF_COLOUR, text_colour=GUI.WHITE,
                          autosize_text=True)

        troll_text = f'TROLLS\n{self.troll_name}\n{self.troll_agent_type}\n wins: {self.troll_wins}'

        self.add_text_box(troll_text, (w - 250 - 20, 20), 250, 100, box_fill=GUI.TROLL_COLOUR, text_colour=GUI.WHITE,
                          autosize_text=True)

        action_text = ' '
        if self.prev_action != None:
            from_loc = self.prev_action.from_loc
            to_loc = self.prev_action.to_loc
            movetype = self.prev_action.movetype
            capture_list_string = ', '.join(
                (str(x) for x in self.prev_action.capture))

            action_text = '\n'.join(['move details',
                                     f'{movetype}',
                                     f'{from_loc} -> {to_loc}',
                                     f'capture {capture_list_string}'])
        self.add_text_box(action_text, (20, 160), 250, 100, box_fill=GUI.GREY, text_colour=GUI.WHITE,
                          autosize_text=True)

        info_text = '\n'.join(['INFO',
                               f'game {self.game_number}/{self.best_of}',
                               f'turn {self.turn_number}/{self.game_length}',
                               f'DWARVES: {state.score(Piece.DWARF)}',
                               f'TROLLS: {state.score(Piece.TROLL)}'])

        self.add_text_box(info_text, (w - 250 - 20, 160), 250, 100, box_fill=GUI.GREY, text_colour=GUI.WHITE,
                          autosize_text=True)

        self.details_panel_height = 250

    def display_grid(self, state):

        self.create_grid(state, self.details_panel_height)
        pg.display.flip()
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()

    def begin_turn(self, state: GameStateTemplate, turn_number, game_length, game_number, best_of, wins, dwarf_player,
                   troll_player, prev_action):
        self.update_info(game_number, best_of, wins, dwarf_player,
                         troll_player, turn_number, game_length, prev_action)
        self.display_details_panel(state)
        self.display_grid(state)
        if prev_action == None:
            return
        self.highlight_squares(
            [prev_action.to_loc, prev_action.from_loc], (17, 189, 77))
        self.highlight_squares((x for x in prev_action.capture), (42, 74, 53))

    def render_text(self, text, colour, top_left, line_height, text_size=24) -> int:
        tx, ty = top_left
        line_height
        for line in text.splitlines():
            img = pg.font.SysFont(None, text_size).render(line, True, colour)
            self.surface.blit(img, (tx, ty))
            ty += line_height
        return ty

    def create_grid(self, state: GameStateTemplate, display_panel_height):
        width, height = pg.display.get_window_size()
        self.surface.fill(GUI.BLACK, (0, display_panel_height,
                          width, height - display_panel_height))
        square_colours = {1: GUI.GREY, -1: GUI.WHITE}

        self.LEFT_MARGIN = width // 60
        self.RIGHT_MARGIN = width // 60
        self.TOP_MARGIN = height // 60 + display_panel_height + 10
        self.BOTTOM_MARGIN = height // 60
        self.square_height = (
            height - (self.TOP_MARGIN + self.BOTTOM_MARGIN)) // 17
        self.square_width = (
            width - (self.LEFT_MARGIN + self.RIGHT_MARGIN)) // 17

        colour = 1
        for x in range(17):
            for y in range(17):
                colour = -colour
                t = state.grid.get_piece(x, y)
                if t == Piece.EMPTY:
                    c = square_colours[colour]
                elif t == Piece.DWARF:
                    c = (0, 0, 255)
                elif t == Piece.TROLL:
                    c = (255, 0, 0)
                else:
                    c = (0, 0, 0)
                left = self.LEFT_MARGIN + x * self.square_width
                top = self.TOP_MARGIN + (16 - y) * self.square_height
                pg.draw.rect(self.surface, c, pg.Rect(
                    left, top, self.square_width, self.square_height))
                if x == 0 and y > 0:
                    self.render_text(f'   {y} ', GUI.WHITE, top_left=(left, top),
                                     line_height=self.square_height)
                if y == 0 and x > 0:
                    self.render_text(f'   {x} ', GUI.WHITE, top_left=(left, top + 15),
                                     line_height=self.square_height)

    def display_invalid_action(self, action):
        w, h = pg.display.get_window_size()

        self.add_text_box(
            text=f'invalid action\n{action}.\nChoose another\nPress enter to continue',
            top_left=(w//2-100, h//2-100),
            width=200, height=200,
            box_fill=GUI.WHITE,
            text_colour=GUI.RED,
        )

    def get_coordinates(self, mouse_position):
        x_pos, y_pos = mouse_position
        x_pos -= self.LEFT_MARGIN
        y_pos -= self.TOP_MARGIN
        x = x_pos // self.square_width
        y = (16 - y_pos // self.square_height)
        if x < 0 or x > 16 or y < 0 or y > 16:
            return -1, -1
        else:
            return x, y

    def highlight_squares(self, locations, colour):
        """
        highlight squares of locations in the list of locations
        @param locations: the list of locations to highlight
        @param colour: the colour to highlight the squares 
        """
        for x, y in locations:
            tlx = self.LEFT_MARGIN + (x) * self.square_width
            tly = self.TOP_MARGIN + (16 - y) * self.square_height
            b_width = self.square_width // 10
            border_colour = colour
            pg.draw.rect(self.surface, border_colour, pg.Rect(
                tlx, tly, self.square_width, b_width))
            pg.draw.rect(self.surface, border_colour,
                         pg.Rect(tlx, tly + self.square_height - b_width, self.square_width, b_width))
            pg.draw.rect(self.surface, border_colour, pg.Rect(
                tlx, tly, b_width, self.square_height))
            pg.draw.rect(self.surface, border_colour,
                         pg.Rect(tlx + self.square_width - b_width, tly, b_width, self.square_height))

        pg.display.flip()

    def add_ok_button(self):
        screen_width, screen_height = pg.display.get_window_size()
        x = screen_width * 10 // 13
        width = screen_width // 13
        y = screen_height * 11 // 13
        height = screen_height // 13
        colour = (100, 100, 100)
        self.ok_rect = self.add_text_box("OK", (x, y), width, height, colour, (255, 255, 255),
                                         verticle_alignment=Alignment.TOP,
                                         horizontal_alignment=Alignment.CENTRE,
                                         autosize_text=True)

    def ok_button_click(self, mouse_position) -> bool:
        return self.ok_rect.collidepoint(mouse_position)

    def add_text_box(self, text, top_left, width, height, box_fill, text_colour, font=pg.font.SysFont,
                     horizontal_alignment=Alignment.CENTRE, verticle_alignment=Alignment.MIDDLE, text_size=24,
                     autosize_text=False):
        margin = 0
        tlx, tly = top_left
        lines = text.splitlines()
        if autosize_text:
            text_block_height = height - margin
        else:
            text_block_height = min(text_size * len(lines), height - margin)
        text_size = text_block_height // len(lines)
        font = font(None, text_size)
        line_number = 0
        rect = pg.draw.rect(self.surface, box_fill,
                            pg.Rect(tlx, tly, width, height))
        ttlx, ttly = 0, tly + margin
        for line in lines:
            text_width, text_height = font.size(line)
            if horizontal_alignment == Alignment.LEFT:
                ttlx = tlx + margin
            elif horizontal_alignment == Alignment.CENTRE:
                ttlx = tlx + (width - text_width) // 2
            elif horizontal_alignment == Alignment.RIGHT:
                ttlx = tlx + (width - margin - text_width)
            line_number += 1
            self.render_text(line, text_colour, (ttlx, ttly),
                             line_height=text_size, text_size=text_size)
            ttly = ttly + text_height
        pg.display.flip()
        return rect
