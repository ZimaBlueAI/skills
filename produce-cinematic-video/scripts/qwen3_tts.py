#!/usr/bin/env python3
"""Safe control-plane CLI for local Qwen3-TTS voice design and cloning."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
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
from qwen3_tts_runner import expand_path, inspect_models


RUNNER = Path(__file__).with_name("qwen3_tts_runner.py")
ADAPTER = "qwen3_tts_local"


class Qwen3TtsError(RuntimeError):
    pass


def find_provider(config: dict[str, Any], requested: str | None) -> tuple[str, dict[str, Any]]:
    providers = config.get("providers")
    if not isinstance(providers, dict):
        raise Qwen3TtsError("Config providers must be an object.")
    if requested:
        provider = providers.get(requested)
        if not isinstance(provider, dict) or provider.get("adapter") != ADAPTER:
            raise Qwen3TtsError(f"Provider {requested} does not use adapter {ADAPTER}.")
        return requested, provider
    matches = [
        (name, provider)
        for name, provider in providers.items()
        if isinstance(provider, dict) and provider.get("adapter") == ADAPTER
    ]
    if not matches:
        raise Qwen3TtsError(f"No provider uses adapter {ADAPTER}.")
    enabled = [item for item in matches if item[1].get("enabled") is True]
    return (enabled or matches)[0]


def runtime_from(provider: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    runtime = provider.get("runtime")
    if not isinstance(runtime, dict):
        raise Qwen3TtsError("Qwen3-TTS provider runtime is missing.")
    resolved = dict(runtime)
    for attr, key in (
        ("python_executable", "python_executable"),
        ("voice_design_model", "voice_design_model"),
        ("custom_voice_model", "custom_voice_model"),
        ("base_model", "base_model"),
        ("device", "device"),
        ("dtype", "dtype"),
        ("attn_implementation", "attn_implementation"),
    ):
        value = getattr(args, attr, None)
        if value:
            resolved[key] = value
    device = str(resolved.get("device") or "auto")
    if not re.fullmatch(r"(?:auto|cpu|mps|xpu|cuda(?::[0-9]+)?)", device):
        raise Qwen3TtsError(f"Unsupported Qwen3-TTS device: {device}")
    if resolved.get("dtype", "auto") not in {"auto", "float32", "float16", "bfloat16"}:
        raise Qwen3TtsError("Qwen3-TTS dtype must be auto, float32, float16, or bfloat16.")
    if resolved.get("attn_implementation", "auto") not in {
        "auto",
        "eager",
        "sdpa",
        "flash_attention_2",
    }:
        raise Qwen3TtsError("Unsupported Qwen3-TTS attention implementation.")
    return resolved


def read_text(args: argparse.Namespace) -> tuple[str, str | None]:
    if args.text_file:
        source = expand_path(args.text_file)
        return source.read_text(encoding="utf-8-sig").strip(), str(source)
    return str(args.text or "").strip(), None


def read_optional_text(value: str | None, file_value: str | None) -> tuple[str | None, str | None]:
    if file_value:
        source = expand_path(file_value)
        return source.read_text(encoding="utf-8-sig").strip(), str(source)
    normalized = str(value or "").strip()
    return (normalized or None), None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_runtime(
    python_value: str, request: dict[str, Any], *, capture: bool = False
) -> dict[str, Any] | None:
    python = resolve_executable(python_value)
    if not python:
        raise Qwen3TtsError(f"Configured Qwen3-TTS Python cannot be resolved: {python_value}")
    with tempfile.TemporaryDirectory(prefix="cine-qwen3tts-") as temp_name:
        request_path = Path(temp_name) / "request.json"
        result_path = Path(temp_name) / "result.json"
        runner_request = dict(request)
        runner_request["_result_path"] = str(result_path)
        request_path.write_text(json.dumps(runner_request, ensure_ascii=False), encoding="utf-8")
        options: dict[str, Any] = {
            "check": False,
            "env": runtime_environment_with_sox(),
        }
        if capture:
            options.update(
                {
                    "capture_output": True,
                    "text": True,
                    "encoding": "utf-8",
                    "errors": "replace",
                }
            )
        result = subprocess.run(
            [python, "-B", str(RUNNER), "--request", str(request_path)], **options
        )
        runtime_result = (
            json.loads(result_path.read_text(encoding="utf-8")) if result_path.is_file() else None
        )
    if result.returncode != 0:
        detail = str(getattr(result, "stderr", "") or "").strip()
        suffix = f" Details: {detail[-1200:]}" if detail else ""
        raise Qwen3TtsError(f"Qwen3-TTS runtime failed with exit code {result.returncode}.{suffix}")
    if isinstance(runtime_result, dict):
        return runtime_result
    if not capture:
        return None
    for line in reversed(str(result.stdout or "").splitlines()):
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise Qwen3TtsError("Qwen3-TTS runtime returned no machine-readable result.")


def model_for_mode(runtime: dict[str, Any], mode: str) -> str:
    key = {
        "voice_design": "voice_design_model",
        "custom_voice": "custom_voice_model",
        "voice_clone": "base_model",
    }[mode]
    return str(runtime.get(key) or "").strip()


def provenance_path(output: Path, explicit: str | None) -> Path:
    return expand_path(explicit) if explicit else output.with_suffix(output.suffix + ".provenance.json")


def write_provenance(
    path: Path,
    *,
    provider_name: str,
    provider: dict[str, Any],
    runtime: dict[str, Any],
    args: argparse.Namespace,
    mode: str,
    text: str,
    text_source: str | None,
    output: Path,
    instruction: str | None,
    reference_text: str | None,
    reference_text_source: str | None,
    reference_audio: Path | None,
    runtime_result: dict[str, Any],
) -> None:
    record: dict[str, Any] = {
        "schema_version": 1,
        "asset_type": f"synthetic_{mode}",
        "synthetic": True,
        "provider": provider_name,
        "adapter": ADAPTER,
        "model": model_for_mode(runtime, mode),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "language": args.language,
        "disclosure_note": args.disclosure_note,
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "text_source": text_source,
        "instruction": instruction,
        "runtime": {
            "python_executable": resolve_executable(str(runtime.get("python_executable", ""))),
            "requested_device": runtime.get("device", "auto"),
            "device": runtime_result.get("device", runtime.get("device", "auto")),
            "requested_dtype": runtime.get("dtype", "auto"),
            "dtype": runtime_result.get("dtype", runtime.get("dtype", "auto")),
            "attn_implementation": runtime.get("attn_implementation", "auto"),
            "offline": bool(runtime.get("offline", True)),
            "gpu_first_auto": runtime.get("device", "auto") == "auto",
        },
        "output": {"path": str(output), "sha256": sha256_file(output)},
    }
    if mode == "custom_voice":
        record["speaker"] = args.speaker
    if mode == "voice_clone":
        record["consent_record"] = args.consent_record
        record["x_vector_only"] = bool(args.x_vector_only)
        record["reference_text_sha256"] = (
            hashlib.sha256(reference_text.encode("utf-8")).hexdigest() if reference_text else None
        )
        record["reference_text_source"] = reference_text_source
        if reference_audio is not None:
            record["reference_audio"] = {
                "path": str(reference_audio),
                "sha256": sha256_file(reference_audio),
            }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(dump_json(record))


def add_runtime_overrides(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--python-executable", help="Override Qwen3-TTS runtime Python.")
    parser.add_argument("--voice-design-model", help="Override local VoiceDesign model directory or model ID.")
    parser.add_argument("--custom-voice-model", help="Override local CustomVoice model directory or model ID.")
    parser.add_argument("--base-model", help="Override local Base/voice-clone model directory or model ID.")
    parser.add_argument("--device", help="auto, cpu, mps, xpu, cuda, or cuda:<index>.")
    parser.add_argument("--dtype", choices=("auto", "float32", "float16", "bfloat16"))
    parser.add_argument(
        "--attn-implementation",
        choices=("auto", "eager", "sdpa", "flash_attention_2"),
    )


def add_text_args(parser: argparse.ArgumentParser) -> None:
    text_group = parser.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--text")
    text_group.add_argument("--text-file", help="UTF-8 script file; preferred for private or long text.")
    parser.add_argument("--language", default=None, help="Chinese, English, Auto, or another supported language.")
    parser.add_argument("--output", required=True, help="New .wav output path.")
    parser.add_argument("--disclosure-note", default="AI-generated speech; disclose when audience context requires it.")
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--top-p", type=float)
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--repetition-penalty", type=float)
    parser.add_argument("--allow-network", action="store_true")
    parser.add_argument("--provenance", help="New provenance sidecar path.")
    parser.add_argument("--dry-run", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local Qwen3-TTS voice-design and voice-clone adapter.")
    parser.add_argument("--config", help="Explicit cinematic-video .env.local path.")
    parser.add_argument("--provider", help="Provider slot; auto-selects qwen3_tts_local.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check runtime and configured model directories without loading weights.")
    add_runtime_overrides(doctor)
    doctor.add_argument("--runtime-import", action="store_true", help="Import qwen_tts without loading weights.")

    design = subparsers.add_parser("design", help="Create a voice from a natural-language voice instruction.")
    add_runtime_overrides(design)
    add_text_args(design)
    design.add_argument("--instruction", required=True, help="Voice identity, delivery, emotion, and pacing direction.")

    custom = subparsers.add_parser("custom", help="Use a built-in CustomVoice speaker with an optional instruction.")
    add_runtime_overrides(custom)
    add_text_args(custom)
    custom.add_argument("--speaker", required=True)
    custom.add_argument("--instruction")

    clone = subparsers.add_parser("clone", help="Clone a consented voice with the Base model.")
    add_runtime_overrides(clone)
    add_text_args(clone)
    clone.add_argument("--reference-audio", required=True)
    reference_group = clone.add_mutually_exclusive_group()
    reference_group.add_argument("--reference-text")
    reference_group.add_argument("--reference-text-file")
    clone.add_argument("--x-vector-only", action="store_true", help="Do not require reference transcript; quality may drop.")
    clone.add_argument("--consent-record", required=True)
    return parser


def command_doctor(
    provider_name: str, provider: dict[str, Any], runtime: dict[str, Any], args: argparse.Namespace
) -> int:
    report = inspect_models(runtime)
    report["provider"] = provider_name
    report["enabled"] = provider.get("enabled") is True
    report["python_executable"] = resolve_executable(str(runtime.get("python_executable", "")))
    if not report["python_executable"]:
        report["ok"] = False
        report.setdefault("issues", []).append("Configured Qwen3-TTS Python cannot be resolved.")
    if args.runtime_import and report["python_executable"]:
        report["runtime_import"] = run_runtime(
            str(runtime["python_executable"]),
            {
                "action": "doctor_import",
                "device": runtime.get("device", "auto"),
                "dtype": runtime.get("dtype", "auto"),
            },
            capture=True,
        )
    print(dump_json(report), end="")
    return 0 if report["ok"] else 2


def command_synthesize(
    provider_name: str, provider: dict[str, Any], runtime: dict[str, Any], args: argparse.Namespace
) -> int:
    mode = {
        "design": "voice_design",
        "custom": "custom_voice",
        "clone": "voice_clone",
    }[args.command]
    text, text_source = read_text(args)
    if not text:
        raise Qwen3TtsError("Synthesis text is empty.")
    defaults = runtime.get("defaults") if isinstance(runtime.get("defaults"), dict) else {}
    args.language = args.language or str(defaults.get("language") or "Auto")
    output = expand_path(args.output)
    sidecar = provenance_path(output, args.provenance)
    if output.suffix.lower() != ".wav":
        raise Qwen3TtsError("Qwen3-TTS output must use a .wav extension.")
    for path in (output, sidecar):
        if path.exists():
            raise Qwen3TtsError(f"Refusing to overwrite existing file: {path}")

    instruction = str(getattr(args, "instruction", "") or "").strip() or None
    reference_text, reference_text_source = read_optional_text(
        getattr(args, "reference_text", None), getattr(args, "reference_text_file", None)
    )
    reference_audio: Path | None = None
    if mode == "voice_clone":
        reference_audio = expand_path(args.reference_audio)
        if not reference_audio.is_file():
            raise Qwen3TtsError(f"Reference audio does not exist: {reference_audio}")
        if not args.x_vector_only and not reference_text:
            raise Qwen3TtsError("Provide --reference-text/--reference-text-file or use --x-vector-only.")
        if not str(args.consent_record).strip():
            raise Qwen3TtsError("A non-empty consent record is required for voice cloning.")

    model_value = model_for_mode(runtime, mode)
    if not model_value:
        raise Qwen3TtsError(f"No model is configured for {mode}.")
    offline = bool(runtime.get("offline", True))
    if not offline and not args.allow_network:
        raise Qwen3TtsError("Offline mode is disabled; pass --allow-network only after approving model downloads.")
    report = inspect_models(runtime)["models"][mode]
    if offline and not report["ok"]:
        raise Qwen3TtsError("Offline model check failed: " + " | ".join(report["issues"]))

    request: dict[str, Any] = {
        "action": "synthesize",
        "mode": mode,
        "model": model_value,
        "device": runtime.get("device", "auto"),
        "dtype": runtime.get("dtype", "auto"),
        "attn_implementation": runtime.get("attn_implementation", "auto"),
        "offline": offline,
        "text": text,
        "language": args.language,
        "output_path": str(output),
        "instruction": instruction,
        "speaker": getattr(args, "speaker", None),
        "reference_audio": str(reference_audio) if reference_audio else None,
        "reference_text": reference_text,
        "x_vector_only": bool(getattr(args, "x_vector_only", False)),
        "do_sample": bool(defaults.get("do_sample", True)),
        "max_new_tokens": int(defaults.get("max_new_tokens", 2048)),
        "temperature": args.temperature,
        "top_p": args.top_p,
        "top_k": args.top_k,
        "repetition_penalty": args.repetition_penalty,
    }
    plan = {
        "provider": provider_name,
        "provider_enabled": provider.get("enabled") is True,
        "mode": mode,
        "runtime_python": resolve_executable(str(runtime.get("python_executable", ""))),
        "model": model_value,
        "device": request["device"],
        "dtype": request["dtype"],
        "offline": offline,
        "output": str(output),
        "provenance": str(sidecar),
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "instruction_sha256": hashlib.sha256(instruction.encode("utf-8")).hexdigest() if instruction else None,
        "reference_audio": str(reference_audio) if reference_audio else None,
    }
    if args.dry_run:
        print(dump_json(plan), end="")
        return 0
    if provider.get("enabled") is not True:
        raise Qwen3TtsError(f"Provider {provider_name} is disabled in .env.local.")
    required_capability = {
        "voice_design": "voice_design",
        "custom_voice": "tts",
        "voice_clone": "voice_clone",
    }[mode]
    if required_capability not in set(provider.get("capabilities") or []):
        raise Qwen3TtsError(f"Provider {provider_name} does not declare {required_capability}.")
    data_policy = provider.get("data_policy")
    if not isinstance(data_policy, dict) or data_policy.get("remote_upload") is not False:
        raise Qwen3TtsError("Local Qwen3-TTS must declare remote_upload=false.")

    runtime_result = run_runtime(str(runtime.get("python_executable", "")), request)
    if not isinstance(runtime_result, dict):
        raise Qwen3TtsError("Qwen3-TTS runtime returned no result record.")
    write_provenance(
        sidecar,
        provider_name=provider_name,
        provider=provider,
        runtime=runtime,
        args=args,
        mode=mode,
        text=text,
        text_source=text_source,
        output=output,
        instruction=instruction,
        reference_text=reference_text,
        reference_text_source=reference_text_source,
        reference_audio=reference_audio,
        runtime_result=runtime_result,
    )
    print(f"Wrote {output} and {sidecar}.")
    return 0


def main() -> int:
    args = build_parser().parse_args()
    try:
        config, _ = load_config(args.config)
        provider_name, provider = find_provider(config, args.provider)
        runtime = runtime_from(provider, args)
        if args.command == "doctor":
            return command_doctor(provider_name, provider, runtime, args)
        return command_synthesize(provider_name, provider, runtime, args)
    except (ConfigError, Qwen3TtsError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
