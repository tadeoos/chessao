import coverage
import doctest
import os
import sys
import time

path_to_src = os.path.split(os.path.dirname(__file__))[0]
sys.path.insert(0, path_to_src)


if __name__ == "__main__":
    t1 = time.time()
    cov = coverage.coverage(branch=True)
    cov.erase()
    cov.start()
    # import testy2
    import chessao.gameplay as gameplay
    import chessao.szachao as szachao
    doctest.testmod(szachao)
    doctest.testmod(gameplay)
    cov.stop()
    modls = [szachao, gameplay]
    cov.report(modls, ignore_errors=1, show_missing=1)
    cov.html_report(morfs=modls, directory='/tmp')
    cov.erase()
    t2 = time.time()
    print('TESTS TOOK TIME: {:.2f} min'.format((t2 - t1) / 60))
