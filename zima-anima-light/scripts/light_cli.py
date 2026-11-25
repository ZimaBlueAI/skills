#!/usr/bin/env python3
"""CLI entry for Zima Anima Light."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))

import config_env
import legacy_import
import light_studio
import masters_catalog
import project_model
import youth_lookbook
from providers import catalog as provider_catalog
from workflow_defs import WORKFLOWS


def cmd_doctor(_: argparse.Namespace) -> int:
    env = config_env.load_env()
    caps = provider_catalog.capabilities()
    lookbook = youth_lookbook.load_lookbook()
    masters = masters_catalog.catalog_payload()
    packs = list((SKILL / "styles" / "packs").glob("*.json"))
    print(json.dumps({
        "skill": str(SKILL),
        "version": "0.2.0",
        "env_file": str(config_env.env_path()),
        "env_exists": config_env.env_path().is_file(),
        "youth_mode": config_env.truthy("ZIMA_LIGHT_YOUTH_MODE", True),
        "lookbook": {
            "count": lookbook.get("count"),
            "style_count": lookbook.get("style_count"),
            "master_count": lookbook.get("master_count"),
            "packs_on_disk": len(packs),
            "masters_on_disk": len(masters.get("all") or []),
            "agents_dir": str(SKILL / "agents" / "design"),
        },
        "providers": caps,
        "keys_loaded": sorted(k for k in env if not k.endswith("_API_KEY")),
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_lookbook(args: argparse.Namespace) -> int:
    if args.sync:
        result = youth_lookbook.sync(write_packs=True, write_agents=True)
        written = masters_catalog.ensure_covers()
        result["covers_written"] = [str(p.relative_to(SKILL)) for p in written]
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    lookbook = youth_lookbook.load_lookbook()
    print(json.dumps({
        "ok": True,
        "count": lookbook.get("count"),
        "style_count": lookbook.get("style_count"),
        "master_count": lookbook.get("master_count"),
        "path": str(youth_lookbook.LOOKBOOK_PATH),
        "categories": sorted({
            str(i.get("category") or "")
            for i in (lookbook.get("items") or [])
            if i.get("kind") == "style" and i.get("category")
        }),
        "research_notes": lookbook.get("research_notes") or [],
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.project)
    doc = project_model.init_project(root, title=args.title, workflow=args.workflow, style_pack=args.style)
    print(json.dumps({"ok": True, "project": str(root.resolve()), "workflow": doc["workflow"], "title": doc["title"]}, ensure_ascii=False))
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    return light_studio.serve(Path(args.project), host=args.host, port=args.port, open_browser=not args.no_browser)


def cmd_import_legacy(args: argparse.Namespace) -> int:
    dest = Path(args.dest) if args.dest else Path.cwd() / f"light-review-{Path(args.source).resolve().name}"
    doc = legacy_import.import_legacy(Path(args.source), dest, workflow=args.workflow)
    print(json.dumps({
        "ok": True,
        "review_project": str(dest.resolve()),
        "source": str(Path(args.source).resolve()),
        "title": doc["title"],
        "workflow": doc["workflow"],
        "legacy": doc.get("legacy"),
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    import tomllib

    targets = tomllib.loads((SKILL / "installer" / "targets.toml").read_text(encoding="utf-8"))
    key = f"cli.{args.target}"
    # targets.toml uses [cli.xxx] -> nested under cli
    cli = targets.get("cli") or {}
    spec = cli.get(args.target)
    if not spec:
        print(f"Unknown target {args.target}. Known: {', '.join(sorted(cli))}", file=sys.stderr)
        return 2
    dest = Path(spec["user_root"]).expanduser() / "zima-anima-light"
    if args.apply:
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(SKILL, dest, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
        print(json.dumps({"ok": True, "installed": str(dest), "register": spec.get("register"), "note": spec.get("support_note")}, ensure_ascii=False))
    else:
        print(json.dumps({"ok": True, "dry_run": True, "would_install": str(dest), "spec": spec}, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="light_cli.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("doctor")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("init")
    p.add_argument("project")
    p.add_argument("--workflow", choices=WORKFLOWS, default="from_story")
    p.add_argument("--title", default="我的短片")
    p.add_argument("--style", default="warm_school")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("serve")
    p.add_argument("project")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--no-browser", action="store_true")
    p.set_defaults(func=cmd_serve)

    p = sub.add_parser("import-legacy", help="Wrap a full zima-anima project as a Light review shell")
    p.add_argument("source", help="Full project directory with project.json")
    p.add_argument("--dest", help="Review shell directory (defaults to light-review-<source-name> in the current directory)")
    p.add_argument("--workflow", choices=WORKFLOWS, default=None)
    p.set_defaults(func=cmd_import_legacy)

    p = sub.add_parser("lookbook", help="Show or sync youth Lookbook 61 (styles + masters + design agents)")
    p.add_argument("--sync", action="store_true", help="Rewrite packs, masters agent fields, agents/design, covers")
    p.set_defaults(func=cmd_lookbook)

    p = sub.add_parser("install")
    p.add_argument("--target", required=True, help="Host name from installer/targets.toml")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_install)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
