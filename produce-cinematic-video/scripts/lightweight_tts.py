#!/usr/bin/env python3
"""Safe control-plane CLI for local Pocket TTS and LuxTTS."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cinematic_config import (
    ConfigError,
    dump_json,
    load_config,
    resolve_executable,
    runtime_environment_with_sox,
)
from lightweight_tts_runner import expand_path


RUNNER = Path(__file__).with_name("lightweight_tts_runner.py")
ADAPTERS = {
    "pocket": "pocket_tts_local",
    "lux": "lux_tts_local",
}
POCKET_LANGUAGES = {
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
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
REMOTE_REFERENCE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")


class LightweightTtsError(RuntimeError):
    """Raised when a lightweight TTS request violates a local gate."""


def adapter_engine(provider: dict[str, Any]) -> str | None:
    adapter = provider.get("adapter")
    for engine, expected in ADAPTERS.items():
        if adapter == expected:
            return engine
    return None


def find_provider(
    config: dict[str, Any], requested: str | None, requested_engine: str | None
) -> tuple[str, dict[str, Any], str]:
    providers = config.get("providers")
    if not isinstance(providers, dict):
        raise LightweightTtsError("Config providers must be an object.")
    if requested:
        provider = providers.get(requested)
        if not isinstance(provider, dict):
            raise LightweightTtsError(f"Provider does not exist: {requested}")
        engine = adapter_engine(provider)
        if engine is None:
            raise LightweightTtsError(
                f"Provider {requested} is not a Pocket TTS or LuxTTS provider."
            )
        if requested_engine and requested_engine != engine:
            raise LightweightTtsError(
                f"Provider {requested} uses engine {engine}, not {requested_engine}."
            )
        return requested, provider, engine

    matches: list[tuple[str, dict[str, Any], str]] = []
    for name, provider in providers.items():
        if not isinstance(provider, dict):
            continue
        engine = adapter_engine(provider)
        if engine is None or (requested_engine and engine != requested_engine):
            continue
        matches.append((name, provider, engine))
    if not matches:
        suffix = f" for engine {requested_engine}" if requested_engine else ""
        raise LightweightTtsError(f"No lightweight local TTS provider is configured{suffix}.")
    enabled = [item for item in matches if item[1].get("enabled") is True]
    candidates = enabled or matches
    if len(candidates) > 1:
        raise LightweightTtsError(
            "More than one lightweight TTS provider matches; pass --engine pocket, "
            "--engine lux, or --provider <name>."
        )
    return candidates[0]


def runtime_from(
    provider: dict[str, Any], engine: str, args: argparse.Namespace
) -> dict[str, Any]:
    runtime = provider.get("runtime")
    if not isinstance(runtime, dict):
        raise LightweightTtsError(f"{engine} provider runtime is missing.")
    resolved = dict(runtime)
    for attr, key in (
        ("python_executable", "python_executable"),
        ("repo_dir", "repo_dir"),
        ("language", "language"),
        ("device", "device"),
        ("threads", "threads"),
        ("offline", "offline"),
        ("quantize", "quantize"),
    ):
        value = getattr(args, attr, None)
        if value is not None:
            resolved[key] = value
    resolved["model"] = str(
        getattr(args, "model", None) or provider.get("model") or ""
    ).strip()
    python_value = str(resolved.get("python_executable") or "").strip()
    if not python_value:
        raise LightweightTtsError(f"{engine} runtime needs a Python executable.")
    offline = resolved.get("offline", True)
    if not isinstance(offline, bool):
        raise LightweightTtsError(f"{engine} runtime offline setting must be boolean.")
    threads = resolved.get("threads", 2)
    if not isinstance(threads, int) or isinstance(threads, bool) or threads < 1 or threads > 64:
        raise LightweightTtsError(f"{engine} runtime threads must be an integer from 1 to 64.")

    if engine == "pocket":
        language = str(resolved.get("language") or "english")
        if language not in POCKET_LANGUAGES:
            raise LightweightTtsError(
                "Unsupported Pocket TTS language pack. Choose one of: "
                + ", ".join(sorted(POCKET_LANGUAGES))
            )
        if not isinstance(resolved.get("quantize", False), bool):
            raise LightweightTtsError("Pocket TTS quantize setting must be boolean.")
    else:
        device = str(resolved.get("device") or "auto")
        if not re.fullmatch(r"(?:auto|cpu|mps|cuda(?::[0-9]+)?)", device):
            raise LightweightTtsError(f"Unsupported LuxTTS device: {device}")
        if not resolved["model"]:
            raise LightweightTtsError("LuxTTS provider needs an explicit model ID or local path.")
    return resolved


def read_text(args: argparse.Namespace) -> tuple[str, str | None]:
    if args.text_file:
        source = expand_path(args.text_file)
        if not source.is_file():
            raise LightweightTtsError(f"Text file does not exist: {source}")
        return source.read_text(encoding="utf-8-sig").strip(), str(source)
    return str(args.text or "").strip(), None


def local_reference(value: str, engine: str) -> Path:
    raw = str(value or "").strip()
    if REMOTE_REFERENCE_RE.match(raw):
        raise LightweightTtsError(
            "Speaker references must be local files; remote URLs and hf:// references are blocked."
        )
    reference = expand_path(raw)
    if not reference.is_file():
        raise LightweightTtsError(f"Speaker reference does not exist: {reference}")
    allowed = {".wav", ".mp3", ".safetensors"} if engine == "pocket" else {".wav", ".mp3"}
    if reference.suffix.lower() not in allowed:
        raise LightweightTtsError(
            f"{engine} speaker reference must use one of: {', '.join(sorted(allowed))}"
        )
    return reference


def wav_duration(path: Path) -> float | None:
    if path.suffix.lower() != ".wav":
        return None
    try:
        with wave.open(str(path), "rb") as handle:
            frame_rate = handle.getframerate()
            return handle.getnframes() / frame_rate if frame_rate else None
    except (OSError, wave.Error):
        return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_runtime(python_value: str, request: dict[str, Any]) -> dict[str, Any]:
    python = resolve_executable(python_value)
    if not python:
        raise LightweightTtsError(
            f"Configured lightweight TTS Python cannot be resolved: {python_value}"
        )
    result = subprocess.run(
        [python, "-B", str(RUNNER), "--request", "-"],
        input=json.dumps(request, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=runtime_environment_with_sox(),
    )
    if result.returncode != 0:
        detail = str(result.stderr or "").strip()
        suffix = f" Details: {detail[-1600:]}" if detail else ""
        raise LightweightTtsError(
            f"Lightweight TTS runtime failed with exit code {result.returncode}.{suffix}"
        )
    for line in reversed(str(result.stdout or "").splitlines()):
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise LightweightTtsError("Lightweight TTS runtime returned no machine-readable result.")


def provenance_path(output: Path, explicit: str | None) -> Path:
    return expand_path(explicit) if explicit else output.with_suffix(
        output.suffix + ".provenance.json"
    )


def consent_record(value: str) -> dict[str, Any]:
    raw = str(value or "").strip()
    if not raw:
        raise LightweightTtsError(
            "A non-empty --consent-record is required for voice cloning."
        )
    record: dict[str, Any] = {"reference": raw}
    candidate = Path(os.path.expandvars(os.path.expanduser(raw)))
    if candidate.is_file():
        resolved = candidate.resolve()
        record.update({"path": str(resolved), "sha256": sha256_file(resolved)})
    return record


def add_runtime_overrides(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--python-executable", help="Override the provider's isolated Python.")
    parser.add_argument("--repo-dir", help="Optional official source checkout added to sys.path.")
    parser.add_argument("--model", help="Override LuxTTS model ID or local model directory.")
    parser.add_argument("--language", help="Pocket language pack; for Lux, an audit label only.")
    parser.add_argument("--device", help="LuxTTS only: auto, cpu, mps, cuda, or cuda:<index>.")
    parser.add_argument("--threads", type=int, help="CPU thread cap; defaults to 2.")
    parser.add_argument(
        "--offline",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Keep Hugging Face/model resolution offline (default from config: true).",
    )
    parser.add_argument(
        "--quantize",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Pocket TTS only: request the installed runtime's quantized path.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CPU/low-VRAM Pocket TTS and LuxTTS adapter."
    )
    parser.add_argument("--config", help="Explicit cinematic-video .env.local path.")
    parser.add_argument("--provider", help="Exact provider slot.")
    parser.add_argument("--engine", choices=tuple(ADAPTERS), help="pocket or lux.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser(
        "doctor", help="Check configuration and optionally import the isolated runtime."
    )
    add_runtime_overrides(doctor)
    doctor.add_argument(
        "--runtime-import",
        action="store_true",
        help="Import the provider package without loading model weights.",
    )

    synthesize = subparsers.add_parser(
        "synthesize", help="Clone a consented local voice and synthesize a new WAV."
    )
    add_runtime_overrides(synthesize)
    text_group = synthesize.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--text")
    text_group.add_argument("--text-file", help="UTF-8 text file; preferred for long/private scripts.")
    synthesize.add_argument("--speaker-reference", required=True, help="Local consented voice file.")
    synthesize.add_argument("--consent-record", required=True, help="Release ID or local consent-record path.")
    synthesize.add_argument("--output", required=True, help="New .wav output path.")
    synthesize.add_argument("--provenance", help="New provenance sidecar path.")
    synthesize.add_argument("--allow-network", action="store_true")
    synthesize.add_argument(
        "--disclosure-note",
        default="AI-generated cloned speech; disclose wherever audience context requires it.",
    )
    synthesize.add_argument("--num-steps", type=int, default=4, help="LuxTTS only.")
    synthesize.add_argument("--t-shift", type=float, default=0.9, help="LuxTTS only.")
    synthesize.add_argument("--speed", type=float, default=1.0, help="LuxTTS only.")
    synthesize.add_argument(
        "--return-smooth",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="LuxTTS only; may reduce metallic sound but soften clarity.",
    )
    synthesize.add_argument(
        "--reference-duration", type=float, default=5.0, help="LuxTTS prompt seconds."
    )
    synthesize.add_argument("--rms", type=float, default=0.01, help="LuxTTS prompt RMS.")
    synthesize.add_argument("--dry-run", action="store_true")
    return parser


def command_doctor(
    provider_name: str,
    provider: dict[str, Any],
    engine: str,
    runtime: dict[str, Any],
    args: argparse.Namespace,
) -> int:
    python_value = str(runtime.get("python_executable") or "")
    python = resolve_executable(python_value)
    repo_value = str(runtime.get("repo_dir") or "").strip()
    repo = expand_path(repo_value) if repo_value else None
    issues: list[str] = []
    if not python:
        issues.append(f"Configured Python cannot be resolved: {python_value}")
    if repo is not None and not repo.is_dir():
        issues.append(f"Configured repository directory does not exist: {repo}")
    report: dict[str, Any] = {
        "ok": not issues,
        "provider": provider_name,
        "provider_enabled": provider.get("enabled") is True,
        "engine": engine,
        "adapter": provider.get("adapter"),
        "python_executable": python,
        "repository": str(repo) if repo else None,
        "model": runtime.get("model"),
        "offline": bool(runtime.get("offline", True)),
        "threads": runtime.get("threads", 2),
        "issues": issues,
    }
    if engine == "pocket":
        report.update(
            {
                "language": runtime.get("language", "english"),
                "quantize_requested": bool(runtime.get("quantize", False)),
                "official_language_packs": sorted(POCKET_LANGUAGES),
                "chinese_supported": False,
                "routing": "CPU-first; do not reroute Chinese text to Pocket TTS.",
            }
        )
    else:
        report.update(
            {
                "requested_device": runtime.get("device", "auto"),
                "language_support": "Unpublished upstream; approve a language-specific audition.",
                "sample_rate_hz": 48000,
            }
        )
    if args.runtime_import and python and not issues:
        report["runtime_import"] = run_runtime(
            python_value,
            {
                "action": "doctor_import",
                "engine": engine,
                "repo_dir": repo_value,
                "device": runtime.get("device", "auto"),
                "threads": runtime.get("threads", 2),
                "offline": bool(runtime.get("offline", True)),
            },
        )
    print(dump_json(report), end="")
    return 0 if report["ok"] else 2


def command_synthesize(
    provider_name: str,
    provider: dict[str, Any],
    engine: str,
    runtime: dict[str, Any],
    args: argparse.Namespace,
) -> int:
    text, text_source = read_text(args)
    if not text:
        raise LightweightTtsError("Synthesis text is empty.")
    reference = local_reference(args.speaker_reference, engine)
    consent = consent_record(args.consent_record)
    output = expand_path(args.output)
    sidecar = provenance_path(output, args.provenance)
    if output.suffix.lower() != ".wav":
        raise LightweightTtsError("Lightweight TTS output must use a .wav extension.")
    for path in (output, sidecar):
        if path.exists():
            raise LightweightTtsError(f"Refusing to overwrite existing file: {path}")

    offline = bool(runtime.get("offline", True))
    if not offline and not args.allow_network:
        raise LightweightTtsError(
            "Offline mode is disabled; pass --allow-network only after approving model downloads."
        )
    warnings: list[str] = []
    language = str(args.language or runtime.get("language") or "").strip()
    if engine == "pocket":
        if CJK_RE.search(text):
            raise LightweightTtsError(
                "Pocket TTS does not currently support Chinese. Use Qwen3-TTS or "
                "IndexTTS2 instead of producing a misleading fallback."
            )
        if language not in POCKET_LANGUAGES:
            raise LightweightTtsError(f"Unsupported Pocket TTS language pack: {language}")
    else:
        language = language or ("Chinese (unverified)" if CJK_RE.search(text) else "unverified")
        warnings.append(
            "LuxTTS upstream does not publish a language matrix; this take needs a "
            "language-specific listening/ASR audition before production approval."
        )
        duration = wav_duration(reference)
        if duration is not None and duration < 3.0:
            raise LightweightTtsError(
                f"LuxTTS reference WAV is {duration:.2f}s; upstream recommends at least 3 seconds."
            )
        if duration is None:
            warnings.append(
                "Reference duration could not be verified locally; confirm it is at least 3 seconds."
            )

    request: dict[str, Any] = {
        "action": "synthesize",
        "engine": engine,
        "repo_dir": runtime.get("repo_dir", ""),
        "model": runtime.get("model", ""),
        "offline": offline,
        "threads": runtime.get("threads", 2),
        "language": language,
        "quantize": bool(runtime.get("quantize", False)),
        "device": runtime.get("device", "auto"),
        "text": text,
        "speaker_reference": str(reference),
        "output_path": str(output),
        "num_steps": args.num_steps,
        "t_shift": args.t_shift,
        "speed": args.speed,
        "return_smooth": args.return_smooth,
        "reference_duration": args.reference_duration,
        "rms": args.rms,
    }
    plan = {
        "provider": provider_name,
        "provider_enabled": provider.get("enabled") is True,
        "engine": engine,
        "python_executable": resolve_executable(str(runtime.get("python_executable") or "")),
        "model": runtime.get("model"),
        "device": "cpu (Pocket TTS CPU-first)" if engine == "pocket" else runtime.get("device", "auto"),
        "offline": offline,
        "language": language,
        "output": str(output),
        "provenance": str(sidecar),
        "speaker_reference": str(reference),
        "speaker_reference_sha256": sha256_file(reference),
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "warnings": warnings,
    }
    if args.dry_run:
        print(dump_json(plan), end="")
        return 0
    if provider.get("enabled") is not True:
        raise LightweightTtsError(f"Provider {provider_name} is disabled in .env.local.")
    if not {"tts", "voice_clone"}.issubset(set(provider.get("capabilities") or [])):
        raise LightweightTtsError(
            f"Provider {provider_name} must declare both tts and voice_clone."
        )
    data_policy = provider.get("data_policy")
    if not isinstance(data_policy, dict) or data_policy.get("remote_upload") is not False:
        raise LightweightTtsError("Local lightweight TTS must declare remote_upload=false.")

    runtime_result = run_runtime(
        str(runtime.get("python_executable") or ""),
        request,
    )
    if not output.is_file() or output.stat().st_size == 0:
        raise LightweightTtsError("Runtime returned without creating a non-empty WAV.")
    record = {
        "schema_version": 1,
        "asset_type": "synthetic_voice_clone",
        "synthetic": True,
        "provider": provider_name,
        "adapter": provider.get("adapter"),
        "engine": engine,
        "model": runtime.get("model"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "language": language,
        "language_support": (
            "official Pocket TTS language pack"
            if engine == "pocket"
            else "upstream matrix unpublished; human audition required"
        ),
        "disclosure_note": args.disclosure_note,
        "consent_record": consent,
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "text_source": text_source,
        "speaker_reference": {
            "path": str(reference),
            "sha256": sha256_file(reference),
        },
        "runtime": {
            "python_executable": resolve_executable(
                str(runtime.get("python_executable") or "")
            ),
            "offline": offline,
            "requested_device": runtime.get("device", "cpu"),
            "selected_device": runtime_result.get("device"),
            "threads": runtime.get("threads", 2),
            "package_version": runtime_result.get("package_version"),
            "repository": runtime_result.get("repository"),
        },
        "generation": {
            key: request[key]
            for key in (
                "quantize",
                "num_steps",
                "t_shift",
                "speed",
                "return_smooth",
                "reference_duration",
                "rms",
            )
            if (engine == "pocket" and key == "quantize")
            or (engine == "lux" and key != "quantize")
        },
        "warnings": warnings,
        "output": {
            "path": str(output),
            "sha256": sha256_file(output),
            "sample_rate": runtime_result.get("sample_rate"),
        },
    }
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    with sidecar.open("x", encoding="utf-8") as handle:
        handle.write(dump_json(record))
    print(f"Wrote {output} and {sidecar}.")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


def main() -> int:
    args = build_parser().parse_args()
    try:
        config, _ = load_config(args.config)
        provider_name, provider, engine = find_provider(
            config, args.provider, args.engine
        )
        runtime = runtime_from(provider, engine, args)
        if args.command == "doctor":
            return command_doctor(
                provider_name, provider, engine, runtime, args
            )
        return command_synthesize(
            provider_name, provider, engine, runtime, args
        )
    except (ConfigError, LightweightTtsError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
