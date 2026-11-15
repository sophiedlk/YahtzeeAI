
import pytest

from game_state import GameState, CATEGORIES
from game_engine import apply_reroll, score_turn


def make_scorecard():
    return {
        category: None
        for category in CATEGORIES
    }


# -----------------------------
# Reroll tests
# -----------------------------

def test_apply_reroll_keeps_selected_dice():
    state = GameState(dice=(1, 2, 3, 4, 5))

    new_state = apply_reroll(
        state,
        kept_indices=[0, 2],
        new_dice=[6, 6, 6],
    )

    assert new_state.dice == (1, 6, 3, 6, 6)
    assert new_state.roll == 2


def test_apply_reroll_does_not_change_original_state():
    state = GameState(dice=(1, 2, 3, 4, 5))

    apply_reroll(
        state,
        kept_indices=[0, 1, 2, 3],
        new_dice=[6],
    )

    assert state.dice == (1, 2, 3, 4, 5)
    assert state.roll == 1


def test_apply_reroll_all_dice():
    state = GameState(dice=(1, 2, 3, 4, 5))

    new_state = apply_reroll(
        state,
        kept_indices=[],
        new_dice=[6, 6, 5, 5, 4],
    )

    assert new_state.dice == (6, 6, 5, 5, 4)


def test_apply_reroll_rejects_wrong_number_of_dice():
    state = GameState(dice=(1, 2, 3, 4, 5))

    with pytest.raises(ValueError):
        apply_reroll(
            state,
            kept_indices=[0, 1, 2],
            new_dice=[6],
        )


def test_apply_reroll_rejects_invalid_index():
    state = GameState()

    with pytest.raises(ValueError):
        apply_reroll(
            state,
            kept_indices=[5],
            new_dice=[1, 2, 3, 4],
        )


def test_apply_reroll_rejects_fourth_roll():
    state = GameState(roll=3)

    with pytest.raises(ValueError):
        apply_reroll(
            state,
            kept_indices=[0, 1, 2, 3],
            new_dice=[6],
        )


# -----------------------------
# Normal scoring tests
# -----------------------------

def test_score_turn_updates_scorecard():
    state = GameState(dice=(1, 1, 2, 3, 4))

    new_state = score_turn(
        state,
        "ones",
        ["ones", "twos", "threes"],
    )

    assert new_state.scorecard["ones"] == 2
    assert new_state.upper_total == 2
    assert new_state.turn == 2
    assert new_state.roll == 1


def test_score_turn_does_not_change_original_state():
    state = GameState(dice=(1, 1, 2, 3, 4))

    score_turn(
        state,
        "ones",
        ["ones"],
    )

    assert state.scorecard["ones"] is None
    assert state.turn == 1


def test_score_turn_rejects_illegal_category():
    state = GameState(dice=(1, 2, 3, 4, 5))

    with pytest.raises(ValueError):
        score_turn(
            state,
            "chance",
            ["ones", "twos"],
        )


def test_score_turn_rejects_filled_category():
    scorecard = make_scorecard()
    scorecard["ones"] = 3

    state = GameState(scorecard=scorecard)

    with pytest.raises(ValueError):
        score_turn(
            state,
            "ones",
            ["ones"],
        )


# -----------------------------
# Yahtzee Joker integration tests
# -----------------------------

def test_score_turn_adds_yahtzee_bonus():
    scorecard = make_scorecard()
    scorecard["yahtzee"] = 50
    scorecard["sixes"] = 30

    state = GameState(
        dice=(6, 6, 6, 6, 6),
        scorecard=scorecard,
        upper_total=30,
    )

    new_state = score_turn(
        state,
        "full_house",
        ["full_house"],
    )

    assert new_state.scorecard["full_house"] == 25
    assert new_state.yahtzee_bonus == 100


def test_score_turn_handles_last_joker_case():
    scorecard = make_scorecard()
    scorecard["yahtzee"] = 50
    scorecard["fours"] = 20

    for category in (
        "three_of_a_kind",
        "four_of_a_kind",
        "full_house",
        "small_straight",
        "large_straight",
        "chance",
    ):
        scorecard[category] = 0

    state = GameState(
        dice=(4, 4, 4, 4, 4),
        scorecard=scorecard,
        upper_total=20,
    )

    new_state = score_turn(
        state,
        "sixes",
        ["sixes"],
    )

    assert new_state.scorecard["sixes"] == 0
    assert new_state.yahtzee_bonus == 100


# -----------------------------
# Game completion test
# -----------------------------

def test_score_turn_finishes_game():
    scorecard = {
        category: 0
        for category in CATEGORIES
    }

    scorecard["chance"] = None

    state = GameState(
        dice=(1, 2, 3, 4, 5),
        turn=13,
        scorecard=scorecard,
    )

    new_state = score_turn(
        state,
        "chance",
        ["chance"],
    )

    assert new_state.is_terminal is True
    assert new_state.scorecard["chance"] == 15
    assert new_state.turn == 13
