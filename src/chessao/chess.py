
# Board and Pieces classes from Szachao module
# pieces value according to Hans Berliner's system
# (https://en.wikipedia.org/wiki/Chess_piece_relative_value)

import random
# from copy import deepcopy
from math import floor
from termcolor import colored
from chessao.pieces import *
from chessao.cards import Card, Deck


class Board:

    def __init__(self, rnd=False, fenrep=False):
        """
        >>> 'K' in Board(rnd=1).fen()
        True
        """
        self.brd = [0 for i in range(120)]

        for a in range(21, 99 + 1):
            if (a % 10 != 0) and (a % 10 != 9):
                self.brd[a] = ' '

        if not rnd and fenrep == False:
            for i in range(31, 39):
                self.brd[i] = Pawn(color='b', position=i)
            for i in range(81, 89):
                self.brd[i] = Pawn('c', i)
            fun = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
            for i in ([20, 'b'], [90, 'c']):
                for j in range(1, 9):
                    self.brd[i[0] + j] = \
                        fun[(j - 1)](color=i[1], position=(i[0] + j))
        elif fenrep == False:
            for k in ('c', 'b'):
                rand2 = random.choice(self.all_empty())
                self.brd[rand2] = King(k, rand2)
                for (t, s, a) in [(Pawn, 8, True), (Bishop, 2, False), (Knight, 2, False), (Rook, 2, False), (Queen, 1, False)]:
                    rand = random.randint(0, s)
                    for i in range(rand):
                        pos = random.choice(self.all_empty(random_pawn=a))
                        self.brd[pos] = t(k, pos)
        else:
            for (k, v) in self.parse_fen(fenrep).items():
                self.brd[k] = v

        self.mapdict = {l + str(j - 1): 10 * j + 1 + 'ABCDEFGH'.index(l)
                        for j in range(2, 10) for l in 'ABCDEFGH'}
        self.bicie = False
        self.zbite = []
        self.enpass = 300
        self.fullmove = 0
        self.halfmoveclock = 0

    def rusz(self, c, d=None, karta=Card(1, '5'), only_bool=False):
        """
        >>> Board(fenrep='R3K2R/8/8/8/8/8/8/8').rusz('E1','B1')
        True
        >>> Board(fenrep='R3K2R/8/8/pP6/8/NnrRqQbB/8/7k').rusz('E1','G1')
        True
        >>> Board(fenrep='R3K2R/8/8/Q7/8/8/8/8').rusz('A4','A1', Card(1,'Q'))
        True
        >>> Board(fenrep='R3K2R/8/8/P7/8/8/8/8').rusz('A4','A5', Card(1,'Q'))
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
        >>> Board().fen()
        'RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr KQkq - 0 0'
        >>> Board(fenrep='R3K2R/8/8/P7/q7/8/8/8').rusz('A5','A4', Card(1,'6'))
        True
        >>> Board(fenrep='R3K2R/8/8/P7/q7/8/1N6/8').rusz('B7','A5', Card(1,'6'))
        True
        >>> b = Board()
        >>> b.rusz('D2','D4')
        True
        >>> b.rusz('A7','A5')
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
        ValueError: BŁĄD w funkcji rusz! skad H2 dokad H5 karta 5♤ mvs 0, enpas 300
        """
        self.bicie = False
        a = self.mapdict[c]
        if self.is_empty(a):
            raise ValueError
        b = self.mapdict[d]

        # first check if the move is an enappsant one
        if self.brd[a].name == 'Pawn' and self.enpass == b:
            if only_bool:
                return True
            assert self.is_empty(b)
            self.bicie = True
            if self.brd[a].color == 'b':
                self.zbite.append(self.brd[b - 10])
                self.brd[b - 10] = ' '
            else:
                self.zbite.append(self.brd[b + 10])
                self.brd[b + 10] = ' '
            self.brd[b] = self.brd[a]
            self.brd[b].position = b
            self.brd[b].mvs_number += 1
            self.brd[a] = ' '
            self.halfmoveclock = 0
            if self.brd[b].color == 'c':
                self.fullmove += 1
            # clearing enpass after enpass -> problem in pat functiong
            self.enpass = 300
            return True
        # then set enpassant if possible
        if self.brd[a].name == 'Pawn' and self.brd[a].mvs_number == 0 and abs(a - b) == 20:
            self.enpass = (a + b) / 2
        else:
            self.enpass = 300

        # checking for castle
        if (karta.ran != 'K' or karta.kol not in (3, 4)) and self.brd[a].name == 'King' and abs(b - a) == 2:
            if only_bool:
                return True
            # determining rook position
            rook_pos = (b - 1, b + 1) if b < a else (b + 1, b - 1)
            # moving the king
            self.brd[b] = self.brd[a]
            self.brd[b].position = b
            self.brd[b].mvs_number += 1
            self.brd[a] = ' '
            # moving the rook
            self.brd[rook_pos[1]] = self.brd[rook_pos[0]]
            self.brd[rook_pos[1]].position = rook_pos[1]
            self.brd[rook_pos[1]].mvs_number += 1
            self.brd[rook_pos[0]] = ' '
            self.halfmoveclock += 1
            if self.brd[b].color == 'c':
                self.fullmove += 1
            return True

        # checking for Queen card and valid Queen move
        if karta.ran == 'Q' and self.brd[a].name == 'Queen' and self.jaki_typ_zostal(self.brd[a].color) != {'King', 'Queen'}:
            if b in self.brd[a].moves(karta, self):
                if only_bool:
                    return True
                self.swap(a, b)
                self.brd[b].mvs_number += 1
                self.halfmoveclock += 1
                if self.brd[b].color == 'c':
                    self.fullmove += 1
                return True
        else:
            # default move
            if b in self.brd[a].moves(karta, self):
                if only_bool:
                    return True
                if self.brd[a].name == 'Pawn':
                    self.halfmoveclock = 0
                else:
                    self.halfmoveclock += 1
                if self.is_empty(b) == 0:
                    self.bicie = True
                    self.halfmoveclock = 0
                    self.zbite.append(self.brd[b])
                self.brd[b] = self.brd[a]
                self.brd[b].position = b
                self.brd[b].mvs_number += 1
                self.brd[a] = ' '
                if self.brd[b].color == 'c':
                    self.fullmove += 1
                return True

        raise ValueError('BŁĄD w funkcji rusz! skad {} dokad {} karta {} mvs {}, enpas {}'.format(
            c, d, karta, self.brd[a].mvs_number, self.enpass))

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

    def is_empty(self, i):
        return self.brd[i] == ' '

    def all_empty(self, random_pawn=False):
        if random_pawn:
            return [i for i in range(len(self.brd)) if self.brd[i] == ' ' and floor(i / 10) not in (2, 9)]
        return [i for i in range(len(self.brd)) if self.brd[i] == ' ']

    def all_taken(self):
        return [i for i in range(len(self.brd)) if self.brd[i] != ' ' and self.brd[i] != 0]

    def position_bierki(self, naz, kol):
        return [i for i in self.all_taken() if self.brd[i].name == naz and self.brd[i].color == kol]

    def jaki_typ_zostal(self, color):
        a = self.all_taken()
        return {self.brd[i].name for i in a if self.brd[i].color == color}

    def get_piece(self, pos):
        return self.brd[self.mapdict[pos]]

    def get_points(self, col):
        """
        >>> Board().get_points('b') > 49
        True
        """
        return sum([self.brd[i].val for i in self.all_taken() if self.brd[i].color == col])

    def simulate_move(self, fro, to, card):
        fenstr = self.fen().split()[0]
        enp = self.fen().split()[2]
        copy = Board(fenrep=fenstr)
        copy.enpass = 300 if enp == '-' else self.mapdict[enp]
        copy.rusz(fro, to, card)
        return copy

    def swap(self, a, b):
        tym = self.brd[b]
        self.brd[b] = self.brd[a]
        self.brd[a] = tym
        if not self.is_empty(b):
            self.brd[b].position = b
        self.brd[a].position = a

    def czy_szach(self, color):
        # for tests purposes there can be no king..
        if 'King' not in self.jaki_typ_zostal(color):
            return False
        res = []
        poz_k = self.position_bierki('King', color)
        assert len(poz_k) == 1
        return (True, color) if self.pod_biciem(poz_k[0], color) else False

    def check_castle(self, kol):
        k = self.position_bierki('King', kol)[0]
        w = self.position_bierki('Rook', kol)
        d = {'if': 0, 'lng': 0, 'shrt': 0}
        if self.brd[k].mvs_number > 0 or len(w) == 0 or self.czy_szach(kol) == (True, kol):
            return d
        cntr = 0
        for r in w:
            if self.brd[r].mvs_number > 0:
                continue
            if r < k:
                where = [i for i in range(r + 1, k)]
            else:
                where = [i for i in range(k + 1, r)]
            c = 0
            for pos in where:
                if self.is_empty(pos) == 0 or self.pod_biciem(pos, kol):
                    break
                else:
                    c += 1
            if c == len(where):
                cntr += 1
                if r < k:
                    d['lng'] = r + 1
                else:
                    d['shrt'] = r - 1
        d['if'] = cntr
        return d

    def fen(self):
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

    def parse_fen(self, fen):
        # return dictionary (pos:piece)
        rows = fen.split('/')
        res_dict = {}
        for i in range(len(rows)):
            res_dict.update(self.parse_row_fen(rows[i], (i + 2) * 10))
        return res_dict

    def parse_row_fen(self, s, i):
        pos = i + 1
        dic = {}
        y = 0
        while y < len(s) and pos < i + 9:
            if s[y].isnumeric():
                pos += int(s[y])
            elif s[y] == 'P':
                dic[pos] = Pawn('b', pos)
                pos += 1
            elif s[y] == 'R':
                dic[pos] = Rook('b', pos)
                pos += 1
            elif s[y] == 'N':
                dic[pos] = Knight('b', pos)
                pos += 1
            elif s[y] == 'B':
                dic[pos] = Bishop('b', pos)
                pos += 1
            elif s[y] == 'Q':
                dic[pos] = Queen('b', pos)
                pos += 1
            elif s[y] == 'K':
                dic[pos] = King('b', pos)
                pos += 1
            elif s[y] == 'p':
                dic[pos] = Pawn('c', pos)
                pos += 1
            elif s[y] == 'r':
                dic[pos] = Rook('c', pos)
                pos += 1
            elif s[y] == 'n':
                dic[pos] = Knight('c', pos)
                pos += 1
            elif s[y] == 'b':
                dic[pos] = Bishop('c', pos)
                pos += 1
            elif s[y] == 'q':
                dic[pos] = Queen('c', pos)
                pos += 1
            elif s[y] == 'k':
                dic[pos] = King('c', pos)
                pos += 1
            else:
                print('row fen err {} {}'.format(s, i))
                raise ValueError
            y += 1
        return dic

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
            if i == ' ':
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
        for i in (1, -1, 10, -10, 9, 11, -9, -11):
            a = pole + i
            if (type(self.brd[a]) == King and self.brd[a].color != color):
                return True

        for i in (-12, -21, -19, -8, 8, 19, 21, 12):
            a = pole + i
            if (type(self.brd[a]) == Knight and self.brd[a].color != color):
                return True
        for i in (1, 10, -1, -10):
            a = pole + i
            while (self.brd[a] != 0):
                if self.is_empty(a) == 0:
                    if self.brd[a].color != color:
                        if type(self.brd[a]) == Rook or type(self.brd[a]) == Queen:
                            return True
                        else:
                            break
                    else:
                        break
                a += i
        for i in (9, 11, -11, -9):
            a = pole + i
            while (self.brd[a] != 0):
                if self.is_empty(a) == 0:
                    if self.brd[a].color != color:
                        if type(self.brd[a]) == Bishop or type(self.brd[a]) == Queen:
                            return True
                        else:
                            break
                    else:
                        break
                a += i

        where = (9, 11) if color == 'b' else (-9, -11)
        for i in where:
            a = pole + i
            if (type(self.brd[a]) == Pawn and self.brd[a].color != color):
                return True

        return False
