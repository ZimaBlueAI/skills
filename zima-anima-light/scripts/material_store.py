"""Material versions with history (no overwrite of approved files)."""
from __future__ import annotations

import hashlib
import json
import shutil
import time
from pathlib import Path
from typing import Any

MEDIA_KINDS = ("image", "video", "audio", "document")


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def material_dir(project: Path, asset_id: str) -> Path:
    return project / "materials" / asset_id


def _write(record: dict[str, Any], project: Path, asset_id: str) -> dict[str, Any]:
    path = material_dir(project, asset_id) / "current.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


def ensure_material(
    project: Path,
    asset_id: str,
    kind: str,
    title: str,
    *,
    media_kind: str = "image",
    stage: str = "assets",
) -> dict[str, Any]:
    if media_kind not in MEDIA_KINDS:
        raise ValueError(f"media_kind must be one of {MEDIA_KINDS}")
    root = material_dir(project, asset_id)
    hist = root / "history"
    root.mkdir(parents=True, exist_ok=True)
    hist.mkdir(exist_ok=True)
    current = root / "current.json"
    if current.exists():
        record = json.loads(current.read_text(encoding="utf-8"))
        changed = False
        if not record.get("media_kind"):
            record["media_kind"] = media_kind
            changed = True
        if not record.get("stage"):
            record["stage"] = stage
            changed = True
        if changed:
            _write(record, project, asset_id)
        return record
    record = {
        "id": asset_id,
        "kind": kind,
        "media_kind": media_kind,
        "stage": stage,
        "title": title,
        "version": 0,
        "file": None,
        "sha256": None,
        "approved": False,
        "history": [],
        "updated_at": _now(),
    }
    return _write(record, project, asset_id)


def add_version(
    project: Path,
    asset_id: str,
    source: Path,
    *,
    note: str = "",
    approve: bool = False,
) -> dict[str, Any]:
    if not source.is_file():
        raise FileNotFoundError(source)
    root = material_dir(project, asset_id)
    current_path = root / "current.json"
    if not current_path.exists():
        raise FileNotFoundError(f"Unknown material: {asset_id}")
    record = json.loads(current_path.read_text(encoding="utf-8"))
    version = int(record.get("version") or 0) + 1
    ext = source.suffix.lower() or ".bin"
    dest_name = f"v{version:03d}{ext}"
    dest = root / dest_name
    shutil.copy2(source, dest)
    digest = sha256(dest)
    old_file = record.get("file")
    if old_file:
        old = root / Path(old_file).name
        if old.is_file():
            archived = root / "history" / f"{Path(old_file).stem}-before-v{version}{old.suffix}"
            if not archived.exists():
                shutil.copy2(old, archived)
            record.setdefault("history", []).append({
                "version": record.get("version"),
                "file": str(archived.relative_to(project)).replace("\\", "/"),
                "sha256": record.get("sha256"),
                "note": record.get("note") or "",
                "archived_at": _now(),
            })
    record.update({
        "version": version,
        "file": str(dest.relative_to(project)).replace("\\", "/"),
        "sha256": digest,
        "note": note,
        "approved": bool(approve),
        "updated_at": _now(),
    })
    return _write(record, project, asset_id)


def list_versions(project: Path, asset_id: str) -> list[dict[str, Any]]:
    record = get_material(project, asset_id)
    versions = list(record.get("history") or [])
    if record.get("version"):
        versions.append({
            "version": record["version"],
            "file": record.get("file"),
            "sha256": record.get("sha256"),
            "note": record.get("note") or "",
            "current": True,
            "approved": bool(record.get("approved")),
        })
    versions.sort(key=lambda item: int(item.get("version") or 0))
    return versions


def restore_version(project: Path, asset_id: str, version: int, *, note: str = "") -> dict[str, Any]:
    record = get_material(project, asset_id)
    target = None
    if int(record.get("version") or 0) == version and record.get("file"):
        return record
    for item in record.get("history") or []:
        if int(item.get("version") or 0) == version:
            target = item
            break
    if not target or not target.get("file"):
        raise FileNotFoundError(f"Version {version} not found for {asset_id}")
    source = project / target["file"]
    if not source.is_file():
        raise FileNotFoundError(source)
    return add_version(
        project,
        asset_id,
        source,
        note=note or f"restore v{version}",
        approve=False,
    )


def get_material(project: Path, asset_id: str) -> dict[str, Any]:
    path = material_dir(project, asset_id) / "current.json"
    if not path.is_file():
        raise FileNotFoundError(f"Unknown material: {asset_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def set_stage(project: Path, asset_id: str, stage: str) -> dict[str, Any]:
    record = get_material(project, asset_id)
    record["stage"] = stage
    record["updated_at"] = _now()
    return _write(record, project, asset_id)


def mark_approved(project: Path, asset_id: str, *, approved: bool = True, note: str = "") -> dict[str, Any]:
    record = get_material(project, asset_id)
    record["approved"] = bool(approved)
    if note:
        record["review_comment"] = note
    record["reviewed_at"] = _now()
    record["updated_at"] = _now()
    return _write(record, project, asset_id)


def set_file_ref(
    project: Path,
    asset_id: str,
    relative_file: str,
    *,
    version: int | None = None,
    note: str = "",
) -> dict[str, Any]:
    """Point current material at an existing relative path (no copy)."""
    record = get_material(project, asset_id)
    record["file"] = relative_file.replace("\\", "/")
    if version is not None:
        record["version"] = int(version)
    elif not record.get("version"):
        record["version"] = 1
    if note:
        record["note"] = note
    record["updated_at"] = _now()
    return _write(record, project, asset_id)


def list_materials(project: Path) -> dict[str, Any]:
    root = project / "materials"
    if not root.is_dir():
        return {}
    out = {}
    for child in sorted(root.iterdir()):
        cur = child / "current.json"
        if cur.is_file():
            out[child.name] = json.loads(cur.read_text(encoding="utf-8"))
    return out


def material_group_key(meta: dict[str, Any]) -> str:
    """Homogeneous stack key: same stage + same kind."""
    return str(meta.get("kind") or meta.get("media_kind") or "item")


def layout_positions(
    nodes: list[dict[str, Any]],
    materials: dict[str, Any],
    *,
    flow_x: int = 72,
    mat_x0: int = 340,
    row_h: int = 220,
    mat_w: int = 176,
    mat_h: int = 196,
    gap: int = 18,
    expanded: set[str] | None = None,
) -> dict[str, Any]:
    """Vertical flow; same-kind materials stack horizontally per stage.

    Collapsed (default): one column per kind stack.
    Expanded keys look like ``assets::character`` and fan members out.
    """
    flow: dict[str, dict[str, int]] = {}
    mats: dict[str, dict[str, int]] = {}
    stacks: dict[str, dict[str, Any]] = {}
    expanded = expanded or set()
    by_stage: dict[str, dict[str, list[str]]] = {n["id"]: {} for n in nodes}
    for asset_id, meta in materials.items():
        stage = str(meta.get("stage") or "assets")
        kind = material_group_key(meta)
        by_stage.setdefault(stage, {}).setdefault(kind, []).append(asset_id)
    for index, node in enumerate(nodes):
        y = 64 + index * row_h
        flow[node["id"]] = {"x": flow_x, "y": y, "w": 230, "h": 118}
        col = 0
        for kind, ids in by_stage.get(node["id"], {}).items():
            ids = sorted(ids)
            stack_id = f"{node['id']}::{kind}"
            stack_x = mat_x0 + col * (mat_w + gap)
            stacks[stack_id] = {
                "stage": node["id"],
                "kind": kind,
                "ids": ids,
                "x": stack_x,
                "y": y,
                "w": mat_w,
                "h": mat_h,
                "count": len(ids),
            }
            if len(ids) == 1 or stack_id in expanded:
                for offset, asset_id in enumerate(ids):
                    mats[asset_id] = {
                        "x": stack_x + offset * (mat_w + gap),
                        "y": y,
                        "w": mat_w,
                        "h": mat_h,
                        "stack": stack_id,
                    }
                col += max(len(ids), 1)
            else:
                # Collapsed: all members share the stack origin (UI peeks them).
                for asset_id in ids:
                    mats[asset_id] = {
                        "x": stack_x,
                        "y": y,
                        "w": mat_w,
                        "h": mat_h,
                        "stack": stack_id,
                        "stacked": True,
                    }
                col += 1
    return {"flow": flow, "materials": mats, "stacks": stacks, "row_h": row_h}
