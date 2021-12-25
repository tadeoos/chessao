from collections import defaultdict

from chessao.cards import Card

CARD_RULES = defaultdict(lambda: defaultdict(lambda: True))

CARD_RULES[Card(1, '4')][Card(1, 'K')] = False
CARD_RULES[Card(2, '4')][Card(1, 'K')] = False
CARD_RULES[Card(3, '4')][Card(1, 'K')] = False
CARD_RULES[Card(4, '4')][Card(1, 'K')] = False
