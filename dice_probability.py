
"""Calculate exact probabilities of rerolling Yahtzee dice."""

from collections import Counter
from fractions import Fraction
from itertools import combinations_with_replacement
from math import factorial


def validate_dice(dice):
    """Validate exactly five dice."""

    if not isinstance(dice, (list, tuple)):
        raise ValueError("Dice must be a list or tuple.")

    if len(dice) != 5:
        raise ValueError("Exactly five dice are required.")

    if any(
        type(die) is not int or not 1 <= die <= 6
        for die in dice
    ):
        raise ValueError("Each die must be an integer from 1 to 6.")


def generate_roll_outcomes(number_of_dice):
    """Generate unique unordered outcomes and exact probabilities."""

    if type(number_of_dice) is not int:
        raise ValueError("number_of_dice must be an integer.")

    if not 0 <= number_of_dice <= 5:
        raise ValueError("number_of_dice must be between 0 and 5.")

    total_ordered_outcomes = 6 ** number_of_dice
    results = []

    for outcome in combinations_with_replacement(
        range(1, 7),
        number_of_dice,
    ):
        counts = Counter(outcome)

        multiplicity = factorial(number_of_dice)

        for count in counts.values():
            multiplicity //= factorial(count)

        probability = Fraction(
            multiplicity,
            total_ordered_outcomes,
        )

        results.append((outcome, probability))

    return tuple(results)


def probability_sum(number_of_dice):
    """Return the sum of all outcome probabilities."""

    return sum(
        probability
        for _, probability in generate_roll_outcomes(number_of_dice)
    )


def generate_reroll_outcomes(current_dice, kept_dice):
    """
    Generate every possible final dice state after a reroll.

    Args:
        current_dice: The five dice currently on the table.
        kept_dice: The values of the dice the agent keeps.

    Returns:
        A tuple of (final_dice, probability) pairs.

        Each final_dice is sorted and contains exactly five dice.
    """

    validate_dice(current_dice)

    if not isinstance(kept_dice, (list, tuple)):
        raise ValueError("kept_dice must be a list or tuple.")

    if any(
        type(die) is not int or not 1 <= die <= 6
        for die in kept_dice
    ):
        raise ValueError("Each kept die must be an integer from 1 to 6.")

    if len(kept_dice) > 5:
        raise ValueError("Cannot keep more than five dice.")

    current_counts = Counter(current_dice)
    kept_counts = Counter(kept_dice)

    # The agent cannot keep dice that are not available.
    for face, count in kept_counts.items():
        if count > current_counts[face]:
            raise ValueError("Cannot keep unavailable dice.")

    number_to_reroll = 5 - len(kept_dice)

    rolled_outcomes = generate_roll_outcomes(number_to_reroll)

    results = []

    for rolled_dice, probability in rolled_outcomes:
        final_dice = tuple(
            sorted(tuple(kept_dice) + rolled_dice)
        )

        results.append((final_dice, probability))

    return tuple(results)
