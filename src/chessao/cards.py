"""Cards module."""
import random
from chessao import CARDS_COLORS, CARDS_RANKS


class Card:
    """
    Card class.

    The CARDS_COLORS variable is a dictionary::

        CARDS_COLORS = {1: '♤', 2: '♡', 3: '♢', 4: '♧'}

    Each card has two attributes: color and rank.

    You would construct a two of spades with ``Card(1, '2')``
    """

    def __init__(self, color, ranga):
        """
        >>> Card(1, 20)
        Traceback (most recent call last):
            ...
        TypeError: Invalid card rank. Should be one of ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
        >>> Card(10, 'K')
        Traceback (most recent call last):
            ...
        TypeError: Card color should be an integer: 1, 2, 3 or 4
        """
        if color not in CARDS_COLORS.keys():
            raise TypeError('Card color should be an integer: 1, 2, 3 or 4')
        if ranga not in CARDS_RANKS:
            raise TypeError('Invalid card rank. Should be one of {}'.format(CARDS_RANKS))

        self.kol = color
        self.ran = ranga

    def __eq__(self, o):
        """
        >>> c1 = (Card(1, '2'))
        >>> c2 = (Card(1, '2'))
        >>> c1 == c2
        True
        """
        assert Card == type(o)
        return self.kol == o.kol and self.ran == o.ran

    def __str__(self):
        """
        >>> print(Card(1, '2'))
        2♤
        """
        return self.ran + CARDS_COLORS[self.kol]

    def __repr__(self):
        """
        >>> c = Card(1, '2')
        >>> c
        2♤
        """
        return str(self)


class Deck:
    """
    A Deck of cards class.

    Holds one attribute ('cards') with a list of cards in order.
    """

    def __init__(self, card_list=None):
        """
        >>> Deck().cards
        [A♤, 2♤, 3♤, 4♤, 5♤, 6♤, 7♤, 8♤, 9♤, 10♤, J♤, Q♤, K♤, A♡, 2♡, 3♡, 4♡, 5♡, 6♡, 7♡, 8♡, 9♡, 10♡, J♡, Q♡, K♡, A♢, 2♢, 3♢, 4♢, 5♢, 6♢, 7♢, 8♢, 9♢, 10♢, J♢, Q♢, K♢, A♧, 2♧, 3♧, 4♧, 5♧, 6♧, 7♧, 8♧, 9♧, 10♧, J♧, Q♧, K♧]
        >>> Deck(card_list=[Card(1,'5')]).cards
        [5♤]
        """
        if card_list is None:
            self.cards = [Card(col, rank) for col in CARDS_COLORS.keys() for rank in CARDS_RANKS]
        else:
            self.cards = card_list

    def deal(self, repeat=1):
        """
        Return a list of top *repeat* cards.

        >>> Deck(card_list=[Card(1,'5')]).deal()
        [5♤]
        """
        return [self.cards.pop() for _ in range(repeat)]

    def combine(self, karty):
        """
        Add a list of Cards to the Deck.

        >>> d = Deck(card_list=[Card(1,'5')])
        >>> d.combine([Card(1,'6'), Card(2, '7')])
        >>> d.cards
        [5♤, 6♤, 7♡]
        """
        self.cards.extend(karty)

    def get_card_index(self, rank='5', suit=1):
        """Return the index of a specified card.

        >>> Deck().get_card_index(rank='A')
        0
        >>> Deck().get_card_index(rank='K', suit=4)
        51
        """
        return self.cards.index(Card(suit, rank))

    def tasuj(self):
        """Shuffle the deck.
        >>> from copy import copy
        >>> d = Deck()
        >>> cards_before = copy(d.cards)
        >>> d.tasuj()
        >>> cards_before != d.cards
        True
        """
        random.shuffle(self.cards)

    def __str__(self):
        """
        >>> print(Deck(card_list=[Card(1,'5')]))
        [5♤]
        """
        return str(self.cards)
