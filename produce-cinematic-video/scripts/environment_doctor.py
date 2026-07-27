#!/usr/bin/env python3
"""Read-only dependency and media-tool diagnostics for the skill."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from cinematic_config import ConfigError, load_config, resolve_executable, resolve_sox


FFMPEG_FILTERS = {
    "scale",
    "tile",
    "blackdetect",
    "freezedetect",
    "silencedetect",
    "ebur128",
}


def result(name: str, status: str, detail: str, required: bool) -> dict[str, Any]:
    return {"name": name, "status": status, "required": required, "detail": detail}


def run_version(executable: str, *args: str) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            [executable, *args],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
            timeout=20,
        )
        output = (completed.stdout or completed.stderr).strip()
        return completed.returncode, output
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 2, str(exc)


def tool_check(name: str, configured: str, args: tuple[str, ...], required: bool) -> dict[str, Any]:
    executable = resolve_executable(configured)
    if not executable:
        return result(name, "missing", f"Cannot resolve '{configured}'.", required)
    code, output = run_version(executable, *args)
    first_line = output.splitlines()[0] if output else "No version output."
    return result(name, "ok" if code == 0 else "error", f"{executable}: {first_line}", required)


def ffmpeg_check(configured: str) -> list[dict[str, Any]]:
    checks = [tool_check("ffmpeg", configured, ("-version",), True)]
    executable = resolve_executable(configured)
    if not executable:
        return checks
    code, output = run_version(executable, "-hide_banner", "-filters")
    if code != 0:
        checks.append(result("ffmpeg_filters", "error", output[:500], True))
        return checks
    missing = sorted(name for name in FFMPEG_FILTERS if name not in output)
    if missing:
        checks.append(
            result(
                "ffmpeg_filters",
                "error",
                "Missing filters required by contact-sheet/QC workflows: " + ", ".join(missing),
                True,
            )
        )
    else:
        checks.append(result("ffmpeg_filters", "ok", "Required scale/tile/QC filters are present.", True))
    return checks


def module_check(import_name: str, package_name: str, required: bool) -> dict[str, Any]:
    try:
        spec = importlib.util.find_spec(import_name)
    except (ImportError, AttributeError, ValueError) as exc:
        return result(package_name, "error", str(exc), required)
    if spec is None:
        return result(package_name, "missing", f"Python import '{import_name}' is unavailable.", required)
    return result(package_name, "ok", f"Python import '{import_name}' is available.", required)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check cinematic-video tools without modifying the system.")
    parser.add_argument("--config", help="Explicit user config path.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-imagemagick", action="store_true")
    parser.add_argument("--require-vision", action="store_true", help="Require Pillow and OpenCV.")
    parser.add_argument(
        "--require-av-sync",
        action="store_true",
        help="Require OpenCV and NumPy for mouth-motion A/V alignment.",
    )
    parser.add_argument("--require-scenedetect", action="store_true")
    parser.add_argument("--require-schema", action="store_true", help="Require jsonschema.")
    parser.add_argument("--require-sox", action="store_true", help="Require the SoX audio utility.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        config, config_path = load_config(args.config)
        tools = config.get("tools", {})
        checks: list[dict[str, Any]] = []
        python_ok = sys.version_info >= (3, 10)
        checks.append(
            result(
                "python_version",
                "ok" if python_ok else "error",
                f"{sys.executable}: Python {sys.version.split()[0]}",
                True,
            )
        )
        checks.extend(ffmpeg_check(str(tools.get("ffmpeg", "ffmpeg"))))
        checks.append(tool_check("ffprobe", str(tools.get("ffprobe", "ffprobe")), ("-version",), True))

        imagemagick = str(tools.get("imagemagick", "") or "magick")
        checks.append(tool_check("imagemagick", imagemagick, ("-version",), args.require_imagemagick))
        checks.append(tool_check("sox", resolve_sox() or "sox", ("--version",), args.require_sox))
        checks.append(module_check("jsonschema", "jsonschema", args.require_schema))
        checks.append(module_check("PIL", "Pillow", args.require_vision))
        checks.append(module_check("cv2", "opencv-python", args.require_vision or args.require_av_sync))
        checks.append(module_check("numpy", "NumPy", args.require_av_sync))
        checks.append(module_check("scenedetect", "PySceneDetect", args.require_scenedetect))

        failed = [item for item in checks if item["required"] and item["status"] != "ok"]
        report = {
            "ok": not failed,
            "config": str(config_path),
            "checks": checks,
            "optional_requirements": str(Path(__file__).resolve().parents[1] / "requirements-optional.txt"),
        }
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            for item in checks:
                marker = "OK" if item["status"] == "ok" else ("ERROR" if item["required"] else "OPTIONAL")
                print(f"[{marker}] {item['name']}: {item['detail']}")
            print("Environment is ready." if report["ok"] else "Environment has required failures.")
        return 0 if report["ok"] else 2
    except (ConfigError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
