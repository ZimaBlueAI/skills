#!/usr/bin/env python3
"""从仓库根的 skill 目录生成两个 harness 的安装包。

    python packaging/build.py                 # 全量构建到 dist/
    python packaging/build.py --only viz-deck # 只构建某个包
    python packaging/build.py --verify        # 构建后与 legacy zip 逐字节核对
    python packaging/build.py --check         # 只检查源，不写产物

产物：
    dist/claude/<archive>.zip   解到 ~/ 或项目根 → .claude/skills/<name>/ (+ .claude/agents/)
    dist/codex/<archive>.zip    解到 ~/ 或项目根 → .codex/skills/<name>/  (+ .codex/agents/)

差异只来自 packaging/harness.toml：安装根目录，以及三个老 skill 在 Codex 侧的
短 frontmatter。skill 正文永远只有一份，改根下的 skill 目录即可，不要改产物。

只依赖标准库（Python 3.11+ 用内置 tomllib；3.10 及以下退回极简解析器）。
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import time
import sys
import zipfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT  # skill 目录直接放在仓库根，与 packaging/ dist/ docs/ 平级
DIST = ROOT / "dist"
CONFIG = Path(__file__).resolve().parent / "harness.toml"

# 根下这些不是 skill；其余"含顶层 SKILL.md 的目录"才算
NOT_SKILLS = {"packaging", "dist", "docs", "_trash", ".git", ".github", ".claude", ".codex"}

FM_RE = re.compile(r"^(---\r?\n)(.*?)(\r?\n---\r?\n)", re.DOTALL)
# 与 legacy zip 核对时，这些目录不参与（samples 过去散落在两侧，不是 skill 本体）
SKIP_DIRS = {".git", "__pycache__", ".gstack", "node_modules"}


# --------------------------------------------------------------------------- #
# 配置读取
# --------------------------------------------------------------------------- #

def load_config() -> dict:
    text = CONFIG.read_text(encoding="utf-8")
    try:
        import tomllib
        return tomllib.loads(text)
    except ModuleNotFoundError:
        return _mini_toml(text)


def _mini_toml(text: str) -> dict:
    """够用就好的 TOML 子集解析：表、表数组、字符串/布尔/字符串数组、多行字符串。"""
    data: dict = {}
    cur: dict = data
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("#"):
            continue
        if line.startswith("[["):
            key = line[2:-2].strip()
            data.setdefault(key, []).append({})
            cur = data[key][-1]
            continue
        if line.startswith("["):
            parts = [p.strip('"') for p in re.findall(r'"[^"]*"|[^.\[\]]+', line[1:-1])]
            cur = data
            for p in parts:
                p = p.strip()
                if not p:
                    continue
                cur = cur.setdefault(p, {})
            continue
        if "=" not in line:
            continue
        key, _, raw = line.partition("=")
        key, raw = key.strip(), raw.strip()
        if raw == '"""':
            buf = []
            while i < len(lines) and lines[i].rstrip("\r") != '"""':
                buf.append(lines[i].rstrip("\r"))
                i += 1
            i += 1
            cur[key] = "\n".join(buf).replace("\\\\", "\\")
        elif raw.startswith('"""'):
            body = raw[3:]
            if body.endswith('"""'):
                cur[key] = body[:-3]
            else:
                buf = [body]
                while i < len(lines) and not lines[i].rstrip("\r").endswith('"""'):
                    buf.append(lines[i].rstrip("\r"))
                    i += 1
                buf.append(lines[i].rstrip("\r")[:-3])
                i += 1
                cur[key] = "\n".join(buf).replace("\\\\", "\\")
        elif raw.startswith("["):
            cur[key] = [v.strip().strip('"') for v in raw[1:-1].split(",") if v.strip()]
        elif raw in {"true", "false"}:
            cur[key] = raw == "true"
        else:
            cur[key] = raw.strip('"')
    return data


# --------------------------------------------------------------------------- #
# 源检查
# --------------------------------------------------------------------------- #

def iter_files(root: Path):
    for p in sorted(root.rglob("*")):
        if p.is_file() and not any(part in SKIP_DIRS for part in p.parts):
            yield p


def discover_skills() -> set[str]:
    """根下带顶层 SKILL.md 的目录就是一个 skill。"""
    return {
        d.name for d in SKILLS.iterdir()
        if d.is_dir() and d.name not in NOT_SKILLS and (d / "SKILL.md").is_file()
    }


def check_sources(cfg: dict) -> list[str]:
    problems = []
    declared = {s for pkg in cfg.get("package", []) for s in pkg.get("skills", [])}
    on_disk = discover_skills()
    for missing in sorted(declared - on_disk):
        problems.append(f"harness.toml 声明了 {missing}/，但根下没有这个 skill（缺目录或缺 SKILL.md）")
    for orphan in sorted(on_disk - declared):
        problems.append(f"{orphan}/ 有 SKILL.md 但没被任何 package 声明，不会被打包")
    for name in sorted(declared & on_disk):
        skill_md = SKILLS / name / "SKILL.md"
        if not FM_RE.match(skill_md.read_text(encoding="utf-8")):
            problems.append(f"{name}/SKILL.md 没有合法的 YAML frontmatter")
    for harness, spec in cfg.get("harness", {}).items():
        src = ROOT / spec["agents_source"]
        if not src.is_dir():
            problems.append(f"{harness} 的 agents_source 不存在：{spec['agents_source']}")
    return problems


# --------------------------------------------------------------------------- #
# 构建
# --------------------------------------------------------------------------- #

def skill_md_for(name: str, harness: str, cfg: dict) -> bytes:
    """按 harness 取 frontmatter 变体；没有变体就用单源原文。"""
    text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    override = cfg.get("frontmatter_override", {}).get(harness, {}).get(name)
    if not override:
        return text.encode("utf-8")
    m = FM_RE.match(text)
    # TOML 多行字符串会带上收尾换行，这里剥掉——否则 frontmatter 会多出一个空行
    body = override["text"].rstrip("\r\n")
    return (m.group(1) + body + m.group(3) + text[m.end():]).encode("utf-8")


def build_package(pkg: dict, harness: str, cfg: dict, out_dir: Path) -> Path:
    spec = cfg["harness"][harness]
    archive = out_dir / f"{pkg['archive']}.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    skills_root = spec["skills_root"].rstrip("/")

    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in pkg["skills"]:
            src = SKILLS / name
            for f in iter_files(src):
                rel = f.relative_to(src).as_posix()
                entry = f"{skills_root}/{name}/{rel}"
                if rel == "SKILL.md":
                    # 用源文件 mtime 而不是"现在"，否则同样的源每次构建都产生不同的 zip，
                    # 提交进仓库会变成每次都有一份无意义的二进制 diff
                    info = zipfile.ZipInfo(entry, date_time=time.localtime(f.stat().st_mtime)[:6])
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = (f.stat().st_mode & 0xFFFF) << 16
                    z.writestr(info, skill_md_for(name, harness, cfg))
                else:
                    z.write(f, entry)
        if pkg.get("include_agents"):
            agents_src = ROOT / spec["agents_source"]
            agents_root = spec["agents_root"].rstrip("/")
            for f in iter_files(agents_src):
                z.write(f, f"{agents_root}/{f.name}")
    return archive


# --------------------------------------------------------------------------- #
# 与 legacy zip 核对
# --------------------------------------------------------------------------- #

# 合并前两套目录各自的 zip，已归档到 _trash。--verify 拿它们做一次性回溯核对；
# 归档被清理后这些路径会失效，届时 --verify 只是安静跳过，不影响构建。
_LEGACY_ROOT = "_trash/legacy-harness-dirs-20260727"
LEGACY = {
    ("claude", "biz-decision-stack"): f"{_LEGACY_ROOT}/claude-code-skills/biz-decision-stack/biz-decision-stack.zip",
    ("claude", "viz-deck"): f"{_LEGACY_ROOT}/claude-code-skills/viz-deck/viz-deck.zip",
    ("claude", "viz-charts"): f"{_LEGACY_ROOT}/claude-code-skills/viz-charts/viz-charts.zip",
    ("codex", "biz-decision-stack"): f"{_LEGACY_ROOT}/codex-skills/biz-decision-stack/biz-decision-stack.zip",
    ("codex", "viz-deck"): f"{_LEGACY_ROOT}/codex-skills/viz-deck/viz-deck.zip",
    ("codex", "viz-charts"): f"{_LEGACY_ROOT}/codex-skills/viz-charts/viz-charts.zip",
    ("codex", "zima-html-ppt"): f"{_LEGACY_ROOT}/codex-skills/zima-html-ppt/zima-html-ppt.zip",
    ("codex", "zima-design"): f"{_LEGACY_ROOT}/codex-skills/zima-design/zima-design.zip",
    ("codex", "gzh-design"): f"{_LEGACY_ROOT}/codex-skills/gzh-design/gzh-design.zip",
}


def verify(harness: str, archive_name: str, built: Path) -> str | None:
    legacy_rel = LEGACY.get((harness, archive_name))
    if not legacy_rel:
        return None
    legacy_path = ROOT / legacy_rel
    if not legacy_path.exists():
        return f"    legacy 包已不在：{legacy_rel}"
    old = zipfile.ZipFile(legacy_path)
    new = zipfile.ZipFile(built)
    o = {n: old.read(n) for n in old.namelist() if not n.endswith("/")}
    n_ = {n: new.read(n) for n in new.namelist() if not n.endswith("/")}
    only_old = sorted(set(o) - set(n_))
    only_new = sorted(set(n_) - set(o))
    changed = [k for k in sorted(set(o) & set(n_))
               if hashlib.sha256(o[k]).hexdigest() != hashlib.sha256(n_[k]).hexdigest()]
    if not (only_old or only_new or changed):
        return "    与 legacy 逐字节一致 ✓"
    out = [f"    与 legacy 有差异：新增 {len(only_new)} / 缺失 {len(only_old)} / 变更 {len(changed)}"]
    out += [f"      - 缺失 {k}" for k in only_old[:4]]
    out += [f"      + 新增 {k}" for k in only_new[:4]]
    out += [f"      ~ 变更 {k}" for k in changed[:6]]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="从 skills/ 单源构建两个 harness 的安装包")
    ap.add_argument("--only", help="只构建某个 archive 名")
    ap.add_argument("--harness", choices=["claude", "codex"], help="只构建某个 harness")
    ap.add_argument("--verify", action="store_true", help="构建后与 legacy zip 核对")
    ap.add_argument("--check", action="store_true", help="只检查源，不写产物")
    ap.add_argument("--clean", action="store_true", help="构建前清空 dist/")
    args = ap.parse_args()

    cfg = load_config()
    problems = check_sources(cfg)
    if problems:
        print("源检查未通过：")
        for p in problems:
            print(f"  ✗ {p}")
        return 1
    print(f"源检查通过 · {len(discover_skills())} 个 skill\n")
    if args.check:
        return 0

    if args.clean and DIST.exists():
        shutil.rmtree(DIST)

    harnesses = [args.harness] if args.harness else list(cfg["harness"])
    packages = [p for p in cfg["package"] if not args.only or p["archive"] == args.only]
    if not packages:
        print(f"没有匹配的 package：{args.only}")
        return 1

    total = 0
    for harness in harnesses:
        print(f"── {cfg['harness'][harness]['name']} → dist/{harness}/")
        for pkg in packages:
            built = build_package(pkg, harness, cfg, DIST / harness)
            size = built.stat().st_size / 1024
            with zipfile.ZipFile(built) as z:
                count = len([n for n in z.namelist() if not n.endswith("/")])
            print(f"   {built.name:<32} {size:7.1f} KB  {count:>4} 文件")
            if args.verify:
                msg = verify(harness, pkg["archive"], built)
                if msg:
                    print(msg)
            total += 1
        print()
    print(f"共产出 {total} 个包。skill 源只有一份，改根下的 skill 目录后重跑本脚本即可。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
