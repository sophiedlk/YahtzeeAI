
from game_state import GameState
from expectimax import ExpectimaxAgent


def test_pruning_is_enabled_by_default():
    agent = ExpectimaxAgent()

    assert agent.enable_pruning is True


def test_pruning_can_be_disabled():
    agent = ExpectimaxAgent(enable_pruning=False)

    assert agent.enable_pruning is False


def test_upper_bound_is_not_below_current_score():
    agent = ExpectimaxAgent()

    state = GameState(
        dice=(6, 6, 6, 6, 6),
    )

    assert agent._upper_bound(state) >= state.total_score


def test_pruning_counters_start_at_zero():
    agent = ExpectimaxAgent()

    assert agent.nodes_expanded == 0
    assert agent.outcomes_evaluated == 0
    assert agent.pruned_outcomes == 0


def test_search_updates_outcome_counter():
    agent = ExpectimaxAgent()

    state = GameState(
        dice=(1, 2, 3, 4, 6),
        roll=2,
    )

    agent.choose_action(state)

    assert (
        agent.outcomes_evaluated + agent.pruned_outcomes
    ) > 0


def test_search_returns_valid_action_with_pruning():
    agent = ExpectimaxAgent(enable_pruning=True)

    state = GameState(
        dice=(1, 2, 3, 4, 6),
        roll=2,
    )

    action = agent.choose_action(state)

    assert action["type"] in ("score", "reroll")


def test_search_returns_valid_action_without_pruning():
    agent = ExpectimaxAgent(enable_pruning=False)

    state = GameState(
        dice=(1, 2, 3, 4, 6),
        roll=2,
    )

    action = agent.choose_action(state)

    assert action["type"] in ("score", "reroll")


def test_pruning_and_unpruned_search_agree_on_final_roll():
    state = GameState(
        dice=(1, 2, 3, 4, 6),
        roll=3,
    )

    pruned_agent = ExpectimaxAgent(enable_pruning=True)
    plain_agent = ExpectimaxAgent(enable_pruning=False)

    pruned_action = pruned_agent.choose_action(state)
    plain_action = plain_agent.choose_action(state)

    assert pruned_action["type"] == plain_action["type"]
    assert pruned_action["category"] == plain_action["category"]
    assert pruned_action["value"] == plain_action["value"]
