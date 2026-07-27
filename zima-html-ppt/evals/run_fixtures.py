#!/usr/bin/env python3
"""闸门回归：跑两份 fixture，确认「好稿放行、坏稿拦住」。

    python evals/run_fixtures.py [--report reports/fixture-eval.json]

minimal-deck.json  必须 build 成功、零 error、能反解回完全相同的 JSON。
broken-deck.json   必须被结构闸门拦下，且下列每一类错误都被点名。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "zima_deck.py"
FIXTURES = ROOT / "evals" / "fixtures"

# 坏稿必须命中的错误类别 → 报告里应出现的关键字
EXPECTED_BROKEN = {
    "缺 min": "min（分钟配额）",
    "缺 notes": "缺少逐字稿",
    "占位符残留": "未替换占位符",
    "split 缺 right": "必须提供 right",
    "图表数据非数字": "必须是纯数字",
    "图表重名": "chart name 重复",
    "表格列数不齐": "与表头",
    "条形越界": "pct 必须是 0–100",
    "未知块类型": "未知块类型",
    "未知 note tag": "未知标签",
}
EXPECTED_BROKEN_WARNINGS = {"名词式标题": "名词式标题"}


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    args = parser.parse_args()

    results: list[dict[str, object]] = []
    tmp = Path(tempfile.mkdtemp(prefix="zima-fixture-"))

    # —— 好稿：build → 零 error → 反解一致 —— #
    good_html = tmp / "minimal.html"
    good_report = tmp / "minimal-report.json"
    proc = run("build", str(FIXTURES / "minimal-deck.json"),
               "--output", str(good_html), "--report", str(good_report))
    report = json.loads(good_report.read_text(encoding="utf-8")) if good_report.exists() else {}
    results.append({
        "case": "minimal-deck build",
        "pass": proc.returncode == 0 and not report.get("errors"),
        "detail": f'exit={proc.returncode} errors={len(report.get("errors", []))} '
                  f'gates={report.get("gates")}',
    })

    back = tmp / "minimal-roundtrip.json"
    proc = run("extract", str(good_html), "--output", str(back))
    same = (
        proc.returncode == 0
        and json.loads(back.read_text(encoding="utf-8"))
        == json.loads((FIXTURES / "minimal-deck.json").read_text(encoding="utf-8"))
    )
    results.append({"case": "minimal-deck round-trip", "pass": same,
                    "detail": "extract(build(x)) == x"})

    # —— 坏稿：必须被拦 —— #
    bad_report = tmp / "broken-report.json"
    proc = run("validate", str(FIXTURES / "broken-deck.json"), "--report", str(bad_report))
    bad = json.loads(bad_report.read_text(encoding="utf-8")) if bad_report.exists() else {}
    err_text = " ".join(e["message"] for e in bad.get("errors", []))
    warn_text = " ".join(w["message"] for w in bad.get("warnings", []))
    results.append({
        "case": "broken-deck rejected",
        "pass": proc.returncode != 0 and bool(bad.get("errors")),
        "detail": f'exit={proc.returncode} errors={len(bad.get("errors", []))}',
    })
    for label, needle in EXPECTED_BROKEN.items():
        results.append({"case": f"broken-deck 命中「{label}」", "pass": needle in err_text,
                        "detail": needle})
    for label, needle in EXPECTED_BROKEN_WARNINGS.items():
        results.append({"case": f"broken-deck 警告「{label}」", "pass": needle in warn_text,
                        "detail": needle})

    # —— 坏稿默认不许产出 —— #
    proc = run("build", str(FIXTURES / "broken-deck.json"), "--output", str(tmp / "broken.html"))
    results.append({
        "case": "broken-deck build 被中止",
        "pass": proc.returncode != 0 and not (tmp / "broken.html").exists(),
        "detail": f"exit={proc.returncode}",
    })

    passed = sum(1 for r in results if r["pass"])
    payload = {"total": len(results), "passed": passed,
               "ok": passed == len(results), "results": results}
    for r in results:
        print(f'{"PASS" if r["pass"] else "FAIL"}  {r["case"]}  ({r["detail"]})')
    print(f'\n{passed}/{len(results)} passed')
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
