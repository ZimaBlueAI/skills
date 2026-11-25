"""选片 / 审片 desk for Light — slim PCV sequential-review pattern.

- catalog: version-locked media candidates from materials/
- decisions: append-only events (approved|rejected|deferred|archived)
- latest event per id wins; approve can bind material as approved
"""
from __future__ import annotations

import hashlib
import json
import secrets
import time
from pathlib import Path
from typing import Any

import material_store

SCHEMA = "zima-anima-light/review/1"
DECISIONS = ("approved", "rejected", "deferred", "archived")
REJECT_CAUSES = ("model", "keyframe", "prompt", "pipeline", "unclear")


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def review_dir(project: Path) -> Path:
    path = project / "review"
    path.mkdir(parents=True, exist_ok=True)
    return path


def catalog_path(project: Path) -> Path:
    return review_dir(project) / "catalog.json"


def decisions_path(project: Path) -> Path:
    return review_dir(project) / "decisions.json"


def empty_catalog() -> dict[str, Any]:
    return {"schema": SCHEMA, "items": [], "updated_at": _now()}


def empty_decisions() -> dict[str, Any]:
    return {"schema": SCHEMA, "events": [], "updated_at": _now()}


def _load_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.is_file():
        return dict(fallback)
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data: dict[str, Any]) -> dict[str, Any]:
    data["updated_at"] = _now()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    return data


def _item_id(asset_id: str, version: int, digest: str) -> str:
    raw = f"{asset_id}|v{version}|{digest}"
    return "R-" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def _kind_from_path(path: Path, media_kind: str | None = None) -> str:
    if media_kind in {"image", "video", "audio", "document"}:
        return media_kind
    ext = path.suffix.lower()
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return "image"
    if ext in {".mp4", ".mov", ".webm", ".mkv"}:
        return "video"
    if ext in {".wav", ".mp3", ".m4a", ".aac", ".flac"}:
        return "audio"
    return "document"


def sync_catalog(project: Path) -> dict[str, Any]:
    """Rebuild catalog from material versions (exact file fingerprints)."""
    items: list[dict[str, Any]] = []
    mats = material_store.list_materials(project)
    for asset_id, meta in mats.items():
        versions = material_store.list_versions(project, asset_id)
        for ver in versions:
            rel = ver.get("file")
            if not rel:
                continue
            file = project / rel
            if not file.is_file():
                # may be legacy source-relative
                continue
            digest = ver.get("sha256") or material_store.sha256(file)
            version = int(ver.get("version") or 0)
            items.append({
                "id": _item_id(asset_id, version, digest),
                "task": f"{meta.get('stage') or 'assets'}/{asset_id}",
                "title": meta.get("title") or asset_id,
                "asset_id": asset_id,
                "stage": meta.get("stage") or "assets",
                "version": version,
                "path": str(Path(rel).as_posix()),
                "sha256": digest,
                "kind": _kind_from_path(file, meta.get("media_kind")),
                "ready_for_review": True,
                "current": bool(ver.get("current")),
                "note": ver.get("note") or "",
            })
    items.sort(key=lambda it: (it.get("stage") or "", it.get("title") or "", int(it.get("version") or 0)))
    catalog = {"schema": SCHEMA, "items": items, "updated_at": _now()}
    return _save_json(catalog_path(project), catalog)


def load_catalog(project: Path, *, refresh: bool = False) -> dict[str, Any]:
    if refresh or not catalog_path(project).is_file():
        return sync_catalog(project)
    return _load_json(catalog_path(project), empty_catalog())


def load_decisions(project: Path) -> dict[str, Any]:
    return _load_json(decisions_path(project), empty_decisions())


def latest_by_id(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for ev in events:
        rid = ev.get("id")
        if rid:
            latest[str(rid)] = ev
    return latest


def snapshot(project: Path, *, refresh: bool = False) -> dict[str, Any]:
    catalog = load_catalog(project, refresh=refresh)
    decisions = load_decisions(project)
    latest = latest_by_id(list(decisions.get("events") or []))
    columns = {
        "unreviewed": [],
        "deferred": [],
        "approved": [],
        "rejected": [],
        "archived": [],
    }
    enriched = []
    for item in catalog.get("items") or []:
        ev = latest.get(item["id"])
        decision = (ev or {}).get("decision")
        row = {**item, "decision": decision, "latest_event": ev}
        enriched.append(row)
        if not decision:
            columns["unreviewed"].append(row)
        elif decision in columns:
            columns[decision].append(row)
        else:
            columns["unreviewed"].append(row)
    # Current selection per asset: latest approved version, else current file.
    selected: dict[str, dict[str, Any]] = {}
    for row in enriched:
        asset_id = row.get("asset_id")
        if not asset_id:
            continue
        if row.get("decision") == "approved":
            prev = selected.get(asset_id)
            if not prev or str((row.get("latest_event") or {}).get("at") or "") >= str((prev.get("latest_event") or {}).get("at") or ""):
                selected[asset_id] = row
    for row in enriched:
        asset_id = row.get("asset_id")
        if asset_id and asset_id not in selected and row.get("current"):
            selected[asset_id] = {**row, "decision": row.get("decision") or "current"}
    return {
        "catalog": catalog,
        "items": enriched,
        "columns": {k: [{"id": i["id"], "title": i["title"], "kind": i["kind"], "version": i["version"], "path": i["path"], "asset_id": i["asset_id"], "decision": i.get("decision")} for i in v] for k, v in columns.items()},
        "counts": {k: len(v) for k, v in columns.items()},
        "selected": selected,
        "events": list(decisions.get("events") or [])[-40:],
    }


def decide(
    project: Path,
    *,
    item_id: str,
    decision: str,
    comment: str = "",
    cause: str | None = None,
    sha256: str | None = None,
    previous_event_id: str | None = None,
    actor: str = "studio",
    bind_on_approve: bool = True,
) -> dict[str, Any]:
    if decision not in DECISIONS:
        raise ValueError(f"decision must be one of {DECISIONS}")
    if cause and cause not in REJECT_CAUSES:
        raise ValueError(f"cause must be one of {REJECT_CAUSES}")
    catalog = load_catalog(project)
    item = next((i for i in (catalog.get("items") or []) if i.get("id") == item_id), None)
    if not item:
        # refresh once in case new materials landed
        catalog = sync_catalog(project)
        item = next((i for i in (catalog.get("items") or []) if i.get("id") == item_id), None)
    if not item:
        raise FileNotFoundError(item_id)
    if sha256 and sha256 != item.get("sha256"):
        raise ValueError("sha256 mismatch — refresh catalog; this version changed")

    decisions = load_decisions(project)
    events = list(decisions.get("events") or [])
    latest = latest_by_id(events).get(item_id)
    if previous_event_id and latest and latest.get("event_id") != previous_event_id:
        raise ValueError("stale review state — reload and retry")

    event = {
        "id": item_id,
        "event_id": f"E-{secrets.token_hex(6)}",
        "task": item.get("task"),
        "title": item.get("title"),
        "path": item.get("path"),
        "sha256": item.get("sha256"),
        "media_sha256": item.get("sha256"),
        "kind": item.get("kind"),
        "asset_id": item.get("asset_id"),
        "version": item.get("version"),
        "decision": decision,
        "comment": (comment or "").strip(),
        "at": _now(),
        "source": "light_review_desk",
        "actor": actor,
    }
    if decision == "rejected":
        event["cause"] = cause or "unclear"
        event["cause_source"] = "user" if cause else "auto"
    events.append(event)
    decisions["events"] = events
    _save_json(decisions_path(project), decisions)

    # Mirror zima take_selection: approving a version marks material approved.
    if bind_on_approve and decision == "approved" and item.get("asset_id"):
        try:
            record = material_store.get_material(project, item["asset_id"])
            # If approved version is not current, restore it first.
            if int(record.get("version") or 0) != int(item.get("version") or 0):
                material_store.restore_version(
                    project, item["asset_id"], int(item["version"]), note=comment or "review approve",
                )
                record = material_store.get_material(project, item["asset_id"])
            material_store.mark_approved(
                project, item["asset_id"], approved=True, note=comment or "review approve",
            )
        except FileNotFoundError:
            pass

    return {"event": event, **snapshot(project)}


def repair_list(project: Path) -> list[dict[str, Any]]:
    snap = snapshot(project)
    return [row for row in snap["items"] if row.get("decision") == "rejected"]
