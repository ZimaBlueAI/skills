#!/usr/bin/env python3
"""Shared configuration helpers for produce-cinematic-video."""

from __future__ import annotations

import copy
import json
import os
import re
import shutil
import sys
import urllib.parse
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = SKILL_DIR / "assets" / "config.defaults.json"
EXAMPLE_ENV = SKILL_DIR / "assets" / ".env.local.example"
CONFIG_SCHEMA = SKILL_DIR / "schemas" / "config.schema.json"
CONFIG_ENV = "CINEMATIC_VIDEO_ENV_FILE"
LEGACY_CONFIG_ENV = "CINEMATIC_VIDEO_CONFIG"
DATA_ENV = "CINEMATIC_VIDEO_DATA_HOME"

ENV_NAME_RE = re.compile(r"[A-Z][A-Z0-9_]*")
ENV_KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

SECRET_ENV_KEYS = {
    "PCV_IMAGE_API_KEY",
    "PCV_VIDEO_API_KEY",
    "PCV_AUDIO_API_KEY",
    "PCV_OPENAI_IMAGE_API_KEY",
    "PCV_GEMINI_IMAGE_API_KEY",
    "PCV_SEEDANCE_API_KEY",
    "PCV_SEEDREAM_IMAGE_API_KEY",
    "PCV_SUNO_API_KEY",
    "PCV_UDIO_API_KEY",
    "PCV_ELEVENLABS_API_KEY",
}

CAPABILITIES = {
    "text_to_image",
    "image_edit",
    "inpaint",
    "outpaint",
    "text_to_video",
    "image_to_video",
    "first_last_frame",
    "video_extend",
    "reference_identity",
    "synchronized_audio",
    "tts",
    "voice_clone",
    "emotion_control",
    "voice_design",
    "sound_effects",
    "music",
    "transcribe",
    "source_separation",
    "dereverb",
    "audio_mix",
    "av_sync",
}

POCKET_TTS_LANGUAGES = {
    "english",
    "english_2026-01",
    "english_2026-04",
    "french",
    "french_24l",
    "german",
    "german_24l",
    "portuguese",
    "portuguese_24l",
    "italian",
    "italian_24l",
    "spanish",
    "spanish_24l",
}

SECRET_KEYS = {
    "api_key",
    "apikey",
    "secret",
    "token",
    "password",
    "authorization",
    "access_key",
    "private_key",
}

SECRET_VALUE_PATTERNS = (
    re.compile(r"^(?:sk|ark|ghp|github_pat|xox[baprs])-", re.IGNORECASE),
    re.compile(r"^AIza[0-9A-Za-z_-]{20,}$"),
    re.compile(r"^eyJ[0-9A-Za-z_-]+\.[0-9A-Za-z_-]+\.[0-9A-Za-z_-]+$"),
    re.compile(r"^Bearer\s+\S+$", re.IGNORECASE),
)


class ConfigError(RuntimeError):
    """Raised when the user configuration cannot be loaded."""


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError("expected true/false")


def _parse_int(value: str) -> int:
    return int(value.strip())


def _parse_number(value: str) -> int | float:
    normalized = value.strip()
    number = float(normalized)
    return int(number) if number.is_integer() else number


def _parse_optional_number(value: str) -> int | float | None:
    normalized = value.strip().lower()
    if normalized in {"", "none", "null"}:
        return None
    return _parse_number(value)


def _parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_fps(value: str) -> str | int | float:
    normalized = value.strip()
    if normalized.lower() == "source":
        return "source"
    return _parse_number(normalized)


def _parse_text(value: str) -> str:
    return value.strip()


EnvBinding = tuple[tuple[str, ...], Callable[[str], Any]]


ENV_BINDINGS: dict[str, EnvBinding] = {
    "PCV_FFMPEG": (("tools", "ffmpeg"), _parse_text),
    "PCV_FFPROBE": (("tools", "ffprobe"), _parse_text),
    "PCV_IMAGEMAGICK": (("tools", "imagemagick"), _parse_text),
    "PCV_PYTHON": (("tools", "python"), _parse_text),
    "PCV_SCENEDETECT": (("tools", "scenedetect"), _parse_text),
    "PCV_TRANSCRIBER": (("tools", "transcriber"), _parse_text),
    "PCV_NLE": (("tools", "nle"), _parse_text),
    "PCV_IMAGE_ENABLED": (("providers", "image_primary", "enabled"), _parse_bool),
    "PCV_IMAGE_ADAPTER": (("providers", "image_primary", "adapter"), _parse_text),
    "PCV_IMAGE_TOOL_NAME": (("providers", "image_primary", "tool_name"), _parse_text),
    "PCV_IMAGE_BASE_URL": (("providers", "image_primary", "base_url"), _parse_text),
    "PCV_IMAGE_MODEL": (("providers", "image_primary", "model"), _parse_text),
    "PCV_IMAGE_CAPABILITIES": (("providers", "image_primary", "capabilities"), _parse_csv),
    "PCV_IMAGE_REMOTE_UPLOAD": (("providers", "image_primary", "data_policy", "remote_upload"), _parse_bool),
    "PCV_IMAGE_REGION": (("providers", "image_primary", "data_policy", "region"), _parse_text),
    "PCV_IMAGE_UNIT_COST": (("providers", "image_primary", "pricing", "estimated_unit_cost"), _parse_optional_number),
    "PCV_IMAGE_PRICING_CHECKED_AT": (("providers", "image_primary", "pricing", "checked_at"), _parse_text),
    "PCV_OPENAI_IMAGE_ENABLED": (("providers", "openai_image", "enabled"), _parse_bool),
    "PCV_OPENAI_IMAGE_BASE_URL": (("providers", "openai_image", "base_url"), _parse_text),
    "PCV_OPENAI_IMAGE_MODEL": (("providers", "openai_image", "model"), _parse_text),
    "PCV_GEMINI_IMAGE_ENABLED": (("providers", "gemini_image", "enabled"), _parse_bool),
    "PCV_GEMINI_IMAGE_BASE_URL": (("providers", "gemini_image", "base_url"), _parse_text),
    "PCV_GEMINI_IMAGE_ENDPOINT": (("providers", "gemini_image", "endpoint"), _parse_text),
    "PCV_GEMINI_IMAGE_MODEL": (("providers", "gemini_image", "model"), _parse_text),
    "PCV_VIDEO_ENABLED": (("providers", "video_primary", "enabled"), _parse_bool),
    "PCV_VIDEO_ADAPTER": (("providers", "video_primary", "adapter"), _parse_text),
    "PCV_VIDEO_TOOL_NAME": (("providers", "video_primary", "tool_name"), _parse_text),
    "PCV_VIDEO_BASE_URL": (("providers", "video_primary", "base_url"), _parse_text),
    "PCV_VIDEO_MODEL": (("providers", "video_primary", "model"), _parse_text),
    "PCV_VIDEO_CAPABILITIES": (("providers", "video_primary", "capabilities"), _parse_csv),
    "PCV_VIDEO_REMOTE_UPLOAD": (("providers", "video_primary", "data_policy", "remote_upload"), _parse_bool),
    "PCV_VIDEO_REGION": (("providers", "video_primary", "data_policy", "region"), _parse_text),
    "PCV_VIDEO_UNIT_COST": (("providers", "video_primary", "pricing", "estimated_unit_cost"), _parse_optional_number),
    "PCV_VIDEO_PRICING_CHECKED_AT": (("providers", "video_primary", "pricing", "checked_at"), _parse_text),
    "PCV_SEEDANCE_ENABLED": (("providers", "seedance_video", "enabled"), _parse_bool),
    "PCV_SEEDANCE_BASE_URL": (("providers", "seedance_video", "base_url"), _parse_text),
    "PCV_SEEDANCE_MODEL": (("providers", "seedance_video", "model"), _parse_text),
    "PCV_AUDIO_ENABLED": (("providers", "audio_primary", "enabled"), _parse_bool),
    "PCV_AUDIO_ADAPTER": (("providers", "audio_primary", "adapter"), _parse_text),
    "PCV_AUDIO_TOOL_NAME": (("providers", "audio_primary", "tool_name"), _parse_text),
    "PCV_AUDIO_BASE_URL": (("providers", "audio_primary", "base_url"), _parse_text),
    "PCV_AUDIO_MODEL": (("providers", "audio_primary", "model"), _parse_text),
    "PCV_AUDIO_CAPABILITIES": (("providers", "audio_primary", "capabilities"), _parse_csv),
    "PCV_AUDIO_REMOTE_UPLOAD": (("providers", "audio_primary", "data_policy", "remote_upload"), _parse_bool),
    "PCV_AUDIO_REGION": (("providers", "audio_primary", "data_policy", "region"), _parse_text),
    "PCV_AUDIO_UNIT_COST": (("providers", "audio_primary", "pricing", "estimated_unit_cost"), _parse_optional_number),
    "PCV_AUDIO_PRICING_CHECKED_AT": (("providers", "audio_primary", "pricing", "checked_at"), _parse_text),
    "PCV_INDEX_TTS2_ENABLED": (("providers", "index_tts2_local", "enabled"), _parse_bool),
    "PCV_INDEX_TTS2_MODEL": (("providers", "index_tts2_local", "model"), _parse_text),
    "PCV_INDEX_TTS2_PYTHON": (("providers", "index_tts2_local", "runtime", "python_executable"), _parse_text),
    "PCV_INDEX_TTS2_REPO_DIR": (("providers", "index_tts2_local", "runtime", "repo_dir"), _parse_text),
    "PCV_INDEX_TTS2_MODEL_DIR": (("providers", "index_tts2_local", "runtime", "model_dir"), _parse_text),
    "PCV_INDEX_TTS2_DEVICE": (("providers", "index_tts2_local", "runtime", "device"), _parse_text),
    "PCV_INDEX_TTS2_OFFLINE": (("providers", "index_tts2_local", "runtime", "offline"), _parse_bool),
    "PCV_INDEX_TTS2_USE_FP16": (("providers", "index_tts2_local", "runtime", "use_fp16"), _parse_bool),
    "PCV_INDEX_TTS2_USE_CUDA_KERNEL": (("providers", "index_tts2_local", "runtime", "use_cuda_kernel"), _parse_bool),
    "PCV_INDEX_TTS2_USE_DEEPSPEED": (("providers", "index_tts2_local", "runtime", "use_deepspeed"), _parse_bool),
    "PCV_INDEX_TTS2_USE_ACCEL": (("providers", "index_tts2_local", "runtime", "use_accel"), _parse_bool),
    "PCV_INDEX_TTS2_USE_TORCH_COMPILE": (("providers", "index_tts2_local", "runtime", "use_torch_compile"), _parse_bool),
    "PCV_INDEX_TTS2_HF_CACHE_DIR": (("providers", "index_tts2_local", "runtime", "hf_cache_dir"), _parse_text),
    "PCV_INDEX_TTS2_NUMBA_CPU_NAME": (("providers", "index_tts2_local", "runtime", "numba_cpu_name"), _parse_text),
    "PCV_LTX_VIDEO_ENABLED": (("providers", "ltx_video_local", "enabled"), _parse_bool),
    "PCV_LTX_VIDEO_BASE_URL": (("providers", "ltx_video_local", "runtime", "base_url"), _parse_text),
    "PCV_LTX_VIDEO_TIMEOUT_S": (("providers", "ltx_video_local", "runtime", "timeout_s"), _parse_int),
    "PCV_QWEN3_IMAGE_ENABLED": (("providers", "qwen3_image_local", "enabled"), _parse_bool),
    "PCV_QWEN3_IMAGE_BASE_URL": (("providers", "qwen3_image_local", "runtime", "base_url"), _parse_text),
    "PCV_QWEN3_IMAGE_MODEL": (("providers", "qwen3_image_local", "model"), _parse_text),
    "PCV_HUNYUAN3D_ENABLED": (("providers", "hunyuan3d_local", "enabled"), _parse_bool),
    "PCV_HUNYUAN3D_BASE_URL": (("providers", "hunyuan3d_local", "runtime", "base_url"), _parse_text),
    "PCV_BLENDER": (("tools", "blender"), _parse_text),
    "PCV_SEEDREAM_IMAGE_ENABLED": (("providers", "seedream_image", "enabled"), _parse_bool),
    "PCV_SEEDREAM_IMAGE_BASE_URL": (("providers", "seedream_image", "base_url"), _parse_text),
    "PCV_SEEDREAM_IMAGE_MODEL": (("providers", "seedream_image", "model"), _parse_text),
    "PCV_VOXCPM2_ENABLED": (("providers", "voxcpm2_local", "enabled"), _parse_bool),
    "PCV_VOXCPM2_PYTHON": (("providers", "voxcpm2_local", "runtime", "python_executable"), _parse_text),
    "PCV_VOXCPM2_MODEL_DIR": (("providers", "voxcpm2_local", "runtime", "model_dir"), _parse_text),
    "PCV_MOSS_TTS_ENABLED": (("providers", "moss_tts_local", "enabled"), _parse_bool),
    "PCV_MOSS_TTS_PYTHON": (("providers", "moss_tts_local", "runtime", "python_executable"), _parse_text),
    "PCV_MOSS_TTS_MODEL_DIR": (("providers", "moss_tts_local", "runtime", "model_dir"), _parse_text),
    "PCV_FUNASR_ENABLED": (("providers", "funasr_local", "enabled"), _parse_bool),
    "PCV_FUNASR_PYTHON": (("providers", "funasr_local", "runtime", "python_executable"), _parse_text),
    "PCV_FUNASR_MODEL_DIR": (("providers", "funasr_local", "runtime", "model_dir"), _parse_text),
    "PCV_SUNO_ENABLED": (("providers", "suno_music", "enabled"), _parse_bool),
    "PCV_SUNO_BASE_URL": (("providers", "suno_music", "base_url"), _parse_text),
    "PCV_UDIO_ENABLED": (("providers", "udio_music", "enabled"), _parse_bool),
    "PCV_UDIO_BASE_URL": (("providers", "udio_music", "base_url"), _parse_text),
    "PCV_ELEVENLABS_ENABLED": (("providers", "elevenlabs_audio", "enabled"), _parse_bool),
    "PCV_ELEVENLABS_BASE_URL": (("providers", "elevenlabs_audio", "base_url"), _parse_text),
    "PCV_INDEX_TTS2_REFERENCE_EMOTION_ALPHA": (("providers", "index_tts2_local", "runtime", "defaults", "reference_emotion_alpha"), _parse_number),
    "PCV_INDEX_TTS2_TEXT_EMOTION_ALPHA": (("providers", "index_tts2_local", "runtime", "defaults", "text_emotion_alpha"), _parse_number),
    "PCV_INDEX_TTS2_USE_RANDOM": (("providers", "index_tts2_local", "runtime", "defaults", "use_random"), _parse_bool),
    "PCV_INDEX_TTS2_INTERVAL_SILENCE_MS": (("providers", "index_tts2_local", "runtime", "defaults", "interval_silence_ms"), _parse_int),
    "PCV_INDEX_TTS2_MAX_TEXT_TOKENS": (("providers", "index_tts2_local", "runtime", "defaults", "max_text_tokens_per_segment"), _parse_int),
    "PCV_INDEX_TTS2_VERBOSE": (("providers", "index_tts2_local", "runtime", "defaults", "verbose"), _parse_bool),
    "PCV_QWEN3_TTS_ENABLED": (("providers", "qwen3_tts_local", "enabled"), _parse_bool),
    "PCV_QWEN3_TTS_PYTHON": (("providers", "qwen3_tts_local", "runtime", "python_executable"), _parse_text),
    "PCV_QWEN3_TTS_VOICE_DESIGN_MODEL": (("providers", "qwen3_tts_local", "runtime", "voice_design_model"), _parse_text),
    "PCV_QWEN3_TTS_CUSTOM_VOICE_MODEL": (("providers", "qwen3_tts_local", "runtime", "custom_voice_model"), _parse_text),
    "PCV_QWEN3_TTS_BASE_MODEL": (("providers", "qwen3_tts_local", "runtime", "base_model"), _parse_text),
    "PCV_QWEN3_TTS_DEVICE": (("providers", "qwen3_tts_local", "runtime", "device"), _parse_text),
    "PCV_QWEN3_TTS_DTYPE": (("providers", "qwen3_tts_local", "runtime", "dtype"), _parse_text),
    "PCV_QWEN3_TTS_ATTENTION": (("providers", "qwen3_tts_local", "runtime", "attn_implementation"), _parse_text),
    "PCV_QWEN3_TTS_OFFLINE": (("providers", "qwen3_tts_local", "runtime", "offline"), _parse_bool),
    "PCV_QWEN3_TTS_LANGUAGE": (("providers", "qwen3_tts_local", "runtime", "defaults", "language"), _parse_text),
    "PCV_POCKET_TTS_ENABLED": (("providers", "pocket_tts_local", "enabled"), _parse_bool),
    "PCV_POCKET_TTS_PYTHON": (("providers", "pocket_tts_local", "runtime", "python_executable"), _parse_text),
    "PCV_POCKET_TTS_REPO_DIR": (("providers", "pocket_tts_local", "runtime", "repo_dir"), _parse_text),
    "PCV_POCKET_TTS_LANGUAGE": (("providers", "pocket_tts_local", "runtime", "language"), _parse_text),
    "PCV_POCKET_TTS_THREADS": (("providers", "pocket_tts_local", "runtime", "threads"), _parse_int),
    "PCV_POCKET_TTS_OFFLINE": (("providers", "pocket_tts_local", "runtime", "offline"), _parse_bool),
    "PCV_POCKET_TTS_QUANTIZE": (("providers", "pocket_tts_local", "runtime", "quantize"), _parse_bool),
    "PCV_LUX_TTS_ENABLED": (("providers", "lux_tts_local", "enabled"), _parse_bool),
    "PCV_LUX_TTS_MODEL": (("providers", "lux_tts_local", "model"), _parse_text),
    "PCV_LUX_TTS_PYTHON": (("providers", "lux_tts_local", "runtime", "python_executable"), _parse_text),
    "PCV_LUX_TTS_REPO_DIR": (("providers", "lux_tts_local", "runtime", "repo_dir"), _parse_text),
    "PCV_LUX_TTS_DEVICE": (("providers", "lux_tts_local", "runtime", "device"), _parse_text),
    "PCV_LUX_TTS_THREADS": (("providers", "lux_tts_local", "runtime", "threads"), _parse_int),
    "PCV_LUX_TTS_OFFLINE": (("providers", "lux_tts_local", "runtime", "offline"), _parse_bool),
    "PCV_GPT_SOVITS_ENABLED": (("providers", "gpt_sovits_uvr5_local", "enabled"), _parse_bool),
    "PCV_GPT_SOVITS_REPO_DIR": (("providers", "gpt_sovits_uvr5_local", "runtime", "repo_dir"), _parse_text),
    "PCV_GPT_SOVITS_PYTHON": (("providers", "gpt_sovits_uvr5_local", "runtime", "python_executable"), _parse_text),
    "PCV_GPT_SOVITS_DEVICE": (("providers", "gpt_sovits_uvr5_local", "runtime", "device"), _parse_text),
    "PCV_DEFAULT_CURRENCY": (("policy", "default_currency"), _parse_text),
    "PCV_GENERATION_SOFT_LIMIT": (("policy", "generation_soft_limit"), _parse_number),
    "PCV_REQUIRE_BUDGET_APPROVAL": (("policy", "require_budget_approval"), _parse_bool),
    "PCV_REQUIRE_REMOTE_UPLOAD_APPROVAL": (("policy", "require_remote_upload_approval"), _parse_bool),
    "PCV_REQUIRE_PUBLISH_APPROVAL": (("policy", "require_publish_approval"), _parse_bool),
    "PCV_RETAIN_PROVENANCE": (("policy", "retain_provenance"), _parse_bool),
}


for _profile, _prefix in {
    "review": "PCV_DELIVERY_REVIEW",
    "web-horizontal": "PCV_DELIVERY_WEB_HORIZONTAL",
    "web-vertical": "PCV_DELIVERY_WEB_VERTICAL",
    "mezzanine": "PCV_DELIVERY_MEZZANINE",
}.items():
    _base = ("delivery_profiles", _profile)
    ENV_BINDINGS.update(
        {
            f"{_prefix}_CONTAINER": (_base + ("container",), _parse_text),
            f"{_prefix}_VIDEO_CODEC": (_base + ("video", "codec"), _parse_text),
            f"{_prefix}_RESOLUTION": (_base + ("video", "resolution"), _parse_text),
            f"{_prefix}_FPS": (_base + ("video", "fps"), _parse_fps),
            f"{_prefix}_PIXEL_FORMAT": (_base + ("video", "pixel_format"), _parse_text),
            f"{_prefix}_COLOR_SPACE": (_base + ("video", "color_space"), _parse_text),
            f"{_prefix}_AUDIO_CODEC": (_base + ("audio", "codec"), _parse_text),
            f"{_prefix}_SAMPLE_RATE": (_base + ("audio", "sample_rate"), _parse_int),
            f"{_prefix}_CHANNELS": (_base + ("audio", "channels"), _parse_int),
            f"{_prefix}_INTEGRATED_LUFS": (_base + ("audio", "integrated_lufs"), _parse_optional_number),
            f"{_prefix}_TRUE_PEAK_DBTP": (_base + ("audio", "true_peak_dbtp"), _parse_optional_number),
            f"{_prefix}_CAPTION_SIDECAR": (_base + ("captions", "sidecar"), _parse_csv),
            f"{_prefix}_CAPTION_BURNED_IN": (_base + ("captions", "burned_in"), _parse_bool),
        }
    )


def platform_config_path(
    *,
    os_name: str | None = None,
    platform_name: str | None = None,
    environ: Mapping[str, str] | None = None,
    home: str | Path | None = None,
) -> Path:
    """Return the per-user config path for a selected operating system.

    The optional arguments make the platform policy testable without writing to
    a real user's profile.
    """
    current_os = os.name if os_name is None else os_name
    current_platform = sys.platform if platform_name is None else platform_name
    current_env = os.environ if environ is None else environ
    current_home = Path.home() if home is None else Path(home)

    override = current_env.get(CONFIG_ENV) or current_env.get(LEGACY_CONFIG_ENV)
    if override:
        return Path(os.path.expandvars(os.path.expanduser(override))).resolve()

    if current_os == "nt":
        base = current_env.get("APPDATA")
        if base:
            return Path(base) / "produce-cinematic-video" / ".env.local"
        return current_home / "AppData" / "Roaming" / "produce-cinematic-video" / ".env.local"

    base = current_env.get("XDG_CONFIG_HOME")
    if base:
        return Path(base) / "produce-cinematic-video" / ".env.local"

    if current_platform == "darwin":
        return current_home / "Library" / "Application Support" / "produce-cinematic-video" / ".env.local"

    return current_home / ".config" / "produce-cinematic-video" / ".env.local"


def default_config_path() -> Path:
    return platform_config_path()


def legacy_config_path(env_path: str | Path | None = None) -> Path:
    """Return the legacy config.json beside the new .env.local file."""
    selected = config_path(env_path)
    if selected.suffix.lower() == ".json":
        return selected
    return selected.with_name("config.json")


def platform_data_dir(
    *,
    os_name: str | None = None,
    platform_name: str | None = None,
    environ: Mapping[str, str] | None = None,
    home: str | Path | None = None,
) -> Path:
    """Return the per-user directory for large models, runtimes, and caches."""
    current_os = os.name if os_name is None else os_name
    current_platform = sys.platform if platform_name is None else platform_name
    current_env = os.environ if environ is None else environ
    current_home = Path.home() if home is None else Path(home)

    override = current_env.get(DATA_ENV)
    if override:
        return Path(os.path.expandvars(os.path.expanduser(override))).resolve()
    if current_os == "nt":
        base = current_env.get("LOCALAPPDATA")
        if base:
            return Path(base) / "produce-cinematic-video"
        return current_home / "AppData" / "Local" / "produce-cinematic-video"

    xdg = current_env.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / "produce-cinematic-video"
    if current_platform == "darwin":
        return current_home / "Library" / "Application Support" / "produce-cinematic-video"
    return current_home / ".local" / "share" / "produce-cinematic-video"


def default_data_dir() -> Path:
    return platform_data_dir()


def user_skill_dir() -> Path:
    """技能自身的安装位置。同一份源码装在哪个 harness 下都要能找到自己，
    所以按 Codex → 旧版 Codex → Claude Code 的顺序探测，都没有再回落到 Codex。"""
    home = Path.home()
    for candidate in (
        home / ".codex" / "skills" / "produce-cinematic-video",
        home / ".agents" / "skills" / "produce-cinematic-video",
        home / ".claude" / "skills" / "produce-cinematic-video",
    ):
        if candidate.is_dir():
            return candidate
    return home / ".codex" / "skills" / "produce-cinematic-video"


def config_path(explicit: str | Path | None = None) -> Path:
    if explicit:
        return Path(os.path.expandvars(os.path.expanduser(str(explicit)))).resolve()
    return default_config_path()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(
            f"Configuration not found: {path}. Run configure.py init first."
        ) from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"Invalid JSON in {path} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def _decode_env_value(raw: str, *, path: Path, line_number: int) -> str:
    value = raw.strip()
    if not value:
        return ""
    if value[0] in {"'", '"'}:
        quote = value[0]
        if len(value) < 2 or value[-1] != quote:
            raise ConfigError(f"Unclosed quote in {path} at line {line_number}.")
        inner = value[1:-1]
        if quote == "'":
            return inner
        out: list[str] = []
        index = 0
        escapes = {"n": "\n", "r": "\r", "t": "\t", '"': '"', "\\": "\\"}
        while index < len(inner):
            if inner[index] == "\\" and index + 1 < len(inner):
                next_char = inner[index + 1]
                if next_char in escapes:
                    out.append(escapes[next_char])
                    index += 2
                    continue
            out.append(inner[index])
            index += 1
        return "".join(out)
    inline_comment = re.search(r"\s+#", value)
    if inline_comment:
        value = value[: inline_comment.start()].rstrip()
    return value


def read_env_file(path: Path) -> dict[str, str]:
    """Read a dotenv file without shell evaluation or interpolation."""
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except FileNotFoundError as exc:
        raise ConfigError(
            f"Configuration not found: {path}. Run configure.py init first."
        ) from exc

    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(lines, 1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[7:].lstrip()
        if "=" not in stripped:
            raise ConfigError(f"Expected KEY=VALUE in {path} at line {line_number}.")
        key, raw_value = stripped.split("=", 1)
        key = key.strip()
        if not ENV_KEY_RE.fullmatch(key):
            raise ConfigError(f"Invalid environment key '{key}' in {path} at line {line_number}.")
        if key in values:
            raise ConfigError(f"Duplicate environment key '{key}' in {path} at line {line_number}.")
        values[key] = _decode_env_value(raw_value, path=path, line_number=line_number)
    return values


def _deep_set(root: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    node = root
    for part in path[:-1]:
        child = node.get(part)
        if not isinstance(child, dict):
            child = {}
            node[part] = child
        node = child
    node[path[-1]] = value


def _deep_get(root: Mapping[str, Any], path: tuple[str, ...]) -> Any:
    node: Any = root
    for part in path:
        if not isinstance(node, Mapping) or part not in node:
            return None
        node = node[part]
    return node


def _stringify_env(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    return str(value)


def unknown_env_keys(values: Mapping[str, str]) -> list[str]:
    return sorted(set(values) - set(ENV_BINDINGS) - SECRET_ENV_KEYS)


def config_to_env_values(config: Mapping[str, Any]) -> dict[str, str]:
    return {
        key: _stringify_env(_deep_get(config, binding[0]))
        for key, binding in ENV_BINDINGS.items()
    }


def render_env_template(config: Mapping[str, Any] | None = None) -> str:
    try:
        template = EXAMPLE_ENV.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ConfigError(f"Bundled environment template is missing: {EXAMPLE_ENV}") from exc
    replacements = config_to_env_values(config) if config is not None else {}
    rendered: list[str] = []
    for line in template.splitlines():
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=", line)
        if match and match.group(1) in replacements:
            rendered.append(f"{match.group(1)}={replacements[match.group(1)]}")
        else:
            rendered.append(line)
    return "\n".join(rendered) + "\n"


def _load_env_config(path: Path) -> dict[str, Any]:
    defaults = read_json(DEFAULT_CONFIG)
    if not isinstance(defaults, dict):
        raise ConfigError(f"Bundled config defaults must be an object: {DEFAULT_CONFIG}")
    config = copy.deepcopy(defaults)
    file_values = read_env_file(path)
    effective = dict(file_values)
    for key in set(ENV_BINDINGS) | SECRET_ENV_KEYS:
        if key in os.environ:
            effective[key] = os.environ[key]

    for key, (target, parser) in ENV_BINDINGS.items():
        if key not in effective:
            continue
        try:
            parsed = parser(effective[key])
        except (TypeError, ValueError) as exc:
            raise ConfigError(f"Invalid value for {key} in {path}: {exc}") from exc
        _deep_set(config, target, parsed)

    qwen_provider = _deep_get(config, ("providers", "qwen3_tts_local"))
    if isinstance(qwen_provider, dict):
        qwen_runtime = qwen_provider.get("runtime")
        if isinstance(qwen_runtime, dict):
            capabilities = {"tts"}
            if str(qwen_runtime.get("voice_design_model") or "").strip():
                capabilities.update({"voice_design", "emotion_control"})
            if str(qwen_runtime.get("custom_voice_model") or "").strip():
                capabilities.add("emotion_control")
            if str(qwen_runtime.get("base_model") or "").strip():
                capabilities.add("voice_clone")
            qwen_provider["capabilities"] = sorted(capabilities)

    # Secrets remain environment variables and never enter the computed config.
    # An already exported process variable has precedence over the dotenv file.
    for key in SECRET_ENV_KEYS:
        if key not in os.environ and file_values.get(key):
            os.environ[key] = file_values[key]
    return config


def load_config(explicit: str | Path | None = None) -> tuple[dict[str, Any], Path]:
    path = config_path(explicit)
    if not path.exists() and path.suffix.lower() != ".json":
        legacy = legacy_config_path(path)
        if legacy.exists():
            path = legacy
    data = read_json(path) if path.suffix.lower() == ".json" else _load_env_config(path)
    if not isinstance(data, dict):
        raise ConfigError(f"Configuration root must be an object: {path}")
    return data, path


def resolve_executable(value: str) -> str | None:
    if not value:
        return None
    expanded = os.path.expandvars(os.path.expanduser(value))
    candidate = Path(expanded)
    if candidate.is_absolute() or candidate.parent != Path("."):
        if candidate.is_file():
            return str(candidate.resolve())
        return None
    return shutil.which(expanded)


def resolve_sox() -> str | None:
    """Resolve SoX from PATH or the standard WinGet package layout."""
    resolved = resolve_executable("sox")
    if resolved:
        return resolved
    local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
    if not local_app_data:
        return None
    root = Path(local_app_data)
    candidates = [root / "Microsoft" / "WinGet" / "Links" / "sox.exe"]
    packages = root / "Microsoft" / "WinGet" / "Packages"
    if packages.is_dir():
        candidates.extend(
            sorted(packages.glob("ChrisBagwell.SoX_*/*/sox.exe"), reverse=True)
        )
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate.resolve())
    return None


def runtime_environment_with_sox() -> dict[str, str]:
    """Return a child environment that exposes an installed SoX without mutating user PATH."""
    environment = dict(os.environ)
    sox = resolve_sox()
    if sox:
        parent = str(Path(sox).parent)
        current = environment.get("PATH", "")
        entries = current.split(os.pathsep) if current else []
        if parent.casefold() not in {entry.casefold() for entry in entries}:
            environment["PATH"] = parent + (os.pathsep + current if current else "")
    return environment


def resolve_tool(config: dict[str, Any], name: str, override: str | None = None) -> str:
    value = override or str(config.get("tools", {}).get(name, ""))
    resolved = resolve_executable(value)
    if not resolved:
        raise ConfigError(
            f"Tool '{name}' is not available from configured value '{value}'. "
            "Update the user config or pass an explicit executable."
        )
    return resolved


def issue(level: str, code: str, message: str) -> dict[str, str]:
    return {"level": level, "code": code, "message": message}


def _looks_like_secret_value(value: Any) -> bool:
    return isinstance(value, str) and any(pattern.search(value.strip()) for pattern in SECRET_VALUE_PATTERNS)


def _secret_field_name(key: str) -> bool:
    key_l = key.lower()
    return key_l in SECRET_KEYS or any(
        key_l.endswith(suffix)
        for suffix in ("_api_key", "_secret", "_token", "_password", "_authorization", "_private_key")
    )


def _secret_issues(value: Any, path: str = "$") -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_l = str(key).lower()
            child_path = f"{path}.{key}"
            if key_l.endswith("_env") and child not in ("", None) and (
                not isinstance(child, str) or not ENV_NAME_RE.fullmatch(child)
            ):
                findings.append(
                    issue(
                        "error",
                        "invalid_secret_reference",
                        f"{child_path} must contain an uppercase environment-variable name, never a secret value.",
                    )
                )
            elif _secret_field_name(str(key)) and not key_l.endswith("_env") and child not in ("", None):
                findings.append(
                    issue(
                        "error",
                        "plaintext_secret",
                        f"{child_path} appears to contain a plaintext secret; store only an environment-variable name.",
                    )
                )
            elif _looks_like_secret_value(child):
                findings.append(
                    issue(
                        "error",
                        "plaintext_secret_pattern",
                        f"{child_path} resembles a plaintext credential and must be moved to .env.local or the process environment.",
                    )
                )
            findings.extend(_secret_issues(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_secret_issues(child, f"{path}[{index}]"))
    return findings


def redact(value: Any) -> Any:
    out = copy.deepcopy(value)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key in list(node):
                key_l = str(key).lower()
                invalid_env_reference = key_l.endswith("_env") and node[key] not in ("", None) and (
                    not isinstance(node[key], str) or not ENV_NAME_RE.fullmatch(node[key])
                )
                if (
                    (_secret_field_name(str(key)) and not key_l.endswith("_env"))
                    or invalid_env_reference
                    or _looks_like_secret_value(node[key])
                ) and node[key] not in ("", None):
                    node[key] = "***REDACTED***"
                else:
                    walk(node[key])
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(out)
    return out


def enabled_providers(config: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    providers = config.get("providers", {})
    if not isinstance(providers, dict):
        return []
    return [
        (name, provider)
        for name, provider in providers.items()
        if isinstance(provider, dict) and provider.get("enabled") is True
    ]


def providers_for_capability(
    config: dict[str, Any], capability: str
) -> list[tuple[str, dict[str, Any]]]:
    return [
        (name, provider)
        for name, provider in enabled_providers(config)
        if capability in provider.get("capabilities", [])
    ]


def validate_config(
    config: dict[str, Any],
    *,
    check_tools: bool = True,
    required_capabilities: list[str] | None = None,
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    required_capabilities = required_capabilities or []

    if config.get("version") != 1:
        issues.append(issue("error", "version", "Config version must be 1."))

    tools = config.get("tools")
    if not isinstance(tools, dict):
        issues.append(issue("error", "tools", "tools must be an object."))
    else:
        for name in ("ffmpeg", "ffprobe"):
            value = tools.get(name)
            if not isinstance(value, str) or not value:
                issues.append(issue("error", f"tool_{name}", f"tools.{name} must be a non-empty string."))
            elif check_tools and not resolve_executable(value):
                issues.append(
                    issue(
                        "error",
                        f"tool_{name}_missing",
                        f"tools.{name} cannot be resolved from '{value}'.",
                    )
                )
        for name, value in tools.items():
            if name not in {"ffmpeg", "ffprobe"} and value:
                if not isinstance(value, str):
                    issues.append(issue("error", f"tool_{name}", f"tools.{name} must be a string."))
                elif check_tools and not resolve_executable(value):
                    issues.append(
                        issue(
                            "warning",
                            f"tool_{name}_missing",
                            f"Optional tool tools.{name} cannot be resolved from '{value}'.",
                        )
                    )

    providers = config.get("providers")
    if not isinstance(providers, dict):
        issues.append(issue("error", "providers", "providers must be an object."))
        providers = {}

    for name, provider in providers.items():
        if not isinstance(provider, dict):
            issues.append(issue("error", f"provider_{name}", f"providers.{name} must be an object."))
            continue
        capabilities = provider.get("capabilities")
        if not isinstance(capabilities, list):
            issues.append(
                issue("error", f"provider_{name}_capabilities", f"providers.{name}.capabilities must be an array.")
            )
            capabilities = []
        invalid = sorted(set(capabilities) - CAPABILITIES)
        if invalid:
            issues.append(
                issue(
                    "error",
                    f"provider_{name}_capability_unknown",
                    f"providers.{name} has unknown capabilities: {', '.join(invalid)}.",
                )
            )
        if len(capabilities) != len(set(capabilities)):
            issues.append(
                issue("error", f"provider_{name}_capability_duplicate", f"providers.{name} repeats capabilities.")
            )

        adapter = provider.get("adapter")
        if adapter == "gemini_images":
            endpoint = provider.get("endpoint", "")
            if endpoint and not isinstance(endpoint, str):
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_endpoint",
                        f"providers.{name}.endpoint must be a string.",
                    )
                )
            elif isinstance(endpoint, str) and endpoint:
                parsed_endpoint = urllib.parse.urlsplit(endpoint)
                if (
                    parsed_endpoint.scheme != "https"
                    or not parsed_endpoint.netloc
                    or parsed_endpoint.username is not None
                    or parsed_endpoint.password is not None
                    or parsed_endpoint.fragment
                ):
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_endpoint_url",
                            f"providers.{name}.endpoint must be an absolute HTTPS URL without user info or a fragment.",
                        )
                    )
                model_match = re.search(r"/models/([^/]+):generateContent$", parsed_endpoint.path)
                if not model_match:
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_endpoint_shape",
                            f"providers.{name}.endpoint must be the complete Gemini .../models/<model>:generateContent URL.",
                        )
                    )
                else:
                    endpoint_model = urllib.parse.unquote(model_match.group(1))
                    configured_model = str(provider.get("model") or "").strip()
                    if configured_model and endpoint_model != configured_model:
                        issues.append(
                            issue(
                                "error",
                                f"provider_{name}_endpoint_model",
                                f"providers.{name}.model must match the model encoded in its endpoint.",
                            )
                        )
                sensitive_query_names = {
                    key.lower()
                    for key in urllib.parse.parse_qs(parsed_endpoint.query, keep_blank_values=True)
                } & {"key", "api_key", "apikey", "token", "access_token", "authorization"}
                if sensitive_query_names:
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_endpoint_query_secret",
                            f"providers.{name}.endpoint must not carry credentials in its query string.",
                        )
                    )

        elif adapter == "index_tts2_local":
            runtime = provider.get("runtime")
            if not isinstance(runtime, dict):
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_runtime",
                        f"providers.{name}.runtime must be an object for index_tts2_local.",
                    )
                )
                runtime = {}

            for key in (
                "offline",
                "use_fp16",
                "use_cuda_kernel",
                "use_deepspeed",
                "use_accel",
                "use_torch_compile",
            ):
                if key in runtime and not isinstance(runtime.get(key), bool):
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_runtime_{key}",
                            f"providers.{name}.runtime.{key} must be boolean.",
                        )
                    )

            device = runtime.get("device")
            if device is not None and (
                not isinstance(device, str)
                or not re.fullmatch(r"(?:auto|cpu|mps|xpu|cuda(?::[0-9]+)?)", device)
            ):
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_runtime_device",
                        f"providers.{name}.runtime.device is invalid.",
                    )
                )
            if device == "cpu" and runtime.get("use_fp16") is True:
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_cpu_fp16",
                        "IndexTTS2 use_fp16 cannot be enabled with device=cpu.",
                    )
                )
            if isinstance(device, str) and device not in {"auto", "cuda"} and not device.startswith("cuda:"):
                for key in ("use_cuda_kernel", "use_deepspeed"):
                    if runtime.get(key) is True:
                        issues.append(
                            issue(
                                "error",
                                f"provider_{name}_{key}_device",
                                f"IndexTTS2 {key} requires CUDA or device=auto that resolves to CUDA.",
                            )
                        )

            defaults = runtime.get("defaults")
            if defaults is not None and not isinstance(defaults, dict):
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_runtime_defaults",
                        f"providers.{name}.runtime.defaults must be an object.",
                    )
                )
                defaults = {}
            if isinstance(defaults, dict):
                for key in ("reference_emotion_alpha", "text_emotion_alpha"):
                    value = defaults.get(key)
                    if value is not None and (
                        not isinstance(value, (int, float))
                        or isinstance(value, bool)
                        or value < 0
                        or value > 1
                    ):
                        issues.append(
                            issue(
                                "error",
                                f"provider_{name}_{key}",
                                f"providers.{name}.runtime.defaults.{key} must be between 0 and 1.",
                            )
                        )
                if defaults.get("use_random") is True:
                    issues.append(
                        issue(
                            "warning",
                            f"provider_{name}_random",
                            "IndexTTS2 random emotion sampling can reduce voice-clone fidelity.",
                        )
                    )

            if provider.get("enabled") is True:
                missing_caps = sorted({"tts", "voice_clone"} - set(capabilities))
                if missing_caps:
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_index_capabilities",
                            "Enabled IndexTTS2 provider is missing capabilities: " + ", ".join(missing_caps) + ".",
                        )
                    )
                data_policy = provider.get("data_policy")
                if not isinstance(data_policy, dict) or data_policy.get("remote_upload") is not False:
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_index_remote",
                            "index_tts2_local must declare data_policy.remote_upload as false.",
                        )
                    )
                python_value = runtime.get("python_executable")
                if not isinstance(python_value, str) or not python_value:
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_python",
                            f"Enabled provider {name} needs runtime.python_executable.",
                        )
                    )
                elif check_tools and not resolve_executable(python_value):
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_python_missing",
                            f"providers.{name}.runtime.python_executable cannot be resolved from '{python_value}'.",
                        )
                    )
                for key in ("repo_dir", "model_dir"):
                    raw_path = runtime.get(key)
                    if not isinstance(raw_path, str) or not raw_path:
                        issues.append(
                            issue(
                                "error",
                                f"provider_{name}_{key}",
                                f"Enabled provider {name} needs runtime.{key}.",
                            )
                        )
                    elif check_tools:
                        expanded_path = Path(os.path.expandvars(os.path.expanduser(raw_path)))
                        if not expanded_path.is_dir():
                            issues.append(
                                issue(
                                    "error",
                                    f"provider_{name}_{key}_missing",
                                    f"providers.{name}.runtime.{key} is not a directory: {raw_path}.",
                                )
                            )

        elif adapter == "qwen3_tts_local":
            runtime = provider.get("runtime")
            if not isinstance(runtime, dict):
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_runtime",
                        f"providers.{name}.runtime must be an object for qwen3_tts_local.",
                    )
                )
                runtime = {}
            offline = runtime.get("offline", True)
            if not isinstance(offline, bool):
                issues.append(
                    issue("error", f"provider_{name}_offline", f"providers.{name}.runtime.offline must be boolean.")
                )
            device = runtime.get("device", "auto")
            if not isinstance(device, str) or not re.fullmatch(
                r"(?:auto|cpu|mps|xpu|cuda(?::[0-9]+)?)", device
            ):
                issues.append(
                    issue("error", f"provider_{name}_device", f"providers.{name}.runtime.device is invalid.")
                )
            dtype = runtime.get("dtype", "auto")
            if dtype not in {"auto", "float32", "float16", "bfloat16"}:
                issues.append(
                    issue("error", f"provider_{name}_dtype", f"providers.{name}.runtime.dtype is invalid.")
                )
            if device == "cpu" and dtype not in {"auto", "float32"}:
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_cpu_dtype",
                        "Qwen3-TTS device=cpu requires dtype=auto or float32.",
                    )
                )
            attention = runtime.get("attn_implementation", "auto")
            if attention not in {"auto", "eager", "sdpa", "flash_attention_2"}:
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_attention",
                        f"providers.{name}.runtime.attn_implementation is invalid.",
                    )
                )
            if attention == "flash_attention_2" and isinstance(device, str) and not (
                device == "auto" or device == "cuda" or device.startswith("cuda:")
            ):
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_flash_device",
                        "Qwen3-TTS flash_attention_2 requires CUDA or device=auto that resolves to CUDA.",
                    )
                )

            if provider.get("enabled") is True:
                data_policy = provider.get("data_policy")
                if not isinstance(data_policy, dict) or data_policy.get("remote_upload") is not False:
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_qwen_remote",
                            "qwen3_tts_local must declare data_policy.remote_upload as false.",
                        )
                    )
                python_value = runtime.get("python_executable")
                if not isinstance(python_value, str) or not python_value:
                    issues.append(
                        issue("error", f"provider_{name}_python", f"Enabled provider {name} needs runtime.python_executable.")
                    )
                elif check_tools and not resolve_executable(python_value):
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_python_missing",
                            f"providers.{name}.runtime.python_executable cannot be resolved from '{python_value}'.",
                        )
                    )
                models = {
                    key: str(runtime.get(key) or "").strip()
                    for key in ("voice_design_model", "custom_voice_model", "base_model")
                }
                if not any(models.values()):
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_models",
                            "Enabled Qwen3-TTS needs at least one configured model.",
                        )
                    )
                if check_tools and offline is True:
                    for key, raw_path in models.items():
                        if not raw_path:
                            continue
                        candidate = Path(os.path.expandvars(os.path.expanduser(raw_path)))
                        if not candidate.is_dir():
                            issues.append(
                                issue(
                                    "error",
                                    f"provider_{name}_{key}_missing",
                                    f"Offline Qwen3-TTS model must be a local directory: {raw_path}.",
                                )
                            )

        elif adapter in {"pocket_tts_local", "lux_tts_local"}:
            runtime = provider.get("runtime")
            if not isinstance(runtime, dict):
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_runtime",
                        f"providers.{name}.runtime must be an object for {adapter}.",
                    )
                )
                runtime = {}
            offline = runtime.get("offline", True)
            if not isinstance(offline, bool):
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_offline",
                        f"providers.{name}.runtime.offline must be boolean.",
                    )
                )
            threads = runtime.get("threads", 2)
            if (
                not isinstance(threads, int)
                or isinstance(threads, bool)
                or threads < 1
                or threads > 64
            ):
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_threads",
                        f"providers.{name}.runtime.threads must be an integer from 1 to 64.",
                    )
                )

            if adapter == "pocket_tts_local":
                language = runtime.get("language", "english")
                if language not in POCKET_TTS_LANGUAGES:
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_language",
                            "Pocket TTS language must be one of the currently documented language packs.",
                        )
                    )
                if not isinstance(runtime.get("quantize", False), bool):
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_quantize",
                            f"providers.{name}.runtime.quantize must be boolean.",
                        )
                    )
                if provider.get("enabled") is True:
                    issues.append(
                        issue(
                            "warning",
                            f"provider_{name}_language_boundary",
                            "Pocket TTS currently has no Chinese language pack; route Chinese "
                            "speech to Qwen3-TTS or IndexTTS2.",
                        )
                    )
            else:
                device = runtime.get("device", "auto")
                if not isinstance(device, str) or not re.fullmatch(
                    r"(?:auto|cpu|mps|cuda(?::[0-9]+)?)", device
                ):
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_device",
                            f"providers.{name}.runtime.device is invalid.",
                        )
                    )
                if provider.get("enabled") is True and not str(
                    provider.get("model") or ""
                ).strip():
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_model",
                            "Enabled LuxTTS needs an explicit model ID or local model directory.",
                        )
                    )
                if provider.get("enabled") is True:
                    issues.append(
                        issue(
                            "warning",
                            f"provider_{name}_language_unverified",
                            "LuxTTS upstream does not publish a language matrix; approve a "
                            "language-specific audition before production use.",
                        )
                    )

            if provider.get("enabled") is True:
                missing_caps = sorted(
                    {"tts", "voice_clone"} - set(capabilities)
                )
                if missing_caps:
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_tts_capabilities",
                            f"Enabled {adapter} provider is missing capabilities: "
                            + ", ".join(missing_caps)
                            + ".",
                        )
                    )
                data_policy = provider.get("data_policy")
                if (
                    not isinstance(data_policy, dict)
                    or data_policy.get("remote_upload") is not False
                ):
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_remote",
                            f"{adapter} must declare data_policy.remote_upload as false.",
                        )
                    )
                python_value = runtime.get("python_executable")
                if not isinstance(python_value, str) or not python_value:
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_python",
                            f"Enabled provider {name} needs runtime.python_executable.",
                        )
                    )
                elif check_tools and not resolve_executable(python_value):
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_python_missing",
                            f"providers.{name}.runtime.python_executable cannot be resolved "
                            f"from '{python_value}'.",
                        )
                    )
                repo_value = runtime.get("repo_dir", "")
                if repo_value and (
                    not isinstance(repo_value, str)
                    or (
                        check_tools
                        and not Path(
                            os.path.expandvars(os.path.expanduser(repo_value))
                        ).is_dir()
                    )
                ):
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_repo_dir",
                            f"providers.{name}.runtime.repo_dir is not a directory: {repo_value}.",
                        )
                    )

        elif adapter == "gpt_sovits_uvr5_local":
            runtime = provider.get("runtime")
            if not isinstance(runtime, dict):
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_runtime",
                        f"providers.{name}.runtime must be an object for gpt_sovits_uvr5_local.",
                    )
                )
                runtime = {}
            device = runtime.get("device", "auto")
            if not isinstance(device, str) or not re.fullmatch(
                r"(?:auto|cpu|mps|cuda(?::[0-9]+)?)", device
            ):
                issues.append(
                    issue("error", f"provider_{name}_device", f"providers.{name}.runtime.device is invalid.")
                )
            offline = runtime.get("offline", True)
            if not isinstance(offline, bool):
                issues.append(
                    issue("error", f"provider_{name}_offline", f"providers.{name}.runtime.offline must be boolean.")
                )

            if provider.get("enabled") is True:
                if "source_separation" not in set(capabilities):
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_uvr_capabilities",
                            "Enabled GPT-SoVITS UVR5 must declare source_separation.",
                        )
                    )
                data_policy = provider.get("data_policy")
                if not isinstance(data_policy, dict) or data_policy.get("remote_upload") is not False:
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_uvr_remote",
                            "gpt_sovits_uvr5_local must declare data_policy.remote_upload as false.",
                        )
                    )
                repo_value = runtime.get("repo_dir")
                repo_path: Path | None = None
                if not isinstance(repo_value, str) or not repo_value.strip():
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_repo_dir",
                            f"Enabled provider {name} needs runtime.repo_dir.",
                        )
                    )
                else:
                    repo_path = Path(os.path.expandvars(os.path.expanduser(repo_value)))
                    if check_tools and not repo_path.is_dir():
                        issues.append(
                            issue(
                                "error",
                                f"provider_{name}_repo_dir_missing",
                                f"providers.{name}.runtime.repo_dir is not a directory: {repo_value}.",
                            )
                        )
                    elif check_tools:
                        for code, relative in (
                            ("uvr_webui", Path("tools") / "uvr5" / "webui.py"),
                            ("uvr_weights", Path("tools") / "uvr5" / "uvr5_weights"),
                        ):
                            if not (repo_path / relative).exists():
                                issues.append(
                                    issue(
                                        "error",
                                        f"provider_{name}_{code}_missing",
                                        f"GPT-SoVITS component is missing: {repo_path / relative}.",
                                    )
                                )

                python_value = str(runtime.get("python_executable") or "").strip()
                if not python_value and repo_path is not None:
                    bundled_python = repo_path / "runtime" / (
                        "python.exe" if os.name == "nt" else "bin/python"
                    )
                    python_value = str(bundled_python) if bundled_python.is_file() else sys.executable
                if check_tools and (not python_value or not resolve_executable(python_value)):
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_python_missing",
                            "GPT-SoVITS Python could not be resolved. Set PCV_GPT_SOVITS_PYTHON "
                            "only when <repo>/runtime/python is unavailable.",
                        )
                    )

        if provider.get("enabled") is True:
            tool_name = provider.get("tool_name")
            if not isinstance(adapter, str) or not adapter:
                issues.append(
                    issue("error", f"provider_{name}_adapter", f"Enabled provider {name} needs an adapter.")
                )
            if adapter == "tool" and (not isinstance(tool_name, str) or not tool_name):
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_tool",
                        f"Provider {name} uses adapter 'tool' but tool_name is empty.",
                    )
                )
            if not capabilities:
                issues.append(
                    issue(
                        "error",
                        f"provider_{name}_capabilities_empty",
                        f"Enabled provider {name} must declare at least one capability.",
                    )
                )
            key_env = provider.get("api_key_env")
            if key_env:
                if not isinstance(key_env, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*", key_env):
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_key_env",
                            f"providers.{name}.api_key_env must be an uppercase environment-variable name.",
                        )
                    )
                elif not os.environ.get(key_env):
                    issues.append(
                        issue(
                            "error",
                            f"provider_{name}_credential_missing",
                            f"Enabled provider {name} expects environment variable {key_env}, but it is not set.",
                        )
                    )
            pricing = provider.get("pricing", {})
            if not isinstance(pricing, dict) or pricing.get("estimated_unit_cost") is None:
                issues.append(
                    issue(
                        "warning",
                        f"provider_{name}_pricing_unknown",
                        f"Provider {name} has no current cost estimate; do not treat generation as free.",
                    )
                )
            elif not pricing.get("checked_at"):
                issues.append(
                    issue(
                        "warning",
                        f"provider_{name}_pricing_date",
                        f"Provider {name} pricing has no checked_at date.",
                    )
                )

    for capability in required_capabilities:
        if capability not in CAPABILITIES:
            issues.append(issue("error", "required_capability_unknown", f"Unknown required capability: {capability}."))
        elif not providers_for_capability(config, capability):
            issues.append(
                issue(
                    "error",
                    "required_capability_missing",
                    f"No enabled provider declares capability '{capability}'.",
                )
            )

    policy = config.get("policy")
    if not isinstance(policy, dict):
        issues.append(issue("error", "policy", "policy must be an object."))
    else:
        limit = policy.get("generation_soft_limit")
        if not isinstance(limit, (int, float)) or isinstance(limit, bool) or limit < 0:
            issues.append(issue("error", "policy_budget", "policy.generation_soft_limit must be a non-negative number."))
        if policy.get("allow_synthetic_documentary_evidence") is not False:
            issues.append(
                issue(
                    "error",
                    "policy_documentary_evidence",
                    "allow_synthetic_documentary_evidence must remain false.",
                )
            )
        for key in (
            "require_budget_approval",
            "require_remote_upload_approval",
            "require_publish_approval",
            "retain_provenance",
        ):
            if not isinstance(policy.get(key), bool):
                issues.append(issue("error", f"policy_{key}", f"policy.{key} must be boolean."))

    profiles = config.get("delivery_profiles")
    if not isinstance(profiles, dict) or not profiles:
        issues.append(issue("error", "delivery_profiles", "delivery_profiles must contain at least one profile."))
    else:
        for name, profile in profiles.items():
            if not isinstance(profile, dict):
                issues.append(issue("error", f"profile_{name}", f"delivery profile {name} must be an object."))
                continue
            video = profile.get("video", {})
            audio = profile.get("audio", {})
            if not re.fullmatch(r"[0-9]+x[0-9]+", str(video.get("resolution", ""))):
                issues.append(
                    issue("error", f"profile_{name}_resolution", f"delivery profile {name} has invalid resolution.")
                )
            fps = video.get("fps")
            if fps != "source" and (
                not isinstance(fps, (int, float)) or isinstance(fps, bool) or fps <= 0
            ):
                issues.append(issue("error", f"profile_{name}_fps", f"delivery profile {name} has invalid fps."))
            sample_rate = audio.get("sample_rate")
            if not isinstance(sample_rate, int) or isinstance(sample_rate, bool) or sample_rate < 8000:
                issues.append(
                    issue("error", f"profile_{name}_sample_rate", f"delivery profile {name} has invalid sample_rate.")
                )

    issues.extend(_secret_issues(config))
    return issues


def dump_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"
