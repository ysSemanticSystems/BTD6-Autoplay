"""macOS input backend. Replaces pydirectinput + the Windows `keyboard` module."""
from __future__ import annotations

import time

import pyautogui

from config import PYAUTOGUI_FAILSAFE
from screen import get_screen

pyautogui.FAILSAFE = PYAUTOGUI_FAILSAFE
pyautogui.PAUSE = 0.02


def click(position, clicks: int = 1, interval: float = 0.05) -> None:
    x, y = int(position[0]), int(position[1])
    pyautogui.moveTo(x, y, duration=0.05)
    pyautogui.click(x, y, clicks=clicks, interval=interval)


def click_design(position, clicks: int = 1) -> tuple[int, int]:
    """Click a coordinate authored for 1920x1080."""
    x, y = get_screen().to_logical(position[0], position[1])
    click((x, y), clicks=clicks)
    return x, y


def press(key: str, presses: int = 1) -> None:
    normalized = key.lower().strip()
    if normalized in {"ctrl tab", "ctrl+tab"}:
        pyautogui.hotkey("ctrl", "tab")
        return
    if normalized in {"shift tab", "shift+tab"}:
        pyautogui.hotkey("shift", "tab")
        return
    pyautogui.press(normalized if len(normalized) == 1 else key, presses=presses)


def tap(key: str, hold: float = 0.05) -> None:
    pyautogui.keyDown(key)
    time.sleep(hold)
    pyautogui.keyUp(key)


def hotkey(*keys: str) -> None:
    pyautogui.hotkey(*keys)


class _Compat:
    """Drop-in stand-ins so older call sites keep working."""

    def press(self, key, presses: int = 1):
        press(key, presses=presses)

    def keyDown(self, key):
        pyautogui.keyDown(key)

    def keyUp(self, key):
        pyautogui.keyUp(key)

    def release(self, key):
        pyautogui.keyUp(key)


pydirectinput = _Compat()
keyboard = _Compat()
