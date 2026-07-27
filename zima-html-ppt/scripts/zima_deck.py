#!/usr/bin/env python3
"""zima_deck.py — ZimaBlue Editorial 讲演 deck 的构建 / 反解 / 校验工具。

四个子命令：

    locate                       检查技能自带资产是否齐全（standalone 自检）
    build   deck.json            deck.json → 单文件 .html（内嵌 #zima-doc 文档源）
    extract deck.html            .html → deck.json（读回 #zima-doc；--legacy 兜底手写 deck）
    validate deck.json|deck.html 结构闸门 + 质量闸门 + shell 闸门

设计契约见 references/deck-json.md，闸门定义见 references/gates.md。
只依赖 Python 3.9+ 标准库；不联网、不覆盖输入文件（除非显式 --overwrite）。
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Windows 控制台默认 GBK，中文报告会花屏；强制 UTF-8 输出。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass

SKILL_ROOT = Path(__file__).resolve().parents[1]
SHELL_PATH = SKILL_ROOT / "templates" / "zima-ppt-shell.html"
STARTER_PATH = SKILL_ROOT / "templates" / "zima-ppt-starter.html"
DESIGN_SYSTEM = SKILL_ROOT / "references" / "design-system.md"
SPEAKER_MODE = SKILL_ROOT / "references" / "speaker-mode.md"

DOC_OPEN = '<script type="application/zima+json" id="zima-doc">'
DOC_CLOSE = "</scr" + "ipt>"
DOC_BLOCK_RE = re.compile(
    re.escape(DOC_OPEN) + r"(?P<body>.*?)" + re.escape(DOC_CLOSE), re.DOTALL
)

SCHEMA_VERSION = "1.0"
LAYOUTS = {"cover", "full", "split", "compare", "closing"}
BLOCK_TYPES = {
    "metrics", "cards", "list", "bars", "table", "chart",
    "quote", "bigline", "term", "pills", "text", "html",
}
TONES = {"teal", "gold", "red", "green", "muted"}
NOTE_TAGS = {"cue", "say", "do", "data", "bridge"}
NOTE_LABELS = {
    "cue": "节奏",
    "say": "【话术】",
    "do": "【动作】",
    "data": "【数据】",
    "bridge": "【过渡】",
}
CHART_KINDS = {"bar", "hbar", "line", "area", "doughnut", "pie", "radar"}
COL = {
    "teal": "#1b5e5a",
    "green": "#2c7a66",
    "gold": "#d59a3a",
    "red": "#a24e3e",
    "muted": "#cfd6cd",
}
SOFT = {
    "teal": "rgba(27,94,90,.14)",
    "green": "rgba(44,122,102,.14)",
    "gold": "rgba(213,154,58,.16)",
    "red": "rgba(162,78,62,.14)",
    "muted": "rgba(207,214,205,.30)",
}
TONE_CYCLE = ["teal", "gold", "green", "red", "muted"]

# 手写 deck 也必须命中的 shell 签名（缺一即 shell gate 不过）
SHELL_SIGNATURES = [
    ("暖纸底色令牌", "--bg:#f7f4ee"),
    ("顶部三色条", "linear-gradient(90deg,var(--teal),var(--gold),var(--red))"),
    ("演讲者模式函数", "togglePresenter"),
    ("S 键绑定", "'s'"),
    ("reduced-motion 降级", "prefers-reduced-motion"),
    ("品牌签名", "brand-mark"),
    ("每页配额计时", "timer-bar"),
    # <i class="fill"> 默认 inline，漏了 display:block 会让所有条形整根不显示（曾经真的漏过）
    ("条形填充可见", "display:block;height:100%;width:0"),
]

NOUN_TITLE_RE = re.compile(
    r"(分析|概览|介绍|简介|总结|汇报|情况|说明|思考|概述|回顾|展望|背景|现状)\s*$"
)
PLACEHOLDER_RE = re.compile(r"\{\{[^}]*\}\}")
LEFTOVER_TOKEN_RE = re.compile(r"%%ZIMA_[A-Z_]+%%")
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# class 必须是完整 token：notes-panel / slide-hint 之类的近名不算命中
SECTION_RE = re.compile(
    r'<section\b[^>]*class="(?:[^"]*\s)?slide(?:\s[^"]*)?"[^>]*>.*?</section>', re.DOTALL
)
NOTES_RE = re.compile(
    r'<div\b[^>]*class="(?:[^"]*\s)?notes(?:\s[^"]*)?"[^>]*>.*?</div>', re.DOTALL
)


# --------------------------------------------------------------------------- #
# 通用工具
# --------------------------------------------------------------------------- #

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def die(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def esc(value: Any) -> str:
    """所有用户文本一律 HTML 转义；只有 html 块例外。"""
    return html.escape("" if value is None else str(value), quote=True)


def read_text(path: Path) -> str:
    if not path.exists():
        die(f"文件不存在：{path}")
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        die(f"输出已存在，默认不覆盖：{path}（确认要覆盖再加 --overwrite）")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def new_report(command: str, target: str) -> dict[str, Any]:
    return {
        "tool": "zima_deck",
        "version": SCHEMA_VERSION,
        "command": command,
        "target": target,
        "generatedAt": utc_now(),
        "errors": [],
        "warnings": [],
        "stats": {},
        "gates": {},
        "missingEvidence": ["browser visual review"],
    }


def add_error(report: dict[str, Any], path: str, message: str) -> None:
    report["errors"].append({"path": path, "message": message})


def add_warning(report: dict[str, Any], path: str, message: str) -> None:
    report["warnings"].append({"path": path, "message": message})


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def valid_uuid(value: Any) -> bool:
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def tone_of(value: Any, fallback: str = "teal") -> str:
    return value if value in TONES else fallback


def collect_strings(node: Any, path: str = "$"):
    """深度遍历，产出 (json path, string) —— 用于占位符扫描。"""
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for key, val in node.items():
            yield from collect_strings(val, f"{path}.{key}")
    elif isinstance(node, list):
        for i, val in enumerate(node):
            yield from collect_strings(val, f"{path}[{i}]")


# --------------------------------------------------------------------------- #
# 渲染：block → HTML
# --------------------------------------------------------------------------- #

def render_metrics(block: dict[str, Any]) -> str:
    items = block.get("items") or []
    cols = block.get("cols") or min(max(len(items), 1), 4)
    cells = []
    for item in items:
        tone = tone_of(item.get("tone"))
        cls = "card metric" + ("" if tone == "teal" else f" {tone}")
        value = item.get("value", "")
        attrs = ""
        text = esc(value)
        if item.get("count", True) and is_number(value):
            dec = int(item.get("dec", 0))
            attrs = f' data-count="{esc(value)}"'
            if item.get("suffix"):
                attrs += f' data-suffix="{esc(item["suffix"])}"'
            if item.get("prefix"):
                attrs += f' data-prefix="{esc(item["prefix"])}"'
            if dec:
                attrs += f' data-dec="{dec}"'
            text = "0"
        else:
            text = f'{esc(item.get("prefix", ""))}{esc(value)}{esc(item.get("suffix", ""))}'
        cells.append(
            f'<div class="{cls}"><strong{attrs}>{text}</strong>'
            f'<span>{esc(item.get("label", ""))}</span></div>'
        )
    return f'<div class="grid cols-{cols}">' + "".join(cells) + "</div>"


def render_cards(block: dict[str, Any]) -> str:
    items = block.get("items") or []
    cols = block.get("cols") or min(max(len(items), 1), 4)
    cells = []
    for item in items:
        inner = []
        if item.get("title"):
            inner.append(f'<h3>{esc(item["title"])}</h3>')
        for pill in item.get("pills") or []:
            tone = tone_of(pill.get("tone") if isinstance(pill, dict) else None, "teal")
            text = pill.get("text") if isinstance(pill, dict) else pill
            cls = "pill" + ("" if tone == "teal" else f" {tone}")
            inner.append(f'<span class="{cls}">{esc(text)}</span>')
        if item.get("body"):
            inner.append(f'<p>{esc(item["body"])}</p>')
        if item.get("list"):
            lis = "".join(f"<li>{esc(li)}</li>" for li in item["list"])
            inner.append(f'<ul class="list">{lis}</ul>')
        if item.get("source"):
            inner.append(f'<div class="source">{esc(item["source"])}</div>')
        cells.append('<div class="card">' + "".join(inner) + "</div>")
    return f'<div class="grid cols-{cols}">' + "".join(cells) + "</div>"


def render_list(block: dict[str, Any]) -> str:
    lis = "".join(f"<li>{esc(li)}</li>" for li in block.get("items") or [])
    body = f'<ul class="list">{lis}</ul>'
    if block.get("bare"):
        return body
    return f'<div class="card">{body}</div>'


def render_bars(block: dict[str, Any]) -> str:
    rows = []
    for item in block.get("items") or []:
        tone = tone_of(item.get("tone"))
        style = f'--w:{item.get("pct", 0)}%'
        if tone != "teal":
            style += f";background:var(--{tone})"
        label = esc(item.get("value", f'{item.get("pct", 0)}%'))
        rows.append(
            f'<div class="bar"><b>{esc(item.get("label", ""))}</b>'
            f'<div class="track"><i class="fill" style="{style}"></i></div>'
            f"<span>{label}</span></div>"
        )
    body = "".join(rows)
    if block.get("bare"):
        return body
    return f'<div class="card">{body}</div>'


def render_table(block: dict[str, Any]) -> str:
    head = block.get("head") or []
    num_cols = set(block.get("numCols") or [])
    thead = "".join(f"<th>{esc(h)}</th>" for h in head)
    trs = []
    for row in block.get("rows") or []:
        tds = "".join(
            f'<td class="num">{esc(cell)}</td>' if i in num_cols else f"<td>{esc(cell)}</td>"
            for i, cell in enumerate(row)
        )
        trs.append(f"<tr>{tds}</tr>")
    table = (
        f'<table class="tbl"><thead><tr>{thead}</tr></thead>'
        f'<tbody>{"".join(trs)}</tbody></table>'
    )
    if block.get("source"):
        table += f'<div class="source">{esc(block["source"])}</div>'
    if block.get("bare"):
        return table
    return f'<div class="card">{table}</div>'


def render_chart(block: dict[str, Any]) -> str:
    name = block.get("name", "chart")
    height = block.get("height")
    style = f' style="min-height:{int(height)}px"' if height else ""
    body = f'<div class="chart-wrap"{style}><canvas id="ch_{esc(name)}"></canvas></div>'
    if block.get("source"):
        body += f'<div class="source">{esc(block["source"])}</div>'
    if block.get("bare"):
        return body
    return f'<div class="card">{body}</div>'


def render_quote(block: dict[str, Any]) -> str:
    cite = f'<cite>{esc(block["cite"])}</cite>' if block.get("cite") else ""
    return f'<p class="quote">{esc(block.get("text", ""))}{cite}</p>'


def render_bigline(block: dict[str, Any]) -> str:
    return f'<p class="bigline">{esc(block.get("text", ""))}</p>'


def render_term(block: dict[str, Any]) -> str:
    return f'<pre class="term">{esc(block.get("text", ""))}</pre>'


def render_pills(block: dict[str, Any]) -> str:
    out = []
    for pill in block.get("items") or []:
        tone = tone_of(pill.get("tone") if isinstance(pill, dict) else None, "teal")
        text = pill.get("text") if isinstance(pill, dict) else pill
        cls = "pill" + ("" if tone == "teal" else f" {tone}")
        out.append(f'<span class="{cls}">{esc(text)}</span>')
    return f'<div>{"".join(out)}</div>'


def render_text(block: dict[str, Any]) -> str:
    return f'<p class="sub">{esc(block.get("text", ""))}</p>'


def render_html(block: dict[str, Any]) -> str:
    return str(block.get("html", ""))


RENDERERS = {
    "metrics": render_metrics,
    "cards": render_cards,
    "list": render_list,
    "bars": render_bars,
    "table": render_table,
    "chart": render_chart,
    "quote": render_quote,
    "bigline": render_bigline,
    "term": render_term,
    "pills": render_pills,
    "text": render_text,
    "html": render_html,
}


def render_blocks(blocks: list[dict[str, Any]] | None) -> str:
    return "".join(
        RENDERERS[b["type"]](b) for b in (blocks or []) if b.get("type") in RENDERERS
    )


def render_notes(slide: dict[str, Any]) -> str:
    lines = []
    for note in slide.get("notes") or []:
        if isinstance(note, str):
            lines.append(f"<p>{esc(note)}</p>")
            continue
        tag = note.get("tag", "say")
        label = note.get("label") or NOTE_LABELS.get(tag, "")
        if tag == "cue" and not note.get("label"):
            label = f'{slide.get("min", "")} 分钟 · {label}'
        lines.append(
            f'<p><b class="tag-{esc(tag)}">{esc(label)}</b> {esc(note.get("text", ""))}</p>'
        )
    return (
        f'<div class="notes" data-min="{esc(slide.get("min", 5))}">'
        + "".join(lines)
        + "</div>"
    )


def render_slide(slide: dict[str, Any], index: int, doc: dict[str, Any]) -> str:
    layout = slide.get("layout", "full")
    chart_names = [
        b["name"]
        for b in (slide.get("blocks") or []) + (slide.get("right") or [])
        if b.get("type") == "chart" and b.get("name")
    ]
    attrs = [
        'class="slide active"' if index == 0 else 'class="slide"',
        f'data-min="{esc(slide.get("min", 5))}"',
    ]
    if slide.get("id"):
        attrs.append(f'data-id="{esc(slide["id"])}"')
    if chart_names:
        attrs.append(f'data-chart="{esc(",".join(chart_names))}"')

    head = []
    if slide.get("kicker"):
        head.append(f'<div class="kicker">{esc(slide["kicker"])}</div>')
    if slide.get("title"):
        tag = "h1" if layout in {"cover", "closing"} else "h2"
        head.append(f"<{tag}>{esc(slide['title'])}</{tag}>")
    if slide.get("sub"):
        head.append(f'<p class="sub">{esc(slide["sub"])}</p>')
    header = f"<header>{''.join(head)}</header>"

    left = render_blocks(slide.get("blocks"))
    right = render_blocks(slide.get("right"))
    if layout == "split":
        stage = f'<div class="split"><div class="stack">{left}</div><div class="stack">{right}</div></div>'
    elif layout == "compare":
        stage = f'<div class="compare"><div class="stack">{left}</div><div class="stack">{right}</div></div>'
    else:
        stage = f'<div class="stack">{left}</div>'
    stage = f'<div class="stage">{stage}</div>'

    meta = doc.get("meta") or {}
    foot_left = slide.get("source") or slide.get("footerLeft") or meta.get("speaker") or ""
    foot_right = slide.get("footerRight") or meta.get("footer") or meta.get("date") or ""
    left_cls = ' class="source"' if slide.get("source") else ""
    footer = (
        f'<div class="footer"><span{left_cls}>{esc(foot_left)}</span>'
        f"<span>{esc(foot_right)}</span></div>"
    )

    return (
        f"  <section {' '.join(attrs)}>\n    {header}\n    {stage}\n    {footer}\n  </section>\n"
        f"  {render_notes(slide)}\n"
    )


# --------------------------------------------------------------------------- #
# 图表编译：block → 纯 JSON 的 Chart.js 配置
# --------------------------------------------------------------------------- #

def compile_chart(block: dict[str, Any]) -> dict[str, Any]:
    kind = block.get("kind", "bar")
    labels = block.get("labels") or []
    datasets = []
    for i, ds in enumerate(block.get("datasets") or []):
        tone = tone_of(ds.get("tone"), TONE_CYCLE[i % len(TONE_CYCLE)])
        entry: dict[str, Any] = {"label": ds.get("label", ""), "data": ds.get("data") or []}
        if kind in {"bar", "hbar"}:
            colors = ds.get("tones")
            if colors:
                entry["backgroundColor"] = [COL[tone_of(c)] for c in colors]
            else:
                entry["backgroundColor"] = COL[tone]
            entry["borderRadius"] = 6
        elif kind in {"line", "area"}:
            entry["borderColor"] = COL[tone]
            entry["backgroundColor"] = SOFT[tone]
            entry["tension"] = 0.35
            entry["fill"] = kind == "area"
            entry["pointRadius"] = 3
        elif kind in {"doughnut", "pie"}:
            tones = ds.get("tones") or TONE_CYCLE
            entry["backgroundColor"] = [
                COL[tone_of(tones[j % len(tones)])] for j in range(len(entry["data"]))
            ]
            entry["borderWidth"] = 0
        elif kind == "radar":
            entry["borderColor"] = COL[tone]
            entry["backgroundColor"] = SOFT[tone]
            entry["pointRadius"] = 3
        datasets.append(entry)

    chart_type = {"hbar": "bar", "area": "line"}.get(kind, kind)
    show_legend = len(datasets) > 1 or kind in {"doughnut", "pie"}
    options: dict[str, Any] = {
        "responsive": True,
        "maintainAspectRatio": False,
        "plugins": {
            "legend": {"display": show_legend, "position": "bottom",
                       "labels": {"boxWidth": 12, "font": {"size": 11}}},
            "title": {
                "display": bool(block.get("title")),
                "text": block.get("title", ""),
                "font": {"size": 13, "weight": "700"},
                "color": "#15211f",
            },
        },
    }
    if chart_type not in {"doughnut", "pie", "radar"}:
        options["scales"] = {
            "x": {"grid": {"display": False}},
            "y": {"grid": {"color": "rgba(0,0,0,.06)"}, "beginAtZero": True},
        }
    if kind == "hbar":
        options["indexAxis"] = "y"
    for key, value in (block.get("options") or {}).items():
        options[key] = value

    return {"type": chart_type, "data": {"labels": labels, "datasets": datasets}, "options": options}


def collect_charts(doc: dict[str, Any]) -> dict[str, Any]:
    specs: dict[str, Any] = {}
    for slide in doc.get("slides") or []:
        for block in (slide.get("blocks") or []) + (slide.get("right") or []):
            if block.get("type") == "chart" and block.get("name"):
                specs[block["name"]] = compile_chart(block)
    return specs


# --------------------------------------------------------------------------- #
# 校验
# --------------------------------------------------------------------------- #

def validate_doc(doc: dict[str, Any], report: dict[str, Any], allow_missing_id: bool = False) -> None:
    if doc.get("zima") != SCHEMA_VERSION:
        add_error(report, "$.zima", f'schema 版本必须是 "{SCHEMA_VERSION}"，当前：{doc.get("zima")!r}')
    if not doc.get("title"):
        add_error(report, "$.title", "缺少 deck 标题")
    deck_id = doc.get("deckId")
    if deck_id is None:
        if not allow_missing_id:
            add_error(report, "$.deckId", "缺少 deckId（新建请用 build --new-document 铸一次）")
    elif not valid_uuid(deck_id):
        add_error(report, "$.deckId", f"deckId 不是合法 UUID：{deck_id!r}")

    slides = doc.get("slides")
    if not isinstance(slides, list) or not slides:
        add_error(report, "$.slides", "slides 必须是非空数组")
        return

    # 占位符 / 残留 token 全局扫描
    for path, text in collect_strings(doc):
        if PLACEHOLDER_RE.search(text):
            add_error(report, path, f"存在未替换占位符：{PLACEHOLDER_RE.search(text).group(0)}")
        if LEFTOVER_TOKEN_RE.search(text):
            add_error(report, path, "存在未替换的 shell token（%%ZIMA_…%%）")

    seen_ids: set[str] = set()
    chart_names: dict[str, str] = {}
    total_min = 0
    uses_html_escape_hatch = False

    for i, slide in enumerate(slides):
        base = f"$.slides[{i}]"
        sid = slide.get("id")
        if sid:
            if sid in seen_ids:
                add_error(report, f"{base}.id", f"slide id 重复：{sid}")
            seen_ids.add(sid)

        minutes = slide.get("min")
        if not is_number(minutes) or minutes <= 0:
            add_error(report, f"{base}.min", "每页必须写正数 min（分钟配额），演讲者模式与计时依赖它")
        else:
            total_min += minutes

        layout = slide.get("layout", "full")
        if layout not in LAYOUTS:
            add_error(report, f"{base}.layout", f"未知 layout：{layout!r}（可用：{sorted(LAYOUTS)}）")
        if layout in {"split", "compare"} and not slide.get("right"):
            add_error(report, f"{base}.right", f"layout={layout} 必须提供 right 栏内容")

        title = slide.get("title")
        if not title:
            add_error(report, f"{base}.title", "缺少页标题")
        elif NOUN_TITLE_RE.search(str(title)) and not re.search(r"\d", str(title)):
            add_warning(report, f"{base}.title", f"名词式标题「{title}」——改成结论句（如「营收四个季度翻倍」）")

        notes = slide.get("notes") or []
        note_text = "".join(
            n if isinstance(n, str) else str(n.get("text", "")) for n in notes
        ).strip()
        if not note_text:
            add_error(report, f"{base}.notes", "缺少逐字稿——演讲者模式是本技能的硬要求，不是可选项")
        else:
            if len(note_text) < 40:
                add_warning(report, f"{base}.notes", f"逐字稿仅 {len(note_text)} 字，台上不够用")
            tags = {n.get("tag") for n in notes if isinstance(n, dict)}
            if not tags & {"say", "data"}:
                add_warning(report, f"{base}.notes", "没有 say/data 标签——演讲者窗口里没有可直接念的橙字")
            for j, note in enumerate(notes):
                if isinstance(note, dict) and note.get("tag") not in NOTE_TAGS:
                    add_error(report, f"{base}.notes[{j}].tag",
                              f'未知标签 {note.get("tag")!r}（可用：{sorted(NOTE_TAGS)}）')

        blocks = (slide.get("blocks") or []) + (slide.get("right") or [])
        if not blocks and layout != "closing":
            add_warning(report, f"{base}.blocks", "本页没有内容块，只有标题")

        tones_used: set[str] = set()
        has_data_block = False
        for j, block in enumerate(blocks):
            bpath = f"{base}.blocks[{j}]"
            btype = block.get("type")
            if btype not in BLOCK_TYPES:
                add_error(report, f"{bpath}.type", f"未知块类型：{btype!r}（可用：{sorted(BLOCK_TYPES)}）")
                continue
            if btype == "html":
                uses_html_escape_hatch = True
                add_warning(report, bpath, "使用了 html 逃生口——绕过结构校验，交付前人工确认样式与转义")
            if btype in {"metrics", "chart", "table", "bars"}:
                has_data_block = True
            for item in block.get("items") or []:
                if isinstance(item, dict) and item.get("tone") in TONES:
                    tones_used.add(item["tone"])
            validate_block(block, bpath, report, chart_names)

        accents = tones_used - {"muted"}
        if len(accents) > 2:
            add_warning(report, base, f"本页用了 {len(accents)} 种强调色（{sorted(accents)}）——规范是一页 ≤ 2 种")
        if has_data_block and not slide.get("source"):
            add_warning(report, f"{base}.source", "本页有数据块但没写来源")

    report["stats"] = {
        "slides": len(slides),
        "totalMinutes": total_min,
        "charts": len(chart_names),
        "htmlEscapeHatch": uses_html_escape_hatch,
    }
    if len(slides) < 12:
        add_warning(report, "$.slides", f"共 {len(slides)} 页，低于规范建议的 12–25 页")
    elif len(slides) > 25:
        add_warning(report, "$.slides", f"共 {len(slides)} 页，高于规范建议的 12–25 页")
    if total_min and not 10 <= total_min <= 180:
        add_warning(report, "$.slides", f"总配额 {total_min} 分钟，超出常见讲演区间（10–180）")


def validate_block(block: dict[str, Any], bpath: str, report: dict[str, Any],
                   chart_names: dict[str, str]) -> None:
    btype = block["type"]

    if btype == "metrics":
        for k, item in enumerate(block.get("items") or []):
            if item.get("count", True) and not is_number(item.get("value")):
                add_warning(report, f"{bpath}.items[{k}].value",
                            "非数字值不会触发滚动动画；如是文字请显式写 \"count\": false")

    elif btype == "bars":
        for k, item in enumerate(block.get("items") or []):
            pct = item.get("pct")
            if not is_number(pct) or not 0 <= pct <= 100:
                add_error(report, f"{bpath}.items[{k}].pct", f"pct 必须是 0–100 的数字，当前：{pct!r}")

    elif btype == "table":
        head = block.get("head") or []
        if not head:
            add_error(report, f"{bpath}.head", "表格缺少表头")
        for k, row in enumerate(block.get("rows") or []):
            if len(row) != len(head):
                add_error(report, f"{bpath}.rows[{k}]",
                          f"列数 {len(row)} 与表头 {len(head)} 不一致")

    elif btype == "chart":
        name = block.get("name")
        if not name:
            add_error(report, f"{bpath}.name", "chart 必须有唯一 name（用于 data-chart 与 canvas id）")
        elif not re.fullmatch(r"[A-Za-z0-9_]+", str(name)):
            add_error(report, f"{bpath}.name", f"chart name 只允许字母数字下划线：{name!r}")
        elif name in chart_names:
            add_error(report, f"{bpath}.name", f"chart name 重复：{name}（已用于 {chart_names[name]}）")
        else:
            chart_names[str(name)] = bpath
        kind = block.get("kind", "bar")
        if kind not in CHART_KINDS:
            add_error(report, f"{bpath}.kind", f"未知图表类型：{kind!r}（可用：{sorted(CHART_KINDS)}）")
        if not block.get("labels"):
            add_error(report, f"{bpath}.labels", "图表缺少 labels")
        datasets = block.get("datasets") or []
        if not datasets:
            add_error(report, f"{bpath}.datasets", "图表缺少 datasets")
        for k, ds in enumerate(datasets):
            data = ds.get("data")
            if not isinstance(data, list) or not data:
                add_error(report, f"{bpath}.datasets[{k}].data", "data 必须是非空数组")
                continue
            if not all(is_number(v) or v is None for v in data):
                add_error(report, f"{bpath}.datasets[{k}].data", "data 必须是纯数字（禁字符串数字）")
            if len(data) != len(block.get("labels") or []):
                add_warning(report, f"{bpath}.datasets[{k}].data",
                            f"数据点 {len(data)} 个，labels {len(block.get('labels') or [])} 个，对不齐")
        raw = json.dumps(block.get("options") or {}, ensure_ascii=False)
        if "function" in raw or "=>" in raw:
            add_error(report, f"{bpath}.options",
                      "chart options 必须是纯 JSON——禁止 function formatter（会被 JSON 序列化吞掉）")

    elif btype == "text":
        if len(str(block.get("text", ""))) > 220:
            add_warning(report, f"{bpath}.text", "单块正文超过 220 字——讲演页靠数字和图说话，不靠段落")

    elif btype in {"quote", "bigline", "term"}:
        if not block.get("text"):
            add_error(report, f"{bpath}.text", f"{btype} 缺少 text")


def validate_html(text: str, report: dict[str, Any]) -> None:
    """对任意 zima deck HTML（build 产物或手写 starter 派生）跑 shell + 结构闸门。"""
    missing = [label for label, needle in SHELL_SIGNATURES if needle not in text]
    report["gates"]["shell"] = "pass" if not missing else "fail"
    for label in missing:
        add_error(report, "shell", f"shell 签名缺失：{label}")

    body = COMMENT_RE.sub("", text)  # 注释里的示例代码不参与结构统计
    sections = SECTION_RE.findall(body)
    notes = NOTES_RE.findall(body)
    report["stats"]["slides"] = len(sections)
    report["stats"]["notes"] = len(notes)
    if not sections:
        add_error(report, "html", "没有找到任何 <section class=\"slide\">")
    if len(notes) < len(sections):
        add_error(report, "html",
                  f"逐字稿 {len(notes)} 段 < 幻灯片 {len(sections)} 页——有页面没写 .notes")

    total_min = 0
    for i, section in enumerate(sections):
        match = re.search(r'data-min="([^"]+)"', section)
        if not match:
            add_error(report, f"section[{i}]", "缺少 data-min 配额")
        else:
            try:
                total_min += float(match.group(1))
            except ValueError:
                add_error(report, f"section[{i}]", f"data-min 不是数字：{match.group(1)!r}")
        for name in re.findall(r'data-chart="([^"]+)"', section):
            for one in [n.strip() for n in name.split(",") if n.strip()]:
                if f'id="ch_{one}"' not in body:
                    add_error(report, f"section[{i}]", f'data-chart="{one}" 没有对应的 <canvas id="ch_{one}">')
    report["stats"]["totalMinutes"] = total_min

    for hit in set(PLACEHOLDER_RE.findall(body)):
        add_error(report, "html", f"存在未替换占位符：{hit}")
    for hit in set(LEFTOVER_TOKEN_RE.findall(body)):
        add_error(report, "html", f"存在未替换的 shell token：{hit}")

    for i, note in enumerate(notes):
        inner = re.sub(r"<[^>]+>", "", note).strip()
        if not inner:
            add_error(report, f"notes[{i}]", "逐字稿是空的")

    report["gates"]["structure"] = "fail" if report["errors"] else "pass"


# --------------------------------------------------------------------------- #
# 构建 / 反解
# --------------------------------------------------------------------------- #

def normalize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """顶层键归位：身份和标题排在前面，别让新铸的 deckId 掉到 slides 后面去。"""
    head = ["zima", "deckId", "title", "meta", "slides"]
    ordered = {k: doc[k] for k in head if k in doc}
    ordered.update({k: v for k, v in doc.items() if k not in ordered})
    return ordered


def serialize_doc(doc: dict[str, Any]) -> str:
    """内嵌文档源；`<` 一律转义为 \\u003c，杜绝 </script> 断出。"""
    raw = json.dumps(doc, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    return DOC_OPEN + "\n" + raw + "\n" + DOC_CLOSE


def extract_doc(text: str) -> dict[str, Any] | None:
    match = DOC_BLOCK_RE.search(text)
    if not match:
        return None
    return json.loads(match.group("body"))


def build_html(doc: dict[str, Any]) -> str:
    shell = read_text(SHELL_PATH)
    meta = doc.get("meta") or {}
    slides_html = "".join(
        render_slide(slide, i, doc) for i, slide in enumerate(doc.get("slides") or [])
    )
    charts = json.dumps(collect_charts(doc), ensure_ascii=False)
    out = shell.replace("%%ZIMA_TITLE%%", esc(doc.get("title", "")))
    out = out.replace("%%ZIMA_SLIDES%%", slides_html.rstrip("\n"))
    out = out.replace("%%ZIMA_CHARTS%%", charts)
    out = out.replace("%%ZIMA_BRAND%%", esc(meta.get("brand", "✦ ZimaBlueAI")))
    out = out.replace("%%ZIMA_BRAND_URL%%", esc(meta.get("brandUrl", "https://www.zimablueai.com")))
    out = out.replace("%%ZIMA_DOC%%", serialize_doc(doc))
    return out


def legacy_extract(text: str, title: str) -> dict[str, Any]:
    """手写 deck 的兜底反解：整段 HTML 收进 html 块，保真优先。"""
    text = COMMENT_RE.sub("", text)  # 注释里的用法示例不是真页面
    sections = SECTION_RE.findall(text)
    notes = NOTES_RE.findall(text)
    slides = []
    for i, section in enumerate(sections):
        min_match = re.search(r'data-min="([^"]+)"', section)
        kicker = re.search(r'class="kicker"[^>]*>(.*?)</div>', section, re.DOTALL)
        heading = re.search(r"<h[12][^>]*>(.*?)</h[12]>", section, re.DOTALL)
        note_html = ""
        if i < len(notes):
            note_html = re.sub(r"^<div[^>]*>|</div>$", "", notes[i].strip(), flags=re.DOTALL)
        inner = re.sub(r"^<section[^>]*>|</section>$", "", section.strip(), flags=re.DOTALL)
        try:
            minutes: float = float(min_match.group(1)) if min_match else 5.0
        except ValueError:
            minutes = 5.0  # data-min 写坏了先兜住，后面 validate 会点名
        slides.append({
            "id": f"s{i + 1:02d}",
            "min": minutes,
            "layout": "full",
            "kicker": re.sub(r"<[^>]+>", "", kicker.group(1)).strip() if kicker else "",
            "title": re.sub(r"<[^>]+>", "", heading.group(1)).strip() if heading else "",
            "blocks": [{"type": "html", "html": inner.strip()}],
            "notes": [{"tag": "say", "label": "【原稿】", "text": re.sub(r"<[^>]+>", " ", note_html).strip()}],
            "_legacyNotesHtml": note_html.strip(),
        })
    return {
        "zima": SCHEMA_VERSION,
        "deckId": str(uuid.uuid4()),
        "title": title,
        "meta": {"note": "legacy extract：由手写 deck 反解，页面内容整段落在 html 块里"},
        "slides": slides,
    }


# --------------------------------------------------------------------------- #
# 子命令
# --------------------------------------------------------------------------- #

def command_locate(args: argparse.Namespace) -> int:
    assets = {
        "shell": SHELL_PATH,
        "starter": STARTER_PATH,
        "designSystem": DESIGN_SYSTEM,
        "speakerMode": SPEAKER_MODE,
    }
    found = {k: v.exists() for k, v in assets.items()}
    payload = {
        "tool": "zima_deck",
        "version": SCHEMA_VERSION,
        "skillRoot": str(SKILL_ROOT),
        "assets": {k: {"path": str(v), "present": found[k]} for k, v in assets.items()},
        "standalone": all(found.values()),
        "network": "not required",
        "generatedAt": utc_now(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["standalone"] else 1


def command_extract(args: argparse.Namespace) -> int:
    src = Path(args.input)
    text = read_text(src)
    doc = extract_doc(text)
    mode = "zima-doc"
    if doc is None:
        if not args.legacy:
            die(
                f"{src} 里没有 #zima-doc 文档块——它不是 build 产物。"
                "手写 deck 请加 --legacy 做兜底反解（页面内容会整段落进 html 块）。"
            )
        title_match = re.search(r"<title>(.*?)</title>", text, re.DOTALL)
        doc = legacy_extract(text, title=title_match.group(1).strip() if title_match else src.stem)
        mode = "legacy"
    out = Path(args.output) if args.output else src.with_suffix(".json")
    write_text(out, json.dumps(doc, ensure_ascii=False, indent=2) + "\n", args.overwrite)
    print(json.dumps({
        "command": "extract", "input": str(src), "output": str(out),
        "deckId": doc.get("deckId"), "slides": len(doc.get("slides") or []), "mode": mode,
    }, ensure_ascii=False, indent=2))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    target = Path(args.input)
    text = read_text(target)
    report = new_report("validate", str(target))

    if target.suffix.lower() in {".html", ".htm"}:
        validate_html(text, report)
        doc = extract_doc(text)
        if doc is not None:
            validate_doc(doc, report)
            report["gates"]["identity"] = "pass" if valid_uuid(doc.get("deckId")) else "fail"
        else:
            report["warnings"].append({
                "path": "html",
                "message": "无 #zima-doc 文档块——手写 deck，只跑了 HTML 层闸门，未做内容契约校验",
            })
    else:
        doc = json.loads(text)
        validate_doc(doc, report)
        report["gates"]["structure"] = "fail" if report["errors"] else "pass"
        report["gates"]["identity"] = "pass" if valid_uuid(doc.get("deckId")) else "fail"

    report["gates"]["quality"] = "pass" if not report["warnings"] else "warn"
    report["ok"] = not report["errors"]
    emit_report(report, args.report)
    return 0 if report["ok"] else 1


def command_build(args: argparse.Namespace) -> int:
    src = Path(args.input)
    doc = json.loads(read_text(src))
    report = new_report("build", str(src))

    # —— 身份闸门 —— #
    if args.new_document:
        if doc.get("deckId") and not args.overwrite_identity:
            die("deck.json 已带 deckId，不能当新文档重铸身份（去掉 --new-document，或加 --overwrite-identity）")
        doc["deckId"] = str(uuid.uuid4())
        report["gates"]["identity"] = "minted"
    elif args.identity_source:
        source_doc = extract_doc(read_text(Path(args.identity_source)))
        if source_doc is None:
            die(f"{args.identity_source} 里没有 #zima-doc，取不到身份")
        source_id = source_doc.get("deckId")
        if doc.get("deckId") and doc["deckId"] != source_id:
            die(f"deckId 与身份来源不一致：{doc.get('deckId')} ≠ {source_id}（拒绝构建）")
        doc["deckId"] = source_id
        report["gates"]["identity"] = "preserved"
    elif not doc.get("deckId"):
        die("deck.json 缺少 deckId：新建加 --new-document，改稿加 --identity-source 原文件.html")
    else:
        report["gates"]["identity"] = "reused"

    doc.setdefault("zima", SCHEMA_VERSION)
    doc = normalize_doc(doc)
    validate_doc(doc, report)
    report["gates"]["structure"] = "fail" if report["errors"] else "pass"
    if report["errors"] and not args.force:
        report["ok"] = False
        emit_report(report, args.report)
        print("build 中止：结构闸门未过（确认要带病产出可加 --force）", file=sys.stderr)
        return 1

    html_out = build_html(doc)
    html_report = new_report("build:htmlgate", str(src))
    validate_html(html_out, html_report)
    report["gates"]["shell"] = html_report["gates"].get("shell", "unknown")
    report["errors"].extend(html_report["errors"])
    report["warnings"].extend(html_report["warnings"])
    report["stats"].update({
        "htmlSlides": html_report["stats"].get("slides"),
        "htmlNotes": html_report["stats"].get("notes"),
        "bytes": len(html_out.encode("utf-8")),
    })

    out = Path(args.output)
    if args.identity_source and Path(args.identity_source).resolve() == out.resolve() and not args.overwrite:
        die("输出与身份来源是同一个文件——默认不原地覆盖（回滚边界）。改个输出名，或显式 --overwrite")
    write_text(out, html_out, args.overwrite)
    report["output"] = str(out)
    report["gates"]["rollback"] = "source-preserved"
    report["gates"]["quality"] = "pass" if not report["warnings"] else "warn"
    report["ok"] = not report["errors"]

    # deck.json 回写（把铸好的身份落盘，便于下次改稿）
    if args.write_back:
        write_text(src, json.dumps(doc, ensure_ascii=False, indent=2) + "\n", overwrite=True)
        report["deckJsonWrittenBack"] = str(src)

    emit_report(report, args.report)
    return 0 if report["ok"] else 1


def emit_report(report: dict[str, Any], report_path: str | None) -> None:
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if report_path:
        path = Path(report_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload + "\n", encoding="utf-8")
    summary = {
        "ok": report.get("ok"),
        "errors": len(report["errors"]),
        "warnings": len(report["warnings"]),
        "gates": report["gates"],
        "stats": report["stats"],
    }
    if report.get("output"):
        summary["output"] = report["output"]
    if report_path:
        summary["report"] = report_path
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    for err in report["errors"]:
        print(f"  ERROR  {err['path']}: {err['message']}", file=sys.stderr)
    for warn in report["warnings"]:
        print(f"  warn   {warn['path']}: {warn['message']}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zima_deck.py",
        description="ZimaBlue Editorial 讲演 deck 构建 / 反解 / 校验",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("locate", help="检查技能自带资产是否齐全")

    p_extract = sub.add_parser("extract", help="从 .html 反解出 deck.json")
    p_extract.add_argument("input")
    p_extract.add_argument("--output")
    p_extract.add_argument("--legacy", action="store_true", help="手写 deck 兜底反解")
    p_extract.add_argument("--overwrite", action="store_true")

    p_validate = sub.add_parser("validate", help="校验 deck.json 或 deck.html")
    p_validate.add_argument("input")
    p_validate.add_argument("--report", help="把完整报告写到此 JSON 路径")

    p_build = sub.add_parser("build", help="deck.json → 单文件 .html")
    p_build.add_argument("input")
    p_build.add_argument("--output", required=True)
    p_build.add_argument("--new-document", action="store_true", help="新建 deck：铸一次 deckId")
    p_build.add_argument("--identity-source", help="改稿：从原 .html 继承 deckId 与身份")
    p_build.add_argument("--overwrite-identity", action="store_true", help="强行重铸已有身份（危险）")
    p_build.add_argument("--overwrite", action="store_true", help="允许覆盖已存在的输出文件")
    p_build.add_argument("--force", action="store_true", help="结构闸门未过也强行产出")
    p_build.add_argument("--write-back", action="store_true", help="把铸好的 deckId 回写进 deck.json")
    p_build.add_argument("--report", help="把完整报告写到此 JSON 路径")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    handlers = {
        "locate": command_locate,
        "extract": command_extract,
        "validate": command_validate,
        "build": command_build,
    }
    raise SystemExit(handlers[args.command](args))


if __name__ == "__main__":
    main()
