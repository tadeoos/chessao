import time
import unittest

import pytest
from pympler import asizeof

import chessao.chess as chess
import chessao.cards as chcards
import chessao.gameplay as gameplay
import chessao.helpers as helpers

# jakie testy?
# 1. Czy dane pole NIE jest w możliwym zakresie
# 2. Czy dane pole JEST w możliwym zakresie
# 3. Czy dana figura JEST/NIE MA w możliwym zakresie...
# Pustość ruchu


def play_game(rand=0):
    game = gameplay.ChessaoGame(rand)
    played = game.graj(rand)
    return game, played


class TestBoard(unittest.TestCase):

    def setUp(self):
        self.board = chess.Board()

    def test_pieces(self):
        with self.assertRaises(AssertionError):
            self.board.move('E1', 'E2')

        self.assertTrue(self.board.move('E2', 'E4'))


class TestPieces(unittest.TestCase):
    pass


class TestHelpers(unittest.TestCase):

    def setUp(self):
        self.deck_one = chcards.Deck()
        self.deck_one.shuffle()
        self.deck_two = chcards.Deck()
        self.deck_two.shuffle()
        self.pile = ([chcards.Card(2, '6')], [chcards.Card(1, '10')])
        self.hand = [chcards.Card(3, '5'), chcards.Card(2, '7'),
                     chcards.Card(2, 'K'), chcards.Card(4, '5')]

    def test_ok_karta(self):
        self.assertTrue(helpers.ok_karta(
            [chcards.Card(1, 'Q')], self.pile))
        self.assertTrue(helpers.ok_karta([chcards.Card(
            2, 'Q')], self.pile))
        self.assertTrue(helpers.ok_karta([chcards.Card(
            3, 'Q')], self.pile))
        self.assertTrue(helpers.ok_karta([chcards.Card(
            4, 'Q')], self.pile))
        self.assertTrue(helpers.ok_karta([chcards.Card(
            1, '5')], self.pile))
        self.assertTrue(helpers.ok_karta([chcards.Card(
            1, '6')], self.pile))
        self.assertTrue(helpers.ok_karta([chcards.Card(
            1, '10')], self.pile))
        self.assertFalse(helpers.ok_karta([chcards.Card(
            3, '5')], self.pile))
        self.assertTrue(helpers.ok_karta([chcards.Card(1, '5'),
                                          chcards.Card(1, '6'),
                                          chcards.Card(1, '7')], self.pile))

    def test_odejmij(self):
        self.assertEqual(helpers.odejmij(self.hand, [chcards.Card(2, '7')]),
                         [chcards.Card(3, '5'), chcards.Card(2, 'K'),
                          chcards.Card(4, '5')])
        self.assertNotEqual(helpers.odejmij(self.hand, [chcards.Card(4, '5')]),
                            [chcards.Card(3, '5')])


@pytest.mark.skip(reason="Pure tests")
class TestRun1(unittest.TestCase):
    NUMBER = 1

    def setUp(self):
        self.gameplay = gameplay.ChessaoGame()

    def test_run(self):
        self.assertFalse(self.gameplay.mat or self.gameplay.pat)
        print('')
        t1 = time.time()
        for i in range(self.NUMBER):
            t2 = time.time()
            eta = ((self.NUMBER / i) - 1) * \
                (t2 - t1) if i > 0 else 30 * self.NUMBER
            with self.subTest(i=i):
                print("\rDONE: {:.0f}%  RUNNING: {} of {} ESTIMATED TIME: {:.1f} min".format(
                    (i / self.NUMBER) * 100, i + 1, self.NUMBER, eta / 60),
                    end="")
                try:
                    game = play_game()
                    g, played = game[0], game[1]
                    print('SIZE OF Gameplay object: {} bytes'.format(asizeof.asizeof(g)))
                    self.assertTrue(played)
                except helpers.ChessaoGameplayError as e:
                    print(e.ChessaoGame.snapshot)
                    raise e

                g_cards = g.spalone + g.karty.cards + g.kupki[0] + g.kupki[1]

                self.assertTrue(g.mat or g.pat)
                self.assertTrue(len(g_cards) == 94)
        # print('\n-- Snapshot:\n{}\n{}'.format(g, g.snapshot()))


class TestGamePlay(unittest.TestCase):

    def setUp(self):
        self.gameplay = gameplay.ChessaoGame(default_setup=True)
        self.HISTORY = [
            "1N3R2/1p1N1p1K/3P4/2b4P/7P/1p2P2r/1p2p3/1r1k1bn1 - - 0 29",
            "b !7♤  NB1:C3",
            "c 4♤  qB2:B1=D",
            "b K♤ "
        ]

    @pytest.mark.skip(reason="Known failure")
    def test_resurect(self):
        resur = gameplay.resurect([
            'RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr KQkq - 0 0',
            'b !8♧  PF2:F3', 'c !J♢  pD7:D5', 'b 5♢  PC2:C4',
            'c !J♧  bC8:E6', 'b !A♧  PC4:D5', 'c 3♢  nB8:C6',
            'b !6♤  PD2:D4', 'c !A♡  rA8:B8', 'b !9♤  PD5:D6',
            'c 9♢  pF7:F5'
        ])
        self.assertFalse(resur.mat)
        with self.assertRaises(helpers.ChessaoGameplayError):
            gameplay.resurect(self.HISTORY)

    @pytest.mark.skip(reason="Not refactored yet")
    def test_printing(self):
        self.assertIsNotNone(str(self.gameplay))
        self.assertIsNotNone(self.gameplay.snapshot())


@pytest.mark.skip(reason="Not doing multiple runs with pytest...")
class TestRun2(TestRun1):
    NUMBER = 2


@pytest.mark.skip(reason="Not doing multiple runs with pytest...")
class TestRun20(TestRun1):
    NUMBER = 20


@pytest.mark.skip(reason="Not doing multiple runs with pytest...")
class TestRun50(TestRun1):
    NUMBER = 50


@pytest.mark.skip(reason="Not doing multiple runs with pytest...")
class TestRun100(TestRun1):
    NUMBER = 100


if __name__ == "__main__":
    unittest.main(verbosity=2)
