# gzh_send.ps1 — 公众号排版频道发送的一行入口 (优先 lark-cli 凭证,回退 REST) · Windows
# ====================================================================================
# 把 gzh_card_send.py 的 --via auto 封成一行。所有参数透传给 gzh_card_send.py。
#
# 用法:
#   ./gzh_send.ps1 --draft draft.md --to-current
#   ./gzh_send.ps1 --file "文章_排版_摸鱼绿(moyu-green)_预览.html" --to-current `
#       --note "下载后浏览器打开 → 点右上角「一键复制」→ 到公众号编辑器粘贴"

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

$py = "python"
if (Get-Command python3 -ErrorAction SilentlyContinue) { $py = "python3" }

$hasVia = $false
foreach ($a in $args) { if ($a -eq "--via") { $hasVia = $true } }

if ($hasVia) {
    & $py "$here\gzh_card_send.py" @args
} else {
    & $py "$here\gzh_card_send.py" --via auto @args
}
exit $LASTEXITCODE
