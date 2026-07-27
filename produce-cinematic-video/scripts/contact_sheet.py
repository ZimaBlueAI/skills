#!/usr/bin/env python3
"""Create a representative-frame contact sheet and timestamp index."""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from cinematic_config import ConfigError, load_config, resolve_tool


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def duration_of(ffprobe: str, video: Path) -> float:
    result = run(
        [
            ffprobe,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            str(video),
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[:500] or "ffprobe failed")
    try:
        duration = float(json.loads(result.stdout)["format"]["duration"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError("ffprobe did not return a usable duration") from exc
    if duration <= 0:
        raise RuntimeError("video duration must be positive")
    return duration


def scene_midpoints(path: Path) -> list[tuple[str, float]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    try:
        header_index = next(
            index
            for index, row in enumerate(rows)
            if row and row[0].strip() == "Scene Number"
        )
    except StopIteration as exc:
        raise RuntimeError("Could not find the PySceneDetect 'Scene Number' header") from exc

    header = [cell.strip() for cell in rows[header_index]]
    try:
        scene_col = header.index("Scene Number")
        start_col = header.index("Start Time (seconds)")
        end_col = header.index("End Time (seconds)")
    except ValueError as exc:
        raise RuntimeError("Scene CSV needs Start/End Time (seconds) columns") from exc

    result: list[tuple[str, float]] = []
    for row in rows[header_index + 1 :]:
        if len(row) <= max(scene_col, start_col, end_col):
            continue
        try:
            start = float(row[start_col])
            end = float(row[end_col])
        except ValueError:
            continue
        if end > start:
            result.append((f"scene-{row[scene_col].strip()}", (start + end) / 2))
    if not result:
        raise RuntimeError("No usable scenes found in the scene CSV")
    return result


def uniform_times(duration: float, count: int) -> list[tuple[str, float]]:
    if count < 1:
        raise RuntimeError("sample count must be at least 1")
    step = duration / (count + 1)
    return [(f"sample-{index + 1}", step * (index + 1)) for index in range(count)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build an ffmpeg contact sheet without modifying the source.")
    parser.add_argument("video")
    parser.add_argument("--scenes", help="PySceneDetect list-scenes CSV.")
    parser.add_argument("-n", "--count", type=int, default=20, help="Uniform sample count without --scenes.")
    parser.add_argument("-w", "--width", type=int, default=320, help="Cell width in pixels.")
    parser.add_argument("-c", "--columns", type=int, default=5)
    parser.add_argument("-o", "--output", default="contact_sheet.jpg")
    parser.add_argument("--index-output", help="Timestamp CSV path; defaults beside the image.")
    parser.add_argument("--config", help="Explicit user config path.")
    parser.add_argument("--ffmpeg", help="Explicit ffmpeg executable.")
    parser.add_argument("--ffprobe", help="Explicit ffprobe executable.")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    video = Path(args.video)
    output = Path(args.output)
    index_output = Path(args.index_output) if args.index_output else output.with_suffix(".index.csv")

    if not video.is_file():
        print(f"ERROR: Video not found: {video}", file=sys.stderr)
        return 2
    if args.width < 32 or args.columns < 1 or args.count < 1:
        print("ERROR: width, columns, and count must be positive.", file=sys.stderr)
        return 2
    existing = [path for path in (output, index_output) if path.exists()]
    if existing and not args.overwrite:
        print(
            "ERROR: Output exists: " + ", ".join(str(path) for path in existing) + ". Pass --overwrite.",
            file=sys.stderr,
        )
        return 2

    try:
        if args.ffmpeg or args.ffprobe:
            config: dict[str, Any] = {
                "tools": {
                    "ffmpeg": args.ffmpeg or "ffmpeg",
                    "ffprobe": args.ffprobe or "ffprobe",
                }
            }
        else:
            config, _ = load_config(args.config)
        ffmpeg = resolve_tool(config, "ffmpeg", args.ffmpeg)
        ffprobe = resolve_tool(config, "ffprobe", args.ffprobe)
        samples = (
            scene_midpoints(Path(args.scenes))
            if args.scenes
            else uniform_times(duration_of(ffprobe, video), args.count)
        )
    except (ConfigError, OSError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    columns = min(args.columns, len(samples))
    rows = math.ceil(len(samples) / columns)
    output.parent.mkdir(parents=True, exist_ok=True)
    index_output.parent.mkdir(parents=True, exist_ok=True)

    try:
        with tempfile.TemporaryDirectory(prefix="cine-contact-") as temp_name:
            temp = Path(temp_name)
            for index, (_, timestamp) in enumerate(samples):
                frame = temp / f"frame{index:04d}.jpg"
                result = run(
                    [
                        ffmpeg,
                        "-hide_banner",
                        "-loglevel",
                        "error",
                        "-y",
                        "-ss",
                        f"{timestamp:.6f}",
                        "-i",
                        str(video),
                        "-frames:v",
                        "1",
                        "-vf",
                        f"scale={args.width}:-2",
                        str(frame),
                    ]
                )
                if result.returncode != 0 or not frame.exists():
                    raise RuntimeError(
                        f"Frame extraction failed at {timestamp:.3f}s: {result.stderr.strip()[:500]}"
                    )

            result = run(
                [
                    ffmpeg,
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-framerate",
                    "1",
                    "-i",
                    str(temp / "frame%04d.jpg"),
                    "-vf",
                    f"tile={columns}x{rows}:padding=4:margin=4:color=black",
                    "-frames:v",
                    "1",
                    "-q:v",
                    "2",
                    str(output),
                ]
            )
            if result.returncode != 0 or not output.exists():
                raise RuntimeError(f"Contact-sheet assembly failed: {result.stderr.strip()[:500]}")
    except (OSError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    with index_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["cell", "row", "column", "label", "time_seconds"])
        for index, (label, timestamp) in enumerate(samples):
            writer.writerow([index + 1, index // columns + 1, index % columns + 1, label, f"{timestamp:.6f}"])

    print(f"Wrote {output} and {index_output}: {len(samples)} frame(s), {columns}x{rows}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
