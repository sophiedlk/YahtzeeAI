
"""Convert competition JSON requests into Yahtzee agent decisions."""

from collections import Counter

from game_state import CATEGORIES, GameState


def _get_field(data, primary, alternative=None):
    """Read a field, optionally accepting an alternative name."""

    if primary in data:
        return data[primary]

    if alternative is not None and alternative in data:
        return data[alternative]

    raise ValueError(f"Missing required field: {primary}")


def parse_request(data):
    """Validate a JSON request and create a GameState."""

    if not isinstance(data, dict):
        raise ValueError("Request must be a JSON object.")

    version = data.get("version")
    if type(version) is not int or version != 1:
        raise ValueError("Only interface version 1 is supported.")

    dice = data.get("dice")
    if not isinstance(dice, list):
        raise ValueError("'dice' must be a list.")

    scorecard = data.get("scorecard")
    if not isinstance(scorecard, dict):
        raise ValueError("'scorecard' must be an object.")

    if set(scorecard.keys()) != set(CATEGORIES):
        raise ValueError("Scorecard must contain exactly 13 categories.")

    upper_total = _get_field(
        data, "upper_total", "total_upper"
    )

    yahtzee_bonus = _get_field(
        data, "yahtzee_bonus", "bonus_yahtzee"
    )

    legal_categories = _get_field(
        data, "legal_categories", "categories_legal"
    )

    if not isinstance(legal_categories, list):
        raise ValueError("'legal_categories' must be a list.")

    if not legal_categories:
        raise ValueError("At least one legal category is required.")

    if len(set(legal_categories)) != len(legal_categories):
        raise ValueError("Legal categories must not contain duplicates.")

    for category in legal_categories:
        if category not in CATEGORIES:
            raise ValueError(f"Unknown category: {category}")

        if scorecard[category] is not None:
            raise ValueError(
                f"Legal category is already filled: {category}"
            )

    state = GameState(
        dice=tuple(dice),
        turn=data.get("turn"),
        roll=data.get("roll"),
        scorecard=dict(scorecard),
        upper_total=upper_total,
        yahtzee_bonus=yahtzee_bonus,
    )

    return state, legal_categories


def convert_action(action, dice, roll):
    """
    Convert the internal agent action to the competition response.

    Internal reroll action:
        {"type": "reroll", "keep": (3, 4)}

    Competition response:
        {"action": "reroll", "indices": [0, 3, 4]}
    """

    if not isinstance(action, dict):
        raise ValueError("Agent returned an invalid action.")

    action_type = action.get("type")

    if action_type == "score":
        category = action.get("category")

        if not isinstance(category, str):
            raise ValueError("Invalid scoring category.")

        return {
            "action": "score",
            "category": category,
        }

    if action_type == "reroll":
        if roll >= 3:
            raise ValueError("Reroll is not allowed after roll 3.")

        kept_dice = action.get("keep")

        if not isinstance(kept_dice, (tuple, list)):
            raise ValueError("Invalid kept dice.")

        keep_counts = Counter(kept_dice)
        available_counts = Counter(dice)

        for face, count in keep_counts.items():
            if type(face) is not int or not 1 <= face <= 6:
                raise ValueError("Invalid kept die value.")

            if count > available_counts[face]:
                raise ValueError("Agent tried to keep unavailable dice.")

        indices = []

        for index, die in enumerate(dice):
            if keep_counts[die] > 0:
                keep_counts[die] -= 1
            else:
                indices.append(index)

        return {
            "action": "reroll",
            "indices": indices,
        }

    raise ValueError(f"Unknown action type: {action_type}")


def process_request(data, agent):
    """Process one request and return one competition response."""

    state, legal_categories = parse_request(data)

    action = agent.choose_action(
        state,
        legal_categories,
    )

    return convert_action(
        action,
        state.dice,
        state.roll,
    )
