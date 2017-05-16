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
    game = roz2.rozgrywka(rnd)
    game.graj(rnd)
    return game


class TestGame(unittest.TestCase):
    import roz2

    def setUp(self):
        self.roz = roz2.rozgrywka(0)

    def test_run(self):
        g = game()
        print(g.historia)
        self.assertFalse(game().szach)

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == "__main__":
    t1 = time.time()
    cov = coverage.coverage(branch=True)
    cov.erase()
    cov.start()
    import testy2
    import roz2
    import szachao
    doctest.testmod(szachao)
    doctest.testmod(roz2)
    cov.stop()
    modules = [szachao, roz2]
    cov.report(modules, ignore_errors=1, show_missing=1)
    cov.html_report(morfs=modules, directory='/tmp')
    cov.erase()
    t2 = time.time()
    print('TESTS TOOK TIME: {:.2f} min'.format((t2 - t1) / 60))
    unittest.main()
