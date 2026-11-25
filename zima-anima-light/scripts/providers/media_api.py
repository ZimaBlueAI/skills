"""Fixed HTTPS routes for the studio's media API console."""
import json
import os
import re
import urllib.request
from urllib.error import HTTPError


ARK = "https://ark.cn-beijing.volces.com/api/v3"
DASH = "https://dashscope.aliyuncs.com/api/v1"
MINI = "https://api.minimaxi.com/v1"
OPENAI = "https://api.openai.com/v1"
ELEVEN = "https://api.elevenlabs.io/v1"
ROUTES = {
    "火山 · 生图": (ARK+"/images/generations", "ARK_API_KEY", {"model":"填写已开通的模型 ID","prompt":"","response_format":"url"}),
    "火山 · 生视频": (ARK+"/contents/generations/tasks", "ARK_API_KEY", {"model":"填写已开通的模型 ID","content":[{"type":"text","text":""}]}),
    "火山 · 视频进度": (ARK+"/contents/generations/tasks/{id}", "ARK_API_KEY", {"id":""}),
    "百炼 · 千问生图": (DASH+"/services/aigc/multimodal-generation/generation", "DASHSCOPE_API_KEY", {"model":"qwen-image-2.0","input":{"messages":[{"role":"user","content":[{"text":""}]}]}}),
    "百炼 · 万相视频": (DASH+"/services/aigc/video-generation/video-synthesis", "DASHSCOPE_API_KEY", {"model":"wan2.6-t2v","input":{"prompt":""}}),
    "百炼 · 任务进度": (DASH+"/tasks/{id}", "DASHSCOPE_API_KEY", {"id":""}),
    "MiniMax · 音乐": (MINI+"/music_generation", "MINIMAX_API_KEY", {"model":"music-2.5","prompt":"","lyrics":"","output_format":"url"}),
    "MiniMax · 人声合成": (MINI+"/t2a_v2", "MINIMAX_API_KEY", {"model":"speech-2.8-hd","text":"","voice_setting":{"voice_id":"female-shaonv"},"output_format":"url"}),
    "MiniMax · 音色设计": (MINI+"/voice_design", "MINIMAX_API_KEY", {"prompt":"","preview_text":""}),
    "MiniMax · 音色克隆": (MINI+"/voice_clone", "MINIMAX_API_KEY", {"file_id":0,"voice_id":"my-studio-voice"}),
    "OpenAI · 生图": (OPENAI+"/images/generations", "OPENAI_API_KEY", {"model":"gpt-image-1","prompt":""}),
    "ElevenLabs · 音效": (ELEVEN+"/sound-generation", "ELEVENLABS_API_KEY", {"text":"","duration_seconds":5}),
}


def catalog():
    return [{"name":name, "credential":key, "configured":bool(os.getenv(key)), "example":example}
            for name, (_, key, example) in ROUTES.items()]


def submit(name, payload, project):
    url, key, _ = ROUTES[name]
    token = os.getenv(key)
    if not token:
        raise ValueError(f"请在服务环境中配置 {key}")
    headers = {"Content-Type":"application/json", "Authorization":"Bearer "+token}
    if url.startswith(ELEVEN):
        headers = {"Content-Type":"application/json", "xi-api-key":token}
    if "video-synthesis" in url:
        headers["X-DashScope-Async"] = "enable"
    data = json.dumps(payload).encode()
    if "{id}" in url:
        task = str(payload.get("id", ""))
        if not re.fullmatch(r"[A-Za-z0-9_-]+", task):
            raise ValueError("请填写任务 ID")
        url = url.format(id=task)
        data = None
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            if response.headers.get_content_type().startswith("audio/"):
                import uuid
                import shutil
                folder = project / "generated"
                folder.mkdir(exist_ok=True)
                path = folder / (uuid.uuid4().hex + ".mp3")
                with path.open("xb") as stream:
                    shutil.copyfileobj(response, stream)
                return {"audio_url":"/media/generated/"+path.name}
            return json.load(response)
    except HTTPError as exc:
        raise ValueError(f"HTTP {exc.code} {exc.read(1200).decode(errors='replace')}") from exc
