import json

from chessao import BLACK_COLOR, WHITE_COLOR
from chessao.cards import Deck
from chessao.chess import Board
from chessao.helpers import deal
from chessao.players import gracz, StrategicBot


class GameplayEncoder(json.JSONEncoder):
    """A JSON encoder class for Gameplay object."""

    def default(self, obj):
        if hasattr(obj, "to_json"):
            return obj.to_json()

        return json.JSONEncoder.default(self, obj)


def get_default_board():
    return Board()


def get_default_players():
    return (
        gracz(1, WHITE_COLOR, bot=True),
        StrategicBot(2, BLACK_COLOR)
    )


def get_default_cards(select_hands=None):
    """
    Args:
        select_hands (tuple of lists, optional): Provide hands for players.

    Returns dict
    """
    cards = Deck.two_decks()
    assert len(cards) == 104
    cards.shuffle()
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
