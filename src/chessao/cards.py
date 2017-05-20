####### CARDS #######
import random
from chessao import CARDS_COLORS


class Card:

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

    def __init__(self, lista_kart=None):
        """
        >>> print(Deck(lista_kart=[Card(1,'5')]))
        [5♤]
        """
        if lista_kart is None:
            a = ['A', '2', '3', '4', '5', '6',
                 '7', '8', '9', '10', 'J', 'Q', 'K']
            k = [1, 2, 3, 4]
            self.cards = [Card(b, c) for b in k for c in a]
        else:
            self.cards = lista_kart

    def deal(self, n=1):
        return [self.cards.pop() for _ in range(n)]

    def combine(self, karty):
        self.cards.extend(karty)

    def get_card_index(self, rank='5', suit=1):
        return self.cards.index(Card(suit, rank))

    def tasuj(self, until=None):
        random.shuffle(self.cards)

    def __str__(self):
        return str(self.cards)
