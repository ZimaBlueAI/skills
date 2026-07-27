#!/usr/bin/env python3
"""Safe local adapter for GPT-SoVITS UVR5 source separation and dereverb."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cinematic_config import ConfigError, dump_json, load_config, resolve_executable


ADAPTER = "gpt_sovits_uvr5_local"
RUNNER = Path(__file__).with_name("gpt_sovits_uvr5_runner.py")


class Uvr5Error(RuntimeError):
    pass


def expand_path(value: str | Path) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(str(value)))).resolve()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_provider(config: dict[str, Any], requested: str | None) -> tuple[str, dict[str, Any]]:
    providers = config.get("providers")
    if not isinstance(providers, dict):
        raise Uvr5Error("Config providers must be an object.")
    matches = [
        (name, provider)
        for name, provider in providers.items()
        if isinstance(provider, dict) and provider.get("adapter") == ADAPTER
    ]
    if requested:
        matches = [item for item in matches if item[0] == requested]
    if not matches:
        raise Uvr5Error(f"No provider uses adapter {ADAPTER}.")
    enabled = [item for item in matches if item[1].get("enabled") is True]
    return (enabled or matches)[0]


def runtime_from(provider: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    runtime = provider.get("runtime")
    if not isinstance(runtime, dict):
        raise Uvr5Error("GPT-SoVITS UVR5 runtime is missing.")
    resolved = dict(runtime)
    if getattr(args, "repo_dir", None):
        resolved["repo_dir"] = args.repo_dir
    if getattr(args, "python_executable", None):
        resolved["python_executable"] = args.python_executable
    if getattr(args, "device", None):
        resolved["device"] = args.device
    repo = expand_path(str(resolved.get("repo_dir") or "."))
    python_value = str(resolved.get("python_executable") or "").strip()
    bundled_python = repo / "runtime" / ("python.exe" if os.name == "nt" else "bin/python")
    if not python_value:
        python_value = str(bundled_python) if bundled_python.is_file() else sys.executable
    resolved["repo_dir"] = str(repo)
    resolved["python_executable"] = python_value
    resolved.setdefault("device", "auto")
    return resolved


def list_models(repo: Path) -> list[dict[str, Any]]:
    root = repo / "tools" / "uvr5" / "uvr5_weights"
    if not root.is_dir():
        return []
    models: list[dict[str, Any]] = []
    for path in sorted(root.iterdir(), key=lambda item: item.name.lower()):
        if path.suffix.lower() in {".pth", ".ckpt"}:
            models.append(
                {
                    "name": path.stem,
                    "path": str(path),
                    "kind": "roformer" if "roformer" in path.stem.lower() else "uvr5",
                    "config": str(path.with_suffix(".yaml")) if path.with_suffix(".yaml").is_file() else None,
                }
            )
        elif path.is_dir() and path.name == "onnx_dereverb_By_FoxJoy":
            models.append({"name": path.name, "path": str(path), "kind": "dereverb", "config": None})
    return models


def runtime_env(repo: Path, scratch: Path) -> dict[str, str]:
    env = os.environ.copy()
    additions = [str(repo), str(repo / "runtime")]
    current = env.get("PATH", "")
    env["PATH"] = os.pathsep.join(additions + ([current] if current else []))
    scratch.mkdir(parents=True, exist_ok=True)
    # Old portable GPT-SoVITS bundles may try to create Numba caches beside
    # read-only site-packages. Keep all transient compilation in our scratch
    # directory instead. This does not disable CUDA for Torch/UVR5.
    numba_cache = scratch / "numba"
    numba_cache.mkdir(parents=True, exist_ok=True)
    env["NUMBA_CACHE_DIR"] = str(numba_cache)
    env.setdefault("NUMBA_CPU_NAME", "generic")
    env["TEMP"] = str(scratch)
    env["TMP"] = str(scratch)
    env["TMPDIR"] = str(scratch)
    return env


def run_runtime(runtime: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    python = resolve_executable(str(runtime["python_executable"]))
    if not python:
        raise Uvr5Error(f"Configured GPT-SoVITS Python cannot be resolved: {runtime['python_executable']}")
    repo = expand_path(runtime["repo_dir"])
    with tempfile.TemporaryDirectory(prefix="pcv-uvr5-") as temp_name:
        scratch = Path(temp_name) / "runtime-cache"
        request_path = Path(temp_name) / "request.json"
        result_path = Path(temp_name) / "result.json"
        payload = dict(request)
        payload["_result_path"] = str(result_path)
        request_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        result = subprocess.run(
            [python, "-B", str(RUNNER), "--request", str(request_path)],
            cwd=str(repo),
            env=runtime_env(repo, scratch),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        response = json.loads(result_path.read_text(encoding="utf-8")) if result_path.is_file() else {}
    if result.returncode != 0 or response.get("ok") is not True:
        detail = str(response.get("error") or result.stderr or "unknown runtime error")
        raise Uvr5Error(detail)
    return response


def doctor_report(provider_name: str, provider: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    repo = expand_path(runtime["repo_dir"])
    python = resolve_executable(str(runtime["python_executable"]))
    required = {
        "repo": repo.is_dir(),
        "runtime_python": bool(python),
        "uvr_webui": (repo / "tools" / "uvr5" / "webui.py").is_file(),
        "weights_dir": (repo / "tools" / "uvr5" / "uvr5_weights").is_dir(),
        "runner": RUNNER.is_file(),
    }
    models = list_models(repo)
    return {
        "ok": all(required.values()) and bool(models),
        "provider": provider_name,
        "enabled": provider.get("enabled") is True,
        "adapter": ADAPTER,
        "repo_dir": str(repo),
        "python_executable": python,
        "requested_device": runtime.get("device", "auto"),
        "checks": required,
        "models": models,
    }


def choose_ffmpeg(config: dict[str, Any], repo: Path) -> str:
    tools = config.get("tools") if isinstance(config.get("tools"), dict) else {}
    configured = str(tools.get("ffmpeg") or "ffmpeg")
    executable = resolve_executable(configured)
    if executable:
        return executable
    bundled = repo / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    if bundled.is_file():
        return str(bundled)
    raise Uvr5Error("FFmpeg cannot be resolved from user config or the GPT-SoVITS repository.")


def prepare_input(ffmpeg: str, source: Path, destination: Path) -> None:
    result = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ac",
            "2",
            "-ar",
            "44100",
            "-y",
            str(destination),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        raise Uvr5Error("FFmpeg input preparation failed: " + (result.stderr or "")[-1000:])


def write_provenance(
    output_dir: Path,
    *,
    provider_name: str,
    source: Path,
    model: str,
    model_path: str,
    args: argparse.Namespace,
    runtime_result: dict[str, Any],
) -> Path:
    outputs = [Path(path) for path in runtime_result.get("outputs", [])]
    record = {
        "schema_version": 1,
        "asset_type": "derived_audio_stems",
        "source": {"path": str(source), "sha256": sha256_file(source)},
        "provider": provider_name,
        "adapter": ADAPTER,
        "model": model,
        "model_path": model_path,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "agg": args.agg,
            "format": args.format,
            "requested_device": args.device,
        },
        "runtime": {
            "device": runtime_result.get("device"),
            "is_half": runtime_result.get("is_half"),
            "offline": True,
        },
        "outputs": [
            {"path": str(path), "sha256": sha256_file(path)}
            for path in outputs
            if path.is_file()
        ],
        "review_required": True,
        "limitations": "Estimated stems may contain bleed, phase changes, dereverb artifacts, or transient loss.",
    }
    path = output_dir / "separation.provenance.json"
    with path.open("x", encoding="utf-8") as handle:
        handle.write(dump_json(record))
    return path


def add_runtime_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo-dir")
    parser.add_argument("--python-executable")
    parser.add_argument("--device", choices=("auto", "cpu", "mps", "cuda"), default=None)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local GPT-SoVITS UVR5 adapter.")
    parser.add_argument("--config", help="Explicit cinematic-video .env.local path.")
    parser.add_argument("--provider")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor")
    add_runtime_args(doctor)
    doctor.add_argument("--runtime-import", action="store_true")

    models = sub.add_parser("list-models")
    add_runtime_args(models)

    separate = sub.add_parser("separate")
    add_runtime_args(separate)
    separate.add_argument("input")
    separate.add_argument("--model", required=True)
    separate.add_argument("--output-dir", required=True)
    separate.add_argument("--format", choices=("wav", "flac"), default="wav")
    separate.add_argument("--agg", type=int, default=10)
    separate.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        config, _ = load_config(args.config)
        provider_name, provider = find_provider(config, args.provider)
        runtime = runtime_from(provider, args)
        report = doctor_report(provider_name, provider, runtime)
        if args.command == "doctor":
            if args.runtime_import and report["ok"]:
                report["runtime_import"] = run_runtime(
                    runtime,
                    {
                        "action": "doctor_import",
                        "repo_dir": runtime["repo_dir"],
                        "device": runtime.get("device", "auto"),
                    },
                )
            print(dump_json(report), end="")
            return 0 if report["ok"] else 2
        if args.command == "list-models":
            print(dump_json({"provider": provider_name, "models": report["models"]}), end="")
            return 0 if report["models"] else 2

        if provider.get("enabled") is not True and not args.dry_run:
            raise Uvr5Error(f"Provider {provider_name} is disabled in .env.local.")
        if "source_separation" not in set(provider.get("capabilities") or []):
            raise Uvr5Error(f"Provider {provider_name} does not declare source_separation.")
        source = expand_path(args.input)
        if not source.is_file():
            raise Uvr5Error(f"Input does not exist: {source}")
        output_dir = expand_path(args.output_dir)
        if output_dir.exists():
            raise Uvr5Error(f"Refusing to overwrite existing output directory: {output_dir}")
        model_names = {item["name"] for item in report["models"]}
        model_path = expand_path(args.model) if Path(args.model).is_absolute() else None
        if args.model not in model_names and not (model_path and model_path.exists()):
            raise Uvr5Error(f"Model is not present in the configured UVR5 weights: {args.model}")
        plan = {
            "provider": provider_name,
            "adapter": ADAPTER,
            "input": str(source),
            "model": args.model,
            "output_dir": str(output_dir),
            "device": runtime.get("device", "auto"),
            "format": args.format,
        }
        if args.dry_run:
            print(dump_json(plan), end="")
            return 0

        repo = expand_path(runtime["repo_dir"])
        ffmpeg = choose_ffmpeg(config, repo)
        with tempfile.TemporaryDirectory(prefix="pcv-uvr5-input-") as temp_name:
            prepared = Path(temp_name) / (source.stem + ".wav")
            prepare_input(ffmpeg, source, prepared)
            response = run_runtime(
                runtime,
                {
                    "action": "separate",
                    "repo_dir": str(repo),
                    "input_wav": str(prepared),
                    "model": args.model,
                    "output_dir": str(output_dir),
                    "format": args.format,
                    "agg": args.agg,
                    "device": runtime.get("device", "auto"),
                    "use_half": True,
                },
            )
        provenance = write_provenance(
            output_dir,
            provider_name=provider_name,
            source=source,
            model=args.model,
            model_path=str(response.get("model_path") or ""),
            args=args,
            runtime_result=response,
        )
        print(f"Wrote {len(response.get('outputs', []))} stem file(s) and {provenance}.")
        return 0
    except (ConfigError, Uvr5Error, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
