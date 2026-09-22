---
name: btd6-live-screen
description: >-
  Capture or click the live Bloons TD 6 window on this Mac. Use when the user
  says the game is open, asks to learn a button, or a control is stale and
  needs a new coordinate.
---

# Live BTD6 screen

Only do this after the user says the game is open. Screen Recording and Accessibility are granted to Cursor.

1. Capture with `.venv/bin/python` and `PIL.ImageGrab` outside the sandbox (`required_permissions: ["all"]`). Save under `/tmp`, not the repo.
2. Read the image. Find the target by color or by eye. Do not guess a coordinate from the 2020 scripts.
3. Click once with `pyautogui`, then capture again.
4. If the expected screen appeared, write the point into `knowledge/controls.json` with `status: verified` and add a success file.
5. If it did not, call `mark_control_stale` and stop. Do not click a second guess in the same turn.
6. Do not run `Autoplay/play_collection_event.py`. Expert maps stay locked until a success log says one opened.
