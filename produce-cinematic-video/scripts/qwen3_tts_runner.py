#!/usr/bin/env python3
"""Isolated runtime runner for local Qwen3-TTS models."""

from __future__ import annotations

import argparse
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Any


class Qwen3TtsRuntimeError(RuntimeError):
    pass


def expand_path(value: str | Path) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(str(value)))).resolve()


def inspect_model(value: str | Path, expected_kind: str) -> dict[str, Any]:
    raw = str(value or "").strip()
    report: dict[str, Any] = {
        "configured": bool(raw),
        "expected_kind": expected_kind,
        "value": raw,
        "local": False,
        "ok": False,
        "issues": [],
    }
    if not raw:
        return report
    candidate = expand_path(raw)
    if not candidate.is_dir():
        report["model_id"] = raw
        report["issues"].append("Model is not a local directory; network permission is required to resolve an ID.")
        return report
    report["local"] = True
    report["path"] = str(candidate)
    if not (candidate / "config.json").is_file():
        report["issues"].append("Missing config.json.")
    weight_patterns = ("*.safetensors", "*.bin", "*.pt", "*.pth")
    has_weight = any(any(candidate.glob(pattern)) for pattern in weight_patterns)
    has_weight_index = any(
        (candidate / name).is_file()
        for name in ("model.safetensors.index.json", "pytorch_model.bin.index.json")
    )
    if not has_weight and not has_weight_index:
        report["issues"].append("No model weights or weight index detected.")
    report["ok"] = not report["issues"]
    return report


def inspect_models(runtime: dict[str, Any]) -> dict[str, Any]:
    models = {
        "voice_design": inspect_model(runtime.get("voice_design_model", ""), "voice_design"),
        "custom_voice": inspect_model(runtime.get("custom_voice_model", ""), "custom_voice"),
        "voice_clone": inspect_model(runtime.get("base_model", ""), "base"),
    }
    configured = [name for name, report in models.items() if report["configured"]]
    return {
        "ok": bool(configured) and all(models[name]["ok"] for name in configured),
        "configured_modes": configured,
        "models": models,
    }


def configure_offline_environment(offline: bool) -> None:
    if offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def import_runtime():
    try:
        import soundfile as sf
        import torch
        from qwen_tts import Qwen3TTSModel
    except Exception as exc:
        raise Qwen3TtsRuntimeError(f"Unable to import qwen_tts runtime: {exc}") from exc
    return Qwen3TTSModel, torch, sf


def accelerator_report(torch: Any) -> dict[str, Any]:
    cuda_available = bool(getattr(torch.cuda, "is_available", lambda: False)())
    cuda_count = int(getattr(torch.cuda, "device_count", lambda: 0)()) if cuda_available else 0
    cuda_names: list[str] = []
    if cuda_available:
        for index in range(cuda_count):
            try:
                cuda_names.append(str(torch.cuda.get_device_name(index)))
            except Exception:
                cuda_names.append(f"cuda:{index}")

    xpu = getattr(torch, "xpu", None)
    xpu_available = bool(xpu is not None and getattr(xpu, "is_available", lambda: False)())
    xpu_count = int(getattr(xpu, "device_count", lambda: 0)()) if xpu_available else 0
    mps = getattr(getattr(torch, "backends", None), "mps", None)
    mps_available = bool(mps is not None and getattr(mps, "is_available", lambda: False)())
    return {
        "gpu_first": True,
        "cuda_available": cuda_available,
        "cuda_device_count": cuda_count,
        "cuda_device_names": cuda_names,
        "xpu_available": xpu_available,
        "xpu_device_count": xpu_count,
        "mps_available": mps_available,
    }


def resolve_device(torch: Any, requested: str) -> str:
    report = accelerator_report(torch)
    if requested == "auto":
        if report["cuda_available"]:
            return "cuda:0"
        if report["xpu_available"]:
            return "xpu"
        if report["mps_available"]:
            return "mps"
        return "cpu"

    if requested.startswith("cuda"):
        if not report["cuda_available"]:
            raise Qwen3TtsRuntimeError(
                "CUDA was requested, but this Qwen3-TTS Python reports no available CUDA device."
            )
        index = int(requested.split(":", 1)[1]) if ":" in requested else 0
        if index >= report["cuda_device_count"]:
            raise Qwen3TtsRuntimeError(
                f"CUDA device {index} was requested, but only {report['cuda_device_count']} device(s) are visible."
            )
        return f"cuda:{index}"
    if requested == "xpu":
        if not report["xpu_available"]:
            raise Qwen3TtsRuntimeError(
                "XPU was requested, but this Qwen3-TTS Python reports no available XPU device."
            )
        return "xpu"
    if requested == "mps":
        if not report["mps_available"]:
            raise Qwen3TtsRuntimeError(
                "MPS was requested, but this Qwen3-TTS Python reports no available Apple Metal device."
            )
        return "mps"
    if requested == "cpu":
        return "cpu"
    raise Qwen3TtsRuntimeError(f"Unsupported Qwen3-TTS device: {requested}")


def _cuda_supports_bfloat16(torch: Any) -> bool:
    checker = getattr(torch.cuda, "is_bf16_supported", None)
    if checker is None:
        return False
    try:
        return bool(checker())
    except Exception:
        return False


def resolve_dtype(torch: Any, requested: str, device: str):
    if requested == "auto":
        if device.startswith("cuda"):
            return torch.bfloat16 if _cuda_supports_bfloat16(torch) else torch.float16
        if device == "xpu":
            return torch.bfloat16
        if device == "mps":
            return torch.float16
        return torch.float32
    dtype = {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }[requested]
    if device == "cpu" and requested != "float32":
        raise Qwen3TtsRuntimeError(
            "CPU Qwen3-TTS requires float32 in this adapter; use dtype=auto or float32."
        )
    return dtype


def resolve_model(value: str, offline: bool) -> str:
    raw = str(value or "").strip()
    if not raw:
        raise Qwen3TtsRuntimeError("The selected Qwen3-TTS model is not configured.")
    candidate = expand_path(raw)
    if candidate.is_dir():
        return str(candidate)
    if offline:
        raise Qwen3TtsRuntimeError(
            "Offline mode requires a local model directory; model IDs cannot be resolved."
        )
    return raw


def load_model(request: dict[str, Any]):
    model_class, torch, sf = import_runtime()
    offline = bool(request.get("offline", True))
    configure_offline_environment(offline)
    device = resolve_device(torch, str(request.get("device") or "auto"))
    dtype = resolve_dtype(torch, str(request.get("dtype") or "auto"), device)
    model_source = resolve_model(str(request.get("model") or ""), offline)
    kwargs: dict[str, Any] = {"device_map": device, "dtype": dtype}
    attention = str(request.get("attn_implementation") or "auto")
    if attention != "auto":
        if attention == "flash_attention_2" and not device.startswith("cuda"):
            raise Qwen3TtsRuntimeError("flash_attention_2 requires a compatible CUDA runtime.")
        kwargs["attn_implementation"] = attention
    model = model_class.from_pretrained(model_source, **kwargs)
    return model, sf, device, str(dtype), model_source


def generation_kwargs(request: dict[str, Any]) -> dict[str, Any]:
    values: dict[str, Any] = {
        "do_sample": bool(request.get("do_sample", True)),
        "max_new_tokens": int(request.get("max_new_tokens", 2048)),
    }
    for key in ("temperature", "top_p", "top_k", "repetition_penalty"):
        if request.get(key) is not None:
            values[key] = request[key]
    return values


def run_synthesis(request: dict[str, Any]) -> dict[str, Any]:
    mode = str(request.get("mode") or "")
    if mode not in {"voice_design", "custom_voice", "voice_clone"}:
        raise Qwen3TtsRuntimeError(f"Unsupported Qwen3-TTS mode: {mode}")
    text = str(request.get("text") or "").strip()
    output = expand_path(request.get("output_path", ""))
    if not text:
        raise Qwen3TtsRuntimeError("Synthesis text is empty.")
    if output.suffix.lower() != ".wav":
        raise Qwen3TtsRuntimeError("Qwen3-TTS output must use a .wav extension.")
    if output.exists():
        raise Qwen3TtsRuntimeError(f"Refusing to overwrite existing output: {output}")

    model, sf, device, dtype, model_source = load_model(request)
    language = str(request.get("language") or "Auto")
    kwargs = generation_kwargs(request)
    if mode == "voice_design":
        instruction = str(request.get("instruction") or "").strip()
        if not instruction:
            raise Qwen3TtsRuntimeError("Voice design requires a non-empty instruction.")
        wavs, sample_rate = model.generate_voice_design(
            text=text, language=language, instruct=instruction, **kwargs
        )
    elif mode == "custom_voice":
        speaker = str(request.get("speaker") or "").strip()
        if not speaker:
            raise Qwen3TtsRuntimeError("Custom voice requires a speaker name.")
        instruction = str(request.get("instruction") or "").strip() or None
        wavs, sample_rate = model.generate_custom_voice(
            text=text, language=language, speaker=speaker, instruct=instruction, **kwargs
        )
    else:
        reference_audio = expand_path(request.get("reference_audio", ""))
        if not reference_audio.is_file():
            raise Qwen3TtsRuntimeError(f"Reference audio does not exist: {reference_audio}")
        x_vector_only = bool(request.get("x_vector_only"))
        reference_text = str(request.get("reference_text") or "").strip() or None
        if not x_vector_only and not reference_text:
            raise Qwen3TtsRuntimeError(
                "Voice clone requires reference_text unless x_vector_only is enabled."
            )
        wavs, sample_rate = model.generate_voice_clone(
            text=text,
            language=language,
            ref_audio=str(reference_audio),
            ref_text=reference_text,
            x_vector_only_mode=x_vector_only,
            **kwargs,
        )

    if not wavs:
        raise Qwen3TtsRuntimeError("Qwen3-TTS returned no waveform.")
    output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output), wavs[0], int(sample_rate))
    if not output.is_file() or output.stat().st_size == 0:
        raise Qwen3TtsRuntimeError("Qwen3-TTS returned without creating a non-empty WAV output.")
    return {
        "ok": True,
        "mode": mode,
        "output_path": str(output),
        "bytes": output.stat().st_size,
        "sample_rate": int(sample_rate),
        "device": device,
        "dtype": dtype,
        "model": model_source,
    }


def run_request(request: dict[str, Any]) -> dict[str, Any]:
    action = request.get("action")
    if action == "doctor_import":
        model_class, torch, sf = import_runtime()
        requested_device = str(request.get("device") or "auto")
        requested_dtype = str(request.get("dtype") or "auto")
        selected_device = resolve_device(torch, requested_device)
        selected_dtype = resolve_dtype(torch, requested_dtype, selected_device)
        return {
            "ok": True,
            "class": f"{model_class.__module__}.{model_class.__name__}",
            "from_pretrained": str(inspect.signature(model_class.from_pretrained)),
            "torch_version": getattr(torch, "__version__", "unknown"),
            "soundfile_version": getattr(sf, "__version__", "unknown"),
            "requested_device": requested_device,
            "selected_device": selected_device,
            "requested_dtype": requested_dtype,
            "selected_dtype": str(selected_dtype),
            "accelerators": accelerator_report(torch),
        }
    if action == "synthesize":
        return run_synthesis(request)
    raise Qwen3TtsRuntimeError(f"Unsupported runner action: {action}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Qwen3-TTS isolated runtime runner.")
    parser.add_argument("--request", required=True, help="UTF-8 JSON request file.")
    args = parser.parse_args()
    try:
        request = json.loads(Path(args.request).read_text(encoding="utf-8"))
        result = run_request(request)
        result_path = str(request.get("_result_path") or "").strip()
        if result_path:
            Path(result_path).write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
