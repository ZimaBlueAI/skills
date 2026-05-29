#!/usr/bin/env python3
"""
resolve_chat.py — 打印当前频道 chat_id (供 SKILL 自检 / 调试)
============================================================
频道对话场景里,agent 要把生成的文件发回【当前这个会话】。
本工具从平台注入的环境变量里解析 chat_id 并打印;解析不到则非零退出,
此时 SKILL.md 会指导 agent 从频道事件上下文里取 chat_id 显式传给投递脚本。

用法:
  python3 resolve_chat.py            # 打印 chat_id,或报"未解析到"
  python3 resolve_chat.py --quiet    # 只打印 id,无附加文本(便于 shell 取值)
"""
import os
import sys

CHAT_ENV_KEYS = [
    "FEISHU_CHAT_ID", "LARK_CHAT_ID",
    "OPENCLAW_CHAT_ID", "OPENCLAW_CHANNEL_CHAT_ID",
    "HERMES_CHAT_ID", "HERMES_CHANNEL_CHAT_ID",
    "CHANNEL_CHAT_ID", "CHAT_ID",
]


def main():
    quiet = "--quiet" in sys.argv
    for k in CHAT_ENV_KEYS:
        v = os.environ.get(k)
        if v:
            if quiet:
                print(v)
            else:
                print(f"chat_id = {v}  (来源环境变量 {k})")
            return 0
    if not quiet:
        sys.stderr.write(
            "未从环境变量解析到当前频道 chat_id。\n"
            "可设置 FEISHU_CHAT_ID / OPENCLAW_CHAT_ID / HERMES_CHAT_ID 之一,\n"
            "或在投递时用 --to <chat_id> --to-type chat_id 显式指定。\n"
            "检查的变量: " + ", ".join(CHAT_ENV_KEYS) + "\n"
        )
    return 2


if __name__ == "__main__":
    sys.exit(main())
