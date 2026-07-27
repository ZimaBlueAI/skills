#!/usr/bin/env python3
"""Generate or edit images through explicit, safety-gated remote adapters."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cinematic_config import ConfigError, dump_json, load_config


ADAPTERS = {"openai_images", "gemini_images"}
MAX_ERROR_BYTES = 64 * 1024
MAX_INPUT_BYTES = 20 * 1024 * 1024
MAX_OUTPUT_BYTES = 50 * 1024 * 1024


class ImageGenerationError(RuntimeError):
    """Raised for a safe, user-facing image adapter failure."""


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
            raise ImageGenerationError(f"Prompt file does not exist: {source}")
        prompt = source.read_text(encoding="utf-8-sig").strip()
        return prompt, str(source)
    prompt = str(args.prompt or "").strip()
    return prompt, None


def find_provider(
    config: dict[str, Any], requested: str | None, *, allow_disabled: bool
) -> tuple[str, dict[str, Any]]:
    providers = config.get("providers")
    if not isinstance(providers, dict):
        raise ImageGenerationError("Config providers must be an object.")
    if requested:
        provider = providers.get(requested)
        if not isinstance(provider, dict) or provider.get("adapter") not in ADAPTERS:
            raise ImageGenerationError(
                f"Provider {requested} is not an OpenAI/Gemini image adapter."
            )
        if provider.get("enabled") is not True and not allow_disabled:
            raise ImageGenerationError(f"Provider {requested} is disabled in .env.local.")
        return requested, provider

    matches = [
        (name, provider)
        for name, provider in providers.items()
        if isinstance(provider, dict) and provider.get("adapter") in ADAPTERS
    ]
    enabled = [item for item in matches if item[1].get("enabled") is True]
    pool = enabled or (matches if allow_disabled else [])
    if len(pool) == 1:
        return pool[0]
    if not pool:
        raise ImageGenerationError(
            "No enabled OpenAI/Gemini image provider is configured."
        )
    names = ", ".join(name for name, _ in pool)
    raise ImageGenerationError(f"Multiple image providers match ({names}); pass --provider.")


def checked_input(path_value: str, *, label: str) -> Path:
    path = expand_path(path_value)
    if not path.is_file():
        raise ImageGenerationError(f"{label} does not exist: {path}")
    size = path.stat().st_size
    if size <= 0:
        raise ImageGenerationError(f"{label} is empty: {path}")
    if size > MAX_INPUT_BYTES:
        raise ImageGenerationError(
            f"{label} exceeds this adapter's {MAX_INPUT_BYTES // (1024 * 1024)} MiB safety limit: {path}"
        )
    return path


def mime_for(path: Path) -> str:
    detected = mimetypes.guess_type(path.name)[0]
    if detected and detected.startswith("image/"):
        return detected
    suffix = path.suffix.lower()
    fallback = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
    if suffix in fallback:
        return fallback[suffix]
    raise ImageGenerationError(f"Unsupported image file type: {path.name}")


def image_part(path: Path) -> dict[str, Any]:
    return {
        "inlineData": {
            "mimeType": mime_for(path),
            "data": base64.b64encode(path.read_bytes()).decode("ascii"),
        }
    }


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
    headers: dict[str, str],
    body: bytes | None,
    secret: str,
    timeout: int,
) -> dict[str, Any]:
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        detail = safe_error_message(exc.read(MAX_ERROR_BYTES), secret)
        suffix = f" Provider message: {detail}" if detail else ""
        raise ImageGenerationError(f"Remote image API returned HTTP {exc.code}.{suffix}") from exc
    except urllib.error.URLError as exc:
        reason = str(getattr(exc, "reason", "network error"))
        if secret:
            reason = reason.replace(secret, "<redacted>")
        raise ImageGenerationError(f"Remote image API connection failed: {reason[:300]}") from exc
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ImageGenerationError("Remote image API returned invalid JSON.") from exc
    if not isinstance(parsed, dict):
        raise ImageGenerationError("Remote image API returned a non-object response.")
    return parsed


def json_post(url: str, payload: dict[str, Any], *, headers: dict[str, str], secret: str, timeout: int) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    merged = {"Content-Type": "application/json", "Accept": "application/json", **headers}
    return request_json(url, method="POST", headers=merged, body=body, secret=secret, timeout=timeout)


def multipart_body(
    fields: list[tuple[str, str]], files: list[tuple[str, Path]]
) -> tuple[bytes, str]:
    boundary = "pcv-" + uuid.uuid4().hex
    chunks: list[bytes] = []
    for name, value in fields:
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("ascii"),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("ascii"),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )
    for name, path in files:
        filename = path.name.replace('"', "_")
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("ascii"),
                f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode("utf-8"),
                f"Content-Type: {mime_for(path)}\r\n\r\n".encode("ascii"),
                path.read_bytes(),
                b"\r\n",
            ]
        )
    chunks.append(f"--{boundary}--\r\n".encode("ascii"))
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def extract_openai_image(response: dict[str, Any], *, secret: str, timeout: int) -> tuple[bytes, str, str]:
    data = response.get("data")
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise ImageGenerationError("OpenAI Images response contained no image data.")
    item = data[0]
    encoded = item.get("b64_json")
    if isinstance(encoded, str) and encoded:
        try:
            return base64.b64decode(encoded, validate=True), "image/png", "b64_json"
        except ValueError as exc:
            raise ImageGenerationError("OpenAI Images returned invalid base64 image data.") from exc
    url = item.get("url")
    if isinstance(url, str) and url.startswith("https://"):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as remote:
                mime = str(remote.headers.get_content_type() or "application/octet-stream")
                return remote.read(), mime, "temporary_url"
        except urllib.error.URLError as exc:
            reason = str(getattr(exc, "reason", "network error"))
            if secret:
                reason = reason.replace(secret, "<redacted>")
            raise ImageGenerationError(f"Generated image download failed: {reason[:300]}") from exc
    raise ImageGenerationError("OpenAI Images response had neither b64_json nor an HTTPS image URL.")


def call_openai(
    provider: dict[str, Any], args: argparse.Namespace, prompt: str, inputs: list[Path], mask: Path | None
) -> tuple[bytes, str, str]:
    base_url = str(provider.get("base_url") or "").rstrip("/")
    model = str(provider.get("model") or "").strip()
    key_name = str(provider.get("api_key_env") or "")
    key = os.environ.get(key_name, "")
    if not base_url or not model or not key:
        raise ImageGenerationError(
            f"OpenAI image provider needs base_url, model, and a set {key_name or 'API key variable'}."
        )
    headers = {"Authorization": f"Bearer {key}"}
    optional = {
        "size": args.size,
        "quality": args.quality,
        "background": args.background,
        "output_format": args.output_format,
    }
    if inputs:
        fields = [("model", model), ("prompt", prompt), ("n", "1")]
        fields.extend((name, str(value)) for name, value in optional.items() if value)
        files = [("image[]", path) for path in inputs]
        if mask is not None:
            files.append(("mask", mask))
        body, content_type = multipart_body(fields, files)
        response = request_json(
            f"{base_url}/images/edits",
            method="POST",
            headers={"Authorization": f"Bearer {key}", "Accept": "application/json", "Content-Type": content_type},
            body=body,
            secret=key,
            timeout=args.timeout,
        )
    else:
        payload: dict[str, Any] = {"model": model, "prompt": prompt, "n": 1}
        payload.update({name: value for name, value in optional.items() if value})
        response = json_post(
            f"{base_url}/images/generations",
            payload,
            headers=headers,
            secret=key,
            timeout=args.timeout,
        )
    return extract_openai_image(response, secret=key, timeout=args.timeout)


def decoded_image(encoded: str, mime_type: str, transport: str) -> tuple[bytes, str, str]:
    value = encoded.strip()
    if value.startswith("data:image/"):
        match = re.fullmatch(r"data:([^;,]+);base64,(.+)", value, flags=re.DOTALL)
        if not match:
            raise ImageGenerationError("Relay returned an invalid image data URL.")
        mime_type = match.group(1)
        value = match.group(2)
        transport += "_data_url"
    try:
        return base64.b64decode(value, validate=True), mime_type, transport
    except ValueError as exc:
        raise ImageGenerationError("Gemini relay returned invalid base64 image data.") from exc


def markdown_image_url(text: str) -> str | None:
    match = re.search(r"!\[[^\]]*\]\((https://[^)\s]+)\)", text)
    return match.group(1) if match else None


def download_relay_image(url: str, *, secret: str, timeout: int) -> tuple[bytes, str, str]:
    if not url.startswith("https://"):
        raise ImageGenerationError("Relay returned a non-HTTPS image URL; refusing download.")
    try:
        request = urllib.request.Request(url, headers={"Accept": "image/*"}, method="GET")
        with urllib.request.urlopen(request, timeout=timeout) as remote:
            mime_type = str(remote.headers.get_content_type() or "application/octet-stream")
            data = remote.read(MAX_OUTPUT_BYTES + 1)
    except urllib.error.URLError as exc:
        reason = str(getattr(exc, "reason", "network error"))
        if secret:
            reason = reason.replace(secret, "<redacted>")
        reason = re.sub(r"https?://\S+", "<redacted-url>", reason)
        raise ImageGenerationError(f"Relay image download failed: {reason[:300]}") from exc
    if not mime_type.startswith("image/"):
        raise ImageGenerationError("Relay image URL returned a non-image content type.")
    if not data:
        raise ImageGenerationError("Relay image URL returned an empty file.")
    if len(data) > MAX_OUTPUT_BYTES:
        raise ImageGenerationError("Relay image exceeds the 50 MiB safety limit.")
    return data, mime_type, "markdown_temporary_url"


def extract_gemini_image(
    response: dict[str, Any], *, secret: str = "", timeout: int = 300
) -> tuple[bytes, str, str]:
    roots: list[dict[str, Any]] = [response]
    for key in ("data", "result", "response", "output"):
        wrapped = response.get(key)
        if isinstance(wrapped, dict):
            roots.append(wrapped)

    for root in roots:
        candidates = root.get("candidates")
        if not isinstance(candidates, list):
            candidates = []
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            content = candidate.get("content")
            parts = content.get("parts") if isinstance(content, dict) else None
            if not isinstance(parts, list):
                continue
            for part in parts:
                if not isinstance(part, dict):
                    continue
                inline = part.get("inlineData") or part.get("inline_data")
                if isinstance(inline, dict):
                    encoded = inline.get("data")
                    if isinstance(encoded, str) and encoded:
                        return decoded_image(
                            encoded,
                            str(inline.get("mimeType") or inline.get("mime_type") or "image/png"),
                            "inline_data",
                        )
                text_part = part.get("text")
                if isinstance(text_part, str):
                    image_url = markdown_image_url(text_part)
                    if image_url:
                        return download_relay_image(image_url, secret=secret, timeout=timeout)

        data = root.get("data")
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                encoded = item.get("b64_json") or item.get("base64")
                if isinstance(encoded, str) and encoded:
                    return decoded_image(encoded, "image/png", "relay_data")

        images = root.get("images")
        if isinstance(images, list):
            for item in images:
                if isinstance(item, str) and item.startswith("data:image/"):
                    return decoded_image(item, "image/png", "relay_images")
                if isinstance(item, dict):
                    encoded = item.get("b64_json") or item.get("base64") or item.get("data")
                    if isinstance(encoded, str) and encoded:
                        return decoded_image(
                            encoded,
                            str(item.get("mime_type") or item.get("mimeType") or "image/png"),
                            "relay_images",
                        )
    raise ImageGenerationError("Gemini response contained no image part.")


def gemini_response_summary(response: dict[str, Any], secret: str) -> dict[str, Any]:
    finish_reasons: list[str] = []
    part_shapes: list[list[str]] = []
    text_preview = ""
    image_url_present = False
    roots: list[dict[str, Any]] = [response]
    for key in ("data", "result", "response", "output"):
        wrapped = response.get(key)
        if isinstance(wrapped, dict):
            roots.append(wrapped)
    for root in roots:
        candidates = root.get("candidates")
        if not isinstance(candidates, list):
            continue
        for candidate in candidates[:4]:
            if not isinstance(candidate, dict):
                continue
            if candidate.get("finishReason") or candidate.get("finish_reason"):
                finish_reasons.append(str(candidate.get("finishReason") or candidate.get("finish_reason")))
            content = candidate.get("content")
            parts = content.get("parts") if isinstance(content, dict) else None
            if not isinstance(parts, list):
                continue
            for part in parts[:8]:
                if not isinstance(part, dict):
                    continue
                part_shapes.append(sorted(str(key) for key in part))
                if not text_preview and isinstance(part.get("text"), str):
                    text_preview = part["text"][:400]
                if isinstance(part.get("text"), str) and markdown_image_url(part["text"]):
                    image_url_present = True
    if secret:
        text_preview = text_preview.replace(secret, "<redacted>")
    text_preview = re.sub(r"https?://\S+", "<redacted-url>", text_preview)
    error_message = safe_error_message(
        json.dumps(response, ensure_ascii=False).encode("utf-8"), secret
    )
    prompt_feedback = response.get("promptFeedback") or response.get("prompt_feedback")
    usage = response.get("usageMetadata") or response.get("usage_metadata")
    safe_usage = (
        {
            str(key): value
            for key, value in usage.items()
            if isinstance(value, (int, float, bool, str))
        }
        if isinstance(usage, dict)
        else {}
    )
    return {
        "top_level_keys": sorted(str(key) for key in response),
        "error_message": error_message or None,
        "finish_reasons": finish_reasons,
        "part_shapes": part_shapes,
        "text_preview": text_preview or None,
        "image_url_present": image_url_present,
        "usage_metadata": safe_usage,
        "prompt_feedback_keys": (
            sorted(str(key) for key in prompt_feedback)
            if isinstance(prompt_feedback, dict)
            else []
        ),
    }


def gemini_request_target(provider: dict[str, Any]) -> tuple[str, str, str]:
    """Return an exact request URL, effective model, and target source."""
    configured_model = str(provider.get("model") or "").strip()
    endpoint = str(provider.get("endpoint") or "").strip()
    if endpoint:
        parsed = urllib.parse.urlsplit(endpoint)
        if (
            parsed.scheme != "https"
            or not parsed.netloc
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
        ):
            raise ImageGenerationError(
                "PCV_GEMINI_IMAGE_ENDPOINT must be an absolute HTTPS URL without user info or a fragment."
            )
        model_match = re.search(r"/models/([^/]+):generateContent$", parsed.path)
        if not model_match:
            raise ImageGenerationError(
                "PCV_GEMINI_IMAGE_ENDPOINT must be the complete .../models/<model>:generateContent URL."
            )
        query_names = {
            key.lower()
            for key in urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        }
        if query_names & {"key", "api_key", "apikey", "token", "access_token", "authorization"}:
            raise ImageGenerationError(
                "PCV_GEMINI_IMAGE_ENDPOINT must not include credentials in its query string."
            )
        endpoint_model = urllib.parse.unquote(model_match.group(1))
        if configured_model and endpoint_model != configured_model:
            raise ImageGenerationError(
                "PCV_GEMINI_IMAGE_MODEL must match the model encoded in PCV_GEMINI_IMAGE_ENDPOINT."
            )
        return endpoint, endpoint_model, "PCV_GEMINI_IMAGE_ENDPOINT"

    base_url = str(provider.get("base_url") or "").rstrip("/")
    if not base_url or not configured_model:
        raise ImageGenerationError(
            "Gemini image provider needs PCV_GEMINI_IMAGE_ENDPOINT, or a base URL and model."
        )
    model_segment = urllib.parse.quote(configured_model, safe="-._")
    return (
        f"{base_url}/models/{model_segment}:generateContent",
        configured_model,
        "provider_base_url",
    )


def target_record(provider: dict[str, Any]) -> dict[str, str]:
    if provider.get("adapter") == "gemini_images":
        target, model, source = gemini_request_target(provider)
        return {
            "source": source,
            "model": model,
            "sha256": hashlib.sha256(target.encode("utf-8")).hexdigest(),
        }
    base_url = str(provider.get("base_url") or "")
    return {
        "source": "provider_base_url",
        "model": str(provider.get("model") or ""),
        "sha256": hashlib.sha256(base_url.encode("utf-8")).hexdigest(),
    }


def gemini_auth_transport(endpoint: str, key: str, source: str) -> tuple[str, dict[str, str]]:
    """Attach relay credentials at request time without persisting or logging them."""
    if source == "PCV_GEMINI_IMAGE_ENDPOINT":
        parsed = urllib.parse.urlsplit(endpoint)
        query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        query.append(("key", key))
        request_url = urllib.parse.urlunsplit(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                urllib.parse.urlencode(query),
                "",
            )
        )
        return request_url, {}
    return endpoint, {"x-goog-api-key": key}


def call_gemini(
    provider: dict[str, Any], args: argparse.Namespace, prompt: str, inputs: list[Path], mask: Path | None
) -> tuple[bytes, str, str]:
    if mask is not None:
        raise ImageGenerationError("A separate mask is supported by the OpenAI adapter, not Gemini; use a prompt-led edit.")
    endpoint, model, source = gemini_request_target(provider)
    key_name = str(provider.get("api_key_env") or "")
    key = os.environ.get(key_name, "")
    if not model or not key:
        raise ImageGenerationError(
            f"Gemini image provider needs a valid endpoint/model and a set {key_name or 'API key variable'}."
        )
    parts: list[dict[str, Any]] = [{"text": prompt}]
    parts.extend(image_part(path) for path in inputs)
    generation: dict[str, Any] = {"responseModalities": ["TEXT", "IMAGE"]}
    image_config = {
        key_name: value
        for key_name, value in {
            "aspectRatio": args.aspect_ratio,
            "imageSize": args.image_size,
        }.items()
        if value
    }
    if image_config:
        # The current generateContent REST schema exposes image output controls
        # under responseFormat.image (SDKs may call the typed field imageConfig).
        generation["responseFormat"] = {"image": image_config}
    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": generation,
    }
    request_url, auth_headers = gemini_auth_transport(endpoint, key, source)
    response = json_post(
        request_url,
        payload,
        headers=auth_headers,
        secret=key,
        timeout=args.timeout,
    )
    try:
        return extract_gemini_image(response, secret=key, timeout=args.timeout)
    except ImageGenerationError as exc:
        output = expand_path(args.output)
        diagnostic = output.with_suffix(output.suffix + ".response.json")
        if not diagnostic.exists():
            write_new(
                diagnostic,
                dump_json(
                    {
                        "schema_version": 1,
                        "provider": "gemini_image",
                        "request_target": target_record(provider),
                        "response_summary": gemini_response_summary(response, key),
                        "image_preserved": False,
                    }
                ).encode("utf-8"),
            )
        raise ImageGenerationError(f"{exc} Safe response summary: {diagnostic}") from exc


def gemini_auth_check(provider_name: str, provider: dict[str, Any], *, timeout: int) -> int:
    endpoint, model, source = gemini_request_target(provider)
    if source != "PCV_GEMINI_IMAGE_ENDPOINT":
        raise ImageGenerationError(
            "Gemini auth-check requires PCV_GEMINI_IMAGE_ENDPOINT; refusing an implicit default target."
        )
    key_name = str(provider.get("api_key_env") or "")
    key = os.environ.get(key_name, "")
    if not key:
        raise ImageGenerationError(f"Gemini provider expects a set {key_name or 'API key variable'}.")
    parsed = urllib.parse.urlsplit(endpoint)
    model_path = parsed.path[: -len(":generateContent")]
    metadata_url = urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, model_path, parsed.query, "")
    )
    request_url, auth_headers = gemini_auth_transport(metadata_url, key, source)
    response = request_json(
        request_url,
        method="GET",
        headers={**auth_headers, "Accept": "application/json"},
        body=None,
        secret=key,
        timeout=timeout,
    )
    returned_name = str(response.get("name") or "")
    if returned_name and model not in returned_name:
        raise ImageGenerationError("Relay model metadata did not match the configured endpoint model.")
    print(f"PASS: Gemini relay authentication/metadata check succeeded for provider {provider_name}.")
    print(f"Configured model: {model}")
    print("No image-generation request was created; endpoint and API key were not printed.")
    return 0


def plan_record(
    provider_name: str,
    provider: dict[str, Any],
    args: argparse.Namespace,
    prompt: str,
    prompt_source: str | None,
    inputs: list[Path],
    mask: Path | None,
    output: Path,
) -> dict[str, Any]:
    return {
        "dry_run": True,
        "action": "edit" if inputs else "generate",
        "provider": provider_name,
        "adapter": provider.get("adapter"),
        "request_target": target_record(provider),
        "model": target_record(provider)["model"],
        "prompt": {
            "source": prompt_source,
            "length": len(prompt),
            "sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        },
        "inputs": [
            {"path": str(path), "mime_type": mime_for(path), "sha256": sha256_file(path)}
            for path in inputs
        ],
        "mask": (
            {"path": str(mask), "mime_type": mime_for(mask), "sha256": sha256_file(mask)}
            if mask is not None
            else None
        ),
        "settings": {
            "size": args.size,
            "quality": args.quality,
            "background": args.background,
            "output_format": args.output_format,
            "aspect_ratio": args.aspect_ratio,
            "image_size": args.image_size,
        },
        "output": str(output),
        "live_call_requires": ["enabled provider", "--approve-remote-upload", "--approve-cost"],
        "secret": "not displayed",
    }


def write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)


def write_provenance(
    path: Path,
    *,
    provider_name: str,
    provider: dict[str, Any],
    args: argparse.Namespace,
    prompt: str,
    prompt_source: str | None,
    inputs: list[Path],
    mask: Path | None,
    output: Path,
    mime_type: str,
    transport: str,
) -> None:
    record = {
        "schema_version": 1,
        "asset_type": "synthetic_image_edit" if inputs else "synthetic_image",
        "synthetic": True,
        "provider": provider_name,
        "adapter": provider.get("adapter"),
        "model": target_record(provider)["model"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "prompt_source": prompt_source,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "remote_upload_approved": True,
        "cost_approved": True,
        "disclosure_note": args.disclosure_note,
        "inputs": [
            {"path": str(item), "sha256": sha256_file(item), "mime_type": mime_for(item)}
            for item in inputs
        ],
        "mask": (
            {"path": str(mask), "sha256": sha256_file(mask), "mime_type": mime_for(mask)}
            if mask is not None
            else None
        ),
        "settings": {
            "size": args.size,
            "quality": args.quality,
            "background": args.background,
            "output_format": args.output_format,
            "aspect_ratio": args.aspect_ratio,
            "image_size": args.image_size,
        },
        "result_transport": transport,
        "request_target": target_record(provider),
        "provider_note": (
            "Gemini-generated images include SynthID according to provider documentation."
            if provider.get("adapter") == "gemini_images"
            else None
        ),
        "output": {
            "path": str(output),
            "mime_type": mime_type,
            "sha256": sha256_file(output),
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(dump_json(record))


def add_common(parser: argparse.ArgumentParser) -> None:
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt")
    prompt_group.add_argument("--prompt-file")
    parser.add_argument("--output", required=True, help="New image path; existing files are never overwritten.")
    parser.add_argument("--provenance", help="New provenance JSON path; defaults beside output.")
    parser.add_argument("--size", help="OpenAI output size, for example 1024x1536 or auto.")
    parser.add_argument("--quality", choices=("auto", "low", "medium", "high"))
    parser.add_argument("--background", choices=("auto", "opaque", "transparent"))
    parser.add_argument("--output-format", choices=("png", "jpeg", "webp"))
    parser.add_argument("--aspect-ratio", help="Gemini image aspect ratio, for example 9:16.")
    parser.add_argument("--image-size", choices=("1K", "2K", "4K"), help="Gemini image size.")
    parser.add_argument("--timeout", type=int, default=300, help="HTTP timeout in seconds.")
    parser.add_argument("--approve-remote-upload", action="store_true")
    parser.add_argument("--approve-cost", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print a secret-free request plan only.")
    parser.add_argument(
        "--disclosure-note",
        default="AI-generated or AI-edited image; disclose when audience context requires it.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safety-gated GPT Image 2 and Gemini image adapter.")
    parser.add_argument("--config", help="Explicit cinematic-video .env.local path.")
    parser.add_argument("--provider", help="Provider slot, such as openai_image or gemini_image.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    auth_check = subparsers.add_parser(
        "auth-check",
        help="Read Gemini model metadata through PCV_GEMINI_IMAGE_ENDPOINT; generates no image.",
    )
    auth_check.add_argument("--timeout", type=int, default=60)

    generate = subparsers.add_parser("generate", help="Generate one image from text.")
    add_common(generate)

    edit = subparsers.add_parser("edit", help="Edit one or more authorized images.")
    add_common(edit)
    edit.add_argument("--input", action="append", required=True, help="Authorized input image; repeatable.")
    edit.add_argument("--mask", help="Optional OpenAI edit mask.")
    return parser


def run(args: argparse.Namespace) -> int:
    config, _ = load_config(args.config)
    dry_run = bool(getattr(args, "dry_run", False))
    provider_name, provider = find_provider(config, args.provider, allow_disabled=dry_run)
    if args.command == "auth-check":
        if provider.get("adapter") != "gemini_images":
            raise ImageGenerationError("auth-check currently supports only the Gemini image adapter.")
        if provider.get("enabled") is not True:
            raise ImageGenerationError(f"Provider {provider_name} is disabled in .env.local.")
        if args.timeout < 1 or args.timeout > 300:
            raise ImageGenerationError("--timeout must be between 1 and 300 seconds.")
        return gemini_auth_check(provider_name, provider, timeout=args.timeout)
    prompt, prompt_source = read_prompt(args)
    if not prompt:
        raise ImageGenerationError("Prompt is empty.")
    if args.timeout < 1 or args.timeout > 3600:
        raise ImageGenerationError("--timeout must be between 1 and 3600 seconds.")
    inputs = [checked_input(value, label="Input image") for value in getattr(args, "input", []) or []]
    mask = checked_input(args.mask, label="Mask image") if getattr(args, "mask", None) else None
    output = expand_path(args.output)
    provenance = expand_path(args.provenance) if args.provenance else output.with_suffix(output.suffix + ".provenance.json")
    if output.exists():
        raise ImageGenerationError(f"Refusing to overwrite output: {output}")
    if provenance.exists():
        raise ImageGenerationError(f"Refusing to overwrite provenance: {provenance}")

    if args.dry_run:
        print(dump_json(plan_record(provider_name, provider, args, prompt, prompt_source, inputs, mask, output)), end="")
        return 0
    if provider.get("enabled") is not True:
        raise ImageGenerationError(f"Provider {provider_name} is disabled in .env.local.")
    if not args.approve_remote_upload:
        raise ImageGenerationError("Live generation requires --approve-remote-upload after reviewing prompt and inputs.")
    if not args.approve_cost:
        raise ImageGenerationError("Live generation requires --approve-cost after checking current provider pricing.")

    adapter = provider.get("adapter")
    if adapter == "openai_images":
        data, mime_type, transport = call_openai(provider, args, prompt, inputs, mask)
    elif adapter == "gemini_images":
        data, mime_type, transport = call_gemini(provider, args, prompt, inputs, mask)
    else:  # Guarded by provider selection; retained for defensive clarity.
        raise ImageGenerationError(f"Unsupported image adapter: {adapter}")
    if not data:
        raise ImageGenerationError("Provider returned an empty image.")
    write_new(output, data)
    write_provenance(
        provenance,
        provider_name=provider_name,
        provider=provider,
        args=args,
        prompt=prompt,
        prompt_source=prompt_source,
        inputs=inputs,
        mask=mask,
        output=output,
        mime_type=mime_type,
        transport=transport,
    )
    print(f"Created image: {output}")
    print(f"Created provenance: {provenance}")
    return 0


def main() -> int:
    try:
        return run(build_parser().parse_args())
    except (ConfigError, ImageGenerationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
