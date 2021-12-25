import re

from chessao.pieces import Pawn, Rook, King
from chessao.chess import Board
from chessao.cards import Card
from chessao.history import ChessaoHistory


class TestHistory:

    def test_get_move_from_turn(self, chessao_four_played):
        assert chessao_four_played.history.get_move_from_turn(1)["card"] == Card(1, '4')
