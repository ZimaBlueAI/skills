#!/usr/bin/env python3
"""Evidence-based creative scoring and conservative empirical performance baselines."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from statistics import NormalDist
from typing import Any


METRICS = {
    "view_rate": ("views", "impressions"),
    "like_rate": ("likes", "views"),
    "completion_rate": ("completions", "views"),
    "click_rate": ("clicks", "impressions"),
    "lead_rate": ("leads", "clicks"),
    "customer_rate": ("customers", "leads"),
}


class EvaluationError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EvaluationError(f"Invalid JSON at line {exc.lineno}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise EvaluationError("Evaluation input must be a JSON object.")
    return value


def creative_score(data: dict[str, Any]) -> dict[str, Any]:
    dimensions = data.get("dimensions")
    weights = data.get("weights")
    if not isinstance(dimensions, dict) or not isinstance(weights, dict):
        raise EvaluationError("Input needs dimensions and weights objects.")
    rows: list[dict[str, Any]] = []
    numerator = 0.0
    denominator = 0.0
    complete = True
    for name, item in dimensions.items():
        if not isinstance(item, dict):
            raise EvaluationError(f"dimensions.{name} must be an object.")
        score = item.get("score")
        evidence = item.get("evidence")
        weight = weights.get(name, 1)
        if not isinstance(weight, (int, float)) or isinstance(weight, bool) or weight < 0:
            raise EvaluationError(f"weights.{name} must be a non-negative number.")
        if score is None:
            complete = False
        elif not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 10:
            raise EvaluationError(f"dimensions.{name}.score must be null or between 0 and 10.")
        if score is not None and (not isinstance(evidence, list) or not evidence):
            complete = False
        if score is not None:
            numerator += float(score) * float(weight)
            denominator += 10.0 * float(weight)
        rows.append(
            {
                "name": name,
                "score": score,
                "weight": weight,
                "evidence_count": len(evidence) if isinstance(evidence, list) else 0,
                "confidence": item.get("confidence", "low"),
                "impact": item.get("impact", ""),
                "recommended_change": item.get("recommended_change", ""),
            }
        )
    scored = [row for row in rows if row["score"] is not None]
    priorities = sorted(
        [row for row in scored if row["recommended_change"]],
        key=lambda row: (float(row["score"]), -float(row["weight"])),
    )
    return {
        "status": "complete" if complete and denominator else "partial",
        "score_100": round(numerator / denominator * 100, 1) if complete and denominator else None,
        "partial_score_100": round(numerator / denominator * 100, 1) if denominator else None,
        "dimensions": rows,
        "priorities": priorities[:5],
    }


def tags(value: str) -> set[str]:
    normalized = value.replace(";", "|").replace(",", "|")
    return {item.strip().lower() for item in normalized.split("|") if item.strip()}


def parse_count(row: dict[str, str], key: str) -> int | None:
    raw = str(row.get(key) or "").strip()
    if not raw:
        return None
    try:
        value = int(float(raw))
    except ValueError:
        return None
    return value if value >= 0 else None


def comparable_rows(path: Path, criteria: dict[str, Any]) -> tuple[list[dict[str, str]], int]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    platform = str(criteria.get("platform") or "").strip().lower()
    format_name = str(criteria.get("format") or "").strip().lower()
    target_tags = {str(item).strip().lower() for item in criteria.get("topic_tags", []) if str(item).strip()}
    selected: list[dict[str, str]] = []
    for row in rows:
        if platform and str(row.get("platform") or "").strip().lower() != platform:
            continue
        if format_name and str(row.get("format") or "").strip().lower() != format_name:
            continue
        row_tags = tags(str(row.get("topic_tags") or ""))
        if target_tags and not (target_tags & row_tags):
            continue
        selected.append(row)
    return selected, len(rows)


def wilson(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    if trials <= 0:
        return 0.0, 0.0
    z = NormalDist().inv_cdf(0.5 + confidence / 2)
    p = successes / trials
    denom = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denom
    radius = z * math.sqrt((p * (1 - p) + z * z / (4 * trials)) / trials) / denom
    return max(0.0, center - radius), min(1.0, center + radius)


def performance_baseline(
    rows: list[dict[str, str]],
    *,
    total_rows: int,
    minimum_rows: int,
    minimum_denominator: int,
) -> dict[str, Any]:
    outputs: dict[str, Any] = {}
    for metric, (numerator_key, denominator_key) in METRICS.items():
        numerator = 0
        denominator = 0
        usable_rows = 0
        for row in rows:
            top = parse_count(row, numerator_key)
            bottom = parse_count(row, denominator_key)
            if top is None or bottom is None or bottom <= 0 or top > bottom:
                continue
            numerator += top
            denominator += bottom
            usable_rows += 1
        eligible = usable_rows >= minimum_rows and denominator >= minimum_denominator
        if eligible:
            low, high = wilson(numerator, denominator)
            outputs[metric] = {
                "status": "empirical_baseline",
                "estimate": round(numerator / denominator, 6),
                "interval_95": [round(low, 6), round(high, 6)],
                "numerator": numerator,
                "denominator": denominator,
                "rows": usable_rows,
                "warning": "Association-only comparable-content baseline; not a guaranteed outcome.",
            }
        else:
            outputs[metric] = {
                "status": "not_estimable",
                "rows": usable_rows,
                "denominator": denominator,
                "needs": {
                    "minimum_rows": minimum_rows,
                    "minimum_denominator": minimum_denominator,
                },
            }
    return {
        "scope": "similar-topic empirical baseline",
        "total_history_rows": total_rows,
        "comparable_rows": len(rows),
        "metrics": outputs,
        "causal": False,
        "guarantee": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Score video evidence and build conservative performance baselines.")
    parser.add_argument("evaluation")
    parser.add_argument("--history", help="CSV using assets/performance-history.template.csv.")
    parser.add_argument("--minimum-rows", type=int, default=30)
    parser.add_argument("--minimum-denominator", type=int, default=10000)
    parser.add_argument("--output", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        source = Path(args.evaluation).expanduser().resolve()
        output = Path(args.output).expanduser().resolve()
        if not source.is_file():
            raise EvaluationError(f"Evaluation input does not exist: {source}")
        if output.exists():
            raise EvaluationError(f"Refusing to overwrite existing output: {output}")
        if args.minimum_rows < 1 or args.minimum_denominator < 1:
            raise EvaluationError("Prediction thresholds must be positive.")
        data = read_json(source)
        result: dict[str, Any] = {
            "version": 1,
            "project_id": data.get("project_id", ""),
            "video": data.get("video", ""),
            "creative_evaluation": creative_score(data),
        }
        if args.history:
            history = Path(args.history).expanduser().resolve()
            if not history.is_file():
                raise EvaluationError(f"History CSV does not exist: {history}")
            selected, total = comparable_rows(
                history,
                data.get("benchmark_filter") if isinstance(data.get("benchmark_filter"), dict) else {},
            )
            result["performance_prediction"] = performance_baseline(
                selected,
                total_rows=total,
                minimum_rows=args.minimum_rows,
                minimum_denominator=args.minimum_denominator,
            )
        else:
            result["performance_prediction"] = {
                "status": "not_requested",
                "note": "Provide comparable first-party history to estimate rate intervals.",
            }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {output}.")
        return 0
    except (EvaluationError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
