
import pytest

from game_state import GameState, CATEGORIES
from expectimax import (
    ExpectimaxAgent,
    get_legal_categories,
    make_successor_state,
)


def make_scorecard():
    return {
        category: None
        for category in CATEGORIES
    }


def test_normal_legal_categories():
    state = GameState()

    assert get_legal_categories(state) == list(CATEGORIES)


def test_filled_categories_are_not_legal():
    scorecard = make_scorecard()
    scorecard["ones"] = 3

    state = GameState(scorecard=scorecard)

    legal = get_legal_categories(state)

    assert "ones" not in legal
    assert len(legal) == 12


def test_joker_requires_matching_upper_category():
    scorecard = make_scorecard()
    scorecard["yahtzee"] = 50

    state = GameState(
        dice=(4, 4, 4, 4, 4),
        scorecard=scorecard,
    )

    assert get_legal_categories(state) == ["fours"]


def test_joker_allows_lower_categories():
    scorecard = make_scorecard()
    scorecard["yahtzee"] = 50
    scorecard["fours"] = 20

    state = GameState(
        dice=(4, 4, 4, 4, 4),
        scorecard=scorecard,
    )

    legal = get_legal_categories(state)

    assert legal == [
        category
        for category in CATEGORIES[6:]
        if scorecard[category] is None
    ]


def test_joker_last_case_allows_empty_upper_categories():
    scorecard = make_scorecard()
    scorecard["yahtzee"] = 50
    scorecard["fours"] = 20

    for category in CATEGORIES[6:]:
        if category != "yahtzee":
            scorecard[category] = 0

    state = GameState(
        dice=(4, 4, 4, 4, 4),
        scorecard=scorecard,
    )

    legal = get_legal_categories(state)

    assert legal == [
        category
        for category in CATEGORIES[:6]
        if scorecard[category] is None
    ]


def test_make_successor_state():
    state = GameState(
        dice=(1, 2, 3, 4, 5),
        roll=1,
    )

    next_state = make_successor_state(
        state,
        (2, 2, 3, 4, 5),
    )

    assert next_state.dice == (2, 2, 3, 4, 5)
    assert next_state.roll == 2
    assert next_state.turn == 1


def test_successor_does_not_change_original():
    state = GameState()

    make_successor_state(
        state,
        (2, 2, 3, 4, 5),
    )

    assert state.dice == (1, 1, 1, 1, 1)
    assert state.roll == 1


def test_agent_returns_valid_action():
    state = GameState(
        dice=(1, 2, 3, 4, 6),
        roll=3,
    )

    agent = ExpectimaxAgent()

    action = agent.choose_action(state)

    assert action["type"] == "score"
    assert action["category"] in CATEGORIES
    assert action["value"] >= 0


def test_agent_can_choose_reroll():
    state = GameState(
        dice=(1, 1, 2, 3, 6),
        roll=1,
    )

    agent = ExpectimaxAgent()

    action = agent.choose_action(state)

    assert action["type"] in ("score", "reroll")

    if action["type"] == "reroll":
        assert len(action["keep"]) < 5


def test_agent_respects_external_legal_categories():
    state = GameState(
        dice=(1, 2, 3, 4, 5),
        roll=3,
    )

    agent = ExpectimaxAgent()

    action = agent.choose_action(
        state,
        legal_categories=["chance"],
    )

    assert action["type"] == "score"
    assert action["category"] == "chance"


def test_agent_rejects_filled_legal_category():
    scorecard = make_scorecard()
    scorecard["ones"] = 3

    state = GameState(scorecard=scorecard)

    agent = ExpectimaxAgent()

    with pytest.raises(ValueError):
        agent.choose_action(
            state,
            legal_categories=["ones"],
        )


def test_agent_rejects_empty_legal_category_list():
    agent = ExpectimaxAgent()

    with pytest.raises(ValueError):
        agent.choose_action(
            GameState(),
            legal_categories=[],
        )


def test_agent_expands_search_nodes():
    state = GameState(
        dice=(1, 2, 3, 4, 6),
        roll=3,
    )

    agent = ExpectimaxAgent()
    agent.choose_action(state)

    assert agent.nodes_expanded > 0


def test_agent_returns_finite_value():
    state = GameState(
        dice=(1, 2, 3, 4, 5),
        roll=3,
    )

    agent = ExpectimaxAgent()
    action = agent.choose_action(state)

    assert action["value"] != float("inf")
    assert action["value"] != float("-inf")
