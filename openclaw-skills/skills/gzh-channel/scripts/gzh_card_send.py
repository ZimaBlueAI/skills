#!/usr/bin/env python3
"""
公众号排版 · 频道发送器 gzh_card_send  (当前 adapter:飞书 / Lark)
================================================================
gzh-channel 技能的自包含发送脚本,三种模式:

  --draft <草稿.md>   发【interactive 卡片】给用户确认 Markdown 草稿:
                      卡片 = 结构摘要(标题/章节/字数) + Markdown 全文代码块。
                      草稿超过 --max-inline(默认 6000 字符)时,卡片只放大纲 +
                      开头预览,并把 .md 作为文件消息一并发出。
                      interactive 发送失败自动回退为带代码围栏的文本消息。
  --file <产物.html>  发文件消息(排版产物:_预览.html / 干净正文.html)。
  --text "..."        发一句文本。

与 viz-channel/channel_deliver.py 同源的凭证/令牌/chat 解析逻辑(自包含,
不跨技能 import):凭证按 命令行 > 环境变量 FEISHU_APP_ID/SECRET
> ~/.bodhi/config.yaml > ~/.lark-cli/config.json;令牌优先 lark-cli 回退 REST。

用法:
  # 发草稿确认卡片到当前频道
  python3 gzh_card_send.py --draft draft.md --to-current

  # 确认后发排版产物
  python3 gzh_card_send.py --file 文章_排版_摸鱼绿(moyu-green)_预览.html --to-current \
      --note "下载后浏览器打开 → 点右上角「复制到公众号」→ 到公众号编辑器粘贴"

  # 解析不到当前频道时显式指定
  python3 gzh_card_send.py --draft draft.md --to oc_xxx --to-type chat_id
"""

import os
import sys
import json
import re
import shutil
import argparse
import subprocess
from pathlib import Path

try:
    import requests
except ImportError:
    print("缺 requests: pip install requests", file=sys.stderr)
    sys.exit(1)


FEISHU_BASE = os.environ.get("FEISHU_API_BASE", "https://open.feishu.cn/open-apis")


# ─────────────────────────────────────────────
# 凭证 / 当前频道 / 令牌 (与 viz-channel 同源)
# ─────────────────────────────────────────────

def load_credentials(cli_app_id=None, cli_app_secret=None) -> tuple:
    app_id = cli_app_id or os.environ.get("FEISHU_APP_ID")
    app_secret = cli_app_secret or os.environ.get("FEISHU_APP_SECRET")
    if app_id and app_secret:
        return app_id, app_secret

    bodhi_config = Path.home() / ".bodhi" / "config.yaml"
    if bodhi_config.exists():
        try:
            import yaml
            c = yaml.safe_load(bodhi_config.read_text(encoding="utf-8"))
            fapp = (c or {}).get("feishu", {})
            app_id = app_id or fapp.get("app_id")
            app_secret = app_secret or fapp.get("app_secret")
            if app_id and app_secret:
                return app_id, app_secret
        except Exception:
            pass

    lark_config = Path.home() / ".lark-cli" / "config.json"
    if lark_config.exists():
        try:
            c = json.loads(lark_config.read_text(encoding="utf-8"))
            app_id = app_id or c.get("appId") or c.get("app_id")
            app_secret = app_secret or c.get("appSecret") or c.get("app_secret")
            if (not app_id or not app_secret) and isinstance(c.get("apps"), dict):
                cur = c.get("current") or next(iter(c["apps"]), None)
                app = c["apps"].get(cur, {}) if cur else {}
                app_id = app_id or app.get("appId") or app.get("app_id")
                app_secret = app_secret or app.get("appSecret") or app.get("app_secret")
        except Exception:
            pass

    return app_id, app_secret


CHAT_ENV_KEYS = [
    "FEISHU_CHAT_ID", "LARK_CHAT_ID",
    "OPENCLAW_CHAT_ID", "OPENCLAW_CHANNEL_CHAT_ID",
    "HERMES_CHAT_ID", "HERMES_CHANNEL_CHAT_ID",
    "CHANNEL_CHAT_ID", "CHAT_ID",
]


def resolve_current_chat() -> tuple:
    for k in CHAT_ENV_KEYS:
        v = os.environ.get(k)
        if v:
            return v, "chat_id"
    return None, None


def _find_lark_cli() -> str:
    for name in ("lark-cli", "lark"):
        p = shutil.which(name)
        if p:
            return p
    return ""


def get_token_via_lark_cli(lark_bin: str) -> str:
    candidates = [
        [lark_bin, "auth", "token", "--type", "tenant"],
        [lark_bin, "auth", "tenant-token"],
        [lark_bin, "token"],
    ]
    for cmd in candidates:
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if out.returncode != 0:
                continue
            txt = out.stdout.strip()
            if txt.startswith("{"):
                try:
                    j = json.loads(txt)
                    tok = (j.get("tenant_access_token") or j.get("token")
                           or j.get("data", {}).get("tenant_access_token"))
                    if tok:
                        return tok
                except Exception:
                    pass
            elif txt and " " not in txt and len(txt) > 20:
                return txt
        except Exception:
            continue
    return ""


def get_tenant_token_rest(app_id: str, app_secret: str) -> str:
    resp = requests.post(
        f"{FEISHU_BASE}/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
        timeout=15,
    )
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"取 token 失败: code={data.get('code')} msg={data.get('msg')}")
    return data["tenant_access_token"]


def acquire_token(via: str, app_id: str, app_secret: str) -> tuple:
    if via in ("auto", "lark-cli"):
        lark_bin = _find_lark_cli()
        if lark_bin:
            tok = get_token_via_lark_cli(lark_bin)
            if tok:
                return tok, "lark-cli"
            if via == "lark-cli":
                raise RuntimeError("--via lark-cli 指定但 lark-cli 取 token 失败")
        elif via == "lark-cli":
            raise RuntimeError("--via lark-cli 指定但找不到 lark-cli/lark 可执行文件")
    if not app_id or not app_secret:
        raise RuntimeError("无 lark-cli 令牌且缺 app_id/app_secret,无法取 token")
    return get_tenant_token_rest(app_id, app_secret), "rest"


# ─────────────────────────────────────────────
# 消息发送
# ─────────────────────────────────────────────

def send_message(token: str, receive_id: str, receive_id_type: str,
                 msg_type: str, content: dict) -> dict:
    resp = requests.post(
        f"{FEISHU_BASE}/im/v1/messages",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        params={"receive_id_type": receive_id_type},
        json={
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": json.dumps(content, ensure_ascii=False),
        },
        timeout=30,
    )
    return resp.json()


def send_text(token: str, receive_id: str, receive_id_type: str, text: str) -> dict:
    return send_message(token, receive_id, receive_id_type, "text", {"text": text})


def upload_file(token: str, file_path: Path, file_type: str = "stream") -> str:
    with open(file_path, "rb") as f:
        resp = requests.post(
            f"{FEISHU_BASE}/im/v1/files",
            headers={"Authorization": f"Bearer {token}"},
            data={"file_type": file_type, "file_name": file_path.name},
            files={"file": (file_path.name, f)},
            timeout=600,
        )
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"文件上传失败: code={data.get('code')} msg={data.get('msg')}")
    return data["data"]["file_key"]


def send_file(token: str, receive_id: str, receive_id_type: str,
              file_path: Path) -> dict:
    key = upload_file(token, file_path)
    return send_message(token, receive_id, receive_id_type, "file", {"file_key": key})


# ─────────────────────────────────────────────
# Markdown 草稿分析 + 确认卡片
# ─────────────────────────────────────────────

def analyze_md(md: str) -> dict:
    """提取标题 / 章节列表 / 字数,用于卡片摘要。"""
    title = ""
    m = re.search(r"^---\s*\n.*?^title:\s*(.+?)\s*$.*?^---\s*$",
                  md, re.M | re.S)
    if m:
        title = m.group(1).strip().strip("\"'")
    if not title:
        m = re.search(r"^#\s+(.+)$", md, re.M)
        title = m.group(1).strip() if m else "(未命名,排版时需确认标题)"
    chapters = re.findall(r"^##\s+(.+)$", md, re.M)
    n_imgs = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", md))
    n_code = len(re.findall(r"^```", md, re.M)) // 2
    words = len(re.sub(r"\s", "", md))
    return {"title": title, "chapters": chapters,
            "n_imgs": n_imgs, "n_code": n_code, "words": words}


def fence(md: str) -> str:
    """4 backtick 围栏,避免与文章内 ``` 代码块冲突。"""
    return "````markdown\n" + md.rstrip() + "\n````"


def build_summary_md(info: dict) -> str:
    lines = [f"**《{info['title']}》**",
             f"章节 **{len(info['chapters'])}** · 图片 {info['n_imgs']}"
             f" · 代码块 {info['n_code']} · 约 **{info['words']}** 字"]
    if info["chapters"]:
        lines.append("")
        for i, c in enumerate(info["chapters"], 1):
            lines.append(f"{i:02d} · {c}")
    return "\n".join(lines)


def build_draft_card(md: str, info: dict, inline: bool) -> dict:
    """飞书 interactive 卡片(经典 v1 结构,markdown 组件带代码围栏)。"""
    elements = [
        {"tag": "markdown", "content": build_summary_md(info)},
        {"tag": "hr"},
    ]
    if inline:
        elements.append({"tag": "markdown", "content": fence(md)})
    else:
        preview = md.strip()[:500]
        elements.append({"tag": "markdown",
                         "content": "**开头预览:**\n" + fence(preview + "\n……")})
        elements.append({"tag": "markdown",
                         "content": "全文较长,完整 Markdown 见随后发送的 `.md` 文件。"})
    elements.append({"tag": "hr"})
    elements.append({"tag": "note", "elements": [{
        "tag": "plain_text",
        "content": "确认无误请回复「确认」开始排版;要调整直接说改哪里(标题/章节/某段文字)。",
    }]})
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "template": "green",
            "title": {"tag": "plain_text", "content": "📝 公众号排版 · Markdown 草稿确认"},
        },
        "elements": elements,
    }


def send_draft(token: str, receive_id: str, receive_id_type: str,
               md_path: Path, max_inline: int) -> bool:
    md = md_path.read_text(encoding="utf-8")
    info = analyze_md(md)
    inline = len(md) <= max_inline

    card = build_draft_card(md, info, inline)
    sent_as = "卡片"
    result = send_message(token, receive_id, receive_id_type, "interactive", card)

    if result.get("code") != 0:
        # 卡片被拒(权限 / 长度 / 组件不支持) → 回退纯文本 + 代码围栏
        print(f"  ⚠ interactive 卡片发送失败 code={result.get('code')}"
              f" msg={result.get('msg')},回退文本消息", file=sys.stderr)
        head = ("📝 公众号排版 · Markdown 草稿确认\n"
                + build_summary_md(info).replace("**", "") + "\n\n")
        body = fence(md) if inline else fence(md.strip()[:500] + "\n……")
        tail = "\n\n确认无误请回复「确认」开始排版;要调整直接说改哪里。"
        sent_as = "文本"
        result = send_text(token, receive_id, receive_id_type, head + body + tail)
        if result.get("code") != 0:
            print(f"  ✗ 文本回退也失败 code={result.get('code')}"
                  f" msg={result.get('msg')}", file=sys.stderr)
            return False

    print(f"  ✓ 草稿确认{sent_as}已发送"
          f" (message_id: {result.get('data', {}).get('message_id', '')[:20]}...)")

    if not inline:
        r2 = send_file(token, receive_id, receive_id_type, md_path)
        if r2.get("code") != 0:
            print(f"  ✗ 全文 .md 附件发送失败 code={r2.get('code')}"
                  f" msg={r2.get('msg')}", file=sys.stderr)
            return False
        print("  ✓ 全文 .md 附件已发送")
    return True


# ─────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="公众号排版 · 频道发送器(飞书)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--draft", help="Markdown 草稿路径 → interactive 确认卡片")
    mode.add_argument("--file", action="append", help="产物文件路径(可多次,如 _预览.html + 干净正文.html)")
    mode.add_argument("--text", help="发一句文本")
    parser.add_argument("--to", help="接收方 ID (open_id / chat_id);不传则配合 --to-current")
    parser.add_argument("--to-current", action="store_true",
                        help="发到当前频道(从平台注入的环境变量解析 chat_id)")
    parser.add_argument("--to-type", default="open_id",
                        choices=["open_id", "user_id", "union_id", "email", "chat_id"])
    parser.add_argument("--note", default="", help="附言(发文件前先发一句文本)")
    parser.add_argument("--max-inline", type=int, default=6000,
                        help="草稿全文内嵌卡片的字符上限,超出改为大纲+md附件(默认 6000)")
    parser.add_argument("--via", default="auto", choices=["auto", "lark-cli", "rest"])
    parser.add_argument("--app-id", help="覆盖 app_id")
    parser.add_argument("--app-secret", help="覆盖 app_secret")
    args = parser.parse_args()

    receive_id, receive_id_type = args.to, args.to_type
    if not receive_id and args.to_current:
        receive_id, receive_id_type = resolve_current_chat()
    if not receive_id:
        print("✗ 缺接收方:传 --to <id> 或在频道会话内用 --to-current", file=sys.stderr)
        sys.exit(2)

    app_id, app_secret = load_credentials(args.app_id, args.app_secret)
    token, source = acquire_token(args.via, app_id, app_secret)
    print(f"令牌来源: {source} → {receive_id} ({receive_id_type})")

    ok = True
    if args.draft:
        p = Path(args.draft)
        if not p.exists():
            print(f"✗ 草稿不存在: {p}", file=sys.stderr)
            sys.exit(1)
        ok = send_draft(token, receive_id, receive_id_type, p, args.max_inline)
    elif args.text:
        r = send_text(token, receive_id, receive_id_type, args.text)
        ok = r.get("code") == 0
        print("  ✓ 文本已发送" if ok else f"  ✗ 发送失败 code={r.get('code')} msg={r.get('msg')}")
    else:
        if args.note:
            send_text(token, receive_id, receive_id_type, args.note)
        for f in args.file:
            p = Path(f)
            if not p.exists():
                print(f"  ✗ 文件不存在: {p}", file=sys.stderr)
                ok = False
                continue
            r = send_file(token, receive_id, receive_id_type, p)
            if r.get("code") != 0:
                print(f"  ✗ {p.name} 发送失败 code={r.get('code')} msg={r.get('msg')}",
                      file=sys.stderr)
                ok = False
            else:
                print(f"  ✓ {p.name} 已发送")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
