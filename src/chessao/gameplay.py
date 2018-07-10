from copy import deepcopy
import json
import os
import re
import sys
import time

from chessao import WHITE_COLOR
from chessao.cards import Card, ChessaoCards
from chessao.chess import Board
from chessao.helpers import (
    ChessaoGameplayError,
    # decode_card_color,
    invert_color,
    # deal,
    decode_card,
    ok_karta,
    odejmij,
    ktora_kupka,
    czy_pion_na_koncu,
)
from chessao.pieces import Rook, Bishop, King, Knight, Queen
from chessao.players import Player
from chessao.utils import get_gameplay_defaults, GameplayEncoder


class ChessaoGame:
    """A gameplay class."""

    def __init__(self, board=None, cards_dict=None,
                 players=None, default_setup=False):

        if default_setup:
            defaults = get_gameplay_defaults()
            board = defaults['board']
            players = defaults['players']
        else:
            assert all([board, players]), 'Wrong arguments'

        players[0].reka = cards_dict['hand_one']
        players[1].reka = cards_dict['hand_two']

        self.board = board or Board()
        self.players = players
        self.cards = ChessaoCards()
        self.history = [self.board.fen()]
        self.current_move = None
        self.last_move = None
        self.to_move = WHITE_COLOR
        self.check = False
        self.mate = False
        self.stalemate = False
        self.promotion = False
        self.can_capture = True
        self.jack = None
        self.three = 0

    def __str__(self):
        blacks = self.get_gracz('b')
        whites = self.get_gracz('c')

        return f"""
Kupki: |{self.piles[0][-1]:>3} |  |{self.piles[1][-1]:>3} |
KARTA:  {'!' if self.burned else ''}{self.now_card}
{blacks.name} {blacks.nr} (white): {blacks.reka}
{self.board}
{whites.name} {whites.nr} (black): {whites.reka}
History:
{self.history}
"""

    @property
    def burned(self):
        return self.cards.current_card is None

    @property
    def current_card(self):
        return self.cards.current_card

    @property
    def last_card(self):
        return self.cards.last_card

    @property
    def penultimate_card(self):
        return self.cards.penultimate_card

    @property
    def current_player(self):
        if players[0].color == self.to_move:
            return players[0]
        return players[1]

    def full_move(self):
        pass

    def play_cards(self, cards: List[Card], pile: int = 0, burn=False):
        if burn:
            self.cards.burn_card(cards)
        else:
            self.cards.play_cards(cards, pile)
        self.current_player.update_cards(self.cards.deal(len(cards)))

    def chess_move(self, start, end):
        self.board.move(self.current_card, end, card)

    @property
    def should_lose_turn(self):
        four_condition = self.last_card.is_('4') and not self.current_card.is_('4')
        king_of_hearts_condition = self.last_card.is_('K', 2)

    @property
    def should_change_last_move(self):  # king of spades
        return self.current_card.is_('K', 1)

    def possible_moves(self):
        """Return a dict of possible moves."""
