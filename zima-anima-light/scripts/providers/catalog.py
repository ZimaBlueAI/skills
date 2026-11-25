"""Capability catalog (declared, not health-probed)."""
from __future__ import annotations

import os
from typing import Any

from config_env import truthy


def capabilities() -> list[dict[str, Any]]:
    rows = [
        {
            "id": "seedream",
            "kind": "image",
            "label": "Seedream",
            "enabled": truthy("ZIMA_LIGHT_SEEDREAM_ENABLED"),
            "model": os.environ.get("ZIMA_LIGHT_SEEDREAM_MODEL", "seedream-4-5"),
            "modes": ["text_to_image", "image_edit"],
        },
        {
            "id": "qwen_image",
            "kind": "image",
            "label": "Qwen-Image / Z-Image",
            "enabled": truthy("ZIMA_LIGHT_QWEN_IMAGE_ENABLED"),
            "model": os.environ.get("ZIMA_LIGHT_QWEN_IMAGE_MODEL", "qwen-image"),
            "modes": ["text_to_image", "image_edit"],
        },
        {
            "id": "seedance",
            "kind": "video",
            "label": "Seedance",
            "enabled": truthy("ZIMA_LIGHT_SEEDANCE_ENABLED"),
            "model": os.environ.get("ZIMA_LIGHT_SEEDANCE_MODEL", "seedance-1-0-pro"),
            "modes": ["text_to_video", "image_to_video"],
        },
        {
            "id": "music",
            "kind": "music",
            "label": os.environ.get("ZIMA_LIGHT_MUSIC_PROVIDER", "haimian"),
            "enabled": truthy("ZIMA_LIGHT_MUSIC_ENABLED"),
            "modes": ["music"],
        },
        {
            "id": "tts",
            "kind": "voice",
            "label": os.environ.get("ZIMA_LIGHT_TTS_PROVIDER", "qwen3_tts"),
            "enabled": truthy("ZIMA_LIGHT_TTS_ENABLED"),
            "modes": ["tts"],
        },
    ]
    return rows


def route_image(*, edit: bool) -> str | None:
    caps = {c["id"]: c for c in capabilities() if c["kind"] == "image" and c["enabled"]}
    if "seedream" in caps:
        return "seedream"
    if "qwen_image" in caps:
        return "qwen_image"
    return None
