#!/usr/bin/env python3
"""Adapter for a local LTX-Video HTTP service (Lightricks/ltx-video).

The service is expected to expose the ai-whiteboard docker contract:
  GET  /health                    -> {"status": "healthy", ...}
  POST /generate  (multipart)     -> {"success": true, "taskId": "...", "status": "queued"}
       fields: prompt (required), negative_prompt, width, height,
               num_frames, frame_rate, seed, file (optional first-frame image)
  GET  /tasks/{task_id}           -> {"status": "queued"|"running"|"completed"|"failed", ...}
  GET  /tasks/{task_id}/result    -> video bytes

Configuration (user .env.local):
  PCV_LTX_VIDEO_ENABLED=true
  PCV_LTX_VIDEO_BASE_URL=http://127.0.0.1:7871
  PCV_LTX_VIDEO_TIMEOUT_S=900          # optional, per-task wait budget

A local loopback service keeps private media on this machine, so the adapter
allows person/child imagery that must never reach a remote provider. It still
refuses to overwrite outputs and records a provenance sidecar per clip.

Constraints enforced client-side: width/height divisible by 32; num_frames
must satisfy num_frames % 8 == 1 (e.g. 81, 97, 121).
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

from cinematic_config import ConfigError, load_config

ADAPTER = "ltx_video_local"
DEFAULT_TIMEOUT_S = 900
POLL_INTERVAL_S = 5


class LtxVideoError(RuntimeError):
    pass


def find_runtime(config: dict, base_url_override: str | None) -> dict:
    providers = config.get("providers") if isinstance(config.get("providers"), dict) else {}
    provider = providers.get(ADAPTER) if isinstance(providers.get(ADAPTER), dict) else {}
    runtime = provider.get("runtime") if isinstance(provider.get("runtime"), dict) else {}
    base_url = base_url_override or str(runtime.get("base_url") or "")
    if not base_url:
        raise LtxVideoError(
            "LTX-Video base_url is not configured. Set PCV_LTX_VIDEO_BASE_URL or pass --base-url."
        )
    if not base_url.startswith(("http://127.0.0.1", "http://localhost", "https://")):
        raise LtxVideoError(
            "Refusing a plain-HTTP non-loopback base_url; private frames must stay local "
            "or travel over TLS."
        )
    timeout_s = runtime.get("timeout_s") or DEFAULT_TIMEOUT_S
    return {"base_url": base_url.rstrip("/"), "timeout_s": int(timeout_s),
            "enabled": provider.get("enabled") is True}


def http_json(url: str, timeout: int = 15) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as exc:
        raise LtxVideoError(f"LTX-Video service is unreachable at {url}: {exc}") from exc


def post_multipart(url: str, fields: dict[str, str], file_path: Path | None) -> dict:
    boundary = uuid.uuid4().hex
    parts: list[bytes] = []
    for key, value in fields.items():
        parts.append(
            (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n").encode()
        )
    if file_path is not None:
        ctype = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        parts.append(
            (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
             f"filename=\"{file_path.name}\"\r\nContent-Type: {ctype}\r\n\r\n").encode()
            + file_path.read_bytes() + b"\r\n"
        )
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    request = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as exc:
        raise LtxVideoError(f"LTX-Video generate call failed: {exc}") from exc


def cmd_doctor(args: argparse.Namespace) -> int:
    config, _ = load_config(args.config)
    runtime = find_runtime(config, args.base_url)
    health = http_json(f"{runtime['base_url']}/health")
    report = {"provider": ADAPTER, "enabled": runtime["enabled"],
              "base_url": runtime["base_url"], "health": health,
              "ok": health.get("status") == "healthy"}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


def cmd_generate(args: argparse.Namespace) -> int:
    config, _ = load_config(args.config)
    runtime = find_runtime(config, args.base_url)
    if not runtime["enabled"]:
        raise LtxVideoError("Provider ltx_video_local is not enabled (PCV_LTX_VIDEO_ENABLED=true).")
    output = Path(args.output)
    if output.exists():
        raise LtxVideoError(f"Output already exists; refusing to overwrite: {output}")
    if args.width % 32 or args.height % 32:
        raise LtxVideoError("width and height must be divisible by 32.")
    if args.num_frames % 8 != 1:
        raise LtxVideoError("num_frames must satisfy num_frames % 8 == 1 (e.g. 81, 97, 121).")
    image = Path(args.image) if args.image else None
    if image is not None and not image.is_file():
        raise LtxVideoError(f"First-frame image does not exist: {image}")

    fields = {"prompt": args.prompt, "width": str(args.width), "height": str(args.height),
              "num_frames": str(args.num_frames), "frame_rate": str(args.frame_rate)}
    if args.negative_prompt:
        fields["negative_prompt"] = args.negative_prompt
    if args.seed is not None:
        fields["seed"] = str(args.seed)

    submitted = post_multipart(f"{runtime['base_url']}/generate", fields, image)
    task_id = submitted.get("taskId")
    if not submitted.get("success") or not task_id:
        raise LtxVideoError(f"Generate submission failed: {submitted}")
    print(f"task {task_id} submitted", file=sys.stderr)

    deadline = time.monotonic() + runtime["timeout_s"]
    status: dict = {}
    while time.monotonic() < deadline:
        status = http_json(f"{runtime['base_url']}/tasks/{task_id}")
        state = str(status.get("status") or "")
        if state == "completed":
            break
        if state == "failed":
            raise LtxVideoError(f"LTX-Video task failed: {status}")
        time.sleep(POLL_INTERVAL_S)
    else:
        raise LtxVideoError(f"Timed out after {runtime['timeout_s']}s waiting for task {task_id}.")

    result_url = f"{runtime['base_url']}/tasks/{task_id}/result"
    try:
        with urllib.request.urlopen(result_url, timeout=120) as response:
            payload = response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        raise LtxVideoError(f"Could not download the result for task {task_id}: {exc}") from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)

    provenance = {
        "adapter": ADAPTER, "task_id": task_id, "base_url": runtime["base_url"],
        "prompt": args.prompt, "negative_prompt": args.negative_prompt,
        "width": args.width, "height": args.height, "num_frames": args.num_frames,
        "frame_rate": args.frame_rate, "seed": args.seed,
        "first_frame_image": str(image) if image else None,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status, "bytes": len(payload),
        "disclosure": "AI-generated video (local LTX-Video service)",
    }
    sidecar = output.with_suffix(output.suffix + ".provenance.json")
    sidecar.write_text(json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "output_path": str(output), "bytes": len(payload),
                      "task_id": task_id}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Local LTX-Video service adapter.")
    parser.add_argument("--config", help="Explicit cinematic-video user config.")
    parser.add_argument("--base-url", help="Override the configured service base URL.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Check configuration and service health.")
    gen = sub.add_parser("generate", help="Generate a clip (text-to-video or image-to-video).")
    gen.add_argument("--prompt", required=True)
    gen.add_argument("--negative-prompt", default=None)
    gen.add_argument("--image", help="Optional first-frame image for image-to-video.")
    gen.add_argument("--width", type=int, default=768)
    gen.add_argument("--height", type=int, default=512)
    gen.add_argument("--num-frames", type=int, default=121)
    gen.add_argument("--frame-rate", type=int, default=25)
    gen.add_argument("--seed", type=int, default=None)
    gen.add_argument("--output", required=True, help="New .mp4 output path.")
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            return cmd_doctor(args)
        return cmd_generate(args)
    except (LtxVideoError, ConfigError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
