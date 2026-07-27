#!/usr/bin/env python3
"""路由闸门：拿 evals/trigger_cases.json 检查「该进本技能 / 该让给姊妹技能」的边界。

    python scripts/trigger_eval.py [--report reports/trigger-eval.json]

判定规则（与 SKILL.md 的路由表一致）：
    命中任一 exclusive_negative                    → 不路由，让给对应技能
    命中 presentation 且命中 live_stage/zima/单文件 → 路由本技能
    其余                                           → 不路由
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "trigger_cases.json"


def hits(prompt: str, words: list[str]) -> list[str]:
    return [w for w in words if w in prompt]


def decide(prompt: str, spec: dict) -> dict:
    low = prompt.lower()
    for target, words in spec["exclusive_negatives"].items():
        found = hits(low, words)
        if found:
            return {"route": False, "route_to": target, "why": f'排除词命中：{found}'}
    concepts = spec["concepts"]
    presentation = hits(low, concepts["presentation"])
    supporting = (
        hits(low, concepts["live_stage"])
        + hits(low, concepts["zima_marker"])
        + hits(low, concepts["single_file_html"])
    )
    if presentation and supporting:
        return {"route": True, "route_to": "zima-html-ppt",
                "why": f"presentation={presentation} supporting={supporting}"}
    return {"route": False, "route_to": "none",
            "why": f"presentation={presentation} supporting={supporting} —— 证据不足"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    args = parser.parse_args()

    spec = json.loads(CASES.read_text(encoding="utf-8"))
    results = []
    for case in spec["cases"]:
        verdict = decide(case["prompt"], spec)
        want_route = case["expect"] == "route"
        ok = verdict["route"] == want_route
        if not want_route and case.get("route_to"):
            ok = ok and verdict["route_to"] == case["route_to"]
        results.append({
            "prompt": case["prompt"],
            "expect": case["expect"],
            "expectRouteTo": case.get("route_to"),
            "gotRouteTo": verdict["route_to"],
            "pass": ok,
            "why": verdict["why"],
        })

    passed = sum(1 for r in results if r["pass"])
    payload = {"skill": spec["skill"], "total": len(results), "passed": passed,
               "ok": passed == len(results), "results": results}
    for r in results:
        mark = "PASS" if r["pass"] else "FAIL"
        print(f'{mark}  [{r["gotRouteTo"]}]  {r["prompt"]}')
        if not r["pass"]:
            print(f'      期望 {r["expect"]}/{r["expectRouteTo"]} · {r["why"]}')
    print(f'\n{passed}/{len(results)} passed')
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
