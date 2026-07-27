# ZimaBlueAI Agent Skills · 安装器（Claude Code / OpenAI Codex CLI 通用，Windows）
#
# 从 dist/<harness>/*.zip 安装。包由 packaging/build.py 从单一源 skills/ 生成，
# 两个 harness 的差别只有安装根目录（.claude\ vs .codex\）与三个 skill 的 description。
#
# 用法：
#   .\packaging\install.ps1                            # 自动探测已装的 harness
#   .\packaging\install.ps1 -Harness claude            # 只装 Claude Code
#   .\packaging\install.ps1 -Harness both              # 两个都装
#   .\packaging\install.ps1 -Skill viz-deck            # 只装一个包
#   .\packaging\install.ps1 -Project C:\path\to\repo   # 装到项目而非 $HOME
#   .\packaging\install.ps1 -NoAgents                  # 跳过 subagent
#   .\packaging\install.ps1 -DryRun                    # 只打印，不动手

[CmdletBinding()]
param(
    [ValidateSet("claude", "codex", "both", "")]
    [string]$Harness = "",
    [string]$Skill = "",
    [string]$Project = "",
    [switch]$NoAgents,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
$dist = Join-Path $root "dist"
$target = if ($Project) { $Project } else { $HOME }

if (-not (Test-Path $dist)) {
    Write-Host "没有 dist/。先构建：python packaging/build.py" -ForegroundColor Red
    exit 1
}

# —— 没指定就按 $HOME 下已存在的 harness 目录来探测 —— #
$harnesses = @()
if (-not $Harness) {
    if (Test-Path (Join-Path $HOME ".claude")) { $harnesses += "claude" }
    if (Test-Path (Join-Path $HOME ".codex"))  { $harnesses += "codex" }
    if ($harnesses.Count -eq 0) {
        Write-Host "没探测到 ~\.claude 或 ~\.codex。用 -Harness claude|codex|both 明确指定。" -ForegroundColor Red
        exit 1
    }
    Write-Host "探测到已安装的 harness：$($harnesses -join ', ')"
}
elseif ($Harness -eq "both") { $harnesses = @("claude", "codex") }
else { $harnesses = @($Harness) }

$installed = 0
foreach ($h in $harnesses) {
    $src = Join-Path $dist $h
    if (-not (Test-Path $src)) {
        Write-Host "  跳过 $h：$src 不存在（跑 python packaging/build.py 生成）" -ForegroundColor Yellow
        continue
    }
    Write-Host ""
    Write-Host "[$h] -> $target\.$h\skills\"
    foreach ($zip in Get-ChildItem -LiteralPath $src -Filter *.zip) {
        $archive = [System.IO.Path]::GetFileNameWithoutExtension($zip.Name)
        if ($Skill -and $archive -ne $Skill) { continue }
        Write-Host "  解开 $($zip.Name)"
        if (-not $DryRun) {
            Expand-Archive -LiteralPath $zip.FullName -DestinationPath $target -Force
        }
        $installed++
    }

    if ($NoAgents -and -not $DryRun) {
        $agentsDir = Join-Path $target ".$h\agents"
        if (Test-Path $agentsDir) {
            $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
            $archiveDir = Join-Path $agentsDir ".archive\no-agents-$stamp"
            New-Item -ItemType Directory -Force -Path $archiveDir | Out-Null
            Get-ChildItem -LiteralPath $agentsDir -Filter "0?-*" -File |
                ForEach-Object { Move-Item -LiteralPath $_.FullName -Destination $archiveDir -Force }
            Write-Host "  -NoAgents：subagent 已移到 $archiveDir"
        }
    }
}

if ($installed -eq 0) {
    Write-Host "没有装上任何包。检查 -Skill 名字，或先跑 python packaging/build.py" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "装好了（$installed 个包）。" -ForegroundColor Green
Write-Host ""
Write-Host "验证："
Write-Host "  Claude Code   /skills"
Write-Host "  Codex CLI     /skills   （subagent 用 /agents）"
Write-Host ""
Write-Host "可选桥接："
Write-Host "  ppt-master（真编辑 PPTX / TTS 旁白，MIT）"
Write-Host "    git clone https://github.com/hugohe3/ppt-master `$HOME\.claude\skills\ppt-master"
Write-Host "    cd `$HOME\.claude\skills\ppt-master; python -m venv .venv"
Write-Host "    .venv\Scripts\pip install python-pptx edge-tts svglib reportlab Pillow numpy"
Write-Host "  huashu-design（动画 / 视频 / 设计哲学）见 docs\install-guide.md"
Write-Host ""
Write-Host "技能脚本会同时探测 ~\.codex、~\.agents、~\.claude 三个位置，桥接装在哪个下面都能找到。"
