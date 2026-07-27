#!/usr/bin/env python3
"""Render an offline, evidence-bearing cinematic production dashboard.

The renderer accepts the existing animation-project shape and the broader
workflow contract in assets/workflow.template.json. It never truncates media,
does not auto-refresh unless explicitly requested, and keeps technical QC,
creative review, and performance estimation as separate states.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
from pathlib import Path
from typing import Any


LEGACY_STATIONS = [
    ("screenwriter", "编剧", "SCRIPT"),
    ("character_designer", "角色设计", "CHARACTER"),
    ("scene_designer", "场景设计", "SCENE"),
    ("prop_designer", "道具设计", "PROP"),
    ("storyboard_director", "分镜", "STORYBOARD"),
    ("sound_director", "声音", "SOUND"),
    ("chief_director", "总导演·剪辑", "DIRECTOR"),
]

DEFAULT_WORKFLOW = [
    ("brief", "需求·权利·预算", []),
    ("research", "同题研究", ["brief"]),
    ("planning", "创作策划", ["research"]),
    ("script", "剧本·证据图", ["planning"]),
    ("design", "角色·场景·声音圣经", ["script"]),
    ("storyboard", "分镜·Animatic", ["design"]),
    ("acquisition", "拍摄·获取·生成", ["storyboard"]),
    ("picture_edit", "画面剪辑", ["acquisition"]),
    ("separation", "音源分离·清理", ["picture_edit"]),
    ("av_sync", "口型·对白定位", ["separation"]),
    ("sound_mix", "声音设计·混音", ["av_sync"]),
    ("finishing", "调色·字幕·母版", ["sound_mix"]),
    ("qc", "技术·创意·权利验收", ["finishing"]),
    ("evaluation", "评分·发布前预测", ["qc"]),
    ("release", "发布·A/B", ["evaluation"]),
    ("learning", "真实数据·复盘校准", ["release"]),
]

DEFAULT_FEEDBACK = [
    {"from": "qc", "to": "picture_edit", "reason": "结构/连续性返工"},
    {"from": "qc", "to": "sound_mix", "reason": "声音返工"},
    {"from": "learning", "to": "research", "reason": "真实数据更新下一轮假设"},
]

STATUS = {
    "planned": ("#77736f", "计划中"),
    "pending": ("#77736f", "待开工"),
    "ready": ("#74a9cf", "可开工"),
    "running": ("#ffb15e", "进行中"),
    "review": ("#e8c268", "待评审"),
    "approved": ("#72c69f", "已通过"),
    "complete": ("#72c69f", "已完成"),
    "rework": ("#e67b63", "返工中"),
    "blocked": ("#ef655b", "阻塞"),
    "fail": ("#ef655b", "未通过"),
    "warning": ("#e8c268", "有警告"),
    "stale": ("#d69254", "上游变更"),
    "skipped": ("#77736f", "不适用"),
    "not_required": ("#77736f", "不适用"),
    "not_estimable": ("#9a86c8", "不可估计"),
}

MEDIA_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".wav",
    ".mp3",
    ".m4a",
    ".flac",
    ".ogg",
    ".mp4",
    ".webm",
    ".mov",
    ".mkv",
}


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON at line {exc.lineno}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError("Project JSON root must be an object.")
    return value


def rel(base: Path, value: str) -> str:
    if not value or "://" in value:
        return value or ""
    path_text, separator, fragment = value.partition("#")
    candidate = Path(path_text)
    try:
        target = candidate if candidate.is_absolute() else base / candidate
        rendered = os.path.relpath(target, base).replace("\\", "/")
    except ValueError:
        rendered = str(candidate).replace("\\", "/")
    return rendered + (separator + fragment if separator else "")


def local_exists(base: Path, value: str) -> bool | None:
    if not value or "://" in value:
        return None
    path_text = value.partition("#")[0]
    candidate = Path(path_text)
    target = candidate if candidate.is_absolute() else base / candidate
    return target.exists()


def media_tag(base: Path, value: str, label: str = "") -> str:
    target = rel(base, value)
    extension = Path(target.partition("#")[0]).suffix.lower()
    exists = local_exists(base, value)
    missing = '<span class="missing">路径缺失</span>' if exists is False else ""
    caption = f"<figcaption>{esc(label or Path(target).stem)}{missing}</figcaption>"
    href = esc(target)
    if extension in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return (
            f'<figure class="media-item image"><a href="{href}" target="_blank" rel="noreferrer">'
            f'<img src="{href}" loading="lazy" alt="{esc(label)}"></a>{caption}</figure>'
        )
    if extension in {".wav", ".mp3", ".m4a", ".flac", ".ogg"}:
        return (
            f'<figure class="media-item audio"><audio controls preload="metadata" src="{href}"></audio>'
            f"{caption}</figure>"
        )
    if extension in {".mp4", ".webm", ".mov", ".mkv"}:
        return (
            f'<figure class="media-item video"><video controls preload="metadata" src="{href}"></video>'
            f"{caption}</figure>"
        )
    return f'<a class="file-link" href="{href}" target="_blank" rel="noreferrer">{esc(label or target)}</a>'


def normalized_status(value: object) -> str:
    status = str(value or "planned").strip().lower()
    return status if status in STATUS else "planned"


def status_badge(value: object) -> str:
    status = normalized_status(value)
    color, label = STATUS[status]
    return f'<span class="status" style="--state:{color}">{esc(label)}</span>'


def legacy_status(project: dict[str, Any], key: str) -> str:
    stations = project.get("stations") if isinstance(project.get("stations"), dict) else {}
    station = stations.get(key) if isinstance(stations.get(key), dict) else {}
    return normalized_status(station.get("status"))


def derived_workflow(project: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    configured = project.get("workflow")
    if isinstance(configured, dict) and isinstance(configured.get("nodes"), list):
        nodes = [dict(node) for node in configured["nodes"] if isinstance(node, dict)]
        feedback = [
            dict(edge)
            for edge in configured.get("feedback_edges", [])
            if isinstance(edge, dict)
        ]
        return nodes, feedback

    final = project.get("final") if isinstance(project.get("final"), dict) else {}
    technical = final.get("technical_qc") if isinstance(final.get("technical_qc"), dict) else {}
    evaluation = project.get("evaluation") if isinstance(project.get("evaluation"), dict) else {}
    release = project.get("release") if isinstance(project.get("release"), dict) else {}
    learning = project.get("learning") if isinstance(project.get("learning"), dict) else {}
    statuses = {
        "brief": "approved" if project.get("brief") else "planned",
        "research": normalized_status(
            (project.get("research") or {}).get("status")
            if isinstance(project.get("research"), dict)
            else "planned"
        ),
        "planning": "approved" if project.get("screenplay") else legacy_status(project, "screenwriter"),
        "script": legacy_status(project, "screenwriter"),
        "design": min(
            (
                legacy_status(project, "character_designer"),
                legacy_status(project, "scene_designer"),
                legacy_status(project, "prop_designer"),
            ),
            key=lambda item: list(STATUS).index(item),
        ),
        "storyboard": legacy_status(project, "storyboard_director"),
        "acquisition": legacy_status(project, "storyboard_director"),
        "picture_edit": legacy_status(project, "chief_director"),
        "separation": normalized_status(
            ((project.get("audio") or {}).get("separation") or {}).get("status")
            if isinstance((project.get("audio") or {}).get("separation"), dict)
            else "planned"
        ),
        "av_sync": normalized_status(
            ((project.get("audio") or {}).get("av_sync") or {}).get("status")
            if isinstance((project.get("audio") or {}).get("av_sync"), dict)
            else "planned"
        ),
        "sound_mix": legacy_status(project, "sound_director"),
        "finishing": normalized_status(final.get("status")),
        "qc": normalized_status(technical.get("status")),
        "evaluation": normalized_status(evaluation.get("status")),
        "release": normalized_status(release.get("status")),
        "learning": normalized_status(learning.get("status")),
    }
    nodes = [
        {
            "id": node_id,
            "label": label,
            "status": statuses[node_id],
            "depends_on": dependencies,
            "outputs": [],
        }
        for node_id, label, dependencies in DEFAULT_WORKFLOW
    ]
    return nodes, list(DEFAULT_FEEDBACK)


def workflow_svg(nodes: list[dict[str, Any]], feedback: list[dict[str, str]]) -> str:
    visible = nodes[:24]
    columns = 4
    card_width, card_height = 245, 76
    gap_x, gap_y = 48, 64
    margin_x, margin_y = 34, 34
    rows = max(1, (len(visible) + columns - 1) // columns)
    width = margin_x * 2 + columns * card_width + (columns - 1) * gap_x
    height = margin_y * 2 + rows * card_height + (rows - 1) * gap_y + 46
    positions: dict[str, tuple[float, float]] = {}
    for index, node in enumerate(visible):
        row = index // columns
        column_in_row = index % columns
        column = column_in_row if row % 2 == 0 else columns - 1 - column_in_row
        positions[str(node.get("id") or index)] = (
            margin_x + column * (card_width + gap_x),
            margin_y + row * (card_height + gap_y),
        )

    output = [
        f'<svg viewBox="0 0 {width} {height}" class="workflow-svg" role="img" '
        'aria-label="完整视频生产工作流">',
        "<defs>",
        '<marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
        '<path d="M0 0 L8 4 L0 8 Z" fill="#6f6962"/></marker>',
        '<marker id="feedback-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
        '<path d="M0 0 L8 4 L0 8 Z" fill="#d69254"/></marker>',
        "</defs>",
    ]

    node_by_id = {str(node.get("id")): node for node in visible}
    for node in visible:
        target_id = str(node.get("id"))
        if target_id not in positions:
            continue
        bx, by = positions[target_id]
        for dependency in node.get("depends_on", []):
            source_id = str(dependency)
            if source_id not in positions:
                continue
            ax, ay = positions[source_id]
            if abs(ay - by) < 1:
                if ax < bx:
                    start, end = (ax + card_width, ay + card_height / 2), (bx, by + card_height / 2)
                else:
                    start, end = (ax, ay + card_height / 2), (bx + card_width, by + card_height / 2)
                path = f"M{start[0]} {start[1]} H{end[0]}"
            else:
                start = (ax + card_width / 2, ay + card_height)
                end = (bx + card_width / 2, by)
                middle = (start[1] + end[1]) / 2
                path = f"M{start[0]} {start[1]} V{middle} H{end[0]} V{end[1]}"
            source_status = normalized_status(node_by_id[source_id].get("status"))
            color = STATUS[source_status][0] if source_status in {"approved", "complete"} else "#514c47"
            output.append(
                f'<path d="{path}" class="workflow-edge" stroke="{color}" marker-end="url(#arrow)"/>'
            )

    feedback_labels: list[str] = []
    for edge_index, edge in enumerate(feedback):
        source_id, target_id = str(edge.get("from") or ""), str(edge.get("to") or "")
        if source_id not in positions or target_id not in positions:
            continue
        sx, sy = positions[source_id]
        tx, ty = positions[target_id]
        lane = height - 32 - edge_index * 11
        path = (
            f"M{sx + card_width / 2} {sy + card_height} "
            f"V{lane} H{tx + card_width / 2} V{ty + card_height}"
        )
        output.append(
            f'<path d="{path}" class="feedback-edge" marker-end="url(#feedback-arrow)"/>'
        )
        reason = str(edge.get("reason") or f"{source_id} → {target_id}")
        feedback_labels.append(reason)

    for index, node in enumerate(visible):
        node_id = str(node.get("id") or index)
        x, y = positions[node_id]
        status = normalized_status(node.get("status"))
        color, status_label = STATUS[status]
        title = str(node.get("label") or node_id)
        output_count = len(node.get("outputs", [])) if isinstance(node.get("outputs"), list) else 0
        output.extend(
            [
                f'<g class="workflow-node" data-state="{esc(status)}" data-stage="{esc(node_id)}" '
                f'tabindex="0" role="link" aria-label="{esc(title)} · {esc(status_label)}">',
                f"<title>{esc(title)} · {esc(status_label)}</title>",
                f'<rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" rx="9" '
                f'fill="#211e1b" stroke="#45403b"/>',
                f'<rect x="{x}" y="{y}" width="6" height="{card_height}" rx="3" fill="{color}"/>',
                f'<text x="{x + 18}" y="{y + 25}" class="node-index">{index:02d}</text>',
                f'<text x="{x + 52}" y="{y + 25}" class="node-title">{esc(title)}</text>',
                f'<text x="{x + 18}" y="{y + 53}" class="node-state" fill="{color}">{esc(status_label)}</text>',
                f'<text x="{x + card_width - 16}" y="{y + 53}" text-anchor="end" '
                f'class="node-output">{output_count} outputs</text>',
                "</g>",
            ]
        )
    output.append("</svg>")
    if feedback_labels:
        output.append(
            '<p class="feedback-legend"><b>反馈回路：</b>'
            + " · ".join(esc(item) for item in feedback_labels)
            + "</p>"
        )
    return "".join(output)


def render_stage_controls(nodes: list[dict[str, Any]], project_path: Path) -> str:
    cards: list[str] = []
    controller = Path(__file__).with_name("workflow_control.py")
    for index, node in enumerate(nodes):
        node_id = str(node.get("id") or index)
        label = str(node.get("label") or node_id)
        dependencies = node.get("depends_on") if isinstance(node.get("depends_on"), list) else []
        outputs = node.get("outputs") if isinstance(node.get("outputs"), list) else []
        command = (
            f'python "{controller}" redo "{project_path}" --stage {node_id} '
            f'--reason "填写重做原因"'
        )
        cards.append(
            f'<article class="stage-control" id="stage-{esc(node_id)}">'
            f'<header><span>{index:02d}</span><h3>{esc(label)}</h3>{status_badge(node.get("status"))}</header>'
            f'<p><b>依赖</b> {esc(" · ".join(str(item) for item in dependencies) or "无")}</p>'
            f'<p><b>产物</b> {len(outputs)} 项</p>'
            + (
                f'<p class="note">{esc(node.get("note") or node.get("revision_reason"))}</p>'
                if node.get("note") or node.get("revision_reason")
                else ""
            )
            + f'<button class="copy-command" type="button" data-copy="{esc(command)}">复制重做预演命令</button>'
            + "</article>"
        )
    return '<div class="stage-controls">' + "".join(cards) + "</div>"


def render_version_history(project_path: Path, base: Path) -> str:
    index_path = project_path.parent / "history" / "index.json"
    if not index_path.is_file():
        return '<p class="empty">尚无工程快照。状态变更前会自动创建，也可手工 checkpoint。</p>'
    try:
        index = read_json(index_path)
    except (OSError, ValueError) as exc:
        return f'<p class="missing">历史索引无法读取：{esc(exc)}</p>'
    entries = [entry for entry in index.get("entries", []) if isinstance(entry, dict)]
    if not entries:
        return '<p class="empty">历史索引存在，但尚无版本。</p>'
    controller = Path(__file__).with_name("workflow_control.py")
    options: list[str] = []
    cards: list[str] = []
    for reverse_index, entry in enumerate(reversed(entries)):
        version_id = str(entry.get("id") or "")
        manifest = str(entry.get("manifest") or "")
        absolute_manifest = (project_path.parent / manifest).resolve() if manifest else index_path
        href = rel(base, str(absolute_manifest))
        options.append(
            f'<option value="{esc(version_id)}">{esc(version_id)} · {esc(entry.get("kind", ""))}</option>'
        )
        restore_command = (
            f'python "{controller}" restore "{project_path}" --version "{version_id}" '
            f'--reason "填写恢复原因"'
        )
        hidden = "" if reverse_index == 0 else " hidden"
        cards.append(
            f'<article class="version-card"{hidden} data-version="{esc(version_id)}">'
            f'<h3>{esc(version_id)}</h3>'
            f'<p><b>类型</b> {esc(entry.get("kind", ""))}　<b>节点</b> {esc(entry.get("stage", "") or "—")}</p>'
            f'<p><b>原因</b> {esc(entry.get("reason", "") or "—")}</p>'
            f'<p><b>时间</b> {esc(entry.get("created_at", ""))}　<b>操作者</b> {esc(entry.get("actor", ""))}</p>'
            f'<div class="version-actions"><a class="file-link" href="{esc(href)}" target="_blank">查看工程快照 JSON</a>'
            f'<button class="copy-command" type="button" data-copy="{esc(restore_command)}">复制恢复预演命令</button></div>'
            "</article>"
        )
    return (
        '<label class="version-picker">选择历史版本 '
        f'<select id="version-selector">{"".join(options)}</select></label>'
        + "".join(cards)
        + '<p class="note">恢复命令默认只预演；核对后手工追加 <code>--confirm</code> 才会写入，且会先保存当前版本。</p>'
    )


def walk_media(value: Any, prefix: str = "") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            label = f"{prefix}.{key}" if prefix else str(key)
            found.extend(walk_media(item, label))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(walk_media(item, f"{prefix}[{index}]"))
    elif isinstance(value, str):
        path_text = value.partition("#")[0]
        if Path(path_text).suffix.lower() in MEDIA_EXTENSIONS:
            found.append((value, prefix))
    return found


def unique_media(project: dict[str, Any]) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    seen: set[str] = set()
    for path, label in walk_media(project):
        normalized = path.replace("\\", "/").lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append((path, label))
    return result


def station_media(key: str, project: dict[str, Any]) -> list[tuple[str, str]]:
    station = (
        project.get("stations", {}).get(key, {})
        if isinstance(project.get("stations"), dict)
        else {}
    )
    results: list[tuple[str, str]] = []
    for item in station.get("outputs", []) if isinstance(station, dict) else []:
        if isinstance(item, str):
            results.append((item, "工位输出"))
    if key == "character_designer":
        for character in project.get("characters", []):
            if not isinstance(character, dict):
                continue
            if character.get("portrait"):
                results.append((str(character["portrait"]), str(character.get("alias") or "角色")))
            voice = character.get("voice")
            if isinstance(voice, dict) and voice.get("sample"):
                results.append((str(voice["sample"]), f"{character.get('alias', '角色')} · 试音"))
    elif key == "scene_designer":
        for scene in project.get("scenes", []):
            if isinstance(scene, dict) and scene.get("master"):
                results.append((str(scene["master"]), str(scene.get("id") or "场景")))
    elif key == "prop_designer":
        for prop in project.get("props", []):
            if not isinstance(prop, dict):
                continue
            for image in prop.get("images", []):
                if isinstance(image, str):
                    results.append((image, str(prop.get("id") or "道具")))
    elif key == "storyboard_director":
        for shot in project.get("shots", []):
            if not isinstance(shot, dict):
                continue
            for media_key in ("first_frame", "video"):
                if shot.get(media_key):
                    results.append(
                        (
                            str(shot[media_key]),
                            f"{shot.get('id', 'shot')} · {media_key} · {shot.get('camera', '')}",
                        )
                    )
    elif key == "sound_director":
        audio = project.get("audio") if isinstance(project.get("audio"), dict) else {}
        for cue in audio.get("cues", []):
            if not isinstance(cue, dict):
                continue
            path = cue.get("path") or cue.get("file")
            if path:
                results.append((str(path), str(cue.get("id") or cue.get("cue_id") or "cue")))
        for mix_key in ("mix", "dialogue", "music", "effects", "ambience"):
            if audio.get(mix_key):
                results.append((str(audio[mix_key]), f"audio.{mix_key}"))
    elif key == "chief_director":
        final = project.get("final") if isinstance(project.get("final"), dict) else {}
        for final_key in ("master", "video", "picture_master", "audio_mix", "title_card", "qc_report"):
            if final.get(final_key):
                results.append((str(final[final_key]), f"final.{final_key}"))

    unique: list[tuple[str, str]] = []
    seen: set[str] = set()
    for path, label in results:
        token = path.replace("\\", "/").lower()
        if token not in seen:
            seen.add(token)
            unique.append((path, label))
    return unique


def render_station_sections(project: dict[str, Any], base: Path) -> str:
    stations = project.get("stations") if isinstance(project.get("stations"), dict) else {}
    if not stations:
        return ""
    sections: list[str] = ['<section class="block"><div class="section-title"><span>03</span><h2>专业工位</h2></div>']
    for index, (key, label, code) in enumerate(LEGACY_STATIONS, 1):
        station = stations.get(key) if isinstance(stations.get(key), dict) else {}
        media = station_media(key, project)
        media_html = "".join(media_tag(base, path, media_label) for path, media_label in media)
        outputs = station.get("outputs", []) if isinstance(station.get("outputs"), list) else []
        file_links = "".join(
            media_tag(base, str(item), "输出")
            for item in outputs
            if isinstance(item, str) and Path(item.partition("#")[0]).suffix.lower() not in MEDIA_EXTENSIONS
        )
        sections.append(
            f'<article class="station-card"><header><span class="station-no">{index:02d}</span>'
            f"<h3>{esc(label)}</h3><code>{esc(code)}</code>{status_badge(station.get('status'))}"
            f'<time>{esc(station.get("updated_at", ""))}</time></header>'
            + (f'<p class="note">{esc(station.get("note"))}</p>' if station.get("note") else "")
            + f'<div class="media-grid">{media_html or file_links or "<span class=empty>暂无已登记输出</span>"}{file_links}</div>'
            + "</article>"
        )
    sections.append("</section>")
    return "".join(sections)


def flatten_rows(value: Any, prefix: str = "", depth: int = 0) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, dict) and depth < 3:
        for key, item in value.items():
            rows.extend(flatten_rows(item, f"{prefix}.{key}" if prefix else str(key), depth + 1))
    elif isinstance(value, list) and depth < 2:
        if all(not isinstance(item, (dict, list)) for item in value):
            rows.append((prefix, " · ".join(str(item) for item in value)))
        else:
            for index, item in enumerate(value):
                rows.extend(flatten_rows(item, f"{prefix}[{index}]", depth + 1))
    else:
        text = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
        rows.append((prefix, text))
    return rows


def data_panel(title: str, value: Any, empty_note: str) -> str:
    if not value:
        return f'<article class="data-panel"><h3>{esc(title)}</h3><p class="empty">{esc(empty_note)}</p></article>'
    rows = flatten_rows(value)
    body = "".join(f"<tr><th>{esc(key)}</th><td>{esc(item)}</td></tr>" for key, item in rows)
    return f'<article class="data-panel"><h3>{esc(title)}</h3><table>{body}</table></article>'


def ledger_rows(project: dict[str, Any]) -> tuple[str, str]:
    costs = []
    for item in project.get("cost_log", []):
        if not isinstance(item, dict):
            continue
        amount = item.get("amount_cny", 0)
        try:
            amount_text = f"¥{float(amount):.2f}"
        except (TypeError, ValueError):
            amount_text = str(amount)
        costs.append(
            f"<tr><th>{esc(item.get('station', ''))}</th><td>{esc(item.get('provider', ''))}</td>"
            f'<td class="number">{esc(amount_text)}</td><td>{esc(item.get("detail", ""))}</td></tr>'
        )
    history = []
    for item in reversed(project.get("history", [])):
        if not isinstance(item, dict):
            continue
        invalidated = item.get("invalidated")
        effect = (
            f' <span class="impact">波及 {esc("、".join(str(value) for value in invalidated))}</span>'
            if isinstance(invalidated, list) and invalidated
            else ""
        )
        history.append(
            f'<tr><th class="number">{esc(item.get("at", ""))}</th><td>{esc(item.get("who", ""))}</td>'
            f'<td colspan="2">{esc(item.get("change", ""))}{effect}</td></tr>'
        )
    return "".join(costs), "".join(history)


def build(project_path: Path, output_path: Path, refresh: int = 0) -> None:
    project = read_json(project_path)
    base = output_path.parent
    nodes, feedback = derived_workflow(project)
    accepted = sum(
        1 for node in nodes if normalized_status(node.get("status")) in {"approved", "complete", "skipped", "not_required"}
    )
    cost = sum(
        float(item.get("amount_cny") or 0)
        for item in project.get("cost_log", [])
        if isinstance(item, dict)
    )
    budget = project.get("budget_cny", "—")
    media = unique_media(project)
    media_html = "".join(media_tag(base, path, label) for path, label in media)
    costs, history = ledger_rows(project)
    auto_refresh = (
        f'<meta http-equiv="refresh" content="{refresh}">' if isinstance(refresh, int) and refresh > 0 else ""
    )
    refresh_label = f"自动刷新 {refresh}s" if refresh > 0 else "手动刷新"
    research = project.get("research") or project.get("creative_research")
    planning = project.get("creative_plan") or project.get("planning")
    evaluation = project.get("evaluation")
    final = project.get("final") if isinstance(project.get("final"), dict) else {}
    qc = final.get("technical_qc") if isinstance(final.get("technical_qc"), dict) else project.get("qc")
    prediction = (
        evaluation.get("performance_prediction")
        if isinstance(evaluation, dict) and isinstance(evaluation.get("performance_prediction"), dict)
        else project.get("performance_prediction")
    )

    doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
{auto_refresh}
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(project.get("title", "Cinematic production"))} · 生产看板</title>
<style>
:root {{
  color-scheme: dark;
  --bg:#151311; --panel:#201d1a; --panel2:#181614; --line:#3d3833;
  --ink:#eee7dd; --muted:#a69d92; --ember:#ff7542; --amber:#ffb15e;
}}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ margin:0; background:var(--bg); color:var(--ink);
  font:14px/1.6 "Segoe UI","PingFang SC","Microsoft YaHei",system-ui,sans-serif; }}
a {{ color:inherit; }}
button {{ font:inherit; }}
.topbar {{ position:sticky; top:0; z-index:10; display:flex; align-items:center; gap:14px;
  flex-wrap:wrap; padding:11px clamp(18px,4vw,52px); background:rgba(32,29,26,.96);
  border-bottom:1px solid var(--line); backdrop-filter:blur(12px); }}
.topbar h1 {{ margin:0; font-size:17px; letter-spacing:.01em; }}
.topbar h1::before {{ content:"◤"; color:var(--ember); margin-right:8px; }}
.meta {{ color:var(--muted); font:11px ui-monospace,Consolas,monospace; }}
.meta b {{ color:var(--ink); }}
.progress {{ height:4px; min-width:110px; flex:1; background:#35302c; border-radius:4px; overflow:hidden; }}
.progress i {{ display:block; height:100%; width:{accepted / max(1, len(nodes)) * 100:.2f}%;
  background:linear-gradient(90deg,var(--ember),var(--amber)); }}
.refresh {{ border:1px solid var(--line); color:var(--ink); background:#28231f;
  border-radius:6px; padding:5px 9px; cursor:pointer; }}
.refresh:hover {{ border-color:var(--amber); }}
.film {{ height:13px; border-bottom:1px solid var(--line);
  background:radial-gradient(circle 3px at 10px 6px,var(--line) 96%,transparent) 0 0/24px 13px; }}
main {{ max-width:1320px; margin:auto; padding:26px clamp(18px,4vw,52px) 72px; }}
.hero {{ display:grid; grid-template-columns:minmax(0,1.55fr) minmax(250px,.7fr); gap:18px; margin-bottom:22px; }}
.brief,.summary {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:18px 20px; }}
.eyebrow {{ color:var(--ember); font:11px ui-monospace,Consolas,monospace; letter-spacing:.14em; }}
.brief h2 {{ margin:6px 0 8px; font-size:24px; }}
.brief p {{ color:var(--muted); max-width:82ch; margin:0; }}
.summary {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }}
.metric {{ border-left:2px solid var(--line); padding-left:10px; }}
.metric span {{ display:block; color:var(--muted); font-size:11px; }}
.metric b {{ font:16px ui-monospace,Consolas,monospace; }}
.block {{ border-top:1px solid var(--line); padding:22px 0 26px; }}
.section-title {{ display:flex; gap:12px; align-items:baseline; margin-bottom:14px; }}
.section-title span {{ color:var(--ember); font:11px ui-monospace,Consolas,monospace; }}
.section-title h2 {{ margin:0; font-size:16px; }}
.workflow-wrap {{ padding:12px; border:1px solid var(--line); border-radius:10px; background:var(--panel2); overflow:auto; }}
.workflow-svg {{ display:block; width:100%; min-width:960px; }}
.workflow-edge,.feedback-edge {{ fill:none; stroke-width:1.6; }}
.feedback-edge {{ stroke:#d69254; stroke-dasharray:7 5; opacity:.85; }}
.node-index,.node-output,.node-state {{ font:11px ui-monospace,Consolas,monospace; }}
.node-index,.node-output {{ fill:#817971; }}
.node-title {{ fill:var(--ink); font-size:13px; font-weight:600; }}
.feedback-legend {{ margin:8px 6px 2px; color:var(--muted); font-size:11px; }}
.feedback-legend b {{ color:#d69254; }}
.workflow-node {{ cursor:pointer; }}
.workflow-node:focus rect:first-of-type {{ stroke:var(--amber); stroke-width:2; }}
.stage-controls {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:9px; margin-top:12px; }}
.stage-control {{ border:1px solid #332e2a; background:#191715; border-radius:8px; padding:10px 11px; }}
.stage-control header {{ display:flex; align-items:center; gap:8px; }}
.stage-control header > span:first-child {{ color:var(--ember); font:10px ui-monospace,Consolas,monospace; }}
.stage-control h3 {{ margin:0; font-size:12px; flex:1; }}
.stage-control p {{ margin:4px 0; color:var(--muted); font-size:10px; }}
.stage-control p b {{ color:#cfc6bb; }}
.copy-command {{ border:1px solid var(--line); background:#26221e; color:var(--muted);
  border-radius:5px; padding:4px 7px; font-size:10px; cursor:pointer; }}
.copy-command:hover {{ color:var(--ink); border-color:var(--amber); }}
.station-card {{ padding:15px 0 18px; border-top:1px solid #302c28; }}
.station-card:first-of-type {{ border-top:0; }}
.station-card header {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; }}
.station-card h3 {{ margin:0; font-size:14px; }}
.station-card code,.station-no {{ color:var(--muted); font:10px ui-monospace,Consolas,monospace; letter-spacing:.1em; }}
.station-no {{ color:var(--ember); }}
.station-card time {{ margin-left:auto; color:var(--muted); font:10px ui-monospace,Consolas,monospace; }}
.status {{ color:var(--state); border:1px solid var(--state); border-radius:999px;
  padding:1px 7px; font-size:10px; line-height:1.6; }}
.note {{ color:var(--muted); margin:6px 0 0; max-width:90ch; }}
.media-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(210px,1fr)); gap:10px; margin-top:12px; }}
.media-item {{ min-width:0; margin:0; padding:8px; border:1px solid #332e2a; border-radius:8px; background:#191715; }}
.media-item img,.media-item video {{ width:100%; max-height:220px; object-fit:contain; display:block; border-radius:5px; background:#0c0b0a; }}
.media-item audio {{ width:100%; height:32px; }}
figcaption {{ margin-top:6px; color:var(--muted); font:10px/1.35 ui-monospace,Consolas,monospace;
  overflow-wrap:anywhere; }}
.missing {{ color:#ef655b; margin-left:8px; }}
.file-link {{ display:inline-block; padding:6px 9px; border:1px solid var(--line); border-radius:5px;
  color:var(--muted); font:11px ui-monospace,Consolas,monospace; overflow-wrap:anywhere; }}
.data-grid,.ledger-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }}
.data-panel {{ border:1px solid var(--line); border-radius:9px; background:var(--panel); padding:14px; min-width:0; overflow:auto; }}
.data-panel h3 {{ margin:0 0 9px; font-size:12px; color:var(--amber); }}
table {{ width:100%; border-collapse:collapse; font-size:11px; }}
th,td {{ text-align:left; vertical-align:top; padding:5px 8px 5px 0; border-bottom:1px solid #302b27; overflow-wrap:anywhere; }}
th {{ width:28%; color:var(--muted); font-weight:500; }}
td {{ color:#d7cfc5; }}
.number {{ white-space:nowrap; font-family:ui-monospace,Consolas,monospace; }}
.impact {{ color:var(--amber); }}
.empty {{ color:#756e66; }}
.version-picker {{ display:block; color:var(--muted); margin-bottom:10px; }}
.version-picker select {{ margin-left:8px; max-width:min(100%,620px); color:var(--ink); background:#26221e;
  border:1px solid var(--line); border-radius:5px; padding:5px 8px; }}
.version-card {{ border:1px solid var(--line); border-radius:9px; background:var(--panel); padding:14px; }}
.version-card[hidden] {{ display:none; }}
.version-card h3 {{ margin:0 0 7px; font:12px ui-monospace,Consolas,monospace; color:var(--amber); }}
.version-card p {{ margin:4px 0; color:var(--muted); }}
.version-actions {{ display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; }}
details summary {{ cursor:pointer; color:var(--amber); margin-bottom:12px; }}
@media (max-width:820px) {{
  .hero,.data-grid,.ledger-grid {{ grid-template-columns:1fr; }}
  .station-card time {{ margin-left:0; width:100%; }}
}}
@media (prefers-reduced-motion:reduce) {{ html {{ scroll-behavior:auto; }} }}
</style>
</head>
<body>
<header class="topbar">
  <h1>{esc(project.get("title", "Cinematic production"))}</h1>
  <span class="meta">目标 <b>{esc(project.get("target_duration_s", "—"))}s</b></span>
  <span class="meta">模式 <b>{esc(project.get("director_mode", "—"))}</b></span>
  <span class="meta">花费 <b>¥{cost:.2f}</b> / ¥{esc(budget)}</span>
  <span class="meta">流程 <b>{accepted}/{len(nodes)}</b></span>
  <div class="progress" aria-label="流程通过进度"><i></i></div>
  <button class="refresh" type="button" onclick="location.reload()">{esc(refresh_label)}</button>
</header>
<div class="film"></div>
<main>
  <section class="hero">
    <article class="brief"><span class="eyebrow">PRODUCTION RECORD</span>
      <h2>{esc(project.get("title", "未命名项目"))}</h2>
      <p>{esc(project.get("brief", "尚未登记创作简报。"))}</p>
    </article>
    <aside class="summary">
      <div class="metric"><span>素材记录</span><b>{len(media)}</b></div>
      <div class="metric"><span>工作流节点</span><b>{len(nodes)}</b></div>
      <div class="metric"><span>技术 QC</span><b>{esc((qc or {}).get("status", "未登记") if isinstance(qc, dict) else "未登记")}</b></div>
      <div class="metric"><span>绩效预测</span><b>{esc((prediction or {}).get("status", "未登记") if isinstance(prediction, dict) else "未登记")}</b></div>
    </aside>
  </section>
  <section class="block">
    <div class="section-title"><span>01</span><h2>端到端工作流与反馈回路</h2></div>
    <div class="workflow-wrap">{workflow_svg(nodes, feedback)}</div>
    {render_stage_controls(nodes, project_path)}
  </section>
  <section class="block">
    <div class="section-title"><span>02</span><h2>历史版本选择</h2></div>
    {render_version_history(project_path, base)}
  </section>
  {render_station_sections(project, base)}
  <section class="block">
    <div class="section-title"><span>04</span><h2>策划、验收与预测证据</h2></div>
    <div class="data-grid">
      {data_panel("同题研究", research, "尚未登记研究样本；不得倒推为已完成。")}
      {data_panel("原创创作策划", planning, "尚未登记独立策划产物。")}
      {data_panel("技术 / 创意 / 权利验收", qc, "尚未登记验收证据。")}
      {data_panel("创意评分", evaluation, "尚未执行证据评分。")}
      {data_panel("相似主题绩效基线", prediction, "没有足够第一方可比数据时应保持不可估计。")}
    </div>
  </section>
  <section class="block">
    <div class="section-title"><span>05</span><h2>完整素材与生成资产</h2></div>
    <details open><summary>显示全部 {len(media)} 项（不截断）</summary>
      <div class="media-grid">{media_html or '<span class="empty">项目尚未登记媒体路径。</span>'}</div>
    </details>
  </section>
  <section class="block">
    <div class="section-title"><span>06</span><h2>成本与变更证据链</h2></div>
    <div class="ledger-grid">
      <article class="data-panel"><h3>成本台账</h3><table>{costs or '<tr><td class="empty">无成本记录</td></tr>'}</table></article>
      <article class="data-panel"><h3>变更历史</h3><table>{history or '<tr><td class="empty">无变更记录</td></tr>'}</table></article>
    </div>
  </section>
</main>
<script>
const jumpToStage = (element) => {{
  const target = document.getElementById("stage-" + element.dataset.stage);
  if (target) target.scrollIntoView({{behavior:"smooth", block:"center"}});
}};
document.querySelectorAll(".workflow-node").forEach((node) => {{
  node.addEventListener("click", () => jumpToStage(node));
  node.addEventListener("keydown", (event) => {{
    if (event.key === "Enter" || event.key === " ") {{
      event.preventDefault();
      jumpToStage(node);
    }}
  }});
}});
document.querySelectorAll("[data-copy]").forEach((button) => {{
  button.addEventListener("click", async () => {{
    try {{
      await navigator.clipboard.writeText(button.dataset.copy);
      const old = button.textContent;
      button.textContent = "已复制";
      setTimeout(() => button.textContent = old, 1400);
    }} catch (_) {{
      window.prompt("复制下面的命令：", button.dataset.copy);
    }}
  }});
}});
const versionSelector = document.getElementById("version-selector");
if (versionSelector) versionSelector.addEventListener("change", () => {{
  document.querySelectorAll(".version-card").forEach((card) => {{
    card.hidden = card.dataset.version !== versionSelector.value;
  }});
}});
</script>
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(doc, encoding="utf-8")
    print(f"dashboard -> {output_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render the cinematic production dashboard.")
    parser.add_argument("project")
    parser.add_argument("-o", "--output")
    parser.add_argument(
        "--refresh",
        type=int,
        default=0,
        help="Optional auto-refresh interval in seconds; disabled by default to preserve playback.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.refresh < 0:
            raise ValueError("--refresh cannot be negative.")
        project = Path(args.project).expanduser().resolve()
        if not project.is_file():
            raise ValueError(f"Project does not exist: {project}")
        output = (
            Path(args.output).expanduser().resolve()
            if args.output
            else project.parent / "dashboard.html"
        )
        build(project, output, args.refresh)
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
