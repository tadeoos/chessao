import json
import os
import pickle

from chessao.cards import Card
from chessao import SIMULATION_BUGS_PATH


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
    path = path or SIMULATION_BUGS_PATH
    for filename in path.iterdir():
        with open(os.path.join(path, filename)) as f:
            try:
                data[str(filename)] = json.load(f)
            except json.decoder.JSONDecodeError:
                continue
    if parametrize:
        parameters = []
        ids_ = []
        for k, v in data.items():
            parameters.append((v['ledger'], v['starting_deck'], v['stalemate'], v['mate']))
            ids_.append(k)
        return parameters, ids_
    return data


def load_game_pkl_from(filename, path=None):
    path = path or SIMULATION_BUGS_PATH
    with open(os.path.join(path, filename), 'rb') as f:
        return pickle.load(f)
