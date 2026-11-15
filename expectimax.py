
"""Expectimax search with chance-node branch-and-bound pruning."""

from game_state import (
    GameState,
    CATEGORIES,
    UPPER_CATEGORIES,
    LOWER_CATEGORIES,
)

from game_engine import score_turn
from heuristic import evaluate_state, EXPECTED_CATEGORY_SCORES
from strategy import generate_keep_actions
from dice_probability import generate_reroll_outcomes
from yahtzee_rules import is_joker_active


CATEGORY_MAX_SCORES = {
    "ones": 5,
    "twos": 10,
    "threes": 15,
    "fours": 20,
    "fives": 25,
    "sixes": 30,
    "three_of_a_kind": 30,
    "four_of_a_kind": 30,
    "full_house": 25,
    "small_straight": 30,
    "large_straight": 40,
    "yahtzee": 50,
    "chance": 30,
}


def get_legal_categories(state):
    """Determine legal categories for the current dice."""

    empty_categories = [
        category
        for category in CATEGORIES
        if state.scorecard[category] is None
    ]

    if not empty_categories:
        return []

    if not is_joker_active(state.dice, state.scorecard):
        return empty_categories

    matching_category = UPPER_CATEGORIES[state.dice[0] - 1]

    if state.scorecard[matching_category] is None:
        return [matching_category]

    empty_lower = [
        category
        for category in LOWER_CATEGORIES
        if state.scorecard[category] is None
    ]

    if empty_lower:
        return empty_lower

    return [
        category
        for category in UPPER_CATEGORIES
        if state.scorecard[category] is None
    ]


def make_successor_state(state, new_dice):
    """Create a new state after a chance outcome."""

    return GameState(
        dice=tuple(new_dice),
        turn=state.turn,
        roll=state.roll + 1,
        scorecard=dict(state.scorecard),
        upper_total=state.upper_total,
        yahtzee_bonus=state.yahtzee_bonus,
    )


class ExpectimaxAgent:
    """Choose Yahtzee actions using Expectimax."""

    def __init__(self, enable_pruning=True):
        self.enable_pruning = enable_pruning

        self.cache = {}

        self.nodes_expanded = 0
        self.outcomes_evaluated = 0
        self.pruned_outcomes = 0

    def _state_key(self, state, legal_categories=None):
        """Create a hashable representation of a state."""

        return (
            tuple(sorted(state.dice)),
            state.turn,
            state.roll,
            tuple(
                state.scorecard[category]
                for category in CATEGORIES
            ),
            state.upper_total,
            state.yahtzee_bonus,
            tuple(sorted(legal_categories))
            if legal_categories is not None
            else None,
        )

    def _validate_legal_categories(self, state, legal_categories):
        """Validate externally supplied legal categories."""

        if not isinstance(legal_categories, (list, tuple, set)):
            raise ValueError(
                "legal_categories must be a list, tuple, or set."
            )

        categories = list(legal_categories)

        if not categories:
            raise ValueError("At least one legal category is required.")

        if len(categories) != len(set(categories)):
            raise ValueError("Duplicate legal categories are not allowed.")

        for category in categories:
            if category not in CATEGORIES:
                raise ValueError(
                    f"Unknown legal category: {category}"
                )

            if state.scorecard[category] is not None:
                raise ValueError(
                    f"Category is already filled: {category}"
                )

        return categories

    def _upper_bound(self, state):
        """
        Calculate a safe upper bound for a state value.

        This bound intentionally overestimates the achievable value.
        """

        remaining = state.remaining_categories

        if not remaining:
            return float(state.total_score)

        maximum_category_score = max(
            CATEGORY_MAX_SCORES[category]
            for category in remaining
        )

        remaining_heuristic = sum(
            EXPECTED_CATEGORY_SCORES[category]
            for category in remaining
        )

        return (
            state.total_score
            + maximum_category_score
            + 100
            + remaining_heuristic
            + 35
        )

    def _expected_reroll_value(self, state, kept_dice, alpha):
        """
        Calculate the expected value of a reroll.

        If the remaining probability mass cannot beat alpha,
        stop evaluating the remaining outcomes.

        When pruning occurs, return a safe upper bound.
        """

        outcomes = generate_reroll_outcomes(
            state.dice,
            kept_dice,
        )

        # Evaluate more probable outcomes first.
        outcomes = sorted(
            outcomes,
            key=lambda item: item[1],
            reverse=True,
        )

        expected_value = 0.0
        remaining_probability = 1.0

        upper_bound = self._upper_bound(state)

        # Local counter: each Chance node has its own count.
        evaluated_count = 0

        for final_dice, probability in outcomes:

            # Calculate the maximum possible value if all
            # unvisited probability mass reaches the upper bound.
            optimistic_value = (
                expected_value
                + remaining_probability * upper_bound
            )

            # Branch-and-bound pruning condition.
            if (
                self.enable_pruning
                and optimistic_value <= alpha
            ):
                self.pruned_outcomes += (
                    len(outcomes) - evaluated_count
                )

                return optimistic_value

            next_state = make_successor_state(
                state,
                final_dice,
            )

            child_value = self._value(next_state)

            probability_value = float(probability)

            expected_value += probability_value * child_value

            remaining_probability -= probability_value

            evaluated_count += 1
            self.outcomes_evaluated += 1

        return expected_value

    def _value(self, state, legal_categories=None):
        """Calculate the expected value of a state."""

        key = self._state_key(state, legal_categories)

        if key in self.cache:
            return self.cache[key]

        self.nodes_expanded += 1

        if state.is_terminal:
            value = float(state.total_score)
            self.cache[key] = value
            return value

        if legal_categories is None:
            legal_categories = get_legal_categories(state)

        if not legal_categories:
            raise ValueError(
                "No legal categories available in a non-terminal state."
            )

        # MAX NODE: consider scoring immediately.
        best_value = float("-inf")

        for category in legal_categories:
            next_state = score_turn(
                state,
                category,
                legal_categories,
            )

            best_value = max(
                best_value,
                evaluate_state(next_state),
            )

        # No rerolls are allowed after roll 3.
        if state.roll >= 3:
            self.cache[key] = best_value
            return best_value

        # MAX NODE: consider every possible keep action.
        for kept_dice in generate_keep_actions(state.dice):

            expected_value = self._expected_reroll_value(
                state,
                kept_dice,
                best_value,
            )

            best_value = max(
                best_value,
                expected_value,
            )

        self.cache[key] = best_value

        return best_value

    def choose_action(self, state, legal_categories=None):
        """Return the best scoring or reroll action."""

        self.cache.clear()

        # Count the root decision node.
        self.nodes_expanded = 1

        self.outcomes_evaluated = 0
        self.pruned_outcomes = 0

        if state.is_terminal:
            raise ValueError("Cannot act in a terminal state.")

        if legal_categories is None:
            legal_categories = get_legal_categories(state)
        else:
            legal_categories = self._validate_legal_categories(
                state,
                legal_categories,
            )

        if not legal_categories:
            raise ValueError("No legal categories available.")

        best_action = None
        best_value = float("-inf")

        # Consider scoring immediately.
        for category in legal_categories:
            next_state = score_turn(
                state,
                category,
                legal_categories,
            )

            value = evaluate_state(next_state)

            if value > best_value:
                best_value = value

                best_action = {
                    "type": "score",
                    "category": category,
                    "value": value,
                }

        # Consider rerolling if possible.
        if state.roll < 3:

            for kept_dice in generate_keep_actions(state.dice):

                expected_value = self._expected_reroll_value(
                    state,
                    kept_dice,
                    best_value,
                )

                if expected_value > best_value:
                    best_value = expected_value

                    best_action = {
                        "type": "reroll",
                        "keep": kept_dice,
                        "value": expected_value,
                    }

        return best_action
