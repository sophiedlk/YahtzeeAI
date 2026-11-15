
"""Game engine for applying Yahtzee actions and updating states."""

from copy import deepcopy

from game_state import GameState, CATEGORIES, UPPER_CATEGORIES
from scoring import score_category
from yahtzee_rules import (
    get_yahtzee_bonus,
    is_joker_active,
    joker_score,
)


def apply_reroll(state, kept_indices, new_dice):
    """
    Apply one reroll to a game state.

    kept_indices:
        Indices of dice that the agent wants to keep.

    new_dice:
        Values of the newly rolled dice.

    Returns:
        A new GameState. The original state is unchanged.
    """

    if state.roll >= 3:
        raise ValueError("No rerolls are allowed after roll 3.")

    if not isinstance(kept_indices, (list, tuple, set)):
        raise ValueError("kept_indices must be a list, tuple, or set.")

    kept_indices = list(kept_indices)

    if any(type(index) is not int for index in kept_indices):
        raise ValueError("Die indices must be integers.")

    if len(kept_indices) != len(set(kept_indices)):
        raise ValueError("Duplicate die indices are not allowed.")

    if any(not 0 <= index < 5 for index in kept_indices):
        raise ValueError("Die indices must be between 0 and 4.")

    if not isinstance(new_dice, (list, tuple)):
        raise ValueError("new_dice must be a list or tuple.")

    rerolled_indices = [
        index for index in range(5)
        if index not in kept_indices
    ]

    if len(new_dice) != len(rerolled_indices):
        raise ValueError(
            "The number of new dice must match the number of rerolled dice."
        )

    if any(
        type(die) is not int or not 1 <= die <= 6
        for die in new_dice
    ):
        raise ValueError("Each new die must be an integer from 1 to 6.")

    updated_dice = list(state.dice)

    for index, new_value in zip(rerolled_indices, new_dice):
        updated_dice[index] = new_value

    new_state = deepcopy(state)
    new_state.dice = tuple(updated_dice)
    new_state.roll += 1

    return new_state


def score_turn(state, category, legal_categories):
    """
    Score the current dice in one legal empty category.

    Returns:
        A new GameState with the scorecard updated.
        The original state remains unchanged.
    """

    if category not in CATEGORIES:
        raise ValueError(f"Unknown category: {category}")

    if not isinstance(legal_categories, (list, tuple, set)):
        raise ValueError("legal_categories must be a list, tuple, or set.")

    if category not in legal_categories:
        raise ValueError("The selected category is not legal.")

    if state.scorecard[category] is not None:
        raise ValueError("The selected category is already filled.")

    # Apply Joker rules when a previous Yahtzee exists.
    if is_joker_active(state.dice, state.scorecard):
        points = joker_score(
            state.dice,
            category,
            state.scorecard,
        )
    else:
        points = score_category(state.dice, category)

    # Make an independent copy before changing the scorecard.
    new_state = deepcopy(state)

    new_state.scorecard[category] = points

    # Update the upper section total.
    if category in UPPER_CATEGORIES:
        new_state.upper_total += points

    # Add the 100-point bonus for an additional Yahtzee.
    new_state.yahtzee_bonus += get_yahtzee_bonus(
        state.dice,
        state.scorecard,
    )

    # Prepare the next turn.
    new_state.roll = 1

    if not new_state.is_terminal:
        if state.turn >= 13:
            raise ValueError(
                "A non-terminal game cannot continue after turn 13."
            )

        new_state.turn += 1

    return new_state
