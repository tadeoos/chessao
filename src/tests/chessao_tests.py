import doctest
import os
import sys
import time
import unittest
import coverage

PATH_TO_SRC = os.path.split(os.path.dirname(__file__))[0]
sys.path.insert(0, PATH_TO_SRC)

if __name__ == "__main__":
    t1 = time.time()
    cov = coverage.coverage(branch=True)
    cov.erase()
    cov.start()
    import chessao.gameplay as gameplay
    import chessao.chess as chess
    import chessao.cards as cards
    import chessao.helpers as helpers
    import chessao.players as players
    import chessao.pieces as pieces
    doctest.testmod(chess)
    doctest.testmod(gameplay)
    doctest.testmod(cards)
    doctest.testmod(helpers)
    doctest.testmod(pieces)
    doctest.testmod(players)
    unittest.main(module='unit_tests', exit=False, verbosity=2)
    cov.stop()
    modls = [chess, gameplay, cards, helpers, pieces, players]
    cov.report(modls, ignore_errors=1, show_missing=1)
    cov.html_report(morfs=modls, directory='htmlcov')
    cov.erase()
    t2 = time.time()
    print('\n----- TESTS TOOK: {:.2f} min'.format((t2 - t1) / 60))
