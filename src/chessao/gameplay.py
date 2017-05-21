import json
import os
import random
import re
import time
from chessao.helpers import *
from chessao.chess import Board
from chessao.players import *
from chessao.cards import Card, Deck
from chessao.pieces import *


class GameplayEncoder(json.JSONEncoder):
    '''A JSON encoder class for Gameplay object.'''

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
    '''Create a Gameplay object from a history.'''
    if not gameplay:
        result_gameplay = rozgrywka(fenrep=history[0])
    else:
        result_gameplay = gameplay
    entry = history[1].split()

    str_card = entry[1]
    if str_card[0] == '!':
        card = Card(1, '5')
    else:
        try:
            assert len(str_card) == 2
        except AssertionError:
            print('long entry: \nentry {}\nstr_card {}'.format(entry, str_card))
        finally:
            color = decode_card_color(str_card[1])
            card = Card(color, str_card[0])

    where = entry[2][1:].split(':')
    try:
        result_gameplay.move(card, where)
    except Exception as e:
        # print(e)
        # print('color: {}, card: {}, where: {}'.format(color, card, where))
        raise ChessaoGameplayError(
            'RESSURECT move function error', gameplay=result_gameplay, errors=e)
    if len(history) == 2:
        return result_gameplay
    return resurect(history[1:], result_gameplay)


# SZACHAO CLASS


class rozgrywka:
    """A gameplay class."""

    def __init__(self, rnd=1, fenrep=False, auto=True, ovr=False, test=False):
        # random.seed()
        self.plansza = Board(rnd, fenrep)
        self.karty = Deck()
        self.karty.combine(Deck().cards)
        self.karty.tasuj()
        tpr = deal(self.karty, ovr)
        # auto play
        self.gracze = (gracz(1, 'b', tpr[0], bot=True), gracz_str(2, 'c', tpr[1])) if auto else (
            gracz(1, 'b', tpr[0], bot=False), gracz(2, 'c', tpr[1], bot=False))

        self.karty = tpr[2]
        self.kupki = ([self.karty.cards.pop()], [self.karty.cards.pop()]) if not test else ([self.karty.cards.pop(
            self.karty.get_card_index(rank='Q', suit=3))], [self.karty.cards.pop(self.karty.get_card_index(rank='Q', suit=4))])
        self.szach = False
        self.mat = False
        self.pat = False
        self.spalone = []
        self.historia = [self.plansza.fen()]
        self.zamiana = False
        self.to_move = 'b'
        self.burned = False
        self.now_card = None
        self.now_move = None
        self.jack = None
        self.three = 0
        self.four = False
        self.capture = True

    def __str__(self):
        gb = self.get_gracz('b')
        gc = self.get_gracz('c')
        print('\nKupki: |{0:>3} |  |{1:>3} |'.format(
            str(self.kupki[0][-1]), str(self.kupki[1][-1])))
        print('\nKARTA:  {}{}'.format('!' if self.burned else '', self.now_card))
        print('\n{} {} (white): {}\n'.format(gb.name, gb.nr, gb.reka))
        print('{}'.format(self.plansza))
        print('{} {} (black): {}'.format(gc.name, gc.nr, gc.reka))
        # print('\nDeck: \n{} ...\n'.format(self.karty.cards[-5:][::-1]))
        return ''

    def snapshot(self, jsn=True, remove=None):
        """Return a JSON representation of a current state."""
        snap = self.__dict__
        # del snap['gracze']
        if remove:
            for key in remove:
                del snap[key]
        try:
            res = json.dumps(self.__dict__, cls=GameplayEncoder,
                             sort_keys=True, indent=2)
        except TypeError as e:
            res = snap
            cards = snap['karty']['cards']
            raise ChessaoGameplayError('\nSNAP ERROR: {}\ntype of cards {}\n type of card {}\n'.format(
                e, type(cards), type(cards[1])), gameplay=self, errors=e)
        else:
            return res

    def do_card_buisness(self, kar, three=False):
        player = self.get_gracz(self.to_move)

        if self.burned:
            if not three:
                assert len(kar) == 1
            try:
                player.reka = odejmij(player.reka, kar)
                # assert len(player.reka)==5
            except AssertionError as e:
                print('\n three: {} reka {}, kar {}'.format(
                    self.three, player.reka, kar))
            self.spalone.extend(kar)
            if len(self.karty.cards) < len(kar):
                self.przetasuj()
            tas = self.karty.deal(len(kar))
            player.reka.extend(tas)
        else:
            if self.szach:
                assert kar[-1].ran != 'A'
            player.reka = odejmij(player.reka, kar)
            self.kupki[ktora_kupka(kar, self.kupki, player.bot)].extend(kar)
            if len(self.karty.cards) < len(kar):
                self.przetasuj()
            tas = self.karty.deal(len(kar))
            player.reka.extend(tas)

        assert len(player.reka) == 5

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

        return True

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
            tmpcar = player.get_three(
                3) if self.three == 3 else player.get_three(5)
            self.do_card_buisness(tmpcar, three=True)
            self.three = 0
        elif w[0] != 2:
            self.do_card_buisness(card[1])

        # now_card birth
        self.now_card = card[1][0]

        if len(card) == 3:
            self.jack = card[2]
            assert self.jack in self.plansza.jaki_typ_zostal(
                invert_color(self.to_move))
        else:
            self.jack = None
        if self.now_card.ran == '4' and not self.burned:
            self.capture = False
        if self.now_card.ran == '3' and not self.burned:
            add = sum([3 for c in card[1] if c.ran == '3'])
            assert add > 2
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

    def move(self, card, where):
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
            print('where: {} card {}'.format(where, card))
            raise ChessaoGameplayError(
                'self.plansza.rusz error', gameplay=self, errors=e)

        # checking if pawn is getting promoted
        q = 'BŁĄD!!'
        zam = czy_pion_na_koncu(self.plansza, self.to_move)
        if zam > 0:
            self.zamiana = True
            self.plansza.zbite.append(self.plansza.brd[zam])
            q = player.choose_prom()
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
                print('wrong input')

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
        record = '{color} {burn}{car}{jack}  {piece}{fro}:{to}{prom}{check}{mate} {fenrep}'.format(color=invert_color(self.to_move),
                                                                                                   burn='!' if self.burned else '', car=card, jack=';' + self.jack[0] if self.jack != None else '',
                                                                                                   piece=self.plansza.get_fen_rep(self.plansza.get_piece(where[1])), fro=where[0], to=where[1],
                                                                                                   prom='=' + q if self.zamiana else '', check='+' if self.szach else '', mate='#' if self.mat else '', fenrep=self.plansza.fen())
        self.historia.append(record)
        return True

    def czy_szach(self, k):
        """Return True if color k is checked."""
        s = self.plansza.czy_szach(k)
        if s == (True, k):
            return True
        # elif s == 2:
        # 	return 2
        return False

    def czy_pat(self, k):
        """Return True if there is a stalemate."""
        if self.plansza.halfmoveclock == 100 or len(self.plansza.all_taken()) == 2:
            return True
        szach = self.czy_szach(k)
        for kar in self.get_gracz(k).reka:
            if ok_karta([kar], self.kupki):
                if szach and kar.ran == 'Q':
                    continue
                res = self.possible_moves(k, True, kar)
                if len(res) > 0:
                    return False
            else:
                res = self.possible_moves(k)
                if len(res) > 0:
                    return False
        return True

    def get_gracz(self, k):
        """Return a player who has pieces of color k."""
        return [g for g in self.gracze if g.kol == k][0]

    def cofnij(self, color, ruch):
        """Reverese the move ."""
        assert len(self.historia) > 2
        a = self.plansza.mapdict[ruch[0]]
        b = self.plansza.mapdict[ruch[1]]

        # clearing enpassant and subtracting move counter
        self.plansza.enpass = 300

        # see if a promotion had been made
        if '=' in self.historia[-2]:
            # if gambit teleżyńskiego occured...
            if 'q' in self.historia[-2].split()[2].lower():
                self.plansza.brd[a] = self.plansza.zbite.pop()
            else:
                self.plansza.brd[b] = self.plansza.zbite.pop()

        self.plansza.brd[b].mvs_number -= 1

        if self.plansza.bicie:
            assert self.plansza.is_empty(a)
            rezurekt = self.plansza.zbite.pop()
            self.plansza.brd[a] = rezurekt
            self.plansza.swap(a, b)
        else:
            self.plansza.swap(a, b)
        assert not self.plansza.is_empty(a) or not self.plansza.is_empty(b)

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
        all_cards = len(self.karty.cards) + len(self.kupki[0]) + len(self.kupki[1]) + len(
            self.spalone) + len(self.gracze[0].reka) + len(self.gracze[1].reka)
        if all_cards != 104:
            print('\nALL CARDS: {}'.format(all_cards))
        #
        assert all_cards == 104

    def what_happened(self):
        """
        this function is parsing the history to make sense of the situation. returns ints that code a situation.
        0 = nothing special, 1 = turn loosing, 2 - king of spades, 3 - king
        of hearts, 4 - jack
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
        elif what == 'K' and s[3] == '♤' and ind != None:
            # r = re.search('\s(.+)\s',s2)
            c = self.from_history_get_card(2)
            return (2, [s2[:ind][-2:], s2[ind + 1:][:2]], c)
        elif what == 'K' and s[3] == '♡' and ind != None:
            if self.plansza.get_piece(s2[ind + 1:][:2]).color != self.to_move:
                return (1,)
            return (3, s2[ind + 1:][:2])
        elif what == 'J' and self.now_card.ran != 'J':
            if self.jack not in self.plansza.jaki_typ_zostal(self.to_move):
                return (1,)
            return (4, self.jack)
        else:
            return (0,)

    def check_if_move(self, n):
        """
        # check if n turnes ago there was a move made
        # if true this means three possible scenarios happened - kspades,ace or
        # lost turn
        """
        return ':' in self.historia[-n]

    def check_card(self, n, r, cl=None):
        """
        # check if card played n turns ago has a rank==ran (and color = col)
        # if card was burned returns False
        """
        c = from_history_get_card(n)
        if c[0] == 1:
            return False
        return c[1].ran == r and c[1].kol == cl if cl != None else c[1].ran == r

    def from_history_get_card(self, n):
        """
        # returns a card played n turns AGO
        """
        if n > len(self.historia):
            return None
        s = self.historia[-n]
        r = re.search('\s(.+?)\s', s)
        c = r.group(1)
        return decode_card(c)

    def card_ok_to_play(self, crd):
        """
        # if card is to be burned its always ok to play it
        """
        if crd[0] == 1:
            return True
        c = crd[1][0]
        # conditions that if met block the card
        cond1 = self.szach and (c.ran == 'A' or c.ran == 'Q')

        # war2 = (kar[-1].ran=='K' and kar[-1].kol==1) and (last_card.ran=='A' or licznik<3 or temp=='ominięta')
        # war3 = (kar[-1].ran=='K' and kar[-1].kol==2) and (licznik<2 or temp=='ominięta')
        # war4 = last_card.ran=='J' and kar[-1].ran=='4' and ok_karta(kar,self.kupki)
        # war5 = kar[-1].ran=='4' and self.szach and
        # len(self.possible_moves(kolej, False, kar[-1]))==0

        if cond1:
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
                    raise ChessaoGameplayError('\n Error in remove! color:{} okzbi:{} karta:{} burned: {} flag {} gdzie: {} skad {} a: {}'.format(
                        color, okzbi, kar, burned, flag, gdzie, skad, a), gameplay=self, errors=e)
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
                    raise ChessaoGameplayError('\n color: {} from {} to {} karta {}'.format(
                        color, key, where, kar), gameplay=self, errors=e)
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
