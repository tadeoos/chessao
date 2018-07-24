import logging

CARDS_COLORS = {1: '♤', 2: '♡', 3: '♢', 4: '♧'}
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
BLACK_COLOR = 'c'
WHITE_COLOR = 'b'

PIECES_STR = {
    WHITE_COLOR: {
        'Pawn': '♙',
        'Rook': '♖',
        'Knight': '♘',
        'Bishop': '♗',
        'Queen': '♛',
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

MAPDICT = {
    letter + str(number - 1): 10 * number + 1 + 'ABCDEFGH'.index(letter)
    for number in range(2, 10)
    for letter in 'ABCDEFGH'
}
INVERTED_MAPDICT = {val: key for key, val in MAPDICT.items()}

# from logging import NullHandler
# logging.getLogger(__name__).addHandler(NullHandler())

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s.%(lineno)s: %(message)s',
                              datefmt='%m/%d/%Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
