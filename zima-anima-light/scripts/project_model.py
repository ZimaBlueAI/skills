"""Project init / load / save for Zima Anima Light."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from workflow_defs import WORKFLOWS, build_nodes, ensure_look_node
from masters_catalog import DEFAULT_MASTERS

SCHEMA = "zima-anima-light/project/1"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def project_path(root: Path) -> Path:
    return root / "project.json"


def init_project(
    root: Path,
    *,
    title: str,
    workflow: str,
    style_pack: str = "warm_school",
) -> dict[str, Any]:
    if workflow not in WORKFLOWS:
        raise ValueError(f"workflow must be one of {WORKFLOWS}")
    root.mkdir(parents=True, exist_ok=True)
    (root / "materials").mkdir(exist_ok=True)
    (root / "exports").mkdir(exist_ok=True)
    (root / "boards").mkdir(exist_ok=True)
    (root / "takes").mkdir(exist_ok=True)
    doc = {
        "schema": SCHEMA,
        "title": title.strip() or "未命名短片",
        "workflow": workflow,
        "mode": "guided",
        "audience": "youth",
        "budget": {"currency": "CNY", "limit": 50, "spent": 0},
        "nodes": build_nodes(workflow),
        "materials": {},
        "continuity": {"shots": {}},
        "canvas": {
            "camera": {"x": 40, "y": 40, "scale": 1},
            "nodes": {},
        },
        "style_pack": style_pack,
        "style_accents": [],
        "ui_theme": "soft_classic",
        "masters": dict(DEFAULT_MASTERS),
        "approvals": [],
        "created_at": _now(),
        "updated_at": _now(),
    }
    # place workflow cards on canvas (vertical Soft Studio layout)
    for i, node in enumerate(doc["nodes"]):
        doc["canvas"]["nodes"][node["id"]] = {
            "x": 72,
            "y": 64 + i * 220,
            "w": 230,
            "h": 118,
        }
    save_project(root, doc)
    readme = root / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# {doc['title']}\n\nworkflow: `{workflow}`\n\n打开：`python -B <skill>/scripts/light_cli.py serve .`\n",
            encoding="utf-8",
        )
    return doc


def load_project(root: Path) -> dict[str, Any]:
    path = project_path(root)
    if not path.is_file():
        raise FileNotFoundError(f"Missing project.json: {path}")
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("schema") != SCHEMA:
        raise ValueError("Unsupported project schema")
    changed = False
    nodes = ensure_look_node(list(doc.get("nodes") or []))
    if nodes is not doc.get("nodes") and [n.get("id") for n in nodes] != [n.get("id") for n in (doc.get("nodes") or [])]:
        doc["nodes"] = nodes
        changed = True
    doc.setdefault("style_accents", [])
    doc.setdefault("ui_theme", "soft_classic")
    masters = doc.setdefault("masters", {})
    for role, name in DEFAULT_MASTERS.items():
        if not masters.get(role) or (role=="supervisor" and masters[role]!=name):
            masters[role]=name
            changed=True
    canvas_nodes = doc.setdefault("canvas", {}).setdefault("nodes", {})
    if "look" not in canvas_nodes:
        # shift existing cards down one row if look was injected
        for key, box in list(canvas_nodes.items()):
            if isinstance(box, dict) and "y" in box:
                box["y"] = int(box["y"]) + 220
        canvas_nodes["look"] = {"x": 72, "y": 64, "w": 230, "h": 118}
        changed = True
    if changed:
        save_project(root, doc)
    return doc


def save_project(root: Path, doc: dict[str, Any]) -> None:
    doc["updated_at"] = _now()
    path = project_path(root)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def approve_node(doc: dict[str, Any], node_id: str, note: str = "") -> dict[str, Any]:
    from workflow_defs import unlock_after

    for node in doc["nodes"]:
        if node["id"] == node_id:
            if node["status"] not in {"ready", "in_progress", "approved"}:
                raise ValueError(f"Node {node_id} is {node['status']}")
            node["status"] = "approved"
            node["notes"] = note
            unlock_after(doc["nodes"], node_id)
            doc.setdefault("approvals", []).append({
                "node": node_id,
                "note": note,
                "at": _now(),
            })
            return node
    raise KeyError(node_id)
