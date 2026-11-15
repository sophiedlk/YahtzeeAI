
"""Compare Expectimax performance with and without pruning."""

import sys
import time
import statistics
from pathlib import Path

# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from game_state import GameState
from expectimax import ExpectimaxAgent


NUMBER_OF_RUNS = 3


TEST_CASES = [
    {
        "name": "Mixed dice",
        "dice": (1, 2, 3, 4, 6),
    },
    {
        "name": "Repeated dice",
        "dice": (2, 2, 3, 3, 5),
    },
    {
        "name": "Three of a kind",
        "dice": (4, 4, 4, 2, 6),
    },
    {
        "name": "Four of a kind",
        "dice": (5, 5, 5, 5, 2),
    },
]


def run_agent(state, enable_pruning):
    """Run one agent and measure its execution time."""

    agent = ExpectimaxAgent(
        enable_pruning=enable_pruning
    )

    start_time = time.perf_counter()

    action = agent.choose_action(state)

    elapsed_time = time.perf_counter() - start_time

    return {
        "action": action,
        "elapsed_time": elapsed_time,
        "nodes_expanded": agent.nodes_expanded,
        "outcomes_evaluated": agent.outcomes_evaluated,
        "pruned_outcomes": agent.pruned_outcomes,
    }


def median_runtime(state, enable_pruning):
    """Measure the median runtime across repeated executions."""

    results = []

    for _ in range(NUMBER_OF_RUNS):
        results.append(
            run_agent(state, enable_pruning)
        )

    runtime = statistics.median(
        result["elapsed_time"]
        for result in results
    )

    return runtime, results[-1]


def compare_agents(test_case):
    """Compare pruned and unpruned agents on the same state."""

    state = GameState(
        dice=test_case["dice"],
        roll=2,
    )

    print("\n" + "=" * 65)
    print(f"Test case: {test_case['name']}")
    print(f"Dice: {state.dice}")
    print(f"Roll: {state.roll}")
    print("=" * 65)

    # Run without pruning.
    plain_runtime, plain_result = median_runtime(
        state,
        enable_pruning=False,
    )

    # Run with pruning.
    pruned_runtime, pruned_result = median_runtime(
        state,
        enable_pruning=True,
    )

    plain_action = plain_result["action"]
    pruned_action = pruned_result["action"]

    print("\nWITHOUT PRUNING")
    print("-" * 40)

    print(f"Action: {plain_action}")
    print(f"Median runtime: {plain_runtime:.6f} seconds")
    print(f"Expanded nodes: {plain_result['nodes_expanded']}")
    print(
        f"Evaluated outcomes: "
        f"{plain_result['outcomes_evaluated']}"
    )
    print(f"Pruned outcomes: {plain_result['pruned_outcomes']}")

    print("\nWITH PRUNING")
    print("-" * 40)

    print(f"Action: {pruned_action}")
    print(f"Median runtime: {pruned_runtime:.6f} seconds")
    print(f"Expanded nodes: {pruned_result['nodes_expanded']}")
    print(
        f"Evaluated outcomes: "
        f"{pruned_result['outcomes_evaluated']}"
    )
    print(f"Pruned outcomes: {pruned_result['pruned_outcomes']}")

    # Verify that pruning does not change the optimal decision.
    if plain_action["type"] != pruned_action["type"]:
        raise AssertionError("The selected action types differ.")

    if plain_action["type"] == "score":
        if plain_action["category"] != pruned_action["category"]:
            raise AssertionError("The selected categories differ.")

    if plain_action["type"] == "reroll":
        if plain_action["keep"] != pruned_action["keep"]:
            raise AssertionError("The selected dice differ.")

    if abs(
        plain_action["value"] - pruned_action["value"]
    ) > 1e-8:
        raise AssertionError("The selected action values differ.")

    # Calculate the reduction in evaluated outcomes.
    plain_count = plain_result["outcomes_evaluated"]
    pruned_count = pruned_result["outcomes_evaluated"]

    if plain_count:
        reduction = (
            (plain_count - pruned_count)
            / plain_count
            * 100
        )
    else:
        reduction = 0.0

    print("\nCOMPARISON")
    print("-" * 40)

    print("Decision: IDENTICAL")
    print("Decision value: IDENTICAL")
    print(f"Outcome evaluation reduction: {reduction:.2f}%")

    if pruned_runtime > 0:
        speedup = plain_runtime / pruned_runtime
        print(f"Runtime speedup: {speedup:.2f}x")

    return {
        "name": test_case["name"],
        "plain_runtime": plain_runtime,
        "pruned_runtime": pruned_runtime,
        "plain_outcomes": plain_count,
        "pruned_outcomes": pruned_count,
        "pruned_count": pruned_result["pruned_outcomes"],
        "reduction": reduction,
    }


def main():
    """Run all benchmark cases."""

    all_results = []

    print("YAHTZEE EXPECTIMAX PRUNING BENCHMARK")
    print(f"Runs per configuration: {NUMBER_OF_RUNS}")

    for test_case in TEST_CASES:
        result = compare_agents(test_case)
        all_results.append(result)


    print("\n\nFINAL SUMMARY")
    print("=" * 105)

    print(
        f"{'Case':<20}"
        f"{'Plain time':>13}"
        f"{'Pruned time':>13}"
        f"{'Plain outcomes':>17}"
        f"{'Pruned outcomes':>18}"
        f"{'Reduction':>13}"
    )

    for result in all_results:
        print(
            f"{result['name']:<20}"
            f"{result['plain_runtime']:>13.6f}"
            f"{result['pruned_runtime']:>13.6f}"
            f"{result['plain_outcomes']:>17}"
            f"{result['pruned_outcomes']:>18}"
            f"{result['reduction']:>12.2f}%"
        )

    print("\nAll benchmark cases completed successfully.")

if __name__ == "__main__":
    main()
