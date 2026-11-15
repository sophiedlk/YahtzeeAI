
"""Baseline heuristic evaluation for Yahtzee states."""

from game_state import UPPER_CATEGORIES


# Original expected category scores.
EXPECTED_CATEGORY_SCORES = {
    "ones": 2.1,
    "twos": 4.2,
    "threes": 6.3,
    "fours": 8.4,
    "fives": 10.5,
    "sixes": 12.6,
    "three_of_a_kind": 21.0,
    "four_of_a_kind": 14.0,
    "full_house": 7.5,
    "small_straight": 15.0,
    "large_straight": 8.0,
    "yahtzee": 4.6,
    "chance": 22.0,
}


UPPER_BONUS_TARGET = 63
UPPER_BONUS_POINTS = 35


def clamp(value, minimum=0.0, maximum=1.0):
    """Limit a value to a specified interval."""
    return max(minimum, min(maximum, value))


def estimate_upper_bonus_probability(state):
    """Estimate the probability of obtaining the upper-section bonus."""

    if state.upper_total >= UPPER_BONUS_TARGET:
        return 1.0

    remaining_upper = [
        category
        for category in UPPER_CATEGORIES
        if state.scorecard[category] is None
    ]

    if not remaining_upper:
        return 0.0

    expected_remaining = sum(
        EXPECTED_CATEGORY_SCORES[category]
        for category in remaining_upper
    )

    projected_total = state.upper_total + expected_remaining

    probability = (
        projected_total - UPPER_BONUS_TARGET + 10
    ) / 20

    return clamp(probability)


def estimate_remaining_score(state):
    """Estimate the expected score of unfilled categories."""

    return sum(
        EXPECTED_CATEGORY_SCORES[category]
        for category in state.remaining_categories
    )


def evaluate_state(state):
    """Evaluate a Yahtzee state using the baseline heuristic."""

    if state.is_terminal:
        return float(state.total_score)

    current_score = float(state.total_score)

    remaining_score = estimate_remaining_score(state)

    upper_bonus_probability = estimate_upper_bonus_probability(state)

    expected_upper_bonus = (
        upper_bonus_probability * UPPER_BONUS_POINTS
    )

    return (
        current_score
        + remaining_score
        + expected_upper_bonus
    )
