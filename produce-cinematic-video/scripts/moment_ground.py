#!/usr/bin/env python3
"""时序定位 v0.2：用 Qwen3-VL 的 temporal grounding 按自然语言查询定位剪辑点，
并将结果吸附到 shot_detect.py 输出的镜头边界（双保险：语义定位 + 边界对齐）。

用法:
  export DASHSCOPE_API_KEY=sk-xxx
  python moment_ground.py video.mp4 "手第一次触碰陶土" --shots shots.json
  python moment_ground.py video.mp4 "所有出现产品特写的片段" --shots shots.json --multi
依赖: pip install openai (走百炼 OpenAI 兼容接口)
输出: moments.json  {"query":..., "windows":[{"start_s":..,"end_s":..,
      "snapped_start_s":..,"snapped_end_s":..,"start_f":..,"end_f":..}]}

注意: 视频需可被 API 访问——本地文件走 base64(短视频)或先传 OSS 取 URL。
      本脚本实现 base64 路径，>50MB 时提示改用 URL。
"""
import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path

GROUNDING_PROMPT = """你是视频时序定位助手。分析视频内容，找出与查询匹配的时间区间。

查询: {query}

要求:
1. 理解画面中的动作、物体交互与场景变化，判断事件发生的精确起止时间
2. 同一事件多次出现时返回全部区间
3. {multi_hint}
4. 只输出 JSON，无任何其他文字，格式:
{{"query": "{query}", "relevant_windows": [["<start_seconds>", "<end_seconds>"]]}}"""


def snap_to_shots(t: float, shots: list[dict], mode: str) -> tuple[float, int]:
    """把时间点吸附到最近的镜头边界。mode: start 吸附到镜头起点, end 吸附到镜头终点。
    语义定位给的是'事件'区间, 剪辑点应落在包含该事件的镜头边界上。"""
    for s in shots:
        if s["start_s"] <= t < s["end_s"]:
            if mode == "start":
                return s["start_s"], s["start_f"]
            return s["end_s"], s["end_f"]
    # 越界: 取最近边界
    edges = [(s["start_s"], s["start_f"]) for s in shots] + \
            [(s["end_s"], s["end_f"]) for s in shots]
    return min(edges, key=lambda e: abs(e[0] - t))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("query")
    ap.add_argument("--shots", help="shot_detect.py 输出，用于边界吸附")
    ap.add_argument("--multi", action="store_true", help="期望多个区间")
    ap.add_argument("--model", default="qwen3-vl-plus")
    ap.add_argument("--no-snap", action="store_true", help="只要语义区间，不吸附镜头边界")
    ap.add_argument("-o", "--output", default="moments.json")
    args = ap.parse_args()

    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        sys.exit("请设置 DASHSCOPE_API_KEY")

    size_mb = Path(args.video).stat().st_size / 1e6
    if size_mb > 50:
        sys.exit(f"视频 {size_mb:.0f}MB 过大，请先上传 OSS 后改造脚本走 URL 输入")

    from openai import OpenAI
    client = OpenAI(api_key=api_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

    b64 = base64.b64encode(Path(args.video).read_bytes()).decode()
    multi_hint = ("查询语义指向多个片段，尽量找全" if args.multi
                  else "若明确只有一次出现，返回单个区间")
    resp = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": [
            {"type": "video_url",
             "video_url": {"url": f"data:video/mp4;base64,{b64}"}},
            {"type": "text",
             "text": GROUNDING_PROMPT.format(query=args.query, multi_hint=multi_hint)},
        ]}],
    )
    text = resp.choices[0].message.content
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        sys.exit(f"未解析出 JSON，原始输出:\n{text[:500]}")
    data = json.loads(m.group(0))

    shots = None
    if args.shots and not args.no_snap:
        shots = json.loads(Path(args.shots).read_text())["shots"]

    windows = []
    for w in data.get("relevant_windows", []):
        start_s, end_s = float(w[0]), float(w[1])
        item = {"start_s": start_s, "end_s": end_s}
        if shots:
            ss, sf = snap_to_shots(start_s, shots, "start")
            es, ef = snap_to_shots(end_s, shots, "end")
            item.update({"snapped_start_s": ss, "snapped_end_s": es,
                         "start_f": sf, "end_f": ef})
        windows.append(item)

    out = {"video": args.video, "query": args.query,
           "model": args.model, "windows": windows}
    Path(args.output).write_text(json.dumps(out, ensure_ascii=False, indent=2))
    for w in windows:
        line = f'{w["start_s"]:.2f}–{w["end_s"]:.2f}s'
        if "snapped_start_s" in w:
            line += f' → 吸附镜头边界 {w["snapped_start_s"]:.3f}–{w["snapped_end_s"]:.3f}s (帧 {w["start_f"]}–{w["end_f"]})'
        print(line)
    print(f"→ {args.output}")


if __name__ == "__main__":
    main()
