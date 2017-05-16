from copy import deepcopy

#######
######## SZACHY  ########


class Piece():
    '''A chess piece abstract class.'''

    def __init__(self, color, position, name, val, mvs=0):
        self.color = color
        self.position = position
        self.mvs_number = mvs
        self.history = []
        self.name = name
        self.val = val

    def moves(self, card, board):
        '''Return a list of positions that a piece can move onto, on a specific card & board'''
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class Pawn(Piece):

    def __init__(self, color, position, name="Pawn", val=1, mvs=0):
        super(Pawn, self).__init__(color, position, name, val, mvs)

    def moves(self, card, board):
        dop = [10, 20] if self.mvs_number == 0 else [10]
        if card.ran == '2':
            dop.append(dop[-1] + 10)
        if self.color == 'b':
            for d in dop[::-1]:
                if self.position + d > 119:
                    continue
                if board.is_empty(self.position + d) == 0:
                    ind = dop.index(d)
                    dop = dop[:ind]
            a = (9, 11)
        else:
            for d in dop[::-1]:
                if self.position - d < 0:
                    continue
                if board.is_empty(self.position - d) == 0:
                    ind = dop.index(d)
                    dop = dop[:ind]
            a = (-9, -11)

        for i in a:
            if (board.brd[self.position + i] != 0 and board.brd[self.position + i] != ' ' and board.brd[self.position + i].color != self.color) or (board.enpass == self.position + i):
                dop.append(abs(i))

        res = [self.position + i if self.color ==
               'b' else self.position - i for i in dop]

        return res

    def __str__(self):
        if self.color == 'b':
            return '♙'
        else:
            return '♟'


class Rook(Piece):

    def __init__(self, color, position, name='Rook', val=5.1, mvs=0):
        super(Rook, self).__init__(color,
                                   position, name, val, mvs)

    def moves(self, card, board):
        res = []
        for i in (1, 10, -1, -10):
            a = self.position + i
            while (board.brd[a] != 0):
                if board.is_empty(a) == 0:
                    if board.brd[a].color != self.color:
                        res.append(a)
                        break
                    else:
                        break
                res.append(a)
                a += i

        return res

    def __str__(self):
        if self.color == 'b':
            return '♖'
        else:
            return '♜'


class Knight(Piece):

    def __init__(self, color, position, name='Knight', val=3.2, mvs=0):
        super(Knight, self).__init__(color,
                                     position, name, val, mvs)

    def moves(self, card, board):
        res = []
        for i in (-12, -21, -19, -8, 8, 19, 21, 12):
            a = self.position + i
            if board.brd[a] != 0:
                if board.is_empty(a) == 1 or board.brd[a].color != self.color:
                    res.append(a)

        return res

    def __str__(self):
        if self.color == 'b':
            return '♘'
        else:
            return '♞'


class Bishop(Piece):

    def __init__(self, color, position, name='Bishop', val=3, mvs=0):
        super(Bishop, self).__init__(color,
                                     position, name, val, mvs)

    def moves(self, card, board):
        res = []
        for i in (9, 11, -11, -9):
            a = self.position + i
            while (board.brd[a] != 0):
                if board.is_empty(a) == 0:
                    if board.brd[a].color != self.color:
                        res.append(a)
                        break
                    else:
                        break
                res.append(a)
                a += i

        return res

    def __str__(self):
        if self.color == 'b':
            return '♗'
        else:
            return '♝'


class Queen(Piece):

    def __init__(self, color, position, name='Queen', val=8.8, mvs=0):
        super(Queen, self).__init__(color,
                                    position, name, val, mvs)

    def moves(self, card, board):
        if card.ran == 'Q' and board.jaki_typ_zostal(self.color) != {'King', 'Queen'}:
            res = [i for i in board.all_taken() if (board.brd[i].color == self.color and board.brd[
                i].name in ('Pawn', 'Bishop', 'Knight', 'Rook'))]
            return res

        res = []
        for i in (9, 11, -11, -9, 1, -1, 10, -10):
            a = self.position + i
            while (board.brd[a] != 0):
                if board.is_empty(a) == 0:
                    if board.brd[a].color != self.color:
                        res.append(a)
                        break
                    else:
                        break
                res.append(a)
                a += i
        return res

    def __str__(self):
        if self.color == 'b':
            return '♕'
        else:
            return '♛'


class King(Piece):

    def __init__(self, color, position, name='King', val=10, mvs=0):
        super(King, self).__init__(color,
                                   position, name, val, mvs)

    def moves(self, card, board):
        res = []
        if card.ran == 'K' and card.kol in (3, 4):
            zakres = [1, -1, 10, -10, 9, 11, -9, -
                      11, 2, -2, 20, -20, 18, 22, -18, -22]
        else:
            zakres = [1, -1, 10, -10, 9, 11, -9, -11]
        for i in zakres:
            # print(self.position)
            # print(i)
            a = self.position + i
            if a > 20 and a < 99 and board.brd[a] != 0:
                if board.is_empty(a):
                    res.append(a)
                    continue
                elif board.brd[a].color != self.color:
                    b = 2 * i
                    if b in zakres:
                        zakres.remove(b)
                    res.append(a)
                else:
                    continue

        # cannot move to a position under check
        res2 = deepcopy(res)
        board.brd[self.position] = ' '
        for r in res2:
            if board.pod_biciem(r, self.color):
                res.remove(r)
        board.brd[self.position] = self

        # checking for castle / cannot castle on a special king card
        cstl = board.check_castle(self.color)
        if cstl['if'] > 0 and (card.ran != 'K' or card.kol not in (3, 4)):
            res.extend([i for i in cstl.values() if i > 10])

        return res

    def __str__(self):
        if self.color == 'b':
            return '♔'
        else:
            return '♚'
