#!/usr/bin/env python3
"""Validate config, manifest, edit plan, and style card contracts plus semantics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from cinematic_config import (
    ConfigError,
    SKILL_DIR,
    dump_json,
    load_config,
    providers_for_capability,
    validate_config,
)

try:
    import jsonschema
except ModuleNotFoundError:  # Optional: semantic validation still runs.
    jsonschema = None


SCHEMAS = {
    "manifest": SKILL_DIR / "schemas" / "project-manifest.schema.json",
    "plan": SKILL_DIR / "schemas" / "edit-plan.schema.json",
    "style_card": SKILL_DIR / "schemas" / "style-card.schema.json",
}

GENERATED_MEDIA = {
    "generated_still",
    "generated_video",
    "generated_audio",
}


def add(
    report: dict[str, Any],
    level: str,
    code: str,
    path: str,
    message: str,
) -> None:
    report["issues"].append(
        {"level": level, "code": code, "path": path, "message": message}
    )


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid JSON in {path} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def schema_validate(
    kind: str,
    value: Any,
    report: dict[str, Any],
) -> None:
    if jsonschema is None:
        if not report.get("_schema_warning_added"):
            add(
                report,
                "warning",
                "jsonschema_unavailable",
                "$",
                "The optional jsonschema package is unavailable; semantic checks ran, but full schema validation did not.",
            )
            report["_schema_warning_added"] = True
        return

    schema = load_json(SCHEMAS[kind])
    validator = jsonschema.Draft7Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )
    for error in sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path)):
        suffix = "".join(
            f"[{part}]" if isinstance(part, int) else f".{part}"
            for part in error.absolute_path
        )
        add(report, "error", f"{kind}_schema", "$" + suffix, error.message)


def duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return repeated


def validate_manifest(
    manifest: dict[str, Any],
    report: dict[str, Any],
    stage: str,
) -> dict[str, dict[str, Any]]:
    schema_validate("manifest", manifest, report)
    assets = manifest.get("assets") if isinstance(manifest.get("assets"), list) else []
    asset_ids = [
        item.get("asset_id", "")
        for item in assets
        if isinstance(item, dict) and isinstance(item.get("asset_id"), str)
    ]
    for repeated in sorted(duplicates(asset_ids)):
        add(report, "error", "asset_id_duplicate", "$.assets", f"Duplicate asset_id: {repeated}.")
    asset_map = {
        item["asset_id"]: item
        for item in assets
        if isinstance(item, dict) and isinstance(item.get("asset_id"), str)
    }

    project = manifest.get("project") if isinstance(manifest.get("project"), dict) else {}
    form = project.get("form")
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            continue
        path = f"$.assets[{index}]"
        kind = asset.get("kind")
        truth_status = asset.get("truth_status")
        provenance = asset.get("provenance") if isinstance(asset.get("provenance"), dict) else {}
        disclosure = str(provenance.get("disclosure", "")).strip()
        status = asset.get("status")
        rights = asset.get("rights") if isinstance(asset.get("rights"), dict) else {}

        if kind == "generated" and truth_status != "synthetic":
            add(report, "error", "generated_truth_status", path, "Generated assets must use truth_status 'synthetic'.")
        if kind == "simulation" and truth_status != "simulated":
            add(report, "error", "simulation_truth_status", path, "Simulation assets must use truth_status 'simulated'.")
        if kind == "reenactment" and truth_status != "reenacted":
            add(report, "error", "reenactment_truth_status", path, "Reenactment assets must use truth_status 'reenacted'.")
        if kind in {"generated", "simulation", "reenactment"} and status in {
            "select",
            "accepted",
            "delivered",
        } and not disclosure:
            add(report, "error", "disclosure_missing", path, "Accepted synthetic/simulated/reenacted media needs disclosure text.")
        if form == "documentary" and kind in {"generated", "simulation", "reenactment"}:
            add(
                report,
                "warning",
                "documentary_synthetic_asset",
                path,
                "Documentary synthetic/simulated/reenacted media requires explicit editorial and disclosure review.",
            )
        if status in {"accepted", "delivered"} and rights.get("status") in {None, "", "unknown", "restricted"}:
            add(report, "error", "rights_not_cleared", path, "Accepted/delivered asset rights are not cleared.")
        checksum = asset.get("checksum_sha256")
        if stage in {"deliver", "publish"} and status in {"accepted", "delivered"} and not checksum:
            add(report, "warning", "checksum_missing", path, "Accepted/delivered asset has no SHA-256 checksum.")

    claims = manifest.get("claims") if isinstance(manifest.get("claims"), list) else []
    claim_ids = [
        claim.get("claim_id", "")
        for claim in claims
        if isinstance(claim, dict) and isinstance(claim.get("claim_id"), str)
    ]
    for repeated in sorted(duplicates(claim_ids)):
        add(report, "error", "claim_id_duplicate", "$.claims", f"Duplicate claim_id: {repeated}.")
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            continue
        path = f"$.claims[{index}]"
        evidence_ids = claim.get("evidence_asset_ids") or []
        for asset_id in evidence_ids:
            if asset_id not in asset_map:
                add(report, "error", "claim_evidence_missing", path, f"Unknown evidence asset_id: {asset_id}.")
        if claim.get("type") in {"fact", "performance", "comparison", "price", "testimonial"}:
            if not evidence_ids:
                add(report, "error", "claim_without_evidence", path, "Factual/marketing claim has no evidence asset.")
            for asset_id in evidence_ids:
                evidence = asset_map.get(asset_id, {})
                if evidence.get("truth_status") in {"illustrative", "simulated", "reenacted", "synthetic"}:
                    add(
                        report,
                        "error",
                        "synthetic_claim_evidence",
                        path,
                        f"Claim uses {evidence.get('truth_status')} asset {asset_id} as evidence.",
                    )
        if stage in {"deliver", "publish"} and claim.get("status") not in {"verified", "qualified", "rejected", "waived"}:
            add(report, "error", "claim_unresolved", path, "Claim is unresolved for delivery/publication.")

    deliverables = (
        manifest.get("deliverables")
        if isinstance(manifest.get("deliverables"), list)
        else []
    )
    deliverable_ids = [
        item.get("deliverable_id", "")
        for item in deliverables
        if isinstance(item, dict) and isinstance(item.get("deliverable_id"), str)
    ]
    for repeated in sorted(duplicates(deliverable_ids)):
        add(
            report,
            "error",
            "deliverable_id_duplicate",
            "$.deliverables",
            f"Duplicate deliverable_id: {repeated}.",
        )
    if stage == "deliver" and not deliverables:
        add(report, "warning", "deliverables_empty", "$.deliverables", "No deliverables are listed.")

    approvals = manifest.get("approvals") if isinstance(manifest.get("approvals"), dict) else {}
    if stage == "generate" and approvals.get("generation_budget", {}).get("status") != "approved":
        add(report, "error", "generation_budget_unapproved", "$.approvals.generation_budget", "Generation budget is not approved.")
    if stage in {"render", "deliver", "publish"} and approvals.get("edit_plan", {}).get("status") != "approved":
        add(report, "error", "manifest_edit_unapproved", "$.approvals.edit_plan", "Manifest edit-plan approval is not approved.")
    if stage == "publish" and approvals.get("publish", {}).get("status") != "approved":
        add(report, "error", "publish_unapproved", "$.approvals.publish", "External publication is not approved.")
    return asset_map


def transition_allows_overlap(transition_type: str) -> bool:
    return transition_type in {
        "dissolve",
        "fade",
        "dip",
        "mask_wipe",
        "whip",
        "graphic",
        "custom",
    }


def validate_plan(
    plan: dict[str, Any],
    report: dict[str, Any],
    *,
    stage: str,
    manifest: dict[str, Any] | None,
    asset_map: dict[str, dict[str, Any]],
    config: dict[str, Any] | None,
) -> None:
    schema_validate("plan", plan, report)
    meta = plan.get("meta") if isinstance(plan.get("meta"), dict) else {}
    timeline = plan.get("timeline") if isinstance(plan.get("timeline"), list) else []
    gaps = plan.get("gaps") if isinstance(plan.get("gaps"), list) else []
    audio = plan.get("audio") if isinstance(plan.get("audio"), dict) else {}
    fps = meta.get("fps")
    frame = 1 / fps if isinstance(fps, (int, float)) and not isinstance(fps, bool) and fps > 0 else 0.04
    tolerance = max(frame * 1.1, 0.01)

    if manifest:
        project = manifest.get("project") if isinstance(manifest.get("project"), dict) else {}
        if project.get("project_id") and meta.get("project_id") != project.get("project_id"):
            add(report, "error", "project_id_mismatch", "$.meta.project_id", "Plan and manifest project_id values differ.")

    clip_ids = [
        clip.get("clip_id", "")
        for clip in timeline
        if isinstance(clip, dict) and isinstance(clip.get("clip_id"), str)
    ]
    for repeated in sorted(duplicates(clip_ids)):
        add(report, "error", "clip_id_duplicate", "$.timeline", f"Duplicate clip_id: {repeated}.")

    gap_ids = [
        gap.get("gap_id", "")
        for gap in gaps
        if isinstance(gap, dict) and isinstance(gap.get("gap_id"), str)
    ]
    for repeated in sorted(duplicates(gap_ids)):
        add(report, "error", "gap_id_duplicate", "$.gaps", f"Duplicate gap_id: {repeated}.")
    gap_map = {
        gap["gap_id"]: gap
        for gap in gaps
        if isinstance(gap, dict) and isinstance(gap.get("gap_id"), str)
    }

    sortable = [
        (index, clip)
        for index, clip in enumerate(timeline)
        if isinstance(clip, dict)
        and isinstance(clip.get("timeline_in"), (int, float))
        and not isinstance(clip.get("timeline_in"), bool)
        and isinstance(clip.get("duration"), (int, float))
        and not isinstance(clip.get("duration"), bool)
    ]
    ordered = sorted(sortable, key=lambda item: item[1]["timeline_in"])
    if [index for index, _ in ordered] != [index for index, _ in sortable]:
        add(report, "error", "timeline_unsorted", "$.timeline", "Timeline items are not sorted by timeline_in.")

    previous_end = 0.0
    for order_index, (source_index, clip) in enumerate(ordered):
        path = f"$.timeline[{source_index}]"
        start = float(clip["timeline_in"])
        duration = float(clip["duration"])
        end = start + duration
        if order_index == 0 and start > tolerance:
            add(report, "error", "implicit_head_gap", path, f"Timeline begins at {start:.6f}s instead of 0.")
        if order_index > 0:
            delta = start - previous_end
            transition = clip.get("transition") if isinstance(clip.get("transition"), dict) else {}
            transition_type = str(transition.get("type", "cut"))
            transition_duration = transition.get("duration", 0)
            transition_duration = (
                float(transition_duration)
                if isinstance(transition_duration, (int, float)) and not isinstance(transition_duration, bool)
                else 0.0
            )
            if delta > tolerance:
                add(report, "error", "implicit_timeline_gap", path, f"Implicit timeline gap of {delta:.6f}s; represent it explicitly.")
            elif delta < -tolerance:
                overlap = -delta
                if not transition_allows_overlap(transition_type) or overlap > transition_duration + tolerance:
                    add(
                        report,
                        "error",
                        "timeline_overlap",
                        path,
                        f"Unexpected overlap of {overlap:.6f}s for transition '{transition_type}'.",
                    )
        previous_end = max(previous_end, end)

        source = clip.get("source") if isinstance(clip.get("source"), dict) else {}
        kind = source.get("kind")
        truth_status = source.get("truth_status")
        asset_id = source.get("asset_id")
        gap_id = source.get("gap_id")
        source_in = source.get("source_in")
        source_out = source.get("source_out")
        speed = source.get("speed")

        if kind in {"live_action", "archival", "animation", "simulation", "reenactment"}:
            if not asset_id:
                add(report, "error", "source_asset_missing", path, f"Source kind '{kind}' needs asset_id.")
            elif asset_map and asset_id not in asset_map:
                add(report, "error", "source_asset_unknown", path, f"Unknown asset_id: {asset_id}.")
            if source_in is None or source_out is None:
                add(report, "error", "source_range_missing", path, f"Source kind '{kind}' needs source_in and source_out.")
            elif isinstance(source_in, (int, float)) and isinstance(source_out, (int, float)):
                if source_out <= source_in:
                    add(report, "error", "source_range_invalid", path, "source_out must be greater than source_in.")
                elif isinstance(speed, (int, float)) and speed > 0:
                    expected = (source_out - source_in) / speed
                    if abs(expected - duration) > max(tolerance, duration * 0.02):
                        add(
                            report,
                            "warning",
                            "source_duration_mismatch",
                            path,
                            f"Timeline duration {duration:.6f}s differs from source range/speed {expected:.6f}s.",
                        )
        if kind == "generated":
            if truth_status != "synthetic":
                add(report, "error", "generated_clip_truth", path, "Generated clips must use truth_status 'synthetic'.")
            if not gap_id or gap_id not in gap_map:
                add(report, "error", "generated_gap_missing", path, "Generated clip must reference a known gap_id.")
        if kind == "simulation" and truth_status != "simulated":
            add(report, "error", "simulation_clip_truth", path, "Simulation clips must use truth_status 'simulated'.")
        if kind == "reenactment" and truth_status != "reenacted":
            add(report, "error", "reenactment_clip_truth", path, "Reenactment clips must use truth_status 'reenacted'.")

        transition = clip.get("transition") if isinstance(clip.get("transition"), dict) else {}
        transition_type = transition.get("type", "cut")
        reason = str(transition.get("reason", "")).strip()
        if transition_type != "cut" and len(reason) < 8:
            add(report, "error", "transition_reason_missing", path, "Non-cut transition needs a specific reason of at least 8 characters.")

        if meta.get("form") == "documentary" and kind in {"generated", "simulation", "reenactment"}:
            overlay = clip.get("text_overlay") if isinstance(clip.get("text_overlay"), dict) else {}
            if overlay.get("role") != "disclosure":
                add(
                    report,
                    "warning",
                    "documentary_clip_disclosure",
                    path,
                    "Documentary synthetic/simulated/reenacted clip has no clip-level disclosure overlay; verify another disclosure mechanism.",
                )

    target = meta.get("target_duration")
    qc = plan.get("qc_targets") if isinstance(plan.get("qc_targets"), dict) else {}
    duration_tolerance = qc.get("duration_tolerance_seconds", 0.5)
    if isinstance(target, (int, float)) and isinstance(duration_tolerance, (int, float)):
        if abs(previous_end - target) > duration_tolerance:
            add(
                report,
                "error",
                "target_duration_mismatch",
                "$.meta.target_duration",
                f"Timeline ends at {previous_end:.6f}s; target is {target:.6f}s with ±{duration_tolerance:.6f}s tolerance.",
            )

    estimated_total = 0.0
    actual_total = 0.0
    unknown_estimate = False
    for index, gap in enumerate(gaps):
        if not isinstance(gap, dict):
            continue
        path = f"$.gaps[{index}]"
        medium = gap.get("proposed_medium")
        estimate = gap.get("estimated_cost")
        actual = gap.get("actual_cost")
        risk = gap.get("factual_risk")
        capability = str(gap.get("required_capability", "")).strip()

        if medium in GENERATED_MEDIA and estimate is None:
            unknown_estimate = True
            level = "error" if stage in {"generate", "render", "deliver", "publish"} else "warning"
            add(report, level, "generation_cost_unknown", path, "Generated-media gap has no estimated_cost.")
        elif isinstance(estimate, (int, float)) and not isinstance(estimate, bool):
            estimated_total += float(estimate)
        if isinstance(actual, (int, float)) and not isinstance(actual, bool):
            actual_total += float(actual)
        if gap.get("status") == "accepted" and medium in GENERATED_MEDIA and actual is None:
            add(report, "warning", "actual_cost_missing", path, "Accepted generated gap has no actual_cost.")
        if risk == "prohibited":
            add(report, "error", "prohibited_gap", path, "Gap is marked factually prohibited.")
        if risk in {"medium", "high"} and not str(gap.get("disclosure", "")).strip():
            add(report, "error", "gap_disclosure_missing", path, "Medium/high factual risk needs disclosure text.")
        if stage == "generate" and medium in GENERATED_MEDIA and gap.get("status") not in {"accepted", "rejected", "switched_medium"}:
            if gap.get("approval_status") != "approved":
                add(report, "error", "gap_unapproved", path, "Generated-media gap is not approved.")
        if capability and config is not None and not providers_for_capability(config, capability):
            level = "error" if stage in {"generate", "render"} else "warning"
            add(report, level, "capability_unavailable", path, f"No enabled provider declares '{capability}'.")

    budget = meta.get("budget") if isinstance(meta.get("budget"), dict) else {}
    approved_limit = budget.get("approved_limit")
    soft_limit = budget.get("soft_limit")
    if isinstance(soft_limit, (int, float)) and estimated_total > soft_limit:
        add(report, "warning", "plan_soft_budget_exceeded", "$.meta.budget", f"Estimated cost {estimated_total:.2f} exceeds plan soft limit {soft_limit:.2f}.")
    if stage in {"generate", "render"} and isinstance(approved_limit, (int, float)):
        if estimated_total > approved_limit or (unknown_estimate and approved_limit >= 0):
            add(report, "error", "approved_budget_exceeded", "$.meta.budget", "Estimated or unknown generation cost exceeds the approved limit.")
    if config is not None:
        user_limit = config.get("policy", {}).get("generation_soft_limit")
        if isinstance(user_limit, (int, float)) and estimated_total > user_limit:
            add(report, "warning", "user_soft_budget_exceeded", "$.gaps", f"Estimated cost {estimated_total:.2f} exceeds user soft limit {user_limit:.2f}.")

    tracks = audio.get("tracks") if isinstance(audio.get("tracks"), list) else []
    track_ids = [
        track.get("track_id", "")
        for track in tracks
        if isinstance(track, dict) and isinstance(track.get("track_id"), str)
    ]
    for repeated in sorted(duplicates(track_ids)):
        add(report, "error", "track_id_duplicate", "$.audio.tracks", f"Duplicate track_id: {repeated}.")
    if audio.get("expected") is True and not tracks:
        add(report, "warning", "audio_tracks_empty", "$.audio.tracks", "Audio is expected but no tracks are planned.")

    if stage in {"generate", "render", "deliver", "publish"} and meta.get("approval", {}).get("status") != "approved":
        add(report, "error", "plan_unapproved", "$.meta.approval", f"Plan must be approved for stage '{stage}'.")
    if stage in {"render", "deliver", "publish"}:
        unresolved = [
            gap.get("gap_id")
            for gap in gaps
            if isinstance(gap, dict) and gap.get("status") in {"open", "in_progress"}
        ]
        if unresolved:
            add(report, "error", "gaps_unresolved", "$.gaps", f"Unresolved gaps: {', '.join(str(item) for item in unresolved)}.")

    report["metrics"]["timeline_duration"] = round(previous_end, 6)
    report["metrics"]["estimated_generation_cost"] = round(estimated_total, 4)
    report["metrics"]["actual_generation_cost"] = round(actual_total, 4)


def validate_style_card(style: dict[str, Any], report: dict[str, Any]) -> None:
    schema_validate("style_card", style, report)
    samples = style.get("samples") if isinstance(style.get("samples"), list) else []
    sample_ids = [
        sample.get("sample_id", "")
        for sample in samples
        if isinstance(sample, dict) and isinstance(sample.get("sample_id"), str)
    ]
    for repeated in sorted(duplicates(sample_ids)):
        add(report, "error", "sample_id_duplicate", "$.samples", f"Duplicate sample_id: {repeated}.")
    sample_set = set(sample_ids)
    groups = {
        sample.get("group")
        for sample in samples
        if isinstance(sample, dict)
    }
    if "target" not in groups:
        add(report, "warning", "target_group_missing", "$.samples", "Style study has no target sample group.")
    if "control" not in groups:
        add(report, "warning", "control_group_missing", "$.samples", "Style study has no comparison/control group.")

    features = style.get("features") if isinstance(style.get("features"), list) else []
    feature_ids = [
        feature.get("feature_id", "")
        for feature in features
        if isinstance(feature, dict) and isinstance(feature.get("feature_id"), str)
    ]
    for repeated in sorted(duplicates(feature_ids)):
        add(report, "error", "feature_id_duplicate", "$.features", f"Duplicate feature_id: {repeated}.")
    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            continue
        for sample_id in feature.get("evidence_refs") or []:
            if sample_id not in sample_set:
                add(
                    report,
                    "error",
                    "feature_evidence_unknown",
                    f"$.features[{index}]",
                    f"Unknown sample evidence reference: {sample_id}.",
                )

    context = style.get("research_context") if isinstance(style.get("research_context"), dict) else {}
    if not context.get("limitations"):
        add(report, "warning", "style_limitations_empty", "$.research_context.limitations", "Record sampling and causal limitations.")
    if style.get("meta", {}).get("confidence") == "high" and (
        "target" not in groups or "control" not in groups
    ):
        add(report, "error", "style_confidence_unsupported", "$.meta.confidence", "High confidence needs both target and control evidence.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate cinematic project artifacts.")
    parser.add_argument("--manifest")
    parser.add_argument("--plan")
    parser.add_argument("--style-card")
    parser.add_argument("--config", help="Explicit user config path.")
    parser.add_argument(
        "--stage",
        choices=["plan", "generate", "render", "deliver", "publish"],
        default="plan",
    )
    parser.add_argument("-o", "--output", default="validation_report.json")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not any((args.manifest, args.plan, args.style_card)):
        print("ERROR: Provide at least one of --manifest, --plan, or --style-card.", file=sys.stderr)
        return 2

    output = Path(args.output)
    if output.exists() and not args.overwrite:
        print(f"ERROR: Output exists: {output}. Pass --overwrite.", file=sys.stderr)
        return 2

    report: dict[str, Any] = {
        "version": 1,
        "stage": args.stage,
        "passed": False,
        "inputs": {},
        "metrics": {},
        "issues": [],
    }
    manifest: dict[str, Any] | None = None
    config: dict[str, Any] | None = None
    asset_map: dict[str, dict[str, Any]] = {}

    try:
        if args.config:
            config, config_file = load_config(args.config)
            report["inputs"]["config"] = str(config_file)
            for item in validate_config(config, check_tools=False):
                add(report, item["level"], f"config_{item['code']}", "$.config", item["message"])
        else:
            try:
                config, config_file = load_config(None)
                report["inputs"]["config"] = str(config_file)
                for item in validate_config(config, check_tools=False):
                    add(report, item["level"], f"config_{item['code']}", "$.config", item["message"])
            except ConfigError as exc:
                add(report, "warning", "config_unavailable", "$.config", str(exc))

        if args.manifest:
            manifest_path = Path(args.manifest)
            manifest = load_json(manifest_path)
            report["inputs"]["manifest"] = str(manifest_path.resolve())
            if not isinstance(manifest, dict):
                raise RuntimeError("Manifest root must be an object.")
            asset_map = validate_manifest(manifest, report, args.stage)

        if args.plan:
            plan_path = Path(args.plan)
            plan = load_json(plan_path)
            report["inputs"]["plan"] = str(plan_path.resolve())
            if not isinstance(plan, dict):
                raise RuntimeError("Plan root must be an object.")
            validate_plan(
                plan,
                report,
                stage=args.stage,
                manifest=manifest,
                asset_map=asset_map,
                config=config,
            )

        if args.style_card:
            style_path = Path(args.style_card)
            style = load_json(style_path)
            report["inputs"]["style_card"] = str(style_path.resolve())
            if not isinstance(style, dict):
                raise RuntimeError("Style-card root must be an object.")
            validate_style_card(style, report)
    except (RuntimeError, OSError, ConfigError) as exc:
        add(report, "error", "load_failure", "$", str(exc))

    report.pop("_schema_warning_added", None)
    errors = sum(item["level"] == "error" for item in report["issues"])
    warnings = sum(item["level"] == "warning" for item in report["issues"])
    report["passed"] = errors == 0
    report["summary"] = {"errors": errors, "warnings": warnings}

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(dump_json(report), encoding="utf-8")
    for item in report["issues"]:
        print(
            f"[{item['level'].upper()}] {item['code']} {item['path']}: {item['message']}"
        )
    print(
        f"{'PASS' if report['passed'] else 'FAIL'}: "
        f"{errors} error(s), {warnings} warning(s) -> {output}"
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
