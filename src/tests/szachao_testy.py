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
        self.board = szachao.board()

    def test_pieces(self):
        # print(self.board.get_points('b'))
        with self.assertRaises(ValueError):
            self.board.rusz('E1', 'E2')
            # self.board.rusz('D5', 'D1')

        self.assertTrue(self.board.rusz('E2', 'E4'))


class TestPieces(unittest.TestCase):
    pass


class TestHelpers(unittest.TestCase):

    def setUp(self):
        self.deck_one = szachao.Talia()
        self.deck_one.tasuj()
        self.deck_two = szachao.Talia()
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
                         [szachao.Card(3, '5')])


class TestGame(unittest.TestCase):

    def setUp(self):
        self.gameplay = gameplay.rozgrywka()

    def test_run(self):
        # g = play_game()
        # print(g.historia)
        # self.assertFalse(play_game().szach)
        self.assertFalse(self.gameplay.mat)

if __name__ == "__main__":
    unittest.main()
