"""Talk to the local LM Studio server for vision OCR and UI state."""
from __future__ import annotations

import base64
import io
import json
import re
from typing import Any

import requests
from PIL import Image

from config import (
    LMSTUDIO_API_KEY,
    LMSTUDIO_BASE_URL,
    LMSTUDIO_TIMEOUT,
    LMSTUDIO_VISION_MODEL,
    USE_LMSTUDIO_VISION,
)


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {LMSTUDIO_API_KEY}",
        "Content-Type": "application/json",
    }


def list_models() -> list[str]:
    try:
        resp = requests.get(f"{LMSTUDIO_BASE_URL}/models", timeout=3)
        resp.raise_for_status()
        return [row["id"] for row in resp.json().get("data", [])]
    except Exception:
        return []


def is_available(model: str | None = None) -> bool:
    if not USE_LMSTUDIO_VISION:
        return False
    models = list_models()
    if not models:
        return False
    if model is None:
        return True
    return model in models or any(model in item for item in models)


def _encode_image(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def chat_vision(prompt: str, image: Image.Image, model: str | None = None, max_tokens: int = 80) -> str:
    payload: dict[str, Any] = {
        "model": model or LMSTUDIO_VISION_MODEL,
        "temperature": 0,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{_encode_image(image)}"},
                    },
                ],
            }
        ],
    }
    resp = requests.post(
        f"{LMSTUDIO_BASE_URL}/chat/completions",
        headers=_headers(),
        json=payload,
        timeout=LMSTUDIO_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def read_money(image: Image.Image) -> int:
    """Read the in-game cash number from a cropped HUD screenshot."""
    text = chat_vision(
        "This is the Bloons TD 6 cash counter. Reply with ONLY the integer cash value. "
        "No $ sign, no commas, no words. If unreadable reply -1.",
        image,
        max_tokens=16,
    )
    digits = re.sub(r"[^\d-]", "", text)
    if digits in {"", "-"}:
        return -1
    try:
        return int(digits)
    except ValueError:
        return -1


def classify_ui(image: Image.Image) -> dict[str, Any]:
    """Ask the local vision model what screen we are on."""
    raw = chat_vision(
        "You are looking at Bloons TD 6 on macOS. Reply with compact JSON only, no markdown. "
        'Keys: screen (one of: gameplay, victory, defeat, map_select, home, collection, unknown), '
        "bonus_rewards (bool), money (int or null), round (int or null).",
        image,
        max_tokens=120,
    )
    match = re.search(r"\{.*\}", raw, flags=re.S)
    if not match:
        return {"screen": "unknown", "raw": raw}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"screen": "unknown", "raw": raw}
