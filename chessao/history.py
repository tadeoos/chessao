import json
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, InitVar, field, asdict
from pprint import pformat
from typing import List, TYPE_CHECKING

from chessao import WHITE_COLOR, BLACK_COLOR
from chessao.cards import Card
from chessao.chess import Board
from chessao.utils import GameplayEncoder

if TYPE_CHECKING:
    from chessao.gameplay import ChessaoGame


PATTERN = (fr'(?P<color>{WHITE_COLOR}|{BLACK_COLOR}) (?P<discarded>\[[\d\w♤♡♢♧,\s]+\])?\s?(?P<burn>!?)'
           r'(?P<card>\d{0,2}\w?[♤♡♢♧]);?(?P<jack>\w?)\((?P<pile>\d)\) '
           r'((?P<piece>\w)(?P<start>\w\d):(?P<end>\w\d))?'
           r'(=(?P<promotion>\w))?(?P<check>\+?)(?P<mate>#?)\s?'
           r'(?P<board>[RNBPQKrpnbqk12345678/]{5,}) '
           r'(?P<white_castle>K?Q?)(?P<black_castle>k?q?)-? '
           r'(?P<enpassant>\w\d|-) (?P<halfmove>\d+) (?P<fullmove>\d+)'
           )


@dataclass
class MoveRecord:
    chessao: InitVar["ChessaoGame"]
    color: str = field(init=False)
    discarded: List[Card] = field(init=False)
    burned: bool = field(init=False)
    card: Card = field(init=False)
    jack: str = field(init=False)
    pile: int = field(init=False)
    promotion: str = field(init=False)
    check: bool = field(init=False)
    mate: bool = field(init=False)
    fen: str = field(init=False)
    move: List[str] = field(init=False)
    piece: str = field(init=False)
    white_hand: List[Card] = field(init=False)
    black_hand: List[Card] = field(init=False)

    def __post_init__(self, chessao):
        self.color = chessao.to_move
        self.discarded = chessao.discarded_cards
        self.burned = chessao.burned
        self.card = chessao.cards.absolute_current
        self.jack = chessao.jack
        self.pile = chessao.cards.current_pile
        self.promotion = chessao.promotion
        self.check = chessao.check
        self.mate = chessao.mate
        self.fen = chessao.board.fen()
        self.white_hand = deepcopy(chessao.get_white().hand)
        self.black_hand = deepcopy(chessao.get_black().hand)

        if chessao.current_move:
            self.piece = chessao.board.get_fen_rep(chessao.board.get_piece(chessao.current_move[1]))
            self.move = chessao.current_move
        else:
            self.piece = ''
            self.move = []

    def to_json(self):
        return json.loads(json.dumps(asdict(self), cls=GameplayEncoder))

    def __str__(self):
        color = self.color
        discarded = f"{self.discarded}" + ' ' if self.discarded else ''
        burn = '!' if self.burned else ''
        card = self.card
        jack = ';' + self.jack if self.jack is not None else ''
        pile = self.pile
        prom = '=' + self.promotion if self.promotion else ''
        check = '+' if self.check else ''
        mate = '#' if self.mate else ''
        fen = self.fen

        if not self.move:
            return f"{color} {discarded}{burn}{card}{jack}({pile}) {fen}"

        piece = self.piece
        start = self.move[0]
        end = self.move[1]

        return f"{color} {discarded}{burn}{card}{jack}({pile}) {piece}{start}:{end}{prom}{check}{mate} {fen}"


class ChessaoHistory:

    def __init__(self, board: Board, ledger=None) -> None:
        self.ledger: List[MoveRecord] = ledger or [board.fen()]
        self.starting_position = board.fen()

    def __len__(self):
        return len(self.ledger)

    def __str__(self):
        return pformat(self.ledger)

    def __repr__(self):
        return str(self)

    def get(self):
        return self.ledger

    def add(self, chessao_game) -> None:
        record = MoveRecord(chessao_game)
        self.ledger.append(record)

    def get_move_from_turn(self, index: int) -> dict:
        if not 0 < abs(index) < len(self.ledger):
            # TODO: logging
            return defaultdict(lambda: None)
        parsed_move = self.ledger[index]
        return asdict(parsed_move)

    # @staticmethod
    # def parse_record(record: MoveRecord) -> dict:
    #     record_dict = defaultdict(lambda: None)
    #     pattern = PATTERN
    #
    #     matched = re.search(pattern, record)
    #     if matched is None:
    #         raise ValueError(f"Record not matched: {record}")
    #
    #     for group in ('color', 'board', 'white_castle', 'black_castle', 'enpassant'):
    #         record_dict[group] = matched.group(group)
    #
    #     for group in ('pile', 'halfmove', 'fullmove'):
    #         record_dict[group] = int(matched.group(group))
    #
    #     for group in ('jack', 'piece', 'promotion'):
    #         if matched.group(group):
    #             record_dict[group] = FEN_DICT[matched.group(group).lower()]
    #
    #     for group in ('check', 'mate'):
    #         if matched.group(group):
    #             record_dict[group] = bool(matched.group(group))
    #         else:
    #             record_dict[group] = False
    #
    #     if matched.group('start') in (None, ''):
    #         assert matched.group('end') in (None, '')
    #         record_dict['move'] = []
    #     else:
    #         assert matched.group('start') is not None
    #         record_dict['move'] = [matched.group('start'), matched.group('end')]
    #
    #     if matched.group('discarded'):
    #         discarded_list = matched.group('discarded')[1:-1].split(', ')
    #         record_dict['discarded'] = [*map(Card.from_string, discarded_list)]
    #
    #     record_dict['burned'] = bool(matched.group('burn'))
    #     record_dict['card'] = Card.from_string(matched.group('card'))
    #
    #     return record_dict

    def get_fens(self):
        return [
            rec.fen for rec in self.ledger if isinstance(rec, MoveRecord)
        ]
