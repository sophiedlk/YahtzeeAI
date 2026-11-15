
import pytest
from game_state import CATEGORIES, GameState
from game_state import CATEGORIES
from yahtzee_rules import (
    is_yahtzee,
    get_yahtzee_bonus,
    is_joker_active,
    joker_score,
)


def make_scorecard(yahtzee_score=50):
    scorecard = {
        category: None for category in CATEGORIES
    }

    scorecard["yahtzee"] = yahtzee_score

    return scorecard


# -----------------------------
# Yahtzee detection tests
# -----------------------------

def test_is_yahtzee():
    assert is_yahtzee((4, 4, 4, 4, 4)) is True


def test_is_not_yahtzee():
    assert is_yahtzee((4, 4, 4, 4, 3)) is False


# -----------------------------
# Yahtzee bonus tests
# -----------------------------

def test_yahtzee_bonus_awarded():
    scorecard = make_scorecard(50)

    assert get_yahtzee_bonus(
        (6, 6, 6, 6, 6),
        scorecard,
    ) == 100


def test_no_bonus_when_yahtzee_box_is_zero():
    scorecard = make_scorecard(0)

    assert get_yahtzee_bonus(
        (6, 6, 6, 6, 6),
        scorecard,
    ) == 0


def test_no_bonus_without_yahtzee():
    scorecard = make_scorecard(50)

    assert get_yahtzee_bonus(
        (6, 6, 6, 6, 5),
        scorecard,
    ) == 0


# -----------------------------
# Joker activation tests
# -----------------------------

def test_joker_active_after_fifty():
    scorecard = make_scorecard(50)

    assert is_joker_active(
        (3, 3, 3, 3, 3),
        scorecard,
    ) is True


def test_joker_not_active_after_zero():
    scorecard = make_scorecard(0)

    assert is_joker_active(
        (3, 3, 3, 3, 3),
        scorecard,
    ) is False


def test_joker_not_active_when_box_is_empty():
    scorecard = make_scorecard(None)

    assert is_joker_active(
        (3, 3, 3, 3, 3),
        scorecard,
    ) is False


# -----------------------------
# Joker lower-section tests
# -----------------------------

def test_joker_full_house():
    scorecard = make_scorecard(50)
    scorecard["sixes"] = 30

    assert joker_score(
        (6, 6, 6, 6, 6),
        "full_house",
        scorecard,
    ) == 25


def test_joker_small_straight():
    scorecard = make_scorecard(50)
    scorecard["sixes"] = 30

    assert joker_score(
        (6, 6, 6, 6, 6),
        "small_straight",
        scorecard,
    ) == 30


def test_joker_large_straight():
    scorecard = make_scorecard(50)
    scorecard["sixes"] = 30

    assert joker_score(
        (6, 6, 6, 6, 6),
        "large_straight",
        scorecard,
    ) == 40


def test_joker_chance():
    scorecard = make_scorecard(50)
    scorecard["fives"] = 25

    assert joker_score(
        (5, 5, 5, 5, 5),
        "chance",
        scorecard,
    ) == 25


def test_joker_three_of_a_kind():
    scorecard = make_scorecard(50)
    scorecard["fours"] = 20

    assert joker_score(
        (4, 4, 4, 4, 4),
        "three_of_a_kind",
        scorecard,
    ) == 20


def test_joker_four_of_a_kind():
    scorecard = make_scorecard(50)
    scorecard["fours"] = 20

    assert joker_score(
        (4, 4, 4, 4, 4),
        "four_of_a_kind",
        scorecard,
    ) == 20


# -----------------------------
# Joker upper-section tests
# -----------------------------

def test_joker_matching_upper_category():
    scorecard = make_scorecard(50)

    assert joker_score(
        (4, 4, 4, 4, 4),
        "fours",
        scorecard,
    ) == 20


def test_joker_rejects_when_yahtzee_box_is_zero():
    scorecard = make_scorecard(0)

    with pytest.raises(ValueError):
        joker_score(
            (2, 2, 2, 2, 2),
            "twos",
            scorecard,
        )


def test_joker_other_upper_category_when_all_lower_are_filled():
    scorecard = make_scorecard(50)

    # The matching upper category is already filled.
    scorecard["fours"] = 20

    # All lower categories are filled.
    for category in (
        "three_of_a_kind",
        "four_of_a_kind",
        "full_house",
        "small_straight",
        "large_straight",
        "chance",
    ):
        scorecard[category] = 0

    # The Yahtzee box is already filled with 50.
    # Another empty upper category must receive zero.
    assert joker_score(
        (4, 4, 4, 4, 4),
        "sixes",
        scorecard,
    ) == 0


# -----------------------------
# Invalid Joker selection tests
# -----------------------------

def test_joker_rejects_filled_category():
    scorecard = make_scorecard(50)
    scorecard["sixes"] = 30
    scorecard["full_house"] = 25

    with pytest.raises(ValueError):
        joker_score(
            (6, 6, 6, 6, 6),
            "full_house",
            scorecard,
        )


def test_joker_rejects_non_matching_upper_category():
    scorecard = make_scorecard(50)

    with pytest.raises(ValueError):
        joker_score(
            (4, 4, 4, 4, 4),
            "sixes",
            scorecard,
        )


def test_joker_rejects_when_not_active():
    scorecard = make_scorecard(None)

    with pytest.raises(ValueError):
        joker_score(
            (4, 4, 4, 4, 4),
            "full_house",
            scorecard,
        )


def test_joker_rejects_other_upper_when_lower_is_empty():
    scorecard = make_scorecard(50)
    scorecard["fours"] = 20

    with pytest.raises(ValueError):
        joker_score(
            (4, 4, 4, 4, 4),
            "sixes",
            scorecard,
        )


def test_joker_rejects_lower_when_matching_upper_is_empty():
    scorecard = make_scorecard(50)

    with pytest.raises(ValueError):
        joker_score(
            (4, 4, 4, 4, 4),
            "chance",
            scorecard,
        )
        def test_score_turn_uses_normal_scoring_after_zero_yahtzee():
            from game_engine import score_turn

            scorecard = make_scorecard(0)
            state = GameState(
                dice=(2, 2, 2, 2, 2),
                scorecard=scorecard,
            )

            result = score_turn(
                state,
                "twos",
                ["twos"],
            )

            assert result.scorecard["twos"] == 10
            assert result.yahtzee_bonus == 0
