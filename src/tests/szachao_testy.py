import coverage
import doctest
import time
import unittest
import chessao.szachao as szachao
import chessao.gameplay as gameplay
import chessao.helpers as helpers

# jakie testy?
# 1. Czy dane pole NIE jest w możliwym zakresie
# 2. Czy dane pole JEST w możliwym zakresie
# 3. Czy dana figura JEST/NIE MA w możliwym zakresie...
# Pustość ruchu


def play_game(rnd=0):
    game = gameplay.rozgrywka(rnd)
    game.graj(rnd)
    return game


class TestBoard(unittest.TestCase):

    def setUp(self):
        self.Board = szachao.Board()

    def test_pieces(self):
        # print(self.Board.get_points('b'))
        with self.assertRaises(ValueError):
            self.Board.rusz('E1', 'E2')
            # self.Board.rusz('D5', 'D1')

        self.assertTrue(self.Board.rusz('E2', 'E4'))


class TestPieces(unittest.TestCase):
    pass


class TestHelpers(unittest.TestCase):

    def setUp(self):
        self.deck_one = szachao.Deck()
        self.deck_one.tasuj()
        self.deck_two = szachao.Deck()
        self.deck_two.tasuj()
        self.pile = ([szachao.Card(2, '6')], [szachao.Card(1, '10')])
        self.hand = [szachao.Card(3, '5'), szachao.Card(2, '7'),
                     szachao.Card(2, 'K'), szachao.Card(4, '5')]

    def test_card_helpers(self):
        self.assertTrue(helpers.ok_karta(
            [szachao.Card(1, 'Q')], self.pile))
        self.assertTrue(helpers.ok_karta([szachao.Card(
            2, 'Q')], self.pile))
        self.assertTrue(helpers.ok_karta([szachao.Card(
            3, 'Q')], self.pile))
        self.assertTrue(helpers.ok_karta([szachao.Card(
            4, 'Q')], self.pile))
        self.assertTrue(helpers.ok_karta([szachao.Card(
            1, '5')], self.pile))
        self.assertTrue(helpers.ok_karta([szachao.Card(
            1, '6')], self.pile))
        self.assertTrue(helpers.ok_karta([szachao.Card(
            1, '10')], self.pile))
        self.assertFalse(helpers.ok_karta([szachao.Card(
            3, '5')], self.pile))
        self.assertTrue(helpers.ok_karta([szachao.Card(1, '5'),
                                          szachao.Card(1, '6'),
                                          szachao.Card(1, '7')], self.pile))

        self.assertEqual(helpers.odejmij(self.hand, [szachao.Card(2, '7')]),
                         [szachao.Card(3, '5'), szachao.Card(2, 'K'),
                          szachao.Card(4, '5')])
        self.assertNotEqual(helpers.odejmij(self.hand, [szachao.Card(4, '5')]),
                            [szachao.Card(3, '5')])


class TestGame(unittest.TestCase):

    def setUp(self):
        self.gameplay = gameplay.rozgrywka()
        self.resurect = gameplay.resurect(['RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr KQkq - 0 0', 'b !8♧  PF2:F3', 'c !J♢  pD7:D5', 'b 5♢  PC2:C4', 'c !J♧  bC8:E6',
                                           'b !A♧  PC4:D5', 'c 3♢  nB8:C6', 'b !6♤  PD2:D4', 'c !A♡  rA8:B8', 'b !9♤  PD5:D6', 'c 9♢  pF7:F5'])

    def test_run(self):
        g = play_game()
        print(
            '\n-- Snapshot:\n{}\n{}'.format(
                '',
                g.snapshot()))
        # print(g.historia)

        self.assertFalse(self.gameplay.mat)

    def test_resurect(self):
        self.assertFalse(self.resurect.mat)

if __name__ == "__main__":
    unittest.main()
