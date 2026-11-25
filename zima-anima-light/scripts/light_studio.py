#!/usr/bin/env python3
"""Loopback infinite-canvas studio for Zima Anima Light."""
from __future__ import annotations

import argparse
import json
import mimetypes
import re
import secrets
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, unquote

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))

import config_env
import edit_timeline
import export_cut
import material_store
import masters_catalog
import project_model
import review_desk
import story_collab
import youth_lookbook
from providers import catalog as provider_catalog
from providers import seedance, seedream
from providers import media_api, creative_chat, creative_context, work_queue
from workflow_defs import WORKFLOWS

UI_DIR = SKILL / "studio"
TOKEN = secrets.token_urlsafe(16)


def json_bytes(data: Any) -> bytes:
    return json.dumps(data, ensure_ascii=False).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    project: Path
    server_version = "ZimaAnimaLight/0.1"

    def log_message(self, fmt: str, *args) -> None:  # quieter default
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: bytes, content_type: str = "application/json; charset=utf-8") -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(str(exc)) from exc
        if not isinstance(data, dict):
            raise ValueError("JSON object required")
        return data

    def _media(self,file,mime):
        size=file.stat().st_size
        start,end=0,size-1
        header=self.headers.get("Range")
        if header:
            match=re.fullmatch(r"bytes=(\d*)-(\d*)",header.strip())
            if match and any(match.groups()):
                left,right=match.groups()
                start=int(left) if left else max(0,size-int(right))
                end=min(end,int(right)) if left and right else end
            else:
                start=size
            if start>end or start>=size:
                self.send_response(416)
                self.send_header("Content-Range",f"bytes */{size}")
                self.end_headers()
                return
        self.send_response(206 if header else 200)
        self.send_header("Content-Type",mime)
        self.send_header("Accept-Ranges","bytes")
        if header:self.send_header("Content-Range",f"bytes {start}-{end}/{size}")
        remaining=end-start+1
        self.send_header("Content-Length",str(remaining))
        self.end_headers()
        try:
            with file.open("rb") as src:
                src.seek(start)
                while remaining:
                    block=src.read(min(remaining,256*1024))
                    if not block:break
                    self.wfile.write(block)
                    remaining-=len(block)
        except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):
            pass

    def _auth_ok(self) -> bool:
        return self.headers.get("X-ZAL-Token") == TOKEN

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            html = (UI_DIR / "index.html").read_bytes()
            boot = (
                f"<script>window.ZAL_BOOT={json.dumps({'token': TOKEN, 'project': str(self.project)})};</script>"
            ).encode("utf-8")
            html = html.replace(b"<!--BOOT-->", boot)
            return self._send(200, html, "text/html; charset=utf-8")
        if path == "/api/media-services":
            return self._send(200, json_bytes(media_api.catalog()))
        if path == "/api/work-queue":
            return self._send(200, json_bytes(work_queue.listing(self.project)))
        if path.startswith("/static/"):
            rel = path[len("/static/") :]
            file = (UI_DIR / rel).resolve()
            if not str(file).startswith(str(UI_DIR.resolve())) or not file.is_file():
                return self._send(404, b'{"error":"not found"}')
            mime = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
            return self._send(200, file.read_bytes(), mime)
        if path.startswith("/masters/"):
            rel = path[len("/masters/") :]
            root = (SKILL / "masters").resolve()
            file = (root / rel).resolve()
            if not str(file).startswith(str(root)) or not file.is_file():
                return self._send(404, b'{"error":"not found"}')
            mime = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
            if file.suffix.lower() == ".svg":
                mime = "image/svg+xml; charset=utf-8"
            return self._send(200, file.read_bytes(), mime)
        if path.startswith("/media/"):
            rel = unquote(path[len("/media/") :])
            roots = [self.project]
            try:
                legacy = project_model.load_project(self.project).get("legacy") or {}
                source = Path(str(legacy.get("source_root") or ""))
                if legacy.get("source_root") and source.is_dir():
                    roots.append(source)
            except Exception:
                pass
            file = None
            for root in roots:
                candidate = (root / rel).resolve()
                if candidate.is_relative_to(root.resolve()) and candidate.is_file():
                    file = candidate
                    break
            if file is None:
                return self._send(404, b'{"error":"not found"}')
            mime = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
            return self._media(file,mime)
        if path == "/api/project":
            doc = project_model.load_project(self.project)
            local_mats = material_store.list_materials(self.project)
            merged = {**(doc.get("materials") or {}), **local_mats}
            canvas = doc.setdefault("canvas", {})
            if not canvas.get("materials") or not canvas.get("nodes"):
                layout = material_store.layout_positions(doc["nodes"], merged)
                canvas["nodes"] = layout["flow"]
                canvas["materials"] = layout["materials"]
                project_model.save_project(self.project, doc)
            doc = {**doc, "materials": merged}
            return self._send(200, json_bytes(doc))
        if path == "/api/capabilities":
            return self._send(200, json_bytes({"providers": provider_catalog.capabilities()}))
        if path == "/api/styles":
            packs = []
            for p in sorted((SKILL / "styles" / "packs").glob("*.json")):
                packs.append(json.loads(p.read_text(encoding="utf-8")))
            lookbook = youth_lookbook.load_lookbook()
            categories = sorted({
                str(x.get("category") or "general")
                for x in packs
                if x.get("category")
            })
            accents = [
                {"id": "soft_light", "title": "柔光"},
                {"id": "clear_faces", "title": "脸清楚"},
                {"id": "simple_bg", "title": "背景干净"},
                {"id": "warm_grade", "title": "暖调"},
                {"id": "cool_grade", "title": "冷调"},
                {"id": "miniature", "title": "微缩感"},
                {"id": "ink_edge", "title": "墨边"},
                {"id": "paper_cut", "title": "剪纸层"},
                {"id": "vertical_safe", "title": "竖屏安全"},
                {"id": "edu_clear", "title": "讲解清楚"},
            ]
            return self._send(200, json_bytes({
                "packs": packs,
                "accents": accents,
                "categories": categories,
                "lookbook_count": lookbook.get("count"),
                "style_count": lookbook.get("style_count"),
                "master_count": lookbook.get("master_count"),
            }))
        if path == "/api/lookbook":
            return self._send(200, json_bytes({"ok": True, **youth_lookbook.load_lookbook()}))
        if path == "/api/ui-themes":
            themes = json.loads((SKILL / "styles" / "ui_themes.json").read_text(encoding="utf-8"))
            return self._send(200, json_bytes({"themes": themes}))
        if path == "/api/masters":
            payload = masters_catalog.catalog_payload()
            return self._send(200, json_bytes({"ok": True, **payload}))
        if path.startswith("/api/masters/cover"):
            from urllib.parse import parse_qs
            qs = parse_qs(urlparse(self.path).query)
            mid = (qs.get("id") or [""])[0]
            try:
                data, mime = masters_catalog.cover_bytes_for(mid)
            except FileNotFoundError:
                return self._send(404, b'{"error":"not found"}')
            return self._send(200, data, mime)
        if path == "/api/workflows":
            return self._send(200, json_bytes({"workflows": list(WORKFLOWS)}))
        if path == "/api/story":
            return self._send(200, json_bytes({"ok": True, **story_collab.snapshot(self.project)}))
        if path == "/api/review":
            from urllib.parse import parse_qs
            qs = parse_qs(urlparse(self.path).query)
            refresh = (qs.get("refresh") or ["0"])[0] in {"1", "true", "yes"}
            return self._send(200, json_bytes({"ok": True, **review_desk.snapshot(self.project, refresh=refresh)}))
        if path == "/api/timeline":
            return self._send(200, json_bytes({"ok": True, **edit_timeline.snapshot(self.project)}))
        return self._send(404, b'{"error":"not found"}')

    timeline_lock = threading.RLock()

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path=="/api/timeline":
            with self.timeline_lock:
                return self._post()
        return self._post()

    def _post(self) -> None:
        if not self._auth_ok():
            return self._send(401, b'{"error":"unauthorized"}')
        path = urlparse(self.path).path
        try:
            body = self._read_json()
        except ValueError as exc:
            return self._send(400, json_bytes({"error": str(exc)}))
        doc = project_model.load_project(self.project)
        try:
            if path == "/api/canvas":
                camera = body.get("camera")
                nodes = body.get("nodes")
                materials = body.get("materials")
                if isinstance(camera, dict):
                    doc["canvas"]["camera"] = camera
                if isinstance(nodes, dict):
                    doc["canvas"]["nodes"] = nodes
                if isinstance(materials, dict):
                    doc["canvas"]["materials"] = materials
                if body.get("auto_layout"):
                    local = material_store.list_materials(self.project)
                    merged = {**(doc.get("materials") or {}), **local}
                    layout = material_store.layout_positions(doc["nodes"], merged)
                    doc["canvas"]["nodes"] = layout["flow"]
                    doc["canvas"]["materials"] = layout["materials"]
                project_model.save_project(self.project, doc)
                return self._send(200, json_bytes({"ok": True, "canvas": doc["canvas"]}))
            if path == "/api/approve":
                node = project_model.approve_node(doc, str(body.get("node") or ""), str(body.get("note") or ""))
                project_model.save_project(self.project, doc)
                return self._send(200, json_bytes({"ok": True, "node": node, "nodes": doc["nodes"]}))
            if path == "/api/material/create":
                asset_id = str(body.get("id") or "").strip()
                kind = str(body.get("kind") or "character")
                title = str(body.get("title") or asset_id)
                media_kind = str(body.get("media_kind") or "image")
                stage = str(body.get("stage") or "assets")
                if not asset_id:
                    raise ValueError("id required")
                record = material_store.ensure_material(
                    self.project, asset_id, kind, title, media_kind=media_kind, stage=stage,
                )
                doc.setdefault("materials", {})[asset_id] = {
                    "kind": kind,
                    "title": title,
                    "media_kind": media_kind,
                    "stage": stage,
                    "version": record.get("version") or 0,
                }
                layout = material_store.layout_positions(
                    doc["nodes"], {**doc["materials"], **material_store.list_materials(self.project)},
                )
                doc["canvas"]["nodes"] = layout["flow"]
                doc["canvas"]["materials"] = layout["materials"]
                project_model.save_project(self.project, doc)
                return self._send(200, json_bytes({"ok": True, "material": record, "canvas": doc["canvas"]}))
            if path == "/api/material/versions":
                asset_id = str(body.get("id") or "").strip()
                return self._send(200, json_bytes({
                    "ok": True,
                    "id": asset_id,
                    "versions": material_store.list_versions(self.project, asset_id),
                }))
            if path == "/api/material/restore":
                asset_id = str(body.get("id") or "").strip()
                version = int(body.get("version") or 0)
                record = material_store.restore_version(self.project, asset_id, version, note=str(body.get("note") or ""))
                return self._send(200, json_bytes({"ok": True, "material": record}))
            if path == "/api/material/stage":
                asset_id = str(body.get("id") or "").strip()
                stage = str(body.get("stage") or "").strip()
                record = material_store.set_stage(self.project, asset_id, stage)
                if asset_id in (doc.get("materials") or {}):
                    doc["materials"][asset_id]["stage"] = stage
                layout = material_store.layout_positions(
                    doc["nodes"], {**doc.get("materials", {}), **material_store.list_materials(self.project)},
                )
                doc["canvas"]["nodes"] = layout["flow"]
                doc["canvas"]["materials"] = layout["materials"]
                project_model.save_project(self.project, doc)
                return self._send(200, json_bytes({"ok": True, "material": record, "canvas": doc["canvas"]}))
            if path == "/api/work-queue":
                if body.get("message"):
                    message = work_queue.intent(self.project,str(body["message"])) or "请说出任务和顺序，例如「让任务 3 插队」。"
                else:
                    verb = body.get("action")
                    if verb=="approve" and body.get("approve_cost") is not True:
                        raise ValueError("请确认本项任务的 API 费用")
                    ok=work_queue.action(self.project,int(body["id"]),verb)
                    message="队列已更新。" if ok else "任务状态已变化，请查看最新队列。"
                return self._send(200,json_bytes({"message":message}))
            if path == "/api/export-cut":
                return self._send(200,json_bytes(export_cut.render(self.project,doc,body.get("aspect","landscape"))))
            if path == "/api/creative-chat":
                try:
                    reply = creative_chat.handle(self.project, doc, body)
                except Exception:
                    reply = {"session":body.get("session"),"message":"创作服务暂时未能完成请求，请稍后再试。"}
                return self._send(200, json_bytes(reply))
            if path == "/api/media-services":
                if body.get("approve_cost") is not True or not isinstance(body.get("payload"), dict):
                    raise ValueError("请确认请求参数与调用费用")
                result = media_api.submit(body["service"], body["payload"], self.project)
                return self._send(200, json_bytes(result))
            if path == "/api/generate/image":
                if body.get("approve_cost") is not True:
                    raise ValueError("approve_cost required for live or dry-run planning")
                prompt = str(body.get("prompt") or "").strip()
                if not prompt:
                    raise ValueError("prompt required")
                dry = bool(body.get("dry_run"))
                result = seedream.generate(prompt, size=str(body.get("size") or "1024x1024"), dry_run=dry)
                out_meta: dict[str, Any] = {"provider": "seedream", "dry_run": dry}
                if not dry:
                    asset_id = str(body.get("asset_id") or "IMG-GEN")
                    material_store.ensure_material(self.project, asset_id, "still", asset_id)
                    dest = self.project / "exports" / f"{asset_id}-{secrets.token_hex(4)}.png"
                    seedream.write_image(result, dest)
                    record = material_store.add_version(self.project, asset_id, dest, note=prompt[:120])
                    out_meta["material"] = record
                    out_meta["file"] = record["file"]
                else:
                    out_meta["plan"] = result
                return self._send(200, json_bytes({"ok": True, **out_meta}))
            if path == "/api/generate/video":
                if body.get("approve_cost") is not True:
                    raise ValueError("approve_cost required")
                prompt = str(body.get("prompt") or "").strip()
                if not prompt:
                    raise ValueError("prompt required")
                dry = bool(body.get("dry_run", True))
                result = seedance.submit(prompt, image_url=body.get("image_url"), dry_run=dry)
                return self._send(200, json_bytes({"ok": True, "result": result}))
            if path == "/api/story":
                action = str(body.get("action") or "save").strip()
                author = str(body.get("author") or doc.get("masters", {}).get("director") or "studio")
                if action == "save":
                    text = str(body.get("text") or "")
                    result = story_collab.write_story(
                        self.project, text, note=str(body.get("note") or "edit"), author=author,
                    )
                    for node in doc["nodes"]:
                        if node["id"] == "story" and node["status"] == "locked":
                            node["status"] = "ready"
                    project_model.save_project(self.project, doc)
                    return self._send(200, json_bytes({"ok": True, "file": "boards/story.md", **result}))
                if action == "annotate":
                    item = story_collab.add_annotation(
                        self.project,
                        kind=str(body.get("kind") or "note"),
                        body=str(body.get("body") or ""),
                        quote=str(body.get("quote") or ""),
                        start=body.get("start"),
                        end=body.get("end"),
                        author=author,
                        suggestion=str(body.get("suggestion") or ""),
                        anchor=body.get("anchor"),
                    )
                    return self._send(200, json_bytes({"ok": True, "annotation": item, **story_collab.snapshot(self.project)}))
                if action == "comment":
                    item = story_collab.add_comment(
                        self.project,
                        body=str(body.get("body") or ""),
                        author=author,
                        target=body.get("target"),
                        anchor=body.get("anchor"),
                    )
                    return self._send(200, json_bytes({"ok": True, "comment": item, **story_collab.snapshot(self.project)}))
                if action == "resolve":
                    item = story_collab.set_feedback_status(
                        self.project,
                        feedback_id=str(body.get("id") or ""),
                        status=str(body.get("status") or "resolved"),
                        author=author,
                    )
                    return self._send(200, json_bytes({"ok": True, "item": item, **story_collab.snapshot(self.project)}))
                if action == "iterate":
                    draft = story_collab.build_iteration_draft(
                        self.project, author=author, note=str(body.get("note") or ""),
                    )
                    return self._send(200, json_bytes({"ok": True, "draft": draft, **story_collab.snapshot(self.project)}))
                if action == "apply_draft":
                    result = story_collab.apply_draft(
                        self.project,
                        text=body.get("text"),
                        accept_feedback=bool(body.get("accept_feedback", True)),
                        author=author,
                    )
                    for node in doc["nodes"]:
                        if node["id"] == "story" and node["status"] == "locked":
                            node["status"] = "ready"
                    project_model.save_project(self.project, doc)
                    return self._send(200, json_bytes({"ok": True, **result}))
                if action == "discard_draft":
                    collab = story_collab.discard_draft(self.project, author=author)
                    return self._send(200, json_bytes({"ok": True, "collab": collab, **story_collab.snapshot(self.project)}))
                raise ValueError(f"unknown story action: {action}")
            if path == "/api/review":
                action = str(body.get("action") or "decide").strip()
                author = str(body.get("author") or doc.get("masters", {}).get("director") or "studio")
                if action == "refresh":
                    review_desk.sync_catalog(self.project)
                    return self._send(200, json_bytes({"ok": True, **review_desk.snapshot(self.project)}))
                if action == "decide":
                    result = review_desk.decide(
                        self.project,
                        item_id=str(body.get("id") or ""),
                        decision=str(body.get("decision") or ""),
                        comment=str(body.get("comment") or ""),
                        cause=body.get("cause"),
                        sha256=body.get("sha256"),
                        previous_event_id=body.get("previous_event_id"),
                        actor=author,
                        bind_on_approve=bool(body.get("bind_on_approve", True)),
                    )
                    return self._send(200, json_bytes({"ok": True, **result}))
                raise ValueError(f"unknown review action: {action}")
            if path == "/api/timeline":
                action = str(body.get("action") or "snapshot").strip()
                if action in {"snapshot", "get"}:
                    return self._send(200, json_bytes({"ok": True, **edit_timeline.snapshot(self.project)}))
                if action in {"seed", "add_from_approved"}:
                    result = edit_timeline.add_from_approved(
                        self.project, limit=int(body.get("limit") or 24),
                    )
                    return self._send(200, json_bytes({"ok": True, **result}))
                if action == "add":
                    result = edit_timeline.add_clip(
                        self.project,
                        asset_id=body.get("asset_id"),
                        path=body.get("path"),
                        kind=body.get("kind"),
                        title=body.get("title"),
                        duration=body.get("duration"),
                        track=str(body.get("track") or "V1"),
                        start=float(body.get("start") or 0),
                        source_duration=body.get("source_duration"),
                        after_id=body.get("after_id"),
                    )
                    return self._send(200, json_bytes({"ok": True, **result}))
                if action == "remove":
                    result = edit_timeline.remove_clip(self.project, str(body.get("clip_id") or ""))
                    return self._send(200, json_bytes({"ok": True, **result}))
                if action == "split":
                    result = edit_timeline.split_clip(
                        self.project,
                        str(body.get("clip_id") or ""),
                        float(body.get("at") if body.get("at") is not None else body.get("playhead") or 0),
                    )
                    return self._send(200, json_bytes({"ok": True, **result}))
                if action == "speed":
                    result = edit_timeline.set_speed(
                        self.project, str(body.get("clip_id") or ""), float(body.get("speed") or 1),
                    )
                    return self._send(200, json_bytes({"ok": True, **result}))
                if action in ("undo","redo"):
                    return self._send(200,json_bytes(edit_timeline.restore_edit(self.project,action)))
                if action=="mix":
                    return self._send(200,json_bytes(edit_timeline.mix_clip(self.project,body["clip_id"],body.get("volume"),body.get("muted"))))
                if action in {"stretch", "scale"}:
                    result = edit_timeline.stretch_clip(
                        self.project,
                        str(body.get("clip_id") or ""),
                        float(body.get("duration") or 1),
                        ripple=bool(body.get("ripple", True)),
                    )
                    return self._send(200, json_bytes({"ok": True, **result}))
                if action == "trim":
                    result = edit_timeline.trim_clip(
                        self.project,
                        str(body.get("clip_id") or ""),
                        in_point=body.get("in_point"),
                        out_point=body.get("out_point"),
                    )
                    return self._send(200, json_bytes({"ok": True, **result}))
                if action == "move":
                    result = edit_timeline.move_clip(
                        self.project, str(body.get("clip_id") or ""), index=int(body.get("index") or 0),
                    )
                    return self._send(200, json_bytes({"ok": True, **result}))
                if action == "copy":
                    result = edit_timeline.copy_clip(self.project, str(body.get("clip_id") or ""))
                    return self._send(200, json_bytes({"ok": True, **result}))
                if action == "paste":
                    result = edit_timeline.paste_clip(self.project, after_id=body.get("after_id"))
                    return self._send(200, json_bytes({"ok": True, **result}))
                if action == "playhead":
                    result = edit_timeline.set_playhead(self.project, float(body.get("t") or 0))
                    return self._send(200, json_bytes({"ok": True, **result}))
                if action == "zoom":
                    result = edit_timeline.set_zoom(self.project, float(body.get("zoom") or 48))
                    return self._send(200, json_bytes({"ok": True, **result}))
                raise ValueError(f"unknown timeline action: {action}")
            if path == "/api/scene-notes":
                scope=str(body.get("scope") or "全片").strip().upper()
                if scope!="全片" and creative_context.scene_id(scope)!=scope:
                    raise ValueError("请输入场次，例如 S01 或 第一场")
                notes={k:str(body.get(k,"")).strip()[:800] for k in ("人物与服装","动作与道具","光线与声音")}
                doc.setdefault("continuity",{}).setdefault("notebook",{})[scope]=notes
                project_model.save_project(self.project,doc)
                return self._send(200,json_bytes({"scope":scope,"notes":notes}))
            if path == "/api/continuity":
                shot = str(body.get("shot") or "").strip()
                if not shot:
                    raise ValueError("shot required")
                doc.setdefault("continuity", {}).setdefault("shots", {})[shot] = body.get("state") or {}
                project_model.save_project(self.project, doc)
                return self._send(200, json_bytes({"ok": True, "continuity": doc["continuity"]}))
            if path == "/api/style":
                pack = str(body.get("pack") or "").strip()
                if pack:
                    doc["style_pack"] = pack
                if "accents" in body:
                    accents = body.get("accents") or []
                    if not isinstance(accents, list):
                        raise ValueError("accents must be a list")
                    doc["style_accents"] = [str(a) for a in accents][:12]
                if body.get("ui_theme"):
                    doc["ui_theme"] = str(body.get("ui_theme")).strip()
                project_model.save_project(self.project, doc)
                return self._send(200, json_bytes({
                    "ok": True,
                    "style_pack": doc.get("style_pack"),
                    "style_accents": doc.get("style_accents") or [],
                    "ui_theme": doc.get("ui_theme"),
                }))
            if path == "/api/masters":
                masters = doc.setdefault("masters", {})
                for role in masters_catalog.CREATIVE_ROLES:
                    if body.get(role):
                        masters[role] = str(body.get(role)).strip()
                project_model.save_project(self.project, doc)
                return self._send(200, json_bytes({"ok": True, "masters": masters}))
            if path == "/api/setup":
                # Batch save look-node choices (style + accents + theme + masters).
                if body.get("style_pack"):
                    doc["style_pack"] = str(body["style_pack"]).strip()
                if "style_accents" in body:
                    accents = body.get("style_accents") or []
                    if not isinstance(accents, list):
                        raise ValueError("style_accents must be a list")
                    doc["style_accents"] = [str(a) for a in accents][:12]
                if body.get("ui_theme"):
                    doc["ui_theme"] = str(body["ui_theme"]).strip()
                masters = doc.setdefault("masters", {})
                incoming = body.get("masters") if isinstance(body.get("masters"), dict) else body
                for role in masters_catalog.CREATIVE_ROLES:
                    if incoming.get(role):
                        masters[role] = str(incoming.get(role)).strip()
                project_model.save_project(self.project, doc)
                return self._send(200, json_bytes({
                    "ok": True,
                    "style_pack": doc.get("style_pack"),
                    "style_accents": doc.get("style_accents") or [],
                    "ui_theme": doc.get("ui_theme"),
                    "masters": masters,
                }))
        except Exception as exc:  # noqa: BLE001 — surface to UI
            return self._send(400, json_bytes({"error": str(exc)}))
        return self._send(404, b'{"error":"not found"}')


def serve(project: Path, *, host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True) -> int:
    config_env.load_env()
    project_model.load_project(project)
    Handler.project = project.resolve()
    httpd = ThreadingHTTPServer((host, port), Handler)
    work_queue.start(Handler.project)
    url = f"http://{host}:{port}/"
    print(f"Zima Anima Light studio: {url}")
    print(f"project: {Handler.project}")
    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Zima Anima Light studio server")
    parser.add_argument("project")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)
    return serve(Path(args.project), host=args.host, port=args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    raise SystemExit(main())
