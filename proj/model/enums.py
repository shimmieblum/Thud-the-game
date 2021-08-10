from enum import Enum


class Piece(Enum):
    DWARF = 1
    TROLL = 2
    EMPTY = 0
    NON_PLAYABLE = -1
