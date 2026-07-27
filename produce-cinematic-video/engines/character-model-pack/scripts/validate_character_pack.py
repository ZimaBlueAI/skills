#!/usr/bin/env python3
"""Validate file, alpha, canvas, baseline, and mirroring rules for a character pack."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required. Install it with: python -m pip install Pillow") from exc


VERSION = "1.0.0"
SAFE_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def flattened_data(image: Image.Image):
    getter = getattr(image, "get_flattened_data", None)
    return getter() if getter else image.getdata()


def visible_bbox(image: Image.Image, threshold: int) -> tuple[int, int, int, int] | None:
    alpha = image.convert("RGBA").getchannel("A")
    return alpha.point(lambda value: 255 if value > threshold else 0).getbbox()


def inspect_png(path: Path, threshold: int) -> dict[str, Any]:
    with Image.open(path) as opened:
        opened.load()
        original_mode = opened.mode
        rgba = opened.convert("RGBA")
    alpha = rgba.getchannel("A")
    alpha_min, alpha_max = alpha.getextrema()
    bbox = visible_bbox(rgba, threshold)
    visible_pixels = sum(1 for value in flattened_data(alpha) if value > threshold)
    coverage = visible_pixels / max(1, rgba.width * rgba.height)
    return {
        "path": str(path.resolve()),
        "mode": original_mode,
        "size": list(rgba.size),
        "alpha_min": alpha_min,
        "alpha_max": alpha_max,
        "visible_bbox": list(bbox) if bbox else None,
        "coverage": round(coverage, 6),
        "baseline_ratio": round((bbox[3] - 1) / max(1, rgba.height - 1), 6) if bbox else None,
    }


def add_issue(issues: list[dict[str, str]], level: str, code: str, message: str) -> None:
    issues.append({"level": level, "code": code, "message": message})


def load_json(path: Path, issues: list[dict[str, str]], label: str) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        add_issue(issues, "error", "invalid-json", f"{label} is not valid JSON: {exc}")
        return None
    if not isinstance(data, dict):
        add_issue(issues, "error", "invalid-json-shape", f"{label} must contain a JSON object")
        return None
    return data


def validate_cutout_folder(
    folder: Path,
    threshold: int,
    issues: list[dict[str, str]],
    inspected: dict[str, Any],
) -> None:
    if not folder.is_dir():
        return
    files = sorted(path for path in folder.glob("*.png") if not path.name.startswith("_") and "contact-sheet" not in path.name)
    for path in files:
        if not SAFE_NAME.fullmatch(path.stem):
            add_issue(issues, "error", "unsafe-filename", f"{path.relative_to(folder.parent)} has an unstable filename")
        try:
            info = inspect_png(path, threshold)
        except OSError as exc:
            add_issue(issues, "error", "unreadable-png", f"Cannot read {path}: {exc}")
            continue
        inspected[str(path.relative_to(folder.parent)).replace("\\", "/")] = info
        if info["visible_bbox"] is None:
            add_issue(issues, "error", "empty-cutout", f"{path.name} has no visible subject")
        if info["alpha_min"] >= 250:
            add_issue(issues, "error", "opaque-cutout", f"{path.name} has no transparent outer background")
        if info["coverage"] < 0.01:
            add_issue(issues, "warning", "tiny-subject", f"{path.name} uses less than 1% of its canvas")
        if info["coverage"] > 0.9:
            add_issue(issues, "warning", "tight-cutout", f"{path.name} leaves very little transparent margin")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", required=True, type=Path)
    parser.add_argument("--required-views", default="front,left,back")
    parser.add_argument("--alpha-threshold", type=int, default=18)
    parser.add_argument("--baseline-tolerance", type=float, default=0.035)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as a failing exit status")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.pack.is_dir():
        raise SystemExit(f"Character pack directory does not exist: {args.pack}")
    required_views = [item.strip() for item in args.required_views.split(",") if item.strip()]
    if not required_views:
        raise SystemExit("At least one required view is needed")
    if not 0 <= args.alpha_threshold <= 254:
        raise SystemExit("--alpha-threshold must be between 0 and 254")
    if not 0 <= args.baseline_tolerance <= 0.25:
        raise SystemExit("--baseline-tolerance must be between 0 and 0.25")

    issues: list[dict[str, str]] = []
    inspected: dict[str, Any] = {}
    views_dir = args.pack / "views"
    view_infos: dict[str, dict[str, Any]] = {}
    if not views_dir.is_dir():
        add_issue(issues, "error", "missing-views-dir", "Missing views/ directory")
    else:
        for name in required_views:
            path = views_dir / f"{name}.png"
            if not path.is_file():
                add_issue(issues, "error", "missing-view", f"Missing required view: views/{name}.png")
                continue
            try:
                info = inspect_png(path, args.alpha_threshold)
            except OSError as exc:
                add_issue(issues, "error", "unreadable-view", f"Cannot read {path}: {exc}")
                continue
            view_infos[name] = info
            inspected[f"views/{name}.png"] = info
            if info["mode"] != "RGBA":
                add_issue(issues, "warning", "non-rgba-view", f"views/{name}.png is {info['mode']}, not RGBA")
            if info["visible_bbox"] is None:
                add_issue(issues, "error", "empty-view", f"views/{name}.png has no visible subject")
            if info["alpha_min"] >= 250:
                add_issue(issues, "error", "opaque-view", f"views/{name}.png has no transparent outer background")
            if info["coverage"] < 0.02:
                add_issue(issues, "warning", "tiny-view", f"views/{name}.png uses less than 2% of its canvas")
            if info["coverage"] > 0.82:
                add_issue(issues, "warning", "tight-view", f"views/{name}.png leaves too little transparent margin")

    sizes = {tuple(info["size"]) for info in view_infos.values()}
    if len(sizes) > 1:
        add_issue(issues, "error", "canvas-mismatch", f"Required views use different canvas sizes: {sorted(sizes)}")
    baselines = {name: info["baseline_ratio"] for name, info in view_infos.items() if info["baseline_ratio"] is not None}
    if baselines and max(baselines.values()) - min(baselines.values()) > args.baseline_tolerance:
        add_issue(issues, "error", "baseline-mismatch", f"Required view baselines differ: {baselines}")

    view_manifest_path = views_dir / "manifest.json"
    view_manifest = load_json(view_manifest_path, issues, "views/manifest.json")
    if view_manifest is None:
        add_issue(issues, "warning", "missing-view-manifest", "Missing views/manifest.json; generation provenance is incomplete")

    pack_manifest_path = args.pack / "character-pack.json"
    pack_manifest = load_json(pack_manifest_path, issues, "character-pack.json")
    if pack_manifest is None:
        add_issue(issues, "warning", "missing-pack-manifest", "Missing character-pack.json; copy and complete the supplied template")
        asymmetry_notes: list[Any] = []
    else:
        anchors = pack_manifest.get("identity_anchors", [])
        if not isinstance(anchors, list) or len([item for item in anchors if str(item).strip()]) < 3:
            add_issue(issues, "warning", "missing-anchors", "character-pack.json should record three identity anchors")
        asymmetry_notes = pack_manifest.get("asymmetry_notes", [])
        review = pack_manifest.get("author_review", {})
        if not isinstance(review, dict) or review.get("status") not in {"green", "yellow", "red"}:
            add_issue(issues, "warning", "missing-author-review", "Record author_review.status as green, yellow, or red")

    if view_manifest:
        manifest_views = view_manifest.get("views", {})
        right = manifest_views.get("right", {}) if isinstance(manifest_views, dict) else {}
        mirrored = isinstance(right, dict) and (right.get("mirrored") or right.get("derived_from") == "left")
        manifest_asymmetry = view_manifest.get("asymmetry_notes", [])
        if mirrored and (asymmetry_notes or manifest_asymmetry):
            add_issue(issues, "error", "mirrored-asymmetry", "right.png was mirrored even though asymmetry is recorded; supply a true right view")
        expected_baseline = view_manifest.get("baseline_ratio")
        if isinstance(expected_baseline, (int, float)):
            for name, baseline in baselines.items():
                if abs(baseline - float(expected_baseline)) > args.baseline_tolerance:
                    add_issue(issues, "warning", "manifest-baseline-drift", f"views/{name}.png baseline {baseline} differs from manifest {expected_baseline}")

    validate_cutout_folder(args.pack / "expressions", args.alpha_threshold, issues, inspected)
    validate_cutout_folder(args.pack / "poses", args.alpha_threshold, issues, inspected)

    errors = [issue for issue in issues if issue["level"] == "error"]
    warnings = [issue for issue in issues if issue["level"] == "warning"]
    report = {
        "schema_version": "1.0",
        "tool": "validate_character_pack.py",
        "tool_version": VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pack": str(args.pack.resolve()),
        "status": "fail" if errors else "pass_with_warnings" if warnings else "pass",
        "summary": {"errors": len(errors), "warnings": len(warnings), "inspected_files": len(inspected)},
        "issues": issues,
        "files": inspected,
        "human_review_required": [
            "same identity and three anchors in every view",
            "correct left/right asymmetry",
            "proportions, colors, markings, clothing, accessories, and limb count",
            "one neutral pose family for the turnaround",
            "author green/yellow/red decision",
        ],
    }
    report_path = args.report or (args.pack / "validation-report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "errors": len(errors), "warnings": len(warnings), "report": str(report_path)}, ensure_ascii=False))
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
