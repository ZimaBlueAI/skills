#!/usr/bin/env python3
"""Initialize, inspect, and validate the per-user cinematic-video config."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

from cinematic_config import (
    CONFIG_SCHEMA,
    DEFAULT_CONFIG,
    ENV_BINDINGS,
    ENV_NAME_RE,
    POCKET_TTS_LANGUAGES,
    SECRET_ENV_KEYS,
    ConfigError,
    config_path,
    config_to_env_values,
    default_data_dir,
    dump_json,
    legacy_config_path,
    load_config,
    read_env_file,
    read_json,
    redact,
    render_env_template,
    resolve_executable,
    unknown_env_keys,
    user_skill_dir,
    validate_config,
)

try:
    import jsonschema
except ModuleNotFoundError:  # Optional; semantic validation remains available.
    jsonschema = None


PROVIDER_SETUP = {
    "seedance": {
        "label": "Seedance / Volcengine ModelArk",
        "enabled_key": "PCV_SEEDANCE_ENABLED",
        "model_key": "PCV_SEEDANCE_MODEL",
        "model_default": "doubao-seedance-2-0-260128",
        "secret_key": "PCV_SEEDANCE_API_KEY",
        "default_note": "Uses the bundled China-region base URL and records the Seedance 2.0 model explicitly.",
    },
    "openai-image": {
        "label": "OpenAI GPT Image",
        "enabled_key": "PCV_OPENAI_IMAGE_ENABLED",
        "model_key": "PCV_OPENAI_IMAGE_MODEL",
        "model_default": "gpt-image-2",
        "secret_key": "PCV_OPENAI_IMAGE_API_KEY",
        "default_note": "Uses the bundled official API root and records gpt-image-2 explicitly.",
    },
    "gemini-image": {
        "label": "Google Gemini image / Nano Banana",
        "enabled_key": "PCV_GEMINI_IMAGE_ENABLED",
        "model_key": "PCV_GEMINI_IMAGE_MODEL",
        "model_default": "gemini-3.1-flash-image",
        "secret_key": "PCV_GEMINI_IMAGE_API_KEY",
        "endpoint_key": "PCV_GEMINI_IMAGE_ENDPOINT",
        "default_note": (
            "Requires a complete Gemini-native relay endpoint ending in "
            ".../models/<model>:generateContent; it never rewrites that endpoint to the official host."
        ),
    },
}

LOCAL_SETUP = ("gpt-sovits",)

LEGACY_ENV_ALIASES = {
    "PCV_OPENAI_IMAGE2_ENABLED": "PCV_OPENAI_IMAGE_ENABLED",
    "PCV_OPENAI_IMAGE2_ENDPOINT": "PCV_OPENAI_IMAGE_BASE_URL",
    "PCV_OPENAI_IMAGE2_MODEL": "PCV_OPENAI_IMAGE_MODEL",
}


def gemini_model_from_endpoint(value: str) -> str:
    endpoint = value.strip()
    parsed = urllib.parse.urlsplit(endpoint)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
    ):
        raise ConfigError(
            "PCV_GEMINI_IMAGE_ENDPOINT must be an absolute HTTPS URL without user info or a fragment."
        )
    match = re.search(r"/models/([^/]+):generateContent$", parsed.path)
    if not match:
        raise ConfigError(
            "PCV_GEMINI_IMAGE_ENDPOINT must be the complete .../models/<model>:generateContent URL."
        )
    query_names = {
        key.lower()
        for key in urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    }
    if query_names & {"key", "api_key", "apikey", "token", "access_token", "authorization"}:
        raise ConfigError("Do not put credentials in PCV_GEMINI_IMAGE_ENDPOINT query parameters.")
    return urllib.parse.unquote(match.group(1))


def command_path(args: argparse.Namespace) -> int:
    print(config_path(args.config))
    return 0


def command_paths(args: argparse.Namespace) -> int:
    data = default_data_dir()
    print(f"skill_dir={user_skill_dir()}")
    print(f"env_file={config_path(args.config)}")
    print(f"data_dir={data}")
    print(f"models_dir={data / 'models'}")
    print(f"runtimes_dir={data / 'runtimes'}")
    return 0


def command_init(args: argparse.Namespace) -> int:
    destination = config_path(args.config)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        if not args.replace:
            print(
                f"Configuration already exists: {destination}\n"
                "No file was changed. Use init --replace to archive it and create a fresh template.",
                file=sys.stderr,
            )
            return 2
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive = destination.with_name(f"{destination.name}.bak.{stamp}")
        destination.replace(archive)
        print(f"Archived existing configuration to: {archive}")

    destination.write_text(render_env_template(), encoding="utf-8")
    if os.name != "nt":
        destination.chmod(0o600)
    print(f"Created configuration: {destination}")
    print("Keep this secret-bearing file outside projects. Edit values, then run validate.")
    return 0


def command_show(args: argparse.Namespace) -> int:
    config, path = load_config(args.config)
    print(f"# {path}")
    if path.suffix.lower() == ".json":
        print("# Legacy JSON configuration; run configure.py migrate.")
        print(dump_json(redact(config)), end="")
        return 0
    values = read_env_file(path)
    unknown = set(unknown_env_keys(values))
    for key in sorted(values):
        value = values[key]
        secret_name = key in SECRET_ENV_KEYS or key.upper().endswith(
            (
                "_API_KEY",
                "_TOKEN",
                "_SECRET",
                "_PASSWORD",
                "_AUTHORIZATION",
                "_PRIVATE_KEY",
                "_ENDPOINT",
            )
        )
        if secret_name:
            safe_value = "<set; redacted>" if value else ""
        elif key not in unknown:
            safe_value = value
        else:
            safe_value = "<unknown key; value redacted>"
        print(f"{key}={safe_value}")
    return 0


def command_migrate(args: argparse.Namespace) -> int:
    destination = config_path(args.config)
    source = Path(args.from_json).expanduser().resolve() if args.from_json else legacy_config_path(destination)
    if not source.is_file():
        print(f"Legacy configuration not found: {source}", file=sys.stderr)
        return 2
    legacy = read_json(source)
    if not isinstance(legacy, dict):
        raise ConfigError(f"Legacy configuration root must be an object: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if not args.replace:
            print(
                f"Environment configuration already exists: {destination}\n"
                "No file was changed. Use migrate --replace to archive it first.",
                file=sys.stderr,
            )
            return 2
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        destination_archive = destination.with_name(f"{destination.name}.bak.{stamp}")
        destination.replace(destination_archive)
        print(f"Archived existing environment configuration to: {destination_archive}")

    destination.write_text(render_env_template(legacy), encoding="utf-8")
    if os.name != "nt":
        destination.chmod(0o600)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    source_archive = source.with_name(f"{source.name}.bak.{stamp}")
    source.replace(source_archive)

    unsafe_slots: list[str] = []
    providers = legacy.get("providers", {})
    if isinstance(providers, dict):
        for name, provider in providers.items():
            if not isinstance(provider, dict):
                continue
            reference = provider.get("api_key_env")
            if reference and (not isinstance(reference, str) or not ENV_NAME_RE.fullmatch(reference)):
                unsafe_slots.append(str(name))

    print(f"Created environment configuration: {destination}")
    print(f"Archived legacy JSON configuration to: {source_archive}")
    print("Credential values and legacy credential references were not copied.")
    if unsafe_slots:
        print("Rotate exposed credentials and set new values for: " + ", ".join(sorted(unsafe_slots)))
    return 0


def command_set(args: argparse.Namespace) -> int:
    destination = config_path(args.config)
    key = args.key.strip().upper()
    if key in SECRET_ENV_KEYS:
        print(
            f"Refusing to place {key} on the command line. Edit .env.local privately "
            "or export it from a secret manager.",
            file=sys.stderr,
        )
        return 2
    if key not in ENV_BINDINGS:
        print(f"Unknown configuration key: {key}", file=sys.stderr)
        return 2
    if "\n" in args.value or "\r" in args.value:
        print("Configuration values cannot contain newlines.", file=sys.stderr)
        return 2
    if not destination.is_file():
        print(f"Environment configuration not found: {destination}", file=sys.stderr)
        return 2

    lines = destination.read_text(encoding="utf-8-sig").splitlines()
    replacement = f"{key}={args.value}"
    found = False
    for index, line in enumerate(lines):
        if re.match(rf"^\s*{re.escape(key)}=", line):
            lines[index] = replacement
            found = True
            break
    if not found:
        lines.append(replacement)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    temp = destination.with_name(f"{destination.name}.tmp.{stamp}")
    archive = destination.with_name(f"{destination.name}.bak.{stamp}")
    temp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if os.name != "nt":
        temp.chmod(0o600)
    destination.replace(archive)
    temp.replace(destination)
    print(f"Updated {key} in {destination}")
    print(f"Archived previous configuration to: {archive}")
    return 0


def _dotenv_value(value: str) -> str:
    """Encode a literal dotenv value without shell interpolation."""
    if re.fullmatch(r"[^\s#'\"\\]+", value):
        return value
    return json.dumps(value, ensure_ascii=False)


def _write_env_updates(destination: Path, updates: dict[str, str]) -> Path | None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.suffix.lower() == ".json":
        raise ConfigError("Interactive provider setup requires a .env.local destination, not config.json.")
    if destination.exists():
        lines = destination.read_text(encoding="utf-8-sig").splitlines()
    else:
        lines = render_env_template().splitlines()

    for key, value in updates.items():
        replacement = f"{key}={_dotenv_value(value)}"
        found = False
        for index, line in enumerate(lines):
            if re.match(rf"^\s*{re.escape(key)}=", line):
                lines[index] = replacement
                found = True
                break
        if not found:
            lines.append(replacement)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    temp = destination.with_name(f"{destination.name}.tmp.{stamp}")
    temp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if os.name != "nt":
        temp.chmod(0o600)
    archive: Path | None = None
    if destination.exists():
        archive = destination.with_name(f"{destination.name}.bak.{stamp}")
        destination.replace(archive)
    temp.replace(destination)
    return archive


def _replace_env_text(destination: Path, text: str) -> Path | None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.suffix.lower() == ".json":
        raise ConfigError("Minimal configuration requires a .env.local destination, not config.json.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    temp = destination.with_name(f"{destination.name}.tmp.{stamp}")
    temp.write_text(text.rstrip() + "\n", encoding="utf-8")
    if os.name != "nt":
        temp.chmod(0o600)
    archive: Path | None = None
    if destination.exists():
        archive = destination.with_name(f"{destination.name}.bak.{stamp}")
        destination.replace(archive)
    temp.replace(destination)
    return archive


def _enabled(values: dict[str, str], key: str) -> bool:
    return values.get(key, "").strip().lower() in {"1", "true", "yes", "on"}


def _append_group(lines: list[str], title: str, entries: list[tuple[str, str]]) -> None:
    if not entries:
        return
    lines.extend(["", f"# {title}"])
    lines.extend(f"{key}={_dotenv_value(value)}" for key, value in entries)


def _print_key_summary(lines: list[str], heading: str) -> None:
    print(heading)
    for line in lines:
        match = re.match(r"^([A-Z][A-Z0-9_]*)=", line)
        if match:
            key = match.group(1)
            suffix = "=<set; redacted>" if key in SECRET_ENV_KEYS else ""
            print(f"- {key}{suffix}")


def command_compact(args: argparse.Namespace) -> int:
    destination = config_path(args.config)
    if not destination.is_file():
        raise ConfigError(f"Configuration not found: {destination}")
    if destination.suffix.lower() == ".json":
        raise ConfigError("Run configure.py migrate before compacting configuration.")
    values = read_env_file(destination)
    legacy = sorted(set(values) & set(LEGACY_ENV_ALIASES))
    unknown = [key for key in unknown_env_keys(values) if key not in LEGACY_ENV_ALIASES]
    if unknown:
        raise ConfigError(
            "Refusing to compact a file with unknown keys: " + ", ".join(unknown)
        )
    for old_key in legacy:
        new_key = LEGACY_ENV_ALIASES[old_key]
        if values.get(old_key) and not values.get(new_key):
            raise ConfigError(
                f"Legacy key {old_key} cannot be removed because {new_key} is empty. "
                "Configure the canonical OpenAI image provider first."
            )
    defaults_config = read_json(DEFAULT_CONFIG)
    defaults = config_to_env_values(defaults_config)

    ffmpeg = str(args.ffmpeg or values.get("PCV_FFMPEG") or "ffmpeg")
    ffprobe = str(args.ffprobe or values.get("PCV_FFPROBE") or "ffprobe")
    lines = [
        "# produce-cinematic-video user configuration",
        "# Keep this file private. Add only providers and runtimes you actually enable.",
        "",
        "# Required core tools",
        f"PCV_FFMPEG={_dotenv_value(ffmpeg)}",
        f"PCV_FFPROBE={_dotenv_value(ffprobe)}",
    ]

    dedicated = [
        ("Seedance / ModelArk", "PCV_SEEDANCE_ENABLED", "PCV_SEEDANCE_MODEL", "PCV_SEEDANCE_API_KEY", ("PCV_SEEDANCE_BASE_URL",)),
        ("OpenAI GPT Image", "PCV_OPENAI_IMAGE_ENABLED", "PCV_OPENAI_IMAGE_MODEL", "PCV_OPENAI_IMAGE_API_KEY", ("PCV_OPENAI_IMAGE_BASE_URL",)),
        (
            "Gemini image / Nano Banana",
            "PCV_GEMINI_IMAGE_ENABLED",
            "PCV_GEMINI_IMAGE_MODEL",
            "PCV_GEMINI_IMAGE_API_KEY",
            ("PCV_GEMINI_IMAGE_ENDPOINT", "PCV_GEMINI_IMAGE_BASE_URL"),
        ),
    ]
    for title, enabled_key, model_key, secret_key, connection_keys in dedicated:
        if not _enabled(values, enabled_key):
            continue
        secret = values.get(secret_key, "")
        if not secret:
            raise ConfigError(f"Enabled provider {title} has no {secret_key} value.")
        model = values.get(model_key, "") or defaults.get(model_key, "")
        if not model:
            raise ConfigError(f"Enabled provider {title} has no model value.")
        entries = [(enabled_key, "true"), (model_key, model), (secret_key, secret)]
        for connection_key in connection_keys:
            connection_value = values.get(connection_key, "")
            if connection_value and connection_value != defaults.get(connection_key, ""):
                entries.append((connection_key, connection_value))
        _append_group(lines, title, entries)

    qwen_enabled = _enabled(values, "PCV_QWEN3_TTS_ENABLED") or bool(args.qwen3_voice_design_model)
    if qwen_enabled:
        qwen_python = str(args.qwen3_python or values.get("PCV_QWEN3_TTS_PYTHON") or "python")
        voice_design = str(
            args.qwen3_voice_design_model
            or values.get("PCV_QWEN3_TTS_VOICE_DESIGN_MODEL")
            or ""
        )
        custom_voice = values.get("PCV_QWEN3_TTS_CUSTOM_VOICE_MODEL", "")
        base_model = values.get("PCV_QWEN3_TTS_BASE_MODEL", "")
        if not any((voice_design, custom_voice, base_model)):
            raise ConfigError("Enabled Qwen3-TTS needs at least one model path.")
        entries = [
            ("PCV_QWEN3_TTS_ENABLED", "true"),
            ("PCV_QWEN3_TTS_PYTHON", qwen_python),
        ]
        if voice_design:
            entries.append(("PCV_QWEN3_TTS_VOICE_DESIGN_MODEL", voice_design))
        if custom_voice:
            entries.append(("PCV_QWEN3_TTS_CUSTOM_VOICE_MODEL", custom_voice))
        if base_model:
            entries.append(("PCV_QWEN3_TTS_BASE_MODEL", base_model))
        for key in (
            "PCV_QWEN3_TTS_DEVICE",
            "PCV_QWEN3_TTS_DTYPE",
            "PCV_QWEN3_TTS_ATTENTION",
            "PCV_QWEN3_TTS_OFFLINE",
            "PCV_QWEN3_TTS_LANGUAGE",
        ):
            value = values.get(key, "")
            if value and value != defaults.get(key, ""):
                entries.append((key, value))
        _append_group(lines, "Local Qwen3-TTS", entries)

    if _enabled(values, "PCV_INDEX_TTS2_ENABLED"):
        model = values.get("PCV_INDEX_TTS2_MODEL", "") or defaults.get(
            "PCV_INDEX_TTS2_MODEL", "IndexTTS-2"
        )
        entries = [
            ("PCV_INDEX_TTS2_ENABLED", "true"),
            ("PCV_INDEX_TTS2_MODEL", model),
            ("PCV_INDEX_TTS2_PYTHON", values.get("PCV_INDEX_TTS2_PYTHON", "")),
            ("PCV_INDEX_TTS2_REPO_DIR", values.get("PCV_INDEX_TTS2_REPO_DIR", "")),
            ("PCV_INDEX_TTS2_MODEL_DIR", values.get("PCV_INDEX_TTS2_MODEL_DIR", "")),
        ]
        if any(not value for _, value in entries):
            raise ConfigError("Enabled IndexTTS2 is missing model, Python, repo, or model directory.")
        for key in (
            "PCV_INDEX_TTS2_DEVICE",
            "PCV_INDEX_TTS2_OFFLINE",
            "PCV_INDEX_TTS2_USE_FP16",
            "PCV_INDEX_TTS2_USE_CUDA_KERNEL",
            "PCV_INDEX_TTS2_USE_DEEPSPEED",
            "PCV_INDEX_TTS2_USE_ACCEL",
            "PCV_INDEX_TTS2_USE_TORCH_COMPILE",
            "PCV_INDEX_TTS2_HF_CACHE_DIR",
            "PCV_INDEX_TTS2_NUMBA_CPU_NAME",
        ):
            value = values.get(key, "")
            if value and value != defaults.get(key, ""):
                entries.append((key, value))
        _append_group(lines, "Local IndexTTS2", entries)

    if _enabled(values, "PCV_POCKET_TTS_ENABLED"):
        python_value = values.get("PCV_POCKET_TTS_PYTHON", "") or "python"
        language = values.get("PCV_POCKET_TTS_LANGUAGE", "") or "english"
        if language not in POCKET_TTS_LANGUAGES:
            raise ConfigError("Enabled Pocket TTS has an unsupported language pack.")
        entries = [
            ("PCV_POCKET_TTS_ENABLED", "true"),
            ("PCV_POCKET_TTS_PYTHON", python_value),
            ("PCV_POCKET_TTS_LANGUAGE", language),
        ]
        repo_value = values.get("PCV_POCKET_TTS_REPO_DIR", "")
        if repo_value:
            entries.append(("PCV_POCKET_TTS_REPO_DIR", repo_value))
        for key in (
            "PCV_POCKET_TTS_THREADS",
            "PCV_POCKET_TTS_OFFLINE",
            "PCV_POCKET_TTS_QUANTIZE",
        ):
            value = values.get(key, "")
            if value and value != defaults.get(key, ""):
                entries.append((key, value))
        _append_group(lines, "Local Pocket TTS (CPU-first)", entries)

    if _enabled(values, "PCV_LUX_TTS_ENABLED"):
        python_value = values.get("PCV_LUX_TTS_PYTHON", "") or "python"
        model = values.get("PCV_LUX_TTS_MODEL", "") or "YatharthS/LuxTTS"
        if not model:
            raise ConfigError("Enabled LuxTTS is missing its model ID or local model path.")
        entries = [
            ("PCV_LUX_TTS_ENABLED", "true"),
            ("PCV_LUX_TTS_PYTHON", python_value),
            ("PCV_LUX_TTS_MODEL", model),
        ]
        repo_value = values.get("PCV_LUX_TTS_REPO_DIR", "")
        if repo_value:
            entries.append(("PCV_LUX_TTS_REPO_DIR", repo_value))
        for key in (
            "PCV_LUX_TTS_DEVICE",
            "PCV_LUX_TTS_THREADS",
            "PCV_LUX_TTS_OFFLINE",
        ):
            value = values.get(key, "")
            if value and value != defaults.get(key, ""):
                entries.append((key, value))
        _append_group(lines, "Local LuxTTS (low-VRAM / CPU)", entries)

    if _enabled(values, "PCV_GPT_SOVITS_ENABLED"):
        repo_dir = values.get("PCV_GPT_SOVITS_REPO_DIR", "")
        if not repo_dir:
            raise ConfigError("Enabled GPT-SoVITS UVR5 is missing its repository directory.")
        entries = [
            ("PCV_GPT_SOVITS_ENABLED", "true"),
            ("PCV_GPT_SOVITS_REPO_DIR", repo_dir),
        ]
        python_value = values.get("PCV_GPT_SOVITS_PYTHON", "")
        if python_value:
            entries.append(("PCV_GPT_SOVITS_PYTHON", python_value))
        device = values.get("PCV_GPT_SOVITS_DEVICE", "")
        if device and device != defaults.get("PCV_GPT_SOVITS_DEVICE", ""):
            entries.append(("PCV_GPT_SOVITS_DEVICE", device))
        _append_group(lines, "Local GPT-SoVITS UVR5", entries)

    if _enabled(values, "PCV_LTX_VIDEO_ENABLED"):
        entries = [("PCV_LTX_VIDEO_ENABLED", "true")]
        for key in ("PCV_LTX_VIDEO_BASE_URL", "PCV_LTX_VIDEO_TIMEOUT_S"):
            value = values.get(key, "")
            if value and value != defaults.get(key, ""):
                entries.append((key, value))
        _append_group(lines, "Local LTX-Video", entries)

    for prefix, title in (
        ("PCV_IMAGE_", "Custom image provider"),
        ("PCV_VIDEO_", "Custom video provider"),
        ("PCV_AUDIO_", "Custom audio provider"),
    ):
        if not _enabled(values, prefix + "ENABLED"):
            continue
        entries = [
            (key, value)
            for key, value in values.items()
            if key.startswith(prefix) and value
        ]
        _append_group(lines, title, sorted(entries))

    policy_entries: list[tuple[str, str]] = []
    for key in (
        "PCV_DEFAULT_CURRENCY",
        "PCV_GENERATION_SOFT_LIMIT",
        "PCV_REQUIRE_BUDGET_APPROVAL",
        "PCV_REQUIRE_REMOTE_UPLOAD_APPROVAL",
        "PCV_REQUIRE_PUBLISH_APPROVAL",
        "PCV_RETAIN_PROVENANCE",
    ):
        value = values.get(key, "")
        if value and value != defaults.get(key, ""):
            policy_entries.append((key, value))
    _append_group(lines, "Only non-default policy overrides", policy_entries)

    if not args.confirm:
        print(f"Preview only; no file was changed: {destination}")
        if legacy:
            print("Legacy aliases that would be removed after canonical fields are verified:")
            for key in legacy:
                print(f"- {key} -> {LEGACY_ENV_ALIASES[key]}")
        _print_key_summary(lines, "Would keep keys:")
        print("Re-run with --confirm to archive the current file and write this compact form.")
        return 2

    archive = _replace_env_text(destination, "\n".join(lines))
    print(f"Compacted configuration: {destination}")
    if archive is not None:
        print(f"Archived the previous configuration to: {archive}")
    _print_key_summary(lines, "Kept keys:")
    return 0


def command_setup_provider(args: argparse.Namespace) -> int:
    recipe = PROVIDER_SETUP[args.provider_name]
    destination = config_path(args.config)
    existing: dict[str, str] = {}
    if destination.is_file():
        if destination.suffix.lower() == ".json":
            raise ConfigError("Run configure.py migrate before interactive provider setup.")
        existing = read_env_file(destination)

    secret_key = str(recipe["secret_key"])
    enabled_key = str(recipe["enabled_key"])
    model_key = str(recipe["model_key"])
    model_default = str(recipe["model_default"])
    endpoint_key = str(recipe.get("endpoint_key") or "")
    print(f"Provider: {recipe['label']}")
    print(f"Config: {destination}")
    print(str(recipe["default_note"]))
    print("The key is entered locally with terminal echo disabled; it is never printed.")
    if not sys.stdin.isatty():
        print(
            "Interactive input requires a local terminal. Run this command directly in PowerShell/Terminal; "
            "do not pipe or paste the key into chat.",
            file=sys.stderr,
        )
        return 2

    endpoint = ""
    model = existing.get(model_key) or model_default
    if endpoint_key:
        endpoint_keep_note = " (press Enter to keep the existing value)" if existing.get(endpoint_key) else ""
        endpoint = input(f"{endpoint_key}{endpoint_keep_note}: ").strip()
        if not endpoint and existing.get(endpoint_key):
            endpoint = existing[endpoint_key]
        if not endpoint:
            print("No endpoint was entered; no file was changed.", file=sys.stderr)
            return 2
        model = gemini_model_from_endpoint(endpoint)

    keep_note = " (press Enter to keep the existing value)" if existing.get(secret_key) else ""
    secret = getpass.getpass(f"{secret_key}{keep_note}: ")
    if not secret and existing.get(secret_key):
        secret = existing[secret_key]
    if not secret:
        print("No key was entered; no file was changed.", file=sys.stderr)
        return 2
    if secret != secret.strip() or any(char in secret for char in "\r\n\x00"):
        print("The key contains surrounding whitespace or control characters; no file was changed.", file=sys.stderr)
        return 2

    updates = {
        enabled_key: "true",
        model_key: model,
        secret_key: secret,
    }
    if endpoint_key:
        updates[endpoint_key] = endpoint
    archive = _write_env_updates(destination, updates)
    print(f"Configured: {enabled_key}=true")
    print(f"Configured: {model_key}={model}")
    if endpoint_key:
        print(f"Configured: {endpoint_key}=<set; redacted>")
    print(f"Stored: {secret_key}=<set; redacted>")
    if archive is not None:
        print(f"Archived the previous configuration to: {archive}")
    print("Next: run configure.py validate. A pricing warning is expected until current cost is reviewed.")
    return 0


def command_setup_local(args: argparse.Namespace) -> int:
    if args.local_name != "gpt-sovits":
        raise ConfigError(f"Unknown local runtime: {args.local_name}")
    destination = config_path(args.config)
    if destination.suffix.lower() == ".json":
        raise ConfigError("Run configure.py migrate before local runtime setup.")

    repo_value = str(args.repo_dir or "").strip()
    if not repo_value:
        if not sys.stdin.isatty():
            print(
                "Pass --repo-dir when running non-interactively. No file was changed.",
                file=sys.stderr,
            )
            return 2
        repo_value = input("GPT-SoVITS repository directory: ").strip()
    if not repo_value:
        print("No repository directory was entered; no file was changed.", file=sys.stderr)
        return 2

    repo = Path(os.path.expandvars(os.path.expanduser(repo_value))).resolve()
    required = (
        repo / "tools" / "uvr5" / "webui.py",
        repo / "tools" / "uvr5" / "uvr5_weights",
    )
    missing = [path for path in required if not path.exists()]
    if missing:
        raise ConfigError(
            "This does not look like a GPT-SoVITS installation with UVR5: "
            + ", ".join(str(path) for path in missing)
        )

    bundled = repo / "runtime" / ("python.exe" if os.name == "nt" else "bin/python")
    python_value = str(args.python_executable or "").strip()
    if python_value and not resolve_executable(python_value):
        raise ConfigError(f"Python executable cannot be resolved: {python_value}")
    if not python_value and not bundled.is_file():
        raise ConfigError(
            "No bundled GPT-SoVITS runtime was found. Re-run with --python-executable "
            "pointing to the environment where UVR5 dependencies are installed."
        )

    updates = {
        "PCV_GPT_SOVITS_ENABLED": "true",
        "PCV_GPT_SOVITS_REPO_DIR": str(repo),
    }
    if python_value:
        updates["PCV_GPT_SOVITS_PYTHON"] = python_value
    archive = _write_env_updates(destination, updates)
    print("Configured local GPT-SoVITS UVR5 source separation.")
    print(f"Repository: {repo}")
    print(f"Python: {python_value or bundled} (GPU is preferred automatically when available)")
    if archive is not None:
        print(f"Archived the previous configuration to: {archive}")
    print("Next: run configure.py validate --capability source_separation.")
    return 0


def _prompt_required(label: str, current: str = "") -> str:
    keep = "（回车保留当前值）" if current else ""
    value = input(f"{label}{keep}: ").strip()
    return value or current


def _prompt_optional(label: str, current: str = "") -> str:
    keep = f"（回车保留：{current}）" if current else "（可留空）"
    value = input(f"{label}{keep}: ").strip()
    return value or current


def _setup_local_tts(destination: Path, values: dict[str, str], kind: str) -> None:
    if kind == "qwen3-tts":
        python_value = _prompt_required(
            "Qwen3-TTS 专用 Python",
            values.get("PCV_QWEN3_TTS_PYTHON", ""),
        )
        print("模型用途：1=VoiceDesign 新音色；2=CustomVoice 预置音色；3=Base 授权克隆")
        choice = input("选择 [1/2/3]: ").strip()
        model_keys = {
            "1": ("PCV_QWEN3_TTS_VOICE_DESIGN_MODEL", "VoiceDesign 模型目录"),
            "2": ("PCV_QWEN3_TTS_CUSTOM_VOICE_MODEL", "CustomVoice 模型目录"),
            "3": ("PCV_QWEN3_TTS_BASE_MODEL", "Base 模型目录"),
        }
        if choice not in model_keys:
            raise ConfigError("未选择有效的 Qwen3-TTS 模型用途。")
        model_key, model_label = model_keys[choice]
        model_value = _prompt_required(model_label, values.get(model_key, ""))
        if not python_value or not resolve_executable(python_value):
            raise ConfigError("Qwen3-TTS Python 无法解析。")
        model_path = Path(os.path.expandvars(os.path.expanduser(model_value)))
        if not model_path.is_dir():
            raise ConfigError(f"Qwen3-TTS 模型目录不存在: {model_value}")
        updates = {
            "PCV_QWEN3_TTS_ENABLED": "true",
            "PCV_QWEN3_TTS_PYTHON": python_value,
            model_key: str(model_path.resolve()),
        }
        title = "Qwen3-TTS"
        routing_note = "设备保持 GPU 优先的 auto 默认值。"
    elif kind == "index-tts2":
        python_value = _prompt_required(
            "IndexTTS2 专用 Python",
            values.get("PCV_INDEX_TTS2_PYTHON", ""),
        )
        repo_value = _prompt_required(
            "IndexTTS2 项目目录",
            values.get("PCV_INDEX_TTS2_REPO_DIR", ""),
        )
        model_value = _prompt_required(
            "IndexTTS2 模型目录",
            values.get("PCV_INDEX_TTS2_MODEL_DIR", ""),
        )
        if not python_value or not resolve_executable(python_value):
            raise ConfigError("IndexTTS2 Python 无法解析。")
        repo_path = Path(os.path.expandvars(os.path.expanduser(repo_value)))
        model_path = Path(os.path.expandvars(os.path.expanduser(model_value)))
        if not repo_path.is_dir() or not model_path.is_dir():
            raise ConfigError("IndexTTS2 项目目录或模型目录不存在。")
        updates = {
            "PCV_INDEX_TTS2_ENABLED": "true",
            "PCV_INDEX_TTS2_PYTHON": python_value,
            "PCV_INDEX_TTS2_REPO_DIR": str(repo_path.resolve()),
            "PCV_INDEX_TTS2_MODEL_DIR": str(model_path.resolve()),
        }
        title = "IndexTTS2"
        routing_note = "设备保持 GPU 优先的 auto 默认值。"
    elif kind == "pocket-tts":
        python_value = _prompt_required(
            "Pocket TTS 专用 Python",
            values.get("PCV_POCKET_TTS_PYTHON", "python"),
        )
        repo_value = _prompt_optional(
            "Pocket TTS 源码目录",
            values.get("PCV_POCKET_TTS_REPO_DIR", ""),
        )
        print(
            "语言包："
            + ", ".join(sorted(POCKET_TTS_LANGUAGES))
            + "（目前不含中文）"
        )
        language = _prompt_required(
            "Pocket TTS 语言包",
            values.get("PCV_POCKET_TTS_LANGUAGE", "english"),
        )
        if not resolve_executable(python_value):
            raise ConfigError("Pocket TTS Python 无法解析。")
        if language not in POCKET_TTS_LANGUAGES:
            raise ConfigError("Pocket TTS 语言包不在当前官方支持列表中。")
        updates = {
            "PCV_POCKET_TTS_ENABLED": "true",
            "PCV_POCKET_TTS_PYTHON": python_value,
            "PCV_POCKET_TTS_LANGUAGE": language,
        }
        if repo_value:
            repo_path = Path(os.path.expandvars(os.path.expanduser(repo_value)))
            if not repo_path.is_dir():
                raise ConfigError(f"Pocket TTS 源码目录不存在：{repo_value}")
            updates["PCV_POCKET_TTS_REPO_DIR"] = str(repo_path.resolve())
        title = "Pocket TTS"
        routing_note = "固定采用 CPU 优先；中文会被适配器阻止并改走 Qwen3-TTS/IndexTTS2。"
    elif kind == "lux-tts":
        python_value = _prompt_required(
            "LuxTTS 专用 Python",
            values.get("PCV_LUX_TTS_PYTHON", "python"),
        )
        repo_value = _prompt_optional(
            "LuxTTS 源码目录",
            values.get("PCV_LUX_TTS_REPO_DIR", ""),
        )
        model_value = _prompt_required(
            "LuxTTS 模型 ID 或本地目录",
            values.get("PCV_LUX_TTS_MODEL", "YatharthS/LuxTTS"),
        )
        if not resolve_executable(python_value):
            raise ConfigError("LuxTTS Python 无法解析。")
        updates = {
            "PCV_LUX_TTS_ENABLED": "true",
            "PCV_LUX_TTS_PYTHON": python_value,
            "PCV_LUX_TTS_MODEL": model_value,
        }
        if repo_value:
            repo_path = Path(os.path.expandvars(os.path.expanduser(repo_value)))
            if not repo_path.is_dir():
                raise ConfigError(f"LuxTTS 源码目录不存在：{repo_value}")
            updates["PCV_LUX_TTS_REPO_DIR"] = str(repo_path.resolve())
        title = "LuxTTS"
        routing_note = (
            "设备保持 CUDA → Apple MPS → CPU；上游未公布语言矩阵，正式使用前先做语言试听。"
        )
    else:
        raise ConfigError(f"Unknown local TTS setup: {kind}")

    archive = _write_env_updates(destination, updates)
    print(f"已配置本地 {title}；{routing_note}")
    if archive is not None:
        print(f"上一版已归档：{archive}")


def command_tui(args: argparse.Namespace) -> int:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("TUI 需要直接在本机 PowerShell/Terminal 中运行，不能通过管道输入。", file=sys.stderr)
        return 2
    destination = config_path(args.config)
    if destination.suffix.lower() == ".json":
        raise ConfigError("TUI 只管理 .env.local；请先运行 configure.py migrate。")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        destination.write_text(render_env_template(), encoding="utf-8")
        if os.name != "nt":
            destination.chmod(0o600)
        print(f"已创建最小配置：{destination}")

    while True:
        values = read_env_file(destination)
        print("\n" + "═" * 58)
        print(" produce-cinematic-video 配置向导")
        print(f" 配置文件：{destination}")
        print("═" * 58)
        print(" 1  核心工具（FFmpeg / FFprobe）")
        print(" 2  Seedance 视频")
        print(" 3  Gemini / Nano Banana 中转图像")
        print(" 4  OpenAI GPT Image")
        print(" 5  本地 GPT-SoVITS / UVR5 音源分离")
        print(" 6  本地 Qwen3-TTS")
        print(" 7  本地 IndexTTS2")
        print(" 8  本地 Pocket TTS（低配 CPU，非中文）")
        print(" 9  本地 LuxTTS（低显存 / CPU）")
        print("10  验证当前配置")
        print("11  显示脱敏配置")
        print(" 0  保存并退出")
        choice = input("请选择: ").strip()
        try:
            if choice == "0":
                print(f"配置保存在：{destination}")
                return 0
            if choice == "1":
                ffmpeg = _prompt_required("FFmpeg", values.get("PCV_FFMPEG", "ffmpeg"))
                ffprobe = _prompt_required("FFprobe", values.get("PCV_FFPROBE", "ffprobe"))
                if not resolve_executable(ffmpeg) or not resolve_executable(ffprobe):
                    raise ConfigError("FFmpeg 或 FFprobe 无法解析；请填写完整路径或可用命令名。")
                archive = _write_env_updates(
                    destination,
                    {"PCV_FFMPEG": ffmpeg, "PCV_FFPROBE": ffprobe},
                )
                print("核心工具已保存。" + (f" 上一版：{archive}" if archive else ""))
            elif choice in {"2", "3", "4"}:
                provider_name = {"2": "seedance", "3": "gemini-image", "4": "openai-image"}[choice]
                command_setup_provider(
                    argparse.Namespace(provider_name=provider_name, config=str(destination))
                )
            elif choice == "5":
                repo_dir = _prompt_required(
                    "GPT-SoVITS 项目目录",
                    values.get("PCV_GPT_SOVITS_REPO_DIR", ""),
                )
                command_setup_local(
                    argparse.Namespace(
                        local_name="gpt-sovits",
                        repo_dir=repo_dir,
                        python_executable=None,
                        config=str(destination),
                    )
                )
            elif choice == "6":
                _setup_local_tts(destination, values, "qwen3-tts")
            elif choice == "7":
                _setup_local_tts(destination, values, "index-tts2")
            elif choice == "8":
                _setup_local_tts(destination, values, "pocket-tts")
            elif choice == "9":
                _setup_local_tts(destination, values, "lux-tts")
            elif choice == "10":
                command_validate(
                    argparse.Namespace(config=str(destination), no_tools=False, capability=[])
                )
            elif choice == "11":
                command_show(argparse.Namespace(config=str(destination)))
            else:
                print("请输入菜单中的数字。")
        except (ConfigError, OSError, ValueError) as exc:
            print(f"未保存这一项：{exc}", file=sys.stderr)
        input("按回车返回菜单…")


def command_validate(args: argparse.Namespace) -> int:
    config, path = load_config(args.config)
    issues = validate_config(
        config,
        check_tools=not args.no_tools,
        required_capabilities=args.capability,
    )
    if path.suffix.lower() == ".json":
        issues.append(
            {
                "level": "warning",
                "code": "legacy_json_config",
                "message": "Legacy config.json is active; run configure.py migrate to create .env.local.",
            }
        )
    else:
        env_values = read_env_file(path)
        for key in unknown_env_keys(env_values):
            if key in LEGACY_ENV_ALIASES:
                issues.append(
                    {
                        "level": "warning",
                        "code": "legacy_env_key",
                        "message": (
                            f"Legacy key {key} is ignored; configure.py compact will archive it "
                            f"after verifying {LEGACY_ENV_ALIASES[key]}."
                        ),
                    }
                )
                continue
            issues.append(
                {
                    "level": "warning",
                    "code": "unknown_env_key",
                    "message": f"Unknown key {key} is ignored; check for a typo.",
                }
            )
    if jsonschema is None:
        issues.append(
            {
                "level": "warning",
                "code": "jsonschema_unavailable",
                "message": "Optional jsonschema is unavailable; semantic checks ran, but full config schema validation did not.",
            }
        )
    else:
        schema = read_json(CONFIG_SCHEMA)
        validator = jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker())
        for error in sorted(validator.iter_errors(config), key=lambda item: list(item.absolute_path)):
            suffix = "".join(
                f"[{part}]" if isinstance(part, int) else f".{part}"
                for part in error.absolute_path
            )
            issues.append(
                {
                    "level": "error",
                    "code": "config_schema",
                    "message": f"${suffix}: {error.message}",
                }
            )
    errors = [item for item in issues if item["level"] == "error"]
    warnings = [item for item in issues if item["level"] == "warning"]

    print(f"Config: {path}")
    for item in issues:
        print(f"[{item['level'].upper()}] {item['code']}: {item['message']}")
    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s).")
        return 1
    print(f"PASS: 0 errors, {len(warnings)} warning(s).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage the per-user configuration for produce-cinematic-video."
    )
    parser.add_argument(
        "--config",
        help="Explicit config path. Overrides the standard per-user location.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    path_cmd = sub.add_parser("path", help="Print the resolved config path.")
    path_cmd.set_defaults(func=command_path)

    paths_cmd = sub.add_parser("paths", help="Print user skill, config, model, and runtime locations.")
    paths_cmd.set_defaults(func=command_paths)

    init_cmd = sub.add_parser("init", help="Create .env.local from the bundled template.")
    init_cmd.add_argument(
        "--replace",
        action="store_true",
        help="Archive an existing config and create a fresh template.",
    )
    init_cmd.set_defaults(func=command_init)

    migrate_cmd = sub.add_parser("migrate", help="Convert legacy config.json to .env.local safely.")
    migrate_cmd.add_argument(
        "--from-json",
        help="Explicit legacy config.json path; defaults beside .env.local.",
    )
    migrate_cmd.add_argument(
        "--replace",
        action="store_true",
        help="Archive an existing .env.local before migration.",
    )
    migrate_cmd.set_defaults(func=command_migrate)

    set_cmd = sub.add_parser("set", help="Update one non-secret .env.local value and archive the previous file.")
    set_cmd.add_argument("key", help="Known PCV_* configuration key.")
    set_cmd.add_argument("value", help="New non-secret value.")
    set_cmd.set_defaults(func=command_set)

    setup_cmd = sub.add_parser(
        "setup-provider",
        help="Interactively enable one remote provider and store its key without terminal echo.",
    )
    setup_cmd.add_argument("provider_name", choices=tuple(PROVIDER_SETUP))
    setup_cmd.set_defaults(func=command_setup_provider)

    local_cmd = sub.add_parser(
        "setup-local",
        help="Configure a local runtime without adding optional values to .env.local.",
    )
    local_cmd.add_argument("local_name", choices=LOCAL_SETUP)
    local_cmd.add_argument("--repo-dir", help="GPT-SoVITS repository directory.")
    local_cmd.add_argument(
        "--python-executable",
        help="Only needed when the repository has no bundled runtime/python executable.",
    )
    local_cmd.set_defaults(func=command_setup_local)

    tui_cmd = sub.add_parser(
        "tui",
        help="Open a dependency-free cross-platform terminal configuration wizard.",
    )
    tui_cmd.set_defaults(func=command_tui)

    compact_cmd = sub.add_parser(
        "compact",
        help="Archive a verbose dotenv and keep only active providers, runtimes, and non-default policy overrides.",
    )
    compact_cmd.add_argument("--confirm", action="store_true", help="Required acknowledgement before replacing the active file.")
    compact_cmd.add_argument("--ffmpeg", help="Set the core FFmpeg path while compacting.")
    compact_cmd.add_argument("--ffprobe", help="Set the core FFprobe path while compacting.")
    compact_cmd.add_argument("--qwen3-python", help="Enable/retain Qwen3-TTS with this Python executable.")
    compact_cmd.add_argument("--qwen3-voice-design-model", help="Enable/retain Qwen3-TTS VoiceDesign with this model directory.")
    compact_cmd.set_defaults(func=command_compact)

    show_cmd = sub.add_parser("show", help="Print a redacted copy of the config.")
    show_cmd.set_defaults(func=command_show)

    validate_cmd = sub.add_parser("validate", help="Validate tools, policy, providers, and profiles.")
    validate_cmd.add_argument(
        "--no-tools",
        action="store_true",
        help="Validate structure without requiring executables to resolve.",
    )
    validate_cmd.add_argument(
        "--capability",
        action="append",
        default=[],
        help="Require an enabled provider capability; repeat for multiple capabilities.",
    )
    validate_cmd.set_defaults(func=command_validate)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.func(args))
    except ConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
