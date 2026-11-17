import random
from typing import List, Optional, Sequence

# attacker_type -> {defender_type: multiplier}
TYPE_CHART = {
    "normal": {"rock": 0.5, "ghost": 0.0, "steel": 0.5},
    "fire": {"fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 2.0, "bug": 2.0,
             "rock": 0.5, "dragon": 0.5, "steel": 2.0},
    "water": {"fire": 2.0, "water": 0.5, "grass": 0.5, "ground": 2.0,
              "rock": 2.0, "dragon": 0.5},
    "electric": {"water": 2.0, "electric": 0.5, "grass": 0.5, "ground": 0.0,
                 "flying": 2.0, "dragon": 0.5},
    "grass": {"fire": 0.5, "water": 2.0, "grass": 0.5, "poison": 0.5,
              "ground": 2.0, "flying": 0.5, "bug": 0.5, "rock": 2.0,
              "dragon": 0.5, "steel": 0.5},
    "ice": {"fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 0.5, "ground": 2.0,
            "flying": 2.0, "dragon": 2.0, "steel": 0.5},
    "fighting": {"normal": 2.0, "ice": 2.0, "poison": 0.5, "flying": 0.5,
                 "psychic": 0.5, "bug": 0.5, "rock": 2.0, "ghost": 0.0,
                 "dark": 2.0, "steel": 2.0, "fairy": 0.5},
    "poison": {"grass": 2.0, "poison": 0.5, "ground": 0.5, "rock": 0.5,
               "ghost": 0.5, "steel": 0.0, "fairy": 2.0},
    "ground": {"fire": 2.0, "electric": 2.0, "grass": 0.5, "poison": 2.0,
               "flying": 0.0, "bug": 0.5, "rock": 2.0, "steel": 2.0},
    "flying": {"electric": 0.5, "grass": 2.0, "ice": 0.5, "fighting": 2.0,
               "bug": 2.0, "rock": 0.5, "steel": 0.5},
    "psychic": {"fighting": 2.0, "poison": 2.0, "psychic": 0.5, "dark": 0.0,
                "steel": 0.5},
    "bug": {"fire": 0.5, "grass": 2.0, "fighting": 0.5, "poison": 0.5,
            "flying": 0.5, "psychic": 2.0, "ghost": 0.5, "dark": 2.0,
            "steel": 0.5, "fairy": 0.5},
    "rock": {"fire": 2.0, "ice": 2.0, "fighting": 0.5, "ground": 0.5,
             "flying": 2.0, "bug": 2.0, "steel": 0.5},
    "ghost": {"normal": 0.0, "ghost": 2.0, "psychic": 2.0, "dark": 0.5},
    "dragon": {"dragon": 2.0, "steel": 0.5, "fairy": 0.0},
    "dark": {"fighting": 0.5, "psychic": 2.0, "ghost": 2.0, "dark": 0.5,
             "fairy": 0.5},
    "steel": {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2.0,
              "rock": 2.0, "steel": 0.5, "fairy": 2.0},
    "fairy": {"fire": 0.5, "fighting": 2.0, "poison": 0.5, "ground": 0.5,
              "dragon": 2.0, "dark": 2.0, "steel": 0.5},
}

DEFAULT_LEVEL = 50
RANDOM_MIN = 0.85
RANDOM_MAX = 1.0


def type_effectiveness(move_type: str, defender_types: Sequence[str]) -> float:
    multiplier = 1.0
    chart = TYPE_CHART.get(move_type, {})
    for defender_type in defender_types:
        multiplier *= chart.get(defender_type, 1.0)
    return multiplier


def calculate_damage(
    move,
    attacker,
    defender,
    level: int = DEFAULT_LEVEL,
    random_factor: Optional[float] = None,
) -> int:
    """Return server-calculated damage for a single attack."""
    if move.power is None or move.power <= 0:
        return 0

    if random_factor is None:
        random_factor = random.uniform(RANDOM_MIN, RANDOM_MAX)

    attack = getattr(attacker, "base_attack", 50)
    defense = getattr(defender, "base_defense", 50)

    base = (((2 * level / 5 + 2) * move.power * attack / defense) / 50) + 2
    effectiveness = type_effectiveness(move.move_type, defender.types)
    damage = base * effectiveness * random_factor

    if effectiveness <= 0:
        return 0
    return max(1, int(damage))
