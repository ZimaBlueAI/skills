"""Wrap a full zima-anima / PCV project as a Light review shell (non-destructive)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import project_model

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv"}
AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".aac", ".flac"}
MEDIA_EXTS = IMAGE_EXTS | VIDEO_EXTS | AUDIO_EXTS
PREVIEW_HINTS = (
    "master", "portrait", "ref", "main", "sheet", "character",
    "lock", "face", "hero", "key", "cover", "still",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _score_preview(path: Path) -> tuple[int, int, str]:
    name = path.name.lower()
    hint = 0
    for token in PREVIEW_HINTS:
        if token in name:
            hint += 4
    depth = len(path.parts)
    # Prefer shallow paths and common still formats.
    ext_bonus = 2 if path.suffix.lower() in {".png", ".webp"} else 0
    return (-hint - ext_bonus, depth, name)


def pick_preview_file(path: Path, *, media_kind: str = "image") -> Path | None:
    """Pick a representative media file from a file or folder."""
    if path.is_file():
        return path if path.suffix.lower() in MEDIA_EXTS else None
    if not path.is_dir():
        return None
    preferred = IMAGE_EXTS
    if media_kind == "video":
        preferred = VIDEO_EXTS
    elif media_kind == "audio":
        preferred = AUDIO_EXTS
    # Prefer files sitting directly in the folder, then recurse one level deep-ish.
    direct = [p for p in path.iterdir() if p.is_file() and p.suffix.lower() in preferred]
    if direct:
        return sorted(direct, key=_score_preview)[0]
    found: list[Path] = []
    for ext in preferred:
        found.extend(path.rglob(f"*{ext}"))
        if len(found) >= 40:
            break
    if not found and preferred is not IMAGE_EXTS:
        for ext in IMAGE_EXTS:
            found.extend(path.rglob(f"*{ext}"))
            if found:
                break
    if not found:
        return None
    # Prefer non-archive nested paths when possible.
    ranked = sorted(found, key=_score_preview)
    return ranked[0]


def detect_workflow(source: Path, full: dict[str, Any]) -> str:
    intake = full.get("intake") if isinstance(full.get("intake"), dict) else {}
    kind = str(intake.get("kind") or intake.get("input_kind") or "").lower()
    if "image" in kind or "still" in kind:
        return "from_image"
    if "music" in kind or "audio" in kind:
        return "from_music"
    if "video" in kind:
        return "from_video"
    if (source / "source").is_dir() and any((source / "source").glob("*.mp4")):
        return "from_video"
    return "from_story"


def summarize_legacy(source: Path) -> dict[str, Any]:
    full = _load_json(source / "project.json")
    storyboard = {}
    if (source / "storyboard.json").is_file():
        storyboard = _load_json(source / "storyboard.json")
    shots = storyboard.get("shots") or full.get("shots") or []
    characters = full.get("characters") or storyboard.get("assets") or {}
    return {
        "title": full.get("title") or storyboard.get("title") or source.name,
        "shot_count": len(shots) if isinstance(shots, list) else 0,
        "character_count": len(characters) if isinstance(characters, dict) else len(characters or []),
        "production_mode": full.get("production_mode"),
        "has_storyboard": bool(storyboard),
    }


def import_legacy(source: Path, dest: Path, *, workflow: str | None = None) -> dict[str, Any]:
    """Create a Light project.json that reviews `source` without modifying it."""
    source = source.resolve()
    if not (source / "project.json").is_file():
        raise FileNotFoundError(f"Not a zima project: {source}")
    full = _load_json(source / "project.json")
    summary = summarize_legacy(source)
    wf = workflow or detect_workflow(source, full)
    title = str(summary["title"])
    doc = project_model.init_project(dest, title=title, workflow=wf, style_pack="warm_school")
    # Re-open and enrich: init already wrote a fresh light project.
    doc = project_model.load_project(dest)
    doc["legacy"] = {
        "source_root": str(source),
        "source_title": title,
        "shot_count": summary["shot_count"],
        "character_count": summary["character_count"],
        "production_mode": summary["production_mode"],
        "note": "审验壳：只读引用完整片场工程，不改写源 project.json。",
    }
    evidence = {
        "look": "审验壳可重选软拟态界面、风格包与大师组合",
        "intake": "已有完整工程 intake",
        "story": "已有剧本/分镜工程",
        "assets": f"角色约 {summary['character_count']} 项",
        "continuity_lock": "完整版连续性可回查",
        "storyboard": f"分镜约 {summary['shot_count']} 镜，可在 Light 画布审验",
        "generate_stills": "可对照完整版关键帧",
        "edit": "可对照完整版剪辑台",
    }
    for node in doc["nodes"]:
        note = evidence.get(node["id"])
        if note:
            node["notes"] = note
            node["evidence"] = [note]
        if node["id"] in {"look", "intake", "story", "assets", "continuity_lock"}:
            node["status"] = "approved"
        elif node["id"] in {"storyboard", "generate_stills", "edit"}:
            node["status"] = "ready"
    doc["ui_theme"] = doc.get("ui_theme") or "soft_classic"
    doc["style_accents"] = doc.get("style_accents") or ["soft_light", "clear_faces"]
    # Seed material index from characters/scenes/audio/renders folders
    import material_store

    materials: dict[str, Any] = {}
    seeds = (
        ("characters", "character", "image", "assets"),
        ("scenes", "scene", "image", "assets"),
        ("props", "prop", "image", "assets"),
        ("concepts", "concept", "image", "assets"),
        ("boards", "storyboard", "image", "storyboard"),
        ("audio", "audio", "audio", "audio"),
        ("renders", "render", "video", "generate_video"),
        ("deliverables", "deliverable", "video", "deliver"),
    )
    for folder, kind, media_kind, stage in seeds:
        root = source / folder
        if not root.is_dir():
            continue
        count = 0
        for child in sorted(root.iterdir()):
            if count >= 12:
                break
            if child.name.startswith(".") or child.name.startswith("_"):
                continue
            preview = pick_preview_file(child, media_kind=media_kind)
            if preview is None and not child.is_dir():
                continue
            if preview is None and child.is_dir():
                # Keep empty shell only when folder looks like an asset id.
                if not any(ch.isalpha() for ch in child.name):
                    continue
            asset_id = (child.stem if child.is_file() else child.name)[:48]
            asset_id = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in asset_id) or f"{kind}-{count}"
            if asset_id in materials:
                asset_id = f"{asset_id}-{count}"
            record = material_store.ensure_material(
                dest, asset_id, kind, child.name, media_kind=media_kind, stage=stage,
            )
            if preview is not None and preview.is_file():
                try:
                    record = material_store.add_version(
                        dest, asset_id, preview, note=f"import preview from {folder}",
                    )
                except OSError:
                    # Fall back to source-relative path so canvas can still show the image.
                    rel = str(preview.relative_to(source)).replace("\\", "/")
                    record = material_store.set_file_ref(
                        dest, asset_id, rel, version=1, note=f"link preview from {folder}",
                    )
            materials[asset_id] = {
                "kind": kind,
                "title": child.name,
                "media_kind": media_kind,
                "stage": stage,
                "version": record.get("version") or 0,
                "file": record.get("file"),
                "legacy_path": str(child.relative_to(source)).replace("\\", "/"),
                "preview": record.get("file"),
            }
            count += 1
    doc["materials"] = materials
    layout = material_store.layout_positions(doc["nodes"], materials)
    doc["canvas"]["nodes"] = layout["flow"]
    doc["canvas"]["materials"] = layout["materials"]
    project_model.save_project(dest, doc)
    pointer = dest / "LEGACY-SOURCE.txt"
    pointer.write_text(f"{source}\n", encoding="utf-8")
    return doc
