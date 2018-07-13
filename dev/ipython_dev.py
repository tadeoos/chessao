import imp

from chessao import WHITE_COLOR, BLACK_COLOR
from chessao.cards import Card, ChessaoCards
from chessao.chess import Board
from chessao.pieces import Rook, Bishop, King, Knight, Queen
from chessao.players import Player
from chessao.gameplay import ChessaoGame

DEFAULT_PLAYERS = (
    Player(1, WHITE_COLOR, name='white'),
    Player(2, BLACK_COLOR, name='black')
)

cards = ChessaoCards()
chessao = ChessaoGame(DEFAULT_PLAYERS)
