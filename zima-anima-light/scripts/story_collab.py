"""Story collaboration for Light — edit / annotate / comment / iterate.

Mirrors zima-anima patterns at a youth Soft Studio scale:
- authoritative script text in boards/story.md (versioned)
- beats + annotations + comments + decision_log in boards/story-collab.json
- draft-then-apply iteration from open feedback (no silent overwrite)
"""
from __future__ import annotations

import json
import re
import secrets
import shutil
import time
from pathlib import Path
from typing import Any

SCHEMA = "zima-anima-light/story-collab/1"
ANNOTATION_KINDS = ("note", "edit", "question")
FEEDBACK_STATUSES = ("open", "accepted", "dismissed", "resolved")


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _uid(prefix: str) -> str:
    return f"{prefix}-{secrets.token_hex(3)}"


def story_path(project: Path) -> Path:
    return project / "boards" / "story.md"


def collab_path(project: Path) -> Path:
    return project / "boards" / "story-collab.json"


def history_dir(project: Path) -> Path:
    path = project / "boards" / "history"
    path.mkdir(parents=True, exist_ok=True)
    return path


def empty_collab() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": 0,
        "beats": [],
        "annotations": [],
        "comments": [],
        "decision_log": [],
        "draft": None,
        "history": [],
        "updated_at": _now(),
    }


def load_collab(project: Path) -> dict[str, Any]:
    path = collab_path(project)
    if not path.is_file():
        return empty_collab()
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("schema", SCHEMA)
    data.setdefault("beats", [])
    data.setdefault("annotations", [])
    data.setdefault("comments", [])
    data.setdefault("decision_log", [])
    data.setdefault("draft", None)
    data.setdefault("history", [])
    return data


def save_collab(project: Path, data: dict[str, Any]) -> dict[str, Any]:
    (project / "boards").mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now()
    path = collab_path(project)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    return data


def read_story(project: Path) -> str:
    path = story_path(project)
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _snapshot(project: Path, text: str, *, note: str, collab: dict[str, Any]) -> dict[str, Any]:
    version = int(collab.get("version") or 0) + 1
    dest = history_dir(project) / f"story-v{version:03d}.md"
    dest.write_text(text, encoding="utf-8")
    entry = {
        "version": version,
        "file": str(dest.relative_to(project)).replace("\\", "/"),
        "note": note,
        "at": _now(),
    }
    collab.setdefault("history", []).append(entry)
    collab["version"] = version
    return entry


def write_story(
    project: Path,
    text: str,
    *,
    note: str = "edit",
    author: str = "studio",
    snapshot: bool = True,
) -> dict[str, Any]:
    (project / "boards").mkdir(parents=True, exist_ok=True)
    collab = load_collab(project)
    previous = read_story(project)
    if snapshot and previous.strip() and previous != text:
        _snapshot(project, previous, note=f"before:{note}", collab=collab)
    story_path(project).write_text(text, encoding="utf-8")
    if snapshot:
        entry = _snapshot(project, text, note=note, collab=collab)
    else:
        entry = {"version": collab.get("version") or 0, "note": note}
    record_decision(
        collab,
        category="story_edit",
        subject="boards/story.md",
        selected=f"v{collab.get('version') or 0}",
        reason=note,
        actor=author,
    )
    # Refresh beats from headings / numbered lines when empty or after major edit.
    if note.startswith("iterate") or not collab.get("beats"):
        collab["beats"] = extract_beats(text)
    save_collab(project, collab)
    return {"text": text, "version": collab.get("version") or 0, "history_entry": entry, "collab": collab}


def extract_beats(text: str) -> list[dict[str, Any]]:
    beats: list[dict[str, Any]] = []
    for line in text.splitlines():
        raw = line.strip()
        if not raw:
            continue
        m = re.match(r"^(?:#{1,3}\s+|第?[0-9一二三四五六七八九十]+[幕场节]\s*[:：.]?\s*|\d+[\.、]\s*)(.+)$", raw)
        if m:
            body = m.group(1).strip()
        elif raw.startswith("- ") or raw.startswith("* "):
            body = raw[2:].strip()
        else:
            continue
        if len(body) < 2:
            continue
        beats.append({
            "id": f"B{len(beats) + 1:02d}",
            "text": body[:240],
            "optional": False,
        })
        if len(beats) >= 40:
            break
    if not beats and text.strip():
        # Fallback: first non-empty paragraphs as beats.
        paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        for para in paras[:12]:
            beats.append({
                "id": f"B{len(beats) + 1:02d}",
                "text": para.splitlines()[0][:240],
                "optional": False,
            })
    return beats


def record_decision(
    collab: dict[str, Any],
    *,
    category: str,
    subject: str,
    selected: str,
    reason: str = "",
    actor: str = "studio",
    user_approved: bool = True,
) -> dict[str, Any]:
    log = collab.setdefault("decision_log", [])
    prior = None
    for item in reversed(log):
        if item.get("category") == category and item.get("subject") == subject:
            prior = item
            break
    entry: dict[str, Any] = {
        "category": category,
        "subject": subject,
        "selected": selected,
        "reason": reason,
        "actor": actor,
        "user_approved": user_approved,
        "at": _now(),
        "options_considered": [],
    }
    if prior and prior.get("selected") and prior.get("selected") != selected:
        entry["revised"] = True
        entry["options_considered"] = list(prior.get("options_considered") or []) + [{
            "option_id": prior.get("selected"),
            "rejected_because": reason or "revised",
            "was_at": prior.get("at"),
        }]
    log.append(entry)
    return entry


def add_annotation(
    project: Path,
    *,
    kind: str,
    body: str,
    quote: str = "",
    start: int | None = None,
    end: int | None = None,
    author: str = "studio",
    suggestion: str = "",
    anchor: dict | None = None,
) -> dict[str, Any]:
    if kind not in ANNOTATION_KINDS:
        raise ValueError(f"kind must be one of {ANNOTATION_KINDS}")
    collab = load_collab(project)
    text = read_story(project)
    if start is not None:
        start = int(start)
    if end is not None:
        end = int(end)
    if quote and start is None:
        idx = text.find(quote)
        if idx >= 0:
            start, end = idx, idx + len(quote)
    item = {
        "id": _uid("A"),
        "kind": kind,
        "body": body.strip(),
        "suggestion": (suggestion or "").strip(),
        "anchor": anchor,
        "quote": quote or (text[start:end] if start is not None and end is not None else ""),
        "start": start,
        "end": end,
        "author": author,
        "status": "open",
        "at": _now(),
    }
    collab.setdefault("annotations", []).append(item)
    record_decision(
        collab,
        category="annotation",
        subject=item["id"],
        selected=kind,
        reason=body[:120],
        actor=author,
    )
    save_collab(project, collab)
    return item


def add_comment(
    project: Path,
    *,
    body: str,
    author: str = "studio",
    target: str | None = None,
    anchor: dict | None = None,
) -> dict[str, Any]:
    collab = load_collab(project)
    item = {
        "id": _uid("C"),
        "body": body.strip(),
        "author": author,
        "target": target,
        "anchor": anchor,
        "status": "open",
        "at": _now(),
    }
    collab.setdefault("comments", []).append(item)
    record_decision(
        collab,
        category="comment",
        subject=item["id"],
        selected="open",
        reason=body[:120],
        actor=author,
    )
    save_collab(project, collab)
    return item


def set_feedback_status(
    project: Path,
    *,
    feedback_id: str,
    status: str,
    author: str = "studio",
) -> dict[str, Any]:
    if status not in FEEDBACK_STATUSES:
        raise ValueError(f"status must be one of {FEEDBACK_STATUSES}")
    collab = load_collab(project)
    found = None
    bucket = None
    for key in ("annotations", "comments"):
        for item in collab.get(key) or []:
            if item.get("id") == feedback_id:
                found = item
                bucket = key
                break
        if found:
            break
    if not found:
        raise FileNotFoundError(feedback_id)
    found["status"] = status
    found["resolved_at"] = _now()
    record_decision(
        collab,
        category=bucket[:-1] if bucket else "feedback",
        subject=feedback_id,
        selected=status,
        reason=f"status->{status}",
        actor=author,
    )
    save_collab(project, collab)
    return found


def open_feedback(collab: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for ann in collab.get("annotations") or []:
        if ann.get("status") == "open":
            items.append({**ann, "channel": "annotation"})
    for com in collab.get("comments") or []:
        if com.get("status") == "open":
            items.append({**com, "channel": "comment"})
    items.sort(key=lambda x: str(x.get("at") or ""))
    return items


def build_iteration_draft(project: Path, *, author: str = "studio", note: str = "") -> dict[str, Any]:
    """Create a draft revision from open annotations/comments (draft-then-apply)."""
    collab = load_collab(project)
    text = read_story(project)
    feedback = open_feedback(collab)
    if not text.strip() and not feedback:
        raise ValueError("no story text or feedback to iterate on")

    working = text
    applied: list[str] = []
    # Apply edit-kind annotations with suggestions (from end to start to keep offsets).
    edits = [
        f for f in feedback
        if f.get("channel") == "annotation"
        and f.get("kind") == "edit"
        and (f.get("suggestion") or "").strip()
        and isinstance(f.get("start"), int)
        and isinstance(f.get("end"), int)
    ]
    for edit in sorted(edits, key=lambda e: int(e["start"]), reverse=True):
        start, end = int(edit["start"]), int(edit["end"])
        if 0 <= start <= end <= len(working):
            working = working[:start] + str(edit["suggestion"]) + working[end:]
            applied.append(edit["id"])

    goals: list[str] = []
    for item in feedback:
        if item["id"] in applied:
            continue
        if item.get("channel") == "annotation":
            label = {"note": "注解", "edit": "改写建议", "question": "疑问"}.get(item.get("kind"), "注解")
            quote = item.get("quote") or ""
            tip = item.get("suggestion") or item.get("body") or ""
            goals.append(f"- [{label}/{item['id']}] {('「' + quote[:60] + '」→ ') if quote else ''}{tip}")
        else:
            goals.append(f"- [评论/{item['id']}] {item.get('body') or ''}")

    brief_lines = [
        "# 迭代草稿（未采纳）",
        "",
        f"> 基于 v{collab.get('version') or 0} · 开放反馈 {len(feedback)} 条 · {author}",
        "",
    ]
    if note:
        brief_lines += [f"导演备注：{note}", ""]
    if goals:
        brief_lines += ["## 待消化反馈", *goals, ""]
    brief_lines += [
        "## 修订正文",
        "",
        working.strip() or "（在此写下一版剧本）",
        "",
    ]
    draft_text = "\n".join(brief_lines)
    draft = {
        "created_at": _now(),
        "author": author,
        "note": note,
        "based_on_feedback": [f["id"] for f in feedback],
        "applied_edits": applied,
        "text": draft_text,
        "source_version": collab.get("version") or 0,
    }
    collab["draft"] = draft
    record_decision(
        collab,
        category="story_draft",
        subject="boards/story.md",
        selected=draft["created_at"],
        reason=note or f"iterate from {len(feedback)} feedback",
        actor=author,
    )
    save_collab(project, collab)
    return draft


def apply_draft(
    project: Path,
    *,
    text: str | None = None,
    accept_feedback: bool = True,
    author: str = "studio",
) -> dict[str, Any]:
    collab = load_collab(project)
    draft = collab.get("draft")
    if not draft:
        raise ValueError("no draft to apply")
    final = text if text is not None else str(draft.get("text") or "")
    # Strip draft scaffolding if still present — keep section after 修订正文.
    marker = "## 修订正文"
    if marker in final:
        final = final.split(marker, 1)[1].lstrip("\n")
    result = write_story(
        project,
        final.strip() + ("\n" if final.strip() else ""),
        note="iterate:apply",
        author=author,
        snapshot=True,
    )
    collab = result["collab"]
    if accept_feedback:
        ids = set(draft.get("based_on_feedback") or [])
        for ann in collab.get("annotations") or []:
            if ann.get("id") in ids and ann.get("status") == "open":
                ann["status"] = "accepted"
                ann["resolved_at"] = _now()
        for com in collab.get("comments") or []:
            if com.get("id") in ids and com.get("status") == "open":
                com["status"] = "resolved"
                com["resolved_at"] = _now()
    collab["draft"] = None
    record_decision(
        collab,
        category="story_apply",
        subject="boards/story.md",
        selected=f"v{collab.get('version')}",
        reason="apply draft",
        actor=author,
        user_approved=True,
    )
    save_collab(project, collab)
    result["collab"] = collab
    return result


def discard_draft(project: Path, *, author: str = "studio") -> dict[str, Any]:
    collab = load_collab(project)
    if not collab.get("draft"):
        return collab
    record_decision(
        collab,
        category="story_draft",
        subject="boards/story.md",
        selected="discarded",
        reason="discard draft",
        actor=author,
    )
    collab["draft"] = None
    return save_collab(project, collab)


def snapshot(project: Path) -> dict[str, Any]:
    collab = load_collab(project)
    text = read_story(project)
    return {
        "text": text,
        "version": collab.get("version") or 0,
        "beats": collab.get("beats") or [],
        "annotations": collab.get("annotations") or [],
        "comments": collab.get("comments") or [],
        "decision_log": (collab.get("decision_log") or [])[-20:],
        "draft": collab.get("draft"),
        "history": collab.get("history") or [],
        "open_feedback": open_feedback(collab),
    }


def seed_from_text(project: Path, text: str, *, note: str = "seed") -> dict[str, Any]:
    if not text.strip():
        return snapshot(project)
    if read_story(project).strip():
        return snapshot(project)
    write_story(project, text if text.endswith("\n") else text + "\n", note=note, snapshot=True)
    return snapshot(project)
