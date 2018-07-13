import pytest

from chessao import BLACK_COLOR, WHITE_COLOR
from chessao.cards import Card
from chessao.players import Player
from chessao.gameplay import ChessaoGame
import chessao.helpers as helpers

from .utils import assert_lists_equal, card_list


def test_sth():
    piles = (card_list(['Q1']), card_list(['Q3']))
    hands = (
        card_list(['Q1', '41', 'J1', 'K1', '73']),
        card_list(['Q3', '42', 'J2', 'K2', '73'])
    )
    chessao = ChessaoGame.for_tests(hands, piles)
    assert chessao.mate == False

class TestPossibleMoves:

    def test_positions_at_start(self, chessao_default):
        assert chessao_default.possible_moves() == {
            'A2': ['A3', 'A4'],
            'B1': ['A3', 'C3'],
            'B2': ['B3', 'B4'],
            'C2': ['C3', 'C4'],
            'D2': ['D3', 'D4'],
            'E2': ['E3', 'E4'],
            'F2': ['F3', 'F4'],
            'G1': ['F3', 'H3'],
            'G2': ['G3', 'G4'],
            'H2': ['H3', 'H4']
        }

    def test_positions_when_four(self, chessao_four_played):
        chessao_four_played.play_cards([Card(1, '5')])
        assert chessao_four_played.possible_moves() == {}

class TestCheck:

    def test_scholars_mate(self, chessao_default):
        chessao_default.full_move(cards=None, move=['E2','E4'], burn=True)
        chessao_default.full_move(cards=None, move=['E7','E5'], burn=True)
        chessao_default.full_move(cards=None, move=['D1','H5'], burn=True)
        chessao_default.full_move(cards=None, move=['B8','C6'], burn=True)
        chessao_default.full_move(cards=None, move=['F1','C4'], burn=True)
        chessao_default.full_move(cards=None, move=['G8','F6'], burn=True)
        chessao_default.full_move(cards=None, move=['H5','F7'], burn=True)

        assert chessao_default.check
        assert chessao_default.finished

    def test_checking_piece_can_be_captured(self):
        pass

class TestFourCardBehavior:

    @classmethod
    def setup_method(self, test_method):
        """Setup test with a 4 of spades played at the begining of a game."""

        self.first_hand = [*map(helpers.str_to_card, ['41', '42', '51', '101', 'J1'])]
        self.second_hand = [*map(helpers.str_to_card, ['41', '42', '51', '101', 'J1'])]
        self.gameplay = ChessaoGame.for_tests([self.first_hand, self.second_hand])
        self.gameplay.full_move(
            cards=[self.first_hand[0]],
            move=['A2','A4']
        )

    def teardown_method(self, test_method):
        self.gameplay = None
        self.first_hand = None
        self.second_hand = None

    # @pytest.mark.xfail(reason="capture parameter gets cleared too early")
    def test_four(self):
        self.gameplay.full_move(
            cards=[self.second_hand[3]],
            move=[],
            burn=True
        )
        assert self.gameplay.to_move == WHITE_COLOR
        # assert not self.gameplay.can_capture

    def test_four_on_four(self):
        self.gameplay.full_move(
            cards=[self.second_hand[1]],
            move=['A7','A6']
        )
        assert self.gameplay.to_move == WHITE_COLOR
        assert not self.gameplay.can_capture

    @pytest.mark.xfail(reason="Wrong card erroring not implemented")
    def test_wrong_card(self):
        assert not self.gameplay.can_capture
        assert self.gameplay.to_move == BLACK_COLOR
        with pytest.raises(helpers.ChessaoGameplayError):
            self.gameplay.full_move(
                cards=card[Card(1, '5')],
                move=['A7', 'A6']
            )

# bugi
# ♡

# co kiedy król zagrywa specjalnego króla i ma w zasięgu króla przeciwnego?
# - dokleiłem jeszcze w movesm damki warunek na typ ktory zostal
# król się zbija w pewnym momencie (jakim?)
# - dokleilem w self.possible_moves pozycje kinga
# kkier unhashable type karta
#  problem w tempie, zmienilem troche na glupa, zeby bral dobre miejsce jak widzie ze cos zle ale olewam to dla k pika.
# co kiedy zagrywam waleta, żądam ruchu damą, którą następnie zbijam?
# robię tak, że tracisz kolejkę.
# czy mogę dać czwórkę na waleta?
# robię, że nie
# może się wydarzyć taka sytuacja: czarne szachują białe. biały król
# ucieka. czarne zagrywają króla pik. (co w efekcie połowicznie realizuje
# króla pik - cofa rozgrywkę, ale zaraz karta już przestaje działać bo
# jest szach ) biały król zagrywa króla pik. -> system się jebie


# może być też tak, że król się gracz się sam wpierdoli w pata. Białe zagrywają 4, więc nie mogą zbijać, ale został im już tylko król, który ma jeden ruch -- zbić coś. Czy dopuszczamy taką opcję? Samopodpierdolenie na remis?
# roboczo - tak

# co jesli chce zagrać roszadę na królu trefl?
# wprowadzam rozwiazanie ze roszady nie można zrobić na królu..

# trzeba napisać test czy rozwiązanie z usuwaniem ruchów w Piece.moves() nie
# zabiera szansy na to, żeby zbić tego co szachuje
