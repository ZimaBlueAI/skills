"""Light Soft Studio timeline — cut / stretch / speed / copy-paste / add-remove.

Slim editorial model inspired by zima-anima timeline clips (no full ffmpeg render gate).
"""
from __future__ import annotations

import copy
import json
import secrets
import time
from pathlib import Path
from typing import Any

import material_store
import review_desk

SCHEMA = "zima-anima-light/timeline/1"
DEFAULT_IMAGE_DUR = 3.0
DEFAULT_VIDEO_DUR = 5.0
DEFAULT_AUDIO_DUR = 5.0


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _uid(prefix: str = "CL") -> str:
    return f"{prefix}-{secrets.token_hex(3)}"


def timeline_path(project: Path) -> Path:
    return project / "editorial" / "timeline.json"


def empty_timeline() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "fps": 24,
        "playhead": 0.0,
        "zoom": 48.0,  # px per second in UI
        "clips": [],
        "clipboard": None,
        "history": [],
        "updated_at": _now(),
    }


def load_timeline(project: Path) -> dict[str, Any]:
    path = timeline_path(project)
    if not path.is_file():
        return empty_timeline()
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("schema", SCHEMA)
    data.setdefault("fps", 24)
    data.setdefault("playhead", 0.0)
    data.setdefault("zoom", 48.0)
    data.setdefault("clips", [])
    data.setdefault("clipboard", None)
    data.setdefault("history", [])
    return data


def save_timeline(project: Path, data: dict[str, Any], *, note: str = "") -> dict[str, Any]:
    (project / "editorial").mkdir(parents=True, exist_ok=True)
    if note:
        if note not in ("undo","redo"):
            previous=load_timeline(project)
            if previous.get("clips")!=data.get("clips"):
                stack=data.setdefault("undo",[])
                stack.append(previous.get("clips",[]))
                data["undo"]=stack[-20:]
                data["redo"]=[]
        data.setdefault("history", []).append({"note": note, "at": _now(), "clip_count": len(data.get("clips") or [])})
        data["history"] = data["history"][-40:]
    data["updated_at"] = _now()
    path = timeline_path(project)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    return data


def _round(t: float) -> float:
    return round(max(0.0, float(t)), 3)


def _source_duration(kind: str, meta: dict[str, Any] | None = None) -> float:
    if meta and meta.get("source_duration"):
        return float(meta["source_duration"])
    if kind == "image":
        return DEFAULT_IMAGE_DUR
    if kind == "audio":
        return DEFAULT_AUDIO_DUR
    return DEFAULT_VIDEO_DUR


def _pack(timeline: dict[str, Any]) -> dict[str, Any]:
    """Keep V1 clips contiguous from 0 without gaps (Light listicle style)."""
    clips = [c for c in (timeline.get("clips") or []) if (c.get("track") or "V1") == "V1"]
    cursor = 0.0
    for clip in clips:
        clip["start"] = _round(cursor)
        cursor = _round(cursor + float(clip.get("duration") or 0))
    others = [c for c in (timeline.get("clips") or []) if (c.get("track") or "V1") != "V1"]
    timeline["clips"] = clips + others
    return timeline


def total_duration(timeline: dict[str, Any]) -> float:
    end = 0.0
    for clip in timeline.get("clips") or []:
        end = max(end, float(clip.get("start") or 0) + float(clip.get("duration") or 0))
    return _round(end)


def snapshot(project: Path) -> dict[str, Any]:
    tl = load_timeline(project)
    tl["can_undo"]=bool(tl.pop("undo",[]))
    tl["can_redo"]=bool(tl.pop("redo",[]))
    return {
        "timeline": tl,
        "duration": total_duration(tl),
        "clip_count": len(tl.get("clips") or []),
    }


def _find_clip(timeline: dict[str, Any], clip_id: str) -> dict[str, Any]:
    for clip in timeline.get("clips") or []:
        if clip.get("id") == clip_id:
            return clip
    raise FileNotFoundError(clip_id)


def restore_edit(project, action):
    tl=load_timeline(project)
    stack=tl.get(action) or []
    if not stack: raise ValueError("没有可恢复的编辑")
    tl.setdefault("redo" if action=="undo" else "undo",[]).append(tl["clips"])
    tl["clips"]=stack.pop()
    tl["playhead"]=min(tl["playhead"],total_duration(tl))
    save_timeline(project,tl,note=action)
    return snapshot(project)


def mix_clip(project,clip_id,volume,muted):
    tl=load_timeline(project)
    clip=_find_clip(tl,clip_id)
    if volume is not None:
        volume=float(volume)
        if not 0<=volume<=1: raise ValueError("音量超出范围")
        clip["volume"]=volume
    if muted is not None: clip["muted"]=bool(muted)
    save_timeline(project,tl,note=f"mix {clip_id}")
    return {"clip":clip,**snapshot(project)}


def add_clip(
    project: Path,
    *,
    asset_id: str | None = None,
    path: str | None = None,
    kind: str | None = None,
    title: str | None = None,
    duration: float | None = None,
    track: str = "V1",
    start: float = 0.0,
    source_duration: float | None = None,
    after_id: str | None = None,
    note: str = "add",
) -> dict[str, Any]:
    tl = load_timeline(project)
    meta: dict[str, Any] = {}
    if asset_id:
        try:
            meta = material_store.get_material(project, asset_id)
        except FileNotFoundError:
            meta = {}
        path = path or meta.get("file")
        kind = kind or meta.get("media_kind") or "image"
        title = title or meta.get("title") or asset_id
    if not path:
        raise ValueError("path or asset_id with file required")
    kind = kind or "image"
    src_dur = float(source_duration) if source_duration is not None else _source_duration(kind, meta)
    if not 0<src_dur<float("inf"):raise ValueError("无效的素材时长")
    dur = _round(duration if duration is not None else src_dur)
    clip = {
        "id": _uid(),
        "asset_id": asset_id,
        "title": title or Path(path).stem,
        "path": str(path).replace("\\", "/"),
        "kind": kind,
        "track": track,
        "start": _round(start),
        "duration": dur,
        "in_point": 0.0,
        "out_point": dur if kind != "image" else src_dur,
        "speed": 1.0,
        "source_duration": src_dur,
        "scale": 1.0,
    }
    clips = list(tl.get("clips") or [])
    if after_id:
        idx = next((i for i, c in enumerate(clips) if c.get("id") == after_id), len(clips) - 1)
        clips.insert(idx + 1, clip)
    else:
        clips.append(clip)
    tl["clips"] = clips
    _pack(tl)
    save_timeline(project, tl, note=note)
    return {"clip": clip, **snapshot(project)}


def add_from_approved(project: Path, *, limit: int = 24) -> dict[str, Any]:
    """Seed / append clips from review-approved (or current) materials."""
    snap = review_desk.snapshot(project, refresh=True)
    selected = snap.get("selected") or {}
    added = []
    existing_assets = {c.get("asset_id") for c in load_timeline(project).get("clips") or []}
    for asset_id, row in list(selected.items())[:limit]:
        if asset_id in existing_assets:
            continue
        result = add_clip(
            project,
            asset_id=asset_id,
            path=row.get("path"),
            kind=row.get("kind"),
            title=row.get("title"),
            note="add-from-review",
        )
        added.append(result["clip"]["id"])
        existing_assets.add(asset_id)
    # If nothing approved yet, take current image materials on assets stage.
    if not added:
        mats = material_store.list_materials(project)
        for asset_id, meta in mats.items():
            if asset_id in existing_assets:
                continue
            if not meta.get("file"):
                continue
            if meta.get("media_kind") not in {None, "image", "video"}:
                continue
            result = add_clip(
                project,
                asset_id=asset_id,
                path=meta.get("file"),
                kind=meta.get("media_kind") or "image",
                title=meta.get("title") or asset_id,
                note="add-from-materials",
            )
            added.append(result["clip"]["id"])
            if len(added) >= min(limit, 8):
                break
    return {"added": added, **snapshot(project)}


def remove_clip(project: Path, clip_id: str) -> dict[str, Any]:
    tl = load_timeline(project)
    tl["clips"] = [c for c in (tl.get("clips") or []) if c.get("id") != clip_id]
    _pack(tl)
    save_timeline(project, tl, note=f"remove {clip_id}")
    return snapshot(project)


def split_clip(project: Path, clip_id: str, at: float) -> dict[str, Any]:
    """Split clip at absolute timeline time `at` (must fall inside clip)."""
    tl = load_timeline(project)
    clip = _find_clip(tl, clip_id)
    start = float(clip["start"])
    dur = float(clip["duration"])
    if not (start + 0.05 < at < start + dur - 0.05):
        raise ValueError("split point must be inside clip")
    left_dur = _round(at - start)
    right_dur = _round(dur - left_dur)
    speed = float(clip.get("speed") or 1.0) or 1.0
    src_consumed = _round(left_dur * speed)
    left = dict(clip)
    left["duration"] = left_dur
    left["out_point"] = _round(float(clip.get("in_point") or 0) + src_consumed)
    right = dict(clip)
    right["id"] = _uid()
    right["start"] = _round(at)
    right["duration"] = right_dur
    right["in_point"] = left["out_point"]
    right["out_point"] = clip.get("out_point")
    clips = list(tl.get("clips") or [])
    idx = next(i for i, c in enumerate(clips) if c.get("id") == clip_id)
    clips[idx] = left
    clips.insert(idx + 1, right)
    tl["clips"] = clips
    _pack(tl)
    save_timeline(project, tl, note=f"split {clip_id}")
    return {"left": left, "right": right, **snapshot(project)}


def set_speed(project: Path, clip_id: str, speed: float) -> dict[str, Any]:
    speed = float(speed)
    if not 0.05 < speed <= 8:
        raise ValueError("speed must be between 0.05 and 8")
    tl = load_timeline(project)
    clip = _find_clip(tl, clip_id)
    in_p = float(clip.get("in_point") or 0)
    out_p = float(clip.get("out_point") or clip.get("source_duration") or clip.get("duration") or 1)
    src_span = max(0.05, out_p - in_p)
    if clip.get("kind")=="image":
        src_span=float(clip["duration"])*float(clip.get("speed") or 1)
    clip["speed"] = _round(speed)
    clip["duration"] = _round(src_span / speed)
    _pack(tl)
    tl["playhead"]=min(float(tl.get("playhead") or 0),total_duration(tl))
    save_timeline(project, tl, note=f"speed {clip_id}={speed}")
    return {"clip": clip, **snapshot(project)}


def stretch_clip(project: Path, clip_id: str, duration: float, *, ripple: bool = True) -> dict[str, Any]:
    """Change timeline duration (stretch/scale). For image: pure duration; for av: adjusts speed."""
    duration = _round(duration)
    if duration < 0.1:
        raise ValueError("duration too short")
    tl = load_timeline(project)
    clip = _find_clip(tl, clip_id)
    kind = clip.get("kind") or "image"
    if kind == "image":
        clip["duration"] = duration
        clip["scale"] = _round(duration / float(clip.get("source_duration") or DEFAULT_IMAGE_DUR))
    else:
        in_p = float(clip.get("in_point") or 0)
        out_p = float(clip.get("out_point") or clip.get("source_duration") or duration)
        src_span = max(0.05, out_p - in_p)
        clip["duration"] = duration
        clip["speed"] = _round(src_span / duration)
        clip["scale"] = clip["speed"]
    if ripple:
        _pack(tl)
    save_timeline(project, tl, note=f"stretch {clip_id}")
    return {"clip": clip, **snapshot(project)}


def trim_clip(project: Path, clip_id: str, *, in_point: float | None = None, out_point: float | None = None) -> dict[str, Any]:
    tl = load_timeline(project)
    clip = _find_clip(tl, clip_id)
    src = float(clip.get("source_duration") or DEFAULT_VIDEO_DUR)
    inn = float(in_point if in_point is not None else clip.get("in_point") or 0)
    out = float(out_point if out_point is not None else clip.get("out_point") or src)
    if not 0 <= inn < out <= max(src,float(clip.get("out_point") or 0)) or out - inn < 0.1:
        raise ValueError("trim window too short")
    clip["in_point"] = _round(max(0.0, inn))
    clip["out_point"] = _round(out)
    speed = float(clip.get("speed") or 1.0) or 1.0
    clip["duration"] = _round((clip["out_point"] - clip["in_point"]) / speed)
    _pack(tl)
    save_timeline(project, tl, note=f"trim {clip_id}")
    return {"clip": clip, **snapshot(project)}


def move_clip(project: Path, clip_id: str, *, index: int) -> dict[str, Any]:
    tl = load_timeline(project)
    clips = list(tl.get("clips") or [])
    idx = next((i for i, c in enumerate(clips) if c.get("id") == clip_id), None)
    if idx is None:
        raise FileNotFoundError(clip_id)
    clip = clips.pop(idx)
    index = max(0, min(index, len(clips)))
    clips.insert(index, clip)
    tl["clips"] = clips
    _pack(tl)
    save_timeline(project, tl, note=f"move {clip_id}->{index}")
    return snapshot(project)


def copy_clip(project: Path, clip_id: str) -> dict[str, Any]:
    tl = load_timeline(project)
    clip = _find_clip(tl, clip_id)
    tl["clipboard"] = copy.deepcopy(clip)
    save_timeline(project, tl, note=f"copy {clip_id}")
    return {"clipboard": tl["clipboard"], **snapshot(project)}


def paste_clip(project: Path, *, after_id: str | None = None) -> dict[str, Any]:
    tl = load_timeline(project)
    blob = tl.get("clipboard")
    if not blob:
        raise ValueError("clipboard empty")
    clip = copy.deepcopy(blob)
    clip["id"] = _uid()
    clips = list(tl.get("clips") or [])
    if after_id:
        idx = next((i for i, c in enumerate(clips) if c.get("id") == after_id), len(clips) - 1)
        clips.insert(idx + 1, clip)
    else:
        clips.append(clip)
    tl["clips"] = clips
    _pack(tl)
    save_timeline(project, tl, note=f"paste {clip['id']}")
    return {"clip": clip, **snapshot(project)}


def set_playhead(project: Path, t: float) -> dict[str, Any]:
    tl = load_timeline(project)
    tl["playhead"] = _round(min(total_duration(tl), max(0.0, t)))
    save_timeline(project, tl)
    return snapshot(project)


def set_zoom(project: Path, zoom: float) -> dict[str, Any]:
    tl = load_timeline(project)
    tl["zoom"] = max(16.0, min(160.0, float(zoom)))
    save_timeline(project, tl)
    return snapshot(project)
