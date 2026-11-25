"""Minimal dotenv loader for Zima Anima Light."""
from __future__ import annotations

import os
from pathlib import Path


def env_path() -> Path:
    override = os.environ.get("ZIMA_LIGHT_ENV_FILE") or os.environ.get("CINEMATIC_VIDEO_ENV_FILE")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".zimablueai_skills" / ".env.local"


# Prefer ZIMA_LIGHT_* ; fall back to existing PCV keys when light keys absent.
_ALIASES = {
    "ZIMA_LIGHT_SEEDREAM_ENABLED": "PCV_SEEDREAM_IMAGE_ENABLED",
    "ZIMA_LIGHT_SEEDREAM_BASE_URL": "PCV_SEEDREAM_IMAGE_BASE_URL",
    "ZIMA_LIGHT_SEEDREAM_MODEL": "PCV_SEEDREAM_IMAGE_MODEL",
    "ZIMA_LIGHT_SEEDREAM_API_KEY": "PCV_SEEDREAM_IMAGE_API_KEY",
    "ZIMA_LIGHT_SEEDANCE_ENABLED": "PCV_SEEDANCE_ENABLED",
    "ZIMA_LIGHT_SEEDANCE_MODEL": "PCV_SEEDANCE_MODEL",
    "ZIMA_LIGHT_SEEDANCE_API_KEY": "PCV_SEEDANCE_API_KEY",
}


def load_env(path: Path | None = None) -> dict[str, str]:
    target = path or env_path()
    values: dict[str, str] = {}
    if target.is_file():
        for raw in target.read_text(encoding="utf-8-sig").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            values[key] = val
            os.environ.setdefault(key, val)
    for light_key, pcv_key in _ALIASES.items():
        if not os.environ.get(light_key) and os.environ.get(pcv_key):
            os.environ[light_key] = os.environ[pcv_key]
            values.setdefault(light_key, os.environ[pcv_key])
    return values


def truthy(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}
