#!/usr/bin/env python3
"""Isolated runtime runner for Pocket TTS and LuxTTS."""

from __future__ import annotations

import argparse
import importlib.metadata
import inspect
import json
import os
import struct
import sys
import wave
from pathlib import Path
from typing import Any, Callable


class LightweightTtsRuntimeError(RuntimeError):
    """Raised when an isolated lightweight TTS runtime cannot complete."""


def expand_path(value: str | Path) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(str(value)))).resolve()


def configure_offline_environment(offline: bool) -> None:
    if offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def configure_cpu_threads(value: Any) -> int:
    threads = int(value or 2)
    if threads < 1 or threads > 64:
        raise LightweightTtsRuntimeError("CPU threads must be from 1 to 64.")
    os.environ["OMP_NUM_THREADS"] = str(threads)
    os.environ["MKL_NUM_THREADS"] = str(threads)
    os.environ["OPENBLAS_NUM_THREADS"] = str(threads)
    return threads


def add_repo_to_path(value: str | None) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    repo = expand_path(raw)
    if not repo.is_dir():
        raise LightweightTtsRuntimeError(f"Configured repository directory does not exist: {repo}")
    sys.path.insert(0, str(repo))
    return str(repo)


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def signature_text(callable_value: Callable[..., Any]) -> str:
    try:
        return str(inspect.signature(callable_value))
    except (TypeError, ValueError):
        return "<signature unavailable>"


def supported_kwargs(
    callable_value: Callable[..., Any],
    values: dict[str, Any],
    *,
    required_when_truthy: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Keep supported keyword arguments and reject silently-lost material options."""
    try:
        signature = inspect.signature(callable_value)
    except (TypeError, ValueError):
        return values
    accepts_any = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    )
    if accepts_any:
        return values
    supported = {
        key: value for key, value in values.items() if key in signature.parameters
    }
    missing_material = [
        key
        for key in required_when_truthy
        if values.get(key) and key not in signature.parameters
    ]
    if missing_material:
        raise LightweightTtsRuntimeError(
            "Installed runtime does not support requested option(s): "
            + ", ".join(missing_material)
        )
    return supported


def accelerator_report(torch: Any | None) -> dict[str, Any]:
    if torch is None:
        return {
            "torch_available": False,
            "cuda_available": False,
            "cuda_device_count": 0,
            "cuda_device_names": [],
            "mps_available": False,
        }
    cuda = getattr(torch, "cuda", None)
    cuda_available = bool(
        cuda is not None and getattr(cuda, "is_available", lambda: False)()
    )
    cuda_count = (
        int(getattr(cuda, "device_count", lambda: 0)()) if cuda_available else 0
    )
    cuda_names: list[str] = []
    for index in range(cuda_count):
        try:
            cuda_names.append(str(cuda.get_device_name(index)))
        except Exception:
            cuda_names.append(f"cuda:{index}")
    mps = getattr(getattr(torch, "backends", None), "mps", None)
    mps_available = bool(
        mps is not None and getattr(mps, "is_available", lambda: False)()
    )
    return {
        "torch_available": True,
        "torch_version": getattr(torch, "__version__", "unknown"),
        "cuda_available": cuda_available,
        "cuda_device_count": cuda_count,
        "cuda_device_names": cuda_names,
        "mps_available": mps_available,
    }


def resolve_lux_device(torch: Any | None, requested: str) -> tuple[str, dict[str, Any]]:
    report = accelerator_report(torch)
    if requested == "auto":
        if report["cuda_available"]:
            return "cuda", report
        if report["mps_available"]:
            return "mps", report
        return "cpu", report
    if requested.startswith("cuda"):
        if not report["cuda_available"]:
            raise LightweightTtsRuntimeError(
                "CUDA was requested, but this LuxTTS Python reports no available CUDA device."
            )
        if ":" in requested:
            index = int(requested.split(":", 1)[1])
            if index >= report["cuda_device_count"]:
                raise LightweightTtsRuntimeError(
                    f"CUDA device {index} was requested, but only "
                    f"{report['cuda_device_count']} device(s) are visible."
                )
        return requested, report
    if requested == "mps":
        if not report["mps_available"]:
            raise LightweightTtsRuntimeError(
                "MPS was requested, but this LuxTTS Python reports no available Apple Metal device."
            )
        return "mps", report
    if requested == "cpu":
        return "cpu", report
    raise LightweightTtsRuntimeError(f"Unsupported LuxTTS device: {requested}")


def import_pocket(repo_dir: str | None = None):
    repo = add_repo_to_path(repo_dir)
    try:
        from pocket_tts import TTSModel
    except Exception as exc:
        raise LightweightTtsRuntimeError(
            "Unable to import pocket_tts. Install pocket-tts in the configured "
            f"Python environment. Original error: {exc}"
        ) from exc
    return TTSModel, repo


def import_lux(repo_dir: str | None = None):
    repo = add_repo_to_path(repo_dir)
    try:
        from zipvoice.luxvoice import LuxTTS
    except Exception as exc:
        raise LightweightTtsRuntimeError(
            "Unable to import zipvoice.luxvoice.LuxTTS. Install the official "
            f"LuxTTS repository in the configured Python environment. Original error: {exc}"
        ) from exc
    try:
        import torch
    except Exception:
        torch = None
    return LuxTTS, torch, repo


def _flatten_waveform(value: Any) -> list[float]:
    current = value
    for method in ("detach", "float", "cpu"):
        candidate = getattr(current, method, None)
        if callable(candidate):
            current = candidate()
    reshape = getattr(current, "reshape", None)
    if callable(reshape):
        try:
            current = reshape(-1)
        except Exception:
            pass
    tolist = getattr(current, "tolist", None)
    if callable(tolist):
        current = tolist()
    elif hasattr(current, "numpy"):
        current = current.numpy()
        if hasattr(current, "reshape"):
            current = current.reshape(-1)
        if hasattr(current, "tolist"):
            current = current.tolist()

    flattened: list[float] = []

    def visit(item: Any) -> None:
        if isinstance(item, (list, tuple)):
            for child in item:
                visit(child)
            return
        try:
            flattened.append(float(item))
        except (TypeError, ValueError) as exc:
            raise LightweightTtsRuntimeError(
                f"Runtime returned a non-numeric waveform item: {type(item).__name__}"
            ) from exc

    visit(current)
    if not flattened:
        raise LightweightTtsRuntimeError("Runtime returned an empty waveform.")
    return flattened


def write_pcm16_wave(output: Path, waveform: Any, sample_rate: int) -> None:
    if sample_rate < 8000:
        raise LightweightTtsRuntimeError(f"Invalid output sample rate: {sample_rate}")
    if output.exists():
        raise LightweightTtsRuntimeError(f"Refusing to overwrite existing output: {output}")
    samples = _flatten_waveform(waveform)
    pcm = bytearray()
    for value in samples:
        clipped = max(-1.0, min(1.0, value))
        integer = int(round(clipped * 32767.0))
        pcm.extend(struct.pack("<h", integer))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as handle:
        with wave.open(handle, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(bytes(pcm))


def doctor_pocket(request: dict[str, Any]) -> dict[str, Any]:
    configure_offline_environment(bool(request.get("offline", True)))
    threads = configure_cpu_threads(request.get("threads", 2))
    model_class, repo = import_pocket(request.get("repo_dir"))
    load_signature = inspect.signature(model_class.load_model)
    quantize_supported = "quantize" in load_signature.parameters or any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in load_signature.parameters.values()
    )
    return {
        "ok": True,
        "engine": "pocket",
        "class": f"{model_class.__module__}.{model_class.__name__}",
        "repository": repo,
        "package_version": package_version("pocket-tts"),
        "load_model": str(load_signature),
        "get_state_for_audio_prompt": signature_text(
            model_class.get_state_for_audio_prompt
        ),
        "generate_audio": signature_text(model_class.generate_audio),
        "quantize_supported": quantize_supported,
        "selected_device": "cpu",
        "threads": threads,
        "routing_note": (
            "Pocket TTS is intentionally CPU-first; upstream reports no speedup "
            "from its current batch-1 GPU path."
        ),
    }


def doctor_lux(request: dict[str, Any]) -> dict[str, Any]:
    configure_offline_environment(bool(request.get("offline", True)))
    configure_cpu_threads(request.get("threads", 2))
    model_class, torch, repo = import_lux(request.get("repo_dir"))
    requested_device = str(request.get("device") or "auto")
    selected_device, accelerators = resolve_lux_device(torch, requested_device)
    return {
        "ok": True,
        "engine": "lux",
        "class": f"{model_class.__module__}.{model_class.__name__}",
        "repository": repo,
        "package_version": package_version("luxtts"),
        "constructor": signature_text(model_class),
        "encode_prompt": signature_text(model_class.encode_prompt),
        "generate_speech": signature_text(model_class.generate_speech),
        "requested_device": requested_device,
        "selected_device": selected_device,
        "accelerators": accelerators,
        "language_support": (
            "Upstream does not publish a language matrix; run and approve a "
            "language-specific audition before production use."
        ),
    }


def synthesize_pocket(request: dict[str, Any]) -> dict[str, Any]:
    offline = bool(request.get("offline", True))
    configure_offline_environment(offline)
    threads = configure_cpu_threads(request.get("threads", 2))
    model_class, repo = import_pocket(request.get("repo_dir"))
    language = str(request.get("language") or "english")
    quantize = bool(request.get("quantize", False))
    load_kwargs = supported_kwargs(
        model_class.load_model,
        {"language": language, "quantize": quantize},
        required_when_truthy=("quantize",),
    )
    model = model_class.load_model(**load_kwargs)
    reference = expand_path(request.get("speaker_reference", ""))
    state = model.get_state_for_audio_prompt(str(reference))
    audio = model.generate_audio(state, str(request.get("text") or ""))
    sample_rate = int(getattr(model, "sample_rate", 24000))
    output = expand_path(request.get("output_path", ""))
    write_pcm16_wave(output, audio, sample_rate)
    return {
        "ok": True,
        "engine": "pocket",
        "output_path": str(output),
        "bytes": output.stat().st_size,
        "sample_rate": sample_rate,
        "device": str(getattr(model, "device", "cpu")),
        "language": language,
        "quantized": quantize,
        "threads": threads,
        "repository": repo,
        "package_version": package_version("pocket-tts"),
    }


def synthesize_lux(request: dict[str, Any]) -> dict[str, Any]:
    offline = bool(request.get("offline", True))
    configure_offline_environment(offline)
    threads = configure_cpu_threads(request.get("threads", 2))
    model_class, torch, repo = import_lux(request.get("repo_dir"))
    requested_device = str(request.get("device") or "auto")
    selected_device, accelerators = resolve_lux_device(torch, requested_device)
    model_value = str(request.get("model") or "").strip()
    if not model_value:
        raise LightweightTtsRuntimeError("LuxTTS model is not configured.")
    model_path = expand_path(model_value)
    model_source = str(model_path) if model_path.is_dir() else model_value
    constructor_kwargs: dict[str, Any] = {"device": selected_device}
    if selected_device == "cpu":
        constructor_kwargs["threads"] = threads
    constructor_kwargs = supported_kwargs(model_class, constructor_kwargs)
    model = model_class(model_source, **constructor_kwargs)

    reference = expand_path(request.get("speaker_reference", ""))
    encode_kwargs = supported_kwargs(
        model.encode_prompt,
        {
            "duration": float(request.get("reference_duration", 5.0)),
            "rms": float(request.get("rms", 0.01)),
        },
    )
    encoded_prompt = model.encode_prompt(str(reference), **encode_kwargs)
    generation_kwargs = supported_kwargs(
        model.generate_speech,
        {
            "num_steps": int(request.get("num_steps", 4)),
            "t_shift": float(request.get("t_shift", 0.9)),
            "speed": float(request.get("speed", 1.0)),
            "return_smooth": bool(request.get("return_smooth", False)),
        },
    )
    audio = model.generate_speech(
        str(request.get("text") or ""), encoded_prompt, **generation_kwargs
    )
    output = expand_path(request.get("output_path", ""))
    write_pcm16_wave(output, audio, 48000)
    return {
        "ok": True,
        "engine": "lux",
        "output_path": str(output),
        "bytes": output.stat().st_size,
        "sample_rate": 48000,
        "requested_device": requested_device,
        "device": selected_device,
        "accelerators": accelerators,
        "model": model_source,
        "repository": repo,
        "package_version": package_version("luxtts"),
    }


def run_request(request: dict[str, Any]) -> dict[str, Any]:
    action = str(request.get("action") or "")
    engine = str(request.get("engine") or "")
    if action == "doctor_import":
        if engine == "pocket":
            return doctor_pocket(request)
        if engine == "lux":
            return doctor_lux(request)
    if action == "synthesize":
        if engine == "pocket":
            return synthesize_pocket(request)
        if engine == "lux":
            return synthesize_lux(request)
    raise LightweightTtsRuntimeError(
        f"Unsupported lightweight TTS request: action={action!r}, engine={engine!r}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pocket TTS / LuxTTS isolated runtime runner."
    )
    parser.add_argument(
        "--request",
        default="-",
        help="UTF-8 JSON request file, or '-' to read the request from standard input.",
    )
    args = parser.parse_args()
    try:
        if args.request == "-":
            request = json.load(sys.stdin)
        else:
            request = json.loads(
                Path(args.request).read_text(encoding="utf-8")
            )
        result = run_request(request)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
