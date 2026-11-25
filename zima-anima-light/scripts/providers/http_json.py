"""Small HTTP helpers without third-party deps."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class ProviderError(RuntimeError):
    pass


def post_json(url: str, payload: dict[str, Any], *, headers: dict[str, str], timeout: int = 120) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={**headers, "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read()[:500].decode("utf-8", errors="replace")
        raise ProviderError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ProviderError(str(exc.reason)) from exc
    return json.loads(body.decode("utf-8"))
