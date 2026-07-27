#!/usr/bin/env python3
"""Non-destructive FFmpeg stem mixer with gain and optional dialogue ducking."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from cinematic_config import ConfigError, dump_json, load_config, resolve_executable


class MixError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stem_args(args: argparse.Namespace) -> list[tuple[str, Path, float]]:
    stems: list[tuple[str, Path, float]] = []
    for name in ("dialogue", "music", "effects", "ambience"):
        value = getattr(args, name)
        if not value:
            continue
        path = Path(value).expanduser().resolve()
        if not path.is_file():
            raise MixError(f"{name} stem does not exist: {path}")
        stems.append((name, path, float(getattr(args, f"{name}_gain_db"))))
    if not stems:
        raise MixError("Provide at least one stem.")
    return stems


def filter_graph(
    stems: list[tuple[str, Path, float]],
    *,
    duck_music: bool,
    duck_threshold: float,
    duck_ratio: float,
    attack_ms: float,
    release_ms: float,
    loudnorm_i: float | None,
    loudnorm_tp: float,
) -> str:
    indexes = {name: index for index, (name, _, _) in enumerate(stems)}
    lines: list[str] = []
    for index, (name, _, gain) in enumerate(stems):
        lines.append(
            f"[{index}:a]aresample=48000,"
            "aformat=sample_fmts=fltp:channel_layouts=stereo,"
            f"volume={gain:.3f}dB[{name}_pre]"
        )

    labels: list[str] = []
    if duck_music:
        if "dialogue" not in indexes or "music" not in indexes:
            raise MixError("--duck-music requires both dialogue and music stems.")
        lines.append("[dialogue_pre]asplit=2[dialogue_mix][dialogue_sc]")
        lines.append(
            "[music_pre][dialogue_sc]sidechaincompress="
            f"threshold={duck_threshold:.6f}:ratio={duck_ratio:.3f}:"
            f"attack={attack_ms:.1f}:release={release_ms:.1f}[music_ducked]"
        )
        labels.extend(["dialogue_mix", "music_ducked"])
    else:
        for name in ("dialogue", "music"):
            if name in indexes:
                labels.append(f"{name}_pre")
    for name in ("effects", "ambience"):
        if name in indexes:
            labels.append(f"{name}_pre")

    mix_inputs = "".join(f"[{label}]" for label in labels)
    lines.append(
        f"{mix_inputs}amix=inputs={len(labels)}:duration=longest:"
        f"dropout_transition=0[mix_normalized];"
        f"[mix_normalized]volume={len(labels):.6f}[mix]"
    )
    if loudnorm_i is not None:
        lines.append(
            f"[mix]loudnorm=I={loudnorm_i:.2f}:TP={loudnorm_tp:.2f}:"
            "LRA=11:linear=false[out]"
        )
    else:
        lines.append("[mix]anull[out]")
    return ";".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mix dialogue, music, effects, and ambience stems.")
    parser.add_argument("--config", help="Explicit cinematic-video .env.local path.")
    for name in ("dialogue", "music", "effects", "ambience"):
        parser.add_argument(f"--{name}")
        parser.add_argument(f"--{name}-gain-db", type=float, default=0.0)
    parser.add_argument("--duck-music", action="store_true")
    parser.add_argument("--duck-threshold", type=float, default=0.035)
    parser.add_argument("--duck-ratio", type=float, default=6.0)
    parser.add_argument("--duck-attack-ms", type=float, default=20.0)
    parser.add_argument("--duck-release-ms", type=float, default=250.0)
    parser.add_argument("--loudnorm-i", type=float)
    parser.add_argument("--loudnorm-tp", type=float, default=-1.0)
    parser.add_argument("--output", required=True)
    parser.add_argument("--provenance")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        config, _ = load_config(args.config)
        tools = config.get("tools") if isinstance(config.get("tools"), dict) else {}
        ffmpeg = resolve_executable(str(tools.get("ffmpeg") or "ffmpeg"))
        if not ffmpeg:
            raise MixError("FFmpeg cannot be resolved from the user configuration.")
        stems = stem_args(args)
        output = Path(args.output).expanduser().resolve()
        provenance = (
            Path(args.provenance).expanduser().resolve()
            if args.provenance
            else output.with_suffix(output.suffix + ".provenance.json")
        )
        for path in (output, provenance):
            if path.exists():
                raise MixError(f"Refusing to overwrite existing file: {path}")
        output.parent.mkdir(parents=True, exist_ok=True)

        graph = filter_graph(
            stems,
            duck_music=args.duck_music,
            duck_threshold=args.duck_threshold,
            duck_ratio=args.duck_ratio,
            attack_ms=args.duck_attack_ms,
            release_ms=args.duck_release_ms,
            loudnorm_i=args.loudnorm_i,
            loudnorm_tp=args.loudnorm_tp,
        )
        command = [ffmpeg, "-hide_banner", "-loglevel", "error"]
        for _, path, _ in stems:
            command.extend(["-i", str(path)])
        command.extend(["-filter_complex", graph, "-map", "[out]", "-ar", "48000", "-ac", "2"])
        if output.suffix.lower() == ".wav":
            command.extend(["-c:a", "pcm_s24le"])
        elif output.suffix.lower() in {".m4a", ".mp4"}:
            command.extend(["-c:a", "aac", "-b:a", "320k"])
        else:
            raise MixError("Output must be .wav, .m4a, or .mp4.")
        command.append(str(output))

        plan = {
            "inputs": [
                {"role": name, "path": str(path), "gain_db": gain}
                for name, path, gain in stems
            ],
            "output": str(output),
            "duck_music": args.duck_music,
            "loudnorm_i": args.loudnorm_i,
            "loudnorm_tp": args.loudnorm_tp,
            "ffmpeg": ffmpeg,
            "filter_complex": graph,
        }
        if args.dry_run:
            print(dump_json(plan), end="")
            return 0

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode != 0:
            raise MixError("FFmpeg mix failed: " + (result.stderr or "")[-1200:])
        if not output.is_file():
            raise MixError("FFmpeg returned without creating the output.")

        record = {
            "schema_version": 1,
            "asset_type": "audio_mix",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "inputs": [
                {
                    "role": name,
                    "path": str(path),
                    "sha256": sha256_file(path),
                    "gain_db": gain,
                }
                for name, path, gain in stems
            ],
            "parameters": {
                "duck_music": args.duck_music,
                "duck_threshold": args.duck_threshold,
                "duck_ratio": args.duck_ratio,
                "duck_attack_ms": args.duck_attack_ms,
                "duck_release_ms": args.duck_release_ms,
                "loudnorm_i": args.loudnorm_i,
                "loudnorm_tp": args.loudnorm_tp,
            },
            "output": {"path": str(output), "sha256": sha256_file(output)},
            "review_required": True,
        }
        provenance.write_text(dump_json(record), encoding="utf-8")
        print(f"Wrote {output} and {provenance}.")
        return 0
    except (ConfigError, MixError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
