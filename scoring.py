
"""Calculate Yahtzee scores for all 13 categories."""

from collections import Counter

from game_state import CATEGORIES, UPPER_CATEGORIES


def score_category(dice, category):
    """Calculate the score for a category using five dice."""

    if len(dice) != 5:
        raise ValueError("Exactly five dice are required.")

    if any(type(die) is not int or not 1 <= die <= 6 for die in dice):
        raise ValueError("Each die must be an integer from 1 to 6.")

    if category not in CATEGORIES:
        raise ValueError(f"Unknown category: {category}")

    counts = Counter(dice)
    total = sum(dice)
    frequencies = sorted(counts.values())

    # Upper section
    if category in UPPER_CATEGORIES:
        face = UPPER_CATEGORIES.index(category) + 1
        return dice.count(face) * face

    # Three of a kind
    if category == "three_of_a_kind":
        return total if max(counts.values()) >= 3 else 0

    # Four of a kind
    if category == "four_of_a_kind":
        return total if max(counts.values()) >= 4 else 0

    # Full house
    if category == "full_house":
        return 25 if frequencies == [2, 3] else 0

    # Small straight
    if category == "small_straight":
        unique_dice = set(dice)

        sequences = (
            {1, 2, 3, 4},
            {2, 3, 4, 5},
            {3, 4, 5, 6},
        )

        return 30 if any(
            sequence.issubset(unique_dice)
            for sequence in sequences
        ) else 0

    # Large straight
    if category == "large_straight":
        unique_dice = set(dice)

        if unique_dice in (
            {1, 2, 3, 4, 5},
            {2, 3, 4, 5, 6},
        ):
            return 40

        return 0

    # Yahtzee
    if category == "yahtzee":
        return 50 if max(counts.values()) == 5 else 0

    # Chance
    if category == "chance":
        return total

    raise ValueError(f"Scoring not implemented for: {category}")


def score_all_categories(dice):
    """Return the score for every category."""

    return {
        category: score_category(dice, category)
        for category in CATEGORIES
    }
