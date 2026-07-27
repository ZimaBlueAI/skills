#!/usr/bin/env python3
"""Versioned workflow control for recoverable video-production projects.

Every manifest mutation first writes an immutable snapshot under the project's
history/versions directory. Redo marks the selected stage as rework and every
dependent descendant as stale. Restore is explicit and never removes versions.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
WORKFLOW_TEMPLATE = SKILL_DIR / "assets" / "workflow.template.json"
ALLOWED_STATUS = {
    "planned",
    "pending",
    "ready",
    "running",
    "review",
    "approved",
    "complete",
    "rework",
    "blocked",
    "fail",
    "warning",
    "stale",
    "skipped",
    "not_required",
    "not_estimable",
}

LEGACY_STAGE_MAP = {
    "script": ("screenwriter",),
    "design": ("character_designer", "scene_designer", "prop_designer"),
    "storyboard": ("storyboard_director",),
    "acquisition": ("storyboard_director",),
    "picture_edit": ("chief_director",),
    "sound_mix": ("sound_director",),
    "finishing": ("chief_director",),
    "qc": ("chief_director",),
}


class WorkflowError(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise WorkflowError(f"Invalid JSON at line {exc.lineno}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise WorkflowError(f"JSON root must be an object: {path}")
    return value


def write_new_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def replace_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.{stamp()}")
    write_new_json(temporary, value)
    os.replace(temporary, path)


def history_paths(project_path: Path) -> tuple[Path, Path]:
    root = project_path.parent / "history"
    return root / "versions", root / "index.json"


def load_index(project_path: Path) -> dict[str, Any]:
    _, index_path = history_paths(project_path)
    if not index_path.is_file():
        return {"version": 1, "project": project_path.name, "entries": []}
    index = read_json(index_path)
    entries = index.get("entries")
    if not isinstance(entries, list):
        raise WorkflowError(f"History index entries must be an array: {index_path}")
    return index


def clean_token(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-")
    return token[:48] or "project"


def snapshot(
    project_path: Path,
    project: dict[str, Any],
    *,
    kind: str,
    reason: str,
    actor: str,
    stage: str = "",
) -> dict[str, Any]:
    versions_dir, index_path = history_paths(project_path)
    version_id = f"{stamp()}-{clean_token(stage or kind)}"
    snapshot_path = versions_dir / f"{version_id}.project.json"
    write_new_json(snapshot_path, project)
    index = load_index(project_path)
    entry = {
        "id": version_id,
        "created_at": now_iso(),
        "kind": kind,
        "stage": stage,
        "reason": reason,
        "actor": actor,
        "manifest": os.path.relpath(snapshot_path, project_path.parent).replace("\\", "/"),
        "title": str(project.get("title") or ""),
    }
    index["updated_at"] = entry["created_at"]
    index["entries"].append(entry)
    replace_json(index_path, index)
    return entry


def template_workflow() -> dict[str, Any]:
    return read_json(WORKFLOW_TEMPLATE)


def project_status(project: dict[str, Any], station_id: str, default: str = "planned") -> str:
    stations = project.get("stations")
    station = stations.get(station_id) if isinstance(stations, dict) else None
    value = str(station.get("status") or default) if isinstance(station, dict) else default
    return value if value in ALLOWED_STATUS else default


def combined_status(values: tuple[str, ...]) -> str:
    if values and all(value in {"approved", "complete"} for value in values):
        return "approved"
    for candidate in ("blocked", "fail", "rework", "stale", "review", "running", "ready"):
        if candidate in values:
            return candidate
    return "planned"


def seed_workflow(project: dict[str, Any], workflow: dict[str, Any]) -> None:
    final = project.get("final") if isinstance(project.get("final"), dict) else {}
    technical = final.get("technical_qc") if isinstance(final.get("technical_qc"), dict) else {}
    audio = project.get("audio") if isinstance(project.get("audio"), dict) else {}
    evaluation = project.get("evaluation") if isinstance(project.get("evaluation"), dict) else {}
    statuses = {
        "brief": "approved" if project.get("brief") else "planned",
        "research": str((project.get("research") or {}).get("status") or "planned")
        if isinstance(project.get("research"), dict)
        else "planned",
        "planning": project_status(project, "screenwriter"),
        "script": project_status(project, "screenwriter"),
        "design": combined_status(
            (
                project_status(project, "character_designer"),
                project_status(project, "scene_designer"),
                project_status(project, "prop_designer"),
            )
        ),
        "storyboard": project_status(project, "storyboard_director"),
        "acquisition": project_status(project, "storyboard_director"),
        "picture_edit": project_status(project, "chief_director"),
        "separation": str((audio.get("separation") or {}).get("status") or "planned")
        if isinstance(audio.get("separation"), dict)
        else "planned",
        "av_sync": str((audio.get("av_sync") or {}).get("status") or "planned")
        if isinstance(audio.get("av_sync"), dict)
        else "planned",
        "sound_mix": project_status(project, "sound_director"),
        "finishing": str(final.get("status") or "planned"),
        "qc": str(technical.get("status") or "planned"),
        "evaluation": str(evaluation.get("status") or "planned"),
        "release": str((project.get("release") or {}).get("status") or "planned")
        if isinstance(project.get("release"), dict)
        else "planned",
        "learning": str((project.get("learning") or {}).get("status") or "planned")
        if isinstance(project.get("learning"), dict)
        else "planned",
    }
    for node in workflow.get("nodes", []):
        if not isinstance(node, dict):
            continue
        value = statuses.get(str(node.get("id") or ""), "planned")
        node["status"] = value if value in ALLOWED_STATUS else "planned"


def ensure_workflow(project: dict[str, Any]) -> dict[str, Any]:
    workflow = project.get("workflow")
    if not isinstance(workflow, dict) or not isinstance(workflow.get("nodes"), list):
        workflow = template_workflow()
        seed_workflow(project, workflow)
        project["workflow"] = workflow
    workflow.setdefault("feedback_edges", [])
    workflow.setdefault("revision_requests", [])
    return workflow


def nodes_by_id(workflow: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for node in workflow.get("nodes", []):
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("id") or "").strip()
        if not node_id:
            raise WorkflowError("Every workflow node needs an id.")
        if node_id in result:
            raise WorkflowError(f"Duplicate workflow node id: {node_id}")
        result[node_id] = node
    return result


def descendants(nodes: dict[str, dict[str, Any]], stage: str) -> list[str]:
    selected: set[str] = set()
    frontier = {stage}
    while frontier:
        next_frontier: set[str] = set()
        for node_id, node in nodes.items():
            dependencies = {str(item) for item in node.get("depends_on", [])}
            if node_id not in selected and dependencies & frontier:
                selected.add(node_id)
                next_frontier.add(node_id)
        frontier = next_frontier
    return [node_id for node_id in nodes if node_id in selected]


def update_legacy(project: dict[str, Any], stage: str, status: str, affected: list[str]) -> None:
    stations = project.get("stations")
    if not isinstance(stations, dict):
        return
    for station_id in LEGACY_STAGE_MAP.get(stage, ()):
        station = stations.get(station_id)
        if isinstance(station, dict):
            station["status"] = "rework" if status == "rework" else status
            station["updated_at"] = now_iso()
    for affected_stage in affected:
        for station_id in LEGACY_STAGE_MAP.get(affected_stage, ()):
            station = stations.get(station_id)
            if isinstance(station, dict) and station.get("status") != "rework":
                station["status"] = "stale"
                station["updated_at"] = now_iso()


def append_history(
    project: dict[str, Any],
    *,
    actor: str,
    change: str,
    invalidated: list[str],
    version_id: str,
) -> None:
    history = project.setdefault("history", [])
    if not isinstance(history, list):
        raise WorkflowError("project.history must be an array.")
    history.append(
        {
            "at": now_iso(),
            "who": actor,
            "change": change,
            "invalidated": invalidated,
            "snapshot_before": version_id,
        }
    )


def load_project(path_value: str) -> tuple[Path, dict[str, Any]]:
    path = Path(path_value).expanduser().resolve()
    if not path.is_file():
        raise WorkflowError(f"Project manifest does not exist: {path}")
    return path, read_json(path)


def command_status(args: argparse.Namespace) -> int:
    project_path, project = load_project(args.project)
    workflow = ensure_workflow(copy.deepcopy(project))
    nodes = nodes_by_id(workflow)
    print(f"Project: {project_path}")
    for node_id, node in nodes.items():
        dependencies = ",".join(str(item) for item in node.get("depends_on", [])) or "-"
        print(
            f"{node_id:16} {str(node.get('status') or 'planned'):14} "
            f"depends={dependencies} outputs={len(node.get('outputs', []))}"
        )
    return 0


def command_checkpoint(args: argparse.Namespace) -> int:
    project_path, project = load_project(args.project)
    entry = snapshot(
        project_path,
        project,
        kind="manual_checkpoint",
        reason=args.note,
        actor=args.actor,
        stage=args.stage or "",
    )
    print(f"Checkpoint {entry['id']} -> {entry['manifest']}")
    return 0


def command_init(args: argparse.Namespace) -> int:
    project_path, project = load_project(args.project)
    if isinstance(project.get("workflow"), dict):
        print("Workflow already exists; no file was changed.")
        return 0
    if not args.confirm:
        print("Would add the 16-stage workflow. Re-run with --confirm to write it.")
        return 0
    entry = snapshot(
        project_path,
        project,
        kind="before_workflow_init",
        reason="Add recoverable workflow graph",
        actor=args.actor,
    )
    ensure_workflow(project)
    append_history(
        project,
        actor=args.actor,
        change="Initialized the recoverable 16-stage production workflow.",
        invalidated=[],
        version_id=entry["id"],
    )
    replace_json(project_path, project)
    print(f"Initialized workflow; prior manifest is version {entry['id']}.")
    return 0


def command_redo(args: argparse.Namespace) -> int:
    project_path, project = load_project(args.project)
    working = copy.deepcopy(project)
    workflow = ensure_workflow(working)
    nodes = nodes_by_id(workflow)
    if args.stage not in nodes:
        raise WorkflowError(f"Unknown stage {args.stage}; run status to list stage ids.")
    affected = descendants(nodes, args.stage)
    print(f"Redo stage: {args.stage}")
    print("Downstream stale: " + (", ".join(affected) if affected else "(none)"))
    if not args.confirm:
        print("Dry run only. Re-run with --confirm to archive and update the manifest.")
        return 0

    entry = snapshot(
        project_path,
        project,
        kind="before_redo",
        reason=args.reason,
        actor=args.actor,
        stage=args.stage,
    )
    selected = nodes[args.stage]
    selected["status"] = "rework"
    selected["updated_at"] = now_iso()
    selected["revision_reason"] = args.reason
    for node_id in affected:
        nodes[node_id]["status"] = "stale"
        nodes[node_id]["updated_at"] = now_iso()
    workflow["revision_requests"].append(
        {
            "requested_at": now_iso(),
            "stage": args.stage,
            "reason": args.reason,
            "invalidated": affected,
            "snapshot_before": entry["id"],
            "actor": args.actor,
        }
    )
    update_legacy(working, args.stage, "rework", affected)
    append_history(
        working,
        actor=args.actor,
        change=f"Requested remake of workflow stage {args.stage}: {args.reason}",
        invalidated=affected,
        version_id=entry["id"],
    )
    replace_json(project_path, working)
    print(f"Applied redo request. Prior manifest is version {entry['id']}.")
    return 0


def command_transition(args: argparse.Namespace) -> int:
    project_path, project = load_project(args.project)
    working = copy.deepcopy(project)
    workflow = ensure_workflow(working)
    nodes = nodes_by_id(workflow)
    if args.stage not in nodes:
        raise WorkflowError(f"Unknown stage {args.stage}; run status to list stage ids.")
    if args.status not in ALLOWED_STATUS:
        raise WorkflowError(f"Unsupported status: {args.status}")
    if not args.confirm:
        print(
            f"Would set {args.stage} -> {args.status} and add {len(args.output)} output(s). "
            "Re-run with --confirm."
        )
        return 0
    entry = snapshot(
        project_path,
        project,
        kind="before_transition",
        reason=args.note or f"Set {args.stage} to {args.status}",
        actor=args.actor,
        stage=args.stage,
    )
    node = nodes[args.stage]
    node["status"] = args.status
    node["updated_at"] = now_iso()
    if args.note:
        node["note"] = args.note
    outputs = node.setdefault("outputs", [])
    if not isinstance(outputs, list):
        raise WorkflowError(f"workflow node {args.stage}.outputs must be an array.")
    for output in args.output:
        if output not in outputs:
            outputs.append(output)
    update_legacy(working, args.stage, args.status, [])
    append_history(
        working,
        actor=args.actor,
        change=f"Workflow stage {args.stage} -> {args.status}. {args.note}".strip(),
        invalidated=[],
        version_id=entry["id"],
    )
    replace_json(project_path, working)
    print(f"Updated {args.stage}; prior manifest is version {entry['id']}.")
    return 0


def command_list(args: argparse.Namespace) -> int:
    project_path, _ = load_project(args.project)
    index = load_index(project_path)
    entries = index.get("entries", [])
    if args.json:
        print(json.dumps(index, ensure_ascii=False, indent=2))
        return 0
    if not entries:
        print("No history versions.")
        return 0
    for entry in reversed(entries):
        print(
            f"{entry.get('id')}  {entry.get('kind')}  {entry.get('stage') or '-'}  "
            f"{entry.get('reason') or '-'}"
        )
    return 0


def command_restore(args: argparse.Namespace) -> int:
    project_path, current = load_project(args.project)
    index = load_index(project_path)
    match = next(
        (entry for entry in index.get("entries", []) if entry.get("id") == args.version),
        None,
    )
    if not isinstance(match, dict):
        raise WorkflowError(f"Unknown version id: {args.version}")
    manifest_value = str(match.get("manifest") or "")
    candidate = (project_path.parent / manifest_value).resolve()
    versions_dir, _ = history_paths(project_path)
    try:
        candidate.relative_to(versions_dir.resolve())
    except ValueError as exc:
        raise WorkflowError("History index points outside history/versions.") from exc
    restored = read_json(candidate)
    if not args.confirm:
        print(f"Would restore {args.version} from {candidate}. Re-run with --confirm.")
        return 0
    before = snapshot(
        project_path,
        current,
        kind="before_restore",
        reason=f"Restore {args.version}: {args.reason}",
        actor=args.actor,
    )
    restored_history = restored.setdefault("history", [])
    if not isinstance(restored_history, list):
        restored_history = []
        restored["history"] = restored_history
    restored_history.append(
        {
            "at": now_iso(),
            "who": args.actor,
            "change": f"Restored project version {args.version}: {args.reason}",
            "invalidated": [],
            "snapshot_before": before["id"],
        }
    )
    restored_workflow = ensure_workflow(restored)
    restored_workflow["restored_from"] = args.version
    replace_json(project_path, restored)
    print(f"Restored {args.version}; previous current state is version {before['id']}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Control and version the production workflow.")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="Show current workflow state.")
    status.add_argument("project")
    status.set_defaults(func=command_status)

    init = sub.add_parser("init", help="Add the default workflow to a project.")
    init.add_argument("project")
    init.add_argument("--actor", default="workflow-control")
    init.add_argument("--confirm", action="store_true")
    init.set_defaults(func=command_init)

    checkpoint = sub.add_parser("checkpoint", help="Write an immutable manifest snapshot.")
    checkpoint.add_argument("project")
    checkpoint.add_argument("--note", required=True)
    checkpoint.add_argument("--stage")
    checkpoint.add_argument("--actor", default="workflow-control")
    checkpoint.set_defaults(func=command_checkpoint)

    redo = sub.add_parser("redo", help="Request a stage remake and stale downstream stages.")
    redo.add_argument("project")
    redo.add_argument("--stage", required=True)
    redo.add_argument("--reason", required=True)
    redo.add_argument("--actor", default="workflow-control")
    redo.add_argument("--confirm", action="store_true")
    redo.set_defaults(func=command_redo)

    transition = sub.add_parser("transition", help="Set a stage status and register outputs.")
    transition.add_argument("project")
    transition.add_argument("--stage", required=True)
    transition.add_argument("--status", required=True, choices=sorted(ALLOWED_STATUS))
    transition.add_argument("--note", default="")
    transition.add_argument("--output", action="append", default=[])
    transition.add_argument("--actor", default="workflow-control")
    transition.add_argument("--confirm", action="store_true")
    transition.set_defaults(func=command_transition)

    versions = sub.add_parser("versions", help="List preserved project versions.")
    versions.add_argument("project")
    versions.add_argument("--json", action="store_true")
    versions.set_defaults(func=command_list)

    restore = sub.add_parser("restore", help="Restore a preserved manifest version.")
    restore.add_argument("project")
    restore.add_argument("--version", required=True)
    restore.add_argument("--reason", required=True)
    restore.add_argument("--actor", default="workflow-control")
    restore.add_argument("--confirm", action="store_true")
    restore.set_defaults(func=command_restore)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.func(args))
    except (WorkflowError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
