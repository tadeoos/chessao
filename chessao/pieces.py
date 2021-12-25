"""Chess pieces implementation."""

from copy import deepcopy
from chessao import PIECES_STR, BLACK_COLOR, WHITE_COLOR


class ChessaoPieceException(Exception):
    pass


class Piece:
    """A chess piece abstract class."""

    def __init__(self, color, position, name, val, mvs=0):
        self.color = color
        self.mvs_number = mvs
        self.history = []
        self.name = name
        self._position = position
        self.val = val

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @position.deleter
    def position(self):
        del self._position

    def _moves(self, card, board):
        raise NotImplementedError

    def _move_results_with_check(self, move, board):
        end_piece = board[move]
        board[self.position] = " "
        board[move] = self
        check = board.color_is_checked(self.color)
        board[self.position] = self
        board[move] = end_piece
        return check

    def moves(self, card, board):
        # TODO: write tests for pieces moves
        """
        Return a list of positions that a piece can move onto, on
        a specific card & board.
        """
        if board.get_piece(self.position) != self:
            raise ChessaoPieceException(
                f'Piece is not on the board. Pos={self.position} Board=\n{board}')

        moves = [move for move in self._moves(card, board)
                 if not self._move_results_with_check(move, board)]

        return moves

    @classmethod
    def under_attack(cls, position_int, color, board):
        "Return True if position is under attack by a Piece of this class."
        raise NotImplementedError

    def __str__(self):
        return PIECES_STR[self.color][self.name]

    # def __repr__(self):
        # return "{} {} at {}".format(self.color, self.name, self.position)

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    def to_json(self):
        return self.__dict__


class SlidingPiece(Piece):

    def __init__(self, color, position, name="Pawn", val=1, mvs=0):
        super(SlidingPiece, self).__init__(color, position, name, val, mvs)
        self.range = None

    def _moves(self, card, board):
        return self.sliding_move(card, board, self.range, self.position, self.color)

    @staticmethod
    def sliding_move(card, board, range_, position, color):
        available_positions = []
        for i in range_:
            potential_position = position + i
            while (board[potential_position] != 0):
                if board.is_empty(potential_position):
                    available_positions.append(potential_position)
                elif board[potential_position].color != color:
                    available_positions.append(potential_position)
                    break
                else:
                    break
                potential_position += i

        return available_positions


class Pawn(Piece):

    def __init__(self, color, position, name="Pawn", val=1, mvs=0):
        super(Pawn, self).__init__(color, position, name, val, mvs)

    def move_helper(self, list_of_positions, board, direction=1):
        updated_positions = list_of_positions
        for pos in list_of_positions[::-1]:
            if not board.is_empty(self.position + (direction * pos)):
                ind = list_of_positions.index(pos)
                updated_positions = list_of_positions[:ind]

        capture_positions = (direction * 9, direction * 11)
        return updated_positions, capture_positions

    def _moves(self, card, board, direction=1):
        dop = [10, 20] if self.mvs_number == 0 else [10]
        if card.rank == '2':
            dop.append(dop[-1] + 10)
        if self.color == BLACK_COLOR:
            direction = -1
            dop, a = self.move_helper(dop, board, direction=direction)
        else:
            dop, a = self.move_helper(dop, board)

        for i in a:
            possible_position = self.position + i
            if (not board.is_empty(possible_position) and
                board[possible_position] != 0 and
                board[possible_position].color != self.color) or \
                    (board.enpass == possible_position):
                dop.append(abs(i))

        res = [self.position + direction * i for i in dop]

        return res


class Rook(SlidingPiece):

    def __init__(self, color, position, name='Rook', val=5.1, mvs=0):
        super(Rook, self).__init__(color, position, name, val, mvs)
        self.range = (1, 10, -1, -10)


class Bishop(SlidingPiece):

    def __init__(self, color, position, name='Bishop', val=3, mvs=0):
        super(Bishop, self).__init__(color, position, name, val, mvs)
        self.range = (9, 11, -11, -9)

    @property
    def piece_color(self):
        pos_str = str(self.position)
        tenths = int(pos_str[0])
        units = int(pos_str[1])
        if tenths % 2 == 0:
            if units % 2 == 1:
                return BLACK_COLOR
        elif units % 2 == 0:
            return BLACK_COLOR
        return WHITE_COLOR


class Knight(Piece):

    def __init__(self, color, position, name='Knight', val=3.2, mvs=0):
        super(Knight, self).__init__(color, position, name, val, mvs)

    def _moves(self, card, board):
        res = []
        for i in (-12, -21, -19, -8, 8, 19, 21, 12):
            a = self.position + i
            if board[a] != 0:
                if board.is_empty(a) or board[a].color != self.color:
                    res.append(a)

        return res


class Queen(Piece):

    def __init__(self, color, position, name='Queen', val=8.8, mvs=0):
        super(Queen, self).__init__(color, position, name, val, mvs)

    def _moves(self, card, board):
        pieces_left = board.piece_types_left(self.color)
        if card.rank == 'Q' and pieces_left != {King, Queen}:
            assert Queen in pieces_left
            res = [i for i in board.all_taken() if
                   (board[i].color == self.color and
                    board[i].name in ('Pawn', 'Bishop', 'Knight', 'Rook'))]
            return res

        range_ = (9, 11, -11, -9, 1, -1, 10, -10)
        return SlidingPiece.sliding_move(card, board, range_, self.position, self.color)


class King(Piece):

    def __init__(self, color, position, name='King', val=10, mvs=0):
        super(King, self).__init__(color, position, name, val, mvs)

    def _move_results_with_check(self, move, board):
        return False

    def _moves(self, card, board):
        res = []
        if card.rank == 'K' and card.color in (3, 4):
            zakres = [1, -1, 10, -10, 9, 11, -9, -11,
                      2, -2, 20, -20, 18, 22, -18, -22]
        else:
            zakres = [1, -1, 10, -10, 9, 11, -9, -11]
        discared_ranges = set()
        for i in zakres:
            if i in discared_ranges:
                continue
            a = self.position + i
            if a > 20 and a < 99 and board[a] != 0:
                if board.is_empty(a):
                    res.append(a)
                elif board[a].color != self.color:
                    b = 2 * i
                    if b in zakres:
                        discared_ranges.add(b)
                    res.append(a)
                else:
                    # board is not empty with the same color piece
                    if (2 * i) in zakres:
                        discared_ranges.add(2 * i)
                    continue

        # cannot move to a position under check
        board[self.position] = ' '
        for r in deepcopy(res):
            if board.under_attack(r, self.color):
                res.remove(r)
        board[self.position] = self

        # checking for castle / cannot castle on a special king card
        cstl = board.check_castle(self.color)
        if cstl['possible_castles'] > 0 and (card.rank != 'K' or card.color not in (3, 4)):
            res.extend([i for i in cstl.values() if i > 10])

        return res

    @classmethod
    def under_attack(cls, position_int, color, board):
        for i in (1, -1, 10, -10, 9, 11, -9, -11):
            a = position_int + i
            if type(board[a]) == cls and board[a].color != color:
                return True