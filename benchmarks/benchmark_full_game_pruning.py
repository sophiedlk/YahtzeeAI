
"""Compare full-game Expectimax with and without pruning."""

import statistics
import time
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from simulation import play_game

NUMBER_OF_GAMES = 5
BASE_SEED = 4000


def main():
    normal_results = []
    pruned_results = []

    start = time.perf_counter()

    print("=" * 70)
    print("FULL GAME PRUNING COMPARISON")
    print("=" * 70)

    for index in range(NUMBER_OF_GAMES):
        seed = BASE_SEED + index

        print(f"\nGame {index + 1}/{NUMBER_OF_GAMES}, seed={seed}")

        normal = play_game(
            agent_type="expectimax",
            enable_pruning=False,
            seed=seed,
        )

        pruned = play_game(
            agent_type="expectimax",
            enable_pruning=True,
            seed=seed,
        )

        normal_results.append(normal)
        pruned_results.append(pruned)

        print(
            f"Without pruning: score={normal['score']}, "
            f"time={normal['runtime']:.2f}s, "
            f"nodes={normal['nodes']}, "
            f"outcomes={normal['outcomes']}"
        )

        print(
            f"With pruning:    score={pruned['score']}, "
            f"time={pruned['runtime']:.2f}s, "
            f"nodes={pruned['nodes']}, "
            f"outcomes={pruned['outcomes']}, "
            f"pruned={pruned['pruned']}"
        )

        if normal["score"] != pruned["score"]:
            print("WARNING: Final scores are different!")

    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    normal_time = statistics.mean(
        result["runtime"] for result in normal_results
    )
    pruned_time = statistics.mean(
        result["runtime"] for result in pruned_results
    )

    normal_nodes = statistics.mean(
        result["nodes"] for result in normal_results
    )
    pruned_nodes = statistics.mean(
        result["nodes"] for result in pruned_results
    )

    normal_outcomes = statistics.mean(
        result["outcomes"] for result in normal_results
    )
    pruned_outcomes = statistics.mean(
        result["outcomes"] for result in pruned_results
    )

    total_pruned = sum(
        result["pruned"] for result in pruned_results
    )

    print(
        f"Average score without pruning: "
        f"{statistics.mean(r['score'] for r in normal_results):.2f}"
    )
    print(
        f"Average score with pruning:    "
        f"{statistics.mean(r['score'] for r in pruned_results):.2f}"
    )

    print(f"\nAverage runtime without pruning: {normal_time:.2f}s")
    print(f"Average runtime with pruning:    {pruned_time:.2f}s")

    print(f"\nAverage nodes without pruning: {normal_nodes:.0f}")
    print(f"Average nodes with pruning:    {pruned_nodes:.0f}")

    print(f"\nAverage outcomes without pruning: {normal_outcomes:.0f}")
    print(f"Average outcomes with pruning:    {pruned_outcomes:.0f}")

    if normal_outcomes:
        reduction = (
            (normal_outcomes - pruned_outcomes)
            / normal_outcomes
        ) * 100
        print(f"\nOutcome reduction: {reduction:.2f}%")

    if pruned_time > 0:
        print(f"Runtime speedup: {normal_time / pruned_time:.2f}x")

    print(f"Total pruned outcomes: {total_pruned}")

    print("\n" + "=" * 70)
    print(f"Total experiment time: {time.perf_counter() - start:.2f}s")
    print("Experiment completed.")


if __name__ == "__main__":
    main()
