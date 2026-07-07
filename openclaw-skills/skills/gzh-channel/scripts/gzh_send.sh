#!/usr/bin/env bash
# gzh_send.sh — 公众号排版频道发送的一行入口 (优先 lark-cli 凭证,回退 REST)
# =======================================================================
# 把 gzh_card_send.py 的 --via auto 封成一行。
#
# 用法:
#   bash gzh_send.sh --draft draft.md --to-current                     # 草稿确认卡片
#   bash gzh_send.sh --file 文章_排版_摸鱼绿(moyu-green)_预览.html --to-current \
#       --note "下载后浏览器打开 → 点右上角「一键复制」→ 到公众号编辑器粘贴"
#
# 所有参数透传给 gzh_card_send.py。默认补 --via auto(可被显式 --via 覆盖)。

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PY="python3"
command -v python3 >/dev/null 2>&1 || PY="python"

HAS_VIA=0
for a in "$@"; do
  [ "$a" = "--via" ] && HAS_VIA=1
done

if [ "$HAS_VIA" -eq 1 ]; then
  exec "$PY" "$HERE/gzh_card_send.py" "$@"
else
  exec "$PY" "$HERE/gzh_card_send.py" --via auto "$@"
fi
