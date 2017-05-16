import coverage
import doctest
import unittest
import time

# jakie testy?
# 1. Czy dane pole NIE jest w możliwym zakresie
# 2. Czy dane pole JEST w możliwym zakresie
# 3. Czy dana figura JEST/NIE MA w możliwym zakresie...
# Pustość ruchu


def game(rnd=0):
    game = gameplay.rozgrywka(rnd)
    game.graj(rnd)
    return game


class TestGame(unittest.TestCase):
    import gameplay

    def setUp(self):
        self.deck = szachao.Talia()
        self.board = szachao.board()
        self.gameplay = gameplay.rozgrywka()

    def test_pieces(self):
        print(self.board.get_points('b'))
        with self.assertRaises(ValueError):
            self.board.rusz('E1', 'E2')
            # self.board.rusz('D5', 'D1')

        self.assertTrue(self.board.rusz('E2', 'E4'))

    def test_run(self):
        g = game()
        print(g.historia)
        self.assertFalse(game().szach)

if __name__ == "__main__":
    t1 = time.time()
    cov = coverage.coverage(branch=True)
    cov.erase()
    cov.start()
    import testy2
    import gameplay
    import szachao
    doctest.testmod(szachao)
    doctest.testmod(gameplay)
    cov.stop()
    modules = [szachao, gameplay]
    cov.report(modules, ignore_errors=1, show_missing=1)
    cov.html_report(morfs=modules, directory='/tmp')
    cov.erase()
    t2 = time.time()
    print('TESTS TOOK TIME: {:.2f} min'.format((t2 - t1) / 60))
    unittest.main()
