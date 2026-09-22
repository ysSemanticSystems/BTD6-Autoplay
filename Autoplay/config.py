"""
Machine + September 2026 runtime config for this Mac mini.

Detected hardware: Mac16,11 (Mac mini, Apple M4 Pro, 12 CPU / 16 GPU, 24 GB).
BTD6 is the Steam macOS build. LM Studio serves OpenAI-compatible APIs on :1234.
"""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUTOPLAY_DIR = Path(__file__).resolve().parent
REFERENCE_DIR = AUTOPLAY_DIR / "reference_images"

# Game was authored against 1920x1080 windowed/fullscreen. All action-script
# and menu coordinates are in this design space and get scaled at runtime.
DESIGN_WIDTH = 1920
DESIGN_HEIGHT = 1080

# Collection farming always uses Hard Standard (round 3-80, 108% of Medium prices).
GAME_MODE = os.environ.get("BTD6_GAME_MODE", "hard")

# Homebrew tesseract on this machine.
TESSERACT_CMD = os.environ.get("TESSERACT_CMD", "/opt/homebrew/bin/tesseract")

# LM Studio local server. None of the 27B/35B models fit comfortably next to
# BTD6 on 24 GB unified memory. Gemma 4 12B is the vision model that does.
LMSTUDIO_BASE_URL = os.environ.get("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
LMSTUDIO_API_KEY = os.environ.get("LMSTUDIO_API_KEY", "lm-studio")
LMSTUDIO_VISION_MODEL = os.environ.get("LMSTUDIO_VISION_MODEL", "btd6-vision")
LMSTUDIO_FAST_MODEL = os.environ.get("LMSTUDIO_FAST_MODEL", "qwen3.8-9b-distill")
LMSTUDIO_TIMEOUT = float(os.environ.get("LMSTUDIO_TIMEOUT", "45"))

# Use the local vision model when Tesseract fails or templates miss.
USE_LMSTUDIO_VISION = os.environ.get("BTD6_USE_LMSTUDIO", "1") != "0"

# Fail-safe: slam mouse into a corner to abort pyautogui.
PYAUTOGUI_FAILSAFE = True

BTD6_APP = Path.home() / (
    "Library/Application Support/Steam/steamapps/common/BloonsTD6/BloonsTD6.app"
)
