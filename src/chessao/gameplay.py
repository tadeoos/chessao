from copy import deepcopy
import json
import os
import re
import sys
import time
from typing import List

from chessao import WHITE_COLOR, BLACK_COLOR
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

    def __init__(self, players, board=None, cards=None, **kwargs):

        self.board = board or Board()
        self.cards = cards or ChessaoCards()
        self.history = kwargs.get('history', [self.board.fen()])
        self.current_move = kwargs.get('current_move', None)
        self.last_move = kwargs.get('last_move', None)
        self.to_move = kwargs.get('to_move', WHITE_COLOR)
        self.check = kwargs.get('check', False)
        self.mate = kwargs.get('mate', False)
        self.stalemate = kwargs.get('stalemate', False)
        self.promotion = kwargs.get('promotion', False)
        self.can_capture = kwargs.get('can_capture', True)
        self.jack = kwargs.get('jack', None)
        self.three = kwargs.get('three', 0)

        # deal cards
        if kwargs.get('deal', True):
            players[0].hand = self.cards.deal(5)
            players[1].hand = self.cards.deal(5)
        self.players = players

    @classmethod
    def for_tests(cls, hands, piles=None, board=None, **kwargs):
        """Method for test purposes."""
        players = (
            Player(1, WHITE_COLOR, name='white', hand=hands[0]),
            Player(2, BLACK_COLOR, name='black', hand=hands[1])
        )
        piles = piles or ([Card(2,'Q')], [Card(4,'Q')])
        cards = ChessaoCards.for_tests(piles, hands=hands)
        chessao = cls(players, board, cards, deal=False, **kwargs)
        assert len(hands[0]) + len(hands[1]) + len(cards.all_cards) == 104
        return chessao

    def __str__(self):
        blacks = self._get_player_by_color(WHITE_COLOR)
        whites = self._get_player_by_color(BLACK_COLOR)

        return f"""
PILES: |{str(self.piles[0][-1]):>3} |  |{str(self.piles[1][-1]):>3} |
CURRENT_CARD:  {'!' if self.burned else ''}{self.current_card}
{blacks.name} {blacks.id} (white): {blacks.hand}
{self.board}
{whites.name} {whites.id} (black): {whites.hand}
History:
{self.history}
"""

    @property
    def burned(self):
        return self.cards.current_card is None

    @property
    def piles(self):
        return self.cards.piles

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
        return self._get_player_by_color(self.to_move)

    def _get_player_by_color(self, color: str):
        if self.players[0].color == color:
            return self.players[0]
        return self.players[1]

    def full_move(self,
                  cards: List[Card],
                  move: List[str],
                  pile: int = 0,
                  burn: bool = False):

        self.play_cards(cards, pile, burn)
        if move:
            assert move[1] in self.possible_moves()[move[0]]
            self.chess_move(move[0], move[1])
        else:
            self.current_move = []
        self.end_move()

    def play_cards(self, cards: List[Card], pile: int = 0, burn: bool = False):
        self.current_player.remove_cards(cards)
        if burn:
            self.cards.burn_card(cards)
        else:
            self.cards.play_cards(cards, pile)
        self.current_player.update_cards(self.cards.deal(len(cards)))
        self.set_capture()

    def chess_move(self, start: str, end: str):
        self.current_move = [start, end]
        self.board.move(start, end, self.current_card)

    def end_move(self):
        self.set_check()
        self.set_mate()
        self.add_to_history()
        self.change_color()

    def set_check(self):
        color = self.invert_color(self.current_player.color)
        if self.board.color_is_checked(color) == (True, color):
            self.check = True
        else:
            self.check = False

    def set_mate(self):
        pass

    def set_capture(self):
        try:
            second_move_of_four = self.penultimate_card.is_('4') and not self.last_card.is_('4')
        except AttributeError:
            second_move_of_four = False
        if any([
            self.current_card is not None and self.current_card.is_('4'),
            second_move_of_four
            ]):
            self.can_capture = False
        else:
            self.can_capture = True

    @property
    def player_should_lose_turn(self):
        if len(self.history) < 2:
            return False
        four_condition = self.last_card.is_('4') and not self.current_card.is_('4')
        # king_of_hearts_condition = self.last_card.is_('K', 2)
        return any([
            four_condition
        ])

    @property
    def should_change_last_move(self):  # king of spades
        return self.current_card.is_('K', 1)

    def positions_taken_by_color(self, color):
        return [pos for pos in self.board.all_taken()
                if self.board[pos].color == color]

    def possible_moves(self, card=None):
        """Return a dict of possible moves.

            meant to be invoked after card was played and before move was made.
        """

        def convert_to_strings(dictionary):
            inverted_mapdict = {v: k for (k, v) in self.board.mapdict.items()}
            new = []
            for key, list_of_positions in dictionary.items():
                new.append((
                    inverted_mapdict[key],
                    [inverted_mapdict[i] for i in list_of_positions]))
            return dict(new)

        if self.player_should_lose_turn:
            return {}

        possible_moves = {}
        inverted_mapdict = {v: k for (k, v) in self.board.mapdict.items()}
        card = card or self.current_card
        possible_start = self.positions_taken_by_color(self.to_move)
        for start in possible_start:
            piece_card = card or Card(1, '5')  # mock card for moves checking
            end = [pos
                   for pos in self.board[start].moves(piece_card, self.board)
                   if not isinstance(self.board[pos], King)
                   ]
            if end:
                possible_moves[start] = end
        return convert_to_strings(possible_moves)

    def change_color(self):
        if self.to_move == WHITE_COLOR:
            self.to_move = BLACK_COLOR
        else:
            self.to_move = WHITE_COLOR

    def add_to_history(self):
        if not self.current_move:
            record = f'{self.to_move} {self.current_card} '
        else:
            record = '{color} {burn}{car}{jack} {piece}{fro}:{to}{prom}{check}{mate} {fenrep}'.format(
                color=self.to_move,
                burn='!' if self.burned else '',
                car=self.current_card,
                jack=';' + self.jack[0] if self.jack is not None else '',
                piece=self.board.get_fen_rep(self.board.get_piece(self.current_move[1])),
                fro=self.current_move[0],
                to=self.current_move[1],
                prom='=' + self.promotion if self.promotion else '',
                check='+' if self.check else '',
                mate='#' if self.mate else '',
                fenrep=self.board.fen()
            )
        self.history.append(record)

    @staticmethod
    def invert_color(color):
        if color == WHITE_COLOR:
            return BLACK_COLOR
        return WHITE_COLOR
