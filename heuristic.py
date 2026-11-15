
"""Heuristic evaluation for Yahtzee states.

The heuristic estimates the value of unfilled categories using
expected scores from a fresh turn with up to three dice rolls.

It considers:
- Expected scores of upper-section categories.
- Expected scores of combination categories.
- Expected score of Chance.
- Probability of reaching the upper-section bonus.
"""

import math

from game_state import CATEGORIES, UPPER_CATEGORIES


# ============================================================
# Expected scores for a fresh turn
# ============================================================

UPPER_EXPECTED_SCORES = {
    "ones": 2.1,
    "twos": 4.2,
    "threes": 6.3,
    "fours": 8.4,
    "fives": 10.5,
    "sixes": 12.6,
}


# Approximate variances for upper-section scores.
UPPER_SCORE_VARIANCES = {
    "ones": 1.7,
    "twos": 3.4,
    "threes": 5.1,
    "fours": 6.8,
    "fives": 8.5,
    "sixes": 10.2,
}


# Approximate probability of completing each combination
# during a fresh turn with up to three rolls.
#
# Format:
# category: (completion_probability, reward)

COMBINATION_OPPORTUNITIES = {
    "three_of_a_kind": (0.70, 30),
    "four_of_a_kind": (0.4667, 30),
    "full_house": (0.30, 25),
    "small_straight": (0.50, 30),
    "large_straight": (0.20, 40),
    "yahtzee": (0.092, 50),
}


CHANCE_EXPECTED_SCORE = 22.0


# ============================================================
# Constants used by Expectimax and pruning
# ============================================================

EXPECTED_CATEGORY_SCORES = {
    **UPPER_EXPECTED_SCORES,
    "three_of_a_kind": 0.70 * 30,
    "four_of_a_kind": 0.4667 * 30,
    "full_house": 0.30 * 25,
    "small_straight": 0.50 * 30,
    "large_straight": 0.20 * 40,
    "yahtzee": 0.092 * 50,
    "chance": CHANCE_EXPECTED_SCORE,
}


UPPER_BONUS_TARGET = 63
UPPER_BONUS_POINTS = 35


# ============================================================
# Utility functions
# ============================================================

def clamp(value, minimum=0.0, maximum=1.0):
    """Limit a value to a specified interval."""
    return max(minimum, min(maximum, value))


def normal_cdf(value):
    """Calculate the cumulative distribution of a standard normal."""
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


# ============================================================
# Combination potential
# ============================================================

def estimate_combination_potential(state):
    """Estimate the expected score of unfilled combination categories."""

    potential = 0.0

    for category, opportunity in COMBINATION_OPPORTUNITIES.items():

        if state.scorecard[category] is not None:
            continue

        probability, reward = opportunity

        potential += probability * reward

    return potential


# ============================================================
# Remaining score estimation
# ============================================================

def estimate_remaining_score(state):
    """Estimate the expected score of all unfilled categories."""

    expected_score = 0.0

    for category in state.remaining_categories:

        if category in COMBINATION_OPPORTUNITIES:
            probability, reward = COMBINATION_OPPORTUNITIES[category]
            expected_score += probability * reward

        else:
            expected_score += EXPECTED_CATEGORY_SCORES[category]

    return expected_score


# ============================================================
# Upper-section bonus estimation
# ============================================================

def estimate_upper_bonus_probability(state):
    """Estimate the probability of reaching the upper-section bonus."""

    if state.upper_total >= UPPER_BONUS_TARGET:
       return 0.0

    remaining_upper = [
        category
        for category in UPPER_CATEGORIES
        if state.scorecard[category] is None
    ]

    if not remaining_upper:
        return 0.0

    expected_remaining = sum(
        UPPER_EXPECTED_SCORES[category]
        for category in remaining_upper
    )

    variance_remaining = sum(
        UPPER_SCORE_VARIANCES[category]
        for category in remaining_upper
    )

    required_points = UPPER_BONUS_TARGET - state.upper_total

    if variance_remaining <= 0:
        return (
            1.0
            if expected_remaining >= required_points
            else 0.0
        )

    standard_deviation = math.sqrt(variance_remaining)

    # Continuity correction for integer-valued scores.
    z_score = (
        expected_remaining - required_points + 0.5
    ) / standard_deviation

    return clamp(normal_cdf(z_score))


# ============================================================
# Main evaluation function
# ============================================================

def evaluate_state(state):
    """Evaluate a Yahtzee game state.

    The evaluation includes:
    1. Current accumulated score.
    2. Expected score of remaining categories.
    3. Expected upper-section bonus.
    """

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
