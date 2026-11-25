"""Render a Light sequence locally from its saved cut, without rewriting source media."""
import json
import math
import secrets
import shutil
import subprocess
from pathlib import Path

import edit_timeline


def _source(project, legacy, relative):
    for root in (project,legacy):
        if not root: continue
        root=Path(root).resolve()
        path=(root/relative).resolve()
        if path.is_relative_to(root) and path.is_file():return path
    raise ValueError(f"缺少素材：{relative}")


def _tempo(speed):
    chain=[]
    while speed<.5:
        chain.append("atempo=0.5")
        speed*=2
    while speed>2:
        chain.append("atempo=2")
        speed/=2
    return ",".join(chain+[f"atempo={speed:.6f}"])


def render(project, doc, aspect, timeline=None):
    tl=timeline if timeline is not None else edit_timeline.load_timeline(project)
    clips=tl.get("clips") or []
    if not clips:raise ValueError("请先把素材加入时间线。")
    size={"landscape":(1280,720),"portrait":(720,1280),"square":(960,960)}.get(aspect)
    if not size:raise ValueError("请选择横屏、竖屏或方形。")
    ffmpeg,probe=shutil.which("ffmpeg"),shutil.which("ffprobe")
    if not ffmpeg or not probe:raise ValueError("工作站需要安装 FFmpeg 和 FFprobe 才能导出。")
    w,h=size
    fps=max(1,min(60,int(tl.get("fps") or 24)))
    args=[ffmpeg,"-nostdin","-hide_banner","-loglevel","error","-filter_complex_threads","2"]
    filters,sequence,overlays=[],[],[]
    total=edit_timeline.total_duration(tl)
    root=(doc.get("legacy") or {}).get("source_root")
    info={}
    for i,c in enumerate(clips):
        path=_source(project,root,c["path"])
        if path not in info:
            inspected=subprocess.run([probe,"-v","error","-show_entries","stream=codec_type","-of","json",str(path)],
                                     capture_output=True,timeout=30)
            if inspected.returncode:raise ValueError(f"无法读取素材：{path.name}")
            info[path]={s["codec_type"] for s in json.loads(inspected.stdout)["streams"]}
        dur=float(c["duration"]);speed=float(c.get("speed") or 1)
        if not (math.isfinite(dur) and dur>0 and 0<speed<=64):raise ValueError("请检查镜头时长和速度。")
        image=c.get("kind")=="image"
        if image:args.extend(["-loop","1","-framerate",str(fps),"-t",str(dur)])
        else:args.extend(["-ss",str(float(c.get("in_point") or 0)),"-t",str(dur*speed)])
        args.extend(["-i",str(path)])
        main=(c.get("track") or "V1")=="V1"
        if main:
            if "video" in info[path]:
                filters.append(f"[{i}:v]setpts=(PTS-STARTPTS)/{1 if image else speed},fps={fps},scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration={dur},trim=duration={dur}[v{i}]")
            else:
                filters.append(f"color=black:s={w}x{h}:r={fps}:d={dur}[v{i}]")
        if "audio" in info[path] and not image:
            vol=0 if c.get("muted") else float(c.get("volume",1))
            audio=f"[{i}:a]asetpts=PTS-STARTPTS,{_tempo(speed)},aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume={vol},apad,atrim=duration={dur}"
        else:
            audio=f"anullsrc=r=48000:cl=stereo,atrim=duration={dur}"
        if main:
            filters.append(audio+f"[a{i}]"); sequence.append(f"[v{i}][a{i}]")
        else:
            delay=round(float(c.get("start") or 0)*1000)
            filters.append(audio+f",adelay={delay}:all=1[a{i}]");overlays.append(f"[a{i}]")
    if sequence:
        filters.append("".join(sequence)+f"concat=n={len(sequence)}:v=1:a=1[vcat][acat]")
        filters.append(f"[vcat]tpad=stop_mode=add:stop_duration={total},trim=duration={total}[vout]")
    else:
        filters.extend([f"color=black:s={w}x{h}:r={fps}:d={total}[vout]",f"anullsrc=r=48000:cl=stereo,atrim=duration={total}[acat]"])
    if overlays:
        filters.append("[acat]"+"".join(overlays)+f"amix=inputs={1+len(overlays)}:duration=longest:normalize=0[aout]")
    else: filters.append("[acat]anull[aout]")
    folder=project/"exports";folder.mkdir(exist_ok=True)
    name="cut-"+secrets.token_hex(8)
    partial=folder/(name+".partial.mp4")
    final=folder/(name+".mp4")
    args.extend(["-filter_complex",";".join(filters),"-map","[vout]","-map","[aout]","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart","-t",str(total),str(partial)])
    result=subprocess.run(args,capture_output=True)
    if result.returncode:
        raise ValueError("导出未完成，请检查素材是否损坏、工作盘空间是否充足。")
    partial.replace(final)
    return {"file":"/media/exports/"+final.name,"duration":total}
