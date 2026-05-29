# channel_send.ps1 — 频道投递的一行入口 (优先 lark-cli 凭证,回退 REST) · Windows
# ============================================================================
# 把 channel_deliver.py 的 --via auto 封成一行。auto 先尝试复用 lark-cli 令牌,
# 取不到再直连 REST。所有参数透传给 channel_deliver.py。
#
# 用法:
#   ./channel_send.ps1 --file output/deck.html --to-current --note "动效报告,下载用浏览器打开"
#   ./channel_send.ps1 --file deck.pptx --to oc_xxx --to-type chat_id

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

$py = "python"
if (Get-Command python3 -ErrorAction SilentlyContinue) { $py = "python3" }

$hasVia = $false
foreach ($a in $args) { if ($a -eq "--via") { $hasVia = $true } }

if ($hasVia) {
    & $py "$here\channel_deliver.py" @args
} else {
    & $py "$here\channel_deliver.py" --via auto @args
}
exit $LASTEXITCODE
