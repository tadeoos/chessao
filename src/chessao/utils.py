from chessao.cards import Deck
from chessao.chess import Board
from chessao.helpers import deal
from chessao.players import gracz, gracz_str


def get_default_board():
    return Board()


def get_default_players():
    return (
        gracz(1, 'b', bot=True),
        gracz_str(2, 'c')
    )


def get_default_cards(select_hands=None):
    """
    Args:
        select_hands (tuple of lists, optional): Provide hands for players.

    Returns dict
    """
    cards = Deck()
    cards.combine(Deck().cards)
    cards.tasuj()
    hand_one, hand_two, deck = deal(cards, override=select_hands)

    if select_hands is not None:  # when hands are selected we assume testing context
        piles = (
            [deck.cards.pop(deck.get_card_index(rank='Q', suit=3))],
            [deck.cards.pop(deck.get_card_index(rank='Q', suit=4))]
        )
    else:
        piles = (
            [deck.cards.pop()],
            [deck.cards.pop()]
        )

    return {
        'hand_one': hand_one,
        'hand_two': hand_two,
        'deck': deck,
        'piles': piles
    }


def get_gameplay_defaults(board=None, cards=None, players=None):
    return {
        'board': board or get_default_board(),
        'cards_dict': cards or get_default_cards(),
        'players': players or get_default_players()
    }
