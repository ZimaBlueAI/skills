"""Light masters catalog + neumorphic SVG covers (zima-anima style cards, slim)."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
MASTERS_DIR = SKILL / "masters"
CATALOG_PATH = MASTERS_DIR / "catalog.json"
COVERS_DIR = MASTERS_DIR / "covers"

ROLE_ORDER = ("director", "supervisor", "producer")
CREATIVE_ROLES = ("director","art","camera","editor","producer")
DEFAULT_MASTERS = dict(director="青禾",art="砚舟",camera="静岚",editor="听桥",producer="灯塔",supervisor="守衡")


def _esc(text: str) -> str:
    return xml_escape(str(text or ""), {"'": "&apos;", '"': "&quot;"})


def load_raw_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def cover_svg(master: dict[str, Any], *, width: int = 480, height: int = 640) -> str:
    """Abstract style cover — no real-person likeness (same rule as zima-anima)."""
    hue = int(master.get("hue") or 200)
    seed = int(hashlib.sha256(str(master.get("name") or master.get("id") or "?").encode("utf-8")).hexdigest()[:8], 16)

    def rnd(k: int, lo: float, hi: float) -> float:
        return lo + ((seed >> (k * 5)) % 1000) / 1000.0 * (hi - lo)

    bg = f"hsl({hue},18%,88%)"
    hi = f"hsl({hue},22%,96%)"
    lo = f"hsl({hue},14%,72%)"
    acc = f"hsl({hue},45%,42%)"
    soft = f"hsl({hue},35%,78%)"
    sig = list(master.get("signature") or [])[:3]
    n_bars = max(3, min(6, len(sig) or 3))
    bars = "".join(
        f'<rect x="{48 + i * (width - 96) / n_bars:.1f}" y="{height * 0.34 + rnd(i, -24, 28):.1f}" '
        f'width="{(width - 96) / n_bars * 0.52:.1f}" height="{rnd(i + 3, 48, 150):.1f}" rx="14" '
        f'fill="{soft}" opacity="{0.55 + 0.08 * (i % 3):.2f}"/>'
        for i in range(n_bars)
    )
    blobs = "".join(
        f'<circle cx="{rnd(i + 2, 70, width - 70):.1f}" cy="{rnd(i + 8, 90, height * 0.42):.1f}" '
        f'r="{rnd(i + 4, 26, 64):.1f}" fill="{acc}" opacity="0.12"/>'
        for i in range(max(2, len(sig)))
    )
    sig_svg = "".join(
        f'<text x="44" y="{height - 132 + i * 26}" font-size="17" fill="hsl({hue},20%,32%)" opacity="0.88">{_esc(line)}</text>'
        for i, line in enumerate(sig)
    )
    tagline = str(master.get("tagline") or "")[:28]
    title = str(master.get("title") or "")[:24]
    reading = str(master.get("reading") or "")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" font-family="'Nunito','IBM Plex Sans SC','PingFang SC','Microsoft YaHei',sans-serif">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{hi}"/><stop offset="1" stop-color="{bg}"/></linearGradient>
  <filter id="neu" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="10" dy="10" stdDeviation="12" flood-color="{lo}" flood-opacity="0.45"/>
    <feDropShadow dx="-8" dy="-8" stdDeviation="10" flood-color="#ffffff" flood-opacity="0.9"/>
  </filter>
</defs>
<rect width="{width}" height="{height}" rx="36" fill="url(#bg)"/>
<rect x="28" y="28" width="{width - 56}" height="{height - 56}" rx="28" fill="{bg}" filter="url(#neu)"/>
<g>{blobs}{bars}</g>
<text x="48" y="128" font-size="64" font-weight="800" fill="hsl({hue},25%,28%)" letter-spacing="2">{_esc(master.get("name") or "")}</text>
<text x="52" y="162" font-size="16" fill="{acc}" letter-spacing="1">{_esc(reading)} · {_esc(title)}</text>
<text x="48" y="{height - 188}" font-size="20" font-weight="700" fill="hsl({hue},22%,30%)">{_esc(tagline)}</text>
{sig_svg}
<rect x="48" y="{height - 48}" width="{width - 96}" height="4" rx="2" fill="{acc}" opacity="0.75"/>
</svg>
"""


def ensure_covers(catalog: dict[str, Any] | None = None) -> list[Path]:
    catalog = catalog or load_raw_catalog()
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for role in ROLE_ORDER:
        for master in catalog.get(role) or []:
            rel = str(master.get("cover") or f"covers/{master.get('id')}.svg")
            path = MASTERS_DIR / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            svg = cover_svg(master)
            if not path.is_file() or path.read_text(encoding="utf-8") != svg:
                path.write_text(svg, encoding="utf-8")
                written.append(path)
            master["cover"] = rel.replace("\\", "/")
    return written


def enrich_master(master: dict[str, Any], role: str) -> dict[str, Any]:
    item = dict(master)
    item["role"] = role
    cover = str(item.get("cover") or "")
    if cover:
        item["cover_url"] = "/masters/" + cover.lstrip("/")
    else:
        item["cover_url"] = f"/api/masters/cover.svg?id={item.get('id')}"
    item.setdefault("intro", item.get("blurb") or "")
    item.setdefault("signature", [])
    item.setdefault("fit", "")
    item.setdefault("unfit", "")
    return item


def catalog_payload() -> dict[str, Any]:
    raw = load_raw_catalog()
    ensure_covers(raw)
    out: dict[str, Any] = {"roles": raw.get("roles") or {}, "catalog": {}}
    flat: list[dict[str, Any]] = []
    for role in ROLE_ORDER:
        enriched = [enrich_master(m, role) for m in (raw.get(role) or [])]
        out["catalog"][role] = enriched
        flat.extend(enriched)
    people = {m["name"]:m for m in flat}
    departments = {
        "art": ("艺术总监","统一造型、材质与色彩", [("砚舟","从纸张纹理、墨色层次与留白建立世界观。"),("小舟","用微缩布景、手工材质与角色比例统一场景。")]),
        "camera": ("摄影 · 灯光 · 运镜","设计机位、光源与镜头运动", [("静岚","用主辅光比例、色温与机位变化交代人物关系。"),("跃场","用低机位跟拍、轴线与动势组织运动场面。")]),
        "editor": ("剪辑大师","组织表演节拍、声画关系与转场", [("听桥","用声音先入和延迟切出连接空间与情绪。"),("木辞","从视线、呼吸和动作停顿寻找表演切点。")]),
    }
    for role,(title,blurb,choices) in departments.items():
        out["roles"][role] = {"title":title,"blurb":blurb}
        out["catalog"][role] = [dict(people[name],role=role,title=title,tagline=blurb,intro=intro,signature=[blurb],fit=intro,unfit="") for name,intro in choices]
    out["roles"]["supervisor"] = {"title":"工作流监工","blurb":"跟踪流程状态、付费确认与生成队列"}
    out["catalog"]["supervisor"] = [dict(people["守衡"],title="工作流监工",
        tagline="队列与进度",intro="跟踪等待确认、排队与制作中的任务，报告超时或失败，继续调度后续已确认任务。")]
    out["all"] = [m for group in out["catalog"].values() for m in group]
    return out


def find_master(name_or_id: str) -> dict[str, Any] | None:
    needle = (name_or_id or "").strip()
    if not needle:
        return None
    payload = catalog_payload()
    for master in payload["all"]:
        if master.get("id") == needle or master.get("name") == needle:
            return master
    return None


def cover_bytes_for(master_id: str) -> tuple[bytes, str]:
    master = find_master(master_id)
    if not master:
        raise FileNotFoundError(master_id)
    rel = master.get("cover") or ""
    path = MASTERS_DIR / rel
    if path.is_file():
        return path.read_bytes(), "image/svg+xml; charset=utf-8"
    svg = cover_svg(master)
    return svg.encode("utf-8"), "image/svg+xml; charset=utf-8"


def main() -> int:
    written = ensure_covers()
    payload = catalog_payload()
    print(json.dumps({
        "ok": True,
        "covers_written": [str(p.relative_to(SKILL)) for p in written],
        "masters": len(payload["all"]),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
