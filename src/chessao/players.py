"""
Players classes
"""

import random
from chessao.cards import Card
from chessao.chess import Board
from chessao.helpers import ok_karta, invert_color, nawaleta


class Player():
    '''A player abstract class.'''

    def __init__(self, ida, kol, reka=None, bot=True, name='gracz'):
        self.nr = ida
        self.kol = kol
        self.reka = reka
        self.name = name
        self.bot = bot

    def __str__(self):
        return '{} {}'.format(self.name, self.nr)

    def __repr__(self):
        return '{} {}'.format(self.name, self.nr)

    def choose_card(self, talie, plansza):
        pass

    def get_three(self, n):
        raise NotImplementedError

    def choose_move(self, d, plansza, karta):
        pass

    def choose_prom(self):
        pass


class gracz(Player):

    def choose_card(self, talie, plansza):
        if self.bot:
            los = random.randint(0, 4)
            burn = 1 if los == 0 else 0
            card = random.choice(self.reka)
            if not ok_karta([card], talie):
                burn = 1
            if not burn and card.ran == 'J':
                ch = [s[0] for s in plansza.jaki_typ_zostal(
                    invert_color(self.kol)) if s != 'King']
                # here is a problem with jack loosing its ability when there is
                # only king left..
                if len(ch) == 0:
                    return (burn, [card])
                choice = random.choice(ch)
                return (burn, [card], nawaleta(choice))
            return (burn, [card])
        else:
            print('\nKupki: |{0:>3} |  |{1:>3} |'.format(
                str(talie[0][-1]), str(talie[1][-1])))
            print(plansza)
            print(self.kol, self.reka)

            ask = int(input('Karta: (1,2,3,4,5)? ')) - 1
            ask_burn = int(input('Do you want to burn that card? (0/1) ')
                           ) if ok_karta([self.reka[ask]], talie) else 1
            return (ask_burn, [self.reka[ask]])
            # trza dokończyć..

    def get_three(self, n):
        if self.bot:
            return random.sample(self.reka, n)
        else:
            # functionality for humans
            return random.sample(self.reka, n)
            # return None

    def choose_move(self, d, plansza, karta):
        if self.bot:
            random_ruch = random.choice(list(d.keys()))
            random_nr = random.randint(0, len(d[random_ruch]) - 1)
            return [random_ruch, d[random_ruch][random_nr]]
        else:
            print('Possible moves: {}'.format(d))
            while True:
                ask = input('Ruch: ').upper().split()
                if ask[0] in d.keys() and ask[1] in d[ask[0]]:
                    break
                print('You cannot make this move, choose another one!')
            return ask

    def choose_prom(self):
        if self.bot:
            return random.choice(['D', 'G', 'S', 'W'])
        else:
            return input('Na jaką figurę chcesz zamienić piona?\nD - Dama\nG - Goniec\nS - Skoczek\nW - Wieża\n').upper()


class gracz_str(gracz):

    def choose_move(self, d, plansza, karta):
        move_list = [[skad, gdzie] for skad in d.keys() for gdzie in d[skad]]
        rating_list = []
        for m in move_list:
            brd = plansza.simulate_move(m[0], m[1], karta)
            check = 1 if brd.czy_szach(invert_color(self.kol)) else 0
            # mat = 100 if brd.czy_szach(invert_color(self.kol)) and
            # brd.czy_pat(invert_color(self.kol)) else 0
            broniony = 4 if plansza.pod_biciem(
                plansza.mapdict[m[1]], self.kol) else 0
            atakowany = 4 if plansza.pod_biciem(
                plansza.mapdict[m[1]], invert_color(self.kol)) else 0
            rating = (brd.get_points(self.kol) - brd.get_points(invert_color(self.kol))
                      ) + (check * broniony) + broniony - atakowany
            rating_list.append((rating, m))
        maks = sorted(rating_list)[-1][0]
        return random.choice([move for (a, move) in rating_list if a == maks])

    def choose_prom(self):
        return 'D'
