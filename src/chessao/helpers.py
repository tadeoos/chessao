import random
from chessao.szachao import Card


def invert_color(color):
    '''Return the other color.'''
    return 'c' if color == 'b' else 'b'


def deal(deck, override=None):
    '''
    Deal for five cads to each player. 

    Returns a tuple with two lists and Talia object.
    Override parameter specifies the hands for players.
    '''
    player_a = []
    player_b = []

    if not override:
        for _ in range(5):
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
    '''Return a Card obj from a string representation.'''
    return Card(int(str_card[-1]), str_card[:-1])


def decode_card_color(card_str):

    if card_str == '♤':
        return 1
    elif card_str == '♡':
        return 2
    elif card_str == '♢':
        return 3
    elif card_str == '♧':
        return 4
    else:
        raise ValueError


def decode_card(card_str):

    burned = 1 if card_str[0] == '!' else 0

    if ';' in card_str:
        assert not burned
        col = decode_card_color(card_str[-3])
        rank = card_str[:-3] if burned == 0 else card_str[1:-3]
        jack_choice = card_str[-1]
        return (burned, [Card(col, rank)], nawaleta(jack_choice))

    col = decode_card_color(card_str[-1])
    rank = card_str[:-1] if burned == 0 else card_str[1:-1]
    return (burned, [Card(col, rank)])


# this should be depracated
def nawaleta(jack_str):
    '''Map the jack choice to a Piece Class.'''
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

    >>> k=Card
    >>> schodki_check([k(1,'6'),k(1,'7'),k(2,'7')])
    True
    >>> schodki_check([k(1,'2'),k(2,'3')])
    False
    >>> schodki_check([k(1,'7'),k(1,'6'),k(1,'5')])
    True
    >>> schodki_check([k(3,'6'),k(1,'6'),k(2,'6'),k(2,'6'),k(4,'6')])
    True
    >>> schodki_check([k(2,'2'),k(1,'2'),k(1,'3')])
    False
    >>> schodki_check([k(2,'3'),k(1,'3'),k(4,'3')])
    True
    >>> schodki_check([k(2,'6'),k(2,'7'),k(3,'7'),k(3,'6')])
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
    '''Return hand after removing the specified cards from it.'''
    for card in cards:
        hand.remove(card)
    return hand


def ktora_kupka(karta, kupki, rnd=False):
    res = []
    for i in range(2):
        if karta[0].kol == kupki[i][-1].kol or karta[0].ran == kupki[i][-1].ran or kupki[i][-1].ran == 'Q'or karta[0].ran == 'Q':
            res.append(i)
    if len(res) == 1:
        return res[0]
    elif len(res) == 2:
        if rnd:
            return random.randint(0, 1)
        a = input('Na którą kupkę dołożyć kartę? (0 - lewa / 1 - prawa) ')
        assert a in ('1', '0')
        return int(a)
    raise ValueError('card: {} kupki {}'.format(karta, kupki))


def rozpakuj_input(inp):
    a = inp.split()
    if len(a) == 3:
        a[0] = [str_to_card(s) for s in a[0].split(',')]
    elif len(a) == 1:
        return [str_to_card(s) for s in inp.split(',')]
    elif len(a) == 2:
        return a
    return a


def last_line_check(color, first_sq, last_sq, board):
    '''Return the position of the Piece in the last row, if none return 0.'''
    for i in range(first_sq, last_sq):
        if board.brd[i].name == Pawn and board.brd[i].color == color:
            return i
    return 0


def czy_pion_na_koncu(brd, k):
    assert k in ('b', 'c')
    return last_line_check('b', 91, 99, brd) if k == 'b' else last_line_check('c', 21, 29, brd)