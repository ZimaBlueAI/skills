#!/usr/bin/env python3
"""镜头切分 v0.2：粗筛到精修两级管线，输出秒级 + 帧级双精度边界。

粗切: PySceneDetect (CPU, 快)
精修: TransNetV2 (神经网络, 准, 能处理渐变转场) —— 未安装时降级为仅粗切并明确警告

用法:
  python shot_detect.py video.mp4 [-o shots.json] [--coarse-only]
依赖:
  pip install scenedetect[opencv] --break-system-packages
  精修层(可选但强烈建议): pip install transnetv2-pytorch torch
输出 shots.json:
  {"fps": 30.0, "method": "pyscenedetect+transnetv2",
   "shots": [{"shot_id":"s001","start_s":0.0,"end_s":2.43,"start_f":0,"end_f":72}, ...]}
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def video_fps(path: str) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=avg_frame_rate", "-of", "json", path],
        capture_output=True, text=True, check=True)
    num, _, den = json.loads(r.stdout)["streams"][0]["avg_frame_rate"].partition("/")
    return int(num) / int(den or 1)


def coarse_pyscenedetect(path: str) -> list[tuple[int, int]]:
    """返回 [(start_frame, end_frame_exclusive)]。"""
    from scenedetect import detect, AdaptiveDetector
    scenes = detect(path, AdaptiveDetector())
    return [(s.frame_num, e.frame_num) for s, e in scenes]


def refine_transnetv2(path: str) -> list[tuple[int, int]] | None:
    """TransNetV2 全片推理，返回帧级镜头区间；未安装返回 None。"""
    try:
        from transnetv2_pytorch import TransNetV2
    except ImportError:
        return None
    import torch
    model = TransNetV2()
    model.eval()
    with torch.no_grad():
        _, single_frame_pred, _ = model.predict_video(path)
        scenes = model.predictions_to_scenes(
            single_frame_pred.cpu().numpy().flatten())
    return [(int(s), int(e) + 1) for s, e in scenes]


def merge(coarse: list, refined: list | None) -> tuple[list, str]:
    """精修结果可用则以其为准（对渐变转场更准），否则用粗切。"""
    if refined and len(refined) >= max(1, len(coarse) // 3):
        return refined, "pyscenedetect+transnetv2"
    if refined is not None:
        # TransNetV2 输出异常稀少时保守回退
        return coarse, "pyscenedetect (transnetv2 output anomalous, fell back)"
    return coarse, "pyscenedetect-only"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("-o", "--output", default="shots.json")
    ap.add_argument("--coarse-only", action="store_true")
    args = ap.parse_args()

    fps = video_fps(args.video)
    coarse = coarse_pyscenedetect(args.video)
    if not coarse:
        # 无切点 = 整条素材是一个镜头，而不是零个镜头
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0",
             "-show_entries", "stream=nb_read_packets", "-of", "json", args.video],
            capture_output=True, text=True, check=True)
        total = int(json.loads(r.stdout)["streams"][0]["nb_read_packets"])
        coarse = [(0, total)]
    refined = None if args.coarse_only else refine_transnetv2(args.video)
    shots_f, method = merge(coarse, refined)

    if "only" in method and not args.coarse_only:
        print("[warn] TransNetV2 未安装，仅粗切。渐变转场边界可能不准："
              "pip install transnetv2-pytorch torch", file=sys.stderr)

    shots = [
        {"shot_id": f"s{i+1:03d}",
         "start_s": round(sf / fps, 3), "end_s": round(ef / fps, 3),
         "start_f": sf, "end_f": ef}
        for i, (sf, ef) in enumerate(shots_f)
    ]
    Path(args.output).write_text(json.dumps(
        {"video": args.video, "fps": round(fps, 3), "method": method,
         "shot_count": len(shots), "shots": shots},
        ensure_ascii=False, indent=2))
    print(f"{len(shots)} 个镜头 ({method}) → {args.output}")


if __name__ == "__main__":
    main()
