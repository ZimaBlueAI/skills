#!/usr/bin/env python3
"""Estimate global dialogue A/V offset from mouth motion and an audio envelope."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any

from cinematic_config import ConfigError, dump_json, load_config, resolve_executable


class SyncError(RuntimeError):
    pass


def correlation(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 3:
        return 0.0
    lm = statistics.fmean(left)
    rm = statistics.fmean(right)
    numerator = sum((a - lm) * (b - rm) for a, b in zip(left, right))
    ld = math.sqrt(sum((a - lm) ** 2 for a in left))
    rd = math.sqrt(sum((b - rm) ** 2 for b in right))
    return numerator / (ld * rd) if ld and rd else 0.0


def audio_envelope(
    ffmpeg: str,
    source: Path,
    *,
    sample_fps: float,
    duration_s: float,
    sample_rate: int = 16000,
) -> list[float]:
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(source),
        "-vn",
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        "-f",
        "s16le",
        "pipe:1",
    ]
    result = subprocess.run(command, capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace")
        raise SyncError("Audio extraction failed: " + detail[-1000:])
    import numpy as np

    samples = np.frombuffer(result.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    window = max(1, int(sample_rate / sample_fps))
    count = max(1, int(math.ceil(duration_s * sample_fps)))
    envelope: list[float] = []
    for index in range(count):
        block = samples[index * window : (index + 1) * window]
        envelope.append(float(np.sqrt(np.mean(block * block))) if block.size else 0.0)
    if envelope:
        floor = statistics.median(envelope)
        envelope = [max(0.0, value - floor * 0.65) for value in envelope]
    return envelope


def visual_mouth_curve(
    video: Path,
    *,
    sample_fps: float,
    max_seconds: float | None,
) -> tuple[list[float | None], float, float]:
    try:
        import cv2
        import numpy as np
    except ModuleNotFoundError as exc:
        raise SyncError("OpenCV and NumPy are required; run environment_doctor.py --require-av-sync.") from exc

    capture = cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise SyncError(f"OpenCV cannot open video: {video}")
    source_fps = float(capture.get(cv2.CAP_PROP_FPS) or 0)
    frame_count = float(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if source_fps <= 0:
        raise SyncError("Video frame rate is unavailable.")
    duration = frame_count / source_fps if frame_count > 0 else 0.0
    if max_seconds is not None:
        duration = min(duration, max_seconds) if duration else max_seconds
    step = max(1, int(round(source_fps / sample_fps)))
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(str(cascade_path))
    if detector.empty():
        raise SyncError(f"OpenCV face cascade is unavailable: {cascade_path}")

    curve: list[float | None] = []
    previous_mouth: Any = None
    previous_upper: Any = None
    frame_index = 0
    sampled = 0
    detected = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        timestamp = frame_index / source_fps
        if duration and timestamp > duration:
            break
        if frame_index % step:
            frame_index += 1
            continue
        sampled += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(
            gray,
            scaleFactor=1.12,
            minNeighbors=5,
            minSize=(48, 48),
        )
        if len(faces) == 0:
            curve.append(None)
            previous_mouth = None
            previous_upper = None
            frame_index += 1
            continue
        x, y, w, h = max(faces, key=lambda item: int(item[2]) * int(item[3]))
        detected += 1
        mouth = gray[y + int(h * 0.56) : y + int(h * 0.94), x + int(w * 0.12) : x + int(w * 0.88)]
        upper = gray[y + int(h * 0.18) : y + int(h * 0.50), x + int(w * 0.12) : x + int(w * 0.88)]
        if mouth.size == 0 or upper.size == 0:
            curve.append(None)
            frame_index += 1
            continue
        mouth = cv2.resize(mouth, (96, 48), interpolation=cv2.INTER_AREA)
        upper = cv2.resize(upper, (96, 48), interpolation=cv2.INTER_AREA)
        if previous_mouth is None or previous_upper is None:
            curve.append(0.0)
        else:
            mouth_motion = float(np.mean(cv2.absdiff(mouth, previous_mouth))) / 255.0
            face_motion = float(np.mean(cv2.absdiff(upper, previous_upper))) / 255.0
            curve.append(max(0.0, mouth_motion - 0.55 * face_motion))
        previous_mouth = mouth
        previous_upper = upper
        frame_index += 1
    capture.release()
    coverage = detected / sampled if sampled else 0.0
    effective_fps = source_fps / step
    return curve, effective_fps, coverage


def align(
    visual: list[float | None],
    audio: list[float],
    *,
    sample_fps: float,
    max_offset_s: float,
) -> dict[str, Any]:
    max_lag = max(1, int(round(max_offset_s * sample_fps)))
    results: list[tuple[int, float, int]] = []
    for lag in range(-max_lag, max_lag + 1):
        left: list[float] = []
        right: list[float] = []
        for index, value in enumerate(visual):
            audio_index = index + lag
            if value is None or audio_index < 0 or audio_index >= len(audio):
                continue
            left.append(float(value))
            right.append(float(audio[audio_index]))
        results.append((lag, correlation(left, right), len(left)))
    best = max(results, key=lambda item: item[1])
    alternatives = [
        item for item in results if abs(item[0] - best[0]) > max(1, int(sample_fps * 0.2))
    ]
    second = max(alternatives, key=lambda item: item[1]) if alternatives else (0, 0.0, 0)
    lag_s = best[0] / sample_fps
    margin = best[1] - second[1]
    if best[1] >= 0.45 and margin >= 0.08 and best[2] >= 20:
        confidence = "high"
    elif best[1] >= 0.25 and margin >= 0.03 and best[2] >= 12:
        confidence = "medium"
    else:
        confidence = "low"
    return {
        "observed_audio_lag_s": round(lag_s, 4),
        "recommended_audio_shift_s": round(-lag_s, 4),
        "correlation": round(best[1], 4),
        "peak_margin": round(margin, 4),
        "paired_samples": best[2],
        "confidence": confidence,
    }


def activity_windows(curve: list[float | None], sample_fps: float) -> list[dict[str, float]]:
    values = [float(value) for value in curve if value is not None]
    if len(values) < 5:
        return []
    threshold = statistics.median(values) + statistics.pstdev(values) * 0.65
    active = [value is not None and value >= threshold for value in curve]
    windows: list[dict[str, float]] = []
    start: int | None = None
    for index, is_active in enumerate(active + [False]):
        if is_active and start is None:
            start = index
        elif not is_active and start is not None:
            if index - start >= max(2, int(round(sample_fps * 0.2))):
                windows.append(
                    {
                        "start_s": round(start / sample_fps, 3),
                        "end_s": round(index / sample_fps, 3),
                    }
                )
            start = None
    return windows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Estimate dialogue A/V offset from mouth motion.")
    parser.add_argument("video")
    parser.add_argument("--audio", help="Dialogue stem; defaults to the video's mixed audio.")
    parser.add_argument("--config")
    parser.add_argument("--sample-fps", type=float, default=8.0)
    parser.add_argument("--max-offset-s", type=float, default=2.0)
    parser.add_argument("--max-seconds", type=float)
    parser.add_argument("--output", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.sample_fps <= 1 or args.sample_fps > 30:
            raise SyncError("--sample-fps must be between 1 and 30.")
        if args.max_offset_s <= 0:
            raise SyncError("--max-offset-s must be positive.")
        config, _ = load_config(args.config)
        tools = config.get("tools") if isinstance(config.get("tools"), dict) else {}
        ffmpeg = resolve_executable(str(tools.get("ffmpeg") or "ffmpeg"))
        if not ffmpeg:
            raise SyncError("FFmpeg cannot be resolved from the user configuration.")
        video = Path(args.video).expanduser().resolve()
        audio = Path(args.audio).expanduser().resolve() if args.audio else video
        output = Path(args.output).expanduser().resolve()
        if not video.is_file() or not audio.is_file():
            raise SyncError("Video or audio input does not exist.")
        if output.exists():
            raise SyncError(f"Refusing to overwrite existing output: {output}")

        visual, effective_fps, coverage = visual_mouth_curve(
            video,
            sample_fps=args.sample_fps,
            max_seconds=args.max_seconds,
        )
        duration_s = len(visual) / effective_fps if effective_fps else 0.0
        envelope = audio_envelope(
            ffmpeg,
            audio,
            sample_fps=effective_fps,
            duration_s=duration_s,
        )
        alignment = align(
            visual,
            envelope,
            sample_fps=effective_fps,
            max_offset_s=args.max_offset_s,
        )
        warnings: list[str] = []
        if coverage < 0.35:
            warnings.append("Visible-face coverage is low; use speaker annotations or a tighter shot range.")
        if alignment["confidence"] == "low":
            warnings.append("Low-confidence correlation; confirm with word timecodes and real-time playback.")
        report = {
            "version": 1,
            "scope": "global_av_offset_candidate",
            "video": str(video),
            "audio": str(audio),
            "sample_fps": round(effective_fps, 4),
            "visible_face_coverage": round(coverage, 4),
            "alignment": alignment,
            "visual_mouth_activity_windows": activity_windows(visual, effective_fps),
            "warnings": warnings,
            "limitations": (
                "Mouth motion does not identify phonemes. Animation, occlusion, voice-over, "
                "camera motion, music bleed, and cuts require forced alignment and human review."
            ),
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(dump_json(report), encoding="utf-8")
        print(f"Wrote {output}; recommended audio shift {alignment['recommended_audio_shift_s']:+.4f}s.")
        return 0
    except (ConfigError, SyncError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
