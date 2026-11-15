
import pytest
from fractions import Fraction

from dice_probability import (
    generate_roll_outcomes,
    probability_sum,
    generate_reroll_outcomes,
)


# ---------------------------------
# Basic probability tests
# ---------------------------------

def test_zero_dice():
    outcomes = generate_roll_outcomes(0)

    assert outcomes == (
        ((), Fraction(1, 1)),
    )


def test_one_die_has_six_outcomes():
    outcomes = generate_roll_outcomes(1)

    assert len(outcomes) == 6


def test_one_die_probabilities():
    outcomes = generate_roll_outcomes(1)

    for outcome, probability in outcomes:
        assert probability == Fraction(1, 6)
        assert len(outcome) == 1


def test_two_dice_have_21_unique_outcomes():
    outcomes = generate_roll_outcomes(2)

    assert len(outcomes) == 21


def test_two_dice_probability_of_equal_values():
    outcomes = generate_roll_outcomes(2)

    probabilities = dict(outcomes)

    assert probabilities[(3, 3)] == Fraction(1, 36)


def test_two_dice_probability_of_different_values():
    outcomes = generate_roll_outcomes(2)

    probabilities = dict(outcomes)

    assert probabilities[(1, 2)] == Fraction(2, 36)


def test_three_dice_have_56_unique_outcomes():
    outcomes = generate_roll_outcomes(3)

    assert len(outcomes) == 56


def test_five_dice_have_252_unique_outcomes():
    outcomes = generate_roll_outcomes(5)

    assert len(outcomes) == 252


# ---------------------------------
# Probability sum tests
# ---------------------------------

@pytest.mark.parametrize(
    "number_of_dice",
    range(6),
)
def test_probability_sum_is_one(number_of_dice):
    assert probability_sum(number_of_dice) == 1


def test_all_outcomes_are_sorted():
    outcomes = generate_roll_outcomes(5)

    for outcome, _ in outcomes:
        assert outcome == tuple(sorted(outcome))


def test_probabilities_are_positive():
    outcomes = generate_roll_outcomes(5)

    for _, probability in outcomes:
        assert probability > 0


# ---------------------------------
# Invalid input tests
# ---------------------------------

@pytest.mark.parametrize(
    "invalid_value",
    [-1, 6, 7, 2.5, "3", True, None],
)
def test_invalid_number_of_dice(invalid_value):
    with pytest.raises(ValueError):
        generate_roll_outcomes(invalid_value)


# ---------------------------------
# Reroll outcome tests
# ---------------------------------

def test_reroll_one_die_has_six_results():
    results = generate_reroll_outcomes(
        (1, 2, 3, 4, 5),
        (1, 2, 3, 4),
    )

    assert len(results) == 6


def test_reroll_two_dice_has_21_results():
    results = generate_reroll_outcomes(
        (1, 1, 2, 4, 6),
        (1, 1, 2),
    )

    assert len(results) == 21


def test_reroll_all_dice_has_252_results():
    results = generate_reroll_outcomes(
        (1, 2, 3, 4, 5),
        (),
    )

    assert len(results) == 252


def test_reroll_probabilities_sum_to_one():
    results = generate_reroll_outcomes(
        (1, 1, 2, 4, 6),
        (1, 1, 2),
    )

    assert sum(
        probability
        for _, probability in results
    ) == 1


def test_reroll_keeps_selected_dice():
    results = generate_reroll_outcomes(
        (1, 1, 2, 4, 6),
        (1, 1, 2),
    )

    for final_dice, _ in results:
        assert final_dice.count(1) >= 2
        assert final_dice.count(2) >= 1


def test_reroll_results_contain_five_dice():
    results = generate_reroll_outcomes(
        (1, 2, 3, 4, 5),
        (1, 2),
    )

    for final_dice, _ in results:
        assert len(final_dice) == 5


def test_reroll_results_are_sorted():
    results = generate_reroll_outcomes(
        (1, 2, 3, 4, 5),
        (1, 2),
    )

    for final_dice, _ in results:
        assert final_dice == tuple(sorted(final_dice))


def test_reroll_all_dice_kept():
    results = generate_reroll_outcomes(
        (1, 2, 3, 4, 5),
        (1, 2, 3, 4, 5),
    )

    assert results == (
        ((1, 2, 3, 4, 5), Fraction(1, 1)),
    )


def test_cannot_keep_unavailable_dice():
    with pytest.raises(ValueError):
        generate_reroll_outcomes(
            (1, 2, 3, 4, 5),
            (1, 1),
        )
