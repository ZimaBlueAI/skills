#!/usr/bin/env python3
"""Runtime-side UVR5 bridge executed with the GPT-SoVITS Python environment."""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path


def write_result(request, payload):
    result_path = Path(request["_result_path"])
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def add_repo_paths(repo):
    repo = repo.resolve()
    uvr = repo / "tools" / "uvr5"
    for path in (str(repo), str(uvr)):
        if path not in sys.path:
            sys.path.insert(0, path)
    os.chdir(str(repo))
    return uvr


def select_device(torch, requested):
    if requested != "auto":
        if requested.startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but torch.cuda.is_available() is false.")
        if requested == "mps":
            backend = getattr(torch.backends, "mps", None)
            if backend is None or not backend.is_available():
                raise RuntimeError("MPS was requested but is unavailable.")
        return requested
    if torch.cuda.is_available():
        return "cuda"
    backend = getattr(torch.backends, "mps", None)
    if backend is not None and backend.is_available():
        return "mps"
    return "cpu"


def doctor_import(request):
    repo = Path(request["repo_dir"])
    uvr = add_repo_paths(repo)
    import librosa  # noqa: F401
    import soundfile  # noqa: F401
    import torch

    from bsroformer import Roformer_Loader  # noqa: F401
    from mdxnet import MDXNetDereverb  # noqa: F401
    from vr import AudioPre, AudioPreDeEcho  # noqa: F401

    device = select_device(torch, str(request.get("device") or "auto"))
    return {
        "ok": True,
        "python": sys.executable,
        "python_version": sys.version.split()[0],
        "torch_version": getattr(torch, "__version__", "unknown"),
        "cuda_available": bool(torch.cuda.is_available()),
        "device": device,
        "uvr_dir": str(uvr),
    }


def model_instance(request, device, is_half):
    repo = Path(request["repo_dir"])
    weight_root = repo / "tools" / "uvr5" / "uvr5_weights"
    model_name = str(request["model"])
    model_path = Path(model_name)
    if not model_path.is_absolute():
        candidates = [
            weight_root / model_name,
            weight_root / (model_name + ".pth"),
            weight_root / (model_name + ".ckpt"),
        ]
        model_path = next((item for item in candidates if item.exists()), candidates[0])

    if model_name == "onnx_dereverb_By_FoxJoy" or model_path.name == "onnx_dereverb_By_FoxJoy":
        from mdxnet import MDXNetDereverb

        return MDXNetDereverb(15), "onnx_dereverb_By_FoxJoy", False

    normalized = model_path.stem
    if "roformer" in normalized.lower():
        from bsroformer import Roformer_Loader

        config_path = model_path.with_suffix(".yaml")
        instance = Roformer_Loader(
            model_path=str(model_path),
            config_path=str(config_path),
            device=device,
            is_half=is_half,
        )
        return instance, str(model_path), False

    from vr import AudioPre, AudioPreDeEcho

    klass = AudioPreDeEcho if "DeEcho" in normalized else AudioPre
    instance = klass(
        agg=int(request.get("agg", 10)),
        model_path=str(model_path),
        device=device,
        is_half=is_half,
    )
    return instance, str(model_path), "HP3" in normalized


def separate(request):
    repo = Path(request["repo_dir"])
    add_repo_paths(repo)
    import torch

    source = Path(request["input_wav"])
    output_dir = Path(request["output_dir"])
    vocals = output_dir / "vocals"
    other = output_dir / "other"
    vocals.mkdir(parents=True, exist_ok=False)
    other.mkdir(parents=True, exist_ok=False)

    device = select_device(torch, str(request.get("device") or "auto"))
    is_half = device.startswith("cuda") and bool(request.get("use_half", True))
    pre_fun, model_path, is_hp3 = model_instance(request, device, is_half)
    try:
        pre_fun._path_audio_(
            str(source),
            str(other),
            str(vocals),
            str(request.get("format") or "wav"),
            is_hp3,
        )
    finally:
        try:
            del pre_fun
        except Exception:
            pass
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    outputs = sorted(
        str(path)
        for path in output_dir.rglob("*")
        if path.is_file()
    )
    if not outputs:
        raise RuntimeError("UVR5 returned without creating any stem files.")
    return {
        "ok": True,
        "device": device,
        "is_half": is_half,
        "model_path": model_path,
        "outputs": outputs,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    try:
        action = request.get("action")
        if action == "doctor_import":
            result = doctor_import(request)
        elif action == "separate":
            result = separate(request)
        else:
            raise RuntimeError("Unknown UVR5 runtime action: %s" % action)
        write_result(request, result)
        return 0
    except Exception as exc:
        write_result(
            request,
            {
                "ok": False,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            },
        )
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
