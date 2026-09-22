"""
Persistent notes for this machine's BTD6 bot.

Controls and mechanics live in JSON and are rewritten when a click or rule
stops matching the game. Wins, failures, and errors are separate folders so
later runs can search what already worked.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

AUTOPLAY_DIR = Path(__file__).resolve().parent
if str(AUTOPLAY_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOPLAY_DIR))

from config import PROJECT_ROOT

ROOT = PROJECT_ROOT / "knowledge"
CONTROLS_PATH = ROOT / "controls.json"
MECHANICS_PATH = ROOT / "mechanics.json"
META_PATH = ROOT / "meta.json"
PROFILE_PATH = ROOT / "profile.json"
PROGRESSION_PATH = ROOT / "progression.json"
ROUNDS_PATH = ROOT / "rounds.json"
SUCCESSES = ROOT / "successes"
FAILURES = ROOT / "failures"
ERRORS = ROOT / "errors"

_FOLDERS = {
    "success": SUCCESSES,
    "failure": FAILURES,
    "error": ERRORS,
}


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _read(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def ensure_layout() -> None:
    for folder in _FOLDERS.values():
        folder.mkdir(parents=True, exist_ok=True)


def control(control_id: str) -> dict:
    entry = _read(CONTROLS_PATH).get("ui", {}).get(control_id)
    if entry is None:
        raise KeyError(f"No control named {control_id} in {CONTROLS_PATH}")
    return entry


def position(control_id: str) -> tuple[int, int]:
    point = control(control_id)["position"]
    return int(point[0]), int(point[1])


def mark_control_stale(control_id: str, reason: str, observed: str | None = None) -> Path:
    """A click or hotkey did not do what it used to. Keep the old point and flag it."""
    data = _read(CONTROLS_PATH)
    entry = data.setdefault("ui", {}).setdefault(control_id, {})
    entry["status"] = "stale"
    entry["stale_reason"] = reason
    entry["stale_at"] = _now()
    if observed:
        entry["last_observed"] = observed
    data["updated"] = _now()
    _write(CONTROLS_PATH, data)
    return record(
        "failure",
        title=f"Control {control_id} stopped matching the game",
        detail=reason,
        tags=["control", control_id],
        extra={"control_id": control_id, "observed": observed, "position": entry.get("position")},
    )


def record(
    kind: str,
    title: str,
    detail: str,
    tags: list[str] | None = None,
    extra: dict | None = None,
) -> Path:
    if kind not in _FOLDERS:
        raise ValueError(f"kind must be one of {', '.join(_FOLDERS)}")
    ensure_layout()
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    slug = "".join(ch if ch.isalnum() else "-" for ch in title.lower()).strip("-")[:48]
    path = _FOLDERS[kind] / f"{stamp}-{slug}.json"
    payload = {
        "time": _now(),
        "kind": kind,
        "title": title,
        "tags": tags or [],
        "detail": detail,
    }
    if extra:
        payload["extra"] = extra
    _write(path, payload)
    return path


def record_success(title: str, detail: str, tags: list[str] | None = None, extra: dict | None = None) -> Path:
    return record("success", title, detail, tags, extra)


def record_failure(title: str, detail: str, tags: list[str] | None = None, extra: dict | None = None) -> Path:
    return record("failure", title, detail, tags, extra)


def record_error(title: str, detail: str, tags: list[str] | None = None, extra: dict | None = None) -> Path:
    return record("error", title, detail, tags, extra)


def _iter_docs():
    for path in (CONTROLS_PATH, MECHANICS_PATH, META_PATH, PROFILE_PATH, PROGRESSION_PATH, ROUNDS_PATH):
        if path.exists():
            yield path, path.stem
    for kind, folder in _FOLDERS.items():
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.json")):
            yield path, kind


def search(query: str, kind: str | None = None) -> list[dict]:
    """Case-insensitive search across controls, mechanics, meta, profile, progression, rounds, and the three logs."""
    needle = query.lower().strip()
    hits = []
    for path, doc_kind in _iter_docs():
        if kind and doc_kind != kind and path.stem != kind:
            continue
        text = path.read_text()
        if needle and needle not in text.lower():
            continue
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = {"raw": text[:240]}
        title = data.get("title") or data.get("id") or path.stem
        hits.append({
            "kind": doc_kind,
            "path": str(path.relative_to(PROJECT_ROOT)),
            "title": title,
            "snippet": _snippet(text, needle),
        })
    return hits


def _snippet(text: str, needle: str, radius: int = 90) -> str:
    if not needle:
        return " ".join(text.split())[: radius * 2]
    lower = text.lower()
    at = lower.find(needle)
    if at < 0:
        return " ".join(text.split())[: radius * 2]
    start = max(0, at - radius)
    end = min(len(text), at + len(needle) + radius)
    chunk = " ".join(text[start:end].split())
    return ("…" if start else "") + chunk + ("…" if end < len(text) else "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Search the BTD6 knowledge folders")
    parser.add_argument("query", nargs="?", default="", help="Text to find")
    parser.add_argument(
        "--kind",
        choices=["controls", "mechanics", "meta", "profile", "progression", "rounds", "success", "failure", "error"],
        help="Limit to one file or log folder",
    )
    args = parser.parse_args()
    hits = search(args.query, args.kind)
    if not hits:
        print("No matches.")
        return
    for hit in hits:
        print(f"[{hit['kind']}] {hit['title']}")
        print(f"  {hit['path']}")
        print(f"  {hit['snippet']}")


if __name__ == "__main__":
    main()
