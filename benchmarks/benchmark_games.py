
"""Benchmark the Yahtzee agent over multiple complete games."""

import sys
import statistics
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from simulation import play_game


NUMBER_OF_GAMES = 5
BASE_SEED = 1000


def run_benchmark():
    scores = []
    runtimes = []
    total_nodes = 0
    total_outcomes = 0
    total_pruned = 0

    print("=" * 65)
    print("YAHTZEE COMPLETE GAME BENCHMARK")
    print(f"Number of games: {NUMBER_OF_GAMES}")
    print("=" * 65)

    benchmark_start = time.perf_counter()

    for game_number in range(NUMBER_OF_GAMES):

        seed = BASE_SEED + game_number

        print(f"\nRunning game {game_number + 1}/{NUMBER_OF_GAMES}...")

        result = play_game(
            use_expectimax=True,
            enable_pruning=True,
            seed=seed,
        )

        scores.append(result["score"])
        runtimes.append(result["runtime"])

        total_nodes += result["nodes"]
        total_outcomes += result["outcomes"]
        total_pruned += result["pruned"]

        print(f"Score: {result['score']}")
        print(f"Runtime: {result['runtime']:.2f} seconds")
        print(f"Expanded nodes: {result['nodes']:,}")
        print(f"Pruned outcomes: {result['pruned']:,}")

    total_runtime = time.perf_counter() - benchmark_start

    print("\n" + "=" * 65)
    print("FINAL RESULTS")
    print("=" * 65)

    print(f"Games completed: {len(scores)}")
    print(f"Average score: {statistics.mean(scores):.2f}")
    print(f"Highest score: {max(scores)}")
    print(f"Lowest score: {min(scores)}")
    print(f"Median score: {statistics.median(scores):.2f}")
    print(f"Average game runtime: {statistics.mean(runtimes):.2f} seconds")
    print(f"Total benchmark runtime: {total_runtime:.2f} seconds")

    print(f"\nTotal expanded nodes: {total_nodes:,}")
    print(f"Total evaluated outcomes: {total_outcomes:,}")
    print(f"Total pruned outcomes: {total_pruned:,}")

    if total_outcomes + total_pruned > 0:
        pruning_rate = (
            total_pruned /
            (total_outcomes + total_pruned)
        ) * 100

        print(f"Pruning rate: {pruning_rate:.2f}%")

    print("\nIndividual scores:", scores)


if __name__ == "__main__":
    run_benchmark()
