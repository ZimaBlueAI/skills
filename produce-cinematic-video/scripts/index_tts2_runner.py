#!/usr/bin/env python3
"""Runtime-side IndexTTS2 adapter.

This file is launched with the Python interpreter configured for IndexTTS2.
It imports the heavy model stack lazily so the skill's control plane remains
usable without torch or the IndexTTS2 dependencies installed.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Any


MAIN_MODEL_FILES = (
    "config.yaml",
    "gpt.pth",
    "s2mel.pth",
    "bpe.model",
    "wav2vec2bert_stats.pt",
    "feat1.pt",
    "feat2.pt",
)
AUX_KEYS = ("w2v_bert", "semantic_codec", "campplus", "bigvgan")


class IndexTts2RuntimeError(RuntimeError):
    pass


def expand_path(value: str | Path) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(str(value)))).resolve()


def resolve_repo_root(value: str | Path) -> Path:
    candidate = expand_path(value)
    if (candidate / "indextts" / "infer_v2.py").is_file():
        return candidate
    if candidate.name == "indextts" and (candidate / "infer_v2.py").is_file():
        return candidate.parent
    raise IndexTts2RuntimeError(
        f"IndexTTS2 repo_dir must contain indextts/infer_v2.py: {candidate}"
    )


def resolve_model_dir(value: str | Path) -> Path:
    candidate = expand_path(value)
    direct_ok = all((candidate / name).is_file() for name in MAIN_MODEL_FILES)
    nested = candidate / "checkpoints"
    nested_ok = all((nested / name).is_file() for name in MAIN_MODEL_FILES)
    if direct_ok:
        return candidate
    if nested_ok:
        return nested
    missing = [name for name in MAIN_MODEL_FILES if not (candidate / name).is_file()]
    raise IndexTts2RuntimeError(
        "IndexTTS2 model_dir is incomplete; missing from "
        f"{candidate}: {', '.join(missing)}"
    )


def _complete_aux(candidate: dict[str, Path]) -> dict[str, str] | None:
    checks = {
        "w2v_bert": candidate["w2v_bert"].is_dir(),
        "semantic_codec": candidate["semantic_codec"].is_file(),
        "campplus": candidate["campplus"].is_file(),
        "bigvgan": candidate["bigvgan"].is_dir()
        and (candidate["bigvgan"] / "config.json").is_file()
        and (candidate["bigvgan"] / "bigvgan_generator.pt").is_file(),
    }
    if not all(checks.values()):
        return None
    return {key: str(candidate[key]) for key in AUX_KEYS}


def discover_aux_paths(
    model_dir: Path, explicit: dict[str, str] | None = None
) -> dict[str, str] | None:
    if explicit:
        if set(explicit) - set(AUX_KEYS):
            unknown = ", ".join(sorted(set(explicit) - set(AUX_KEYS)))
            raise IndexTts2RuntimeError(f"Unknown IndexTTS2 aux_paths keys: {unknown}")
        if set(explicit) != set(AUX_KEYS):
            missing = ", ".join(sorted(set(AUX_KEYS) - set(explicit)))
            raise IndexTts2RuntimeError(f"IndexTTS2 aux_paths is missing: {missing}")
        resolved = {key: expand_path(explicit[key]) for key in AUX_KEYS}
        complete = _complete_aux(resolved)
        if complete is None:
            raise IndexTts2RuntimeError("Configured IndexTTS2 aux_paths are incomplete.")
        return complete

    modern = {
        "w2v_bert": model_dir / "hf_cache" / "w2v-bert-2.0",
        "semantic_codec": model_dir / "hf_cache" / "semantic_codec_model.safetensors",
        "campplus": model_dir / "hf_cache" / "campplus_cn_common.bin",
        "bigvgan": model_dir / "hf_cache" / "bigvgan",
    }
    complete = _complete_aux(modern)
    if complete:
        return complete

    legacy = {
        "w2v_bert": model_dir / "w2v-bert-2.0",
        "semantic_codec": model_dir / "MaskGCT" / "semantic_codec" / "model.safetensors",
        "campplus": model_dir / "campplus" / "campplus_cn_common.bin",
        "bigvgan": model_dir / "bigvgan_v2_22khz_80band_256x",
    }
    return _complete_aux(legacy)


def inspect_layout(repo_dir: str | Path, model_dir: str | Path) -> dict[str, Any]:
    report: dict[str, Any] = {"ok": False, "issues": []}
    try:
        repo = resolve_repo_root(repo_dir)
        report["repo_dir"] = str(repo)
    except IndexTts2RuntimeError as exc:
        report["issues"].append(str(exc))
        repo = None
    try:
        model = resolve_model_dir(model_dir)
        report["model_dir"] = str(model)
        aux = discover_aux_paths(model)
        report["aux_layout"] = "complete" if aux else "not detected"
        if not (model / "qwen0.6bemo4-merge").is_dir():
            report["issues"].append(
                f"Text-emotion model directory is missing: {model / 'qwen0.6bemo4-merge'}"
            )
        if aux is None:
            report["issues"].append(
                "Auxiliary models were not found in the official hf_cache or legacy layout."
            )
    except IndexTts2RuntimeError as exc:
        report["issues"].append(str(exc))
        model = None
    report["ok"] = repo is not None and model is not None and not report["issues"]
    return report


def configure_offline_environment(offline: bool) -> None:
    if offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def import_torch():
    try:
        import torch
    except Exception as exc:
        raise IndexTts2RuntimeError(f"Unable to import torch in the IndexTTS2 runtime: {exc}") from exc
    return torch


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
            raise IndexTts2RuntimeError(
                "CUDA was requested, but this IndexTTS2 Python reports no available CUDA device."
            )
        index = int(requested.split(":", 1)[1]) if ":" in requested else 0
        if index >= report["cuda_device_count"]:
            raise IndexTts2RuntimeError(
                f"CUDA device {index} was requested, but only {report['cuda_device_count']} device(s) are visible."
            )
        return f"cuda:{index}"
    if requested == "xpu":
        if not report["xpu_available"]:
            raise IndexTts2RuntimeError(
                "XPU was requested, but this IndexTTS2 Python reports no available XPU device."
            )
        return "xpu"
    if requested == "mps":
        if not report["mps_available"]:
            raise IndexTts2RuntimeError(
                "MPS was requested, but this IndexTTS2 Python reports no available Apple Metal device."
            )
        return "mps"
    if requested == "cpu":
        return "cpu"
    raise IndexTts2RuntimeError(f"Unsupported IndexTTS2 device: {requested}")


def import_model_class(repo_dir: Path):
    repo_text = str(repo_dir)
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)
    importlib.invalidate_caches()
    try:
        module = importlib.import_module("indextts.infer_v2")
        return getattr(module, "IndexTTS2")
    except Exception as exc:
        raise IndexTts2RuntimeError(
            "Unable to import indextts.infer_v2.IndexTTS2 with the configured "
            f"runtime: {exc}"
        ) from exc


def _supported_kwargs(callable_obj: Any, values: dict[str, Any]) -> dict[str, Any]:
    parameters = inspect.signature(callable_obj).parameters
    accepts_extra = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in parameters.values()
    )
    return values if accepts_extra else {key: value for key, value in values.items() if key in parameters}


def build_model(model_class: Any, request: dict[str, Any], model_dir: Path):
    torch = import_torch()
    device = resolve_device(torch, str(request.get("device") or "auto"))
    use_fp16 = bool(request.get("use_fp16"))
    if use_fp16 and device == "cpu":
        raise IndexTts2RuntimeError("IndexTTS2 FP16 cannot be enabled on CPU.")
    values: dict[str, Any] = {
        "cfg_path": str(model_dir / "config.yaml"),
        "model_dir": str(model_dir),
        "device": device,
        "use_fp16": use_fp16,
        "use_cuda_kernel": bool(request.get("use_cuda_kernel")),
        "use_deepspeed": bool(request.get("use_deepspeed")),
        "use_accel": bool(request.get("use_accel")),
        "use_torch_compile": bool(request.get("use_torch_compile")),
    }
    constructor_parameters = inspect.signature(model_class).parameters
    if "aux_paths" in constructor_parameters:
        aux_paths = discover_aux_paths(model_dir, request.get("aux_paths"))
        if bool(request.get("offline")) and aux_paths is None:
            raise IndexTts2RuntimeError(
                "Offline mode is enabled, but a complete auxiliary-model layout was not found."
            )
        if aux_paths:
            values["aux_paths"] = aux_paths
    constructor_values = _supported_kwargs(model_class, values)
    return model_class(**constructor_values), device, "device" in constructor_values


def validate_emotion(emotion: dict[str, Any]) -> None:
    mode = emotion.get("mode", "speaker")
    if mode not in {"speaker", "reference", "vector", "text", "script"}:
        raise IndexTts2RuntimeError(f"Unsupported emotion mode: {mode}")
    alpha = emotion.get("alpha")
    if not isinstance(alpha, (int, float)) or isinstance(alpha, bool) or not 0 <= alpha <= 1:
        raise IndexTts2RuntimeError("emotion.alpha must be between 0 and 1.")
    if mode == "reference" and not Path(str(emotion.get("reference") or "")).is_file():
        raise IndexTts2RuntimeError("Emotion reference audio does not exist.")
    if mode == "vector":
        vector = emotion.get("vector")
        if not isinstance(vector, list) or len(vector) != 8:
            raise IndexTts2RuntimeError("Emotion vector must contain exactly 8 numbers.")
        if any(
            not isinstance(item, (int, float)) or isinstance(item, bool) or not 0 <= item <= 1
            for item in vector
        ):
            raise IndexTts2RuntimeError("Every emotion-vector value must be between 0 and 1.")
    if mode == "text" and not str(emotion.get("text") or "").strip():
        raise IndexTts2RuntimeError("Text emotion mode requires an emotion description.")


def run_synthesis(request: dict[str, Any]) -> dict[str, Any]:
    repo_dir = resolve_repo_root(request.get("repo_dir", ""))
    model_dir = resolve_model_dir(request.get("model_dir", ""))
    speaker = expand_path(request.get("speaker_reference", ""))
    output = expand_path(request.get("output_path", ""))
    text = str(request.get("text") or "").strip()
    emotion = request.get("emotion") or {"mode": "speaker", "alpha": 1.0}

    if not speaker.is_file():
        raise IndexTts2RuntimeError(f"Speaker reference audio does not exist: {speaker}")
    if not text:
        raise IndexTts2RuntimeError("Synthesis text is empty.")
    if output.suffix.lower() != ".wav":
        raise IndexTts2RuntimeError("IndexTTS2 output must use a .wav extension.")
    if output.exists():
        raise IndexTts2RuntimeError(f"Refusing to overwrite existing output: {output}")
    validate_emotion(emotion)

    configure_offline_environment(bool(request.get("offline")))
    model_class = import_model_class(repo_dir)
    model, device, device_argument_passed = build_model(model_class, request, model_dir)
    output.parent.mkdir(parents=True, exist_ok=True)

    infer_values: dict[str, Any] = {
        "spk_audio_prompt": str(speaker),
        "text": text,
        "output_path": str(output),
        "emo_alpha": float(emotion["alpha"]),
        "use_random": bool(emotion.get("use_random")),
        "interval_silence": int(request.get("interval_silence_ms", 200)),
        "max_text_tokens_per_segment": int(request.get("max_text_tokens_per_segment", 120)),
        "verbose": bool(request.get("verbose")),
    }
    mode = emotion.get("mode", "speaker")
    if mode == "reference":
        infer_values["emo_audio_prompt"] = str(expand_path(emotion["reference"]))
    elif mode == "vector":
        infer_values["emo_vector"] = [float(item) for item in emotion["vector"]]
    elif mode in {"text", "script"}:
        infer_values["use_emo_text"] = True
        if mode == "text":
            infer_values["emo_text"] = str(emotion["text"])

    model.infer(**_supported_kwargs(model.infer, infer_values))
    if not output.is_file() or output.stat().st_size == 0:
        raise IndexTts2RuntimeError("IndexTTS2 returned without creating a non-empty WAV output.")
    return {
        "ok": True,
        "output_path": str(output),
        "bytes": output.stat().st_size,
        "device": device,
        "device_argument_passed": device_argument_passed,
        "use_fp16": bool(request.get("use_fp16")),
    }


def run_request(request: dict[str, Any]) -> dict[str, Any]:
    action = request.get("action")
    if action == "doctor_import":
        repo = resolve_repo_root(request.get("repo_dir", ""))
        torch = import_torch()
        model_class = import_model_class(repo)
        requested_device = str(request.get("device") or "auto")
        selected_device = resolve_device(torch, requested_device)
        return {
            "ok": True,
            "class": f"{model_class.__module__}.{model_class.__name__}",
            "constructor": str(inspect.signature(model_class)),
            "torch_version": getattr(torch, "__version__", "unknown"),
            "requested_device": requested_device,
            "selected_device": selected_device,
            "accelerators": accelerator_report(torch),
        }
    if action == "synthesize":
        return run_synthesis(request)
    raise IndexTts2RuntimeError(f"Unsupported runner action: {action}")


def main() -> int:
    parser = argparse.ArgumentParser(description="IndexTTS2 isolated runtime runner.")
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
