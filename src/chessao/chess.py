"""
Board and Pieces classes from Szachao module.

Pieces values according to Hans Berliner's system
(https://en.wikipedia.org/wiki/Chess_piece_relative_value)
"""
import random
# from copy import deepcopy
from math import floor
from termcolor import colored
from chessao.pieces import Pawn, Rook, Knight, Bishop, Queen, King
from chessao.cards import Card

EMPTY = ' '


class Board:
    """
    Chess Board class.
    """

    def __init__(self, rand=False, fenrep=None):
        """
        Board constructor.

        >>> 'K' in Board(rand=1).fen()
        True
        """
        self.brd = [0 for i in range(120)]
        self.mapdict = {l + str(j - 1): 10 * j + 1 + 'ABCDEFGH'.index(l)
                        for j in range(2, 10) for l in 'ABCDEFGH'}
        self.bicie = False
        self.zbite = []
        self.enpass = 300
        self.fullmove = 0
        self.halfmoveclock = 0

        if not fenrep:
            fenrep = 'RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr w KQkq - 0 1'

        for position in range(21, 99 + 1):
            if (position % 10 != 0) and (position % 10 != 9):
                self.brd[position] = EMPTY

        # # TODO: use fenrep only!!!
        # if not rand and not fenrep:
        #     for i in range(31, 39):
        #         self.brd[i] = Pawn(color='b', position=i)
        #     for i in range(81, 89):
        #         self.brd[i] = Pawn('c', i)
        #     fun = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        #     for i in ([20, 'b'], [90, 'c']):
        #         for j in range(1, 9):
        #             self.brd[i[0] + j] = \
        #                 fun[(j - 1)](color=i[1], position=(i[0] + j))
        if rand:
            for k in ('c', 'b'):
                rand2 = random.choice(self.all_empty())
                self.brd[rand2] = King(k, rand2)
                for (piece, quantity, pawn) in [(Pawn, 8, True), (Bishop, 2, False),
                                                (Knight, 2, False), (Rook, 2, False),
                                                (Queen, 1, False)]:
                    rand = random.randint(0, quantity)
                    for i in range(rand):
                        pos = random.choice(self.all_empty(random_pawn=pawn))
                        self.brd[pos] = piece(k, pos)
        else:
            for (position, piece) in self.parse_fen(fenrep).items():
                self.brd[position] = piece

    def pieces(self):
        """Generator yielding pieces on the board"""
        for position in self.all_taken():
            yield self.brd[position]

    def _move_piece(self, pos_to, pos_from):
        """Replace the piece from for the piece to"""
        self.brd[pos_to] = self.brd[pos_from]
        self.brd[pos_to].position = pos_to
        self.brd[pos_to].mvs_number += 1
        self.brd[pos_from] = EMPTY
        return

    def _turn_clock(self, piece_color, clock=1):
        """If clock = i -> increment else zero"""
        if clock:
            self.halfmoveclock += 1
        else:
            self.halfmoveclock = 0
        if self.brd[piece_color].color == 'c':
            self.fullmove += 1
        return

    def rusz(self, pos_from, pos_to=None, karta=Card(1, '5'), only_bool=False):
        """
        Move a piece on a board.

        >>> Board(fenrep='R3K2R/8/8/8/8/8/8/8').rusz('E1','C1')  # roszada
        True
        >>> Board(fenrep='R3K2R/8/8/pP6/8/NnrRqQbB/8/7k KQ').rusz('E1','G1')  # zła roszada
        Traceback (most recent call last):
        ...
        AssertionError: Move is not possible: E1 -> G1; R3K2R/8/8/pP6/8/NnrRqQbB/8/7k KQ- - 0 0
        >>> Board(fenrep='R3K2R/8/8/pP6/8/NnrRqQbB/8/7k KQ').rusz('E1','C1')  #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        AssertionError: ...
        >>> Board(fenrep='K7/8/8/pP6/8/NnrRqQbB/8/r3k2r KQ').rusz('E8','C8')  #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        AssertionError: ...
        >>> Board(fenrep='R3K2R/8/8/Q7/8/8/8/8').rusz('A4','A1', Card(1,'Q'))
        True
        >>> Board(fenrep='R3K2R/8/8/P7/8/8/8/8').rusz('A4','A5', Card(1,'Q'))
        True
        >>> Board(fenrep='R3K2R/8/8/P7/q7/8/8/8').rusz('A5','A4', Card(1,'6'))
        True
        >>> Board(fenrep='R3K2R/8/8/P7/q7/8/1N6/8').rusz('B7','A5', Card(1,'6'))
        True
        >>> b = Board()
        >>> b.rusz('D2','D4')
        True
        >>> b.rusz('A7','A6')
        True
        >>> b.rusz('D4', 'D5')
        True
        >>> b.rusz('E7','E5')
        True
        >>> b.rusz('D5','E6')
        True
        >>> b.rusz('A6','A5')
        True
        >>> b.rusz('A5', 'A4')
        True
        >>> b.rusz('B2','B4')
        True
        >>> b.rusz('A4','B3')
        True
        >>> b.rusz('H2', 'H5', only_bool=True)
        Traceback (most recent call last):
        ...
        AssertionError: Move is not possible: H2 -> H5; RNBQKBNR/P1P1PPPP/1p6/8/8/4P3/1ppp1ppp/rnbqkbnr KQkq - 0 5
        """

        self.bicie = False
        start_position_int = self.mapdict[pos_from]
        end_position_int = self.mapdict[pos_to]

        if self.is_empty(start_position_int):
            raise ValueError('There is no Piece in that field {}'.format(pos_from))

        assert end_position_int in self.brd[start_position_int].moves(karta, self), \
            f"Move is not possible: {pos_from} -> {pos_to}; {self.fen()}"

        # first check if the move is an enappsant one
        if self.brd[start_position_int].name == 'Pawn' and self.enpass == end_position_int:
            if only_bool:
                return True
            assert self.is_empty(end_position_int)
            self.bicie = True
            if self.brd[start_position_int].color == 'b':
                self.zbite.append(self.brd[end_position_int - 10])
                self.brd[end_position_int - 10] = EMPTY
            else:
                self.zbite.append(self.brd[end_position_int + 10])
                self.brd[end_position_int + 10] = EMPTY
            self._move_piece(pos_from=start_position_int, pos_to=end_position_int)
            self._turn_clock(piece_color=end_position_int, clock=0)
            # clearing enpass after enpass -> problem in pat functiong
            self.enpass = 300
            return True
        # then set enpassant if possible
        if self.brd[start_position_int].name == 'Pawn' and \
            self.brd[start_position_int].mvs_number == 0 and \
                abs(start_position_int - end_position_int) == 20:
            self.enpass = (start_position_int + end_position_int) / 2
        else:
            self.enpass = 300

        # checking for castle
        if (karta.ran != 'K' or karta.kol not in (3, 4)) \
                and self.brd[start_position_int].name == 'King' and abs(end_position_int - start_position_int) == 2:
            if only_bool:
                return True
            # determining rook position
            rook_pos = (end_position_int - 2, end_position_int + 1) if end_position_int < start_position_int else (end_position_int + 1, end_position_int - 1)
            # moving the king
            self._move_piece(pos_from=start_position_int, pos_to=end_position_int)
            # moving the rook
            self._move_piece(pos_from=rook_pos[0], pos_to=rook_pos[1])
            self._turn_clock(piece_color=end_position_int, clock=1)
            return True

        # checking for Queen card and valid Queen move
        if karta.ran == 'Q' and self.brd[start_position_int].name == 'Queen' \
                and self.jaki_typ_zostal(self.brd[start_position_int].color) != {'King', 'Queen'}:
            if end_position_int in self.brd[start_position_int].moves(karta, self):
                if only_bool:
                    return True
                self.swap(start_position_int, end_position_int)
                self.brd[end_position_int].mvs_number += 1
                self._turn_clock(piece_color=end_position_int, clock=1)
                return True
        else:
            # default move
            if end_position_int in self.brd[start_position_int].moves(karta, self):
                if only_bool:
                    return True
                if self.brd[start_position_int].name == 'Pawn':
                    clock_value = 0
                else:
                    clock_value = 1
                if not self.is_empty(end_position_int):
                    self.bicie = True
                    clock_value = 0
                    self.zbite.append(self.brd[end_position_int])
                self._move_piece(pos_from=start_position_int, pos_to=end_position_int)
                self._turn_clock(piece_color=end_position_int, clock=clock_value)
                return True

        raise ValueError('BŁĄD w funkcji rusz! skad {} dokad {} karta {} mvs {}, enpas {}'.format(
            pos_from, pos_to, karta, self.brd[start_position_int].mvs_number, self.enpass))

    def __str__(self):
        print('    {:<2}{:<2}{:<2}{:<2}{:>2}{:>2}{:>2}{:>2}'.format(
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'))
        # print('    -----------------')
        for i in range(len(self.brd)):
            r = int(((i - (i % 10)) / 10) - 1)
            if self.brd[i] == 0:
                continue
            if r % 2 == 1:
                if i % 10 == 1:
                    print('    ', end="")
                if i % 10 != 8 and (i % 10) % 2 == 1:
                    print(colored('{!s:} '.format(
                        self.brd[i]), 'grey', attrs=['reverse']), end='')
                elif i % 10 != 8:
                    print(colored('{!s:} '.format(
                        self.brd[i]), 'white', attrs=['reverse']), end='')
                else:
                    print(colored('{!s:} '.format(self.brd[i]), 'white', attrs=[
                          'reverse']), end=' {}\n'.format(r))
            else:
                if i % 10 == 1:
                    print('    ', end="")
                if i % 10 != 8 and (i % 10) % 2 == 1:
                    print(colored('{!s:} '.format(
                        self.brd[i]), 'white', attrs=['reverse']), end='')
                elif i % 10 != 8:
                    print(colored('{!s:} '.format(
                        self.brd[i]), 'grey', attrs=['reverse']), end='')
                else:
                    print(colored('{!s:} '.format(self.brd[i]), 'grey', attrs=[
                          'reverse']), end=' {}\n'.format(r))

        return ''

    def print_positions(self):
        result_str = ''
        for i, el in enumerate(self.brd):
            if i % 10 == 0:
                result_str += '\n'
            appending = str(i) if el != 0 else '0'
            result_str += ' {} '.format(appending)
        return result_str

    def is_empty(self, i):
        if i not in range(120):
            return False
        return self.brd[i] == EMPTY

    def all_empty(self, random_pawn=False):
        """Return list of empty positions."""
        if random_pawn:
            return [i for i in range(len(self.brd))
                    if self.brd[i] == EMPTY and floor(i / 10) not in (2, 9)]
        return [i for i in range(len(self.brd)) if self.brd[i] == EMPTY]

    def all_taken(self):
        """Return list of positions taken by some Piece."""
        return [i for i in range(len(self.brd)) if self.brd[i] != EMPTY and self.brd[i] != 0]

    def position_bierki(self, naz, kol):
        """Reterurn a list of positions of a specified Piece of a specified color."""
        return [i for i in self.all_taken() if self.brd[i].name == naz and self.brd[i].color == kol]

    def jaki_typ_zostal(self, color):
        taken = self.all_taken()
        return {self.brd[pos].name for pos in taken if self.brd[pos].color == color}

    def get_piece(self, position):
        if type(position) == str:
            return self.brd[self.mapdict[position]]
        return self.brd[position]

    def get_points(self, col):
        """
        Returns a sum of points for pieces of color col

        >>> Board().get_points('b') > 49
        True
        """
        return sum([self.brd[i].val for i in self.all_taken() if self.brd[i].color == col])

    def simulate_move(self, from_, to_, card):
        fenstr = self.fen().split()[0]
        enp = self.fen().split()[2]
        copy = Board(fenrep=fenstr)
        copy.enpass = 300 if enp == '-' else self.mapdict[enp]
        copy.rusz(from_, to_, card)
        return copy

    def swap(self, pos_a, pos_b):
        tym = self.brd[pos_b]
        self.brd[pos_b] = self.brd[pos_a]
        self.brd[pos_a] = tym
        if not self.is_empty(pos_b):
            self.brd[pos_b].position = pos_b
        self.brd[pos_a].position = pos_a
        return

    def czy_szach(self, color):
        # for tests purposes there can be no king..
        if 'King' not in self.jaki_typ_zostal(color):
            return False
        poz_k = self.position_bierki('King', color)
        assert len(poz_k) == 1
        return (True, color) if self.pod_biciem(poz_k[0], color) else False

    def check_castle(self, kol):
        """
        Returns a dictionary with castle metadata

        >>> Board().check_castle('b')
        {'if': 0, 'lng': 0, 'shrt': 0}
        >>> Board().check_castle('c')
        {'if': 0, 'lng': 0, 'shrt': 0}
        >>> b = Board(fenrep='R3K2R/PPPPP3/8/pP6/8/Nnr1qQbB/8/7k KQ')
        >>> b.check_castle('b')
        {'if': 2, 'lng': 23, 'shrt': 27}
        """
        king_pawn = self.position_bierki('King', kol)[0]
        rook_positions = self.position_bierki('Rook', kol)
        castle_dict = {'if': 0, 'lng': 0, 'shrt': 0}
        if any([self.brd[king_pawn].mvs_number > 0,
                len(rook_positions) == 0,
                self.czy_szach(kol) == (True, kol)]):
            return castle_dict
        castle_counter = 0
        for rook_pos in rook_positions:
            if self.brd[rook_pos].mvs_number > 0:
                continue
            if rook_pos < king_pawn:
                in_between_positions = [i for i in range(rook_pos + 1, king_pawn)]
            else:
                in_between_positions = [i for i in range(king_pawn + 1, rook_pos)]
            c = 0
            for pos in in_between_positions:
                if not self.is_empty(pos) or self.pod_biciem(pos, kol):
                    break
                else:
                    c += 1
            if c == len(in_between_positions):
                castle_counter += 1
                if rook_pos < king_pawn:
                    castle_dict['lng'] = rook_pos + 2
                else:
                    castle_dict['shrt'] = rook_pos - 1
        castle_dict['if'] = castle_counter
        return castle_dict

    def fen(self):
        """
        Return a FEN representation of a board.

        >>> Board().fen()
        'RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr KQkq - 0 0'
        """
        res = ''
        for i in range(2, 10):
            start = i * 10 + 1
            end = start + 8
            row = self.brd[start:end]
            res += self.fen_row(row) + '/'
        wc = self.fen_castle('b')
        bc = self.fen_castle('c').lower()
        jc = wc + bc
        c = '-' if jc == '--' else jc
        enp = '-' if self.enpass not in self.mapdict.values() else [k for (
            k, v) in self.mapdict.items() if v == self.enpass][0]
        ret = [res[:-1], c,
               str(enp), str(self.halfmoveclock), str(self.fullmove)]
        return ' '.join(ret)

    def fen_castle(self, kol):
        if 'Rook' not in self.jaki_typ_zostal(kol) or 'King' not in self.jaki_typ_zostal(kol):
            return '-'
        res = ''
        k = self.position_bierki('King', kol)[0]
        w = self.position_bierki('Rook', kol)
        w.sort()
        if self.brd[k].mvs_number > 0:
            return '-'
        # just temporarily
        if len(w) < 2:
            return '-'
        if self.brd[w[1]].mvs_number == 0:
            res += 'K'
        if self.brd[w[0]].mvs_number == 0:
            res += 'Q'
        if len(res) == 0:
            res = '-'
        return res

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
        FEN_DICT = {
            'p': Pawn,
            'r': Rook,
            'n': Knight,
            'k': King,
            'q': Queen,
            'b': Bishop,
        }
        while counter < len(row_str) and pos < i + 9:
            if row_str[counter].isnumeric():
                pos += int(row_str[counter])
            else:
                color = 'b' if row_str[counter].isupper() else 'c'
                piece = FEN_DICT[row_str[counter].lower()]
                pieces_dict[pos] = piece(color, pos)
                pos += 1
            counter += 1
        return pieces_dict

    def get_fen_rep(self, piece):
        letter = 'n' if piece.name == 'Knight' else piece.name[0]
        if piece.color == 'b':
            return letter.upper()
        else:
            return letter.lower()

    def fen_row(self, row):
        res = ''
        empty_counter = 0
        for i in row:
            if i == EMPTY:
                empty_counter += 1
            elif empty_counter == 0:
                res += self.get_fen_rep(i)
            else:
                res += str(empty_counter) + self.get_fen_rep(i)
                empty_counter = 0
        if empty_counter > 0:
            res += str(empty_counter)
        return res

    def pod_biciem(self, pole, color):
        """
        Return True if a position is under attack.

        >>> Board(fenrep='R3K2R/8/8/8/8/8/8/8').pod_biciem(88,'b')
        False
        >>> Board(fenrep='R3K2R/8/8/8/8/8/8/8').pod_biciem(35,'c')
        True
        >>> Board(fenrep='b3K2R/8/8/8/8/8/8/8').pod_biciem(32,'b')
        True
        >>> Board(fenrep='N3K2R/8/8/8/8/8/8/8').pod_biciem(33,'c')
        True
        >>> Board(fenrep='R3K2R/8/8/8/8/8/8/8').pod_biciem(81,'c')
        True
        >>> Board(fenrep='R3K2R/P7/8/8/8/8/8/8').pod_biciem(42,'c')
        True
        """

        def non_sliding_piece_check(position, move_range, piece_type):
            for i in move_range:
                potential_capturing_piece_pos = position + i
                if (type(self.brd[potential_capturing_piece_pos]) == piece_type and
                   self.brd[potential_capturing_piece_pos].color != color):
                    return True
            return False

        def sliding_piece_check(position, move_range, piece_type):
            for i in move_range:
                a = position + i
                while (self.brd[a] != 0):
                    if not self.is_empty(a):
                        if self.brd[a].color != color:
                            if type(self.brd[a]) == piece_type or type(self.brd[a]) == Queen:
                                return True
                            else:
                                break
                        else:
                            break
                    a += i
            return False

        pawn_range = (9, 11) if color == 'b' else (-9, -11)

        for move_range, piece_type in (
            ((1, -1, 10, -10, 9, 11, -9, -11), King),
            ((-12, -21, -19, -8, 8, 19, 21, 12), Knight),
            (pawn_range, Pawn)
        ):
            if non_sliding_piece_check(pole, move_range, piece_type):
                return True

        for move_range, piece_type in (
            ((1, 10, -1, -10), Rook),
            ((9, 11, -11, -9), Bishop),
        ):
            if sliding_piece_check(pole, move_range, piece_type):
                return True

        # for i in (1, -1, 10, -10, 9, 11, -9, -11):
        #     a = pole + i
        #     if (type(self.brd[a]) == King and self.brd[a].color != color):
        #         return True
        #
        # for i in (-12, -21, -19, -8, 8, 19, 21, 12):
        #     a = pole + i
        #     if (type(self.brd[a]) == Knight and self.brd[a].color != color):
        #         return True

        # for i in (1, 10, -1, -10):
        #     a = pole + i
        #     while (self.brd[a] != 0):
        #         if self.is_empty(a) == 0:
        #             if self.brd[a].color != color:
        #                 if type(self.brd[a]) == Rook or type(self.brd[a]) == Queen:
        #                     return True
        #                 else:
        #                     break
        #             else:
        #                 break
        #         a += i
        # for i in (9, 11, -11, -9):
        #     a = pole + i
        #     while (self.brd[a] != 0):
        #         if self.is_empty(a) == 0:
        #             if self.brd[a].color != color:
        #                 if type(self.brd[a]) == Bishop or type(self.brd[a]) == Queen:
        #                     return True
        #                 else:
        #                     break
        #             else:
        #                 break
        #         a += i

        # where = (9, 11) if color == 'b' else (-9, -11)
        # for i in where:
        #     a = pole + i
        #     if (type(self.brd[a]) == Pawn and self.brd[a].color != color):
        #         return True

        return False
