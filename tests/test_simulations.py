import os
from distutils.util import strtobool

import pytest

from chessao.gameplay import ChessaoGame
from .utils import load_simulation_bugs


simulation_data, ids_ = load_simulation_bugs(parametrize=True)


# @pytest.mark.xfail(reason="Testing bugs")
@pytest.mark.simbugs
@pytest.mark.skipif(strtobool(os.environ.get('CHESSAO_TEST_FULL', '0')) == 0,
                    reason='Skipping by default. `export CHESSAO_TEST_FULL=1` to run.')
@pytest.mark.parametrize("ledger,starting_deck,stalemate,mate", simulation_data, ids=ids_)
def test_simulation_bugs(ledger, starting_deck, stalemate, mate):
    game = ChessaoGame.from_ledger(ledger, starting_deck)
    assert game.stalemate == stalemate
    assert game.mate == mate
