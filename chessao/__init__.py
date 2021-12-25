import logging
from pathlib import Path
from typing import Dict

CARDS_COLORS = {1: '♤', 2: '♡', 3: '♢', 4: '♧'}
CARDS_COLORS_NAMES = {1: 'S', 2: 'H', 3: 'D', 4: 'C'}
CARDS_COLOR_FROM_HUMAN = {"spades": 1, "hearts": 2, 'diamonds': 3, 'clubs': 4}
CARDS_RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
CARDS_RANKS_MAPPING = {
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'J': 11,
    'Q': 12,
    'K': 13,
    'A': 14
}
BLACK_COLOR = 'black'
WHITE_COLOR = 'white'

PIECES_STR = {
    WHITE_COLOR: {
        'Pawn': '♙',
        'Rook': '♖',
        'Knight': '♘',
        'Bishop': '♗',
        'Queen': '♕',
        'King': '♔'

    },
    BLACK_COLOR: {
        'Pawn': '♟',
        'Rook': '♜',
        'Knight': '♞',
        'Bishop': '♝',
        'Queen': '♛',
        'King': '♚'

    }
}

MAPDICT: Dict[str, int] = {
    letter + str(number - 1): 10 * number + 1 + 'ABCDEFGH'.index(letter)
    for number in range(2, 10)
    for letter in 'ABCDEFGH'
}
INVERTED_MAPDICT: Dict[int, str] = {val: key for key, val in MAPDICT.items()}

SIMULATION_BUGS_PATH = Path(__file__).parent.parent / 'tests' / 'simulation_bugs'

# from logging import NullHandler
# logging.getLogger(__name__).addHandler(NullHandler())

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s.%(lineno)s: %(message)s',
                              datefmt='%m/%d/%Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
