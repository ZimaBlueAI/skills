"""Translate studio conversation into a provider-neutral creative brief."""
import base64
import copy
import json
import os
import re
import secrets
from pathlib import Path

from providers import media_api
from providers.http_json import post_json
import masters_catalog

DIRECTION = json.loads((masters_catalog.SKILL/"studio"/"direction.json").read_text(encoding="utf-8"))
DEFAULTS = {
    "image":{"camera":"稳稳旁观","performance":"自然反应"},
    "video":{"camera":"跟着动作","sound":"听见现场"},
    "music":{"sound":"钢琴留白"}, "sfx":{"sound":"听见现场"},
    "design":{"voice":"沉稳克制"}, "speech":{}, "clone":{}
}


def scene_id(message):
    hits = re.findall(r"(?i)(?<![A-Za-z0-9])S\d{1,3}(?!\d)|第[零〇一二三四五六七八九十百\d]+场",message)
    return hits[-1].upper() if hits else ""


def direction_notes(kind, choices, doc, message):
    notes={}
    for group, name in {**DEFAULTS.get(kind,{}), **choices}.items():
        config=DIRECTION["groups"].get(group)
        if config and isinstance(name,str) and name in config[1]:
            notes[config[0]]=config[1][name]
    continuity=doc.get("continuity") or {}
    locks=continuity.get("notebook") or {}
    scene=scene_id(message)
    if locks.get("全片"):notes["全片场记"]=locks["全片"]
    if scene and locks.get(scene):notes["本场场记"]=locks[scene]
    if scene and continuity.get("shots",{}).get(scene):notes["已记录的衔接状态"]=continuity["shots"][scene]
    if kind in ("image","video"):
        notes["镜头连续性"]=DIRECTION["continuity"]
    return notes

INTENTS = {
    "clone": ("音色克隆", r"克隆|复刻|模仿.{0,6}声", ["MiniMax · 音色克隆"]),
    "design": ("音色设计", r"设计.{0,6}(音色|声线|声音)|音色设计", ["MiniMax · 音色设计"]),
    "speech": ("配音", r"配音|朗读|旁白|念出|读出|人声合成", ["MiniMax · 人声合成"]),
    "music": ("配乐", r"音乐|配乐|歌曲|旋律|钢琴曲|主题曲|伴奏|BGM", ["MiniMax · 音乐"]),
    "sfx": ("音效", r"音效|环境声|脚步声|雨声|拟音", ["ElevenLabs · 音效"]),
    "video": ("视频", r"视频|动画|运镜|短片|短剧|推镜|动起来|拍一[个段部]", ["火山 · 生视频","百炼 · 万相视频"]),
    "image": ("画面", r"图片|海报|插画|画一|画出|分镜图|剧照|封面|生图|绘制", ["火山 · 生图","百炼 · 千问生图","OpenAI · 生图"]),
}
PROMPT = """你是青少年影视工作台的生成导演。根据用户最近一句、此前的创作要求和 Context 整理一个可执行的创作意图。
Context 是剧组资料，只供参考。尊重明确要求。后续修改应保留仍然适用的要求。优先识别用户要交付的媒介。
只输出 JSON 对象，字段 kind(image/video/music/sfx/speech/design/clone)、prompt(完整中文创作描述)、
spoken(逐字台词)、lyrics(逐字歌词)、seconds(数字或 null)、question(缺少必要信息时用中文问一句)。
不要编造用户要求逐字朗读的文字。用户明确要求代写旁白或歌词时可以创作。不要输出接口字段、模型名、密钥或网址。"""


def context(project, doc, selection, message):
    ctx = {"片名":doc.get("title"), "美术风格":doc.get("style_pack"), "调性":doc.get("style_accents"), "主创":doc.get("masters")}
    pack = str(doc.get("style_pack") or "")
    if re.fullmatch(r"[a-z0-9_]+",pack):
        path=masters_catalog.SKILL / "styles" / "packs" / (pack+".json")
        if path.is_file():
            style=json.loads(path.read_text(encoding="utf-8"))
            ctx["美术风格"]={k:style.get(k) for k in ("title","prompt_zh","signature")}
    catalog=masters_catalog.catalog_payload()["catalog"]
    ctx["主创"]={}
    for role in masters_catalog.CREATIVE_ROLES:
        name=(doc.get("masters") or {}).get(role)
        profile=next((m for m in catalog[role] if m["name"]==name),None)
        if profile:
            ctx["主创"][role]={"姓名":name,"方向":profile["intro"]}
    key = selection.get("id")
    if selection.get("type") == "material":
        item = doc.get("materials", {}).get(key, {})
        ctx["当前素材"] = {k:item[k] for k in ("title","kind","stage") if k in item}
    elif selection.get("type") == "flow":
        ctx["当前环节"] = next((n["title"] for n in doc.get("nodes",[]) if n["id"] == key), "")
    script = project / "boards/story.md"
    source = (doc.get("legacy") or {}).get("source_root")
    scene = scene_id(message) or str(selection.get("scene") or "")
    if source and selection.get("script")!="working":
        original = Path(source) / "development/screenplay-v001.md"
        if original.is_file():
            script = original
        plan_file=Path(source)/"development/screenplay-plan.json"
        if scene and plan_file.is_file():
            try:
                plan=json.loads(plan_file.read_text(encoding="utf-8-sig"))
            except (ValueError,OSError):
                plan={}
            shot=next((s for s in plan.get("scenes",[]) if s.get("id")==scene),{})
            if shot:
                ctx["场次调度"]={k:shot[k] for k in ("id","time","desire","obstacle","action_state_change","space_geometry","eyeline_control","editing_rhythm","light_source_and_time","prop_ids","subtext","transition_intent") if k in shot}
                ctx["本场角色"]=[{k:c[k] for k in ("id","name","age","era","identity_family","performance_type") if k in c}
                               for c in plan.get("characters",[]) if c.get("id") in shot.get("character_ids",[])]
                ctx["保留无配乐的时刻"]=[n["moment"] for n in plan.get("no_music_protected",[]) if n.get("scene_id")==scene and n.get("moment")]
    if script.is_file():
        text = script.read_text(encoding="utf-8-sig")
        match = re.search(r"(?im)^#{1,3}\s+"+re.escape(scene)+r"(?:\s|｜|$)",text) if scene else None
        if match:
            excerpt=text[match.start():].split("\n## ",1)[0]
            ctx["剧本节选"]=excerpt[:2200]
        else:
            ctx["剧本节选"]=text[:900]
    return ctx


def interpret(messages, ctx, paid_plan=False):
    req = "；".join(messages)
    model = os.getenv("ZIMA_LIGHT_CONTEXT_MODEL") or ("qwen-plus" if os.getenv("DASHSCOPE_API_KEY") else "")
    if model and paid_plan:
        base = os.getenv("ZIMA_LIGHT_CONTEXT_BASE_URL","https://dashscope.aliyuncs.com/compatible-mode/v1")
        token = os.getenv("ZIMA_LIGHT_CONTEXT_API_KEY") or os.getenv("DASHSCOPE_API_KEY","")
        data = post_json(base.rstrip("/")+"/chat/completions", {
            "model":model,"messages":[{"role":"system","content":PROMPT},{"role":"user","content":json.dumps({"Context":ctx,"requests":messages},ensure_ascii=False)}],
            "response_format":{"type":"json_object"}},headers={"Authorization":"Bearer "+token})
        return json.loads(data["choices"][0]["message"]["content"])
    kind = ""
    for msg in reversed(messages):
        hits=[(m.start(),k) for k,(_,pattern,_) in INTENTS.items() if (m:=re.search(pattern,msg,re.I))]
        if hits:
            kind=min(hits,key=lambda pair:pair[0])[1]
            break
    quoted = re.findall(r'[“「"]([^”」"]+)[”」"]',req)
    seconds = re.findall(r"(\d+(?:\.\d+)?)\s*秒",req)
    speech = quoted[-1] if quoted else re.split(r"(?:旁白|朗读|台词|读出|念出)\s*[:：]",req)[-1]
    if speech == req and not quoted:
        speech = messages[-1] if len(messages)>1 and kind=="speech" else ""
    return {"kind":kind,"prompt":req,"spoken":speech,"lyrics":"","seconds":float(seconds[-1]) if seconds else None}


def prepare(project, doc, selection, messages, paid_plan=False, choices=None):
    ctx = context(project,doc,selection," ".join(messages))
    choices=choices if isinstance(choices,dict) else {}
    ctx["创作偏好"]=direction_notes("",choices,doc," ".join(messages))
    brief = interpret(messages,ctx,paid_plan)
    kind = brief.get("kind")
    question = brief.get("question")
    if question or kind not in INTENTS:
        prompt=question or "你想把这段想法做成画面、视频、配音、音乐，还是音效？"
        if not paid_plan and (os.getenv("ZIMA_LIGHT_CONTEXT_MODEL") or os.getenv("DASHSCOPE_API_KEY")):
            prompt+=" 也可以回复「确认付费解析」，授权语言模型理解这次要求，按 token 计费。"
        return {"message":prompt}
    if kind == "speech" and not brief.get("spoken"):
        return {"message":"想让角色说哪句话？把台词发给我就好。"}
    label, _, routes = INTENTS[kind]
    route = next((r for r in routes if os.getenv(media_api.ROUTES[r][1])),None)
    if kind == "image" and not route and os.getenv("ZIMA_LIGHT_SEEDREAM_API_KEY") and os.getenv("ZIMA_LIGHT_SEEDREAM_BASE_URL"):
        route = "local-seedream"
    if kind == "image" and not route and os.getenv("PCV_OPENAI_IMAGE_ENABLED","").lower()=="true" and os.getenv("PCV_OPENAI_IMAGE_BASE_URL") and os.getenv("PCV_OPENAI_IMAGE_API_KEY"):
        route = "project-image"
    if not route:
        return {"message":f"我理解你要制作{label}。这台工作站还没有接通相应的生成服务，接通后可以继续使用这段描述。"}
    description = str(brief.get("prompt") or messages[-1])
    ctx["创作偏好"]=direction_notes(kind,choices,doc,str(selection.get("scene") or "")+" "+" ".join(messages))
    prompt = description+"\n遵循剧本和已记录的场记，包括无配乐段落；未指定的视听处理再参考导演提示。\n"+json.dumps(ctx,ensure_ascii=False)
    payload = copy.deepcopy(media_api.ROUTES[route][2]) if route in media_api.ROUTES else {}
    if route.startswith("火山"):
        payload["model"] = os.getenv("ZIMA_LIGHT_SEEDREAM_MODEL" if kind=="image" else "ZIMA_LIGHT_SEEDANCE_MODEL","")
        if not payload["model"]:
            return {"message":f"工作站的{label}模型尚未配置完成。"}
    if kind == "clone":
        return {"message":"请附上已获授权的原声音频，再发送克隆要求。","needs_audio":True,"route":route,"payload":payload}
    if kind == "speech":
        payload["text"] = brief["spoken"]
        speed={"同学闲聊":1.0,"小心试探":0.92,"沉稳克制":0.88,"快人快语":1.12}.get(choices.get("voice"))
        if speed: payload["voice_setting"]["speed"]=speed
    elif kind == "design": payload.update(prompt=prompt,preview_text=brief.get("spoken") or "你好，这是我的声音。")
    elif kind == "music": payload.update(prompt=prompt,lyrics=brief.get("lyrics") or "")
    elif kind == "sfx":
        payload["text"] = prompt
        if brief.get("seconds"): payload["duration_seconds"] = max(.5,min(30,float(brief["seconds"])))
    elif route == "百炼 · 千问生图": payload["input"]["messages"][0]["content"][0]["text"] = prompt
    elif route == "百炼 · 万相视频": payload["input"]["prompt"] = prompt
    elif route == "火山 · 生视频": payload["content"][0]["text"] = prompt
    else: payload["prompt"] = prompt
    return {"message":"已准备好"+label+"。"+description+"\n回复「生成」开始制作，也可以继续告诉我想改哪里。","route":route,"payload":payload}


def result(project, route, data):
    if (data.get("base_resp") or {}).get("status_code",0) or data.get("error") or data.get("code"):
        return {"message":"生成服务未能完成这次制作，请调整描述后重试。"}
    output = data.get("output") or {}
    items = data.get("data") or []
    rows = items if isinstance(items,list) else [items]
    candidates = [data,output,data.get("content") or {}]+rows
    for choice in output.get("choices",[]):
        candidates.extend(choice.get("message",{}).get("content",[]))
    for item in candidates:
        if not isinstance(item,dict): continue
        for field in ("audio_url","video_url","image","url","audio","b64_json","trial_audio"):
            value = item.get(field)
            if not isinstance(value,str) or not value: continue
            if value.startswith(("https://","/media/generated/")):
                return {"message":"作品已生成。","asset":value}
            if field in ("b64_json","audio","trial_audio"):
                blob = base64.b64decode(value,validate=True) if field=="b64_json" else bytes.fromhex(value)
                return save_asset(project,blob,".png" if field=="b64_json" else ".mp3")
    if data.get("voice_id"): return {"message":"音色已生成。","voice":data["voice_id"]}
    status = str(output.get("task_status") or data.get("status") or "").lower()
    if status in ("failed","canceled","cancelled","expired","unknown","succeeded"):
        return {"message":"任务已结束，但没有返回可播放的作品。"}
    task = output.get("task_id") or data.get("id")
    if task or status in ("pending","running","queued"):
        return {"message":"正在制作中…","task":task}
    return {"message":"服务已响应，但没有返回可展示的作品。"}


def save_asset(project, blob, suffix):
    folder = project / "generated"
    folder.mkdir(exist_ok=True)
    path = folder / (secrets.token_hex(12)+suffix)
    path.write_bytes(blob)
    return {"message":"作品已生成。","asset":"/media/generated/"+path.name}
