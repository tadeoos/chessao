from chessao import WHITE_COLOR, BLACK_COLOR
from chessao.cards import Card
from chessao.gameplay import ChessaoGame
from chessao.players import StrategicBot


def assert_lists_equal(l1, l2):
    assert set(l1) == set(l2)


def card_list(list_of_strings):
    return [*map(Card.from_string, list_of_strings)]


def random_game():
    # not finished
    players = (StrategicBot(1, WHITE_COLOR), StrategicBot(2, BLACK_COLOR))
    game = ChessaoGame(players)
    while not game.mate:
        player = game.current_player
        burn, cards = player.choose_card(game.piles, game.board)
        game.play_cards(cards, burn=burn)
        move = player.choose_move(
            game.possible_moves(), game.board, game.current_card)
        if move:
            game.chess_move(move[0], move[1])
        game.end_move()
