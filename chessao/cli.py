#!/usr/bin/env python
import json
import random
import time
import traceback

import click

from chessao import WHITE_COLOR, BLACK_COLOR
from chessao.gameplay import ChessaoGame
from chessao.players import gracz


def dump_error_info(game):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    path = f'/Users/Tadeo/dev/TAD/szachao/tests/simulation_bugs/{timestr}.json'
    data = {
        'starting_deck': game.cards.starting_deck,
        'ledger': game.history.get(),
        'mate': game.mate,
        'stalemate': game.stalemate
    }
    with open(path, 'w') as outfile:
        json.dump(data, outfile)


def simulate_game(quiet):
    click.secho('Running a simulated game...', fg='green')
    chessao, error = control_loop(quiet)
    if error:
        click.secho(f"Error occured: {error}", fg='red')
    else:
        click.secho("Game finished succesfuly!", fg='green')
        print(chessao)
        print(f'STALEMATE: {chessao.stalemate}')
        print(f'MATE: {chessao.mate}')
    click.secho(f"Dumping info...", fg='blue')
    dump_error_info(chessao)


def control_loop(quiet):
    players = (gracz(1, WHITE_COLOR, name='Adam'),
               gracz(2, BLACK_COLOR, name='Eve'))
    game = ChessaoGame(players)
    moves = 0
    try:
        while not game.finished:
            move = True
            moves += 1
            burn, cards = game.current_player.choose_card(game.piles)
            pile = game.cards.pick_a_pile(cards[-1])
            cards_to_remove = game.current_player.get_three(3, blacklist=cards)
            jack = random.choice(game.possible_jack_choices())
            if game.king_of_spades_active():
                game._handle_king_of_spades()
            else:
                game.play_cards(cards, pile, burn, jack, cards_to_remove)

            if game.card_is(game.current_card, 'A'):
                if not game.check:
                    game.swap_players_color()
                    game.add_to_history()
                    continue
            if game.card_is(game.current_card, 'K', 1):
                move = []
            if game.player_should_lose_turn:
                possible_moves = None
            else:
                possible_moves = game.possible_moves()
            if possible_moves and move:
                move = game.current_player.choose_move(possible_moves)
                game.chess_move(move[0], move[1])
            else:
                move = []
                game.current_move = []

            game.end_move()
            if not quiet:
                output = f"\rMove {moves}: {game.invert_color(game.to_move)} {move} {cards if not burn else ''}"
                if not burn and cards[-1].rank == 'J':
                    output += f" jack: {jack}"
                if not burn and cards[-1].rank == '3':
                    output += f"{cards_to_remove} | hand: {game.current_player.hand}"
                click.echo(output)
        return game, None
    except Exception as e:
        return game, traceback.format_exc()


@click.command(help="Chessao CLI")
@click.option('--simulate', is_flag=True, default=False,
              help='Simulate a chessao game between two AI players')
@click.option('--quiet', is_flag=True, default=False,
              help='No output during simulation')
@click.option('--number', '-n', default=1, help="Number of games to simulate")
def cli(simulate, quiet, number):
    """
    Chessao CLI.
    """
    # erase = '\x1b[1A\x1b[2K' * 16
    if simulate:
        for _ in range(number):
            simulate_game(quiet)


if __name__ == '__main__':
    cli()
