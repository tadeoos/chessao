"""
Players classes
"""
import random
from typing import List

from chessao.cards import Card
from chessao.helpers import ok_karta, invert_color


class Player:
    """A player abstract class."""

    def __init__(self, id_, color, hand=None, bot=True, name='gracz'):
        self.id = id_
        self.color = color
        self.hand = hand or []
        self.name = name
        self.bot = bot

    def __str__(self):
        return f'{self.name}(hand={self.hand}, color={self.color})'

    def __repr__(self):
        return str(self)

    def choose_card(self, talie, plansza):
        """Returns a card from player hand."""
        raise NotImplementedError

    def choose_any(self):
        """Returns random card"""
        return [random.choice(self.hand)]

    def get_three(self, n):
        raise NotImplementedError

    def update_cards(self, cards: List[Card]):
        self.hand.extend(cards)
        assert len(self.hand) == 5

    def remove_cards(self, cards: List[Card]):
        for card in cards:
            try:
                self.hand.remove(card)
            except ValueError:
                raise ValueError(
                    f"Card not in player's hand: {card}, hand: {self.hand}")

    def choose_move(self, d, plansza, karta):
        """Select a move out ou a board."""
        raise NotImplementedError

    def choose_prom(self):
        """Choose a promotion for pawn at the end of the board."""
        raise NotImplementedError

    def to_json(self):
        return str(self)


class gracz(Player):

    def choose_card(self, talie, plansza=None):
        if self.bot:
            los = random.randint(0, 4)
            burn = 1 if los == 0 else 0
            card = random.choice(self.hand)
            if not ok_karta([card], talie):
                burn = 1
            # if not burn and card.ran == 'J':
            #     ch = [s[0] for s in plansza.piece_types_left(
            #         invert_color(self.color)) if s != 'King']
            #     # here is a problem with jack loosing its ability when there is
            #     # only king left..
            #     if len(ch) == 0:
            #         return (burn, [card])
            #     choice = random.choice(ch)
            #     return (burn, [card], nawaleta(choice))
            return (burn, [card])
        else:
            print('\nKupki: |{0:>3} |  |{1:>3} |'.format(
                str(talie[0][-1]), str(talie[1][-1])))
            print(plansza)
            print(self.color, self.hand)

            ask = int(input('Karta: (1,2,3,4,5)? ')) - 1
            ask_burn = int(input('Do you want to burn that card? (0/1) ')
                           ) if ok_karta([self.hand[ask]], talie) else 1
            return (ask_burn, [self.hand[ask]])
            # trza dokończyć..

    def get_three(self, n, blacklist=[]):
        if self.bot:
            sample = [c for c in self.hand if c not in blacklist]
            return random.sample(sample, n)
        else:
            # functionality for humans
            return random.sample(self.hand, n)
            # return None

    def choose_move(self, possible_moves):
        if self.bot:
            random_ruch = random.choice(list(possible_moves.keys()))
            random_nr = random.randint(0, len(possible_moves[random_ruch]) - 1)
            return [random_ruch, possible_moves[random_ruch][random_nr]]
        else:
            print('Possible moves: {}'.format(possible_moves))
            while True:
                ask = input('Ruch: ').upper().split()
                if ask[0] in possible_moves.keys() and ask[1] in possible_moves[ask[0]]:
                    break
                print('You cannot make this move, choose another one!')
            return ask

    def choose_prom(self):
        if self.bot:
            return random.choice(['D', 'G', 'S', 'W'])
        else:
            return input(f'''Na jaką figurę chcesz zamienić piona?
                        \nD - Dama\nG - Goniec\nS - Skoczek\nW - Wieża\n''').upper()


class StrategicBot(gracz):

    def choose_move(self, d, plansza, karta):
        move_list = [[skad, gdzie] for skad in d.keys() for gdzie in d[skad]]
        rating_list = []
        for m in move_list:
            brd = plansza.simulate_move(m[0], m[1], karta)
            check = 1 if brd.color_is_checked(invert_color(self.color)) else 0
            # mat = 100 if brd.color_is_checked(invert_color(self.color)) and
            # brd.czy_pat(invert_color(self.color)) else 0
            broniony = 4 if plansza.under_attack(
                plansza.mapdict[m[1]], self.color) else 0
            atakowany = 4 if plansza.under_attack(
                plansza.mapdict[m[1]], invert_color(self.color)) else 0
            rating = (brd.get_points(self.color) - brd.get_points(invert_color(self.color))
                      ) + (check * broniony) + broniony - atakowany
            rating_list.append((rating, m))
        maks = sorted(rating_list)[-1][0]
        return random.choice([move for (a, move) in rating_list if a == maks])

    def choose_prom(self):
        return 'D'