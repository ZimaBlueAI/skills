"""Project-owned production queue. Only confirmed rows can be submitted."""
import json
import re
import sqlite3
import threading
import time
from contextlib import contextmanager

from providers import media_api, creative_context


@contextmanager
def db(project):
    folder = project / "queue"
    folder.mkdir(exist_ok=True)
    conn = sqlite3.connect(folder / "production.sqlite",timeout=10,isolation_level="IMMEDIATE")
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY, title TEXT, plan TEXT, state TEXT,
                priority INTEGER DEFAULT 0, approved REAL, started REAL, updated REAL,
                remote TEXT, next_poll REAL DEFAULT 0, result TEXT DEFAULT '{}')""")
            yield conn
    finally:
        conn.close()


def enqueue(project,title,plan,priority=False):
    with db(project) as c:
        return c.execute("INSERT INTO jobs(title,plan,state,priority,updated) VALUES(?,?,'waiting',?,?)",
                         (title,json.dumps(plan),int(priority),time.time())).lastrowid


def action(project,ident,verb):
    with db(project) as c:
        if verb=="approve":
            cur=c.execute("UPDATE jobs SET state='queued',approved=?,updated=? WHERE id=? AND state='waiting'",(time.time(),time.time(),ident))
        elif verb=="promote":
            cur=c.execute("UPDATE jobs SET priority=(SELECT COALESCE(MAX(priority),0)+1 FROM jobs WHERE state IN ('waiting','queued')) WHERE id=? AND state IN ('waiting','queued')",(ident,))
        elif verb=="cancel":
            cur=c.execute("UPDATE jobs SET state='cancelled',plan='{}',updated=? WHERE id=? AND state IN ('waiting','queued')",(time.time(),ident))
        else: raise ValueError("未知队列操作")
        return cur.rowcount==1


def listing(project):
    with db(project) as c:
        rows=c.execute("""SELECT id,title,state,priority,approved,started,updated,result FROM jobs
            ORDER BY CASE state WHEN 'running' THEN 0 WHEN 'remote' THEN 1 WHEN 'queued' THEN 2 WHEN 'waiting' THEN 3 ELSE 4 END,
            priority DESC,id""").fetchall()
    return [dict(r,result=json.loads(r["result"]),slow=r["state"] in ("running","remote") and time.time()-(r["started"] or time.time())>300) for r in rows]


def intent(project,message):
    if not re.search("插队|优先|提前|先做|先生成|排到最前",message):
        return None
    rows=[r for r in listing(project) if r["state"] in ("waiting","queued")]
    number=re.search(r"(?:#|任务\s*|编号\s*)(\d+)",message)
    if number: matches=[r for r in rows if r["id"]==int(number[1])]
    else:
        terms=re.findall(r"[a-zA-Z]+\d+",message)+re.findall(r"(?=([\u4e00-\u9fff]{2}))",message)
        scores=[(sum(t.lower() in r["title"].lower() for t in terms),r) for r in rows]
        best=max((s for s,_ in scores),default=0)
        matches=[r for s,r in scores if s==best and s>0]
    if not matches and not re.search("任务|队列|插队|提前|排到最前",message):
        return None
    if len(matches)!=1: return "请指定要提前的任务编号，例如「让任务 3 插队」。"
    row=matches[0]
    if not action(project,row["id"],"promote"):return "这项任务刚刚开始执行，队列已更新。"
    return f"任务 {row['id']} 已提前。"+("确认费用后即可排入执行。" if row["state"]=="waiting" else "将在可用执行位接续制作。")


def run_once(project):
    with db(project) as c:
        c.execute("BEGIN IMMEDIATE")
        row=c.execute("""SELECT * FROM jobs WHERE (state='remote' AND next_poll<=?) OR (state='queued' AND approved IS NOT NULL)
            ORDER BY CASE state WHEN 'remote' THEN 0 ELSE 1 END,priority DESC,id LIMIT 1""",(time.time(),)).fetchone()
        if not row:return False
        polling=row["state"]=="remote"
        if polling:
            c.execute("UPDATE jobs SET next_poll=? WHERE id=?",(time.time()+330,row["id"]))
        else:
            c.execute("UPDATE jobs SET state='running',started=?,updated=? WHERE id=?",(time.time(),time.time(),row["id"]))
    plan=json.loads(row["plan"])
    try:
        if polling:
            route="百炼 · 任务进度" if plan["route"].startswith("百炼") else "火山 · 视频进度"
            reply=creative_context.result(project,route,media_api.submit(route,{"id":row["remote"]},project))
        else:
            from providers.creative_chat import execute_plan
            reply=execute_plan(project,plan)
        remote=reply.pop("task",None) or (row["remote"] if reply.get("message")=="正在制作中…" else None)
        status="remote" if remote else "done" if reply.get("asset") or reply.get("voice") else "failed"
    except Exception:
        remote=row["remote"]
        status="remote" if polling and time.time()-row["started"]<3600 else "blocked"
        reply={"message":"查询暂时失败，稍后继续跟踪。" if status=="remote" else "请核对供应商任务记录，避免重复付费。后续任务继续执行。"}
    with db(project) as c:
        c.execute("UPDATE jobs SET state=?,remote=?,next_poll=?,updated=?,result=? WHERE id=?",
                  (status,remote,time.time()+5,time.time(),json.dumps(reply),row["id"]))
    return True


def start(project):
    with db(project) as c:
        c.execute("UPDATE jobs SET state='blocked',result=? WHERE state='running'",(json.dumps({"message":"服务重启时正在提交，请先核对供应商记录。"}),))
    def worker():
        while True:
            try:
                if run_once(project): continue
            except (sqlite3.Error,OSError):
                pass
            time.sleep(1)
    for i in range(2):
        threading.Thread(target=worker,name=f"production-worker-{i}",daemon=True).start()
