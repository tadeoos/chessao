import logging
from collections import defaultdict
from pprint import pformat
from typing import List, Optional, Tuple

from chessao import WHITE_COLOR, BLACK_COLOR
from chessao.cards import Card, ChessaoCards
from chessao.chess import Board, FEN_DICT, EMPTY

from chessao.pieces import King, Piece
from chessao.players import Player
from chessao.helpers import get_inverted_mapdict, ok_karta, invert_dict, get_mapdict
from chessao.history import ChessaoHistory


class ChessaoError(Exception):
    pass


class DiscardMissingError(ChessaoError):
    pass


class BadMoveError(ChessaoError):
    pass


class ChessaoGame:
    """A gameplay class."""

    def __init__(self, players, board=None, cards=None, **kwargs):

        self.board = board or Board()
        self.cards = cards or ChessaoCards()
        self.history = kwargs.get('history', ChessaoHistory(self.board))
        self.current_move = kwargs.get('current_move', None)
        self.last_move = kwargs.get('last_move', None)
        self.to_move = kwargs.get('to_move', WHITE_COLOR)
        self.check = kwargs.get('check', False)
        self.mate = kwargs.get('mate', False)
        self.stalemate = kwargs.get('stalemate', False)
        self.promotion = kwargs.get('promotion', False)
        # self.can_capture = kwargs.get('can_capture', True)
        self.jack = kwargs.get('jack', None)
        # self.three = kwargs.get('three', 0)
        self.logger = logging.getLogger(__name__)

        # deal cards
        if kwargs.get('deal', True):
            players[0].hand = self.cards.deal(5)
            players[1].hand = self.cards.deal(5)
        self.players = players

    @classmethod
    def for_tests(cls, hands, piles=None, board=None, **kwargs):
        """Method for test purposes."""
        players = (
            Player(1, WHITE_COLOR, name='Adam', hand=hands[0] if hands else None),
            Player(2, BLACK_COLOR, name='Eve', hand=hands[1] if hands else None)
        )
        piles = piles or ([Card(2, 'Q')], [Card(4, 'Q')])
        cards = ChessaoCards.for_tests(piles, hands=hands)
        chessao = cls(players, board, cards, deal=False, **kwargs)
        if hands:
            assert len(hands[0]) + len(hands[1]) + len(cards.all_cards) == 104
        else:
            assert len(cards.all_cards) == 104
        return chessao

    @classmethod
    def from_ledger(cls,
                    ledger: List[str],
                    starting_deck: Tuple[str],
                    players: Optional[Tuple[Player]] = None) -> "ChessaoGame":

        # we assume that ledger start with fenrep of starting board
        if players is None:
            players = (
                Player(1, WHITE_COLOR, name='Adam'),
                Player(2, BLACK_COLOR, name='Eve')
            )
        cards = ChessaoCards(deck=starting_deck)
        board = Board(fenrep=ledger[0])
        chessao = cls(players, board=board, cards=cards)
        for record in ledger[1:]:
            turn = ChessaoHistory.parse_record(record)
            chessao.full_move(
                cards=[turn['card']],
                move=turn['move'],
                pile=turn['pile'],
                burn=turn['burned'],
                jack=turn['jack'],
                cards_to_discard=turn['discarded'])
        return chessao

    def __str__(self):
        blacks = self._get_player_by_color(WHITE_COLOR)
        whites = self._get_player_by_color(BLACK_COLOR)

        return f"""\
PILES: |{str(self.piles[0][-1]):>3} |  |{str(self.piles[1][-1]):>3} |
CURRENT_CARD:  {'!' if self.burned else ''}{self.current_card}
{blacks.name} {blacks.id} (white): {blacks.hand}
{self.board.print_for(self.to_move)}
{whites.name} {whites.id} (black): {whites.hand}
History:
{self.cards.starting_deck}
{self.history}"""

    def __repr__(self):
        return pformat(self.__dict__)

    @property
    def discarded_cards(self):
        if self.three:
            assert self._discarded_cards is not None
            return self._discarded_cards
        return None

    @discarded_cards.setter
    def discarded_cards(self, value):
        self._discarded_cards = value

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

    @property
    def finished(self):
        return self.mate or self.stalemate

    @property
    def can_capture(self):
        second_move_after_four = all([self.card_is(self.penultimate_card, '4'),
                                      not self.card_is(self.last_card, '4')])

        if any([self.card_is(self.current_card, '4'),
                second_move_after_four]):
            return False
        return True

    @property
    def three(self):
        if all([self.card_is(self.last_card, '3'),
                not self.card_is(self.current_card, '3')]):
            three = 5 if self.card_is(self.penultimate_card, '3') else 3
        else:
            three = 0
        return three

    @staticmethod
    def invert_color(color):
        if color == WHITE_COLOR:
            return BLACK_COLOR
        return WHITE_COLOR

    def card_is(self, card, rank=None, color=None):
        if card is None:
            return False
        try:
            return card.is_(rank, color)
        except AttributeError:
            raise(f'{card} has no attribute is_')

    def piece_has(self, position, **kwargs):
        piece = self.board[position]
        if piece == EMPTY:
            return False
        return all([getattr(piece, k) == v for k, v in kwargs.items()])

    def change_color(self):
        self.to_move = self.invert_color(self.to_move)

    def swap_players_color(self):
        for player in self.players:
            player.color = self.invert_color(player.color)

    def add_to_history(self):
        self.history.add(self)

    def _get_player_by_color(self, color: str):
        if self.players[0].color == color:
            return self.players[0]
        return self.players[1]

    def full_move(self,
                  cards: List[Card],
                  move: List[str],
                  pile: int = 0,
                  burn: bool = False,
                  jack: Optional[str] = None,
                  cards_to_discard: Optional[List[Card]] = None) -> None:

        if cards is None:  # for tests purposes
            cards = self.current_player.choose_any()
            burn = True
        if self.king_of_spades_active():
            self._handle_king_of_spades()
        else:
            self.play_cards(cards, pile, burn,
                            jack=jack, cards_to_remove=cards_to_discard)

        # Handle Ace
        if self.card_is(self.current_card, 'A'):
            if not self.check:
                self.swap_players_color()
                self.add_to_history()
                return
        if self.card_is(self.current_card, 'K', 1):
            self.logger.info("King of spades played")
            move = []
        if self.player_should_lose_turn:
            self.logger.info("Player loosing turn...")
            move = []
        if move:
            possible_moves = self.possible_moves()
            assert move[0] in possible_moves, f'{self.possible_moves()}| {self.current_card}'
            move_ends = possible_moves[move[0]]
            assert move[1] in move_ends, f'{self.possible_moves()}| {self.current_card}| {self.board.fen()}'
            self.chess_move(move[0], move[1])
        else:
            self.current_move = []

        self.end_move()

    def play_cards(self,
                   cards: List[Card],
                   pile: int = 0,
                   burn: bool = False,
                   jack: Optional[str] = None,
                   cards_to_remove: Optional[List[Card]] = None):
        self.discarded_cards = cards_to_remove
        self.current_player.remove_cards(cards)
        if burn:
            self.cards.burn_card(cards)
        else:
            self.cards.play_cards(cards, pile)
        self.current_player.update_cards(self.cards.deal(len(cards)))
        self.set_jack(jack)
        if self.three:
            self._handle_three(cards_to_remove)

    def _handle_three(self, cards_to_remove):
        if self.three == 3:
            if cards_to_remove is None:
                raise DiscardMissingError("No cards to discard passed")
        else:
            assert self.three == 5
            cards_to_remove = [c for c in self.current_player.hand]
        assert len(cards_to_remove) == self.three
        self.current_player.remove_cards(cards_to_remove)
        self.cards.burned.extend(cards_to_remove)
        self.current_player.update_cards(
            self.cards.deal(len(cards_to_remove)))

    def _handle_king_of_spades(self):
        penultimate_move = self.history.get_move_from_turn(-2)
        card = penultimate_move['card']
        burn = penultimate_move['burned']
        done_move = penultimate_move['move']
        assert done_move, "Can't redo undone move"
        self.cards._put_card(card, burn)
        mapdict = get_mapdict()
        self.board.swap(mapdict[done_move[0]],
                        mapdict[done_move[1]])

    def chess_move(self, start: str, end: str):
        self.current_move = [start, end]
        self.board.move(start, end, self.current_card)

    def end_move(self):
        self.set_check()
        self.set_stalemate()
        self.set_mate()
        self.add_to_history()
        self.change_color()

    def set_jack(self, jack: str):
        if all([self.card_is(self.current_card, 'J'),
                self.possible_jack_choices()]):
            if jack not in FEN_DICT:
                assert issubclass(jack, Piece), f"Wrong value for `jack`: {jack}"
                jack = [k for k, v in FEN_DICT.items() if v == jack][0]
            self.jack = jack
        # elif not self.card_is(self.current_card, 'J') and not self.card_is(self.last_card, 'J'):
        else:
            self.jack = None

    def possible_jack_choices(self):
        """Return current player's possible choices for jack"""
        left = self.board.piece_types_left(color=self.invert_color(self.to_move))
        inverted_fen_dict = invert_dict(FEN_DICT)
        return [inverted_fen_dict[piece_type]
                for piece_type in left
                if piece_type != King]

    def set_check(self):
        color = self.invert_color(self.current_player.color)
        if self.board.color_is_checked(color):
            self.check = True
        else:
            self.check = False

    def set_mate(self):
        self.mate = self.check and self.stalemate

    def set_stalemate(self):

        if any([self.board.halfmoveclock == 100,
                len(self.board.all_taken()) == 2]):
            self.stalemate = True
            return
        color = self.invert_color(self.to_move)
        self.to_move = color
        for card in self._get_player_by_color(color).hand:
            if ok_karta([card], self.piles):
                # exclude the Queen because it can be played anytime,
                # but it can't help you during check
                # if self.check and card.rank == 'Q':
                    # continue
                # TODO: handle this shiit, it's still shady
                if self.possible_moves(card, stalemate_checking=True):
                    self.stalemate = False
                    self.to_move = self.invert_color(color)
                    return
            elif self.possible_moves(Card(1, '5'), stalemate_checking=True):
                self.stalemate = False
                self.to_move = self.invert_color(color)
                return
        self.stalemate = True
        self.to_move = self.invert_color(color)

    @property
    def player_should_lose_turn(self):
        number_of_moves = len(self.history)
        if number_of_moves < 2:
            return False
        if all([self.card_is(self.last_card, '4'),
                not self.card_is(self.current_card, '4')]):
            return True  # four is active
        if number_of_moves < 3:
            return False

        return not bool(self.possible_moves())

    def positions_taken_by_color(self, color):
        return [pos for pos in self.board.all_taken()
                if self.board[pos].color == color]

    def king_of_spades_active(self):
        if len(self.history) < 2:
            return False
        last_move = self.history.get_move_from_turn(-1)
        last_move_burned = last_move['burned']
        if not last_move_burned:
            if self.card_is(last_move['card'], 'K', 1):
                return True
        return False

    @staticmethod
    def get_piece_name(piece_class):
        """Do dummy initialization just to get the name."""
        return piece_class(WHITE_COLOR, 45).name

    def possible_moves(self, card=None, stalemate_checking=False):
        """Return a dict of possible moves.

            meant to be invoked after card was played and before move was made.
        """

        def convert_to_strings(dictionary):
            inverted_mapdict = get_inverted_mapdict()
            new = []
            for key, list_of_positions in dictionary.items():
                try:
                    start = inverted_mapdict[key]
                except KeyError:
                    start = key
                new.append((
                    start,
                    [inverted_mapdict[i] for i in list_of_positions]))
            return dict(new)

        possible_moves = {}
        card = card or self.current_card
        possible_start = self.positions_taken_by_color(self.to_move)
        self.logger.debug(f'Setting up... card={card} posstart={possible_start}')
        # if self.player_should_lose_turn:
        #     return possible_moves

        penultimate_move = self.history.get_move_from_turn(-2)
        last_move = self.history.get_move_from_turn(-1)
        last_move_burned = last_move['burned']
        if stalemate_checking:
            penultimate_move = last_move
            last_move = defaultdict(
                lambda: None,
                {'card': card,
                 'jack': FEN_DICT[self.jack] if self.jack else None})
        if not last_move_burned:
            if penultimate_move['move']:
                if self.card_is(last_move['card'], 'K', 1):
                    # if king of spades is active
                    self.logger.debug('King of spades active...')
                    possible_start = [penultimate_move['move'][0]]
                elif self.card_is(last_move['card'], 'K', 2):
                    # if king of hearts is active
                    self.logger.debug('King of hearts active...')
                    possible_start = [penultimate_move['move'][1]]
            if all([last_move['jack'] is not None,
                    not self.card_is(self.current_card, 'J')]):
                # if jack is active
                self.logger.debug('Jack active...')
                piece_name = self.get_piece_name(last_move['jack'])
                possible_start = self.board.positions_of_piece(
                    piece_name, self.to_move)
        if self.card_is(card, 'Q'):
            self.logger.debug('Queen active...')
            possible_start = self.board.positions_of_piece('Queen', self.to_move)

        for start in possible_start:
            self.logger.debug(f'Possible start at the end: {possible_start}')
            piece_card = card or Card(1, '5')  # mock card for moves checking
            try:
                end = [pos
                       for pos in self.board[start].moves(piece_card, self.board)
                       if not isinstance(self.board[pos], King)]
            except AttributeError:
                raise BadMoveError(f"Possible starts: {possible_start}, board: {self.board}")
            if end:
                possible_moves[start] = end
        self.logger.debug(f'Result: {convert_to_strings(possible_moves)}')
        return convert_to_strings(possible_moves)
