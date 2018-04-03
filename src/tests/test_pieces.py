from itertools import permutations
import pytest

from chessao import BLACK_COLOR, WHITE_COLOR
from chessao.cards import Card
from chessao.chess import Board, EMPTY
from chessao.pieces import Pawn, ChessaoPieceException
from chessao.helpers import get_mapdict


DEFAULT_CARD = Card(1, '5')
DEFAULT_BOARD = Board()
MAPDICT = get_mapdict()


def test_pawns_ineqaulity():
    pieces_pairs = permutations([piece for piece in Board().pieces()], 2)
    for p1, p2 in pieces_pairs:
        assert p1 != p2


def test_pawn_moves():
    black_pawn = Pawn(color=BLACK_COLOR, position=87)
    assert black_pawn.moves(DEFAULT_CARD, DEFAULT_BOARD) == [77, 67]
    white_pawn = Pawn(color=WHITE_COLOR, position=31)
    assert white_pawn.moves(DEFAULT_CARD, DEFAULT_BOARD) == [41, 51]


def test_cant_move_on_wrong_tile():
    black_pawn = Pawn(color=BLACK_COLOR, position=MAPDICT['D5'])
    assert DEFAULT_BOARD.get_piece('D5') == EMPTY
    with pytest.raises(ChessaoPieceException):
        black_pawn.moves(DEFAULT_CARD, DEFAULT_BOARD)


def test_moves_of_all_pieces_in_starting_position():
    board = Board()
    for piece in board.pieces():
        if piece.name in ('Pawn', 'Knight'):
            direction = -1 if piece.color == BLACK_COLOR else 1
            moves = set(piece.moves(DEFAULT_CARD, board))
            assert len(moves) == 2
            if piece.name == 'Pawn':  # check beggining Pawns' moves
                assert moves == {piece.position + direction * 10,
                                 piece.position + direction * 20}
            else:  # check beggining Knights moves
                assert moves == {piece.position + direction * 19,
                                 piece.position + direction * 21}
        else:
            assert not piece.moves(DEFAULT_CARD, board)


def test_castle():
    board = Board(fenrep='R3K2R/PPPPP3/8/pP6/8/Nnr1qQbB/8/7k KQ')
    king_moves = board.get_piece(25).moves(DEFAULT_CARD, board)
    assert 23 in king_moves, king_moves
    assert 27 in king_moves, king_moves
