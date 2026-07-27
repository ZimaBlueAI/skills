#!/usr/bin/env python3
"""Safe control-plane CLI for local IndexTTS2 emotional voice cloning."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
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
from index_tts2_runner import expand_path, inspect_layout


SKILL_DIR = Path(__file__).resolve().parents[1]
RUNNER = Path(__file__).with_name("index_tts2_runner.py")
ADAPTER = "index_tts2_local"
EMOTION_NAMES = (
    "happy",
    "angry",
    "sad",
    "afraid",
    "disgusted",
    "melancholic",
    "surprised",
    "calm",
)


class IndexTts2Error(RuntimeError):
    pass


def find_provider(config: dict[str, Any], requested: str | None) -> tuple[str, dict[str, Any]]:
    providers = config.get("providers")
    if not isinstance(providers, dict):
        raise IndexTts2Error("Config providers must be an object.")
    if requested:
        provider = providers.get(requested)
        if not isinstance(provider, dict):
            raise IndexTts2Error(f"IndexTTS2 provider does not exist: {requested}")
        if provider.get("adapter") != ADAPTER:
            raise IndexTts2Error(f"Provider {requested} does not use adapter {ADAPTER}.")
        return requested, provider
    matches = [
        (name, provider)
        for name, provider in providers.items()
        if isinstance(provider, dict) and provider.get("adapter") == ADAPTER
    ]
    if not matches:
        raise IndexTts2Error(f"No provider uses adapter {ADAPTER}.")
    enabled = [item for item in matches if item[1].get("enabled") is True]
    return (enabled or matches)[0]


def runtime_from(provider: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    runtime = provider.get("runtime")
    if not isinstance(runtime, dict):
        raise IndexTts2Error("IndexTTS2 provider runtime is missing.")
    resolved = dict(runtime)
    for attr, key in (
        ("python_executable", "python_executable"),
        ("repo_dir", "repo_dir"),
        ("model_dir", "model_dir"),
        ("device", "device"),
    ):
        value = getattr(args, attr, None)
        if value:
            resolved[key] = value
    device = str(resolved.get("device") or "auto")
    if not re.fullmatch(r"(?:auto|cpu|mps|xpu|cuda(?::[0-9]+)?)", device):
        raise IndexTts2Error(f"Unsupported IndexTTS2 device: {device}")
    return resolved


def parse_vector(raw: str) -> list[float]:
    try:
        value = json.loads(raw) if raw.lstrip().startswith("[") else raw.split(",")
        vector = [float(item) for item in value]
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise argparse.ArgumentTypeError("Use 8 comma-separated numbers or a JSON array.") from exc
    if len(vector) != 8 or any(item < 0 or item > 1 for item in vector):
        raise argparse.ArgumentTypeError("Emotion vector needs 8 values between 0 and 1.")
    return vector


def read_text(args: argparse.Namespace) -> tuple[str, str | None]:
    if args.text_file:
        source = expand_path(args.text_file)
        text = source.read_text(encoding="utf-8-sig").strip()
        return text, str(source)
    return str(args.text or "").strip(), None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_emotion(args: argparse.Namespace, defaults: dict[str, Any]) -> dict[str, Any]:
    if args.emotion_reference:
        mode = "reference"
    elif args.emotion_vector is not None:
        mode = "vector"
    elif args.emotion_text:
        mode = "text"
    elif args.use_script_emotion:
        mode = "script"
    else:
        mode = "speaker"

    if args.emotion_alpha is not None:
        alpha = args.emotion_alpha
    elif mode in {"text", "script"}:
        alpha = defaults.get("text_emotion_alpha", 0.6)
    else:
        alpha = defaults.get("reference_emotion_alpha", 1.0)
    alpha = float(alpha)
    if not 0 <= alpha <= 1:
        raise IndexTts2Error("Emotion alpha must be between 0 and 1.")

    emotion: dict[str, Any] = {
        "mode": mode,
        "alpha": alpha,
        "use_random": bool(args.random or defaults.get("use_random", False)),
    }
    if mode == "reference":
        emotion["reference"] = str(expand_path(args.emotion_reference))
    elif mode == "vector":
        emotion["vector"] = args.emotion_vector
        emotion["vector_order"] = list(EMOTION_NAMES)
    elif mode == "text":
        emotion["text"] = args.emotion_text
    return emotion


def build_job(
    runtime: dict[str, Any], text: str, speaker: Path, output: Path, emotion: dict[str, Any]
) -> dict[str, Any]:
    defaults = runtime.get("defaults") if isinstance(runtime.get("defaults"), dict) else {}
    return {
        "action": "synthesize",
        "repo_dir": str(expand_path(runtime.get("repo_dir", ""))),
        "model_dir": str(expand_path(runtime.get("model_dir", ""))),
        "device": runtime.get("device", "auto"),
        "offline": bool(runtime.get("offline", True)),
        "use_fp16": bool(runtime.get("use_fp16", False)),
        "use_cuda_kernel": bool(runtime.get("use_cuda_kernel", False)),
        "use_deepspeed": bool(runtime.get("use_deepspeed", False)),
        "use_accel": bool(runtime.get("use_accel", False)),
        "use_torch_compile": bool(runtime.get("use_torch_compile", False)),
        "aux_paths": runtime.get("aux_paths"),
        "hf_cache_dir": runtime.get("hf_cache_dir"),
        "numba_cpu_name": runtime.get("numba_cpu_name"),
        "text": text,
        "speaker_reference": str(speaker),
        "output_path": str(output),
        "emotion": emotion,
        "interval_silence_ms": int(defaults.get("interval_silence_ms", 200)),
        "max_text_tokens_per_segment": int(defaults.get("max_text_tokens_per_segment", 120)),
        "verbose": bool(defaults.get("verbose", False)),
    }


def run_runtime(
    python_value: str, job: dict[str, Any], cwd: str | Path, *, capture: bool = False
) -> dict[str, Any] | None:
    python = resolve_executable(python_value)
    if not python:
        raise IndexTts2Error(f"Configured IndexTTS2 Python cannot be resolved: {python_value}")
    with tempfile.TemporaryDirectory(prefix="cine-indextts2-") as temp_name:
        request_path = Path(temp_name) / "request.json"
        result_path = Path(temp_name) / "result.json"
        runner_job = dict(job)
        runner_job["_result_path"] = str(result_path)
        request_path.write_text(json.dumps(runner_job, ensure_ascii=False), encoding="utf-8")
        environment = runtime_environment_with_sox()
        # Some official/community IndexTTS2 checkouts resolve auxiliary models through
        # INDEXTTS_MODEL_DIR and a cwd-relative HF_HUB_CACHE; export absolute paths so
        # resolution never depends on the caller's working directory.
        model_dir = str(job.get("model_dir") or "")
        repo_dir = str(job.get("repo_dir") or "")
        if model_dir:
            environment.setdefault("INDEXTTS_MODEL_DIR", model_dir)
        hf_cache = str(job.get("hf_cache_dir") or "")
        if not hf_cache:
            for candidate in (
                Path(model_dir) / "hf_cache" if model_dir else None,
                Path(repo_dir) / "checkpoints" / "hf_cache" if repo_dir else None,
            ):
                if candidate is not None and candidate.is_dir():
                    hf_cache = str(candidate)
                    break
        if hf_cache:
            environment.setdefault("HF_HUB_CACHE", hf_cache)
        if job.get("offline"):
            environment.setdefault("HF_HUB_OFFLINE", "1")
            environment.setdefault("TRANSFORMERS_OFFLINE", "1")
        # Windows numba/LLVM SVML crash guard (LLVM ERROR: __svml_cosf8_ha).
        # A fresh cache is important: an old .nbc object can retain an SVML
        # symbol even after NUMBA_DISABLE_INTEL_SVML changes.
        numba_cache = Path(temp_name) / "numba-cache"
        numba_cache.mkdir(parents=True, exist_ok=True)
        environment["NUMBA_CACHE_DIR"] = str(numba_cache)
        environment["NUMBA_DISABLE_INTEL_SVML"] = "1"
        numba_cpu = str(job.get("numba_cpu_name") or "")
        if numba_cpu:
            environment["NUMBA_CPU_NAME"] = numba_cpu
            if numba_cpu.casefold() == "generic":
                environment["NUMBA_CPU_FEATURES"] = ""
        run_options: dict[str, Any] = {
            "cwd": str(expand_path(cwd)),
            "check": False,
            "env": environment,
        }
        if capture:
            run_options.update(
                {
                    "capture_output": True,
                    "text": True,
                    "encoding": "utf-8",
                    "errors": "replace",
                }
            )
        result = subprocess.run(
            [python, "-B", str(RUNNER), "--request", str(request_path)],
            **run_options,
        )
        runtime_result = (
            json.loads(result_path.read_text(encoding="utf-8")) if result_path.is_file() else None
        )
    if result.returncode != 0:
        detail = str(getattr(result, "stderr", "") or "").strip()
        suffix = f" Details: {detail[-1000:]}" if detail else ""
        raise IndexTts2Error(f"IndexTTS2 runtime failed with exit code {result.returncode}.{suffix}")
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
    raise IndexTts2Error("IndexTTS2 runtime returned no machine-readable result.")


def provenance_path(output: Path, explicit: str | None) -> Path:
    return expand_path(explicit) if explicit else output.with_suffix(output.suffix + ".provenance.json")


def write_provenance(
    path: Path,
    *,
    provider_name: str,
    provider: dict[str, Any],
    runtime: dict[str, Any],
    args: argparse.Namespace,
    text: str,
    text_source: str | None,
    speaker: Path,
    output: Path,
    emotion: dict[str, Any],
    runtime_result: dict[str, Any],
) -> None:
    record = {
        "schema_version": 1,
        "asset_type": "synthetic_voice_clone",
        "synthetic": True,
        "provider": provider_name,
        "adapter": ADAPTER,
        "model": provider.get("model", "IndexTTS-2"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "consent_record": args.consent_record,
        "disclosure_note": args.disclosure_note,
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "text_source": text_source,
        "speaker_reference": {"path": str(speaker), "sha256": sha256_file(speaker)},
        "emotion": emotion,
        "runtime": {
            "repo_dir": str(expand_path(runtime["repo_dir"])),
            "model_dir": str(expand_path(runtime["model_dir"])),
            "requested_device": runtime.get("device", "auto"),
            "device": runtime_result.get("device", runtime.get("device", "auto")),
            "device_argument_passed": runtime_result.get("device_argument_passed"),
            "offline": bool(runtime.get("offline", True)),
            "gpu_first_auto": runtime.get("device", "auto") == "auto",
            "use_fp16": runtime_result.get("use_fp16", bool(runtime.get("use_fp16", False))),
        },
        "output": {"path": str(output), "sha256": sha256_file(output)},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(dump_json(record))


def add_runtime_overrides(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--python-executable", help="Override provider runtime Python.")
    parser.add_argument("--repo-dir", help="Override IndexTTS2 repository directory.")
    parser.add_argument("--model-dir", help="Override IndexTTS2 model directory.")
    parser.add_argument("--device", help="auto, cpu, mps, xpu, cuda, or cuda:<index>.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local IndexTTS2 emotional voice-clone adapter.")
    parser.add_argument("--config", help="Explicit cinematic-video user config.")
    parser.add_argument("--provider", help="Provider slot name; auto-selects index_tts2_local.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check configuration and local model layout without loading weights.")
    add_runtime_overrides(doctor)
    doctor.add_argument("--runtime-import", action="store_true", help="Also import IndexTTS2 in its configured Python.")

    synth = subparsers.add_parser("synthesize", help="Generate a new WAV without overwriting existing files.")
    add_runtime_overrides(synth)
    text_group = synth.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--text")
    text_group.add_argument("--text-file", help="UTF-8 script file; preferred for private or long text.")
    synth.add_argument("--speaker-reference", required=True, help="Consented timbre reference audio.")
    synth.add_argument("--output", required=True, help="New .wav output path.")
    synth.add_argument("--consent-record", required=True, help="Stable consent/release record ID or local path.")
    synth.add_argument("--disclosure-note", default="AI-generated voice clone; disclose to the intended audience.")
    emotion_group = synth.add_mutually_exclusive_group()
    emotion_group.add_argument("--emotion-reference", help="Separate emotional-style reference audio.")
    emotion_group.add_argument("--emotion-vector", type=parse_vector, help="8 values: happy, angry, sad, afraid, disgusted, melancholic, surprised, calm.")
    emotion_group.add_argument("--emotion-text", help="Natural-language emotional direction.")
    emotion_group.add_argument("--use-script-emotion", action="store_true", help="Infer emotion from the synthesis text.")
    synth.add_argument("--emotion-alpha", type=float)
    synth.add_argument("--random", action="store_true", help="Enable emotion sampling; may reduce clone fidelity.")
    synth.add_argument(
        "--allow-network",
        action="store_true",
        help="Explicitly allow the configured runtime to fetch missing auxiliary models when offline=false.",
    )
    synth.add_argument("--provenance", help="New provenance sidecar path.")
    synth.add_argument("--dry-run", action="store_true", help="Validate and print a redacted plan without loading the model.")
    return parser


def command_doctor(
    provider_name: str, provider: dict[str, Any], runtime: dict[str, Any], args: argparse.Namespace
) -> int:
    report = inspect_layout(runtime.get("repo_dir", ""), runtime.get("model_dir", ""))
    report["provider"] = provider_name
    report["enabled"] = provider.get("enabled") is True
    report["python_executable"] = resolve_executable(str(runtime.get("python_executable", "")))
    if not report["python_executable"]:
        report["issues"].append("Configured IndexTTS2 Python cannot be resolved.")
        report["ok"] = False
    if args.runtime_import and report["ok"]:
        job = {
            "action": "doctor_import",
            "repo_dir": report["repo_dir"],
            "device": runtime.get("device", "auto"),
        }
        runtime_result = run_runtime(
            str(runtime["python_executable"]), job, report["repo_dir"], capture=True
        )
        report["runtime_import"] = runtime_result
    print(dump_json(report), end="")
    return 0 if report["ok"] else 2


def command_synthesize(
    provider_name: str, provider: dict[str, Any], runtime: dict[str, Any], args: argparse.Namespace
) -> int:
    text, text_source = read_text(args)
    if not text:
        raise IndexTts2Error("Synthesis text is empty.")
    speaker = expand_path(args.speaker_reference)
    output = expand_path(args.output)
    sidecar = provenance_path(output, args.provenance)
    if not speaker.is_file():
        raise IndexTts2Error(f"Speaker reference audio does not exist: {speaker}")
    if args.emotion_reference and not expand_path(args.emotion_reference).is_file():
        raise IndexTts2Error(f"Emotion reference audio does not exist: {expand_path(args.emotion_reference)}")
    if output.suffix.lower() != ".wav":
        raise IndexTts2Error("IndexTTS2 output must use a .wav extension.")
    for path in (output, sidecar):
        if path.exists():
            raise IndexTts2Error(f"Refusing to overwrite existing file: {path}")
    defaults = runtime.get("defaults") if isinstance(runtime.get("defaults"), dict) else {}
    emotion = build_emotion(args, defaults)
    job = build_job(runtime, text, speaker, output, emotion)
    plan = {
        "provider": provider_name,
        "provider_enabled": provider.get("enabled") is True,
        "runtime_python": resolve_executable(str(runtime.get("python_executable", ""))),
        "repo_dir": job["repo_dir"],
        "model_dir": job["model_dir"],
        "device": job["device"],
        "offline": job["offline"],
        "speaker_reference": str(speaker),
        "output": str(output),
        "provenance": str(sidecar),
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "emotion": emotion,
    }
    if args.dry_run:
        print(dump_json(plan), end="")
        return 0
    if provider.get("enabled") is not True:
        raise IndexTts2Error(f"Provider {provider_name} is disabled in the user config.")
    capabilities = provider.get("capabilities")
    if not isinstance(capabilities, list) or not {"tts", "voice_clone"}.issubset(set(capabilities)):
        raise IndexTts2Error(
            f"Provider {provider_name} must declare both tts and voice_clone capabilities."
        )
    data_policy = provider.get("data_policy")
    if not isinstance(data_policy, dict) or data_policy.get("remote_upload") is not False:
        raise IndexTts2Error("The local IndexTTS2 provider must declare remote_upload=false.")
    if not str(args.consent_record).strip():
        raise IndexTts2Error("A non-empty consent record is required.")
    if not bool(runtime.get("offline", True)) and not args.allow_network:
        raise IndexTts2Error(
            "runtime.offline is false. Pass --allow-network only after approving auxiliary-model downloads."
        )
    layout = inspect_layout(job["repo_dir"], job["model_dir"])
    if not layout["ok"]:
        raise IndexTts2Error("IndexTTS2 layout check failed: " + " | ".join(layout["issues"]))
    runtime_result = run_runtime(str(runtime["python_executable"]), job, job["repo_dir"])
    if not isinstance(runtime_result, dict):
        raise IndexTts2Error("IndexTTS2 runtime returned no result record.")
    write_provenance(
        sidecar,
        provider_name=provider_name,
        provider=provider,
        runtime=runtime,
        args=args,
        text=text,
        text_source=text_source,
        speaker=speaker,
        output=output,
        emotion=emotion,
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
    except (ConfigError, IndexTts2Error, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
