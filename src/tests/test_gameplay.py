import pytest
from chessao import BLACK_COLOR, WHITE_COLOR
from chessao.cards import Card
from chessao.gameplay import ChessaoGame, resurect
import chessao.helpers as helpers
from chessao.utils import (
    get_default_board,
    get_default_cards,
    get_default_players,
    get_gameplay_defaults
)


def simple_gameplay():
    gameplay = ChessaoGame(default_setup=True)

    white_player_cards = gameplay.get_user_cards(WHITE_COLOR, first=False)
    black_player_cards = gameplay.get_user_cards(BLACK_COLOR, first=False)

    cards_queue = [
        white_player_cards[0],
        black_player_cards[0],
        white_player_cards[1]
    ]

    # first move from white
    gameplay.make_an_overriden_move_in_one_func(
        card=(1, [cards_queue[0]]),
        move=['A2', 'A4']
    )
    # first move from blacks
    gameplay.make_an_overriden_move_in_one_func(
        card=(1, [cards_queue[1]]),
        move=['A7', 'A6']
    )
    # second move from white
    gameplay.make_an_overriden_move_in_one_func(
        card=(1, [cards_queue[2]]),
        move=['A4', 'A5']
    )
    return gameplay, cards_queue


def test_bad_constructor():
    with pytest.raises(AssertionError):
        ChessaoGame()


def test_obvious():
    test_gameplay, used_cards = simple_gameplay()
    print(test_gameplay.snapshot())
    assert test_gameplay.to_move == BLACK_COLOR
    assert not test_gameplay.mat
    assert test_gameplay.historia == [
        "RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr KQkq - 0 0",
        "b !{} PA2:A4 RNBQKBNR/1PPPPPPP/8/P7/8/8/pppppppp/rnbqkbnr KQkq A3 0 0".format(used_cards[0]),
        "c !{} pA7:A6 RNBQKBNR/1PPPPPPP/8/P7/8/p7/1ppppppp/rnbqkbnr KQkq - 0 1".format(used_cards[1]),
        "b !{} PA4:A5 RNBQKBNR/1PPPPPPP/8/8/P7/p7/1ppppppp/rnbqkbnr KQkq - 0 1".format(used_cards[2])
    ]
    assert test_gameplay.get_cards_quantity() == 104


class TestFourCardBehavior:

    @classmethod
    def setup_method(self, test_method):
        self.first_hand = [*map(helpers.str_to_card, ['41', '42', '51', '101', 'J1'])]
        self.second_hand = [*map(helpers.str_to_card, ['41', '42', '51', '101', 'J1'])]
        cards = get_default_cards(select_hands=(self.first_hand, self.second_hand))
        gameplay_args = get_gameplay_defaults(cards=cards)
        self.gameplay = ChessaoGame(**gameplay_args)
        self.gameplay.make_an_overriden_move_in_one_func(
            card=(0, [self.first_hand[0]]),
            move=['A2', 'A4']
        )
        assert not self.gameplay.capture

    def teardown_method(self, test_method):
        self.gameplay = None
        self.first_hand = None
        self.second_hand = None

    @pytest.mark.xfail(reason="capture parameter gets cleared too early")
    def test_four(self):
        assert not self.gameplay.capture
        self.gameplay.make_an_overriden_move_in_one_func(
            card=(1, [self.second_hand[3]]),
            move=[]
        )
        assert self.gameplay.to_move == WHITE_COLOR
        assert not self.gameplay.capture

    def test_four_on_four(self):
        assert not self.gameplay.capture
        self.gameplay.make_an_overriden_move_in_one_func(
            card=(0, [self.second_hand[1]]),
            move=['A7', 'A6']
        )
        assert not self.gameplay.capture
        assert self.gameplay.to_move == WHITE_COLOR

    @pytest.mark.xfail(reason="Wrong card erroring not implemented")
    def test_wrong_card(self):
        assert not self.gameplay.capture
        assert self.gameplay.to_move == BLACK_COLOR
        with pytest.raises(helpers.ChessaoGameplayError):
            self.gameplay.make_an_overriden_move_in_one_func(
                card=(0, [Card(1, '5')]),
                move=['A7', 'A6'])
