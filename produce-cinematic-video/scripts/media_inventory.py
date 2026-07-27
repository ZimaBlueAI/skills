#!/usr/bin/env python3
"""Inventory media with ffprobe without changing source files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from pathlib import Path
from typing import Any

from cinematic_config import ConfigError, dump_json, load_config, resolve_tool


VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".mts", ".m2ts", ".mxf"}
AUDIO_EXT = {".mp3", ".wav", ".bwf", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".aif", ".aiff"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp", ".exr", ".dpx"}
MEDIA_EXT = VIDEO_EXT | AUDIO_EXT | IMAGE_EXT


def number(value: Any) -> float | None:
    try:
        if value in (None, "", "N/A"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def integer(value: Any) -> int | None:
    try:
        if value in (None, "", "N/A"):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def rate(value: Any) -> float | None:
    try:
        if value in (None, "", "N/A", "0/0"):
            return None
        parsed = Fraction(str(value))
        if parsed.denominator == 0 or parsed <= 0:
            return None
        return round(float(parsed), 6)
    except (ValueError, ZeroDivisionError):
        return None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_asset_id(path: Path) -> str:
    normalized = os.path.normcase(str(path.resolve()))
    return "AS_" + hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:10].upper()


def stream_rotation(stream: dict[str, Any]) -> float | None:
    tags = stream.get("tags") or {}
    tagged = number(tags.get("rotate"))
    if tagged is not None:
        return tagged
    for side_data in stream.get("side_data_list") or []:
        rotated = number(side_data.get("rotation"))
        if rotated is not None:
            return rotated
    return None


def run_probe(ffprobe: str, path: Path, include_hash: bool) -> dict[str, Any]:
    command = [
        ffprobe,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        "-show_chapters",
        str(path),
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    base: dict[str, Any] = {
        "asset_id": stable_asset_id(path),
        "path": str(path.resolve()),
        "file_name": path.name,
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
        "checksum_sha256": sha256(path) if include_hash else "",
    }
    if result.returncode != 0:
        base["error"] = result.stderr.strip()[:500] or f"ffprobe exited {result.returncode}"
        return base

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        base["error"] = f"ffprobe returned invalid JSON: {exc}"
        return base

    streams = data.get("streams") or []
    video_streams = [
        stream
        for stream in streams
        if stream.get("codec_type") == "video"
        and (stream.get("disposition") or {}).get("attached_pic") != 1
    ]
    audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]
    format_info = data.get("format") or {}
    suffix = path.suffix.lower()
    if suffix in IMAGE_EXT:
        media_kind = "image"
    elif video_streams:
        media_kind = "video"
    elif audio_streams:
        media_kind = "audio"
    else:
        media_kind = "unknown"

    item: dict[str, Any] = {
        **base,
        "kind": media_kind,
        "duration": number(format_info.get("duration")),
        "start_time": number(format_info.get("start_time")),
        "container": format_info.get("format_name", ""),
        "format_long_name": format_info.get("format_long_name", ""),
        "bit_rate": integer(format_info.get("bit_rate")),
        "chapter_count": len(data.get("chapters") or []),
        "video": None,
        "audio": None,
    }

    if video_streams:
        stream = video_streams[0]
        avg_fps = rate(stream.get("avg_frame_rate"))
        nominal_fps = rate(stream.get("r_frame_rate"))
        item["video"] = {
            "stream_count": len(video_streams),
            "codec": stream.get("codec_name"),
            "profile": stream.get("profile"),
            "width": integer(stream.get("width")),
            "height": integer(stream.get("height")),
            "sample_aspect_ratio": stream.get("sample_aspect_ratio"),
            "display_aspect_ratio": stream.get("display_aspect_ratio"),
            "avg_fps": avg_fps,
            "nominal_fps": nominal_fps,
            "vfr_suspected": bool(
                avg_fps
                and nominal_fps
                and abs(avg_fps - nominal_fps) > 0.01
            ),
            "time_base": stream.get("time_base"),
            "pixel_format": stream.get("pix_fmt"),
            "bits_per_raw_sample": integer(stream.get("bits_per_raw_sample")),
            "field_order": stream.get("field_order"),
            "color_range": stream.get("color_range"),
            "color_space": stream.get("color_space"),
            "color_transfer": stream.get("color_transfer"),
            "color_primaries": stream.get("color_primaries"),
            "rotation": stream_rotation(stream),
        }

    if audio_streams:
        stream = audio_streams[0]
        item["audio"] = {
            "stream_count": len(audio_streams),
            "codec": stream.get("codec_name"),
            "sample_rate": integer(stream.get("sample_rate")),
            "channels": integer(stream.get("channels")),
            "channel_layout": stream.get("channel_layout"),
            "sample_format": stream.get("sample_fmt"),
            "bit_rate": integer(stream.get("bit_rate")),
        }
    return item


def collect(inputs: list[str], recursive: bool) -> list[Path]:
    files: list[Path] = []
    for raw in inputs:
        path = Path(raw).expanduser()
        if path.is_dir():
            iterator = path.rglob("*") if recursive else path.glob("*")
            files.extend(
                child.resolve()
                for child in iterator
                if child.is_file() and child.suffix.lower() in MEDIA_EXT
            )
        elif path.is_file() and path.suffix.lower() in MEDIA_EXT:
            files.append(path.resolve())
    return sorted(set(files), key=lambda item: os.path.normcase(str(item)))


def summarize(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    good = [item for item in items if "error" not in item]
    videos = [item for item in good if item.get("kind") == "video"]
    audios = [item for item in good if item.get("audio")]

    def add(code: str, message: str, assets: list[str]) -> None:
        warnings.append({"code": code, "message": message, "asset_ids": assets})

    failed = [item["asset_id"] for item in items if "error" in item]
    if failed:
        add("probe_failed", f"{len(failed)} file(s) could not be probed.", failed)

    fps_values = {
        item["video"]["avg_fps"]
        for item in videos
        if item.get("video") and item["video"].get("avg_fps")
    }
    if len(fps_values) > 1:
        add("mixed_fps", f"Mixed average frame rates: {sorted(fps_values)}.", [item["asset_id"] for item in videos])

    resolutions = {
        (item["video"]["width"], item["video"]["height"])
        for item in videos
        if item.get("video")
    }
    if len(resolutions) > 1:
        add("mixed_resolution", f"Mixed video rasters: {sorted(resolutions)}.", [item["asset_id"] for item in videos])

    color_signatures = {
        (
            item["video"].get("color_primaries"),
            item["video"].get("color_transfer"),
            item["video"].get("color_space"),
        )
        for item in videos
        if item.get("video")
    }
    if len(color_signatures) > 1:
        add("mixed_color", "Mixed or inconsistent color metadata.", [item["asset_id"] for item in videos])

    vfr = [
        item["asset_id"]
        for item in videos
        if item.get("video") and item["video"].get("vfr_suspected")
    ]
    if vfr:
        add("vfr_suspected", "Average and nominal frame rates differ; inspect variable-frame-rate media.", vfr)

    rotated = [
        item["asset_id"]
        for item in videos
        if item.get("video") and item["video"].get("rotation") not in (None, 0, 0.0)
    ]
    if rotated:
        add("rotation_metadata", "Rotation metadata is present; normalize display orientation in proxies.", rotated)

    no_audio = [item["asset_id"] for item in videos if not item.get("audio")]
    if no_audio:
        add("video_without_audio", f"{len(no_audio)} video file(s) have no audio stream.", no_audio)

    sample_rates = {
        item["audio"]["sample_rate"]
        for item in audios
        if item.get("audio") and item["audio"].get("sample_rate")
    }
    if len(sample_rates) > 1:
        add("mixed_sample_rate", f"Mixed audio sample rates: {sorted(sample_rates)}.", [item["asset_id"] for item in audios])
    return warnings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only ffprobe inventory for video, audio, and stills.")
    parser.add_argument("inputs", nargs="+", help="Media files or directories.")
    parser.add_argument("-o", "--output", default="media_inventory.json")
    parser.add_argument("--config", help="Explicit user config path.")
    parser.add_argument("--ffprobe", help="Explicit ffprobe executable; highest precedence.")
    parser.add_argument("--hash", action="store_true", help="Compute SHA-256 checksums.")
    parser.add_argument("--no-recursive", action="store_true", help="Do not recurse into input directories.")
    parser.add_argument("--jobs", type=int, default=4, help="Parallel ffprobe jobs (default: 4).")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output report.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output = Path(args.output)
    if output.exists() and not args.overwrite:
        print(f"ERROR: Output exists: {output}. Pass --overwrite to replace it.", file=sys.stderr)
        return 2
    if args.jobs < 1:
        print("ERROR: --jobs must be at least 1.", file=sys.stderr)
        return 2

    try:
        if args.ffprobe:
            config: dict[str, Any] = {"tools": {"ffprobe": args.ffprobe}}
        else:
            config, _ = load_config(args.config)
        ffprobe = resolve_tool(config, "ffprobe", args.ffprobe)
    except ConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    files = collect(args.inputs, recursive=not args.no_recursive)
    if not files:
        print("ERROR: No recognized media files found.", file=sys.stderr)
        return 2

    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        items = list(executor.map(lambda path: run_probe(ffprobe, path, args.hash), files))

    durations = [
        item["duration"]
        for item in items
        if "error" not in item and isinstance(item.get("duration"), (int, float))
    ]
    report = {
        "version": 1,
        "source_count": len(items),
        "total_duration": round(sum(durations), 3),
        "checksum_mode": "sha256" if args.hash else "off",
        "items": items,
        "warnings": summarize(items),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(dump_json(report), encoding="utf-8")
    print(
        f"Wrote {output}: {len(items)} asset(s), "
        f"{report['total_duration']:.3f}s, {len(report['warnings'])} warning group(s)."
    )
    return 1 if any("error" in item for item in items) else 0


if __name__ == "__main__":
    raise SystemExit(main())
