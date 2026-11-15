
import pytest

from strategy import generate_keep_actions


def test_generate_actions_returns_tuple():
    actions = generate_keep_actions((1, 2, 3, 4, 5))

    assert isinstance(actions, tuple)


def test_generate_actions_includes_reroll_all():
    actions = generate_keep_actions((1, 2, 3, 4, 5))

    assert () in actions


def test_generate_actions_excludes_keep_all():
    dice = (1, 2, 3, 4, 5)

    actions = generate_keep_actions(dice)

    assert dice not in actions
    assert len(actions) == 31


def test_generate_actions_are_unique():
    actions = generate_keep_actions((1, 1, 2, 2, 3))

    assert len(actions) == len(set(actions))


def test_generate_actions_are_sorted():
    actions = generate_keep_actions((6, 2, 4, 1, 3))

    for action in actions:
        assert action == tuple(sorted(action))


def test_generate_actions_with_duplicate_dice():
    actions = generate_keep_actions((1, 1, 2, 2, 3))

    assert len(actions) == 17


def test_generate_actions_with_all_equal_dice():
    actions = generate_keep_actions((4, 4, 4, 4, 4))

    assert len(actions) == 5

    assert actions == (
        (),
        (4,),
        (4, 4),
        (4, 4, 4),
        (4, 4, 4, 4),
    )


def test_generate_actions_can_keep_all_occurrences_of_a_value():
    actions = generate_keep_actions((2, 2, 3, 4, 5))

    assert (2, 2) in actions


def test_generate_actions_never_keep_unavailable_dice():
    dice = (1, 1, 3, 5, 6)

    actions = generate_keep_actions(dice)

    for action in actions:
        for face in range(1, 7):
            assert action.count(face) <= dice.count(face)


def test_invalid_number_of_dice():
    with pytest.raises(ValueError):
        generate_keep_actions((1, 2, 3, 4))


def test_invalid_die_value():
    with pytest.raises(ValueError):
        generate_keep_actions((1, 2, 3, 4, 7))


def test_invalid_die_type():
    with pytest.raises(ValueError):
        generate_keep_actions((1, 2, 3, 4, True))
