Report where this BTD6 bot stands. Do not click the game.

1. Run `.venv/bin/python Autoplay/diagnose.py`.
2. Run `.venv/bin/python Autoplay/knowledge_store.py "" --kind meta` and the same for `failure` and `success`. If an empty query is awkward, search `expert`, `play`, and `badge`.
3. Read `knowledge/profile.json`. If `last_seen` is not today, say the profile is stale.
4. Summarize: display and vision model, level and XP bar, which controls are verified versus stale, whether Expert maps are still locked, and the active XP plan from `knowledge/meta.json`.
