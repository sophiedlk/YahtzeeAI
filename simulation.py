
"""Simulate complete Yahtzee games with reproducible dice."""

import random
import time
from collections import Counter

from game_state import GameState
from game_engine import apply_reroll, score_turn
from expectimax import ExpectimaxAgent, get_legal_categories
from strategy import generate_keep_actions
from greedy_agent import GreedyAgent

def roll_dice_for_turn(seed, turn, roll_number, indices):
    """
    Generate reproducible dice values.

    Each die depends on the game seed, turn, roll number,
    and its original position.
    """

    values = []

    for index in indices:
        die_seed = (
            seed * 1_000_003
            + turn * 10_007
            + roll_number * 101
            + index * 17
        )

        rng = random.Random(die_seed)
        values.append(rng.randint(1, 6))

    return tuple(values)


def get_kept_indices(current_dice, kept_dice):
    """Convert kept dice values into their original indices."""

    remaining = Counter(kept_dice)
    indices = []

    for index, die in enumerate(current_dice):
        if remaining[die] > 0:
            indices.append(index)
            remaining[die] -= 1

    if any(remaining.values()):
        raise ValueError("The requested kept dice are unavailable.")

    return indices


def random_action(state, legal_categories, rng):
    """Choose a random baseline action."""

    if state.roll < 3 and rng.random() < 0.65:
        kept_dice = rng.choice(
            generate_keep_actions(state.dice)
        )

        return {
            "type": "reroll",
            "keep": kept_dice,
        }

    return {
        "type": "score",
        "category": rng.choice(legal_categories),
    }



def play_game(
    use_expectimax=True,
    enable_pruning=True,
    seed=1,
    agent_type=None,
):
    """Play one complete 13-turn Yahtzee game.

    Supported agent types:
        "expectimax"
        "greedy"
        "random"

    The use_expectimax parameter is retained for compatibility
    with the previous benchmark scripts.
    """

    decision_rng = random.Random(seed ^ 0x5DEECE66D)

    initial_dice = roll_dice_for_turn(
        seed, 1, 1, range(5)
    )

    state = GameState(dice=initial_dice)

    # Preserve compatibility with older calls.
    if agent_type is None:
        agent_type = "expectimax" if use_expectimax else "random"

    if agent_type not in ("expectimax", "greedy", "random"):
        raise ValueError(f"Unknown agent type: {agent_type}")

    agent = None

    if agent_type == "expectimax":
        agent = ExpectimaxAgent(
            enable_pruning=enable_pruning
        )
    elif agent_type == "greedy":
        agent = GreedyAgent()

    total_nodes = 0
    total_outcomes = 0
    total_pruned = 0
    total_greedy_actions = 0
    total_greedy_outcomes = 0
    decisions = 0

    start_time = time.perf_counter()

    while not state.is_terminal:

        legal_categories = get_legal_categories(state)

        if not legal_categories:
            raise RuntimeError(
                "No legal categories in a non-terminal state."
            )

        # Select an action using the chosen agent.
        if agent_type == "expectimax":

            action = agent.choose_action(
                state,
                legal_categories,
            )

            total_nodes += agent.nodes_expanded
            total_outcomes += agent.outcomes_evaluated
            total_pruned += agent.pruned_outcomes

        elif agent_type == "greedy":

            action = agent.choose_action(
                state,
                legal_categories,
            )

            total_greedy_actions += agent.actions_evaluated
            total_greedy_outcomes += agent.outcomes_evaluated

        else:

            action = random_action(
                state,
                legal_categories,
                decision_rng,
            )

        decisions += 1

        # Apply the selected action.
        if action["type"] == "reroll":

            kept_indices = get_kept_indices(
                state.dice,
                action["keep"],
            )

            rerolled_indices = [
                index
                for index in range(5)
                if index not in kept_indices
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

        elif action["type"] == "score":

            state = score_turn(
                state,
                action["category"],
                legal_categories,
            )

            if not state.is_terminal:

                next_dice = roll_dice_for_turn(
                    seed,
                    state.turn,
                    1,
                    range(5),
                )

                state = GameState(
                    dice=next_dice,
                    turn=state.turn,
                    roll=1,
                    scorecard=dict(state.scorecard),
                    upper_total=state.upper_total,
                    yahtzee_bonus=state.yahtzee_bonus,
                )

        else:
            raise ValueError(
                f"Unknown action type: {action['type']}"
            )

    elapsed_time = time.perf_counter() - start_time

    return {
        "agent_type": agent_type,
        "score": state.total_score,
        "upper_total": state.upper_total,
        "upper_bonus": state.upper_bonus,
        "yahtzee_bonus": state.yahtzee_bonus,
        "decisions": decisions,
        "runtime": elapsed_time,
        "nodes": total_nodes,
        "outcomes": total_outcomes,
        "pruned": total_pruned,
        "greedy_actions": total_greedy_actions,
        "greedy_outcomes": total_greedy_outcomes,
        "scorecard": dict(state.scorecard),
    }
