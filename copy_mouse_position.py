"""Copy the current mouse position. F8 on macOS (no Insert key on Apple keyboards)."""
from __future__ import annotations

import time

import pyautogui
import pyperclip
from pynput import keyboard

print("Running copy_mouse_position.py")
print("Press F8 to copy the current mouse position. Ctrl+C in this terminal to quit.")


def on_press(key):
    if key != keyboard.Key.f8:
        return
    x, y = pyautogui.position()
    pyperclip.copy(f"{x}, {y}")
    print(f"Copied mouse position ({x}, {y})")


with keyboard.Listener(on_press=on_press) as listener:
    try:
        while listener.running:
            time.sleep(0.2)
    except KeyboardInterrupt:
        listener.stop()
