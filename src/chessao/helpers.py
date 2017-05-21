import json
import random
from chessao import CARDS_COLORS
from chessao.cards import Card, Deck
from chessao.chess import Board
from chessao.pieces import Pawn


class ChessaoGameplayError(Exception):
    '''Custom gameplay error'''

    def __init__(self, message, gameplay, errors=None):

        # Call the base class constructor with the parameters it needs
        super(ChessaoGameplayError, self).__init__(message)
        self.gameplay = gameplay
        print(self.gameplay.snapshot())
        # Now for your custom code...
        self.errors = errors


def invert_color(color):
    '''
    Return the other color.

    >>> invert_color('c')
    'b'
    >>> invert_color('b')
    'c'
    >>> invert_color('sth')
    'b'
    '''
    return 'c' if color == 'b' else 'b'


def deal(deck, override=None, number=5):
    '''
    Deal for #number cads to each player. 

    Returns a tuple with two lists and Deck object.
    Override parameter specifies the hands for players.
    '''
    player_a = []
    player_b = []

    if not override:
        for _ in range(number):
            player_a.append(deck.cards.pop())
            player_b.append(deck.cards.pop())
    else:
        player_a = override[0]
        player_b = override[1]
        for hand in override:
            for card in hand:
                deck.cards.remove(card)

    return (player_a, player_b, deck)


def str_to_card(str_card):
    '''
    Return a Card obj from a string representation.

    >>> str_to_card('102')
    10♡
    >>> str_to_card('!102')
    10♡
    '''
    if str_card.startswith('!'):
        str_card = str_card[1:]
    return Card(int(str_card[-1]), str_card[:-1])


def decode_card_color(card_str):
    """
    return integer repr of a color

    >>> decode_card_color('♡')
    2
    >>> decode_card_color('sth')
    Traceback (most recent call last):
    ...
    ValueError: incorrect card sring: sth
    """
    try:
        return [key for key, item in CARDS_COLORS.items() if item ==
                card_str][0]
    except IndexError:
        raise ValueError('incorrect card sring: {}'.format(card_str))


def decode_card(card_str):
    """
    Parse card for gameflow

    >>> decode_card('!10♡')
    (1, [10♡])
    >>> decode_card('J♡;R')
    (0, [J♡], 'Rook')
    """

    burned = 1 if card_str[0] == '!' else 0

    if ';' in card_str:
        assert not burned
        col = decode_card_color(card_str[-3])
        rank = card_str[:-3] if not burned else card_str[1:-3]
        jack_choice = card_str[-1]
        return (burned, [Card(col, rank)], nawaleta(jack_choice))

    col = decode_card_color(card_str[-1])
    rank = card_str[:-1] if not burned else card_str[1:-1]
    return (burned, [Card(col, rank)])


def nawaleta(jack_str):
    '''
    # this should be depracated
    Map the jack choice to a Piece Class.

    >>> nawaleta('p')
    'Pawn'
    '''
    choice = jack_str.lower()
    if choice == 'p':
        return 'Pawn'
    elif choice == 'r':
        return 'Rook'
    elif choice == 'k':
        return 'Knight'
    elif choice == 'b':
        return 'Bishop'
    elif choice == 'q':
        return 'Queen'
    return jack_str


def schodki_check(card_list):
    """
    Check if "card stairs" are build correctly.

    >>> c = Card
    >>> schodki_check([c(1,'6'),c(1,'7'),c(2,'7')])
    True
    >>> schodki_check([c(1,'2'),c(2,'3')])
    False
    >>> schodki_check([c(1,'7'),c(1,'6'),c(1,'5')])
    True
    >>> schodki_check([c(3,'6'),c(1,'6'),c(2,'6'),c(2,'6'),c(4,'6')])
    True
    >>> schodki_check([c(2,'2'),c(1,'2'),c(1,'3')])
    False
    >>> schodki_check([c(2,'3'),c(1,'3'),c(4,'3')])
    True
    >>> schodki_check([c(2,'6'),c(2,'7'),c(3,'7'),c(3,'6')])
    True
    """

    for i in range(len(card_list) - 1):

        color_check = card_list[i].kol == card_list[i + 1].kol
        current_rank = int(card_list[i].ran)
        next_rank = int(card_list[i + 1].ran)
        big_stair_check = current_rank + 1 == next_rank
        low_stair_check = current_rank - 1 == next_rank

        if current_rank == next_rank:
            continue
        if color_check:
            if big_stair_check or low_stair_check:
                continue
        return False
    return True


def ok_karta(card, decks):
    """
    Returns True if a card is can be put on one of a decks

    >>> ok_karta([Card(1,'5')], ([Card(1,'9')],[Card(3, 'K')]))
    True
    >>> ok_karta([Card(1,'5'), Card(2,'7')], ([Card(1,'9')],[Card(3, 'K')]))
    False
    """
    if len(card) > 1:
        if not schodki_check(card):
            return False

    card_color = card[0].kol
    card_rank = card[0].ran

    for deck in decks:
        last_card_color = deck[-1].kol
        last_card_rank = deck[-1].ran
        if card_color == last_card_color \
                or card_rank == last_card_rank \
                or 'Q' in (last_card_rank, card_rank):
            return True
    return False


def odejmij(hand, cards):
    '''
    Return hand after removing the specified cards from it.

    >>> odejmij([Card(1,'7'), Card(4,'5')], [Card(1,'7')])
    [5♧]
    >>> odejmij([Card(1,'7'), Card(4,'5')], [Card(2,'7')])
    Traceback (most recent call last):
    ...
    ValueError: The card(s) is(are) not in the hand.
    '''
    for card in cards:
        try:
            hand.remove(card)
        except ValueError:
            raise ValueError('The card(s) is(are) not in the hand.')
    return hand


def ktora_kupka(karta, kupki, rnd=False):
    '''
    Return the index of a pile wherein the card goes.
    Expects a list with a card, and a list of two Deck objects.

    >>> ktora_kupka([Card(1,'5')], ([Card(1,'9')],[Card(3, 'K')]))
    0
    >>> ktora_kupka([Card(1,'5')], ([Card(1,'9')],[Card(2, 'K')]))
    0
    >>> ktora_kupka([Card(4,'2')], ([Card(1,'9')],[Card(2, 'K')]))
    Traceback (most recent call last):
    ...
    ValueError: card: [2♧] kupki ([9♤], [K♡])

    '''
    res = []
    card_rank = karta[0].ran
    card_color = karta[0].kol
    for i, pile in enumerate(kupki):
        pile_rank = pile[-1].ran

        color_check = card_color == pile[-1].kol
        rank_check = card_rank == pile_rank
        queen_check = pile_rank == 'Q'or card_rank == 'Q'

        if color_check or rank_check or queen_check:
            res.append(i)
    if len(res) == 1:
        return res[0]
    elif len(res) == 2:
        if rnd:
            return random.randint(0, 1)
        usr_input = input(
            'Na którą kupkę dołożyć kartę? (0 - lewa / 1 - prawa) ')
        assert a in ('1', '0')
        return int(usr_input)
    raise ValueError('card: {} kupki {}'.format(karta, kupki))


def rozpakuj_input(inp):
    """
    >>> rozpakuj_input('24')
    [2♧]
    >>> rozpakuj_input('104')
    [10♧]
    >>> rozpakuj_input('!A4')
    [A♧]
    >>> rozpakuj_input('54,64,74')
    [5♧, 6♧, 7♧]
    rozpakuj_input('54,64')
    [5♧]
    """
    a = inp.split()

    if len(a) == 3:
        a[0] = [str_to_card(s) for s in a[0].split(',')]
    elif len(a) == 1:
        return [str_to_card(s) for s in inp.split(',')]
    return a


def last_line_check(color, first_sq, last_sq, board):
    '''Return the position of the Piece in the last row, if none return 0.'''
    for i in range(first_sq, last_sq):
        try:
            if type(board.brd[i]) == Pawn and board.brd[i].color == color:
                return i
        except AttributeError:
            # print(board)
            print(board.brd[i])
            raise AttributeError
    return 0


def czy_pion_na_koncu(brd, k):
    """
    Returns True if a Pawn reached the end of Board.

    >>> czy_pion_na_koncu(Board(), 'b')
    0
    >>> czy_pion_na_koncu(Board(), 'c')
    0
    >>> czy_pion_na_koncu(Board(), 'f')
    Traceback (most recent call last):
    ...
    AssertionError
    """
    assert k in ('b', 'c')
    return last_line_check('b', 91, 99, brd) if k == 'b' else last_line_check('c', 21, 29, brd)
