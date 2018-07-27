import imp

from chessao import WHITE_COLOR, BLACK_COLOR, MAPDICT
from chessao.cards import Card, ChessaoCards, Deck
from chessao.chess import Board
from chessao.pieces import Rook, Bishop, King, Knight, Queen
from chessao.players import Player
from chessao.gameplay import ChessaoGame
from chessao.history import ChessaoHistory
from tests.utils import load_game_pkl_from, load_simulation_bugs

DEFAULT_PLAYERS = (
    Player(1, WHITE_COLOR, name='white'),
    Player(2, BLACK_COLOR, name='black')
)

cards = ChessaoCards()
chessao = ChessaoGame(DEFAULT_PLAYERS)
