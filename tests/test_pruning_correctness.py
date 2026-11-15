
import pytest

from game_state import GameState, CATEGORIES
from expectimax import (
    ExpectimaxAgent,
    get_legal_categories,
    make_successor_state,
)
from dice_probability import generate_reroll_outcomes
from heuristic import evaluate_state


def make_scorecard(filled=None):
    """Create a scorecard with selected categories already filled."""

    scorecard = {category: None for category in CATEGORIES}

    if filled:
        scorecard.update(filled)

    return scorecard


def make_state(
    dice=(1, 2, 3, 4, 6),
    roll=1,
    filled=None,
    upper_total=0,
    yahtzee_bonus=0,
):
    """Create a valid game state for testing."""

    scorecard = make_scorecard(filled)

    completed = sum(
        score is not None
        for score in scorecard.values()
    )

    return GameState(
        dice=tuple(dice),
        turn=completed + 1,
        roll=roll,
        scorecard=scorecard,
        upper_total=upper_total,
        yahtzee_bonus=yahtzee_bonus,
    )


def make_agents():
    """Create agents with and without pruning."""

    return (
        ExpectimaxAgent(enable_pruning=False),
        ExpectimaxAgent(enable_pruning=True),
    )


# ---------------------------------------------------------
# Test 1: Upper bound must cover immediate child evaluations
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "dice",
    [
        (1, 2, 3, 4, 6),
        (2, 2, 3, 3, 5),
        (4, 4, 4, 2, 6),
        (5, 5, 5, 5, 2),
        (6, 6, 6, 6, 6),
        (1, 1, 1, 1, 1),
    ],
)
def test_upper_bound_covers_immediate_child_values(dice):
    state = make_state(dice=dice)

    agent = ExpectimaxAgent(enable_pruning=False)

    upper_bound = agent._upper_bound(state)

    legal_categories = get_legal_categories(state)

    child_values = []

    for category in legal_categories:
        from game_engine import score_turn

        next_state = score_turn(
            state,
            category,
            legal_categories,
        )

        child_values.append(evaluate_state(next_state))

    assert child_values

    assert upper_bound >= max(child_values)


# ---------------------------------------------------------
# Test 2: Upper bound must cover all one-step chance outcomes
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "dice, roll",
    [
        ((1, 2, 3, 4, 6), 1),
        ((2, 2, 3, 3, 5), 2),
        ((4, 4, 4, 2, 6), 1),
        ((5, 5, 5, 5, 2), 2),
    ],
)
def test_upper_bound_covers_chance_outcomes(dice, roll):
    state = make_state(
        dice=dice,
        roll=roll,
    )

    agent = ExpectimaxAgent(enable_pruning=False)

    upper_bound = agent._upper_bound(state)

    for kept_dice in (
        (dice[0],),
        tuple(sorted(dice[:2])),
        tuple(sorted(dice[:3])),
        tuple(sorted(dice[:4])),
    ):

        outcomes = generate_reroll_outcomes(
            state.dice,
            kept_dice,
        )

        for final_dice, probability in outcomes:

            next_state = make_successor_state(
                state,
                final_dice,
            )

            value = agent._value(next_state)

            assert upper_bound >= value, (
                f"Upper bound violation: "
                f"bound={upper_bound}, value={value}, "
                f"dice={final_dice}"
            )


# ---------------------------------------------------------
# Test 3: Pruning and non-pruning must return equal values
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "dice, roll",
    [
        ((1, 2, 3, 4, 6), 1),
        ((2, 2, 3, 3, 5), 2),
        ((4, 4, 4, 2, 6), 2),
        ((5, 5, 5, 5, 2), 1),
        ((6, 6, 6, 6, 6), 2),
    ],
)
def test_pruning_preserves_value(dice, roll):
    state = make_state(
        dice=dice,
        roll=roll,
    )

    plain_agent, pruned_agent = make_agents()

    plain_value = plain_agent._value(state)
    pruned_value = pruned_agent._value(state)

    assert pruned_value == pytest.approx(
        plain_value,
        abs=1e-9,
    )


# ---------------------------------------------------------
# Test 4: Pruning and non-pruning must select equal actions
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "dice, roll",
    [
        ((1, 2, 3, 4, 6), 1),
        ((2, 2, 3, 3, 5), 2),
        ((4, 4, 4, 2, 6), 2),
        ((5, 5, 5, 5, 2), 1),
    ],
)
def test_pruning_preserves_selected_action(dice, roll):
    state = make_state(
        dice=dice,
        roll=roll,
    )

    plain_agent, pruned_agent = make_agents()

    plain_action = plain_agent.choose_action(state)
    pruned_action = pruned_agent.choose_action(state)

    assert plain_action["type"] == pruned_action["type"]

    if plain_action["type"] == "score":
        assert (
            plain_action["category"]
            == pruned_action["category"]
        )

    else:
        assert tuple(plain_action["keep"]) == tuple(
            pruned_action["keep"]
        )

    assert pruned_action["value"] == pytest.approx(
        plain_action["value"],
        abs=1e-9,
    )


# ---------------------------------------------------------
# Test 5: Yahtzee and Joker states
# ---------------------------------------------------------

def test_pruning_with_active_yahtzee_joker():
    filled = {
        "yahtzee": 50,
        "sixes": 30,
    }

    state = make_state(
        dice=(6, 6, 6, 6, 6),
        roll=2,
        filled=filled,
        upper_total=30,
        yahtzee_bonus=100,
    )

    plain_agent, pruned_agent = make_agents()

    plain_value = plain_agent._value(state)
    pruned_value = pruned_agent._value(state)

    assert pruned_value == pytest.approx(
        plain_value,
        abs=1e-9,
    )


def test_pruning_with_upper_bonus_already_earned():
    filled = {
        "ones": 5,
        "twos": 10,
        "threes": 15,
        "fours": 20,
        "fives": 25,
        "sixes": 30,
    }

    state = make_state(
        dice=(2, 3, 4, 5, 6),
        roll=2,
        filled=filled,
        upper_total=105,
    )

    plain_agent, pruned_agent = make_agents()

    plain_value = plain_agent._value(state)
    pruned_value = pruned_agent._value(state)

    assert pruned_value == pytest.approx(
        plain_value,
        abs=1e-9,
    )
