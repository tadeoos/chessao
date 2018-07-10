from chessao.cards import ChessaoCards, Card, Deck


def test_stairs_generation():
    cards = [Card(1,'2'), Card(1,'3'), Card(2,'2'), Card(3,'8')]
    gs = ChessaoCards.generate_stairs

    assert gs(cards) == [
        [Card(1,'2'), Card(1,'3')],
        [Card(1,'2'), Card(2,'2')],
        [Card(1,'3'), Card(1,'2')],
        [Card(1,'3'), Card(1,'2'), Card(2,'2')],
        [Card(2,'2'), Card(1,'2')],
        [Card(2,'2'), Card(1,'2'), Card(1,'3')],
    ]

    assert gs(cards, strict=True) == []

    cards = [Card(1,'2'), Card(3,'7'), Card(3, '8'), Card(1, '8'), Card(1, '7')]
    stairs = ChessaoCards.generate_stairs(cards)

    assert stairs == [
        [Card(3,'7'), Card(3,'8')],
        [Card(3,'7'), Card(1,'7'), Card(1,'8'), Card(3,'8')],
        [Card(3,'7'), Card(3,'8'), Card(1,'8')],
        [Card(3,'7'), Card(1,'7'), Card(1,'8')],
        [Card(3,'7'), Card(3,'8'), Card(1,'8'), Card(1,'7')],
        [Card(3,'7'), Card(1,'7')],
        [Card(3,'8'), Card(3,'7')],
        [Card(3,'8'), Card(1,'8'), Card(1,'7'), Card(3,'7')],
        [Card(3,'8'), Card(3,'7'), Card(1,'7'), Card(1,'8')],
        [Card(3,'8'), Card(1,'8')],
        [Card(3,'8'), Card(3,'7'), Card(1,'7')],
        [Card(3,'8'), Card(1,'8'), Card(1,'7')],
        [Card(1,'8'), Card(3,'8'), Card(3,'7')],
        [Card(1,'8'), Card(1,'7'), Card(3,'7')],
        [Card(1,'8'), Card(3,'8')],
        [Card(1,'8'), Card(1,'7'), Card(3,'7'), Card(3, '8')],
        [Card(1,'8'), Card(3, '8'), Card(3,'7'), Card(1,'7')],
        [Card(1,'8'), Card(1,'7')],
        [Card(1,'7'), Card(3,'7')],
        [Card(1,'7'), Card(1,'8'), Card(3,'8'), Card(3,'7')],
        [Card(1,'7'), Card(3,'7'), Card(3,'8')],
        [Card(1,'7'), Card(1,'8'), Card(3,'8')],
        [Card(1,'7'), Card(3,'7'), Card(3,'8'), Card(1,'8')],
        [Card(1,'7'), Card(1,'8')],
        ]

def test_stairs_generation_with_the_same_card_twice():
    # can't use a duplicate of card in stairs
    cards = [Card(1,'2'), Card(3,'7'), Card(4, '8'), Card(4, '8'), Card(1, '5')]
    stairs = ChessaoCards.generate_stairs(cards)
    assert stairs == []
