
"""Compare Yahtzee heuristic decisions using Expectimax."""

import sys
import time
import statistics
import importlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import expectimax
import simulation


NUMBER_OF_GAMES = 20
BASE_SEED = 6000


def activate_heuristic(module_name):
    """Load a heuristic and reload Expectimax."""

    heuristic_module = importlib.import_module(module_name)
    sys.modules["heuristic"] = heuristic_module

    importlib.reload(expectimax)

    simulation.ExpectimaxAgent = expectimax.ExpectimaxAgent
    simulation.get_legal_categories = expectimax.get_legal_categories



def install_decision_recorder():
    """Record every decision made by the active Expectimax agent."""

    original_choose_action = expectimax.ExpectimaxAgent.choose_action

    def recorded_choose_action(agent, state, *args, **kwargs):
        action = original_choose_action(
            agent, state, *args, **kwargs
        )

        record = {
            "turn": state.turn,
            "roll": state.roll,
            "dice": tuple(state.dice),
            "scorecard": tuple(sorted(state.scorecard.items())),
            "action": repr(action),
        }

        agent.decision_trace.append(record)

        return action

    expectimax.ExpectimaxAgent.choose_action = recorded_choose_action
    simulation.ExpectimaxAgent = expectimax.ExpectimaxAgent


def run_games(module_name, label):

    activate_heuristic(module_name)
    install_decision_recorder()

    scores = []
    runtimes = []
    nodes = []
    outcomes = []
    pruned = []
    traces = {}

    print("\n" + "=" * 75)
    print(f"RUNNING: {label}")
    print(f"Heuristic module: {module_name}")
    print(f"Number of games: {NUMBER_OF_GAMES}")
    print(f"Base seed: {BASE_SEED}")
    print("=" * 75)

    total_start = time.perf_counter()

    for index in range(NUMBER_OF_GAMES):

        seed = BASE_SEED + index

        print(f"\nGame {index + 1}/{NUMBER_OF_GAMES} | Seed: {seed}")

        # A fresh trace for this game.
        decision_trace = []

        # Attach the trace to the agent class.
        expectimax.ExpectimaxAgent.decision_trace = decision_trace

        result = simulation.play_game(
            agent_type="expectimax",
            enable_pruning=True,
            seed=seed,
        )

        scores.append(result["score"])
        runtimes.append(result["runtime"])
        nodes.append(result["nodes"])
        outcomes.append(result["outcomes"])
        pruned.append(result["pruned"])

        traces[seed] = list(decision_trace)

        print(f"Score: {result['score']}")
        print(f"Runtime: {result['runtime']:.2f} seconds")
        print(f"Expanded nodes: {result['nodes']}")
        print(f"Evaluated outcomes: {result['outcomes']}")
        print(f"Pruned outcomes: {result['pruned']}")
        print(f"Recorded decisions: {len(decision_trace)}")

    total_runtime = time.perf_counter() - total_start

    summary = {
        "label": label,
        "scores": scores,
        "average_score": statistics.mean(scores),
        "median_score": statistics.median(scores),
        "average_runtime": statistics.mean(runtimes),
        "average_nodes": statistics.mean(nodes),
        "average_outcomes": statistics.mean(outcomes),
        "average_pruned": statistics.mean(pruned),
        "total_runtime": total_runtime,
        "traces": traces,
    }

    return summary


def compare_decisions(baseline, improved):

    print("\n" + "=" * 75)
    print("DECISION-BY-DECISION COMPARISON")
    print("=" * 75)

    total_decisions = 0
    different_decisions = 0
    identical_decisions = 0

    for seed in sorted(baseline["traces"]):

        old_trace = baseline["traces"][seed]
        new_trace = improved["traces"][seed]

        common_length = min(len(old_trace), len(new_trace))

        game_differences = 0

        print(f"\nSeed: {seed}")
        print(f"Baseline decisions: {len(old_trace)}")
        print(f"Improved decisions: {len(new_trace)}")

        for index in range(common_length):

            old = old_trace[index]
            new = new_trace[index]

            total_decisions += 1

            if old["action"] == new["action"]:
                identical_decisions += 1
            else:
                different_decisions += 1
                game_differences += 1

                print(f"\n  Different decision #{index + 1}")
                print(f"  Turn: {old['turn']}")
                print(f"  Roll: {old['roll']}")
                print(f"  Dice: {old['dice']}")
                print(f"  Baseline action: {old['action']}")
                print(f"  Improved action: {new['action']}")

        print(f"Different actions in this game: {game_differences}")

        if len(old_trace) != len(new_trace):
            print("WARNING: Decision trace lengths are different.")

    print("\n" + "=" * 75)
    print("DECISION COMPARISON SUMMARY")
    print("=" * 75)

    print(f"Total compared decisions: {total_decisions}")
    print(f"Identical decisions: {identical_decisions}")
    print(f"Different decisions: {different_decisions}")

    if total_decisions:
        percentage = 100 * different_decisions / total_decisions
        print(f"Decision difference percentage: {percentage:.2f}%")


def print_comparison(baseline, improved):

    print("\n" + "=" * 75)
    print("HEURISTIC PERFORMANCE COMPARISON")
    print("=" * 75)

    print(f"\nNumber of games: {NUMBER_OF_GAMES}")
    print(f"Seeds: {BASE_SEED} to {BASE_SEED + NUMBER_OF_GAMES - 1}")

    print("\nAverage scores:")
    print(f"Baseline: {baseline['average_score']:.2f}")
    print(f"Improved: {improved['average_score']:.2f}")

    print(
        "Score difference: "
        f"{improved['average_score'] - baseline['average_score']:+.2f}"
    )

    print("\nAverage runtime:")
    print(f"Baseline: {baseline['average_runtime']:.2f} seconds")
    print(f"Improved: {improved['average_runtime']:.2f} seconds")

    print("\nAverage expanded nodes:")
    print(f"Baseline: {baseline['average_nodes']:.0f}")
    print(f"Improved: {improved['average_nodes']:.0f}")

    print("\nIndividual game scores:")
    print("Baseline:", baseline["scores"])
    print("Improved:", improved["scores"])


def main():

    print("YAHTZEE HEURISTIC DECISION BENCHMARK")
    print("Both versions use Expectimax with pruning.")
    print("Both versions use identical seeds and dice generation.")

    baseline = run_games(
        "heuristic_baseline",
        "BASELINE HEURISTIC",
    )

    improved = run_games(
        "heuristic",
        "IMPROVED HEURISTIC",
    )

    print_comparison(baseline, improved)
    compare_decisions(baseline, improved)

    print("\nComparison completed.")


if __name__ == "__main__":
    main()
