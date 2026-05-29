#!/usr/bin/env bash
# channel_send.sh — 频道投递的一行入口 (优先 lark-cli 凭证,回退 REST)
# ================================================================
# 这是 SKILL 推荐的投递入口:把 channel_deliver.py 的 --via auto 封成一行。
# auto 通道会先尝试复用 lark-cli 的令牌(明镜先生那套已配),取不到再直连 REST。
#
# 用法:
#   bash channel_send.sh --file output/deck.html --to-current --note "动效报告,下载用浏览器打开"
#   bash channel_send.sh --file deck.pptx --to oc_xxx --to-type chat_id
#
# 所有参数透传给 channel_deliver.py。默认补 --via auto(可被显式 --via 覆盖)。

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PY="python3"
command -v python3 >/dev/null 2>&1 || PY="python"

# 若调用方没指定 --via,补一个 auto
HAS_VIA=0
for a in "$@"; do
  [ "$a" = "--via" ] && HAS_VIA=1
done

if [ "$HAS_VIA" -eq 1 ]; then
  exec "$PY" "$HERE/channel_deliver.py" "$@"
else
  exec "$PY" "$HERE/channel_deliver.py" --via auto "$@"
fi
