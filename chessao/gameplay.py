import logging
from collections import defaultdict
from pprint import pformat
from typing import List, Optional, Tuple, Dict, Any, Union, Type

from chessao import WHITE_COLOR, BLACK_COLOR, MAPDICT
from chessao.cards import Card, ChessaoCards
from chessao.chess import Board, FEN_DICT, EMPTY

from chessao.pieces import King, Piece, Queen
from chessao.players import Player
from chessao.helpers import invert_dict, convert_to_strings
from chessao.history import ChessaoHistory


class ChessaoError(Exception):
    pass


class DiscardMissingError(ChessaoError):
    pass


class BadMoveError(ChessaoError):
    pass


class CardsRemovalError(ChessaoError):
    pass


class CardValidationError(ChessaoError):
    pass


class ChessaoGame:
    """A gameplay class."""

    def __init__(self, players, board=None, cards=None, **kwargs):

        self.board = board or Board(fenrep=kwargs.get("fen"))
        self.cards = cards or ChessaoCards()
        self.history = kwargs.get('history', ChessaoHistory(self.board))
        self.current_move = kwargs.get('current_move', None)
        self.to_move = kwargs.get('to_move', WHITE_COLOR)
        self.check = kwargs.get('check', False)
        self.mate = kwargs.get('mate', False)
        self.stalemate = kwargs.get('stalemate', False)
        self.promotion = kwargs.get('promotion', False)
        self.last_player_number_of_moves = 12
        # self.can_capture = kwargs.get('can_capture', True)
        self.jack = kwargs.get('jack', None)
        # self.three = kwargs.get('three', 0)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.WARNING)

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
                    ledger: List,
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
            chessao.full_move(
                cards=[record.card],
                move=record.move,
                pile=record.pile,
                burn=record.burned,
                jack=record.jack,
                cards_to_discard=record.discarded)
        return chessao

    def __str__(self):
        blacks = self._get_player_by_color(WHITE_COLOR)
        whites = self._get_player_by_color(BLACK_COLOR)

        return f"""\
PILES: |{str(self.piles[0][-1]):>3} |  |{str(self.piles[1][-1]):>3} |
CURRENT_CARD:  {'!' if self.burned else ''}{self.current_card}
{blacks.name} {blacks.id} (white): {blacks.hand}
{self.board.print_for(self.to_move)}
{whites.name} {whites.id} (black): {whites.hand}"""

    # History:
    # {self.cards.starting_deck}
    # {self.history}"""

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
    def last_move(self):
        return self.history.get_move_from_turn(-1)

    @property
    def moves(self):
        return len(self.history) - 1

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
        second_go_after_king = self.card_is(self.penultimate_card, 'K', 1)
        if all([self.card_is(self.last_card, '3'),
                not self.card_is(self.current_card, '3'),
                not second_go_after_king]):
            three = 5 if self.card_is(self.penultimate_card, '3') else 3
        else:
            three = 0
        return three

    @staticmethod
    def invert_color(color):
        if color == WHITE_COLOR:
            return BLACK_COLOR
        return WHITE_COLOR

    def card_is(self, card: Card, rank: str = None, color: int = None):
        if card is None:
            return False
        return card.is_(rank, color)

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

    def get_white(self):
        return self._get_player_by_color(WHITE_COLOR)

    def get_black(self):
        return self._get_player_by_color(BLACK_COLOR)

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
                  cards_to_discard: Optional[List[Card]] = None,
                  promotion: Optional[str] = None) -> None:

        if cards is None:  # for tests purposes
            cards = self.current_player.choose_any()
            burn = True
        if self.king_of_spades_active():
            self._play_penultimate_card()
        else:
            self.play_cards(cards, pile, burn, jack=jack, cards_to_remove=cards_to_discard)

        # Handle Ace
        if self.card_is(self.current_card, 'A'):
            if not self.check:
                self.swap_players_color()
                self.add_to_history()
                return
        if self.player_should_lose_turn:
            self.logger.info("Player loosing turn...")
            move = []
        self.chess_move(move, promotion)
        self.end_move()

    def play_cards(self,
                   cards: List[Card],
                   pile: int = 0,
                   burn: bool = False,
                   jack: Optional[str] = None,
                   cards_to_remove: Optional[List[Card]] = None):
        self._cards_checks(cards[-1], burn)
        try:
            self.current_player.remove_cards(cards)
        except ValueError:
            msg = (f"Moves: {len(self.history)}, reshuffled: {self.cards.reshuffled}"
                   f" cards: {cards}, player: {self.current_player}, last three moves: {self.history.ledger[-3:]}")
            raise CardsRemovalError(msg) from None
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
        self.discarded_cards = cards_to_remove
        self.current_player.remove_cards(cards_to_remove)
        self.cards.burned.extend(cards_to_remove)
        self.current_player.update_cards(
            self.cards.deal(len(cards_to_remove)))

    def _play_penultimate_card(self):
        pen_move = self.history.get_move_from_turn(-2)
        card = pen_move['card']
        burn = pen_move['burned']
        self.cards._put_card(card, burn)

    def _revert_last_move(self):
        done_move = self.last_move['move']
        assert done_move, f"Can't redo undone move: {self.last_move}, Board:\n{self.board}"
        self.board.revert_move(done_move[0], done_move[1])

    def chess_move(self, move: List[str], promotion: Optional[str]):
        if not move:
            self.current_move = []
            return
        start, end = move[0], move[1]
        possible_moves = self.possible_moves()
        assert start in possible_moves, f'{self.possible_moves()}| {self.current_card}'
        move_ends = possible_moves[move[0]]
        assert end in move_ends, f'{self.possible_moves()}| {self.current_card}| {self.board.fen()}'
        card_to_use_for_move = self.current_card
        if self.check and self.card_is(self.current_card, 'Q'):
            card_to_use_for_move = None
        self.board.move(start, end, card_to_use_for_move, promotion)
        self.current_move = [start, end]

    def end_move(self):
        if self.card_is(self.current_card, 'K', 1) and self.moves > 0 and self.last_move['move']:
            self.logger.info("Handling king of spades...")
            pm = self.history.get_move_from_turn(-2)
            self.check = pm['check']
            self.stalemate = pm.get('stalemate', None)  # TODO: what is this?
            self.mate = pm['mate']
            self._revert_last_move()
        else:
            self.set_check()
            self.set_stalemate()
            self.set_mate()

        self.add_to_history()
        self.change_color()

    def set_jack(self, jack: Union[str, Type[Piece]]):
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

    def all_possible_moves_on_cards(self, hand, stalemate=False
                                    ) -> Dict[str, Dict[str, List[str]]]:
        """Return dict for possible moves on every card."""
        moves = {}
        moves['neutral'] = self.possible_moves(Card(1, '5'), stalemate)
        for card in [*filter(lambda card: card.rank not in '345678910JA', hand)]:
            if self.cards.validate_cards([card]):
                moves[card] = self.possible_moves(card, stalemate)
        return moves

    @staticmethod
    def possible_moves_count(possible_moves_dict: Dict[Any, Dict[Any, List[Any]]]) -> int:
        moves = set()

        for moves_dict in possible_moves_dict.values():
            pairs = {
                (k, v[i])
                for k, v in moves_dict.items()
                for i in range(len(v))
            }
            moves.update(pairs)

        return len(moves)

    def check_if_sufficient_material(self):
        """ugly as hell..."""
        pieces_left = self.board.pieces_left()
        # len(self.board.all_taken()) == 2
        if len(pieces_left) > 4:
            return True
        pieces_by_color = defaultdict(list)
        for piece in pieces_left:
            pieces_by_color[piece.color].append(piece)

        if len(pieces_by_color[WHITE_COLOR]) == 1:
            # must be king
            oponents_pieces = {piece.name.lower() for piece in pieces_by_color[BLACK_COLOR]}
            if oponents_pieces in [{'king', 'knight'}, {'king', 'bishop'}, {'king'}]:
                return False

        if len(pieces_by_color[BLACK_COLOR]) == 1:
            # must be king
            oponents_pieces = {piece.name.lower() for piece in pieces_by_color[WHITE_COLOR]}
            if oponents_pieces in [{'king', 'knight'}, {'king', 'bishop'}, {'king'}]:
                return False

        if len(pieces_by_color[WHITE_COLOR]) == 2 == len(pieces_by_color[BLACK_COLOR]):
            white_pieces = sorted([piece.name for piece in pieces_by_color[WHITE_COLOR]])
            black_pieces = sorted([piece.name for piece in pieces_by_color[BLACK_COLOR]])
            if white_pieces == ["Bishop", "King"] == black_pieces:
                colors = {getattr(piece, "piece_color", None) for piece in pieces_left}
                if len(colors) == 2:
                    return False
        return True

    def set_stalemate(self):
        cur_player = self.current_player
        if self.board.halfmoveclock == 100 or not self.check_if_sufficient_material():
            self.stalemate = True
            if self.board.halfmoveclock == 100:
                self.logger.info('Stalemate out of boringness')
            else:
                self.logger.info('Stalemate: insufficient material')
            return
        color = self.invert_color(self.to_move)
        self.to_move = color
        checked_player = self._get_player_by_color(color)
        assert cur_player.name != checked_player.name

        if self.cards.any_in(['K1'], checked_player.hand):
            self.stalemate = False
            self.to_move = self.invert_color(color)
            return
        possible_moves = self.all_possible_moves_on_cards(
            checked_player.hand, stalemate=True
        )

        number_of_possible_moves = self.possible_moves_count(possible_moves)
        self.last_player_number_of_moves = number_of_possible_moves

        player_can_lose_turn = any([
            self.card_is(self.current_card, 'K', 2),
            self.card_is(self.current_card, '4'),
            self.card_is(self.current_card, 'J'),
        ]) and not self.check

        if number_of_possible_moves == 0 and not player_can_lose_turn:
            self.stalemate = True
        else:
            self.stalemate = False
        self.to_move = self.invert_color(color)

    @property
    def player_should_lose_turn(self):
        if self.check:
            return False
        if self.card_is(self.current_card, 'K', 1) and self.moves > 0:
            self.logger.debug("King of spades played - ignoring move")
            return True
        if all([self.card_is(self.last_card, '4'),
                not self.card_is(self.current_card, '4')]):
            self.logger.debug("Four is active - ignoring move")
            return True  # four is active

        have_moves = bool(self.possible_moves())
        if not have_moves:
            self.logger.debug(f"Player {self.current_player} should lose turn")
        return not have_moves

    def positions_taken_by_color(self, color):
        return [pos for pos in self.board.all_taken()
                if self.board[pos].color == color]

    def king_of_spades_active(self):
        if self.moves < 2:
            return False
        last_move = self.history.get_move_from_turn(-1)
        penultimate_move = self.history.get_move_from_turn(-2)
        last_move_burned = last_move['burned']
        if not last_move_burned and penultimate_move['move']:
            if self.card_is(last_move['card'], 'K', 1):
                return True
        return False

    @staticmethod
    def get_piece_name(piece_class):
        """Do dummy initialization just to get the name."""
        if isinstance(piece_class, str):
            piece_class = FEN_DICT[piece_class.lower()]
        return piece_class(WHITE_COLOR, 45).name

    def possible_moves(self, card=None, stalemate_checking=False):
        """Return a dict of possible moves.

            meant to be invoked after card was played and before move was made
            or during stalemate checking.
        """

        card = card or self.current_card
        possible_start = self.positions_taken_by_color(self.to_move)
        # self.logger.debug(f'Setting up... card={card} posstart={possible_start}')
        penultimate_move = self.history.get_move_from_turn(-2)
        last_move = self.history.get_move_from_turn(-1)

        if stalemate_checking:
            # mock a situation as one move ahead
            penultimate_move = last_move
            last_move = defaultdict(
                lambda: None,
                {'card': self.current_card,
                 'jack': FEN_DICT[self.jack] if self.jack else None})

        filtered_possible_starts, blacklisted_moves = self._filter_possible_starts(
            possible_start=possible_start,
            card=card,
            penultimate_move=penultimate_move,
            last_move=last_move
        )
        possible_moves = self._get_possible_moves(filtered_possible_starts, card, blacklisted_moves)
        if not possible_moves and self.check and self._one_of_kings_is_active():
            # we're not filtering starts here...
            return self._get_possible_moves(possible_start, card, blacklisted_moves)
        # self.logger.debug(f'Possible starts: {filtered_possible_start}')
        # self.logger.debug(f'Blacklisted: {blacklisted_moves}')
        return possible_moves

    def _one_of_kings_is_active(self):
        last_move = self.history.get_move_from_turn(-1)
        was_king_of_spades = self.card_is(last_move['card'], 'K', 1)
        was_king_of_hearts = self.card_is(last_move['card'], 'K', 2)
        return not last_move['burned'] and (was_king_of_hearts or was_king_of_spades)

    def _filter_possible_starts(
            self, possible_start,
            card, penultimate_move,
            last_move
    ) -> Tuple[List[int], List[int]]:
        """Shrink down default possible starting positions based on active special cards."""

        blacklisted_moves = []  # for king of spades
        if not last_move['burned']:
            if penultimate_move['move']:

                if self.card_is(last_move['card'], 'K', 1):
                    self.logger.debug('King of spades active...')
                    possible_start = [penultimate_move['move'][0]]
                    blacklisted_moves.append(MAPDICT[penultimate_move['move'][1]])

                elif self.card_is(last_move['card'], 'K', 2):
                    self.logger.debug('King of hearts active...')
                    last_move_end = penultimate_move['move'][1]
                    if self.board[last_move_end].color == self.to_move:
                        possible_start = [MAPDICT[penultimate_move['move'][1]]]
                    else:
                        possible_start = []

        if all([last_move['jack'] is not None,
                not self.card_is(self.current_card, 'J'),
                not self.check]):
            self.logger.debug('Jack active...')
            piece_name = self.get_piece_name(last_move['jack'])
            possible_start = self.board.positions_of_piece(piece_name, self.to_move)
        elif self.card_is(card, 'Q') and Queen in self.board.piece_types_left(self.to_move) and not self.check:
            self.logger.debug('Queen active...')
            possible_start = self.board.positions_of_piece('Queen', self.to_move)

        return possible_start, blacklisted_moves

    def _get_possible_moves(self, possible_start: List[int],
                            card: Optional[Card],
                            blacklisted_moves: List[int]) -> Dict[str, List[str]]:
        possible_moves = {}
        for start in possible_start:
            # self.logger.debug(f'Possible start at the end: {possible_start}')
            piece_card = card or Card(1, '5')  # mock card for moves checking
            if self.check:
                if piece_card.rank == 'Q':
                    # player played queen card while being under check -- it doesnt have effect
                    piece_card = Card(1, '5')
            try:
                end = [
                    pos
                    for pos in self.board[start].moves(piece_card, self.board)
                    if not isinstance(self.board[pos], King) and pos not in blacklisted_moves
                ]
            except (AttributeError, TypeError):
                msg = (f"Possible starts: {possible_start}, move: {self.current_move}, card: {card}"
                       f"Current_player: {self.current_player} Last 2 moves: {self.history.get()[-2:]}"
                       f"\nBoard: {self.board}")
                raise BadMoveError(msg)
            if end:
                possible_moves[start] = end
        return convert_to_strings(possible_moves)

    def _cards_checks(self, card, burn=False):
        if burn:
            return
        if self.jack and self.card_is(card, 'Q'):
            raise CardValidationError('Cannot play Queen card after Jack card')
        if self.check and self.card_is(card, 'A'):
            raise CardValidationError('Cannot play Ace when checked')
        pm = self.history.get_move_from_turn(-2)
        if all([pm['check'],
                self.last_player_number_of_moves < 2,
                self.card_is(card, 'K', 1)]):
            raise CardValidationError('Cannot mate with King of spades')
