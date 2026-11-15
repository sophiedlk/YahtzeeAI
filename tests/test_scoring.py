
import pytest

from scoring import score_category, score_all_categories


def test_ones():
    assert score_category((1, 1, 2, 3, 4), "ones") == 2


def test_sixes():
    assert score_category((6, 6, 6, 2, 3), "sixes") == 18


def test_three_of_a_kind():
    assert score_category((4, 4, 4, 2, 1), "three_of_a_kind") == 15


def test_four_of_a_kind():
    assert score_category((5, 5, 5, 5, 2), "four_of_a_kind") == 22


def test_full_house():
    assert score_category((3, 3, 3, 6, 6), "full_house") == 25


def test_invalid_full_house():
    assert score_category((3, 3, 3, 3, 6), "full_house") == 0


def test_small_straight():
    assert score_category((1, 2, 3, 4, 6), "small_straight") == 30


def test_small_straight_with_duplicate():
    assert score_category((1, 2, 2, 3, 4), "small_straight") == 30


def test_large_straight():
    assert score_category((2, 3, 4, 5, 6), "large_straight") == 40


def test_invalid_large_straight():
    assert score_category((1, 2, 3, 4, 4), "large_straight") == 0


def test_yahtzee():
    assert score_category((6, 6, 6, 6, 6), "yahtzee") == 50


def test_chance():
    assert score_category((1, 2, 3, 4, 5), "chance") == 15


def test_score_all_categories():
    scores = score_all_categories((1, 2, 3, 4, 5))

    assert len(scores) == 13
    assert scores["small_straight"] == 30
    assert scores["large_straight"] == 40
    assert scores["chance"] == 15


def test_invalid_dice():
    with pytest.raises(ValueError):
        score_category((1, 2, 3, 4, 7), "chance")


def test_invalid_category():
    with pytest.raises(ValueError):
        score_category((1, 2, 3, 4, 5), "unknown")
