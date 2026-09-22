#
# Medium-difficulty prices as of Blooncyclopedia, September 2026.
# Hard / Impoppable / Easy are computed at lookup time (108% / 120% / 85%, nearest $5).
# Monkey Knowledge discounts are NOT applied.
#
import sys
from pathlib import Path

_AUTOPLAY = Path(__file__).resolve().parent.parent
if str(_AUTOPLAY) not in sys.path:
    sys.path.insert(0, str(_AUTOPLAY))

from costs import scale_cost
from config import GAME_MODE

# Values are Medium. Use cost_of() / get_monkey_costs() for the active difficulty.
_MEDIUM = {
    "Hero": {
        "Psi": 1000,
    },
    "Dart Monkey": {
        "category": "primary",
        "place": 200,
        "top1": 140, "top2": 200, "top3": 320, "top4": 1800, "top5": 15000,
        "middle1": 100, "middle2": 190, "middle3": 450, "middle4": 7200, "middle5": 45000,
        "bottom1": 90, "bottom2": 200, "bottom3": 575, "bottom4": 2050, "bottom5": 21500,
    },
    "Boomerang Monkey": {
        "category": "primary",
        "place": 315,
        "top1": 200, "top2": 280, "top3": 600, "top4": 2000, "top5": 32500,
        "middle1": 175, "middle2": 250, "middle3": 1250, "middle4": 4200, "middle5": 35000,
        "bottom1": 100, "bottom2": 300, "bottom3": 1300, "bottom4": 2700, "bottom5": 50000,
    },
    "Bomb Shooter": {
        "category": "primary",
        "place": 525,
        "top1": 250, "top2": 650, "top3": 1100, "top4": 2800, "top5": 55000,
        "middle1": 250, "middle2": 400, "middle3": 1000, "middle4": 3450, "middle5": 26000,
        "bottom1": 200, "bottom2": 300, "bottom3": 700, "bottom4": 2500, "bottom5": 30000,
    },
    "Tack Shooter": {
        "category": "primary",
        "place": 280,
        "top1": 150, "top2": 220, "top3": 600, "top4": 3500, "top5": 45500,
        "middle1": 100, "middle2": 225, "middle3": 550, "middle4": 2700, "middle5": 15000,
        "bottom1": 150, "bottom2": 150, "bottom3": 450, "bottom4": 3200, "bottom5": 20000,
    },
    "Ice Monkey": {
        "category": "primary",
        "place": 500,
        "top1": 150, "top2": 350, "top3": 1500, "top4": 2300, "top5": 28000,
        "middle1": 200, "middle2": 300, "middle3": 2750, "middle4": 4750, "middle5": 21000,
        "bottom1": 150, "bottom2": 200, "bottom3": 1900, "bottom4": 2750, "bottom5": 30000,
    },
    "Glue Gunner": {
        "category": "primary",
        "place": 275,
        "top1": 200, "top2": 300, "top3": 2000, "top4": 5000, "top5": 22500,
        "middle1": 100, "middle2": 970, "middle3": 1950, "middle4": 4000, "middle5": 16000,
        "bottom1": 280, "bottom2": 400, "bottom3": 3600, "bottom4": 4000, "bottom5": 24000,
    },
    "Desperado": {
        "category": "primary",
        "place": 340,
        "top1": 200, "top2": 200, "top3": 1200, "top4": 5800, "top5": 16500,
        "middle1": 150, "middle2": 350, "middle3": 3000, "middle4": 6000, "middle5": 42000,
        "bottom1": 220, "bottom2": 280, "bottom3": 2100, "bottom4": 9500, "bottom5": 31000,
    },
    "Sniper Monkey": {
        "category": "military",
        "place": 350,
        "top1": 350, "top2": 1300, "top3": 2200, "top4": 6300, "top5": 32000,
        "middle1": 250, "middle2": 450, "middle3": 2100, "middle4": 7600, "middle5": 12000,
        "bottom1": 450, "bottom2": 450, "bottom3": 2700, "bottom4": 4100, "bottom5": 14900,
    },
    "Monkey Sub": {
        "category": "military",
        "place": 325,
        "top1": 130, "top2": 500, "top3": 700, "top4": 2400, "top5": 28000,
        "middle1": 450, "middle2": 300, "middle3": 1350, "middle4": 13000, "middle5": 29000,
        "bottom1": 450, "bottom2": 1000, "bottom3": 1100, "bottom4": 2500, "bottom5": 25000,
    },
    "Monkey Buccaneer": {
        "category": "military",
        "place": 500,
        "top1": 275, "top2": 425, "top3": 3350, "top4": 8000, "top5": 26000,
        "middle1": 550, "middle2": 500, "middle3": 900, "middle4": 3900, "middle5": 29000,
        "bottom1": 200, "bottom2": 350, "bottom3": 2400, "bottom4": 5500, "bottom5": 23000,
    },
    "Monkey Ace": {
        "category": "military",
        "place": 800,
        "top1": 450, "top2": 550, "top3": 1000, "top4": 3300, "top5": 42500,
        "middle1": 200, "middle2": 350, "middle3": 900, "middle4": 16000, "middle5": 26000,
        "bottom1": 500, "bottom2": 550, "bottom3": 2550, "bottom4": 23400, "bottom5": 90000,
    },
    "Heli Pilot": {
        "category": "military",
        "place": 1500,
        "top1": 800, "top2": 500, "top3": 1450, "top4": 20000, "top5": 45000,
        "middle1": 300, "middle2": 600, "middle3": 3500, "middle4": 9500, "middle5": 30000,
        "bottom1": 250, "bottom2": 350, "bottom3": 3400, "bottom4": 8500, "bottom5": 35000,
    },
    "Mortar Monkey": {
        "category": "military",
        "place": 750,
        "top1": 300, "top2": 500, "top3": 825, "top4": 7000, "top5": 36000,
        "middle1": 400, "middle2": 500, "middle3": 900, "middle4": 6500, "middle5": 38000,
        "bottom1": 200, "bottom2": 400, "bottom3": 1100, "bottom4": 9500, "bottom5": 40000,
    },
    "Dartling Gunner": {
        "category": "military",
        "place": 850,
        "top1": 300, "top2": 900, "top3": 3000, "top4": 11750, "top5": 75000,
        "middle1": 250, "middle2": 950, "middle3": 4500, "middle4": 5000, "middle5": 65000,
        "bottom1": 150, "bottom2": 1200, "bottom3": 3000, "bottom4": 12000, "bottom5": 58000,
    },
    "Wizard Monkey": {
        "category": "magic",
        "place": 375,
        "top1": 175, "top2": 450, "top3": 1450, "top4": 10000, "top5": 32000,
        "middle1": 300, "middle2": 800, "middle3": 3300, "middle4": 6000, "middle5": 50000,
        "bottom1": 300, "bottom2": 300, "bottom3": 1500, "bottom4": 2800, "bottom5": 26500,
    },
    "Super Monkey": {
        "category": "magic",
        "place": 2500,
        "top1": 2000, "top2": 2500, "top3": 20000, "top4": 100000, "top5": 500000,
        "middle1": 1500, "middle2": 1900, "middle3": 7500, "middle4": 25000, "middle5": 70000,
        "bottom1": 3000, "bottom2": 1200, "bottom3": 5600, "bottom4": 55555, "bottom5": 165650,
    },
    "Ninja Monkey": {
        "category": "magic",
        "place": 400,
        "top1": 350, "top2": 350, "top3": 900, "top4": 2750, "top5": 35000,
        "middle1": 250, "middle2": 400, "middle3": 1200, "middle4": 5200, "middle5": 22000,
        "bottom1": 300, "bottom2": 450, "bottom3": 2250, "bottom4": 5000, "bottom5": 40000,
    },
    "Alchemist": {
        "category": "magic",
        "place": 550,
        "top1": 250, "top2": 350, "top3": 1400, "top4": 2850, "top5": 48000,
        "middle1": 250, "middle2": 475, "middle3": 2800, "middle4": 4200, "middle5": 45000,
        "bottom1": 650, "bottom2": 450, "bottom3": 1000, "bottom4": 2750, "bottom5": 40000,
    },
    "Druid": {
        "category": "magic",
        "place": 400,
        "top1": 350, "top2": 850, "top3": 1700, "top4": 4500, "top5": 60000,
        "middle1": 250, "middle2": 350, "middle3": 1050, "middle4": 4900, "middle5": 35000,
        "bottom1": 100, "bottom2": 300, "bottom3": 600, "bottom4": 2350, "bottom5": 45000,
    },
    "Mermonkey": {
        "category": "magic",
        "place": 475,
        "top1": 150, "top2": 250, "top3": 1800, "top4": 4200, "top5": 23000,
        "middle1": 200, "middle2": 225, "middle3": 2000, "middle4": 8000, "middle5": 52000,
        "bottom1": 200, "bottom2": 280, "bottom3": 2000, "bottom4": 7600, "bottom5": 25000,
    },
    "Skywarden": {
        "category": "magic",
        "place": 205,
        "top1": 110, "top2": 215, "top3": 1650, "top4": 3300, "top5": 19000,
        "middle1": 175, "middle2": 275, "middle3": 1800, "middle4": 2000, "middle5": 35000,
        "bottom1": 150, "bottom2": 250, "bottom3": 1500, "bottom4": 3900, "bottom5": 20000,
    },
    "Banana Farm": {
        "category": "support",
        "place": 1250,
        "top1": 500, "top2": 600, "top3": 3000, "top4": 19000, "top5": 115000,
        "middle1": 300, "middle2": 800, "middle3": 3650, "middle4": 7200, "middle5": 100000,
        "bottom1": 250, "bottom2": 400, "bottom3": 2700, "bottom4": 15000, "bottom5": 70000,
    },
    "Spike Factory": {
        "category": "support",
        "place": 1000,
        "top1": 800, "top2": 600, "top3": 2300, "top4": 9500, "top5": 125000,
        "middle1": 600, "middle2": 800, "middle3": 2500, "middle4": 7000, "middle5": 41000,
        "bottom1": 150, "bottom2": 400, "bottom3": 1300, "bottom4": 3600, "bottom5": 30000,
    },
    "Monkey Village": {
        "category": "support",
        "place": 1200,
        "top1": 400, "top2": 1500, "top3": 800, "top4": 2500, "top5": 25000,
        "middle1": 250, "middle2": 2000, "middle3": 7500, "middle4": 20000, "middle5": 40000,
        "bottom1": 500, "bottom2": 500, "bottom3": 10000, "bottom4": 3000, "bottom5": 5000,
    },
    "Engineer Monkey": {
        "category": "support",
        "place": 350,
        "top1": 500, "top2": 400, "top3": 575, "top4": 2500, "top5": 32000,
        "middle1": 250, "middle2": 350, "middle3": 900, "middle4": 13500, "middle5": 72000,
        "bottom1": 450, "bottom2": 220, "bottom3": 450, "bottom4": 3600, "bottom5": 45000,
    },
    "Beast Handler": {
        "category": "support",
        "place": 250,
        "top1": 160, "top2": 810, "top3": 2010, "top4": 12500, "top5": 45000,
        "middle1": 175, "middle2": 830, "middle3": 2065, "middle4": 9500, "middle5": 60000,
        "bottom1": 190, "bottom2": 860, "bottom3": 2120, "bottom4": 9000, "bottom5": 30000,
    },
}

# Back-compat alias used by older comments / mental model.
_MEDIUM["Glue Monkey"] = _MEDIUM["Glue Gunner"]


def get_monkey_costs(difficulty: str | None = None) -> dict:
    """Difficulty-scaled copy of the cost table (default: Hard)."""
    mode = difficulty or GAME_MODE
    scaled = {}
    for name, data in _MEDIUM.items():
        row = {}
        for key, value in data.items():
            row[key] = scale_cost(value, mode) if isinstance(value, int) else value
        scaled[name] = row
    return scaled


def cost_of(tower: str, key: str, difficulty: str | None = None) -> int:
    return scale_cost(_MEDIUM[tower][key], difficulty or GAME_MODE)


# Existing scripts import monkey_info as a dict of Hard prices.
monkey_info = get_monkey_costs()
