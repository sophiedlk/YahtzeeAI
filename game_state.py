
"""Represent the complete state of a Yahtzee game."""

from dataclasses import dataclass, field
from typing import Optional


CATEGORIES = (
    "ones",
    "twos",
    "threes",
    "fours",
    "fives",
    "sixes",
    "three_of_a_kind",
    "four_of_a_kind",
    "full_house",
    "small_straight",
    "large_straight",
    "yahtzee",
    "chance",
)

UPPER_CATEGORIES = CATEGORIES[:6]

LOWER_CATEGORIES = CATEGORIES[6:]


@dataclass
class GameState:
    """Store all information required to describe a game state."""

    dice: tuple[int, ...] = (1, 1, 1, 1, 1)

    turn: int = 1

    roll: int = 1

    scorecard: dict[str, Optional[int]] = field(
        default_factory=lambda: {
            category: None for category in CATEGORIES
        }
    )

    upper_total: int = 0

    yahtzee_bonus: int = 0

    def __post_init__(self):
        self.validate()

    def validate(self):
        """Validate the game state."""

        if len(self.dice) != 5:
            raise ValueError("Exactly five dice are required.")

        if any(type(die) is not int or not 1 <= die <= 6
               for die in self.dice):
            raise ValueError("Each die must be an integer from 1 to 6.")

        if type(self.turn) is not int or not 1 <= self.turn <= 13:
            raise ValueError("Turn must be between 1 and 13.")

        if type(self.roll) is not int or not 1 <= self.roll <= 3:
            raise ValueError("Roll must be between 1 and 3.")

        if set(self.scorecard.keys()) != set(CATEGORIES):
            raise ValueError("Scorecard must contain exactly 13 categories.")

        for score in self.scorecard.values():
            if score is not None:
                if type(score) is not int or score < 0:
                    raise ValueError("Scores must be non-negative integers.")

        if type(self.upper_total) is not int or self.upper_total < 0:
            raise ValueError("Upper total must be non-negative.")

        if type(self.yahtzee_bonus) is not int or self.yahtzee_bonus < 0:
            raise ValueError("Yahtzee bonus must be non-negative.")

    @property
    def remaining_categories(self) -> list[str]:
        """Return categories that have not been used yet."""

        return [
            category
            for category, score in self.scorecard.items()
            if score is None
        ]

    @property
    def is_terminal(self) -> bool:
        """Check whether all 13 scorecard categories are filled."""

        return len(self.remaining_categories) == 0

    @property
    def upper_bonus(self) -> int:
        """Return the 35-point upper section bonus when earned."""

        return 35 if self.upper_total >= 63 else 0

    @property
    def total_score(self) -> int:
        """Calculate the current total game score."""

        recorded_score = sum(
            score
            for score in self.scorecard.values()
            if score is not None
        )

        return (
            recorded_score
            + self.upper_bonus
            + self.yahtzee_bonus
        )
