
"""A one-step greedy baseline agent for Yahtzee."""

from fractions import Fraction

from game_state import GameState
from scoring import score_category
from yahtzee_rules import is_joker_active, joker_score
from expectimax import get_legal_categories
from strategy import generate_keep_actions
from dice_probability import generate_reroll_outcomes


class GreedyAgent:
    """
    A one-step greedy agent.

    It compares:
    1. The best score available with the current dice.
    2. The expected best immediate score after one reroll.

    Unlike Expectimax, it does not recursively search future decisions.
    """

    def __init__(self):
        self.actions_evaluated = 0
        self.outcomes_evaluated = 0

    @staticmethod
    def _category_score(dice, category, scorecard):
        """Calculate the score of a category, including Joker rules."""

        if is_joker_active(dice, scorecard):
            return joker_score(dice, category, scorecard)

        return score_category(dice, category)

    @classmethod
    def _best_immediate_score(cls, dice, scorecard):
        """Return the best legal immediate score for a dice result."""

        temporary_state = GameState(
            dice=tuple(dice),
            turn=1,
            roll=1,
            scorecard=dict(scorecard),
        )

        legal_categories = get_legal_categories(temporary_state)

        if not legal_categories:
            return 0, None

        best_category = max(
            legal_categories,
            key=lambda category: cls._category_score(
                dice, category, scorecard
            ),
        )

        best_score = cls._category_score(
            dice, best_category, scorecard
        )

        return best_score, best_category

    def choose_action(self, state, legal_categories=None):
        """
        Choose a score or reroll action.

        The returned action format matches ExpectimaxAgent.
        """

        self.actions_evaluated = 0
        self.outcomes_evaluated = 0

        if legal_categories is None:
            legal_categories = get_legal_categories(state)

        if not legal_categories:
            raise ValueError("No legal categories are available.")

        for category in legal_categories:
            if category not in state.scorecard:
                raise ValueError(f"Unknown category: {category}")

            if state.scorecard[category] is not None:
                raise ValueError(
                    f"Category is already filled: {category}"
                )

        # Find the best score using the current dice.
        best_score = max(
            self._category_score(
                state.dice, category, state.scorecard
            )
            for category in legal_categories
        )

        best_category = max(
            legal_categories,
            key=lambda category: self._category_score(
                state.dice, category, state.scorecard
            ),
        )

        best_action = {
            "type": "score",
            "category": best_category,
            "value": float(best_score),
        }

        # No more rerolls are allowed on the third roll.
        if state.roll >= 3:
            return best_action

        # Examine every possible keep action.
        for kept_dice in generate_keep_actions(state.dice):
            self.actions_evaluated += 1

            outcomes = generate_reroll_outcomes(
                state.dice, kept_dice
            )

            expected_score = Fraction(0, 1)

            for outcome_dice, probability in outcomes:
                self.outcomes_evaluated += 1

                outcome_score, _ = self._best_immediate_score(
                    outcome_dice,
                    state.scorecard,
                )

                expected_score += probability * outcome_score

            expected_value = float(expected_score)

            # Reroll only when its expected immediate score
            # is strictly better than scoring now.
            if expected_value > best_action["value"]:
                best_action = {
                    "type": "reroll",
                    "keep": kept_dice,
                    "value": expected_value,
                }

        return best_action
