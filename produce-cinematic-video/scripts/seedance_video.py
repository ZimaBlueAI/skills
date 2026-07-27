#!/usr/bin/env python3
"""Create and immediately preserve Seedance video tasks through ModelArk/Ark."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cinematic_config import ConfigError, dump_json, load_config


ADAPTER = "volcengine_ark_seedance"
TERMINAL_STATUSES = {"succeeded", "failed", "cancelled", "expired"}
MAX_ERROR_BYTES = 64 * 1024
MAX_IMAGE_BYTES = 30 * 1024 * 1024
MAX_BASE64_SOURCE_BYTES = 45 * 1024 * 1024


class SeedanceError(RuntimeError):
    """Raised for a safe, user-facing Seedance adapter failure."""


class SeedanceTransientError(SeedanceError):
    """Raised when an existing task can be queried again without resubmission."""


def expand_path(value: str | Path) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(str(value)))).resolve()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_prompt(args: argparse.Namespace) -> tuple[str, str | None]:
    if args.prompt_file:
        source = expand_path(args.prompt_file)
        if not source.is_file():
            raise SeedanceError(f"Prompt file does not exist: {source}")
        return source.read_text(encoding="utf-8-sig").strip(), str(source)
    return str(args.prompt or "").strip(), None


def find_provider(
    config: dict[str, Any], requested: str | None, *, allow_disabled: bool
) -> tuple[str, dict[str, Any]]:
    providers = config.get("providers")
    if not isinstance(providers, dict):
        raise SeedanceError("Config providers must be an object.")
    if requested:
        provider = providers.get(requested)
        if not isinstance(provider, dict) or provider.get("adapter") != ADAPTER:
            raise SeedanceError(f"Provider {requested} does not use adapter {ADAPTER}.")
        if provider.get("enabled") is not True and not allow_disabled:
            raise SeedanceError(f"Provider {requested} is disabled in .env.local.")
        return requested, provider
    matches = [
        (name, provider)
        for name, provider in providers.items()
        if isinstance(provider, dict) and provider.get("adapter") == ADAPTER
    ]
    enabled = [item for item in matches if item[1].get("enabled") is True]
    pool = enabled or (matches if allow_disabled else [])
    if len(pool) == 1:
        return pool[0]
    if not pool:
        raise SeedanceError("No enabled Seedance provider is configured.")
    names = ", ".join(name for name, _ in pool)
    raise SeedanceError(f"Multiple Seedance providers match ({names}); pass --provider.")


def image_mime(path: Path) -> str:
    detected = mimetypes.guess_type(path.name)[0]
    if detected in {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff", "image/gif", "image/heic", "image/heif"}:
        return detected
    suffix = path.suffix.lower()
    fallback = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
        ".gif": "image/gif",
        ".heic": "image/heic",
        ".heif": "image/heif",
    }
    if suffix in fallback:
        return fallback[suffix]
    raise SeedanceError(f"Unsupported Seedance image format: {path.name}")


def checked_image(value: str, *, label: str) -> Path:
    path = expand_path(value)
    if not path.is_file():
        raise SeedanceError(f"{label} does not exist: {path}")
    size = path.stat().st_size
    if size <= 0:
        raise SeedanceError(f"{label} is empty: {path}")
    if size >= MAX_IMAGE_BYTES:
        raise SeedanceError(f"{label} must be smaller than 30 MiB: {path}")
    image_mime(path)
    return path


def data_url(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{image_mime(path)};base64,{encoded}"


def safe_error_message(payload: bytes, secret: str) -> str:
    message = ""
    try:
        parsed = json.loads(payload.decode("utf-8", errors="replace"))
        if isinstance(parsed, dict):
            error = parsed.get("error")
            if isinstance(error, dict):
                message = str(error.get("message") or error.get("code") or "")
            elif error:
                message = str(error)
            elif parsed.get("message"):
                message = str(parsed["message"])
    except (json.JSONDecodeError, UnicodeDecodeError):
        message = ""
    if secret:
        message = message.replace(secret, "<redacted>")
    message = re.sub(r"https?://\S+", "<redacted-url>", message)
    return message[:500]


def request_json(
    url: str,
    *,
    method: str,
    key: str,
    timeout: int,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        detail = safe_error_message(exc.read(MAX_ERROR_BYTES), key)
        suffix = f" Provider message: {detail}" if detail else ""
        if exc.code in {408, 425, 429, 500, 502, 503, 504}:
            raise SeedanceTransientError(
                f"Seedance API returned transient HTTP {exc.code}.{suffix}"
            ) from exc
        raise SeedanceError(f"Seedance API returned HTTP {exc.code}.{suffix}") from exc
    except (urllib.error.URLError, TimeoutError, ConnectionError, socket.timeout, ssl.SSLError) as exc:
        reason = str(getattr(exc, "reason", "network error"))
        if reason == "network error":
            reason = str(exc)
        if key:
            reason = reason.replace(key, "<redacted>")
        raise SeedanceTransientError(f"Seedance API connection failed: {reason[:300]}") from exc
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SeedanceError("Seedance API returned invalid JSON.") from exc
    if not isinstance(parsed, dict):
        raise SeedanceError("Seedance API returned a non-object response.")
    return parsed


def provider_runtime(provider: dict[str, Any]) -> tuple[str, str, str]:
    base_url = str(provider.get("base_url") or "").rstrip("/")
    model = str(provider.get("model") or "").strip()
    key_name = str(provider.get("api_key_env") or "")
    key = os.environ.get(key_name, "")
    if not base_url or not model:
        raise SeedanceError("Seedance provider needs a base_url and model.")
    if not key:
        raise SeedanceError(f"Seedance provider expects a set {key_name or 'API key variable'}.")
    return base_url, model, key


def collect_inputs(args: argparse.Namespace) -> tuple[Path | None, Path | None, list[Path], list[str]]:
    first = checked_image(args.first_frame, label="First frame") if args.first_frame else None
    last = checked_image(args.last_frame, label="Last frame") if args.last_frame else None
    references = [checked_image(value, label="Reference image") for value in (args.reference_image or [])]
    assets = [str(value).strip() for value in (args.reference_asset or [])]
    for asset in assets:
        if not re.fullmatch(r"asset://[A-Za-z0-9._:-]+", asset):
            raise SeedanceError("--reference-asset must be an authorized asset:// URI.")
    if last is not None and first is None:
        raise SeedanceError("--last-frame requires --first-frame.")
    if (first is not None or last is not None) and (references or assets):
        raise SeedanceError("First/last-frame mode and reference-image mode are mutually exclusive.")
    count = int(first is not None) + int(last is not None) + len(references) + len(assets)
    if count > 9:
        raise SeedanceError("Seedance 2.0 accepts at most nine image inputs.")
    total = sum(path.stat().st_size for path in [p for p in [first, last, *references] if p is not None])
    if total > MAX_BASE64_SOURCE_BYTES:
        raise SeedanceError(
            "Local image inputs are too large for a safe Base64 request; resize them or use approved hosted assets."
        )
    if count:
        if not args.content_class:
            raise SeedanceError("Image input requires --content-class animation, nonperson, or real-person-authorized.")
        if args.content_class == "real-person-authorized" and (first or last or references):
            raise SeedanceError(
                "Seedance 2.0 does not support direct local uploads containing real human faces. "
                "Use the provider's consented asset-library flow and pass only an approved --reference-asset URI."
            )
        if assets and args.content_class != "real-person-authorized":
            raise SeedanceError("Authorized asset:// inputs require --content-class real-person-authorized.")
    return first, last, references, assets


def build_content(
    prompt: str,
    first: Path | None,
    last: Path | None,
    references: list[Path],
    assets: list[str],
) -> list[dict[str, Any]]:
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    if first is not None:
        content.append({"type": "image_url", "image_url": {"url": data_url(first)}, "role": "first_frame"})
    if last is not None:
        content.append({"type": "image_url", "image_url": {"url": data_url(last)}, "role": "last_frame"})
    for path in references:
        content.append({"type": "image_url", "image_url": {"url": data_url(path)}, "role": "reference_image"})
    for asset in assets:
        content.append({"type": "image_url", "image_url": {"url": asset}, "role": "reference_image"})
    return content


def build_payload(model: str, content: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "content": content,
        "generate_audio": bool(args.generate_audio),
        "ratio": args.ratio,
        "duration": args.duration,
        "watermark": bool(args.watermark),
    }
    if args.resolution:
        payload["resolution"] = args.resolution
    if args.seed is not None:
        payload["seed"] = args.seed
    if args.return_last_frame:
        payload["return_last_frame"] = True
    return payload


def input_records(first: Path | None, last: Path | None, references: list[Path], assets: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for role, path in [
        ("first_frame", first),
        ("last_frame", last),
        *[("reference_image", item) for item in references],
    ]:
        if path is not None:
            records.append(
                {
                    "role": role,
                    "path": str(path),
                    "mime_type": image_mime(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    records.extend({"role": "reference_image", "authorized_asset_uri": asset} for asset in assets)
    return records


def sanitized_task(task: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "id",
        "model",
        "status",
        "error",
        "usage",
        "created_at",
        "updated_at",
        "seed",
        "resolution",
        "ratio",
        "duration",
        "framespersecond",
        "generate_audio",
        "service_tier",
        "execution_expires_after",
    }
    return {key: value for key, value in task.items() if key in allowed}


def write_json_new(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(dump_json(value))


def download_video(url: str, output: Path, *, timeout: int) -> None:
    if not url.startswith("https://"):
        raise SeedanceError("Seedance returned a non-HTTPS video URL; refusing download.")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.partial.{uuid.uuid4().hex}")
    try:
        request = urllib.request.Request(url, headers={"Accept": "video/mp4"}, method="GET")
        with urllib.request.urlopen(request, timeout=timeout) as response, temporary.open("xb") as handle:
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                handle.write(block)
    except urllib.error.URLError as exc:
        raise SeedanceError(f"Generated video download failed; partial file retained at {temporary}.") from exc
    if temporary.stat().st_size == 0:
        raise SeedanceError(f"Generated video download was empty; partial file retained at {temporary}.")
    if output.exists():
        raise SeedanceError(f"Output appeared during download; partial file retained at {temporary}.")
    temporary.rename(output)


def task_error(task: dict[str, Any]) -> str:
    error = task.get("error")
    if isinstance(error, dict):
        return str(error.get("message") or error.get("code") or "unknown provider error")[:500]
    return str(error or "unknown provider error")[:500]


def poll_task(base_url: str, task_id: str, key: str, args: argparse.Namespace) -> dict[str, Any]:
    deadline = time.monotonic() + args.max_wait
    last_status = ""
    consecutive_failures = 0
    while True:
        if time.monotonic() >= deadline:
            raise SeedanceError(
                f"Timed out waiting for task {task_id}; resume the recorded task instead of submitting it again."
            )
        try:
            task = request_json(
                f"{base_url}/contents/generations/tasks/{task_id}",
                method="GET",
                key=key,
                timeout=args.timeout,
            )
        except SeedanceTransientError as exc:
            consecutive_failures += 1
            if consecutive_failures >= 8:
                raise SeedanceError(
                    f"Polling task {task_id} was interrupted after {consecutive_failures} transient failures. "
                    "The task was not resubmitted; resume its task record later."
                ) from exc
            print(
                f"Transient polling error for task {task_id} "
                f"({consecutive_failures}/8); retrying the same task without resubmission.",
                flush=True,
            )
            time.sleep(min(args.poll_interval, max(0.0, deadline - time.monotonic())))
            continue
        consecutive_failures = 0
        status = str(task.get("status") or "unknown")
        if status != last_status:
            print(f"Seedance task {task_id}: {status}", flush=True)
            last_status = status
        if status in TERMINAL_STATUSES:
            return task
        time.sleep(args.poll_interval)


def read_task_record(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SeedanceError(f"Task record does not exist: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SeedanceError(f"Task record is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise SeedanceError(f"Task record must contain a JSON object: {path}")
    return value


def default_resume_output(task_record: Path) -> Path:
    suffix = ".task.json"
    if not task_record.name.endswith(suffix):
        raise SeedanceError(
            "Cannot derive output from this task-record name; pass --output explicitly."
        )
    return task_record.with_name(task_record.name[: -len(suffix)])


def preserve_terminal_task(
    *,
    task: dict[str, Any],
    task_record_value: dict[str, Any],
    output: Path,
    result_record: Path,
    provenance: Path,
    disclosure_note: str,
    timeout: int,
) -> None:
    task_id = str(task_record_value.get("task_id") or "").strip()
    status = str(task.get("status") or "unknown")
    if status != "succeeded":
        write_json_new(result_record, sanitized_task(task))
        raise SeedanceError(f"Seedance task {task_id} ended as {status}: {task_error(task)}")
    content_result = task.get("content")
    video_url = content_result.get("video_url") if isinstance(content_result, dict) else None
    if not isinstance(video_url, str) or not video_url:
        raise SeedanceError(f"Seedance task {task_id} succeeded but returned no video URL.")

    # Preserve the media before writing the terminal record. If a transient download
    # fails, the same task record remains resumable and no new paid task is created.
    download_video(video_url, output, timeout=timeout)
    write_json_new(result_record, sanitized_task(task))
    write_json_new(
        provenance,
        {
            "schema_version": 1,
            "asset_type": "synthetic_video",
            "synthetic": True,
            "provider": task_record_value.get("provider"),
            "adapter": ADAPTER,
            "model": task_record_value.get("model"),
            "task_id": task_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "submitted_at": task_record_value.get("submitted_at"),
            "prompt": task_record_value.get("prompt"),
            "prompt_source": task_record_value.get("prompt_source"),
            "prompt_sha256": task_record_value.get("prompt_sha256"),
            "inputs": task_record_value.get("inputs", []),
            "content_class": task_record_value.get("content_class"),
            "rights_basis": task_record_value.get("rights_basis"),
            "remote_upload_approved": task_record_value.get("remote_upload_approved") is True,
            "cost_approved": task_record_value.get("cost_approved") is True,
            "disclosure_note": disclosure_note,
            "settings": task_record_value.get("settings", {}),
            "task_result": sanitized_task(task),
            "output": {"path": str(output), "sha256": sha256_file(output)},
        },
    )


def resume_task(
    args: argparse.Namespace,
    provider_name: str,
    provider: dict[str, Any],
    task_record_path: Path,
    task_record_value: dict[str, Any],
) -> int:
    if task_record_value.get("adapter") != ADAPTER:
        raise SeedanceError(f"Task record does not use adapter {ADAPTER}.")
    recorded_provider = str(task_record_value.get("provider") or "").strip()
    if not recorded_provider or recorded_provider != provider_name:
        raise SeedanceError("Task record provider does not match the configured provider.")
    task_id = str(task_record_value.get("task_id") or "").strip()
    if not task_id:
        raise SeedanceError("Task record contains no task ID.")
    if task_record_value.get("remote_upload_approved") is not True:
        raise SeedanceError("Task record does not contain the original remote-upload approval.")
    if task_record_value.get("cost_approved") is not True:
        raise SeedanceError("Task record does not contain the original cost approval.")

    base_url, model, key = provider_runtime(provider)
    recorded_model = str(task_record_value.get("model") or "").strip()
    if not recorded_model or recorded_model != model:
        raise SeedanceError(
            f"Task record model {recorded_model or '<missing>'} does not match configured model {model}."
        )

    output = expand_path(args.output) if args.output else default_resume_output(task_record_path)
    result_record = (
        expand_path(args.result_record)
        if args.result_record
        else output.with_suffix(output.suffix + ".result.json")
    )
    provenance = (
        expand_path(args.provenance)
        if args.provenance
        else output.with_suffix(output.suffix + ".provenance.json")
    )
    for label, path in (("output", output), ("result record", result_record), ("provenance", provenance)):
        if path.exists():
            raise SeedanceError(f"Refusing to overwrite {label}: {path}")

    print(
        f"Resuming existing Seedance task {task_id}; no new generation task will be created.",
        flush=True,
    )
    task = poll_task(base_url, task_id, key, args)
    preserve_terminal_task(
        task=task,
        task_record_value=task_record_value,
        output=output,
        result_record=result_record,
        provenance=provenance,
        disclosure_note=args.disclosure_note,
        timeout=args.timeout,
    )
    print(f"Downloaded generated video: {output}")
    print(f"Created provenance: {provenance}")
    return 0


def dry_run_record(
    provider_name: str,
    provider: dict[str, Any],
    args: argparse.Namespace,
    prompt: str,
    prompt_source: str | None,
    inputs: list[dict[str, Any]],
    output: Path,
) -> dict[str, Any]:
    return {
        "dry_run": True,
        "provider": provider_name,
        "adapter": ADAPTER,
        "base_url": provider.get("base_url"),
        "model": provider.get("model"),
        "prompt": {
            "source": prompt_source,
            "length": len(prompt),
            "sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        },
        "inputs": inputs,
        "content_class": args.content_class,
        "rights_basis": args.rights_basis,
        "settings": {
            "generate_audio": bool(args.generate_audio),
            "ratio": args.ratio,
            "duration": args.duration,
            "resolution": args.resolution,
            "seed": args.seed,
            "watermark": bool(args.watermark),
            "return_last_frame": bool(args.return_last_frame),
        },
        "output": str(output),
        "live_call_requires": ["enabled provider", "--approve-remote-upload", "--approve-cost"],
        "secret": "not displayed",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safety-gated Seedance 2.0 ModelArk adapter.")
    parser.add_argument("--config", help="Explicit cinematic-video .env.local path.")
    parser.add_argument("--provider", help="Provider slot; defaults to the enabled Seedance adapter.")
    parser.add_argument(
        "--auth-check",
        action="store_true",
        help="Verify the configured key with a read-only one-item task-list request; creates no generation task.",
    )
    parser.add_argument(
        "--list-recent",
        type=int,
        metavar="N",
        help="Read-only list of N recent task IDs/statuses; useful after an ambiguous create connection failure.",
    )
    parser.add_argument(
        "--resume-task-record",
        help="Resume polling/downloading an existing .task.json without creating a new paid task.",
    )
    prompt_group = parser.add_mutually_exclusive_group()
    prompt_group.add_argument("--prompt")
    prompt_group.add_argument("--prompt-file")
    parser.add_argument("--output", help="New MP4 path; existing files are never overwritten.")
    parser.add_argument("--first-frame")
    parser.add_argument("--last-frame")
    parser.add_argument("--reference-image", action="append", help="Animation/non-person reference; repeatable.")
    parser.add_argument("--reference-asset", action="append", help="Provider-approved asset:// URI; repeatable.")
    parser.add_argument(
        "--content-class",
        choices=("animation", "nonperson", "real-person-authorized"),
        help="Required whenever an image or asset is supplied.",
    )
    parser.add_argument("--rights-basis", help="Why the supplied references may be used for this production.")
    parser.add_argument("--ratio", default="adaptive")
    parser.add_argument("--duration", type=int, default=5)
    parser.add_argument("--resolution")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--generate-audio", action="store_true")
    parser.add_argument("--watermark", action="store_true", help="Ask provider to add its AI watermark; default false.")
    parser.add_argument("--return-last-frame", action="store_true")
    parser.add_argument("--poll-interval", type=int, default=10)
    parser.add_argument("--max-wait", type=int, default=1800)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--task-record", help="New submitted-task JSON; defaults beside output.")
    parser.add_argument("--result-record", help="New terminal-task JSON; defaults beside output.")
    parser.add_argument("--provenance", help="New provenance JSON; defaults beside output.")
    parser.add_argument("--approve-remote-upload", action="store_true")
    parser.add_argument("--approve-cost", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print a secret-free request plan only.")
    parser.add_argument(
        "--disclosure-note",
        default="AI-generated video shot; disclose when audience context requires it.",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    config, _ = load_config(args.config)
    resume_record_path: Path | None = None
    resume_record_value: dict[str, Any] | None = None
    requested_provider = args.provider
    if args.resume_task_record:
        if args.auth_check or args.list_recent is not None or args.dry_run:
            raise SeedanceError(
                "--resume-task-record cannot be combined with --auth-check, --list-recent, or --dry-run."
            )
        if any(
            (
                args.prompt,
                args.prompt_file,
                args.first_frame,
                args.last_frame,
                args.reference_image,
                args.reference_asset,
                args.task_record,
                args.approve_remote_upload,
                args.approve_cost,
            )
        ):
            raise SeedanceError(
                "Resume accepts only the existing task record plus optional output/result/provenance paths; "
                "generation inputs and approvals are already recorded."
            )
        resume_record_path = expand_path(args.resume_task_record)
        resume_record_value = read_task_record(resume_record_path)
        recorded_provider = str(resume_record_value.get("provider") or "").strip()
        if not recorded_provider:
            raise SeedanceError("Task record contains no provider name.")
        if requested_provider and requested_provider != recorded_provider:
            raise SeedanceError("--provider does not match the provider stored in the task record.")
        requested_provider = recorded_provider

    provider_name, provider = find_provider(
        config, requested_provider, allow_disabled=args.dry_run
    )
    if resume_record_path is not None and resume_record_value is not None:
        if provider.get("enabled") is not True:
            raise SeedanceError(f"Provider {provider_name} is disabled in .env.local.")
        if args.poll_interval < 2 or args.poll_interval > 60:
            raise SeedanceError("--poll-interval must be between 2 and 60 seconds.")
        if args.max_wait < args.poll_interval:
            raise SeedanceError("--max-wait must be at least one poll interval.")
        return resume_task(
            args,
            provider_name,
            provider,
            resume_record_path,
            resume_record_value,
        )
    if args.list_recent is not None:
        if args.auth_check or args.dry_run:
            raise SeedanceError("--list-recent cannot be combined with --auth-check or --dry-run.")
        if any(
            (
                args.prompt,
                args.prompt_file,
                args.output,
                args.first_frame,
                args.last_frame,
                args.reference_image,
                args.reference_asset,
                args.approve_remote_upload,
                args.approve_cost,
            )
        ):
            raise SeedanceError("--list-recent is read-only and cannot be combined with generation arguments.")
        if args.list_recent < 1 or args.list_recent > 100:
            raise SeedanceError("--list-recent N must be between 1 and 100.")
        if provider.get("enabled") is not True:
            raise SeedanceError(f"Provider {provider_name} is disabled in .env.local.")
        base_url, _, key = provider_runtime(provider)
        response = request_json(
            f"{base_url}/contents/generations/tasks?page_num=1&page_size={args.list_recent}",
            method="GET",
            key=key,
            timeout=args.timeout,
        )
        items = response.get("items", [])
        if not isinstance(items, list):
            raise SeedanceError("Seedance recent-task request returned an unexpected shape.")
        allowed_fields = ("id", "status", "model", "created_at", "updated_at", "duration", "resolution")
        safe_items = [
            {key_name: item.get(key_name) for key_name in allowed_fields if item.get(key_name) is not None}
            for item in items
            if isinstance(item, dict)
        ]
        print(dump_json({"provider": provider_name, "read_only": True, "tasks": safe_items}), end="")
        return 0
    if args.auth_check:
        if args.dry_run:
            raise SeedanceError("--auth-check is already a read-only live check and cannot be combined with --dry-run.")
        if provider.get("enabled") is not True:
            raise SeedanceError(f"Provider {provider_name} is disabled in .env.local.")
        base_url, model, key = provider_runtime(provider)
        response = request_json(
            f"{base_url}/contents/generations/tasks?page_num=1&page_size=1",
            method="GET",
            key=key,
            timeout=args.timeout,
        )
        if not isinstance(response.get("items", []), list) or not isinstance(response.get("total", 0), int):
            raise SeedanceError("Seedance authentication request succeeded but returned an unexpected task-list shape.")
        print(f"PASS: Seedance authentication succeeded for provider {provider_name}.")
        print(f"Configured model: {model}")
        print("No generation task was created; API key and task contents were not printed.")
        return 0

    if not args.prompt and not args.prompt_file:
        raise SeedanceError("Generation requires --prompt or --prompt-file.")
    if not args.output:
        raise SeedanceError("Generation requires --output.")
    if args.duration < 4 or args.duration > 15:
        raise SeedanceError("Seedance 2.0 duration must be between 4 and 15 seconds.")
    if args.seed is not None and (args.seed < -1 or args.seed > 2**32 - 1):
        raise SeedanceError("--seed must be between -1 and 2^32-1.")
    if args.poll_interval < 2 or args.poll_interval > 60:
        raise SeedanceError("--poll-interval must be between 2 and 60 seconds.")
    if args.max_wait < args.poll_interval:
        raise SeedanceError("--max-wait must be at least one poll interval.")
    prompt, prompt_source = read_prompt(args)
    if not prompt:
        raise SeedanceError("Prompt is empty.")
    first, last, references, assets = collect_inputs(args)
    inputs = input_records(first, last, references, assets)
    if inputs and not str(args.rights_basis or "").strip():
        raise SeedanceError("Reference inputs require a concise --rights-basis record.")

    output = expand_path(args.output)
    task_record = expand_path(args.task_record) if args.task_record else output.with_suffix(output.suffix + ".task.json")
    result_record = expand_path(args.result_record) if args.result_record else output.with_suffix(output.suffix + ".result.json")
    provenance = expand_path(args.provenance) if args.provenance else output.with_suffix(output.suffix + ".provenance.json")
    for label, path in (
        ("output", output),
        ("task record", task_record),
        ("result record", result_record),
        ("provenance", provenance),
    ):
        if path.exists():
            raise SeedanceError(f"Refusing to overwrite {label}: {path}")

    if args.dry_run:
        print(
            dump_json(
                dry_run_record(
                    provider_name,
                    provider,
                    args,
                    prompt,
                    prompt_source,
                    inputs,
                    output,
                )
            ),
            end="",
        )
        return 0
    if provider.get("enabled") is not True:
        raise SeedanceError(f"Provider {provider_name} is disabled in .env.local.")
    if not args.approve_remote_upload:
        raise SeedanceError("Live generation requires --approve-remote-upload after reviewing prompt and inputs.")
    if not args.approve_cost:
        raise SeedanceError("Live generation requires --approve-cost after checking current provider pricing.")

    base_url, model, key = provider_runtime(provider)
    content = build_content(prompt, first, last, references, assets)
    payload = build_payload(model, content, args)
    created = request_json(
        f"{base_url}/contents/generations/tasks",
        method="POST",
        key=key,
        timeout=args.timeout,
        payload=payload,
    )
    task_id = str(created.get("id") or "").strip()
    if not task_id:
        raise SeedanceError("Seedance create response contained no task ID.")
    task_record_value = {
        "schema_version": 1,
        "provider": provider_name,
        "adapter": ADAPTER,
        "model": model,
        "task_id": task_id,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "prompt_source": prompt_source,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "inputs": inputs,
        "content_class": args.content_class,
        "rights_basis": args.rights_basis,
        "settings": {key: value for key, value in payload.items() if key != "content"},
        "remote_upload_approved": True,
        "cost_approved": True,
    }
    write_json_new(task_record, task_record_value)
    print(f"Created Seedance task: {task_id}", flush=True)
    task = poll_task(base_url, task_id, key, args)
    preserve_terminal_task(
        task=task,
        task_record_value=task_record_value,
        output=output,
        result_record=result_record,
        provenance=provenance,
        disclosure_note=args.disclosure_note,
        timeout=args.timeout,
    )
    print(f"Downloaded generated video: {output}")
    print(f"Created provenance: {provenance}")
    return 0


def main() -> int:
    try:
        return run(build_parser().parse_args())
    except (ConfigError, SeedanceError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
