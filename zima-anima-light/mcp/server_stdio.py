#!/usr/bin/env python3
"""Minimal JSON-lines MCP-like helper for Work agents (stdio)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(HERE))

import config_env
import project_model
import youth_lookbook
from providers import catalog as provider_catalog
from workflow_defs import ENTRY_FOCUS


def status(project_dir: str) -> dict:
    doc = project_model.load_project(Path(project_dir))
    ready = [n for n in doc["nodes"] if n["status"] == "ready"]
    return {
        "title": doc["title"],
        "workflow": doc["workflow"],
        "style_pack": doc.get("style_pack"),
        "masters": doc.get("masters"),
        "budget": doc.get("budget"),
        "ready_nodes": [n["id"] for n in ready],
        "approved": [n["id"] for n in doc["nodes"] if n["status"] == "approved"],
    }


def lookbook(item_id: str | None = None) -> dict:
    book = youth_lookbook.load_lookbook()
    if not item_id:
        return {
            "count": book.get("count"),
            "style_count": book.get("style_count"),
            "master_count": book.get("master_count"),
            "ids": [i.get("id") for i in (book.get("items") or [])],
        }
    needle = str(item_id).strip()
    for item in book.get("items") or []:
        if item.get("id") == needle or item.get("name") == needle:
            return {"ok": True, "item": item}
    return {"ok": False, "error": f"not found: {needle}"}


def next_step(project_dir: str) -> dict:
    doc = project_model.load_project(Path(project_dir))
    for node in doc["nodes"]:
        if node["status"] == "ready":
            return {"next": node["id"], "title": node["title"], "gate": node["gate"]}
    return {"next": None, "title": "全部完成或仍有锁定", "focus": ENTRY_FOCUS.get(doc["workflow"])}


def main() -> int:
    config_env.load_env()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        req = json.loads(line)
        name = req.get("tool")
        args = req.get("input") or {}
        try:
            if name == "light_project_status":
                out = status(args["project_dir"])
            elif name == "light_next_step":
                out = next_step(args["project_dir"])
            elif name == "light_capabilities":
                out = {"providers": provider_catalog.capabilities()}
            elif name == "light_lookbook":
                out = lookbook(args.get("id"))
            else:
                out = {"error": f"unknown tool {name}"}
        except Exception as exc:  # noqa: BLE001
            out = {"error": str(exc)}
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
