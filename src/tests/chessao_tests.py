#!/usr/bin/env python
import doctest
from os import path
import sys
import time
import unittest
import coverage

PATH_TO_SRC_DIR = path.join(path.abspath(path.dirname(__file__)), '..')
sys.path.insert(0, PATH_TO_SRC_DIR)  # make chessao module available to Python

if __name__ == "__main__":
    try:
        runs = int(sys.argv[1])
        sys.argv.pop()
    except IndexError:
        runs = 1
    print('Running {} games...'.format(runs))
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

    test_run = 'TestRun{}'.format(runs) if runs > 0 else None

    tests = ['TestBoard', 'TestHelpers', 'TestGamePlay']
    if test_run:
        tests.append(test_run)
    # tests.append('TestRun20')
    unittest.main(module='unit_tests', exit=False, verbosity=2, defaultTest=tests)
    cov.stop()
    modls = [chess, gameplay, cards, helpers, pieces, players]
    cov.report(modls, ignore_errors=1, show_missing=1)
    cov.html_report(morfs=modls, directory='htmlcov')
    cov.erase()
    t2 = time.time()
    print('\n----- TESTS TOOK: {:.2f} min'.format((t2 - t1) / 60))
