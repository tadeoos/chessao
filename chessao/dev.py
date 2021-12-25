import statistics
import time

from flask import Flask, after_this_request

from chessao.cli import control_loop

app = Flask(__name__)


def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/")
def hello_world():
    @after_this_request
    def add_header(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    i = 0
    error = None
    times_took = []
    while not error and i < 100:
        start = time.time()
        chessao, error = control_loop(quiet=True)
        took = time.time() - start
        i += 1
        times_took.append(took)
        print(f"Simulated game {i}. Took {took:.2f}s")

    mean_simulation_time = statistics.mean(times_took)
    print(f"Mean simulation time: {mean_simulation_time:.2f} seconds")
    resp = {
        "error": error,
        # "fens": chessao.history.get_fens(),
        "game": repr(chessao),
        "verbose_story": [record.to_json() for record in chessao.history.ledger[1:]]
    }
    return resp
