#!/usr/bin/env python3
"""
频道交付桥 channel_deliver  (当前 adapter:飞书 / Lark)
=====================================================
把 viz-deck / viz-charts / biz-html-viz 生成的动效 HTML、PPTX、MP4、PDF、图片,
发给指定用户或【当前频道】(channel chat)。

频道无关的入口是 channel_send.sh / .ps1;本脚本是**当前实现的频道适配器**——
飞书 / Lark(open.feishu.cn REST + 可选复用 lark-cli 令牌)。要支持企业微信 / Slack /
Telegram,在本文件按相同结构(分类 → 上传 → 发消息)加 adapter,上层无需改动。

仓库本身只管"生成",这个脚本管"送达"。
本脚本提供:
  - --via {auto,lark-cli,rest}  : 投递通道。auto = 优先复用 lark-cli 的凭证/令牌,回退直连 REST
  - --to-current                : 自动解析当前频道 chat_id (从 OpenClaw/Hermes 注入的环境变量)
  - 更稳的 mp4 时长探测 (有 ffprobe 时带 duration,飞书视频消息更友好)

支持的文件 → 飞书消息类型:
  .html  → 文件消息(用户下载用浏览器开,动效保留)
  .pptx  → 文件消息
  .pdf   → 文件消息
  .mp4   → 视频消息(飞书原生播放)
  .png/.jpg/... → 图片消息

用法:
  # 发单个文件给当前频道(频道对话场景最常用)
  python3 channel_deliver.py --file output/deck.html --to-current

  # 发给指定用户
  python3 channel_deliver.py --file deck.html --to ou_xxx

  # 发到群,带附言
  python3 channel_deliver.py --file deck.pptx --to oc_xxx --to-type chat_id \\
    --note "可编辑 PPT,在 PowerPoint 里直接改"

  # 强制走直连 REST(不尝试 lark-cli)
  python3 channel_deliver.py --file deck.html --to-current --via rest

凭证按优先级自动找:
  命令行 --app-id/--app-secret > 环境变量 FEISHU_APP_ID/SECRET
  > ~/.bodhi/config.yaml > ~/.lark-cli/config.json
"""

import os
import sys
import json
import time
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
# 配置加载 (命令行 > env > ~/.bodhi/config.yaml > ~/.lark-cli/config.json)
# ─────────────────────────────────────────────

def load_credentials(cli_app_id=None, cli_app_secret=None) -> tuple:
    """返回 (app_id, app_secret)。"""
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
            # lark-cli 配置结构可能嵌套,尽量找
            app_id = app_id or c.get("appId") or c.get("app_id")
            app_secret = app_secret or c.get("appSecret") or c.get("app_secret")
            # 有的版本把当前 app 放在 apps[current] 下
            if (not app_id or not app_secret) and isinstance(c.get("apps"), dict):
                cur = c.get("current") or next(iter(c["apps"]), None)
                app = c["apps"].get(cur, {}) if cur else {}
                app_id = app_id or app.get("appId") or app.get("app_id")
                app_secret = app_secret or app.get("appSecret") or app.get("app_secret")
        except Exception:
            pass

    return app_id, app_secret


# ─────────────────────────────────────────────
# 当前频道 chat_id 解析 (--to-current)
# ─────────────────────────────────────────────

CHAT_ENV_KEYS = [
    "FEISHU_CHAT_ID", "LARK_CHAT_ID",
    "OPENCLAW_CHAT_ID", "OPENCLAW_CHANNEL_CHAT_ID",
    "HERMES_CHAT_ID", "HERMES_CHANNEL_CHAT_ID",
    "CHANNEL_CHAT_ID", "CHAT_ID",
]


def resolve_current_chat() -> tuple:
    """
    从平台注入的环境变量解析当前频道。
    返回 (receive_id, receive_id_type)。解析不到则 (None, None)。
    OpenClaw/Hermes 在频道会话里通常会把当前 chat_id 注入环境;
    若没有,SKILL.md 会指导 agent 从频道上下文里取并用 --to 显式传入。
    """
    for k in CHAT_ENV_KEYS:
        v = os.environ.get(k)
        if v:
            # oc_ 开头是群,o_/ou_ 是单聊 open_id;chat_id 类型对两者都适用
            return v, "chat_id"
    return None, None


# ─────────────────────────────────────────────
# 令牌获取 (优先 lark-cli,回退 REST)
# ─────────────────────────────────────────────

def _find_lark_cli() -> str:
    for name in ("lark-cli", "lark"):
        p = shutil.which(name)
        if p:
            return p
    return ""


def get_token_via_lark_cli(lark_bin: str) -> str:
    """
    尝试用 lark-cli 取 tenant_access_token。
    lark-cli 各版本子命令不一,这里best-effort,失败返回空串由上层回退 REST。
    """
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
            # 可能直接是 token,也可能是 JSON
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
    """返回 (token, source)。"""
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
    # auto 回退 / rest
    if not app_id or not app_secret:
        raise RuntimeError("无 lark-cli 令牌且缺 app_id/app_secret,无法取 token")
    return get_tenant_token_rest(app_id, app_secret), "rest"


# ─────────────────────────────────────────────
# 文件分类 + 上传 + 发送
# ─────────────────────────────────────────────

FILE_TYPE_MAP = {
    ".pdf": "pdf",
    ".ppt": "ppt", ".pptx": "ppt",
    ".doc": "doc", ".docx": "doc",
    ".xls": "xls", ".xlsx": "xls",
    ".mp4": "mp4",
    ".opus": "opus",
}


def classify(file_path: Path) -> dict:
    ext = file_path.suffix.lower()
    if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"):
        return {"category": "image", "msg_type": "image"}
    if ext == ".mp4":
        return {"category": "media", "msg_type": "media", "file_type": "mp4"}
    file_type = FILE_TYPE_MAP.get(ext, "stream")
    return {"category": "file", "msg_type": "file", "file_type": file_type}


def probe_mp4_duration_ms(file_path: Path) -> int:
    """有 ffprobe 时探测 mp4 时长(毫秒),取不到返回 0。"""
    ff = shutil.which("ffprobe")
    if not ff:
        return 0
    try:
        out = subprocess.run(
            [ff, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)],
            capture_output=True, text=True, timeout=20,
        )
        if out.returncode == 0 and out.stdout.strip():
            return int(float(out.stdout.strip()) * 1000)
    except Exception:
        pass
    return 0


def upload_image(token: str, file_path: Path) -> str:
    with open(file_path, "rb") as f:
        resp = requests.post(
            f"{FEISHU_BASE}/im/v1/images",
            headers={"Authorization": f"Bearer {token}"},
            data={"image_type": "message"},
            files={"image": (file_path.name, f)},
            timeout=120,
        )
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"图片上传失败: code={data.get('code')} msg={data.get('msg')}")
    return data["data"]["image_key"]


def upload_file(token: str, file_path: Path, file_type: str) -> str:
    fields = {"file_type": file_type, "file_name": file_path.name}
    if file_type == "mp4":
        dur = probe_mp4_duration_ms(file_path)
        if dur:
            fields["duration"] = str(dur)
    with open(file_path, "rb") as f:
        resp = requests.post(
            f"{FEISHU_BASE}/im/v1/files",
            headers={"Authorization": f"Bearer {token}"},
            data=fields,
            files={"file": (file_path.name, f)},
            timeout=600,
        )
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"文件上传失败: code={data.get('code')} msg={data.get('msg')}")
    return data["data"]["file_key"]


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


def deliver(file_path: Path, token: str, receive_id: str,
            receive_id_type: str) -> dict:
    if not file_path.exists():
        return {"ok": False, "file": str(file_path), "error": "文件不存在"}

    info = classify(file_path)
    size_mb = file_path.stat().st_size / 1024 / 1024
    print(f"  → {file_path.name} ({size_mb:.1f}MB, {info['category']})")

    if size_mb > 30:
        print(f"    ⚠ 文件 {size_mb:.1f}MB 超过飞书 ~30MB 文件消息上限,可能失败。")

    try:
        if info["category"] == "image":
            key = upload_image(token, file_path)
            content = {"image_key": key}
        else:
            key = upload_file(token, file_path, info.get("file_type", "stream"))
            content = {"file_key": key}

        result = send_message(token, receive_id, receive_id_type,
                              info["msg_type"], content)
        if result.get("code") != 0:
            return {"ok": False, "file": file_path.name,
                    "error": f"发送失败 code={result.get('code')} msg={result.get('msg')}"}

        msg_id = result.get("data", {}).get("message_id", "")
        print(f"    ✓ 已发送 (message_id: {msg_id[:20]}...)")
        return {"ok": True, "file": file_path.name, "message_id": msg_id}
    except Exception as e:
        return {"ok": False, "file": file_path.name, "error": str(e)}


# ─────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="飞书交付桥 (channel edition)")
    parser.add_argument("--file", action="append", required=True,
                        help="要发的文件,可多次")
    parser.add_argument("--to", help="接收方 ID (open_id / chat_id);不传则配合 --to-current")
    parser.add_argument("--to-current", action="store_true",
                        help="发到当前频道(从平台注入的环境变量解析 chat_id)")
    parser.add_argument("--to-type", default="open_id",
                        choices=["open_id", "user_id", "union_id", "email", "chat_id"],
                        help="接收方 ID 类型(--to-current 时自动设为 chat_id)")
    parser.add_argument("--note", default="", help="附言(发文件前先发一句文本)")
    parser.add_argument("--via", default="auto",
                        choices=["auto", "lark-cli", "rest"],
                        help="投递通道:auto=优先 lark-cli 凭证再回退 REST")
    parser.add_argument("--app-id", help="覆盖 app_id")
    parser.add_argument("--app-secret", help="覆盖 app_secret")
    args = parser.parse_args()

    # 接收方
    receive_id, receive_id_type = args.to, args.to_type
    if args.to_current:
        rid, rtype = resolve_current_chat()
        if not rid:
            print("✗ --to-current 解析不到当前频道 chat_id。", file=sys.stderr)
            print("  请确认平台注入了 FEISHU_CHAT_ID / OPENCLAW_CHAT_ID / HERMES_CHAT_ID 之一,",
                  file=sys.stderr)
            print("  或改用 --to <chat_id> --to-type chat_id 显式指定。", file=sys.stderr)
            sys.exit(1)
        receive_id, receive_id_type = rid, rtype
    if not receive_id:
        print("✗ 必须提供 --to 或 --to-current", file=sys.stderr)
        sys.exit(1)

    # 凭证 + 令牌
    app_id, app_secret = load_credentials(args.app_id, args.app_secret)
    try:
        token, src = acquire_token(args.via, app_id, app_secret)
    except Exception as e:
        print(f"✗ {e}", file=sys.stderr)
        print("  设 FEISHU_APP_ID / FEISHU_APP_SECRET,或确保 ~/.lark-cli/config.json 存在",
              file=sys.stderr)
        sys.exit(1)

    print("━━━ 飞书交付 ━━━")
    print(f"令牌来源: {src}")
    print(f"接收方: {receive_id} ({receive_id_type})")
    print(f"文件数: {len(args.file)}\n")

    if args.note:
        send_text(token, receive_id, receive_id_type, args.note)
        print(f"  附言: {args.note}\n")

    results = []
    for fp in args.file:
        results.append(deliver(Path(fp), token, receive_id, receive_id_type))
        time.sleep(0.5)

    print()
    ok = sum(1 for r in results if r["ok"])
    fail = len(results) - ok
    print(f"━━━ 完成: 成功 {ok}, 失败 {fail} ━━━")
    if fail:
        for r in results:
            if not r["ok"]:
                print(f"  ✗ {r['file']}: {r['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
