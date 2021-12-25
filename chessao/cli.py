#!/usr/bin/env python
import json
import logging
import pickle
import random
import time
import traceback
from typing import Tuple

import click

from chessao import WHITE_COLOR, BLACK_COLOR, SIMULATION_BUGS_PATH
from chessao.gameplay import ChessaoGame
from chessao.players import gracz
from chessao.utils import GameplayEncoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def dump_pickle(game):
    timestr = time.strftime("%m%d-%H:%M:%S")
    path = SIMULATION_BUGS_PATH / f'{timestr}.pkl'
    with open(path, 'wb') as outfile:
        pickle.dump(game, outfile, pickle.HIGHEST_PROTOCOL)


def dump_error_info(game, error_tb):
    timestr = time.strftime("%m%d-%H:%M:%S")
    path = SIMULATION_BUGS_PATH / f'{timestr}.json'
    data = {
        'starting_deck': game.cards.starting_deck,
        'ledger': game.history.get(),
        'mate': game.mate,
        'stalemate': game.stalemate,
        'error': error_tb,
        'fen': game.board.fen(),
        'current_card': str(game.current_card),
        'current_move': game.current_move,
    }
    with open(path, 'w') as outfile:
        json.dump(data, outfile, indent=4, cls=GameplayEncoder)


def simulate_game(quiet):
    click.secho('Running a simulated game...', fg='green')
    chessao, error = control_loop(quiet)
    if error:
        click.secho(f"Error occured: {error}", fg='red')
        dump_error_info(chessao, error)
    else:
        click.secho("Game finished succesfuly!", fg='green')
        print(chessao)
        print(chessao.board.fen())
        print(f'STALEMATE: {chessao.stalemate}')
        print(f'MATE: {chessao.mate}')
    if not chessao.cards.reshuffled:  # messes up the ledger
        click.secho(f"Dumping info...", fg='blue')
        dump_error_info(chessao, error)
    # dump_pickle(chessao)


def get_cards_to_play(game):
    burn, cards = game.current_player.choose_card(game.piles)
    pile = game.cards.pick_a_pile(cards[-1])
    cards_to_remove = game.current_player.get_three(3, blacklist=cards)
    return burn, cards, pile, cards_to_remove


def control_loop(quiet) -> Tuple[ChessaoGame, str]:
    players = (gracz(1, WHITE_COLOR, name='Adam'),
               gracz(2, BLACK_COLOR, name='Eve'))
    game = ChessaoGame(players)
    moves = 0
    try:
        while not game.finished and moves < 250:
            move = True
            moves += 1
            cards_ok = False
            logger.debug(f"Move {moves}")

            all_moves_per_card = game.all_possible_moves_on_cards(game.current_player.hand, stalemate=False)

            # game loop
            if game.king_of_spades_active():
                game._play_penultimate_card()
            else:
                i = 0
                while not cards_ok:
                    i += 1
                    burn, cards, pile, cards_to_remove = get_cards_to_play(game)
                    if burn:
                        if all_moves_per_card['neutral'] or game.player_should_lose_turn:
                            cards_ok = True
                        else:
                            cards_ok = False
                    else:
                        if all_moves_per_card.get(cards[-1], []):
                            cards_ok = True
                        else:
                            cards_ok = False
                    if i > 100:
                        print("I is super big: ", burn, cards, pile, cards_to_remove, all_moves_per_card)
                        return game, "Stuck in loop"

                possible_jacks = game.possible_jack_choices()
                if possible_jacks:
                    jack = random.choice(possible_jacks)
                else:
                    jack = None

                game.play_cards(cards, pile, burn, jack, cards_to_remove)

            if game.card_is(game.current_card, 'A'):
                if not game.check:
                    game.current_move = []
                    game.swap_players_color()
                    game.add_to_history()
                    continue
            possible_moves = game.possible_moves()
            if game.player_should_lose_turn:
                move = []
            elif not burn and game.card_is(game.current_card, "K", 1):
                move = []
            if possible_moves and move:
                move = game.current_player.choose_move(possible_moves)
            game.chess_move(move, promotion='q')
            game.end_move()

            if len(game.board.all_taken()) < 6:
                print("breaking cause only 5 pieces left")
                break

            # printing
            if not quiet:
                output = f"\rMove {moves}: {game.invert_color(game.to_move)} {move} {cards if not burn else ''}"
                if not burn and cards[-1].rank == 'J':
                    output += f" jack: {jack}"
                if not burn and cards[-1].rank == '3':
                    output += f"{cards_to_remove} | hand: {game.current_player.hand}"
                click.echo(output)
        if game.stalemate and not game.mate:
            logger.debug("STALEMATE")
        return game, ""
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
