import pytest

from chessao import BLACK_COLOR, WHITE_COLOR
from chessao.chess import EMPTY
from chessao.cards import Card
from chessao.gameplay import ChessaoGame, CardValidationError
import chessao.helpers as helpers

from .utils import card_list


def test_sth():
    piles = (card_list(['Q1']), card_list(['Q3']))
    hands = (
        card_list(['Q1', '41', 'J1', 'K1', '73']),
        card_list(['Q3', '42', 'J2', 'K2', '73'])
    )
    chessao = ChessaoGame.for_tests(hands, piles)
    assert not chessao.mate


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

    def test_should_lose_turn_when_four(self, chessao_four_played):
        chessao_four_played.play_cards([Card(1, '5')])
        assert chessao_four_played.player_should_lose_turn


class TestCheck:

    def test_scholars_mate(self, chessao_default):
        chessao_default.full_move(cards=None, move=['E2', 'E4'], burn=True)
        chessao_default.full_move(cards=None, move=['E7', 'E5'], burn=True)
        chessao_default.full_move(cards=None, move=['D1', 'H5'], burn=True)
        chessao_default.full_move(cards=None, move=['B8', 'C6'], burn=True)
        chessao_default.full_move(cards=None, move=['F1', 'C4'], burn=True)
        chessao_default.full_move(cards=None, move=['G8', 'F6'], burn=True)
        chessao_default.full_move(cards=None, move=['H5', 'F7'], burn=True)

        assert chessao_default.check
        assert chessao_default.finished

    def test_checking_piece_can_be_captured(self, chessao_default):
        chessao_default.full_move(cards=None, move=['E2', 'E4'])
        chessao_default.full_move(cards=None, move=['F7', 'F5'])
        chessao_default.full_move(cards=None, move=['E4', 'E5'])
        chessao_default.full_move(cards=None, move=['G8', 'F6'])
        chessao_default.full_move(cards=None, move=['D1', 'H5'])
        assert chessao_default.check, str(chessao_default)
        chessao_default.full_move(cards=None, move=['F6', 'H5'])
        assert not chessao_default.check

    def test_card_cannot_mate(self, fen_setup):
        g = fen_setup('7K/8/Q7/4B2R/8/8/8/1k6', ["K1"], [])
        g.full_move([Card(1, '7')], ["H4", "H8"])
        assert g.check
        g.full_move([Card(1, '7')], ["B8", "C7"])
        assert not g.check
        g.full_move([Card(1, 'K')], [])
        assert g.check
        assert not g.mate
        assert not g.player_should_lose_turn

class TestStalemate:

    def test_after_simulate(self, stalemate_setup):
        g = stalemate_setup
        g.full_move(cards=[Card(3, 'Q')], move=['F2', 'F3'], burn=1)
        g.full_move(cards=[Card(2, '4')], move=['F7', 'F6'], burn=1)
        g.full_move(cards=[Card(1, '8')], move=['E1', 'F2'], burn=1)
        g.full_move(cards=[Card(1, 'J')], move=['A7', 'A6'], jack='q')
        g.full_move(cards=[Card(4, 'K')], move=['D1', 'E1'])
        assert not g.stalemate
        assert not g.mate
        assert not g.finished


class TestKingOfSpades:

    def test_simple(self, kos_setup):
        game = kos_setup
        assert game.to_move == WHITE_COLOR
        game.full_move(cards=None, move=['E2', 'E4'])
        assert game.to_move == BLACK_COLOR
        assert game.moves == 1
        game.full_move(cards=[Card(1, 'K')], move=[])
        assert game.to_move == WHITE_COLOR
        print(game.history.get_move_from_turn(-1))
        assert game.king_of_spades_active()
        assert game.current_card == Card(1, 'K')
        assert game.possible_moves() == {'E2': ['E3']}

    # @pytest.mark.xfail(raises=AssertionError, reason="Not handled yet")
    def test_king_after_four(self, hand_setup):
        """If you play KOS after lost move, KOS has no power."""

        g = hand_setup(['84', 'K1', '41'], ['93', 'Q3'])
        assert g.to_move == WHITE_COLOR
        g.full_move(cards=[Card(1, '4')], move=['B1', 'C3'])
        assert g.to_move == BLACK_COLOR
        g.full_move(cards=[Card(3, '9')], move=[])
        assert g.to_move == WHITE_COLOR
        g.full_move(cards=[Card(1, 'K')], move=['E2', 'E3'])
        assert not g.king_of_spades_active()

    def test_king_at_the_begining(self, hand_setup):
        # when played at the begining, it should work as normal
        g = hand_setup(['84', 'K1'], ['93', 'Q3'])
        assert g.to_move == WHITE_COLOR
        g.full_move(cards=[Card(1, 'K')], move=['B1', 'C3'])
        assert not g.king_of_spades_active()
        assert g.board['B1'] == EMPTY

    def test_king_after_three(self, hand_setup):
        # three card should have his powers only once
        g = hand_setup(['34'], ['K1', 'Q3', '21', '52'])
        assert g.to_move == WHITE_COLOR
        g.full_move(cards=[Card(4, '3')], move=['B1', 'C3'])
        assert g.moves == 1
        g.full_move(cards=[Card(1, 'K')], move=['B1', 'C3'],  # move doesn't matter
                    cards_to_discard=card_list(['Q3', '21', '52']))
        assert g.king_of_spades_active()
        assert g.player_should_lose_turn  # current card is still KOS
        g.full_move(cards=[], move=['B1', 'A3'])
        assert g.board['A3'].name == 'Knight'
        g.full_move(cards=None, move=['E7', 'E6'])

    def test_after_enpassant(self, hand_setup):
        g = hand_setup([], ['K1', '63', '71', '52'])
        g.full_move(cards=None, move=['E2', 'E4'])
        g.full_move(cards=[Card(3, '6')], move=['F7', 'F5'])
        g.full_move(cards=None, move=['E4', 'E5'])
        g.full_move(cards=[Card(1, '7')], move=['D7', 'D5'])
        g.full_move(cards=None, move=['E5', 'D6'])
        assert g.board['D5'] == EMPTY
        g.full_move(cards=[Card(1, 'K')], move=[])
        assert g.board['D6'] == EMPTY
        assert g.board['E5'].name == 'Pawn'
        assert g.board['D5'].name == 'Pawn'
        assert g.player_should_lose_turn  # current card is still KOS


class TestKingOfHearts:

    def test_simple(self, koh_setup):
        game = koh_setup
        game.full_move(cards=[Card(1, '6')], move=['E2', 'E4'], burn=1)
        game.full_move(cards=None, move=['E7', 'E5'])
        game.full_move(cards=[Card(2, 'K')], move=['F2', 'F3'])
        assert game.to_move == BLACK_COLOR
        assert game.possible_moves() == {}
        assert game.player_should_lose_turn

    def test_turn_losing_after_capture(self, koh_setup):
        g = koh_setup
        g.full_move(cards=[Card(1, '6')], move=['E2', 'E4'], burn=1)
        g.full_move(cards=None, move=['D7', 'D5'])
        g.full_move(cards=[Card(2, 'K')], move=['E4', 'D5'])
        assert g.board['D5'].color == WHITE_COLOR
        assert g.possible_moves() == {}
        assert g.player_should_lose_turn


class TestQueen:

    def test_simple(self, q_setup):
        game = q_setup
        game.play_cards([Card(3, 'Q')])
        expected = {'A1', 'B1', 'C1', 'F1', 'G1', 'H1',
                    'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2'}
        pos_moves = game.possible_moves()
        assert set(pos_moves.keys()) == {'D1'}
        assert set(pos_moves['D1']) == expected

    @pytest.mark.xfail(reason="Queen after jack raises error in current implementation")
    def test_queen_after_jack(self, hand_setup):
        # test that Queen cards doesn't trumps active jack
        g = hand_setup(['J1', 'K2'], ['93', 'Q3'])
        g.full_move(cards=[Card(1, 'J')], move=['E2', 'E4'], pile=1, jack='n')
        assert g.jack == 'n'
        g.play_cards([Card(3, 'Q')])
        pos_starts = set(g.possible_moves().keys())
        assert pos_starts != {'D8'}
        assert pos_starts == {'B8', 'G8'}

    def test_queen_after_jack_errors(self, hand_setup):
        g = hand_setup(['84', 'J3'], ['93', 'Q3'])
        assert g.to_move == WHITE_COLOR
        g.full_move(cards=[Card(4, '8')], move=['B1', 'C3'])
        g.full_move(cards=[Card(3, '9')], move=['G7', 'G5'])
        g.full_move(cards=[Card(3, 'J')], move=['F2', 'F4'], jack='b')
        assert not g.stalemate
        assert g.jack == 'b'
        with pytest.raises(CardValidationError):
            g.full_move(cards=[Card(3, 'Q')], move=['D8', 'A7'])


class TestAce:

    def test_ace_default(self):
        fh = card_list(['31', 'A1', '61', '81', '53'])
        sh = card_list(['41', 'A2', '51', '101', 'J1'])
        hands = (fh, sh)
        chessao = ChessaoGame.for_tests(hands=hands)
        assert chessao.to_move == WHITE_COLOR
        assert Card(1, "A") in chessao.current_player.hand
        chessao.full_move(cards=[fh[0]], move=['E2', 'E4'], burn=True)
        assert chessao.to_move == BLACK_COLOR
        chessao.full_move(cards=[sh[1]], move=['E2', 'E4'], pile=1)  # move doesn't matter
        assert chessao.to_move == BLACK_COLOR
        assert Card(1, "A") in chessao.current_player.hand

    def test_ace_under_check(self):
        fh = card_list(['31', 'A1', '61', '81', '53'])
        sh = card_list(['41', 'A2', '51', '101', 'J1'])

        hands = (fh, sh)
        chessao = ChessaoGame.for_tests(hands=hands)
        chessao.full_move(
            cards=[chessao.current_player.hand[-1]], move=['E2', 'E4'], burn=True)
        chessao.full_move(
            cards=[chessao.current_player.hand[-1]], move=['F7', 'F5'], burn=True)
        chessao.full_move(
            cards=[chessao.current_player.hand[-1]], move=['E4', 'E5'], burn=True)
        chessao.full_move(
            cards=[chessao.current_player.hand[-1]], move=['G8', 'F6'], burn=True)
        chessao.full_move(
            cards=[chessao.current_player.hand[-1]], move=['D1', 'H5'], burn=True)

        assert chessao.to_move == BLACK_COLOR
        assert chessao.check

        chessao.full_move(
            cards=[chessao.current_player.hand[1]], move=['F6', 'H5'], pile=1)  # ace didn't took effect

        assert not chessao.check
        assert chessao.to_move == WHITE_COLOR


class TestJack:

    def test_jack_default(self):
        fh = card_list(['31', 'A1', '61', '81', '53'])
        sh = card_list(['41', 'A2', '51', '101', 'J1'])
        hands = (fh, sh)
        chessao = ChessaoGame.for_tests(hands=hands)
        assert chessao.to_move == WHITE_COLOR
        chessao.full_move(cards=[fh[0]], move=['E2', 'E4'], burn=True)
        assert chessao.to_move == BLACK_COLOR
        chessao.full_move(cards=[sh[-1]], move=['E7', 'E5'], pile=1, jack='r')
        assert chessao.jack == 'r'
        assert chessao.to_move == WHITE_COLOR
        chessao.play_cards(cards=[fh[2]], burn=True)
        assert chessao.jack is None
        assert chessao.possible_moves() == {}

    def test_jack_on_jack(self):
        fh = card_list(['31', 'A1', '61', '81', 'J2'])
        sh = card_list(['41', 'A2', '51', '101', 'J1'])
        hands = (fh, sh)
        chessao = ChessaoGame.for_tests(hands=hands)
        assert chessao.to_move == WHITE_COLOR
        chessao.full_move(cards=[fh[0]], move=['E2', 'E4'], burn=True)
        assert chessao.to_move == BLACK_COLOR
        chessao.full_move(cards=[sh[-1]], move=['E7', 'E5'], pile=1, jack='r')
        assert chessao.jack == 'r'
        assert chessao.to_move == WHITE_COLOR
        chessao.play_cards(cards=[fh[-2]], pile=1, jack='n')
        assert chessao.jack == 'n'
        assert chessao.possible_moves() != {}

    def test_four_on_jack(self, hand_setup):
        # when 4 is played after Jack, turn is lost
        g = hand_setup(['J1'], ['41'])
        g.full_move(cards=[Card(1, 'J')], move=['E2', 'E4'], jack='r')
        g.full_move(cards=[Card(1, '4')], move=[])
        g.play_cards(cards=[Card(1, '7')])
        assert g.player_should_lose_turn


class TestThree:

    def test_single_discard(self, three_setup):
        chessao = three_setup
        discarded = [Card(1, '10'), Card(1, 'J'), Card(2, 'A')]

        chessao.full_move(cards=[chessao.current_player.hand[0]], move=['E2', 'E4'])
        assert chessao.three == 0
        assert chessao.cards.burned == []

        chessao.full_move(
            cards=[chessao.current_player.hand[2]],
            move=['E7', 'E5'],
            pile=1,
            cards_to_discard=discarded)
        assert chessao.three == 3
        assert chessao.cards.burned == discarded
        assert chessao.history.get_move_from_turn(-1, 'discarded') == discarded

    def test_three_with_defence(self, three_setup):
        chessao = three_setup
        chessao.full_move(cards=[chessao.current_player.hand[0]], move=['E2', 'E4'])
        assert chessao.three == 0
        assert chessao.cards.burned == []
        chessao.full_move(
            cards=[chessao.current_player.hand[0]],
            move=['E7', 'E5'],
            pile=1)
        assert chessao.three == 0
        assert chessao.cards.burned == []

    def test_three_with_double_defence(self, three_setup):
        chessao = three_setup
        chessao.full_move(cards=[Card(1, '3')], move=['E2', 'E4'])
        assert chessao.three == 0
        assert chessao.cards.burned == []
        chessao.full_move(
            cards=[Card(2, '3')],
            move=['E7', 'E5'],
            pile=1)
        assert chessao.three == 0
        assert chessao.cards.burned == []
        chessao.full_move(
            cards=[Card(1, '3')],
            move=['D2', 'D3'])
        assert chessao.three == 0
        assert chessao.cards.burned == []
        chessao.full_move(
            cards=[Card(2, '5')],
            move=['F7', 'F5'],
            pile=1)  # there is no need to pass additional arg, when whole hand is discarded
        assert chessao.three == 5
        assert len(chessao.cards.burned) == 5


class TestFourCardBehavior:

    @classmethod
    def setup_method(self, test_method):
        """Setup test with a 4 of spades played at the begining of a game."""

        self.first_hand = [
            *map(helpers.str_to_card, ['41', '42', '51', '101', 'J1'])]
        self.second_hand = [
            *map(helpers.str_to_card, ['41', '42', '51', '101', 'J1'])]
        self.gameplay = ChessaoGame.for_tests(
            [self.first_hand, self.second_hand])
        self.gameplay.full_move(
            cards=[self.first_hand[0]],
            move=['A2', 'A4']
        )

    def teardown_method(self, test_method):
        self.gameplay = None
        self.first_hand = None
        self.second_hand = None

    def test_four(self):
        assert not self.gameplay.can_capture
        self.gameplay.full_move(
            cards=[self.second_hand[3]],
            move=[],
            burn=True
        )
        assert self.gameplay.to_move == WHITE_COLOR
        self.gameplay.play_cards([self.first_hand[3]], burn=True)
        assert not self.gameplay.can_capture

    def test_four_on_four(self):
        self.gameplay.full_move(
            cards=[self.second_hand[1]],
            move=['A7', 'A6']
        )
        assert self.gameplay.to_move == WHITE_COLOR
        assert not self.gameplay.can_capture

    @pytest.mark.xfail(reason="Wrong card erroring not implemented")
    def test_wrong_card(self):
        assert not self.gameplay.can_capture
        assert self.gameplay.to_move == BLACK_COLOR
        with pytest.raises(helpers.ChessaoGameplayError):
            self.gameplay.full_move(
                cards=[Card(1, '5')],
                move=['A7', 'A6']
            )


class TestPromotion:

    def test_simple(self, fen_setup):
        g = fen_setup('K7/8/8/8/8/8/4P3/k7')
        g.full_move(None, ['E7', 'E8'], promotion='q')
        assert g.board.promotion_took_place
        assert g.board['E8'].name == 'Queen'
        assert g.check

    def test_king_of_spades_after(self, fen_setup):
        g = fen_setup('K7/8/8/8/8/8/4P3/k7', None, ['K1'])
        g.board['E7'].mvs_number = 6
        g.full_move(None, ['E7', 'E8'], promotion='q')
        g.full_move([Card(1, 'K')], [])
        assert g.board['E8'] == EMPTY
        assert g.board['E7'].name == 'Pawn'
        assert g.board['E7'].mvs_number == 6
        assert g.player_should_lose_turn


class TestMoves:

    def test_enpassant(self, chessao_default):
        chessao_default.full_move(cards=None, move=['E2', 'E4'])
        chessao_default.full_move(cards=None, move=['F7', 'F5'])
        chessao_default.full_move(cards=None, move=['E4', 'E5'])
        chessao_default.full_move(cards=None, move=['D7', 'D5'])
        chessao_default.full_move(cards=None, move=['E5', 'D6'])
        assert chessao_default.board['D5'] == EMPTY


# bugi
# ♡

# co kiedy król zagrywa specjalnego króla i ma w zasięgu króla przeciwnego?
# - dokleiłem jeszcze w movesm damki warunek na typ ktory zostal

# co kiedy zagrywam waleta, żądam ruchu damą, którą następnie zbijam?
# robię tak, że tracisz kolejkę.
# czy mogę dać czwórkę na waleta?
# TAk

# może się wydarzyć taka sytuacja: czarne szachują białe. biały król
# ucieka. czarne zagrywają króla pik. (co w efekcie połowicznie realizuje
# króla pik - cofa rozgrywkę, ale zaraz karta już przestaje działać bo
# jest szach ) biały król zagrywa króla pik. -> system się jebie


# może być też tak, że król się gracz się sam wpierdoli w pata.
# Białe zagrywają 4, więc nie mogą zbijać, ale został im już tylko król,
# który ma jeden ruch -- zbić coś. Czy dopuszczamy taką opcję?
# Samopodpierdolenie na remis?
# roboczo - tak

# co jesli chce zagrać roszadę na królu trefl?
# wprowadzam rozwiazanie ze roszady nie można zrobić na królu..

# trzeba napisać test czy rozwiązanie z usuwaniem ruchów w Piece.moves() nie
# zabiera szansy na to, żeby zbić tego co szachuje
