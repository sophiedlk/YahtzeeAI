
import pytest

from game_state import GameState
from expectimax import get_legal_categories
from greedy_agent import GreedyAgent


def test_greedy_scores_on_third_roll():
    """On the third roll, the agent must score instead of rerolling."""

    state = GameState(
        dice=(1, 2, 3, 4, 5),
        roll=3,
    )

    agent = GreedyAgent()
    action = agent.choose_action(
        state,
        get_legal_categories(state),
    )

    assert action["type"] == "score"
    assert action["category"] == "large_straight"
    assert action["value"] == 40.0


def test_greedy_can_choose_reroll():
    """The agent should be able to choose a reroll."""

    state = GameState(dice=(2, 2, 3, 4, 5), roll=1)

    agent = GreedyAgent()
    action = agent.choose_action(
        state,
        get_legal_categories(state),
    )

    assert action["type"] in ("score", "reroll")

    if action["type"] == "reroll":
        assert isinstance(action["keep"], tuple)
        assert len(action["keep"]) < 5
        assert all(die in (2, 3, 4, 5) for die in action["keep"])

    assert agent.actions_evaluated > 0
    assert agent.outcomes_evaluated > 0


def test_greedy_does_not_reroll_on_third_roll():
    """No reroll action is allowed on roll three."""

    state = GameState(dice=(6, 6, 6, 2, 3), roll=3)

    agent = GreedyAgent()
    action = agent.choose_action(
        state,
        get_legal_categories(state),
    )

    assert action["type"] == "score"


def test_greedy_rejects_filled_category():
    """The agent must reject a category that is already filled."""

    scorecard = GameState().scorecard
    scorecard["chance"] = 20

    state = GameState(
        dice=(1, 2, 3, 4, 5),
        scorecard=scorecard,
    )

    agent = GreedyAgent()

    with pytest.raises(ValueError):
        agent.choose_action(state, ["chance"])


def test_greedy_rejects_empty_legal_categories():
    """The agent must reject an empty list of legal categories."""

    state = GameState(dice=(1, 2, 3, 4, 5))
    agent = GreedyAgent()

    with pytest.raises(ValueError):
        agent.choose_action(state, [])
