from pytest import fixture

from chessao import BLACK_COLOR, WHITE_COLOR
from chessao.cards import Card
from chessao.gameplay import ChessaoGame
from chessao.players import Player

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
    chessao.full_move(cards=None, move=['E2','E4'])
    chessao.full_move(cards=None, move=['F7','F5'])
    chessao.full_move(cards=None, move=['E4','E5'])
    chessao.full_move(cards=None, move=['G8','F6'])
    chessao.full_move(cards=None, move=['D1','H5'])
    return chessao

@fixture
def chessao_four_played():
    first_hand = [*map(Card.from_string, ['41', '42', '51', '101', 'J1'])]
    second_hand = [*map(Card.from_string, ['41', '42', '51', '101', 'J1'])]
    game = ChessaoGame.for_tests([first_hand, second_hand])
    game.full_move(
        cards=[first_hand[0]],
        move=['A2','A4']
    )
    return game
