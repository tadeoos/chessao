"""Cards module."""
import random
from collections import defaultdict, OrderedDict
from itertools import permutations
from functools import total_ordering
from typing import List, Optional

from chessao import CARDS_COLORS, CARDS_RANKS, CARDS_RANKS_MAPPING


@total_ordering
class Card:
    """
    Card class.

    The CARDS_COLORS variable is a dictionary::

        CARDS_COLORS = {1: '♤', 2: '♡', 3: '♢', 4: '♧'}

    Each card has two attributes: color and rank.

    You would construct a two of spades with ``Card(1, '2')``
    """

    def __init__(self, color: int, rank: str, burned=False):
        """
        >>> Card(1, 20)
        Traceback (most recent call last):
            ...
        TypeError: Invalid card rank. Should be one of ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
        >>> Card(10, 'K')
        Traceback (most recent call last):
            ...
        TypeError: Card color should be an integer: 1, 2, 3 or 4
        >>> c = Card(1, '5', True)
        >>> c.burned
        True
        """
        if color not in CARDS_COLORS.keys():
            raise TypeError('Card color should be an integer: 1, 2, 3 or 4')
        if rank not in CARDS_RANKS:
            raise TypeError('Invalid card rank. Should be one of {}'.format(CARDS_RANKS))

        self.color = color
        self.rank = rank
        self.burned = burned

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, o):
        """
        >>> c1 = (Card(1, '2'))
        >>> c2 = (Card(1, '2'))
        >>> c1 == c2
        True
        """
        assert Card == type(o)
        return self.color == o.color and self.rank == o.rank

    def __lt__(self, other):
        if CARDS_RANKS_MAPPING[self.rank] == CARDS_RANKS_MAPPING[other.rank]:
            return self.color < other.color
        return CARDS_RANKS_MAPPING[self.rank] < CARDS_RANKS_MAPPING[other.rank]

    def __str__(self):
        """
        >>> print(Card(1, '2'))
        2♤
        """
        return self.rank + CARDS_COLORS[self.color]

    def __repr__(self):
        """
        >>> c = Card(1, '2')
        >>> c
        2♤
        """
        return str(self)

    def is_near(self, card):
        """
        >>> Card(1, '7').is_near(Card(1, '8')
        True
        >>> Card(1, '7').is_near(Card(2, '7')
        True
        >>> Card(1, '7').is_near(Card(1, '9')
        False
        >>> Card(1, 'K').is_near(Card(1, 'A')
        True
        >>> Card(1, '2').is_near(Card(1, '3')
        True
        """
        rank_diff = CARDS_RANKS_MAPPING[self.rank] - CARDS_RANKS_MAPPING[card.rank]
        if abs(rank_diff) == 1 and self.color == card.color:
            return True
        if abs(rank_diff) == 0 and self.color != card.color:
            return True
        return False

    def is_(self, rank=None, color=None):
        if rank:
            if color:
                return rank == self.rank and color == self.color
            return rank == self.rank
        return color == self.color

    @classmethod
    def from_string(cls, str_card, burned=False):
        if str_card.startswith('!'):
            burned = True
            str_card = str_card[1:]
        return cls(int(str_card[-1]), str_card[:-1], burned)

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

    def remove(self, cards: List[Card]):
        for card in cards:
            self.cards.remove(card)

    def combine(self, cards: List[Card]):
        """
        Add a list of Cards to the Deck.

        >>> d = Deck(card_list=[Card(1,'5')])
        >>> d.combine([Card(1,'6'), Card(2, '7')])
        >>> d.cards
        [5♤, 6♤, 7♡]
        """
        self.cards.extend(cards)

    def get_card_index(self, rank='5', suit=1):
        """Return the index of a specified card.

        >>> Deck().get_card_index(rank='A')
        0
        >>> Deck().get_card_index(rank='K', suit=4)
        51
        """
        return self.cards.index(Card(suit, rank))

    def shuffle(self):
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

    def __len__(self):
        return len(self.cards)

    @classmethod
    def two_decks(cls):
        first_deck = cls()
        second_deck = cls()
        first_deck.combine(second_deck.cards)
        return first_deck

    def pop(self):
        return self.cards.pop()

class ChessaoCards:

    def __init__(self):
        self.deck = Deck.two_decks()
        self.deck.shuffle()
        self.burned = []
        self.piles = (
            [self.deck.pop()],
            [self.deck.pop()]
        )
        self.penultimate_card = None
        self.last_card = None
        self.current_card = None

    @classmethod
    def for_tests(cls, piles: List[List[Card]], **kwargs):
        """Return ChessaoCards with specific piles."""
        cards = cls()
        for pile in cards.piles:
            cards.deck.combine(pile)
        for pile in piles:
            cards.deck.remove(pile)
        cards.piles = piles
        if kwargs.get('hands'):
            for hand in kwargs.get('hands'):
                cards._remove_from_anywhere(hand)
        return cards

    def _remove_from_anywhere(self, cards: List[Card]):
        for card in cards:
            try:
                self.deck.remove([card])
            except ValueError:
                try:
                    self.burned.remove(card)
                except ValueError:
                    try:
                        self.piles[0].remove(card)
                    except ValueError:
                        self.piles[1].remove(card)


    def deal(self, repeat=1):
        return self.deck.deal(repeat)

    @property
    def count(self) -> int:
        return len(self.deck) + len(self.burned) + len(self.piles[0]) + len(self.piles[1])

    @property
    def all_cards(self) -> List[Card]:
        return self.deck.cards + self.burned + self.piles[0] + self.piles[1]

    def _put_card(self, card):
        self.penultimate_card = self.last_card
        self.last_card = self.current_card
        self.current_card = card

    def play_cards(self, cards: List[Card], pile: Optional[int]):
        if not self.validate_cards(cards):
            raise ValueError("Invalid card")
        self.piles[pile].extend(cards)
        self._put_card(cards[-1])

    def burn_card(self, cards: List[Card]):
        assert len(cards) == 1
        self.burned.append(cards[-1])
        self._put_card(None)

    def validate_cards(self, cards: List[Card]):
        """
        Returns True if a card is can be put on one of a decks

        # >>> validate_cards([Card(1,'5')], ([Card(1,'9')],[Card(3, 'K')]))
        # True
        # >>> validate_cards([Card(1,'5'), Card(2,'7')], ([Card(1,'9')],[Card(3, 'K')]))
        # False
        """
        if len(cards) > 1:
            if not self.validate_stairs(cards):
                return False

        card = cards[-1]
        return self._card_can_be_played(card)

    def _card_can_be_played(self, card: Card):
        for pile in self.piles:
            if any([card.color == pile[-1].color,
                    card.rank == pile[-1].rank,
                    'Q' in (card.rank, pile[-1].rank)]):
                return True
        return False

    def possible_cards(self, hand: List[Card]) -> List[Card]:
        single_cards = [card for card in hand
                if self._card_can_be_played(card)]
        stairs = self.generate_stairs(hand, strict=True)
        return single_cards + stairs

    @staticmethod
    def validate_stairs(cards: List[Card]):
        """
        Check if card stairs are build correctly.
        >>> validate_stairs = ChessaoCards.validate_stairs
        >>> c = Card
        >>> validate_stairs([c(1,'6'),c(1,'7'),c(2,'7')])
        True
        >>> validate_stairs([c(1,'2'),c(2,'3')])
        False
        >>> validate_stairs([c(1,'7'),c(1,'6'),c(1,'5')])
        True
        >>> validate_stairs([c(3,'6'),c(1,'6'),c(2,'6'),c(2,'6'),c(4,'6')])
        True
        >>> validate_stairs([c(2,'2'),c(1,'2'),c(1,'3')])
        False
        >>> validate_stairs([c(2,'3'),c(1,'3'),c(4,'3')])
        True
        >>> validate_stairs([c(2,'6'),c(2,'7'),c(3,'7'),c(3,'6')])
        True
        """

        for i in range(len(cards) - 1):

            if cards[i].rank in ['A', '2', '3', '4', 'J', 'Q', 'K']:
                return False

            color_check = cards[i].color == cards[i + 1].color
            current_rank = int(cards[i].rank)
            next_rank = int(cards[i + 1].rank)
            big_stair_check = current_rank + 1 == next_rank
            low_stair_check = current_rank - 1 == next_rank

            if current_rank == next_rank:
                continue
            if color_check:
                if big_stair_check or low_stair_check:
                    continue
            return False
        return True

    @staticmethod
    def generate_stairs(cards: List[Card], strict: bool = False) -> List[List[Card]]:

        def get_graph(cards):
            graph = {}
            for card in cards:
                graph[card] = [other for other in cards if card.is_near(other)]
            return graph

        def find_all_paths(graph, start, end, path=[]):
            # thanks to https://www.python.org/doc/essays/graphs
            path = path + [start]
            if start == end:
                return [path]
            if start not in graph:
                return []
            paths = []
            for node in graph[start]:
                if node not in path:
                    newpaths = find_all_paths(graph, node, end, path)
                    for newpath in newpaths:
                        paths.append(newpath)
            return paths

        cards = list(OrderedDict((x, True) for x in cards).keys())  # for ease of written tests
        result = []
        graph = get_graph(cards)
        for node, end in permutations(cards, 2):
            result.extend(find_all_paths(graph, node, end))

        if strict:
            return [stairs for stairs in result if ChessaoCards.validate_stairs(stairs)]
        return result
