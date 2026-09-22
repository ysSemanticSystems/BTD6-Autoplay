---
name: btd6-knowledge
description: >-
  Search and update this repo's BTD6 knowledge store (controls, mechanics,
  strategies, successes, failures, errors). Use when a click misses, the UI
  changes, a game wins or loses, prices or hotkeys change, or before measuring
  the screen again.
---

# BTD6 knowledge

Search before measuring or editing a coordinate:

```bash
.venv/bin/python Autoplay/knowledge_store.py "<question>"
```

`--kind` is `controls`, `mechanics`, `meta`, `profile`, `progression`, `rounds`, `success`, `failure`, or `error`.

## Write a log

Use `record_success`, `record_failure`, or `record_error` from `Autoplay/knowledge_store.py`. One event, one file. Include the control id when a click was involved.

When a verified click does not produce the expected screen, call `mark_control_stale`. Keep the old `position` until a new screenshot confirms the replacement, then update `knowledge/controls.json` and set `status` back to `verified`.

Update `knowledge/mechanics.json` when a game rule changed. Update `knowledge/meta.json` when a strategy becomes safe or unsafe.

Profile and the tower tree are `knowledge/profile.json` and `knowledge/progression.json`. Refresh the profile when `last_seen` is not today and the home screen is visible. The primary run goal is one tower's upgrade XP on Hard through round 80. Before the run, check `knowledge/rounds.json`: a specialty tower is required when the target cannot hit a property on that list. Gift Box pops are a separate counter and only move the selected tower.

Do not store screenshots or the account name in these files.
