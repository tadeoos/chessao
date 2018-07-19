import re

from chessao.pieces import Pawn, Rook, King
from chessao.chess import Board
from chessao.cards import Card
from chessao.gameplay import ChessaoHistory


class TestHistory:

    def test_parsing(self):
        parsed = ChessaoHistory(Board()).parse_record(
            "b !4♤(0) PA2:A4 RNBQKBNR/1PPPPPPP/8/P7/8/8/pppppppp/rnbqkbnr KQkq A3 0 0")

        assert parsed == {
            'color': 'b',
            'burned': True,
            'card': Card(1, '4'),
            'piece': Pawn,
            'move': ['A2', 'A4'],
            'board': 'RNBQKBNR/1PPPPPPP/8/P7/8/8/pppppppp/rnbqkbnr',
            'white_castle': 'KQ',
            'black_castle': 'kq',
            'enpassant': 'A3',
            'halfmove': 0,
            'fullmove': 0,
            'pile': 0
        }

    def test_problematic_parsing(self):
        record = 'c !A♤(0) kE8:E7 RNBQKBNR/PPPP2PP/4P3/5P2/p3p3/8/1pppkppp/rnbq1bnr KQ - 1 3'
        parsed = ChessaoHistory(Board()).parse_record(record)
        assert parsed == {
            'color': 'c',
            'burned': True,
            'card': Card(1, 'A'),
            'piece': King,
            'move': ['E8', 'E7'],
            'board': 'RNBQKBNR/PPPP2PP/4P3/5P2/p3p3/8/1pppkppp/rnbq1bnr',
            'white_castle': 'KQ',
            'black_castle': '',
            'enpassant': '-',
            'halfmove': 1,
            'fullmove': 3,
            'pile': 0
        }

    def test_parsing_with_promotion(self):
        parsed = ChessaoHistory(Board()).parse_record(
            "b 6♤(0) PA7:A8=R+# RNBQKBNR/1PPPPPPP/8/P7/8/8/1ppppppp/R5k1 KQ - 0 43")

        assert parsed == {
            'color': 'b',
            'burned': False,
            'card': Card(1, '6'),
            'piece': Pawn,
            'move': ['A7', 'A8'],
            'board': 'RNBQKBNR/1PPPPPPP/8/P7/8/8/1ppppppp/R5k1',
            'promotion': Rook,
            'check': True,
            'mate': True,
            'white_castle': 'KQ',
            'black_castle': '',
            'enpassant': '-',
            'halfmove': 0,
            'fullmove': 43,
            'pile': 0
        }

    def test_parsing_with_jack(self):
        parsed = ChessaoHistory(Board()).parse_record(
            "b J♤;R(0) PA2:A3 RNBQKBNR/1PPPPPPP/8/P7/8/8/pppppppp/rnbqkbnr KQkq - 0 20")

        assert parsed == {
            'color': 'b',
            'burned': False,
            'card': Card(1, 'J'),
            'jack': Rook,
            'piece': Pawn,
            'move': ['A2', 'A3'],
            'board': 'RNBQKBNR/1PPPPPPP/8/P7/8/8/pppppppp/rnbqkbnr',
            'white_castle': 'KQ',
            'black_castle': 'kq',
            'enpassant': '-',
            'halfmove': 0,
            'fullmove': 20,
            'pile': 0
        }

    def test_parsing_short(self):
        parsed = ChessaoHistory(Board()).parse_record(
            "b !J♤(1) RNBQKBNR/1PPPPPPP/8/P7/8/8/pppppppp/rnbqkbnr KQkq - 0 20")

        assert parsed != {
            'color': 'b',
            'burned': True,
            'card': Card(1, 'J'),
            'move': [],
            'board': 'RNBQKBNR/1PPPPPPP/8/P7/8/8/pppppppp/rnbqkbnr',
            'white_castle': 'KQ',
            'black_castle': 'kq',
            'enpassant': None,
            'halfmove': 0,
            'full_move': 20,
            'pile': 1
        }

    def test_discarded_cards(self):
        parsed = ChessaoHistory(Board()).parse_record(
            "b [J♤, 2♤, 3♤] !J♤(1) RNBQKBNR/1PPPPPPP/8/P7/8/8/pppppppp/rnbqkbnr KQkq - 0 20")

        assert parsed != {
            'color': 'b',
            'burned': True,
            'discarded': [Card(1, 'J'), Card(1, '2'), Card(1, '3')],
            'card': Card(1, 'J'),
            'move': [],
            'board': 'RNBQKBNR/1PPPPPPP/8/P7/8/8/pppppppp/rnbqkbnr',
            'white_castle': 'KQ',
            'black_castle': 'kq',
            'enpassant': None,
            'halfmove': 0,
            'full_move': 20,
            'pile': 1
        }

    def test_get_move_from_turn(self, chessao_four_played):
        assert chessao_four_played.history.get_move_from_turn(1, 'card') == Card(1, '4')
