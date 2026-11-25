"""Seedance video task submit (dry-run first; live when configured)."""
from __future__ import annotations

import os
from typing import Any

from providers.http_json import ProviderError, post_json


def submit(prompt: str, *, image_url: str | None = None, dry_run: bool = False) -> dict[str, Any]:
    base = (os.environ.get("ZIMA_LIGHT_SEEDANCE_BASE_URL") or "").rstrip("/")
    model = os.environ.get("ZIMA_LIGHT_SEEDANCE_MODEL") or "seedance-1-0-pro"
    key = os.environ.get("ZIMA_LIGHT_SEEDANCE_API_KEY") or ""
    plan = {
        "provider": "seedance",
        "model": model,
        "prompt": prompt,
        "image_url": image_url,
        "mode": "image_to_video" if image_url else "text_to_video",
    }
    if dry_run:
        return {"dry_run": True, **plan}
    if not base or not key:
        raise ProviderError("Seedance needs base URL and API key")
    # Generic content generation envelope; concrete Ark path may vary by account.
    payload = {"model": model, "content": [{"type": "text", "text": prompt}]}
    if image_url:
        payload["content"].append({"type": "image_url", "image_url": {"url": image_url}})
    response = post_json(
        f"{base}/contents/generations/tasks",
        payload,
        headers={"Authorization": f"Bearer {key}"},
    )
    return {"dry_run": False, **plan, "response_keys": sorted(response.keys()), "task": response}
