#!/usr/bin/python3
"""Sanity-check this Mac mini + LM Studio + BTD6 setup."""
from __future__ import annotations

import platform
import sys
from pathlib import Path

AUTOPLAY_DIR = Path(__file__).resolve().parent
if str(AUTOPLAY_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOPLAY_DIR))

from config import BTD6_APP, GAME_MODE, LMSTUDIO_VISION_MODEL, TESSERACT_CMD
from costs import scale_cost
from lmstudio_client import is_available, list_models
from monkey_info.monkey_info import cost_of
from screen import detect_screen


def main() -> None:
    screen = detect_screen()
    models = list_models()
    print("machine:", platform.platform())
    print("python:", sys.version.split()[0])
    print(f"screen logical={screen.logical_width}x{screen.logical_height} "
          f"pixels={screen.pixel_width}x{screen.pixel_height} scale={screen.scale:.2f}")
    print("tesseract:", TESSERACT_CMD)
    print("btd6 app:", "yes" if BTD6_APP.exists() else f"missing ({BTD6_APP})")
    print("game mode:", GAME_MODE)
    print("hard dart / ninja / psi:", cost_of("Dart Monkey", "place"),
          cost_of("Ninja Monkey", "place"), cost_of("Hero", "Psi"))
    print("heli hard (was hardcoded 1070):", scale_cost(1500))
    print("lm studio models:", models or "server not reachable")
    print("vision model loaded:", is_available(LMSTUDIO_VISION_MODEL),
          f"({LMSTUDIO_VISION_MODEL})")
    if screen.logical_width != 1920 or screen.logical_height != 1080:
        print("note: scripts were authored at 1920x1080; clicks will be scaled.")


if __name__ == "__main__":
    main()
