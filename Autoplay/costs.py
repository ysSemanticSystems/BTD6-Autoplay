"""BTD6 difficulty price conversion. Wiki Medium prices in, Hard (default) out."""
from __future__ import annotations

DIFFICULTY_MULT = {
    "easy": 0.85,
    "medium": 1.0,
    "hard": 1.08,
    "impoppable": 1.20,
}


def scale_cost(medium: int, difficulty: str = "hard") -> int:
    """Hard/Impoppable/Easy prices round to the nearest $5."""
    if medium is None:
        return 0
    factor = DIFFICULTY_MULT.get(difficulty, 1.08)
    return int(round(medium * factor / 5.0) * 5)
