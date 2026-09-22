#!/usr/bin/env python3
"""Inject a short knowledge briefing at the start of a Cursor session."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "knowledge"


def _load(name: str) -> dict:
    path = ROOT / name
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def _latest(folder: str, limit: int = 3) -> list[str]:
    directory = ROOT / folder
    if not directory.exists():
        return []
    titles = []
    for path in sorted(directory.glob("*.json"), reverse=True)[:limit]:
        try:
            titles.append(json.loads(path.read_text()).get("title") or path.name)
        except json.JSONDecodeError:
            titles.append(path.name)
    return titles


def main() -> None:
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    controls = _load("controls.json").get("ui", {})
    verified = [name for name, row in controls.items() if row.get("status") == "verified"]
    stale = [name for name, row in controls.items() if row.get("status") == "stale"]
    profile = _load("profile.json")
    lines = [
        "BTD6 knowledge briefing.",
        f"Profile last seen {profile.get('last_seen', 'never')}: level {profile.get('level', '?')}, "
        f"XP {profile.get('xp_into_level', '?')}/{profile.get('xp_required_for_next', '?')}. "
        "Primary goal is tower upgrade XP, then Gift Box pops. Refresh profile.json if last_seen is not today.",
        "Verified controls: " + (", ".join(verified) or "none") + ".",
        "Stale controls: " + (", ".join(stale) or "none") + ".",
        "Recent successes: " + ("; ".join(_latest("successes")) or "none") + ".",
        "Recent failures: " + ("; ".join(_latest("failures")) or "none") + ".",
        "Recent errors: " + ("; ".join(_latest("errors")) or "none") + ".",
        "Search with: .venv/bin/python Autoplay/knowledge_store.py \"<question>\".",
        "Do not start Autoplay/play_collection_event.py while Expert maps are locked.",
    ]
    print(json.dumps({"additional_context": " ".join(lines)}))


if __name__ == "__main__":
    main()
