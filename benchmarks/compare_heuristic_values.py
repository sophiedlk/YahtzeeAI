
"""Compare baseline and improved Yahtzee heuristic values directly."""

import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from game_state import GameState, CATEGORIES, UPPER_CATEGORIES

import heuristic_baseline as baseline
import heuristic as improved
CATEGORY_MAX = {
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


def make_state(scorecard, dice=(1, 2, 3, 4, 5), yahtzee_bonus=0):
    upper_total = sum(
        scorecard[category] or 0
        for category in UPPER_CATEGORIES
    )

    filled_count = sum(
        value is not None for value in scorecard.values()
    )

    return GameState(
        dice=tuple(dice),
        turn=min(filled_count + 1, 13),
        roll=1,
        scorecard=scorecard.copy(),
        upper_total=upper_total,
        yahtzee_bonus=yahtzee_bonus,
    )


def random_scorecard(rng):
    scorecard = {category: None for category in CATEGORIES}

    # Generate a partially completed scorecard.
    for category in CATEGORIES:
        if rng.random() < 0.55:
            maximum = CATEGORY_MAX[category]
            scorecard[category] = rng.randint(0, maximum)

    return scorecard


def main():
    rng = random.Random(2026)

    states = []

    # A completely empty scorecard.
    states.append(
        make_state(
            {category: None for category in CATEGORIES},
            dice=(1, 2, 3, 4, 5),
        )
    )

    # Low upper-section progress.
    card = {category: None for category in CATEGORIES}
    card.update({"ones": 1, "twos": 4, "threes": 6})
    states.append(make_state(card, dice=(1, 1, 2, 3, 4)))

    # Upper-section bonus already reached.
    card = {category: None for category in CATEGORIES}
    card.update({
        "ones": 3,
        "twos": 6,
        "threes": 9,
        "fours": 12,
        "fives": 15,
        "sixes": 18,
    })
    states.append(make_state(card, dice=(5, 5, 5, 2, 3)))

    # Several lower categories already filled.
    card = {category: None for category in CATEGORIES}
    card.update({
        "ones": 2,
        "twos": 6,
        "three_of_a_kind": 24,
        "full_house": 25,
        "small_straight": 30,
        "chance": 22,
    })
    states.append(make_state(card, dice=(2, 3, 4, 5, 6)))

    # Generate additional reproducible test states.
    for _ in range(96):
        scorecard = random_scorecard(rng)
        dice = tuple(rng.randint(1, 6) for _ in range(5))
        states.append(make_state(scorecard, dice=dice))

    differences = []

    print("=" * 75)
    print("DIRECT HEURISTIC VALUE COMPARISON")
    print("=" * 75)

    for index, state in enumerate(states, start=1):
        baseline_value = baseline.evaluate_state(state)
        improved_value = improved.evaluate_state(state)

        difference = improved_value - baseline_value
        differences.append(abs(difference))

        print(
            f"State {index:03d} | "
            f"Baseline: {baseline_value:10.4f} | "
            f"Improved: {improved_value:10.4f} | "
            f"Difference: {difference:+10.6f}"
        )

    different_count = sum(value > 1e-9 for value in differences)

    print("\n" + "=" * 75)
    print("SUMMARY")
    print("=" * 75)
    print(f"Total states tested: {len(states)}")
    print(f"States with different values: {different_count}")
    print(f"States with identical values: {len(states) - different_count}")
    print(f"Maximum absolute difference: {max(differences):.8f}")
    print(f"Average absolute difference: {sum(differences) / len(differences):.8f}")


if __name__ == "__main__":
    main()
