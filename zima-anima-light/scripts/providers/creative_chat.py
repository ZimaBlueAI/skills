"""Server-owned briefs, confirmation and async generation status."""
import base64
import json
import os
import re
import secrets
import threading
import urllib.request

from providers import creative_context as creative
from providers import media_api, seedream
from providers.http_json import post_json

sessions = {}
guard = threading.Lock()


def upload_sample(encoded):
    sample = base64.b64decode(encoded,validate=True)
    if not sample or len(sample)>20*1024*1024:
        raise ValueError("请提供 20 MB 以内的声音样本。")
    boundary = secrets.token_hex(16)
    ext = "wav" if sample.startswith(b"RIFF") else "m4a" if sample[4:8]==b"ftyp" else "mp3"
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"purpose\"\r\n\r\nvoice_clone\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"sample.{ext}\"\r\nContent-Type: application/octet-stream\r\n\r\n").encode()+sample+f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(media_api.MINI+"/files/upload",data=body,headers={
        "Authorization":"Bearer "+os.environ["MINIMAX_API_KEY"],"Content-Type":"multipart/form-data; boundary="+boundary})
    with urllib.request.urlopen(req,timeout=120) as res:
        return json.load(res)["file"]["file_id"]


def handle(project, doc, body):
    sid = body.get("session")
    with guard:
        if not sid:
            sid = secrets.token_urlsafe(20)
            sessions[sid] = {"messages":[],"lock":threading.Lock()}
        session = sessions.get(sid)
    if session is None:
        return {"message":"会话已结束，请再描述一次想做的作品。","session":None}
    with session["lock"]:
        result = advance(project,doc,body,session)
    return {"session":sid,**result}


def execute_plan(project, plan):
    route,payload = plan["route"],dict(plan["payload"])
    if route=="local-seedream":
        return creative.save_asset(project,seedream.generate(payload["prompt"])["bytes"],".png")
    if route=="project-image":
        data=post_json(os.environ["PCV_OPENAI_IMAGE_BASE_URL"].rstrip("/")+"/images/generations",
                       {"model":os.environ["PCV_OPENAI_IMAGE_MODEL"],"prompt":payload["prompt"],"n":1},
                       headers={"Authorization":"Bearer "+os.environ["PCV_OPENAI_IMAGE_API_KEY"]},timeout=300)
        return creative.result(project,route,data)
    reply=creative.result(project,route,media_api.submit(route,payload,project))
    if plan.get("needs_audio") and ("asset" in reply or "voice" in reply):
        reply["voice"]=payload["voice_id"]
    return reply


def advance(project,doc,body,s):
    from providers import work_queue as queue
    message=str(body.get("message","")).strip()[:4000]
    if body.get("poll"):
        row=next((r for r in queue.listing(project) if r["id"]==s.get("job")),None)
        if row and row["state"] in ("queued","remote","running"):return {"message":"监工正在跟进制作。","pending":True}
        return (row or {}).get("result") or {"message":"请在监工队列查看这项任务。"}
    if re.fullmatch(r"(?:确认付费生成|确认付费制作|同意付费生成)[。！! ]*",message):
        job=s.get("job")
        if s.get("plan",{}).get("needs_audio") and not job:
            if not body.get("sample"):return {"message":"请先附上声音样本。","needs_audio":True}
            plan=s["plan"]
            plan["payload"].update(file_id=upload_sample(body["sample"]),voice_id="studio-"+secrets.token_hex(8))
            job=s["job"]=queue.enqueue(project,s["messages"][-1],plan)
        if job and queue.action(project,job,"approve"):
            return {"message":f"任务 {job} 已获付费确认，监工已接手。","pending":True}
        return {"message":"当前没有可确认的待制作任务。"}
    if message in ("生成","开始生成","确认","开始") and s.get("plan"):
        return {"message":"本次生成将使用付费 API。回复「确认付费生成」仅授权这一项任务。","needs_audio":bool(s["plan"].get("needs_audio"))}
    priority=queue.intent(project,message)
    if priority:return {"message":priority}
    if not message:return {"message":"想制作什么？"}
    paid_plan=message=="确认付费解析" and bool(s.get("messages"))
    if not paid_plan:
        s["messages"]=(s.get("messages",[])+[message])[-8:]
    old=s.pop("job",None)
    if old:queue.action(project,old,"cancel")
    plan=creative.prepare(project,doc,body.get("selection") or {},s["messages"],paid_plan=paid_plan,choices=body.get("choices"))
    s["plan"]=plan
    if plan.get("route") and not plan.get("needs_audio"):
        s["job"]=queue.enqueue(project,s["messages"][-1],plan)
    reply={k:v for k,v in plan.items() if k in ("message","needs_audio")}
    if plan.get("route"):
        reply["message"]=reply["message"].split("\n回复")[0]+"\n本次制作调用付费 API，按供应商实际用量计费。回复「确认付费生成」仅批准此任务。"
    return reply
