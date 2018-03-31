from copy import deepcopy
import json
import os
import re
import sys
import time

from chessao import WHITE_COLOR
from chessao.cards import Card, Deck
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
from chessao.utils import get_gameplay_defaults


class GameplayEncoder(json.JSONEncoder):
    """A JSON encoder class for Gameplay object."""

    def default(self, obj):
        if isinstance(obj, Card):
            return '{} {}'.format(obj.ran, obj.kol)
        if isinstance(obj, Deck):
            return obj.cards
        if isinstance(obj, Board):
            return obj.fen()
        if isinstance(obj, Player):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


def resurect(history, gameplay=None):
    """Create a Gameplay object from a history."""

    if not gameplay:
        defaults = get_gameplay_defaults(board=Board(fenrep=history[0]))
        result_gameplay = ChessaoGame(**defaults)
    else:
        result_gameplay = gameplay

    try:
        moving_color, str_card, where = history[1].split()
    except ValueError:
        moving_color, str_card = history[1].split()
        where = []

    card = decode_card(str_card)
    where = where[1:6].split(':') if where else where
    promotion = where[-1] if '=' in where else None
    try:
        result_gameplay.make_an_overriden_move_in_one_func(card=card,
                                                           move=where,
                                                           promotion=promotion)
    except Exception as e:
        info = sys.exc_info()[0]
        raise ChessaoGameplayError(
            'RESSURECT move function error\nSNAPSHOT:{}\n{}'.format(
                result_gameplay.snapshot(), info),
            gameplay=result_gameplay,
            errors=e)

    if len(history) == 2:  # end recursion
        return result_gameplay
    return resurect(history[1:], result_gameplay)


class ChessaoGame:
    """A gameplay class."""

    def __init__(self, board=None, cards_dict=None,
                 players=None, default_setup=False):

        if default_setup:
            defaults = get_gameplay_defaults()
            board = defaults['board']
            players = defaults['players']
            cards_dict = defaults['cards_dict']
        else:
            assert all([board, cards_dict, players]), 'Wrong arguments'

        players[0].reka = cards_dict['hand_one']
        players[1].reka = cards_dict['hand_two']

        self.plansza = board
        self.gracze = players
        self.karty = cards_dict['deck']
        self.kupki = cards_dict['piles']
        self.szach = False
        self.mat = False
        self.pat = False
        self.spalone = []
        self.historia = [self.plansza.fen()]
        self.zamiana = False
        self.to_move = WHITE_COLOR
        self.burned = False
        self.now_card = None
        self.now_move = None
        self.jack = None
        self.three = 0
        self.capture = True

    def __str__(self):
        blacks = self.get_gracz('b')
        whites = self.get_gracz('c')
        print('\nKupki: |{0:>3} |  |{1:>3} |'.format(
            str(self.kupki[0][-1]), str(self.kupki[1][-1])))
        print('\nKARTA:  {}{}'.format('!' if self.burned else '', self.now_card))
        print('\n{} {} (white): {}\n'.format(
            blacks.name, blacks.nr, blacks.reka))
        print('{}'.format(self.plansza))
        print('{} {} (black): {}'.format(whites.name, whites.nr, whites.reka))
        print('\nHistory: \n{}'.format(self.historia))
        return ''

    def get_user_cards(self, color, first=True):
        player = self.get_gracz(color)
        if first:
            return player.reka[0]
        else:
            return player.reka

    def snapshot(self, remove=None):
        """Return a JSON representation of a current state.

        Args:
            remove (iterable): attributes to remove from snapshot
        """
        snap = self.__dict__
        if remove:
            for key in remove:
                del snap[key]
        try:
            json_dumps = json.dumps(self.__dict__, cls=GameplayEncoder,
                                    sort_keys=True, indent=2)
        except TypeError as e:
            raise ChessaoGameplayError('Error in `snapshot`', gameplay=self, errors=e)
        return json_dumps

    def do_card_buisness(self, played_cards, three=False):
        player = self.get_gracz(self.to_move)

        player.reka = odejmij(player.reka, played_cards)

        if self.burned:
            if not three:
                assert len(played_cards) == 1
            self.spalone.extend(played_cards)
        else:
            if self.szach:
                assert played_cards[-1].ran != 'A', "Ace was played during check"
            self.kupki[ktora_kupka(played_cards, self.kupki, player.bot)].extend(played_cards)

        if len(self.karty.cards) < len(played_cards):
            self.przetasuj()
        tas = self.karty.deal(len(played_cards))
        player.reka.extend(tas)

        assert len(player.reka) == 5, 'Invalid amout of cards in players hand'

    def graj(self, video=False):
        """play a game untill there is stalemate or checkmate."""
        while not self.mat and not self.pat:
            if video:
                os.system('clear')
            self.get_card()
            self.now_move = self.get_move()
            self.move(self.now_card, self.now_move)
            if video:
                print('{}'.format(self))
                time.sleep(1)

        if video:
            os.system('clear')
            print('\n\n    {}    \n'.format('MAT !' if self.mat else 'PAT !'))
            print(self)

        mate_msg = '\n=== WYGRAŁ {}'.format(
            self.get_gracz(invert_color(self.to_move)))
        stale_msg = '\n=== PAT'
        print(mate_msg or stale_msg)
        return True

    def make_an_overriden_move_in_one_func(self, card, move, **kwargs):
        """
        args:
            card is a tuple: (if_burned, [Cards])
            move is a two items long list of moves: ['A2', 'A3']
        """
        self.get_card(ovr=card)
        self.now_move = self.get_move(ovr=move)
        self.move(self.now_card, self.now_move, **kwargs)
        return self

    def get_card(self, ovr=None):
        """First stage of a move: getting a card from a player."""

        # clearing self.capture
        self.capture = True

        player = self.get_gracz(self.to_move)

        w = self.what_happened()

        # if king of spades was played get card from history (2 halfmoves ago)
        if w[0] == 2:
            self.cofnij(self.to_move, w[1])
            card = w[2]
        else:
            if ovr is not None:
                card = ovr
                assert self.card_ok_to_play(card), "Invalid card: {}".format(card)
            else:
                card = player.choose_card(self.kupki, self.plansza)
                while(not self.card_ok_to_play(card)):
                    card = player.choose_card(self.kupki, self.plansza)

        self.burned = card[0]

        # checking for three
        if self.three > 0 and (card[1][0].ran != '3' or self.burned):
            # if you don't defend yourself on three you have to burn the card
            # (makes three more powerful)
            self.burned = 1
            tmpcar = player.get_three(3) if self.three == 3 else player.get_three(5)
            self.do_card_buisness(tmpcar, three=True)
            self.three = 0
        elif w[0] != 2:
            self.do_card_buisness(card[1])

        # now_card birth
        self.now_card = card[1][0]

        if len(card) == 3:
            self.jack = card[2]
            assert self.jack in self.plansza.jaki_typ_zostal(
                invert_color(self.to_move)), "Invalid piece requested on Jack"
        else:
            self.jack = None

        if self.now_card.ran == '4' and not self.burned:
            self.capture = False

        if self.now_card.ran == '3' and not self.burned:
            add = sum([3 for c in card[1] if c.ran == '3'])
            assert add > 2  # sanity check
            self.three += add

    def get_move(self, ovr=None):
        """Second stage of a move: get a chess move."""
        self.zamiana = False
        player = self.get_gracz(self.to_move)
        # after ace or king of spikes there is no move
        if not self.burned and (self.now_card.ran == 'A' or (self.now_card.ran == 'K' and self.now_card.kol == 1)):
            return []

        w = self.what_happened()
        all_moves = self.possible_moves(
            self.to_move, self.capture, self.now_card, self.burned, w)
        if len(all_moves) == 0:
            return []
        crd = self.now_card if not self.burned else Card(1, '5')
        move = player.choose_move(
            all_moves, self.plansza, crd) if ovr is None else ovr
        return move

    def move(self, card, where, promotion=None):
        """Make an actual move."""
        player = self.get_gracz(self.to_move)
        # passing a move
        if where == []:
            # changing the color to move
            self.to_move = invert_color(self.to_move)
            # udapting check and mate although i think it shoudln't change
            self.szach = self.czy_szach(self.to_move)
            if self.szach and self.czy_pat(self.to_move):
                self.szach = False
                self.mat = True
            elif self.czy_pat(self.to_move):
                self.pat = True

            # udpating history
            record = '{color} {car} '.format(
                color=invert_color(self.to_move), car=card)
            self.historia.append(record)

            # checking for Ace, and switching color
            if self.now_card.ran == 'A' and not self.burned:
                self.to_move = invert_color(self.to_move)
                for g in self.gracze:
                    g.kol = invert_color(g.kol)

            return None

        # actual move happens
        try:
            if self.burned:
                self.plansza.rusz(where[0], where[1])
            else:
                self.plansza.rusz(where[0], where[1], card)
        except Exception as e:
            raise ChessaoGameplayError(
                'self.plansza.rusz error:\nwhere: {} card: {}\nSNAPSHOT: {}'.format(
                    where, card, self.snapshot()),
                gameplay=self, errors=e)

        # checking if pawn is getting promoted
        zam = czy_pion_na_koncu(self.plansza, self.to_move)
        if zam > 0:
            self.zamiana = True
            self.plansza.zbite.append(self.plansza.brd[zam])
            q = player.choose_prom() if not promotion else promotion
            if q == 'E':
                return 'exit'
            elif q == 'D':
                self.plansza.brd[zam] = Queen(self.to_move, zam)
            elif q == 'G':
                self.plansza.brd[zam] = Bishop(self.to_move, zam)
            elif q == 'S':
                self.plansza.brd[zam] = Knight(self.to_move, zam)
            elif q == 'W':
                self.plansza.brd[zam] = Rook(self.to_move, zam)
            else:
                raise ChessaoGameplayError('Wrong promotion input')

        # after my move I must not be checked
        assert not self.czy_szach(self.to_move)

        # changing the color to move
        self.to_move = invert_color(self.to_move)

        # udapting check and mate
        self.szach = self.czy_szach(self.to_move)

        if self.szach and self.czy_pat(self.to_move):
            self.szach = False
            self.mat = True
        elif self.czy_pat(self.to_move):
            self.pat = True
        # updating history
        record = '{color} {burn}{car}{jack} {piece}{fro}:{to}{prom}{check}{mate} {fenrep}'.format(
            color=invert_color(self.to_move),
            burn='!' if self.burned else '',
            car=card,
            jack=';' + self.jack[0] if self.jack is not None else '',
            piece=self.plansza.get_fen_rep(self.plansza.get_piece(where[1])),
            fro=where[0],
            to=where[1],
            prom='=' + q if self.zamiana else '',
            check='+' if self.szach else '',
            mate='#' if self.mat else '',
            fenrep=self.plansza.fen()
        )
        self.historia.append(record)
        return True

    def czy_szach(self, color):
        """Return True if color is checked."""
        if self.plansza.czy_szach(color) == (True, color):
            return True
        return False

    def czy_pat(self, color):
        """Return True if there is a stalemate."""
        if self.plansza.halfmoveclock == 100 or \
                len(self.plansza.all_taken()) == 2:
            return True
        szach = self.czy_szach(color)
        for card in self.get_gracz(color).reka:
            if ok_karta([card], self.kupki):
                # exclude the Queen because it can be played anytime,
                # but it can't help you during check
                if szach and card.ran == 'Q':
                    continue
                if self.possible_moves(color, True, card):
                    return False
            elif self.possible_moves(color):
                    return False
        return True

    def get_gracz(self, color):
        """Return a player who has pieces of color `color`."""
        return [player for player in self.gracze if player.kol == color][0]

    def cofnij(self, color, ruch):
        """Reverese the move."""
        # sanity check
        assert len(self.historia) > 2, "There is no move to reverse"

        move_start = self.plansza.mapdict[ruch[0]]
        move_dest = self.plansza.mapdict[ruch[1]]

        # clearing enpassant and subtracting move counter
        self.plansza.enpass = 300

        # see if a promotion had been made
        if '=' in self.historia[-2]:
            # if gambit Teleżyńskiego occured...
            if 'q' in self.historia[-2].split()[2].lower():
                self.plansza.brd[move_start] = self.plansza.zbite.pop()
            else:
                self.plansza.brd[move_dest] = self.plansza.zbite.pop()

        self.plansza.brd[move_dest].mvs_number -= 1

        if self.plansza.bicie:
            assert self.plansza.is_empty(move_start)
            rezurekt = self.plansza.zbite.pop()
            self.plansza.brd[move_start] = rezurekt
            self.plansza.swap(move_start, move_dest)
        else:
            self.plansza.swap(move_start, move_dest)

        # sanity check
        assert not self.plansza.is_empty(move_start) or not self.plansza.is_empty(move_dest)

    def przetasuj(self):
        """Reshuffle the deck."""
        kup_1 = self.kupki[0][-1]
        kup_2 = self.kupki[1][-1]
        do_tasu = self.kupki[0][:-1] + self.kupki[1][:-1] + self.spalone

        out = Deck(do_tasu)

        self.spalone = []
        out.tasuj()
        out.combine(self.karty.cards)
        self.karty = out
        self.kupki = ([kup_1], [kup_2])
        assert self.get_cards_quantity() == 104, "Wrong cards quantity after reshuffle"

    def get_cards_quantity(self):
        all_cards = sum(map(
            len,
            [self.karty.cards,
             self.kupki[0],
             self.kupki[1],
             self.spalone,
             self.gracze[0].reka,
             self.gracze[1].reka])
        )
        return all_cards

    def what_happened(self):
        """
        Parse history to make sense of the situation.
        Returns int which codes a situation.

        0 -> nothing special
        1 -> turn loosing
        2 -> king of spades
        3 -> king of hearts
        4 -> jack
        """
        s = self.historia[-1]
        s2 = self.historia[-2] if len(self.historia) > 1 else ''
        ind = s2.index(':') if ':' in s2 else None
        what = s[2]
        # if the card was burned or there is a check, last card doesn't matter
        if what == '!' or self.szach or len(self.historia) == 1:
            return (0,)
        elif what == '4' and self.now_card.ran != '4':
            return (1,)
        elif what == 'K' and s[3] == '♤' and ind is not None:
            # r = re.search('\s(.+)\s',s2)
            c = self.from_history_get_card(2)
            return (2, [s2[:ind][-2:], s2[ind + 1:][:2]], c)
        elif what == 'K' and s[3] == '♡' and ind is not None:
            if self.plansza.get_piece(s2[ind + 1:][:2]).color != self.to_move:
                return (1,)
            return (3, s2[ind + 1:][:2])
        elif what == 'J' and self.now_card.ran != 'J':
            if self.jack not in self.plansza.jaki_typ_zostal(self.to_move):
                return (1,)
            return (4, self.jack)
        else:
            return (0,)

    def from_history_get_card(self, number_of_turns):
        """
        # returns a card played number_of_turns turns AGO
        """
        if number_of_turns > len(self.historia):
            return None
        history_string = self.historia[-number_of_turns]
        card = re.search('\s(.+?)\s', history_string).group(1)
        return decode_card(card)

    def card_ok_to_play(self, card):
        """
        args:
            card (tuple => (bool, [cards]))
        """
        burned = card[0]
        top_card = card[1][0]

        if burned:
            return True

        # conditions that if met block the card
        card_should_not_be_played = self.szach and top_card.ran in ('A', 'Q')

        if card_should_not_be_played:
            return False
        return True

    def possible_moves(self, color, okzbi=True, kar=Card(1, '5'), burned=False, flag=(0,)):
        """
        Return a dict of possible moves.
        """
        if burned:
            kar = Card(1, '5')

        d = {v: k for (k, v) in self.plansza.mapdict.items()}

        if flag[0] == 1:
            return {}

        elif flag[0] == 2:  # king of spades
            a = [self.plansza.mapdict[flag[1][0]]]
        elif flag[0] == 3:  # king of hearts
            a = [self.plansza.mapdict[flag[1]]]
        elif flag[0] == 4:  # jack
            a = [i for i in self.plansza.all_taken() if self.plansza.brd[
                i].color == color and self.plansza.brd[i].name == flag[1]]
        elif kar.ran == 'Q' and len(self.plansza.position_bierki('Queen', color)) > 0:
            assert flag[0] == 0
            if self.plansza.jaki_typ_zostal(color) != {'King', 'Queen'}:
                a = self.plansza.position_bierki('Queen', color)
            else:
                kar = Card(1, '5')
                a = [i for i in self.plansza.all_taken() if self.plansza.brd[
                    i].color == color]
        else:
            a = [i for i in self.plansza.all_taken() if self.plansza.brd[
                i].color == color]

        res = {}
        for i in a:
            skad = d[i]
            if okzbi:
                gdzie = [d[c] for c in self.plansza.brd[i].moves(
                    kar, self.plansza) if type(self.plansza.brd[c]) != King]
            else:
                gdzie = [d[c] for c in self.plansza.brd[i].moves(kar, self.plansza) if type(
                    self.plansza.brd[c]) != King and (self.plansza.is_empty(c) or self.plansza.brd[c].color == color)]

            if flag[0] == 2:
                try:
                    gdzie.remove(flag[1][1])
                except Exception as e:
                    raise ChessaoGameplayError('\n Error in remove! color:{} okzbi:{} karta:{} burned: {} flag {} gdzie: {} skad {} a: {}\n{}'.format(
                        color, okzbi, kar, burned, flag, gdzie, skad, a, self.snapshot()), gameplay=self, errors=e)
            if len(gdzie) > 0:
                res[skad] = gdzie

        res2 = deepcopy(res)
        for key in res2:
            for where in res2[key]:
                try:
                    pln = self.plansza.simulate_move(key, where, kar)
                except Exception as e:
                    # print('\n color: {} from {} to {} karta {}'.format(
                        # color, key, where, kar))
                    raise ChessaoGameplayError('\n color: {} from {} to {} karta {}\nSNAPSHOT:{}'.format(
                        color, key, where, kar, self.snapshot()), gameplay=self, errors=e)
                if pln.czy_szach(color) == (True, color):
                    res[key].remove(where)
                del pln
        final = {k: v for (k, v) in res.items() if v != []}
        return final


# bugi
# ♡

# co kiedy król zagrywa specjalnego króla i ma w zasięgu króla przeciwnego?
# - dokleiłem jeszcze w movesm damki warunek na typ ktory zostal
# król się zbija w pewnym momencie (jakim?)
# - dokleilem w self.possible_moves pozycje kinga
# kkier unhashable type karta
#  problem w tempie, zmienilem troche na glupa, zeby bral dobre miejsce jak widzie ze cos zle ale olewam to dla k pika.
# co kiedy zagrywam waleta, żądam ruchu damą, którą następnie zbijam?
# robię tak, że tracisz kolejkę.
# czy mogę dać czwórkę na waleta?
# robię, że nie
# może się wydarzyć taka sytuacja: czarne szachują białe. biały król
# ucieka. czarne zagrywają króla pik. (co w efekcie połowicznie realizuje
# króla pik - cofa rozgrywkę, ale zaraz karta już przestaje działać bo
# jest szach ) biały król zagrywa króla pik. -> system się jebie


# może być też tak, że król się gracz się sam wpierdoli w pata. Białe zagrywają 4, więc nie mogą zbijać, ale został im już tylko król, który ma jeden ruch -- zbić coś. Czy dopuszczamy taką opcję? Samopodpierdolenie na remis?
# roboczo - tak

# co jesli chce zagrać roszadę na królu trefl?
# wprowadzam rozwiazanie ze roszady nie można zrobić na królu..
