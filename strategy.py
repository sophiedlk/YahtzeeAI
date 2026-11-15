
"""Generate possible dice-keeping actions for the Yahtzee agent."""

from collections import Counter
from itertools import product


def validate_dice(dice):
    """Validate a collection of exactly five dice."""

    if len(dice) != 5:
        raise ValueError("Exactly five dice are required.")

    if any(
        type(die) is not int or not 1 <= die <= 6
        for die in dice
    ):
        raise ValueError("Each die must be an integer from 1 to 6.")


def generate_keep_actions(dice):
    """
    Generate all unique ways to keep some of the five dice.

    Each action is a sorted tuple containing the values
    of the dice that the agent wants to keep.

    Keeping all five dice is excluded because it does not
    produce a new roll. Scoring the current dice is a
    separate decision handled by the search algorithm.

    Examples:
        (1, 1, 2) means keep two 1s and one 2.
        () means reroll all five dice.
    """

    validate_dice(dice)

    counts = Counter(dice)

    # Number of available dice for each face.
    available_counts = [
        counts[face]
        for face in range(1, 7)
    ]

    actions = []

    # Generate every possible count of kept dice
    # for faces 1 through 6.
    ranges = [
        range(count + 1)
        for count in available_counts
    ]

    for kept_counts in product(*ranges):
        kept_dice = tuple(
            face
            for face, count in enumerate(kept_counts, start=1)
            for _ in range(count)
        )

        # Exclude keeping all five dice.
        if len(kept_dice) == 5:
            continue

        actions.append(kept_dice)

    return tuple(actions)
