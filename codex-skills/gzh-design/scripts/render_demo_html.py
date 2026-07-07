#!/usr/bin/env python3
"""Render bundled demo Markdown files into gzh-design demo HTML.

This is a deterministic demo renderer, not the full gzh-design layout engine.
It creates compliant clean section HTML under assets/demo-html/clean/ and
copy-ready HTML with a one-click-copy toolbar under assets/demo-html/.
"""

from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path


THEMES = {
    "01": ("科技蓝图", "tech-blueprint", "#2563EB", "#EFF6FF", "#0F172A", "#334155", "TECH BLUEPRINT"),
    "02": ("极客终端风", "geek-terminal", "#16A34A", "#0B1220", "#F9FAFB", "#D1D5DB", "GEEK TERMINAL"),
    "03": ("AI 星云风", "ai-nebula", "#7C3AED", "#F5F3FF", "#1E1B4B", "#475569", "AI NEBULA"),
    "04": ("文艺杂志风", "literary-zine", "#B45309", "#FFFBEB", "#292524", "#57534E", "LITERARY ZINE"),
    "05": ("自媒体栏目风", "creator-media", "#F97316", "#FFF7ED", "#1F2937", "#4B5563", "CREATOR MEDIA"),
    "06": ("产品宣发风", "product-launch", "#0EA5E9", "#F0F9FF", "#0F172A", "#475569", "PRODUCT LAUNCH"),
    "07": ("公益倡议风", "public-welfare", "#0F766E", "#F0FDFA", "#134E4A", "#475569", "PUBLIC GOOD"),
}


def leaf(text: str, style: str | None = None) -> str:
    text = html.escape(text, quote=False)
    if style:
        return f'<span leaf="" style="{style}">{text}</span>'
    return f'<span leaf="">{text}</span>'


def inline(text: str, accent: str) -> str:
    text = text.strip()
    parts: list[str] = []
    pos = 0
    pattern = re.compile(r"(\*\*([^*]+)\*\*|==([^=]+)==|`([^`]+)`)")
    for match in pattern.finditer(text):
        if match.start() > pos:
            parts.append(leaf(text[pos:match.start()]))
        if match.group(2):
            parts.append(leaf(match.group(2), f"color:{accent};font-weight:700;"))
        elif match.group(3):
            parts.append(leaf(match.group(3), f"border-bottom:2px solid {accent};font-weight:700;"))
        elif match.group(4):
            parts.append(leaf(match.group(4), "font-family:Consolas,Monaco,monospace;background:#F3F4F6;padding:1px 4px;border-radius:4px;"))
        pos = match.end()
    if pos < len(text):
        parts.append(leaf(text[pos:]))
    return "".join(parts)


def para(text: str, accent: str, body: str) -> str:
    return (
        f'<p style="margin:0 0 14px;font-size:15px;line-height:1.95;color:{body};">'
        f"{inline(text, accent)}</p>"
    )


def render_table(lines: list[str], accent: str) -> str:
    rows = []
    for line in lines:
        if re.match(r"^\|\s*-", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        rows.append(cells)
    out = [f'<section style="margin:18px 0;border:1px solid #E5E7EB;border-radius:10px;overflow:hidden;">']
    for i, cells in enumerate(rows):
        bg = "#F9FAFB" if i == 0 else "#FFFFFF"
        weight = "700" if i == 0 else "400"
        out.append(f'<section style="display:flex;background:{bg};border-bottom:1px solid #E5E7EB;">')
        for cell in cells:
            out.append(
                f'<p style="flex:1;margin:0;padding:10px;font-size:13px;line-height:1.7;color:#374151;font-weight:{weight};">'
                f"{leaf(cell)}</p>"
            )
        out.append("</section>")
    out.append("</section>")
    return "\n".join(out)


def render_markdown(md: str, theme: tuple[str, str, str, str, str, str, str]) -> str:
    theme_name, theme_id, accent, pale, dark, body, label = theme
    lines = md.splitlines()
    title = ""
    blocks: list[str] = []
    quote_buffer: list[str] = []
    list_buffer: list[str] = []
    table_buffer: list[str] = []
    code_buffer: list[str] = []
    in_code = False

    def flush_quote() -> None:
        nonlocal quote_buffer
        if quote_buffer:
            text = " ".join(quote_buffer)
            blocks.append(
                f'<section style="margin:18px 0;padding:16px 18px;border-radius:12px;background:{pale};border-left:4px solid {accent};">'
                f'<p style="margin:0;font-size:15px;line-height:1.9;color:{dark};font-weight:600;">{inline(text, accent)}</p>'
                f"</section>"
            )
            quote_buffer = []

    def flush_list() -> None:
        nonlocal list_buffer
        if list_buffer:
            items = []
            for item in list_buffer:
                items.append(
                    f'<p style="margin:0 0 8px;font-size:15px;line-height:1.85;color:{body};">'
                    f'{leaf("• ", f"color:{accent};font-weight:800;")}{inline(item, accent)}</p>'
                )
            blocks.append(f'<section style="margin:14px 0 18px;padding:14px 16px;border-radius:12px;background:#FFFFFF;border:1px solid #E5E7EB;">{"".join(items)}</section>')
            list_buffer = []

    def flush_table() -> None:
        nonlocal table_buffer
        if table_buffer:
            blocks.append(render_table(table_buffer, accent))
            table_buffer = []

    def flush_code() -> None:
        nonlocal code_buffer
        if code_buffer:
            rows = []
            for row in code_buffer:
                rows.append(f'<p style="margin:0;font-size:13px;line-height:1.7;color:#D1FAE5;font-family:Consolas,Monaco,monospace;">{leaf(row)}</p>')
            blocks.append(f'<section style="margin:18px 0;padding:16px;border-radius:10px;background:#0F172A;overflow:auto;">{"".join(rows)}</section>')
            code_buffer = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("```"):
            if in_code:
                in_code = False
                flush_code()
            else:
                flush_quote()
                flush_list()
                flush_table()
                in_code = True
            continue
        if in_code:
            code_buffer.append(line)
            continue
        if not line.strip():
            flush_quote()
            flush_list()
            flush_table()
            continue
        if line.startswith("# "):
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            flush_quote()
            flush_list()
            flush_table()
            idx = sum(1 for b in blocks if "SECTION-NO" in b) + 1
            heading = line[3:].strip()
            blocks.append(
                f'<section style="margin:28px 0 14px;padding:0 0 0 12px;border-left:4px solid {accent};" data-note="SECTION-NO">'
                f'<p style="margin:0 0 4px;font-size:12px;color:{accent};font-weight:800;">{leaf(f"{idx:02d} / {label}")}</p>'
                f'<h2 style="margin:0;font-size:20px;line-height:1.45;color:{dark};font-weight:900;">{leaf(heading)}</h2>'
                f"</section>"
            )
            continue
        if line.startswith(">"):
            quote_buffer.append(line.lstrip(">").strip())
            continue
        if line.startswith("|"):
            flush_quote()
            flush_list()
            table_buffer.append(line)
            continue
        m = re.match(r"^(\d+\.|-)\s+(.+)$", line)
        if m:
            flush_quote()
            flush_table()
            list_buffer.append(m.group(2))
            continue
        flush_quote()
        flush_list()
        flush_table()
        blocks.append(para(line, accent, body))

    flush_quote()
    flush_list()
    flush_table()
    flush_code()

    cover = (
        f'<section style="margin:0 auto 24px;padding:26px 22px;border-radius:16px;background:{pale};border:1px solid #E5E7EB;">'
        f'<p style="margin:0 0 10px;font-size:13px;color:{accent};font-weight:900;">{leaf(label)}</p>'
        f'<h1 style="margin:0 0 14px;font-size:24px;line-height:1.35;color:{dark};font-weight:900;">{leaf(title)}</h1>'
        f'<p style="margin:0;font-size:14px;line-height:1.8;color:{body};">{leaf(f"Demo 主题：{theme_name}。这是一份可复制到公众号编辑器的预览样张。")}</p>'
        f"</section>"
    )
    footer = (
        f'<section style="margin:28px 0 0;padding:18px;border-radius:14px;background:#F9FAFB;border:1px solid #E5E7EB;">'
        f'<p style="margin:0;font-size:14px;line-height:1.9;color:{body};">{leaf("我是 {{作者名}}，{{一句话简介}}。如果这篇文章对你有帮助，欢迎点赞、在看、转发。")}</p>'
        f"</section>"
    )
    return (
        f'<section style="max-width:677px;margin:0 auto;padding:0 12px;font-family:-apple-system,BlinkMacSystemFont,'
        f"'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;\">"
        f"\n{cover}\n" + "\n".join(blocks).replace(' data-note="SECTION-NO"', "") + f"\n{footer}\n</section>\n"
    )


def wrap_copy_page(root: Path, title: str, content: str) -> str:
    tpl_path = root / "assets" / "preview-template.html"
    tpl = tpl_path.read_text(encoding="utf-8")
    return tpl.replace("{{TITLE}}", title).replace("<!--GZH_CONTENT-->", content.strip())


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    case_dir = root / "assets" / "demo-cases"
    out_dir = root / "assets" / "demo-html"
    clean_dir = out_dir / "clean"
    out_dir.mkdir(parents=True, exist_ok=True)
    clean_dir.mkdir(parents=True, exist_ok=True)
    for md_path in sorted(case_dir.glob("*.md")):
        prefix = md_path.name[:2]
        if prefix not in THEMES:
            continue
        theme = THEMES[prefix]
        html_text = render_markdown(md_path.read_text(encoding="utf-8"), theme)
        stem = md_path.stem
        theme_name, theme_id = theme[0], theme[1]
        clean_path = clean_dir / f"{stem}_正文片段_{theme_name}({theme_id}).html"
        copy_path = out_dir / f"{stem}_一键复制_{theme_name}({theme_id}).html"
        clean_path.write_text(html_text, encoding="utf-8")
        copy_path.write_text(wrap_copy_page(root, stem, html_text), encoding="utf-8")
        print(copy_path)
        print(f"  clean: {clean_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
