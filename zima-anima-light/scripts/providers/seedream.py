"""Seedream image adapter (Ark-compatible Images/chat style)."""
from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any

from providers.http_json import ProviderError, post_json


def generate(prompt: str, *, size: str = "1024x1024", dry_run: bool = False) -> dict[str, Any]:
    base = (os.environ.get("ZIMA_LIGHT_SEEDREAM_BASE_URL") or "").rstrip("/")
    model = os.environ.get("ZIMA_LIGHT_SEEDREAM_MODEL") or "seedream-4-5"
    key = os.environ.get("ZIMA_LIGHT_SEEDREAM_API_KEY") or ""
    if dry_run:
        return {"dry_run": True, "provider": "seedream", "model": model, "prompt": prompt, "size": size}
    if not base or not key:
        raise ProviderError("Seedream needs ZIMA_LIGHT_SEEDREAM_BASE_URL and ZIMA_LIGHT_SEEDREAM_API_KEY")
    # Prefer OpenAI-compatible images generations when relay supports it.
    payload = {"model": model, "prompt": prompt, "size": size, "n": 1, "response_format": "b64_json"}
    response = post_json(
        f"{base}/images/generations",
        payload,
        headers={"Authorization": f"Bearer {key}"},
    )
    data = response.get("data") or []
    if not data or not isinstance(data[0], dict):
        raise ProviderError("Seedream response missing image data")
    item = data[0]
    if item.get("b64_json"):
        return {"provider": "seedream", "model": model, "bytes": base64.b64decode(item["b64_json"]), "mime": "image/png"}
    raise ProviderError("Seedream response had no b64_json (url download not enabled in light adapter yet)")


def write_image(result: dict[str, Any], path: Path) -> Path:
    if result.get("dry_run"):
        raise ProviderError("dry_run cannot write image")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(result["bytes"])
    return path
