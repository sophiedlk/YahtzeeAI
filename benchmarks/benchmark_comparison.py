
"""Compare Expectimax against a random Yahtzee agent."""

import sys
import statistics
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from simulation import play_game


NUMBER_OF_GAMES = 50
BASE_SEED = 2000


def run_comparison():

    expectimax_scores = []
    random_scores = []

    expectimax_times = []
    random_times = []

    wins = 0
    draws = 0
    losses = 0

    total_start = time.perf_counter()

    print("=" * 72)
    print("EXPECTIMAX VS RANDOM AGENT")
    print(f"Number of games: {NUMBER_OF_GAMES}")
    print("Both agents use the same reproducible dice conditions.")
    print("=" * 72)

    for game_number in range(NUMBER_OF_GAMES):

        seed = BASE_SEED + game_number

        print(
            f"\nGame {game_number + 1}/{NUMBER_OF_GAMES}"
            f" | Seed: {seed}"
        )

        expectimax_result = play_game(
            use_expectimax=True,
            enable_pruning=True,
            seed=seed,
        )

        random_result = play_game(
            use_expectimax=False,
            seed=seed,
        )

        expectimax_score = expectimax_result["score"]
        random_score = random_result["score"]

        expectimax_scores.append(expectimax_score)
        random_scores.append(random_score)

        expectimax_times.append(
            expectimax_result["runtime"]
        )

        random_times.append(
            random_result["runtime"]
        )

        if expectimax_score > random_score:
            wins += 1
            result = "EXPECTIMAX WINS"

        elif expectimax_score < random_score:
            losses += 1
            result = "RANDOM WINS"

        else:
            draws += 1
            result = "DRAW"

        print(f"Expectimax score: {expectimax_score}")
        print(f"Random score:     {random_score}")
        print(f"Score difference: {expectimax_score - random_score:+d}")
        print(f"Result: {result}")

        print(
            f"Expectimax time: "
            f"{expectimax_result['runtime']:.2f} seconds"
        )

        print(
            f"Random time: "
            f"{random_result['runtime']:.4f} seconds"
        )

    total_runtime = time.perf_counter() - total_start

    print("\n" + "=" * 72)
    print("FINAL COMPARISON")
    print("=" * 72)

    print(
        f"Expectimax average score: "
        f"{statistics.mean(expectimax_scores):.2f}"
    )

    print(
        f"Random average score: "
        f"{statistics.mean(random_scores):.2f}"
    )

    print(
        f"Average score difference: "
        f"{statistics.mean(expectimax_scores) - statistics.mean(random_scores):+.2f}"
    )

    print(f"\nExpectimax wins: {wins}")
    print(f"Random wins:     {losses}")
    print(f"Draws:           {draws}")

    print(
        f"\nExpectimax average runtime: "
        f"{statistics.mean(expectimax_times):.2f} seconds"
    )

    print(
        f"Random average runtime: "
        f"{statistics.mean(random_times):.4f} seconds"
    )

    print(f"\nTotal comparison time: {total_runtime:.2f} seconds")

    print("\nExpectimax scores:", expectimax_scores)
    print("Random scores:    ", random_scores)

    print("\nComparison completed successfully.")


if __name__ == "__main__":
    run_comparison()
