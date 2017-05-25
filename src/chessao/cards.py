####### CARDS #######
import random
from chessao import CARDS_COLORS


class Card:
    """
    Card class.

    The CARDS_COLORS variable is a dictionary::

        CARDS_COLORS = {1: '♤', 2: '♡', 3: '♢', 4: '♧'}

    Each card has two attributes: color and rank.

    You would construct a two of spades with ``Card(1, '2')``
    """

    def __init__(self, color, ranga):
        self.kol = color
        self.ran = ranga

    def __eq__(self, o):
        assert Card == type(o)
        return self.kol == o.kol and self.ran == o.ran

    def __str__(self):
        return self.ran + CARDS_COLORS[self.kol]

    def __repr__(self):
        return str(self)


class Deck:
    """
    A Deck of cards class.

    Holds one attribute ('cards') with a list of cards in order.
    """

    def __init__(self, card_list=None):
        """
        >>> print(Deck(card_list=[Card(1,'5')]))
        [5♤]
        """
        if card_list is None:
            ranks = ['A', '2', '3', '4', '5', '6',
                     '7', '8', '9', '10', 'J', 'Q', 'K']
            colors = [1, 2, 3, 4]
            self.cards = [Card(col, rank) for col in colors for rank in ranks]
        else:
            self.cards = card_list

    def deal(self, repeat=1):
        """
        Return a list of top *repeat* cards.

        >>> Deck(lista_kart=[Card(1,'5')]).deal()
        [5♤]
        """
        return [self.cards.pop() for _ in range(repeat)]

    def combine(self, karty):
        self.cards.extend(karty)

    def get_card_index(self, rank='5', suit=1):
        """Return the index of a specified card."""
        return self.cards.index(Card(suit, rank))

    def tasuj(self):
        """Shuffle the deck."""
        random.shuffle(self.cards)

    def __str__(self):
        return str(self.cards)
