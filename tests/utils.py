import json
import os

from chessao import WHITE_COLOR, BLACK_COLOR
from chessao.cards import Card


def assert_lists_equal(l1, l2):
    """
    >>> assert_lists_equal([1,2], [2,1])
    """
    assert set(l1) == set(l2)


def card_list(list_of_strings):
    """
    >>> card_list(['21', '71'])
    [2♤, 7♤]
    """
    return [*map(Card.from_string, list_of_strings)]


def load_simulation_bugs(parametrize=False, path=None):
    data = {}
    path = path or '/Users/Tadeo/dev/TAD/szachao/tests/simulation_bugs/'
    for filename in os.listdir(path):
        with open(os.path.join(path, filename)) as f:
            data[filename] = json.load(f)
    if parametrize:
        parameters = []
        ids_ = []
        for k, v in data.items():
            parameters.append((v['ledger'], v['starting_deck'], v['stalemate'], v['mate']))
            ids_.append(k)
        return parameters, ids_
    return data
