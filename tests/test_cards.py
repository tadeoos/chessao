import pytest

from chessao.cards import ChessaoCards, Card, Deck
from .utils import assert_lists_equal, card_list


class TestDeck:

    def test_two_decks(self):
        assert len(Deck.two_decks()) == 104


class TestChessaoCards:

    def test_stairs_generation(self):
        cards = [Card(1, '2'), Card(1, '3'), Card(2, '2'), Card(3, '8')]
        gs = ChessaoCards.generate_stairs

        assert gs(cards) == [
            [Card(1, '2'), Card(1, '3')],
            [Card(1, '2'), Card(2, '2')],
            [Card(1, '3'), Card(1, '2')],
            [Card(1, '3'), Card(1, '2'), Card(2, '2')],
            [Card(2, '2'), Card(1, '2')],
            [Card(2, '2'), Card(1, '2'), Card(1, '3')],
        ]

        assert gs(cards, strict=True) == []

        cards = [Card(1, '2'), Card(3, '7'), Card(
            3, '8'), Card(1, '8'), Card(1, '7')]
        stairs = ChessaoCards.generate_stairs(cards)

        assert stairs == [
            [Card(3, '7'), Card(3, '8')],
            [Card(3, '7'), Card(1, '7'), Card(1, '8'), Card(3, '8')],
            [Card(3, '7'), Card(3, '8'), Card(1, '8')],
            [Card(3, '7'), Card(1, '7'), Card(1, '8')],
            [Card(3, '7'), Card(3, '8'), Card(1, '8'), Card(1, '7')],
            [Card(3, '7'), Card(1, '7')],
            [Card(3, '8'), Card(3, '7')],
            [Card(3, '8'), Card(1, '8'), Card(1, '7'), Card(3, '7')],
            [Card(3, '8'), Card(3, '7'), Card(1, '7'), Card(1, '8')],
            [Card(3, '8'), Card(1, '8')],
            [Card(3, '8'), Card(3, '7'), Card(1, '7')],
            [Card(3, '8'), Card(1, '8'), Card(1, '7')],
            [Card(1, '8'), Card(3, '8'), Card(3, '7')],
            [Card(1, '8'), Card(1, '7'), Card(3, '7')],
            [Card(1, '8'), Card(3, '8')],
            [Card(1, '8'), Card(1, '7'), Card(3, '7'), Card(3, '8')],
            [Card(1, '8'), Card(3, '8'), Card(3, '7'), Card(1, '7')],
            [Card(1, '8'), Card(1, '7')],
            [Card(1, '7'), Card(3, '7')],
            [Card(1, '7'), Card(1, '8'), Card(3, '8'), Card(3, '7')],
            [Card(1, '7'), Card(3, '7'), Card(3, '8')],
            [Card(1, '7'), Card(1, '8'), Card(3, '8')],
            [Card(1, '7'), Card(3, '7'), Card(3, '8'), Card(1, '8')],
            [Card(1, '7'), Card(1, '8')],
        ]

    def test_stairs_generation_with_the_same_card_twice(self):
        # can't use a duplicate of card in stairs
        cards = [Card(1, '2'), Card(3, '7'), Card(
            4, '8'), Card(4, '8'), Card(1, '5')]
        stairs = ChessaoCards.generate_stairs(cards)
        assert stairs == []

    def test_for_tests(self):
        piles = [[Card.from_string('101')], [Card.from_string('Q2')]]
        cards = ChessaoCards.for_tests(piles)
        assert cards.count == 104
        assert_lists_equal(Deck.two_decks().cards, cards.all_cards)

    def test_remove_from_anywhere(self):
        cards = ChessaoCards()
        with pytest.raises(ValueError):
            cards._remove_from_anywhere(card_list(['21', '21', '21']))
        cards = ChessaoCards()
        cards._remove_from_anywhere(card_list(['21', '21']))
        assert Card(1, '2') not in cards.all_cards
