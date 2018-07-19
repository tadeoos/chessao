"""
Board and Pieces classes from Szachao module.

Pieces values according to Hans Berliner's system
(https://en.wikipedia.org/wiki/Chess_piece_relative_value)
"""
import random
from math import floor
from typing import List, Dict, Union, Iterable

from termcolor import colored

from chessao import WHITE_COLOR, BLACK_COLOR
from chessao.pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King
from chessao.cards import Card
from chessao.helpers import get_mapdict, get_inverted_mapdict

EMPTY = ' '

FEN_DICT = {
    'p': Pawn,
    'r': Rook,
    'n': Knight,
    'k': King,
    'q': Queen,
    'b': Bishop,
}


class Board:
    """
    Chess Board class.
    """

    def __init__(self, rand: bool = False, fenrep: str = None) -> None:
        """
        Board constructor.

        >>> 'K' in Board(rand=1).fen()
        True
        """
        self._brd: List[Union[int, str, Piece]] = [0 for i in range(120)]
        self.mapdict: Dict[str, int] = get_mapdict()
        self.capture_took_place: bool = False
        self.captured_pieces: List = []
        self.enpass: int = 300
        self.fullmove: int = 0
        self.halfmoveclock: int = 0

        if not fenrep:
            fenrep = 'RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr w KQkq - 0 1'

        for position in range(21, 99 + 1):
            if (position % 10 != 0) and (position % 10 != 9):
                self[position] = EMPTY

        if rand:
            for k in (BLACK_COLOR, WHITE_COLOR):
                rand2 = random.choice(self.list_empty_positions())
                self[rand2] = King(k, rand2)
                for (piece, quantity, pawn) in [(Pawn, 8, True), (Bishop, 2, False),
                                                (Knight, 2, False), (Rook, 2, False),
                                                (Queen, 1, False)]:
                    for i in range(random.randint(0, quantity)):
                        pos = random.choice(
                            self.list_empty_positions(random_pawn=pawn))
                        self[pos] = piece(k, pos)
        else:
            for (position, piece) in self.parse_fen(fenrep).items():
                self[position] = piece

    def __getitem__(self, key: Union[int, str]) -> Union[int, str, Piece]:
        """
        >>> b = Board()
        >>> b[2]
        0
        """
        if isinstance(key, str):
            try:
                key = self.mapdict[key.upper()]
            except KeyError:
                raise IndexError('Invalid square name: {}'.format(key))
        elif not isinstance(key, slice) and (key < 0 or key > 119):
            raise IndexError('Board index out of range')
        return self._brd[key]

    def __setitem__(self, key, value) -> None:
        self._brd[key] = value

    def pieces(self) -> Iterable[Piece]:
        """Generator yielding pieces on the board"""
        for position in self.all_taken():
            yield self[position]

    def _move_piece(self, pos_from: int, pos_to: int) -> None:
        """Replace the piece from `pos_from` to `pos_to`

        Args:
            pos_to (int)
            pos_from (int)
        """
        self[pos_to] = self[pos_from]
        piece = self[pos_to]
        if isinstance(piece, Piece):
            piece.position = pos_to
            piece.mvs_number += 1
        else:
            raise ValueError
        self[pos_from] = EMPTY

    def _turn_clock(self, piece_color: int, clock: bool = True):
        """If clock = i -> increment halfmoveclock else zero"""
        if clock:
            self.halfmoveclock += 1
        else:
            self.halfmoveclock = 0

        if self[piece_color].color == BLACK_COLOR:
            self.fullmove += 1

    def _enpassant_move(self, start_position_int: int, end_position_int: int, only_bool: bool):
        if only_bool:
            return True
        assert self.is_empty(end_position_int)
        self.capture_took_place = True
        if self[start_position_int].color == WHITE_COLOR:
            self.captured_pieces.append(self[end_position_int - 10])
            self[end_position_int - 10] = EMPTY
        else:
            self.captured_pieces.append(self[end_position_int + 10])
            self[end_position_int + 10] = EMPTY
        self._move_piece(pos_from=start_position_int, pos_to=end_position_int)
        self._turn_clock(piece_color=end_position_int, clock=False)
        # clearing enpass after enpass -> problem in pat functiong
        self.enpass = 300
        return self

    def _castle_move(self, start_position_int, end_position_int, only_bool):
        if only_bool:
            return True
        # determining rook position
        if end_position_int < start_position_int:
            rook_pos = (end_position_int - 2, end_position_int + 1)
        else:
            rook_pos = (end_position_int + 1, end_position_int - 1)
        # moving the king
        self._move_piece(pos_from=start_position_int, pos_to=end_position_int)
        # moving the rook
        self._move_piece(pos_from=rook_pos[0], pos_to=rook_pos[1])
        self._turn_clock(piece_color=end_position_int, clock=1)
        return self

    def _queen_move(self, start_position_int, end_position_int, only_bool):
        if only_bool:
            return True
        self.swap(start_position_int, end_position_int)
        self[end_position_int].mvs_number += 1
        self._turn_clock(piece_color=end_position_int, clock=1)
        return self

    def move(self, pos_from, pos_to=None, card=None, only_bool=False):
        """
        Move a piece on a board.

        Args:
            pos_from (str): e.g. 'A2'
            pos_to (str): e.g. 'A4'
            card (Card): a Card that is played alongisde the move
            only_bool (bool): check if move is valid, don't change state

        >>> Board(fenrep='R3K2R/8/8/8/8/8/8/8').move('E1','C1')  # roszada
        Board: 2KR3R/8/8/8/8/8/8/8 - - 1 0
        >>> Board(fenrep='R3K2R/8/8/pP6/8/NnrRqQbB/8/7k KQ').move('E1','G1')  # zła roszada
        Traceback (most recent call last):
        ...
        AssertionError: Move is not possible: E1 -> G1; R3K2R/8/8/pP6/8/NnrRqQbB/8/7k KQ - 0 0
        >>> Board(fenrep='R3K2R/8/8/pP6/8/NnrRqQbB/8/7k KQ').move('E1','C1')  #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        AssertionError: ...
        >>> Board(fenrep='K7/8/8/pP6/8/NnrRqQbB/8/r3k2r KQ').move('E8','C8')  #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        AssertionError: ...
        >>> Board(fenrep='R3K2R/8/8/Q7/8/8/8/8').move('A4','A1', Card(1,'Q'))
        Board: Q3K2R/8/8/R7/8/8/8/8 K - 1 0
        >>> Board(fenrep='R3K2R/8/8/P7/8/8/8/8').move('A4','A5', Card(1,'Q'))
        Board: R3K2R/8/8/8/P7/8/8/8 KQ - 0 0
        >>> Board(fenrep='R3K2R/8/8/P7/q7/8/8/3k4').move('A5','A4', Card(1,'6'))
        Board: R3K2R/8/8/q7/8/8/8/3k4 KQ - 0 1
        >>> Board(fenrep='R3K2R/8/8/P7/q7/8/1N6/k7').move('B7','A5', Card(1,'6'))  # can capture while check
        Board: R3K2R/8/8/P7/N7/8/8/k7 KQ - 0 0
        >>> b = Board()
        >>> b.move('D2','D4')
        Board: RNBQKBNR/PPP1PPPP/8/3P4/8/8/pppppppp/rnbqkbnr KQkq D3 0 0
        >>> b.move('A7','A6')
        Board: RNBQKBNR/PPP1PPPP/8/3P4/8/p7/1ppppppp/rnbqkbnr KQkq - 0 1
        >>> b.move('D4', 'D5')
        Board: RNBQKBNR/PPP1PPPP/8/8/3P4/p7/1ppppppp/rnbqkbnr KQkq - 0 1
        >>> b.move('E7','E5')
        Board: RNBQKBNR/PPP1PPPP/8/8/3Pp3/p7/1ppp1ppp/rnbqkbnr KQkq E6 0 2
        >>> b.move('D5','E6')
        Board: RNBQKBNR/PPP1PPPP/8/8/8/p3P3/1ppp1ppp/rnbqkbnr KQkq - 0 2
        >>> b.move('A6','A5')
        Board: RNBQKBNR/PPP1PPPP/8/8/p7/4P3/1ppp1ppp/rnbqkbnr KQkq - 0 3
        >>> b.move('A5', 'A4')
        Board: RNBQKBNR/PPP1PPPP/8/p7/8/4P3/1ppp1ppp/rnbqkbnr KQkq - 0 4
        >>> b.move('B2','B4')
        Board: RNBQKBNR/P1P1PPPP/8/pP6/8/4P3/1ppp1ppp/rnbqkbnr KQkq B3 0 4
        >>> b.move('A4','B3')
        Board: RNBQKBNR/P1P1PPPP/1p6/8/8/4P3/1ppp1ppp/rnbqkbnr KQkq - 0 5
        >>> b.move('H2', 'H5', only_bool=True)
        Traceback (most recent call last):
        ...
        AssertionError: Move is not possible: H2 -> H5; RNBQKBNR/P1P1PPPP/1p6/8/8/4P3/1ppp1ppp/rnbqkbnr KQkq - 0 5
        """

        card = card or Card(1, '5')

        self.capture_took_place = False
        start_position_int = self.mapdict[pos_from] if isinstance(
            pos_from, str) else pos_from
        end_position_int = self.mapdict[pos_to] if isinstance(
            pos_to, str) else pos_to

        if self.is_empty(start_position_int):
            raise ValueError(
                'There is no Piece in that field {}'.format(pos_from))

        assert end_position_int in self[start_position_int].moves(card, self), \
            f"Move is not possible: {pos_from} -> {pos_to}; {self.fen()}"

        # first check if the move is an enappsant one
        if self[start_position_int].name == 'Pawn':
            if self.enpass == end_position_int:
                return self._enpassant_move(start_position_int, end_position_int, only_bool)
            elif self[start_position_int].mvs_number == 0 and \
                    abs(start_position_int - end_position_int) == 20:  # then set enpassant
                self.enpass = (start_position_int + end_position_int) / 2
            else:
                self.enpass = 300

        # checking for castle
        if all([card.rank != 'K' or card.color not in (3, 4),
                self[start_position_int].name == 'King',
                abs(end_position_int - start_position_int) == 2]):
            return self._castle_move(start_position_int, end_position_int, only_bool)

        # checking for Queen card and valid Queen move
        enemy_pieces_left = self.piece_types_left(
            self[start_position_int].color)
        if all([card.rank == 'Q',
                self[start_position_int].name == 'Queen',
                enemy_pieces_left != {King, Queen}]):
            return self._queen_move(start_position_int, end_position_int, only_bool)

        else:
            # default move
            if only_bool:
                return True
            if self[start_position_int].name == 'Pawn':
                clock_value = 0
            else:
                clock_value = 1
            if not self.is_empty(end_position_int):
                self.capture_took_place = True
                clock_value = 0
                self.captured_pieces.append(self[end_position_int])
            self._move_piece(pos_from=start_position_int,
                             pos_to=end_position_int)
            self._turn_clock(piece_color=end_position_int, clock=clock_value)
            return self

        raise ValueError(
            'BŁĄD w funkcji move! skad {} dokad {} card {} mvs {}, enpas {}'.format(
                pos_from, pos_to, card, self[start_position_int].mvs_number, self.enpass))

    def __str__(self, color=WHITE_COLOR):

        def colorize(first, second):
            result = ''
            if position % 10 == 1:
                result += ' ' * 4
            if position % 10 != 8 and (position % 10) % 2 == 1:
                result += colored('{!s:} '.format(self[position]), first, attrs=['reverse'])
            elif position % 10 != 8:
                result += colored('{!s:} '.format(self[position]), second, attrs=['reverse'])
            else:
                result += colored('{!s:} '.format(self[position]), second, attrs=['reverse'])
                result += f' {row}\n'
            return result

        top = '    {:<2}{:<2}{:<2}{:<2}{:>2}{:>2}{:>2}{:>2}\n'.format(
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
        result = ''
        for position in range(len(self._brd)):
            row = int(((position - (position % 10)) / 10) - 1)
            if self[position] == 0:
                continue
            if row % 2 == 1:
                result += colorize('grey', 'white')
            else:
                result += colorize('white', 'grey')

        result = result[:-1]  # remove trailing \n
        if color == WHITE_COLOR:
            rows = result.split('\n')
            result = '\n'.join(rows[::-1])
        return top + result

    def print_for(self, color):
        return self.__str__(color)

    def __repr__(self):
        return 'Board: {}'.format(self.fen())

    def print_positions(self):
        result_str = ''
        for i, el in enumerate(self._brd):
            if i % 10 == 0:
                result_str += '\n'
            appending = str(i) if el != 0 else '0'
            result_str += ' {} '.format(appending)
        return result_str

    def is_empty(self, i):
        try:
            return self[i] == EMPTY
        except IndexError:
            return False

    def list_empty_positions(self, random_pawn=False):
        """Return list of empty positions."""
        if random_pawn:
            return [i for i in range(len(self._brd))
                    if self[i] == EMPTY and floor(i / 10) not in (2, 9)]
        return [i for i in range(len(self._brd)) if self[i] == EMPTY]

    def all_taken(self) -> List[int]:
        """Return list of positions taken by some Piece."""
        return [i for i in range(len(self._brd))
                if self[i] != EMPTY and self[i] != 0]

    def positions_of_piece(self, piece_name, color, as_str=False):
        """Reterurn a list of positions of a specified Piece of a specified color."""
        positions = [i for i in self.all_taken()
                     if self[i].name == piece_name and self[i].color == color]
        if as_str:
            inverted = get_inverted_mapdict()
            return [inverted[pos] for pos in positions]
        return positions

    def piece_types_left(self, color):
        taken = self.all_taken()
        return {type(self[pos]) for pos in taken if self[pos].color == color}

    def get_piece(self, position):
        if type(position) == str:
            return self[self.mapdict[position]]
        return self[position]

    def get_points(self, col):
        """
        Returns a sum of points for pieces of color col

        >>> Board().get_points('b') > 49
        True
        """
        return sum([self[i].val
                    for i in self.all_taken()
                    if self[i].color == col])

    def swap(self, pos_a, pos_b):
        """Swap what's on two positions. Asserts that pos_b is not empty."""
        self[pos_a], self[pos_b] = self[pos_b], self[pos_a]
        if not self.is_empty(pos_b):
            self[pos_b].position = pos_b
        assert not self.is_empty(pos_a)
        self[pos_a].position = pos_a
        return self

    def color_is_checked(self, color):
        """
        >>> b = Board(fenrep='8/8/K7/8/r7/8/k7/8')
        >>> b.color_is_checked(WHITE_COLOR)
        True
        >>> b.color_is_checked(BLACK_COLOR)
        False
        """
        king_pos = self.positions_of_piece('King', color)
        assert len(king_pos) == 1
        return True if self.under_attack(king_pos[0], color) else False

    def check_castle(self, color):
        """
        Returns a dictionary with castle metadata

        >>> Board().check_castle('b')
        {'possible_castles': 0, 'long': 0, 'short': 0}
        >>> Board().check_castle('c')
        {'possible_castles': 0, 'long': 0, 'short': 0}
        >>> b = Board(fenrep='R3K2R/PPPPP3/8/pP6/8/Nnr1qQbB/8/7k KQ')
        >>> b.check_castle('b')
        {'possible_castles': 2, 'long': 23, 'short': 27}
        """
        king_pawn = self.positions_of_piece('King', color)[0]
        rook_positions = self.positions_of_piece('Rook', color)

        castle_dict = {'possible_castles': 0, 'long': 0, 'short': 0}

        if any([self[king_pawn].mvs_number > 0,
                len(rook_positions) == 0,
                self.color_is_checked(color)]):
            return castle_dict

        castle_counter = 0
        for rook_pos in rook_positions:
            if self[rook_pos].mvs_number > 0:
                continue

            long_castle = rook_pos < king_pawn
            if long_castle:
                in_between_positions = [
                    i for i in range(rook_pos + 1, king_pawn)]
            else:
                in_between_positions = [
                    i for i in range(king_pawn + 1, rook_pos)]

            can_castle = True
            for pos in in_between_positions:
                if not self.is_empty(pos) or self.under_attack(pos, color):
                    can_castle = False
                    break
            if can_castle:
                castle_counter += 1
                if long_castle:
                    castle_dict['long'] = rook_pos + 2
                else:
                    castle_dict['short'] = rook_pos - 1

        castle_dict['possible_castles'] = castle_counter
        return castle_dict

    def fen(self):
        """
        Return a FEN representation of a board.

        >>> Board().fen()
        'RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr KQkq - 0 0'
        >>> Board(fenrep="1NBQK2R/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr").fen()
        '1NBQK2R/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr Kkq - 0 0'
        """
        res = ''
        for i in range(2, 10):
            start = i * 10 + 1
            end = start + 8
            row = self[start:end]
            res += self.fen_row(row) + '/'

        white_castle = self.fen_castle(WHITE_COLOR)
        black_castle = self.fen_castle(BLACK_COLOR)
        jc = white_castle + black_castle
        c = '-' if jc == '' else jc

        enp = '-' if self.enpass not in self.mapdict.values() else [k for (
            k, v) in self.mapdict.items() if v == self.enpass][0]
        ret = [res[:-1], c,
               str(enp), str(self.halfmoveclock), str(self.fullmove)]
        return ' '.join(ret)

    def fen_castle(self, color):
        """Return castle part of FEN_DICT

        >>> b = Board()
        >>> b.fen_castle('b')
        'KQ'
        >>> b.fen_castle('c')
        'kq'
        """
        if Rook not in self.piece_types_left(color) or King not in self.piece_types_left(color):
            return ''
        result = ''
        king_pos = self.positions_of_piece('King', color)[0]
        rooks_postions = self.positions_of_piece('Rook', color)
        rooks_postions.sort(reverse=True)  # start iteration with King side
        if self[king_pos].mvs_number > 0:
            return ''
        for rook_pos in rooks_postions:
            if self[rook_pos].mvs_number > 0 or int(rook_pos / 10) != int(king_pos / 10):
                continue
            if rook_pos > king_pos:
                result += 'K'
            else:
                result += 'Q'
        assert len(result) < 3, 'Fen caslte cannot give more than 2 results'
        if len(result) == 2:
            assert len(set(result)) == 2, f"Got two of the same when parsing FEN {self}"
        if color == BLACK_COLOR:
            result = result.lower()
        return result

    @staticmethod
    def parse_fen(fen):
        """
        Returns dictionary {pos: piece}.

        >>> Board.parse_fen('RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr KQkq - 0 0')
        ...     #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        {21: <chessao.pieces.Rook object at 0x...>, 22: <chessao.pieces.Knight object at 0x...>,
        23: <chessao.pieces.Bishop object at 0x...>, 24: <chessao.pieces.Queen object at 0x...>,
        25: <chessao.pieces.King object at 0x...>, 26: <chessao.pieces.Bishop object at 0x...>,
        27: <chessao.pieces.Knight object at 0x...>, 28: <chessao.pieces.Rook object at 0x...>,
        31: <chessao.pieces.Pawn object at 0x...>, 32: <chessao.pieces.Pawn object at 0x...>,
        33: <chessao.pieces.Pawn object at 0x...>, 34: <chessao.pieces.Pawn object at 0x...>,
        35: <chessao.pieces.Pawn object at 0x...>, 36: <chessao.pieces.Pawn object at 0x...>,
        37: <chessao.pieces.Pawn object at 0x...>, 38: <chessao.pieces.Pawn object at 0x...>,
        81: <chessao.pieces.Pawn object at 0x...>, 82: <chessao.pieces.Pawn object at 0x...>,
        83: <chessao.pieces.Pawn object at 0x...>, 84: <chessao.pieces.Pawn object at 0x...>,
        85: <chessao.pieces.Pawn object at 0x...>, 86: <chessao.pieces.Pawn object at 0x...>,
        87: <chessao.pieces.Pawn object at 0x...>, 88: <chessao.pieces.Pawn object at 0x...>,
        91: <chessao.pieces.Rook object at 0x...>, 92: <chessao.pieces.Knight object at 0x...>,
        93: <chessao.pieces.Bishop object at 0x...>, 94: <chessao.pieces.Queen object at 0x...>,
        95: <chessao.pieces.King object at 0x...>, 96: <chessao.pieces.Bishop object at 0x...>,
        97: <chessao.pieces.Knight object at 0x...>, 98: <chessao.pieces.Rook object at 0x...>}
        """
        rows = fen.split('/')
        res_dict = {}
        for i in range(len(rows)):
            res_dict.update(Board.parse_row_fen(rows[i], (i + 2) * 10))
        return res_dict

    @staticmethod
    def parse_row_fen(row_str, i):
        """
        >>> Board.parse_row_fen('RNBQKBNR', 20) #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        {21: <chessao.pieces.Rook object at 0x...>, 22: <chessao.pieces.Knight object at 0x...>,
         23: <chessao.pieces.Bishop object at 0x...>, 24: <chessao.pieces.Queen object at 0x...>,
         25: <chessao.pieces.King object at 0x...>, 26: <chessao.pieces.Bishop object at 0x...>,
         27: <chessao.pieces.Knight object at 0x...>, 28: <chessao.pieces.Rook object at 0x...>}
        >>> Board.parse_row_fen('kPppRnNP', 10) #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        {11: <chessao.pieces.King object at 0x...>, 12: <chessao.pieces.Pawn object at 0x...>,
         13: <chessao.pieces.Pawn object at 0x...>, 14: <chessao.pieces.Pawn object at 0x...>,
         15: <chessao.pieces.Rook object at 0x...>, 16: <chessao.pieces.Knight object at 0x...>,
         17: <chessao.pieces.Knight object at 0x...>, 18: <chessao.pieces.Pawn object at 0x...>}
        >>> rf = Board.parse_row_fen('3pP3', 40)
        >>> rf #doctest: +ELLIPSIS
        {44: <chessao.pieces.Pawn object at 0x...>, 45: <chessao.pieces.Pawn object at 0x...>}
        >>> rf[44].color != rf[45].color
        True
        >>> Board.parse_row_fen('rnbqkbnr KQkq - 0 0', 90) #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        {91: <chessao.pieces.Rook object at 0x...>, 92: <chessao.pieces.Knight object at 0x...>,
         93: <chessao.pieces.Bishop object at 0x...>, 94: <chessao.pieces.Queen object at 0x...>,
         95: <chessao.pieces.King object at 0x...>, 96: <chessao.pieces.Bishop object at 0x...>,
         97: <chessao.pieces.Knight object at 0x...>, 98: <chessao.pieces.Rook object at 0x...>}
        """
        pos = i + 1
        pieces_dict = {}
        counter = 0
        while counter < len(row_str) and pos < i + 9:
            if row_str[counter].isnumeric():
                pos += int(row_str[counter])
            else:
                color = WHITE_COLOR if row_str[counter].isupper(
                ) else BLACK_COLOR
                piece = FEN_DICT[row_str[counter].lower()]
                pieces_dict[pos] = piece(color, pos)
                pos += 1
            counter += 1
        return pieces_dict

    @staticmethod
    def get_fen_rep(piece):
        letter = 'n' if piece.name == 'Knight' else piece.name[0]
        if piece.color == WHITE_COLOR:
            return letter.upper()
        else:
            return letter.lower()

    def fen_row(self, row):
        """Return a fen represenation of a row"""
        res_row = ''
        empty_counter = 0
        for i in row:
            if i == EMPTY:
                empty_counter += 1
            elif empty_counter == 0:
                res_row += self.get_fen_rep(i)
            else:
                res_row += str(empty_counter) + self.get_fen_rep(i)
                empty_counter = 0
        if empty_counter > 0:
            res_row += str(empty_counter)
        return res_row

    def under_attack(self, square, color):
        """
        Return True if a position is under attack,
        by an oposite color then `color`

        >>> Board(fenrep='R3K2R/8/8/8/8/8/8/8').under_attack(88,'b')
        False
        >>> Board(fenrep='R3K2R/8/8/8/8/8/8/8').under_attack(35,'c')
        True
        >>> Board(fenrep='b3K2R/8/8/8/8/8/8/8').under_attack(32,'b')
        True
        >>> Board(fenrep='N3K2R/8/8/8/8/8/8/8').under_attack(33,'c')
        True
        >>> Board(fenrep='R3K2R/8/8/8/8/8/8/8').under_attack(81,'c')
        True
        >>> Board(fenrep='R3K2R/P7/8/8/8/8/8/8').under_attack(42,'c')
        True
        """

        def non_sliding_piece_check(position, move_range, piece_type):
            for i in move_range:
                potential_capturing_piece_pos = position + i
                if (type(self[potential_capturing_piece_pos]) == piece_type and
                        self[potential_capturing_piece_pos].color != color):
                    return True
            return False

        def sliding_piece_check(position, move_range, piece_type):
            for i in move_range:
                a = position + i
                while (self[a] != 0):
                    if not self.is_empty(a):
                        if self[a].color != color:
                            if type(self[a]) == piece_type or type(self[a]) == Queen:
                                return True
                            else:
                                break
                        else:
                            break
                    a += i
            return False

        pawn_range = (9, 11) if color == WHITE_COLOR else (-9, -11)

        for move_range, piece_type in (
            ((1, -1, 10, -10, 9, 11, -9, -11), King),
            ((-12, -21, -19, -8, 8, 19, 21, 12), Knight),
            (pawn_range, Pawn)
        ):
            if non_sliding_piece_check(square, move_range, piece_type):
                return True

        for move_range, piece_type in (
            ((1, 10, -1, -10), Rook),
            ((9, 11, -11, -9), Bishop),
        ):
            if sliding_piece_check(square, move_range, piece_type):
                return True

        return False
