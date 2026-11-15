
"""Compare Expectimax, Greedy, and Random over identical seeds."""

import statistics
import time
import sys
from pathlib import Path

# Add the project root directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from simulation import play_game


NUMBER_OF_GAMES = 50
BASE_SEED = 3000

AGENTS = ("expectimax", "greedy", "random")


def main():
    results = {
        agent: []
        for agent in AGENTS
    }

    total_start = time.perf_counter()

    print("=" * 75)
    print("EXPECTIMAX VS GREEDY VS RANDOM")
    print("=" * 75)
    print(f"Number of games per agent: {NUMBER_OF_GAMES}")
    print("All agents use the same reproducible dice seeds.")
    print()

    for game_index in range(NUMBER_OF_GAMES):

        seed = BASE_SEED + game_index

        print("-" * 75)
        print(f"GAME {game_index + 1}/{NUMBER_OF_GAMES} | Seed: {seed}")

        for agent_type in AGENTS:

            result = play_game(
                agent_type=agent_type,
                seed=seed,
            )

            results[agent_type].append(result)

            print(
                f"{agent_type.capitalize():12}"
                f" | Score: {result['score']:3}"
                f" | Runtime: {result['runtime']:8.3f}s"
            )

    total_time = time.perf_counter() - total_start

    print()
    print("=" * 75)
    print("FINAL COMPARISON")
    print("=" * 75)

    for agent_type in AGENTS:

        scores = [
            result["score"]
            for result in results[agent_type]
        ]

        runtimes = [
            result["runtime"]
            for result in results[agent_type]
        ]

        print(f"\n{agent_type.upper()}")
        print(f"Average score:   {statistics.mean(scores):.2f}")
        print(f"Median score:    {statistics.median(scores):.2f}")
        print(f"Minimum score:   {min(scores)}")
        print(f"Maximum score:   {max(scores)}")
        print(f"Average runtime: {statistics.mean(runtimes):.4f}s")
        print(f"Scores: {scores}")

    # Count wins using the results from identical seeds.
    wins = {
        agent: 0
        for agent in AGENTS
    }

    draws = 0

    for game_index in range(NUMBER_OF_GAMES):

        game_scores = {
            agent: results[agent][game_index]["score"]
            for agent in AGENTS
        }

        highest_score = max(game_scores.values())

        winners = [
            agent
            for agent, score in game_scores.items()
            if score == highest_score
        ]

        if len(winners) == 1:
            wins[winners[0]] += 1
        else:
            draws += 1

    print("\n" + "=" * 75)
    print("WIN COUNTS")
    print("=" * 75)

    for agent_type in AGENTS:
        print(f"{agent_type.capitalize():12}: {wins[agent_type]}")

    print(f"{'Draws':12}: {draws}")

    # Calculate average score differences.
    average_scores = {
        agent: statistics.mean(
            result["score"]
            for result in results[agent]
        )
        for agent in AGENTS
    }

    print("\nAVERAGE SCORE DIFFERENCES")

    print(
        "Expectimax - Greedy: "
        f"{average_scores['expectimax'] - average_scores['greedy']:+.2f}"
    )

    print(
        "Expectimax - Random: "
        f"{average_scores['expectimax'] - average_scores['random']:+.2f}"
    )

    print(
        "Greedy - Random:     "
        f"{average_scores['greedy'] - average_scores['random']:+.2f}"
    )

    print("\n" + "=" * 75)
    print(f"Total comparison time: {total_time:.2f} seconds")
    print("Comparison completed successfully.")


if __name__ == "__main__":
    main()
