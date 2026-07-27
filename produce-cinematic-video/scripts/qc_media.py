#!/usr/bin/env python3
"""Automated technical QC for a rendered video; editorial review remains separate."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

from cinematic_config import ConfigError, dump_json, load_config, resolve_tool


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid JSON in {path} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")
    return value


def rate(value: Any) -> float | None:
    try:
        if value in (None, "", "N/A", "0/0"):
            return None
        parsed = Fraction(str(value))
        if parsed <= 0:
            return None
        return float(parsed)
    except (ValueError, ZeroDivisionError):
        return None


def probe(ffprobe: str, media: Path) -> dict[str, Any]:
    result = run(
        [
            ffprobe,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(media),
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[:800] or "ffprobe failed")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("ffprobe returned invalid JSON") from exc


def check(
    checks: list[dict[str, Any]],
    name: str,
    status: str,
    observed: Any,
    expected: Any,
    detail: str,
) -> None:
    checks.append(
        {
            "name": name,
            "status": status,
            "observed": observed,
            "expected": expected,
            "detail": detail,
        }
    )


def merge_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    valid = sorted((max(0.0, start), max(0.0, end)) for start, end in intervals if end > start)
    merged: list[tuple[float, float]] = []
    for start, end in valid:
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    return merged


def subtract_intervals(
    intervals: list[tuple[float, float]],
    allowed: list[tuple[float, float]],
    padding: float = 0.1,
) -> list[tuple[float, float]]:
    padded = merge_intervals(
        [(max(0.0, start - padding), end + padding) for start, end in allowed]
    )
    output: list[tuple[float, float]] = []
    for start, end in merge_intervals(intervals):
        pieces = [(start, end)]
        for allow_start, allow_end in padded:
            next_pieces: list[tuple[float, float]] = []
            for piece_start, piece_end in pieces:
                if allow_end <= piece_start or allow_start >= piece_end:
                    next_pieces.append((piece_start, piece_end))
                    continue
                if piece_start < allow_start:
                    next_pieces.append((piece_start, allow_start))
                if allow_end < piece_end:
                    next_pieces.append((allow_end, piece_end))
            pieces = next_pieces
        output.extend((start, end) for start, end in pieces if end - start > 0.001)
    return output


def interval_dicts(intervals: list[tuple[float, float]]) -> list[dict[str, float]]:
    return [
        {
            "start": round(start, 6),
            "end": round(end, 6),
            "duration": round(end - start, 6),
        }
        for start, end in intervals
    ]


def parse_complete_intervals(text: str, prefix: str, media_duration: float) -> list[tuple[float, float]]:
    event_re = re.compile(
        rf"{re.escape(prefix)}_(start|end|duration):\s*(-?(?:inf|[0-9]+(?:\.[0-9]+)?))"
    )
    current_start: float | None = None
    intervals: list[tuple[float, float]] = []
    for match in event_re.finditer(text):
        kind = match.group(1)
        raw = match.group(2)
        if raw in {"inf", "-inf"}:
            continue
        value = float(raw)
        if kind == "start":
            if current_start is not None and value > current_start:
                intervals.append((current_start, value))
            current_start = value
        elif kind == "end" and current_start is not None:
            if value > current_start:
                intervals.append((current_start, value))
            current_start = None
    if current_start is not None and media_duration > current_start:
        intervals.append((current_start, media_duration))
    return merge_intervals(intervals)


def detect_black(
    ffmpeg: str,
    media: Path,
    min_duration: float,
) -> tuple[list[tuple[float, float]], str | None]:
    result = run(
        [
            ffmpeg,
            "-hide_banner",
            "-nostats",
            "-nostdin",
            "-i",
            str(media),
            "-vf",
            f"blackdetect=d={min_duration}:pix_th=0.10",
            "-an",
            "-f",
            "null",
            "-",
        ]
    )
    if result.returncode != 0:
        return [], result.stderr.strip()[-1000:] or "blackdetect failed"
    pattern = re.compile(
        r"black_start:([0-9]+(?:\.[0-9]+)?)\s+"
        r"black_end:([0-9]+(?:\.[0-9]+)?)"
    )
    intervals = [
        (float(match.group(1)), float(match.group(2)))
        for match in pattern.finditer(result.stderr)
        if float(match.group(2)) > float(match.group(1))
    ]
    return merge_intervals(intervals), None


def detect_event_intervals(
    ffmpeg: str,
    media: Path,
    filter_text: str,
    prefix: str,
    media_duration: float,
) -> tuple[list[tuple[float, float]], str | None]:
    result = run(
        [
            ffmpeg,
            "-hide_banner",
            "-nostats",
            "-nostdin",
            "-i",
            str(media),
            "-vf" if prefix == "freeze" else "-af",
            filter_text,
            "-an" if prefix == "freeze" else "-vn",
            "-f",
            "null",
            "-",
        ]
    )
    if result.returncode != 0:
        return [], result.stderr.strip()[-1000:] or f"{prefix} detection failed"
    return parse_complete_intervals(result.stderr, prefix, media_duration), None


def measure_loudness(
    ffmpeg: str,
    media: Path,
) -> tuple[dict[str, float], str | None]:
    result = run(
        [
            ffmpeg,
            "-hide_banner",
            "-nostats",
            "-nostdin",
            "-i",
            str(media),
            "-map",
            "0:a:0",
            "-vn",
            "-af",
            "ebur128=peak=true:framelog=verbose",
            "-f",
            "null",
            "-",
        ]
    )
    if result.returncode != 0:
        return {}, result.stderr.strip()[-1000:] or "ebur128 failed"

    def last_number(pattern: str) -> float | None:
        values = re.findall(pattern, result.stderr)
        for raw in reversed(values):
            if raw not in {"inf", "-inf"}:
                return float(raw)
        return None

    integrated = last_number(r"\bI:\s*(-?(?:inf|[0-9]+(?:\.[0-9]+)?))\s+LUFS")
    peak = last_number(r"\bPeak:\s*(-?(?:inf|[0-9]+(?:\.[0-9]+)?))\s+dBFS")
    measured: dict[str, float] = {}
    if integrated is not None:
        measured["integrated_lufs"] = integrated
    if peak is not None:
        measured["true_peak_dbtp"] = peak
    if not measured:
        return {}, "ebur128 completed but no summary values were parsed"
    return measured, None


def timeline_intervals(plan: dict[str, Any], kinds: set[str]) -> list[tuple[float, float]]:
    intervals: list[tuple[float, float]] = []
    for clip in plan.get("timeline") or []:
        if not isinstance(clip, dict):
            continue
        source = clip.get("source") if isinstance(clip.get("source"), dict) else {}
        if source.get("kind") not in kinds:
            continue
        start = clip.get("timeline_in")
        duration = clip.get("duration")
        if isinstance(start, (int, float)) and isinstance(duration, (int, float)) and duration > 0:
            intervals.append((float(start), float(start + duration)))
    return merge_intervals(intervals)


def planned_silence(plan: dict[str, Any]) -> list[tuple[float, float]]:
    audio = plan.get("audio") if isinstance(plan.get("audio"), dict) else {}
    intervals: list[tuple[float, float]] = []
    for silence in audio.get("silence_moments") or []:
        if not isinstance(silence, dict):
            continue
        start = silence.get("start")
        duration = silence.get("duration")
        if isinstance(start, (int, float)) and isinstance(duration, (int, float)) and duration > 0:
            intervals.append((float(start), float(start + duration)))
    return merge_intervals(intervals)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Technical QC for a final or review video.")
    parser.add_argument("video")
    parser.add_argument("--plan", help="Edit plan JSON for expected timeline and QC targets.")
    parser.add_argument("--profile", help="Delivery profile name; defaults to the plan profile.")
    parser.add_argument("--config", help="Explicit user config path.")
    parser.add_argument("--ffmpeg", help="Explicit ffmpeg executable.")
    parser.add_argument("--ffprobe", help="Explicit ffprobe executable.")
    parser.add_argument("-o", "--output", default="qc_report.json")
    parser.add_argument("--loudness-tolerance", type=float, default=1.5)
    parser.add_argument("--quick", action="store_true", help="Run metadata checks only; skip full decode scans.")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    media = Path(args.video)
    output = Path(args.output)
    if not media.is_file():
        print(f"ERROR: Media not found: {media}", file=sys.stderr)
        return 2
    if output.exists() and not args.overwrite:
        print(f"ERROR: Output exists: {output}. Pass --overwrite.", file=sys.stderr)
        return 2
    if args.loudness_tolerance < 0:
        print("ERROR: --loudness-tolerance must be non-negative.", file=sys.stderr)
        return 2

    try:
        if args.config:
            config, config_file = load_config(args.config)
        elif args.ffmpeg or args.ffprobe:
            config: dict[str, Any] = {
                "tools": {
                    "ffmpeg": args.ffmpeg or "ffmpeg",
                    "ffprobe": args.ffprobe or "ffprobe",
                },
                "delivery_profiles": {},
            }
            config_file = None
        else:
            config, config_file = load_config(args.config)
        ffmpeg = resolve_tool(config, "ffmpeg", args.ffmpeg)
        ffprobe = resolve_tool(config, "ffprobe", args.ffprobe)
        plan = load_json(Path(args.plan)) if args.plan else {}
        info = probe(ffprobe, media)
    except (ConfigError, OSError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    checks: list[dict[str, Any]] = []
    streams = info.get("streams") or []
    video_stream = next(
        (
            stream
            for stream in streams
            if stream.get("codec_type") == "video"
            and (stream.get("disposition") or {}).get("attached_pic") != 1
        ),
        None,
    )
    audio_stream = next(
        (stream for stream in streams if stream.get("codec_type") == "audio"),
        None,
    )
    format_info = info.get("format") or {}
    try:
        media_duration = float(format_info.get("duration"))
    except (TypeError, ValueError):
        media_duration = 0.0

    if not video_stream:
        check(checks, "video_stream", "fail", None, "present", "No video stream found.")
    else:
        check(checks, "video_stream", "pass", video_stream.get("codec_name"), "present", "Video stream is readable.")

    meta = plan.get("meta") if isinstance(plan.get("meta"), dict) else {}
    qc_targets = plan.get("qc_targets") if isinstance(plan.get("qc_targets"), dict) else {}
    profile_name = args.profile or meta.get("delivery_profile")
    profiles = config.get("delivery_profiles", {}) if isinstance(config.get("delivery_profiles"), dict) else {}
    profile = profiles.get(profile_name, {}) if profile_name else {}
    if profile_name and not profile:
        check(checks, "delivery_profile", "warning", profile_name, "configured", "Delivery profile is not present in the loaded config.")

    target_duration = meta.get("target_duration")
    tolerance = qc_targets.get("duration_tolerance_seconds", 0.5)
    if isinstance(target_duration, (int, float)) and isinstance(tolerance, (int, float)):
        passed = abs(media_duration - target_duration) <= tolerance
        check(
            checks,
            "duration",
            "pass" if passed else "fail",
            round(media_duration, 6),
            {"seconds": target_duration, "tolerance": tolerance},
            "Rendered duration compared with the edit plan.",
        )
    else:
        check(checks, "duration", "info", round(media_duration, 6), None, "No plan target supplied.")

    if video_stream:
        resolution = f"{video_stream.get('width')}x{video_stream.get('height')}"
        expected_resolution = meta.get("resolution") or (profile.get("video") or {}).get("resolution")
        check(
            checks,
            "resolution",
            "pass" if not expected_resolution or resolution == expected_resolution else "fail",
            resolution,
            expected_resolution,
            "Raster dimensions.",
        )
        actual_fps = rate(video_stream.get("avg_frame_rate"))
        expected_fps = meta.get("fps") or (profile.get("video") or {}).get("fps")
        fps_pass = (
            expected_fps in (None, "source")
            or (
                actual_fps is not None
                and isinstance(expected_fps, (int, float))
                and abs(actual_fps - float(expected_fps)) < 0.02
            )
        )
        check(checks, "fps", "pass" if fps_pass else "fail", actual_fps, expected_fps, "Average video frame rate.")

        profile_video = profile.get("video") if isinstance(profile.get("video"), dict) else {}
        for field, stream_field in (
            ("pixel_format", "pix_fmt"),
            ("color_space", "color_space"),
        ):
            expected = profile_video.get(field)
            observed = video_stream.get(stream_field)
            if expected and expected != "source":
                check(
                    checks,
                    field,
                    "pass" if observed == expected else "fail",
                    observed,
                    expected,
                    f"Video {field}.",
                )

    plan_audio = plan.get("audio") if isinstance(plan.get("audio"), dict) else {}
    audio_expected = plan_audio.get("expected")
    if audio_expected is True:
        check(checks, "audio_stream", "pass" if audio_stream else "fail", bool(audio_stream), True, "Plan expects audio.")
    elif audio_expected is False:
        check(checks, "audio_stream", "pass" if not audio_stream else "warning", bool(audio_stream), False, "Plan is intentionally silent.")
    else:
        check(checks, "audio_stream", "info", bool(audio_stream), None, "No explicit audio expectation.")

    if audio_stream and profile:
        profile_audio = profile.get("audio") if isinstance(profile.get("audio"), dict) else {}
        expected_rate = profile_audio.get("sample_rate")
        observed_rate = int(audio_stream["sample_rate"]) if str(audio_stream.get("sample_rate", "")).isdigit() else None
        if expected_rate:
            check(checks, "sample_rate", "pass" if observed_rate == expected_rate else "fail", observed_rate, expected_rate, "Audio sample rate.")
        expected_channels = profile_audio.get("channels")
        observed_channels = audio_stream.get("channels")
        if expected_channels:
            check(checks, "channels", "pass" if observed_channels == expected_channels else "fail", observed_channels, expected_channels, "Audio channel count.")

    scan_results: dict[str, Any] = {}
    if args.quick:
        check(
            checks,
            "decode_scans",
            "warning",
            "not_run",
            "full",
            "Quick mode skipped black, freeze, silence, and loudness scans.",
        )
    elif video_stream:
        black_min = float(qc_targets.get("black_min_duration_seconds", 0.08))
        blacks, error = detect_black(ffmpeg, media, black_min)
        if error:
            check(checks, "black_scan", "fail", error, "successful scan", "blackdetect could not run.")
        else:
            intended_black = timeline_intervals(plan, {"black"})
            unexpected_black = subtract_intervals(blacks, intended_black)
            unexpected_seconds = sum(end - start for start, end in unexpected_black)
            max_black = float(qc_targets.get("max_unexpected_black_seconds", 0))
            scan_results["black_segments"] = interval_dicts(blacks)
            scan_results["unexpected_black_segments"] = interval_dicts(unexpected_black)
            check(
                checks,
                "unexpected_black",
                "pass" if unexpected_seconds <= max_black + 0.001 else "fail",
                round(unexpected_seconds, 6),
                {"max_seconds": max_black},
                "Total unexpected black duration after subtracting planned black clips.",
            )

        freeze_min = float(qc_targets.get("freeze_min_duration_seconds", 1))
        freezes, error = detect_event_intervals(
            ffmpeg,
            media,
            f"freezedetect=n=-60dB:d={freeze_min}",
            "freeze",
            media_duration,
        )
        if error:
            check(checks, "freeze_scan", "fail", error, "successful scan", "freezedetect could not run.")
        else:
            planned_static = timeline_intervals(plan, {"still", "title", "black"})
            unexpected_freeze = subtract_intervals(freezes, planned_static)
            scan_results["freeze_segments"] = interval_dicts(freezes)
            scan_results["unexpected_freeze_segments"] = interval_dicts(unexpected_freeze)
            check(
                checks,
                "freeze_review",
                "warning" if unexpected_freeze else "pass",
                interval_dicts(unexpected_freeze),
                "review",
                "Unexpected freeze segments require editorial review; they are not automatically defects.",
            )

        if audio_stream:
            silence_min = float(qc_targets.get("silence_min_duration_seconds", 2))
            silences, error = detect_event_intervals(
                ffmpeg,
                media,
                f"silencedetect=noise=-50dB:d={silence_min}",
                "silence",
                media_duration,
            )
            if error:
                check(checks, "silence_scan", "fail", error, "successful scan", "silencedetect could not run.")
            else:
                unexpected_silence = subtract_intervals(silences, planned_silence(plan))
                scan_results["silence_segments"] = interval_dicts(silences)
                scan_results["unexpected_silence_segments"] = interval_dicts(unexpected_silence)
                check(
                    checks,
                    "silence_review",
                    "warning" if unexpected_silence else "pass",
                    interval_dicts(unexpected_silence),
                    "review",
                    "Unexpected silence needs contextual review; silence may be intentional.",
                )

            loudness, error = measure_loudness(ffmpeg, media)
            if error:
                check(checks, "loudness_scan", "fail", error, "successful scan", "ebur128 could not run.")
            else:
                scan_results["loudness"] = loudness
                profile_audio = profile.get("audio") if isinstance(profile.get("audio"), dict) else {}
                target_lufs = profile_audio.get("integrated_lufs")
                target_peak = profile_audio.get("true_peak_dbtp")
                observed_lufs = loudness.get("integrated_lufs")
                observed_peak = loudness.get("true_peak_dbtp")
                if target_lufs is not None:
                    passed = (
                        observed_lufs is not None
                        and abs(observed_lufs - float(target_lufs)) <= args.loudness_tolerance
                    )
                    check(
                        checks,
                        "integrated_loudness",
                        "pass" if passed else "fail",
                        observed_lufs,
                        {"lufs": target_lufs, "tolerance": args.loudness_tolerance},
                        "Integrated programme loudness.",
                    )
                else:
                    check(checks, "integrated_loudness", "info", observed_lufs, None, "No profile target.")
                if target_peak is not None:
                    passed = observed_peak is not None and observed_peak <= float(target_peak)
                    check(
                        checks,
                        "true_peak",
                        "pass" if passed else "fail",
                        observed_peak,
                        {"maximum_dbtp": target_peak},
                        "True peak ceiling.",
                    )
                else:
                    check(checks, "true_peak", "info", observed_peak, None, "No profile target.")

    failures = [item for item in checks if item["status"] == "fail"]
    warnings = [item for item in checks if item["status"] == "warning"]
    report = {
        "version": 1,
        "video": str(media.resolve()),
        "plan": str(Path(args.plan).resolve()) if args.plan else "",
        "config": str(config_file) if config_file else "",
        "delivery_profile": profile_name or "",
        "passed": not failures,
        "scope": "metadata-only" if args.quick else "automated-technical",
        "checks": checks,
        "scan_results": scan_results,
        "summary": {
            "failures": len(failures),
            "warnings": len(warnings),
            "note": "This report does not validate story, performance, facts, rights, continuity, accessibility, or marketing claims.",
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(dump_json(report), encoding="utf-8")
    for item in checks:
        print(f"[{item['status'].upper()}] {item['name']}: {item['detail']}")
    print(
        f"{'PASS' if report['passed'] else 'FAIL'}: "
        f"{len(failures)} failure(s), {len(warnings)} warning(s) -> {output}"
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
