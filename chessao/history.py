from collections import defaultdict
from pprint import pformat
import re
from typing import List, Optional, Tuple

from chessao import WHITE_COLOR, BLACK_COLOR
from chessao.cards import Card
from chessao.chess import Board, FEN_DICT


PATTERN = (fr'(?P<color>{WHITE_COLOR}|{BLACK_COLOR}) (?P<discarded>\[[\d\w♤♡♢♧,\s]+\])?\s?(?P<burn>!?)'
           r'(?P<card>\d{0,2}\w?[♤♡♢♧]);?(?P<jack>\w?)\((?P<pile>\d)\) '
           r'((?P<piece>\w)(?P<start>\w\d):(?P<end>\w\d))?'
           r'(=(?P<promotion>\w))?(?P<check>\+?)(?P<mate>#?)\s?'
           r'(?P<board>[RNBPQKrpnbqk12345678/]{5,}) '
           r'(?P<white_castle>K?Q?)(?P<black_castle>k?q?)-? '
           r'(?P<enpassant>\w\d|-) (?P<halfmove>\d+) (?P<fullmove>\d+)'
           )


class ChessaoHistory:

    def __init__(self, board: Board, ledger=None) -> None:
        self.ledger = ledger or [board.fen()]

    def __len__(self):
        return len(self.ledger)

    def __str__(self):
        return pformat(self.ledger)

    def __repr__(self):
        return str(self)

    def get(self):
        return self.ledger

    def add(self, chessao_game: 'ChessaoGame') -> None:
        color = chessao_game.to_move
        discarded = f"{chessao_game.discarded_cards}" + ' ' if chessao_game.discarded_cards else ''
        burn = '!' if chessao_game.burned else ''
        card = chessao_game.cards.absolute_current
        jack = ';' + chessao_game.jack if chessao_game.jack is not None else ''
        pile = chessao_game.cards.current_pile
        prom = '=' + chessao_game.promotion if chessao_game.promotion else ''
        check = '+' if chessao_game.check else ''
        mate = '#' if chessao_game.mate else ''
        fen = chessao_game.board.fen()
        if not chessao_game.current_move:
            record = (f"{color} {discarded}{burn}{card}"
                      f"{jack}({pile}) {fen}")
        else:
            piece = chessao_game.board.get_fen_rep(chessao_game.board.get_piece(chessao_game.current_move[1]))
            start = chessao_game.current_move[0]
            end = chessao_game.current_move[1]
            record = (f"{color} {discarded}{burn}{card}{jack}({pile}) "
                      f"{piece}{start}:{end}{prom}{check}{mate} {fen}")
        self.ledger.append(record)

    def get_move_from_turn(self, index: int, key: str = None):
        if not 0 < abs(index) < len(self.ledger):
            # TODO: logging
            return defaultdict(lambda: None)
        parsed_move = self.parse_record(self.ledger[index])
        if key:
            return parsed_move[key]
        return parsed_move

    @staticmethod
    def parse_record(record: str) -> dict:
        record_dict = defaultdict(lambda: None)
        pattern = PATTERN

        matched = re.search(pattern, record)
        if matched is None:
            raise ValueError(f"Record not matched: {record}")

        for group in ('color', 'board', 'white_castle', 'black_castle', 'enpassant'):
            record_dict[group] = matched.group(group)

        for group in ('pile', 'halfmove', 'fullmove'):
            record_dict[group] = int(matched.group(group))

        for group in ('jack', 'piece', 'promotion'):
            if matched.group(group):
                record_dict[group] = FEN_DICT[matched.group(group).lower()]

        for group in ('check', 'mate'):
            if matched.group(group):
                record_dict[group] = bool(matched.group(group))

        if matched.group('start') in (None, ''):
            assert matched.group('end') in (None, '')
            record_dict['move'] = []
        else:
            assert matched.group('start') is not None
            record_dict['move'] = [matched.group('start'), matched.group('end')]

        if matched.group('discarded'):
            discarded_list = matched.group('discarded')[1:-1].split(', ')
            record_dict['discarded'] = [*map(Card.from_string, discarded_list)]

        record_dict['burned'] = bool(matched.group('burn'))
        record_dict['card'] = Card.from_string(matched.group('card'))

        return record_dict
