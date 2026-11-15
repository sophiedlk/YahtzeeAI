
"""Handle special Yahtzee bonus and Joker rules."""

from game_state import CATEGORIES, UPPER_CATEGORIES, LOWER_CATEGORIES


def is_yahtzee(dice):
    """Return True if all five dice have the same value."""

    if len(dice) != 5:
        raise ValueError("Exactly five dice are required.")

    if any(type(die) is not int or not 1 <= die <= 6 for die in dice):
        raise ValueError("Each die must be an integer from 1 to 6.")

    return len(set(dice)) == 1


def get_yahtzee_bonus(dice, scorecard):
    """Return the bonus earned for an additional Yahtzee."""

    if set(scorecard) != set(CATEGORIES):
        raise ValueError("Invalid scorecard.")

    if is_yahtzee(dice) and scorecard["yahtzee"] == 50:
        return 100

    return 0


def is_joker_active(dice, scorecard):
    """Check whether the Joker rule applies."""

    if set(scorecard) != set(CATEGORIES):
        raise ValueError("Invalid scorecard.")

    return (
        is_yahtzee(dice)
        and scorecard["yahtzee"] == 50
    )

def joker_score(dice, category, scorecard):
    """
    Calculate a category score under Joker rules.

    The caller must also check that category belongs
    to the evaluator's legal_categories list.
    """

    if category not in CATEGORIES:
        raise ValueError(f"Unknown category: {category}")

    if set(scorecard) != set(CATEGORIES):
        raise ValueError("Invalid scorecard.")

    if not is_joker_active(dice, scorecard):
        raise ValueError("Joker rules are not active.")

    if scorecard[category] is not None:
        raise ValueError("This category has already been filled.")

    matching_category = UPPER_CATEGORIES[dice[0] - 1]

    # Upper-section Joker rules
    if category in UPPER_CATEGORIES:

        # Priority 1: the matching upper category is mandatory.
        if scorecard[matching_category] is None:
            if category == matching_category:
                return 5 * dice[0]

            raise ValueError(
                "The matching upper category must be selected."
            )

        # Last Joker case:
        # All lower categories are filled, so another empty
        # upper category must be filled with zero.
        all_lower_filled = all(
            scorecard[lower_category] is not None
            for lower_category in LOWER_CATEGORIES
        )

        if all_lower_filled:
            return 0

        raise ValueError(
            "Another upper category is not legal yet."
        )

    # Priority 2: lower-section Joker scores
    if category in LOWER_CATEGORIES:

        if scorecard[matching_category] is None:
            raise ValueError(
                "The matching upper category must be selected first."
            )

        if category in (
            "three_of_a_kind",
            "four_of_a_kind",
            "chance",
        ):
            return sum(dice)

        if category == "full_house":
            return 25

        if category == "small_straight":
            return 30

        if category == "large_straight":
            return 40

    raise ValueError("Invalid Joker category.")
