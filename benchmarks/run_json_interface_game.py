
"""Run a complete Yahtzee game through the JSON interface."""

import argparse
import sys
import time
from pathlib import Path

# Make the project root importable.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from expectimax import ExpectimaxAgent, get_legal_categories
from game_engine import apply_reroll, score_turn
from game_state import CATEGORIES, GameState
from json_interface import process_request
from simulation import roll_dice_for_turn


def build_request(state, legal_categories):
    """Build one request using the competition input format."""

    return {
        "version": 1,
        "turn": state.turn,
        "roll": state.roll,
        "dice": list(state.dice),
        "scorecard": dict(state.scorecard),
        "upper_total": state.upper_total,
        "yahtzee_bonus": state.yahtzee_bonus,
        "legal_categories": list(legal_categories),
    }


def validate_response(response, state, legal_categories):
    """Validate the response against the competition protocol."""

    if not isinstance(response, dict):
        raise ValueError("Response must be a JSON object.")

    action = response.get("action")

    if action == "reroll":
        if set(response) != {"action", "indices"}:
            raise ValueError("Invalid reroll response fields.")

        if state.roll >= 3:
            raise ValueError("Reroll is forbidden after roll 3.")

        indices = response["indices"]

        if not isinstance(indices, list):
            raise ValueError("Reroll indices must be a list.")

        if any(type(index) is not int for index in indices):
            raise ValueError("Reroll indices must be integers.")

        if len(indices) != len(set(indices)):
            raise ValueError("Duplicate reroll indices.")

        if any(index < 0 or index > 4 for index in indices):
            raise ValueError("Reroll index must be between 0 and 4.")

        return

    if action == "score":
        if set(response) != {"action", "category"}:
            raise ValueError("Invalid score response fields.")

        category = response["category"]

        if category not in legal_categories:
            raise ValueError("Selected category is not legal.")

        return

    raise ValueError(f"Unknown response action: {action}")


def play_json_game(seed=2026, enable_pruning=True):
    """Play one complete game using the competition JSON interface."""

    agent = ExpectimaxAgent(enable_pruning=enable_pruning)

    initial_dice = roll_dice_for_turn(
        seed,
        turn=1,
        roll_number=1,
        indices=range(5),
    )

    state = GameState(dice=initial_dice)

    decisions = 0
    rerolls = 0
    scoring_actions = 0

    total_nodes = 0
    total_outcomes = 0
    total_pruned = 0

    start_time = time.perf_counter()

    while not state.is_terminal:

        legal_categories = get_legal_categories(state)

        if not legal_categories:
            raise RuntimeError(
                f"No legal categories at turn {state.turn}."
            )

        # Build the exact request structure used by the competition.
        request = build_request(state, legal_categories)

        # Run the agent through the JSON interface.
        response = process_request(request, agent)

        # Validate the competition response.
        validate_response(
            response,
            state,
            legal_categories,
        )

        decisions += 1

        total_nodes += agent.nodes_expanded
        total_outcomes += agent.outcomes_evaluated
        total_pruned += agent.pruned_outcomes

        if response["action"] == "reroll":

            rerolls += 1

            rerolled_indices = response["indices"]

            kept_indices = [
                index
                for index in range(5)
                if index not in rerolled_indices
            ]

            new_dice = roll_dice_for_turn(
                seed,
                state.turn,
                state.roll + 1,
                rerolled_indices,
            )

            state = apply_reroll(
                state,
                kept_indices,
                new_dice,
            )

        else:

            scoring_actions += 1

            category = response["category"]

            scored_state = score_turn(
                state,
                category,
                legal_categories,
            )

            if scored_state.is_terminal:
                state = scored_state

            else:
                next_dice = roll_dice_for_turn(
                    seed,
                    scored_state.turn,
                    1,
                    range(5),
                )

                state = GameState(
                    dice=next_dice,
                    turn=scored_state.turn,
                    roll=1,
                    scorecard=dict(scored_state.scorecard),
                    upper_total=scored_state.upper_total,
                    yahtzee_bonus=scored_state.yahtzee_bonus,
                )

    elapsed = time.perf_counter() - start_time

    # Final integrity checks.
    if not state.is_terminal:
        raise AssertionError("Game did not finish.")

    if set(state.scorecard) != set(CATEGORIES):
        raise AssertionError("Invalid final scorecard.")

    if any(
        state.scorecard[category] is None
        for category in CATEGORIES
    ):
        raise AssertionError("Some scorecard categories remain empty.")

    if scoring_actions != 13:
        raise AssertionError(
            f"Expected 13 scoring actions, got {scoring_actions}."
        )

    if decisions != rerolls + scoring_actions:
        raise AssertionError("Decision counter mismatch.")

    return {
        "seed": seed,
        "score": state.total_score,
        "upper_total": state.upper_total,
        "upper_bonus": state.upper_bonus,
        "yahtzee_bonus": state.yahtzee_bonus,
        "decisions": decisions,
        "rerolls": rerolls,
        "scoring_actions": scoring_actions,
        "nodes": total_nodes,
        "outcomes": total_outcomes,
        "pruned": total_pruned,
        "runtime": elapsed,
        "scorecard": state.scorecard,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--no-pruning", action="store_true")
    args = parser.parse_args()

    print("Starting JSON interface full-game test...")
    print(f"Seed: {args.seed}")
    print(f"Pruning enabled: {not args.no_pruning}")
    print()

    result = play_json_game(
        seed=args.seed,
        enable_pruning=not args.no_pruning,
    )

    print("=" * 55)
    print("JSON INTERFACE FULL GAME TEST")
    print("=" * 55)

    print(f"Seed:              {result['seed']}")
    print(f"Final score:       {result['score']}")
    print(f"Upper total:       {result['upper_total']}")
    print(f"Upper bonus:       {result['upper_bonus']}")
    print(f"Yahtzee bonus:     {result['yahtzee_bonus']}")
    print(f"Total decisions:   {result['decisions']}")
    print(f"Reroll actions:    {result['rerolls']}")
    print(f"Scoring actions:   {result['scoring_actions']}")
    print(f"Expanded nodes:    {result['nodes']}")
    print(f"Evaluated outcomes:{result['outcomes']}")
    print(f"Pruned outcomes:   {result['pruned']}")
    print(f"Runtime:           {result['runtime']:.2f} seconds")

    print()
    print("FINAL SCORECARD")

    for category in CATEGORIES:
        print(f"{category:20s}: {result['scorecard'][category]}")

    print()
    print("SUCCESS: Complete 13-turn JSON game finished.")
    print("All 13 categories were filled.")
    print("All responses passed protocol validation.")


if __name__ == "__main__":
    main()
