from pytest import fixture

from chessao import BLACK_COLOR, WHITE_COLOR
from chessao.chess import Board
from chessao.cards import Card
from chessao.gameplay import ChessaoGame
from chessao.players import Player
from .utils import card_list

collect_ignore = ["chessao/dev.py:"]

DEFAULT_PLAYERS = (
    Player(1, WHITE_COLOR, name='white'),
    Player(2, BLACK_COLOR, name='black')
)


@fixture
def chessao_default():
    return ChessaoGame(DEFAULT_PLAYERS)


@fixture
def chessao_check():
    chessao = ChessaoGame(DEFAULT_PLAYERS)
    chessao.full_move(cards=None, move=['E2', 'E4'])
    chessao.full_move(cards=None, move=['F7', 'F5'])
    chessao.full_move(cards=None, move=['E4', 'E5'])
    chessao.full_move(cards=None, move=['G8', 'F6'])
    chessao.full_move(cards=None, move=['D1', 'H5'])
    return chessao


@fixture()
def hand_setup():

    def _hand_setup(x, y, **kwargs):
        neutral_cards = card_list(['51', '61', '71', '81', '91'])
        hands = []
        for hand in (x, y):
            cards = card_list(hand) + neutral_cards
            hands.append(cards[:5])
        return ChessaoGame.for_tests(hands=hands, **kwargs)

    return _hand_setup


@fixture()
def fen_setup():

    def _fen_setup(fen, x=None, y=None, **kwargs):
        neutral_cards = card_list(['51', '61', '71', '81', '91'])
        hands = []
        for hand in (x, y):
            if hand is None:
                hands.append(neutral_cards[:])
            else:
                cards = card_list(hand) + neutral_cards
                hands.append(cards[:5])
        board = Board(fenrep=fen)
        return ChessaoGame.for_tests(hands=hands, board=board, **kwargs)

    return _fen_setup


@fixture
def three_setup():
    fh = card_list(['31', '31', '61', '81', '53'])
    sh = card_list(['32', 'A2', '52', '101', 'J1'])
    hands = (fh, sh)
    return ChessaoGame.for_tests(hands=hands)


@fixture(scope='function')
def kos_setup():
    fh = card_list(['71', '31', '61', '81', '53'])
    sh = card_list(['K1', 'A2', '42', '101', 'J1'])
    hands = (fh, sh)
    return ChessaoGame.for_tests(hands=hands)


@fixture
def koh_setup():
    fh = card_list(['K2', '31', '61', '81', '53'])
    sh = card_list(['K2', 'A2', '42', '101', 'J1'])
    hands = (fh, sh)
    return ChessaoGame.for_tests(hands=hands)


@fixture
def q_setup():
    fh = card_list(['K2', 'Q3', '61', '81', '53'])
    sh = card_list(['K2', 'Q4', '42', '101', 'J1'])
    hands = (fh, sh)
    return ChessaoGame.for_tests(hands=hands)


@fixture
def stalemate_setup():
    fh = card_list(['K2', 'Q3', 'K4', '81', '53'])
    sh = card_list(['K2', 'Q4', '42', '101', 'J1'])
    hands = (fh, sh)
    return ChessaoGame.for_tests(hands=hands)


@fixture
def chessao_four_played():
    first_hand = [*map(Card.from_string, ['41', '42', '51', '101', 'J1'])]
    second_hand = [*map(Card.from_string, ['41', '42', '51', '101', 'J1'])]
    game = ChessaoGame.for_tests([first_hand, second_hand])
    game.full_move(
        cards=[first_hand[0]],
        move=['A2', 'A4']
    )
    return game
