
import pytest

from game_state import GameState, CATEGORIES


def test_initial_state():
    state = GameState()

    assert state.turn == 1
    assert state.roll == 1
    assert state.dice == (1, 1, 1, 1, 1)
    assert len(state.remaining_categories) == 13
    assert state.total_score == 0


def test_upper_bonus():
    state = GameState(upper_total=63)

    assert state.upper_bonus == 35


def test_no_upper_bonus():
    state = GameState(upper_total=62)

    assert state.upper_bonus == 0


def test_total_score():
    scorecard = {
        category: None for category in CATEGORIES
    }

    scorecard["ones"] = 3
    scorecard["twos"] = 6

    state = GameState(
        scorecard=scorecard,
        upper_total=63,
        yahtzee_bonus=100,
    )

    assert state.total_score == 144


def test_terminal_state():
    scorecard = {
        category: 0 for category in CATEGORIES
    }

    state = GameState(scorecard=scorecard)

    assert state.is_terminal is True


def test_invalid_dice():
    with pytest.raises(ValueError):
        GameState(dice=(1, 2, 3, 4, 7))


def test_invalid_turn():
    with pytest.raises(ValueError):
        GameState(turn=14)
