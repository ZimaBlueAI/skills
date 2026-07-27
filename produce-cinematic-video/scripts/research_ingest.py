#!/usr/bin/env python3
"""Build an auditable research manifest from an OmniGet/export folder."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cinematic_config import ConfigError, dump_json, load_config, resolve_executable


VIDEO_EXTENSIONS = {
    ".3gp",
    ".avi",
    ".m2ts",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".ts",
    ".webm",
}
AUDIO_EXTENSIONS = {
    ".aac",
    ".flac",
    ".m4a",
    ".mp3",
    ".ogg",
    ".opus",
    ".wav",
}
SUBTITLE_EXTENSIONS = {".ass", ".srt", ".ssa", ".vtt"}
IMAGE_EXTENSIONS = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".webp"}
DOCUMENT_EXTENSIONS = {".epub", ".html", ".md", ".pdf", ".txt"}
RIGHTS_BASES = {
    "owned",
    "licensed",
    "permission",
    "public-domain",
    "research-only",
}
SENSITIVE_QUERY_NAMES = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "key",
    "sig",
    "signature",
    "token",
}


class ResearchIngestError(RuntimeError):
    """Raised when research ingest cannot preserve an auditable boundary."""


def expand_path(value: str | Path) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(str(value)))).resolve()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix in VIDEO_EXTENSIONS:
        return "video"
    if suffix in AUDIO_EXTENSIONS:
        return "audio"
    if suffix in SUBTITLE_EXTENSIONS:
        return "subtitle"
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in DOCUMENT_EXTENSIONS:
        return "document"
    if path.name.lower().endswith(".info.json"):
        return "metadata"
    return None


def canonical_base(path: Path, kind: str) -> str:
    name = path.name
    if kind == "metadata" and name.lower().endswith(".info.json"):
        return name[: -len(".info.json")]
    if kind == "subtitle":
        # yt-dlp commonly emits title.<language>.srt.
        first = name[: -len(path.suffix)]
        return first.rsplit(".", 1)[0] if "." in first else first
    return path.stem


def safe_metadata(path: Path) -> tuple[dict[str, Any], list[str]]:
    issues: list[str] = []
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {}, [f"Could not parse metadata sidecar {path.name}: {exc}"]
    if not isinstance(raw, dict):
        return {}, [f"Metadata sidecar is not an object: {path.name}"]
    selected: dict[str, Any] = {}
    for key in (
        "id",
        "title",
        "fulltitle",
        "description",
        "uploader",
        "uploader_id",
        "channel",
        "channel_id",
        "extractor",
        "extractor_key",
        "upload_date",
        "timestamp",
        "duration",
        "view_count",
        "like_count",
        "comment_count",
        "availability",
        "license",
    ):
        value = raw.get(key)
        if value is not None:
            if key == "description" and isinstance(value, str) and len(value) > 2000:
                value = value[:2000]
                issues.append(
                    f"Description in {path.name} was truncated to 2000 characters."
                )
            selected[key] = value
    for key in ("webpage_url", "original_url"):
        value = raw.get(key)
        if isinstance(value, str) and value.startswith(("https://", "http://")):
            selected["source_url"] = value
            break
    # Never retain direct media URLs, headers, cookies, tokens, or request data.
    return selected, issues


def validate_source_url(value: str, asset: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ResearchIngestError(
            f"Source URL for {asset} must be an absolute HTTP(S) page URL without user info."
        )
    query_names = {
        key.casefold()
        for key in urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    }
    if query_names & SENSITIVE_QUERY_NAMES:
        raise ResearchIngestError(
            f"Source URL for {asset} appears to contain a credential or signature; "
            "store the public canonical page URL instead."
        )
    return value


def probe_media(path: Path, ffprobe: str | None) -> tuple[dict[str, Any] | None, str | None]:
    if not ffprobe:
        return None, "FFprobe was not resolved; technical media metadata was not inspected."
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            (
                "format=format_name,duration,size,bit_rate:"
                "stream=index,codec_type,codec_name,width,height,r_frame_rate,"
                "sample_rate,channels"
            ),
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        detail = str(result.stderr or "").strip()
        return None, f"FFprobe failed for {path.name}: {detail[-500:]}"
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return None, f"FFprobe returned invalid JSON for {path.name}: {exc}"
    return parsed if isinstance(parsed, dict) else None, None


def read_source_map(path: str | None) -> dict[str, dict[str, Any]]:
    if not path:
        return {}
    source = expand_path(path)
    try:
        parsed = json.loads(source.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ResearchIngestError(f"Unable to read source map {source}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ResearchIngestError("Source map must be a JSON object keyed by relative path.")
    normalized: dict[str, dict[str, Any]] = {}
    for key, value in parsed.items():
        if not isinstance(key, str) or not isinstance(value, dict):
            raise ResearchIngestError("Each source-map entry must map a path string to an object.")
        normalized[key.replace("\\", "/")] = value
    return normalized


def resolve_ffprobe(args: argparse.Namespace) -> str | None:
    if args.ffprobe:
        try:
            resolved = resolve_executable(args.ffprobe)
        except OSError as exc:
            raise ResearchIngestError(
                f"FFprobe path cannot be accessed: {args.ffprobe}: {exc}"
            ) from exc
        if not resolved:
            raise ResearchIngestError(f"FFprobe cannot be resolved: {args.ffprobe}")
        return resolved
    try:
        config, _ = load_config(args.config)
    except (ConfigError, OSError):
        return resolve_executable("ffprobe")
    tools = config.get("tools")
    value = tools.get("ffprobe") if isinstance(tools, dict) else "ffprobe"
    try:
        return resolve_executable(str(value or "ffprobe"))
    except OSError:
        return None


def build_manifest(args: argparse.Namespace) -> dict[str, Any]:
    if not str(args.collection_title or "").strip():
        raise ResearchIngestError("Collection title must not be empty.")
    accessed_at = args.accessed_at or datetime.now(timezone.utc).date().isoformat()
    try:
        datetime.strptime(accessed_at, "%Y-%m-%d")
    except ValueError as exc:
        raise ResearchIngestError("--accessed-at must use YYYY-MM-DD.") from exc
    input_dir = expand_path(args.input_dir)
    if not input_dir.is_dir():
        raise ResearchIngestError(f"Research input directory does not exist: {input_dir}")
    output = expand_path(args.output)
    source_map = read_source_map(args.source_map)
    ffprobe = resolve_ffprobe(args)
    discovered: list[tuple[Path, str]] = []
    for path in sorted(input_dir.rglob("*")):
        if not path.is_file() or path == output:
            continue
        kind = classify(path)
        if kind:
            discovered.append((path, kind))
    by_directory_and_base: dict[tuple[Path, str], list[tuple[Path, str]]] = {}
    for path, kind in discovered:
        key = (path.parent, canonical_base(path, kind).casefold())
        by_directory_and_base.setdefault(key, []).append((path, kind))
    primary: list[tuple[Path, str]] = []
    for path, kind in discovered:
        if kind in {"video", "audio", "document"}:
            primary.append((path, kind))
            continue
        if kind == "image":
            group = by_directory_and_base.get(
                (path.parent, canonical_base(path, kind).casefold()), []
            )
            if not any(
                sibling_kind in {"video", "audio", "document"}
                for _, sibling_kind in group
            ):
                primary.append((path, kind))
    if not primary:
        raise ResearchIngestError(
            "No video, audio, image, PDF/EPUB, HTML, Markdown, or text research assets were found."
        )

    records: list[dict[str, Any]] = []
    issues: list[dict[str, str]] = []
    for index, (path, kind) in enumerate(primary, start=1):
        relative = path.relative_to(input_dir).as_posix()
        group = by_directory_and_base.get(
            (path.parent, canonical_base(path, kind).casefold()), []
        )
        metadata: dict[str, Any] = {}
        sidecars: list[dict[str, Any]] = []
        for sidecar, sidecar_kind in group:
            if sidecar == path:
                continue
            sidecar_relative = sidecar.relative_to(input_dir).as_posix()
            sidecars.append(
                {
                    "kind": sidecar_kind,
                    "path": sidecar_relative,
                    "sha256": sha256_file(sidecar),
                    "bytes": sidecar.stat().st_size,
                }
            )
            if sidecar_kind == "metadata":
                selected, metadata_issues = safe_metadata(sidecar)
                metadata.update(selected)
                for message in metadata_issues:
                    issues.append(
                        {"level": "warning", "asset": relative, "message": message}
                    )

        mapped = source_map.get(relative, {})
        source_url = str(mapped.get("source_url") or metadata.pop("source_url", "")).strip()
        if source_url:
            source_url = validate_source_url(source_url, relative)
        rights_basis = str(mapped.get("rights_basis") or args.rights_basis)
        if rights_basis not in RIGHTS_BASES:
            raise ResearchIngestError(
                f"Invalid rights_basis for {relative}: {rights_basis}"
            )
        rights_note = str(mapped.get("rights_note") or args.rights_note or "").strip()
        if not source_url:
            issues.append(
                {
                    "level": "warning",
                    "asset": relative,
                    "message": "No canonical source URL was found; add it before citing this sample.",
                }
            )
        technical = None
        if kind in {"video", "audio"}:
            technical, probe_issue = probe_media(path, ffprobe)
            if probe_issue:
                issues.append(
                    {"level": "warning", "asset": relative, "message": probe_issue}
                )
        record = {
            "reference_id": f"REF-{index:04d}",
            "kind": kind,
            "path": relative,
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "source_url": source_url or None,
            "source_metadata": metadata,
            "technical_metadata": technical,
            "sidecars": sorted(sidecars, key=lambda item: (item["kind"], item["path"])),
            "rights": {
                "basis": rights_basis,
                "note": rights_note,
                "user_declared": True,
                "reuse_allowed": rights_basis != "research-only",
                "verification_required": True,
            },
        }
        records.append(record)

    return {
        "schema_version": 1,
        "collection_title": str(args.collection_title).strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "accessed_at": accessed_at,
        "source_workflow": "OmniGet/manual authorized export; read-only PCV ingest",
        "input_directory": str(input_dir),
        "ffprobe": ffprobe,
        "records": records,
        "issues": issues,
        "research_boundary": {
            "purpose": (
                "Study explainable mechanisms and evidence. Do not re-edit, republish, "
                "or imitate protected expression without separate rights."
            ),
            "credentials_retained": False,
            "direct_media_urls_retained": False,
            "downloads_performed_by_this_script": False,
        },
        "recommended_next_steps": [
            "Use media_inventory.py and shot_detect.py for technical/shot structure.",
            "Generate contact sheets and transcripts with source timecodes.",
            "Use moment_ground.py only for approved local media when semantic event timing matters.",
            "Write reference cards that separate observation, inference, and transferable mechanism.",
            "Create an originality map before drafting the new script.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read an authorized OmniGet/export folder and build a provenance-first "
            "research manifest without downloading or modifying source files."
        )
    )
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output", required=True, help="New research manifest JSON.")
    parser.add_argument("--collection-title", required=True)
    parser.add_argument("--rights-basis", required=True, choices=sorted(RIGHTS_BASES))
    parser.add_argument("--rights-note")
    parser.add_argument(
        "--source-map",
        help=(
            "Optional JSON map keyed by relative asset path with source_url, "
            "rights_basis, and rights_note overrides."
        ),
    )
    parser.add_argument("--accessed-at", help="YYYY-MM-DD; defaults to today.")
    parser.add_argument("--config", help="Explicit PCV .env.local path for FFprobe.")
    parser.add_argument("--ffprobe", help="Explicit FFprobe executable override.")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        output = expand_path(args.output)
        if output.exists():
            raise ResearchIngestError(f"Refusing to overwrite existing output: {output}")
        manifest = build_manifest(args)
        if args.dry_run:
            print(
                dump_json(
                    {
                        "output": str(output),
                        "record_count": len(manifest["records"]),
                        "issue_count": len(manifest["issues"]),
                        "kinds": sorted(
                            {record["kind"] for record in manifest["records"]}
                        ),
                        "downloads_performed": False,
                    }
                ),
                end="",
            )
            return 0
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as handle:
            handle.write(dump_json(manifest))
        print(f"Wrote {output} with {len(manifest['records'])} research record(s).")
        if manifest["issues"]:
            print(
                f"WARNING: {len(manifest['issues'])} issue(s) require review before citation."
            )
        return 0
    except (ConfigError, ResearchIngestError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
