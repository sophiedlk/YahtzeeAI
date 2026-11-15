
import pytest

from game_state import GameState, CATEGORIES
from heuristic import (
    clamp,
    estimate_upper_bonus_probability,
    estimate_remaining_score,
    evaluate_state,
)


def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-2, 0, 10) == 0
    assert clamp(15, 0, 10) == 10


def test_terminal_state_evaluation():
    scorecard = {
        category: 0
        for category in CATEGORIES
    }

    scorecard["chance"] = 20

    state = GameState(
        scorecard=scorecard,
        upper_total=0,
    )

    assert evaluate_state(state) == 20.0


def test_remaining_score_is_positive():
    state = GameState()

    assert estimate_remaining_score(state) > 0


def test_remaining_score_decreases_when_category_is_filled():
    state = GameState()

    original = estimate_remaining_score(state)

    state.scorecard["chance"] = 20

    updated = estimate_remaining_score(state)

    assert updated < original


def test_upper_bonus_probability_is_zero_when_bonus_already_earned():
    state = GameState(upper_total=63)

    assert estimate_upper_bonus_probability(state) == 0.0


def test_upper_bonus_probability_is_zero_without_remaining_upper():
    scorecard = {
        category: None
        for category in CATEGORIES
    }

    for category in CATEGORIES[:6]:
        scorecard[category] = 0

    state = GameState(
        scorecard=scorecard,
        upper_total=0,
    )

    assert estimate_upper_bonus_probability(state) == 0.0


def test_upper_bonus_probability_is_between_zero_and_one():
    state = GameState(upper_total=30)

    probability = estimate_upper_bonus_probability(state)

    assert 0.0 <= probability <= 1.0


def test_evaluation_is_not_less_than_current_score():
    state = GameState(
        upper_total=20,
    )

    assert evaluate_state(state) >= state.total_score


def test_evaluation_returns_number():
    state = GameState()

    assert isinstance(evaluate_state(state), (int, float))



def test_evaluation_increases_with_current_score():
    scorecard1 = {
        category: None
        for category in CATEGORIES
    }

    scorecard2 = {
        category: None
        for category in CATEGORIES
    }

    # Both states have exactly the same remaining categories.
    scorecard1["ones"] = 0
    scorecard2["ones"] = 5

    state1 = GameState(
        scorecard=scorecard1,
        upper_total=0,
    )

    state2 = GameState(
        scorecard=scorecard2,
        upper_total=5,
    )

    assert evaluate_state(state2) > evaluate_state(state1)


def test_upper_bonus_probability_is_zero_when_all_upper_filled():
    scorecard = {
        category: None
        for category in CATEGORIES
    }

    for category in CATEGORIES[:6]:
        scorecard[category] = 0

    state = GameState(
        scorecard=scorecard,
        upper_total=0,
    )

    assert estimate_upper_bonus_probability(state) == 0.0
