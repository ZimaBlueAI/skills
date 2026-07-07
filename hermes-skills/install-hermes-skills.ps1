<#
Hermes Agent · ZimaBlueAI 动效HTML+PPTX+频道对话交付 一键安装 (Windows / PowerShell)
=====================================================================================
把生成能力(viz-deck / viz-charts [/ biz-html-viz])+ 频道对话交付技能(viz-channel)
装进 Hermes 的 skills 目录,配齐依赖。当前投递 adapter = 飞书/Lark。

Hermes 的 skills 目录因部署而异,默认 $HOME\.hermes\skills。先 `hermes doctor` 确认;
不对就用 -Target <你的skills目录> 指定。

用法:
  ./install-hermes-skills.ps1
  ./install-hermes-skills.ps1 -Target "$HOME/.hermes/skills"
  ./install-hermes-skills.ps1 -WithBridges        # huashu + ppt-master(MP4 / 可编辑 PPTX)
  ./install-hermes-skills.ps1 -WithBiz            # 额外装 biz-html-viz
  ./install-hermes-skills.ps1 -Minimal           # 只装动效 HTML 所需
  ./install-hermes-skills.ps1 -FromGithub
#>
[CmdletBinding()]
param(
    [string]$Target = "$HOME\.hermes\skills",
    [switch]$WithBridges,
    [switch]$WithBiz,
    [switch]$Minimal,
    [switch]$FromGithub
)
$ErrorActionPreference = "Stop"
function Ok($m){Write-Host "  [OK] $m" -ForegroundColor Green}
function Warn($m){Write-Host "  [! ] $m" -ForegroundColor Yellow}
function Err($m){Write-Host "  [X ] $m" -ForegroundColor Red}
function Head($m){Write-Host $m -ForegroundColor Blue}

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $Here
$LocalCcs = Join-Path $RepoRoot "claude-code-skills"
$GhRepo = "https://github.com/ZimaBlueAI/skills.git"
$Tmp = Join-Path $env:TEMP "hermes-zima-install-$PID"
$Extract = Join-Path $Tmp "extracted"
$Archive = Join-Path $Target ".zima-replaced"

Head "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Head "  Hermes · 动效HTML + PPTX + 频道对话交付"
Head "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host "目标目录: $Target"
Write-Host ("生成技能来源: " + $(if($FromGithub){"GitHub 实时拉"}else{"本仓库 $LocalCcs"}))
Write-Host ("桥接: " + $(if($WithBridges){"安装"}else{"跳过"}) + "  biz: " + $(if($WithBiz){"安装"}else{"跳过"}) + "  最小: " + $(if($Minimal){"是"}else{"否"}))
Write-Host ""

# [1] 基础环境
Head "[1/5] 基础环境"
$missing = $false
foreach($t in @("git","node","npm","python")){
    $c = Get-Command $t -ErrorAction SilentlyContinue
    if($c){ Ok "$t ($((& $t --version 2>&1 | Select-Object -First 1)))" } else { Err $t; $missing = $true }
}
if($missing){ Err "缺基础工具,先装 git / node / npm / python"; exit 1 }
if(-not $Minimal){
    if(Get-Command ffmpeg -ErrorAction SilentlyContinue){ Ok "ffmpeg" } else { Warn "ffmpeg 未装(只有 HTML→MP4 才需要)" }
}
if(Get-Command hermes -ErrorAction SilentlyContinue){ Ok "hermes" } else { Warn "未在 PATH 找到 hermes(若 skills 目录已确认仍可继续)" }
Write-Host ""

New-Item -ItemType Directory -Force -Path $Target | Out-Null
New-Item -ItemType Directory -Force -Path $Extract | Out-Null

function Archive-Existing($p){
    if(Test-Path $p){
        New-Item -ItemType Directory -Force -Path $Archive | Out-Null
        $stamp = Get-Date -Format "yyyyMMddHHmmss"
        Move-Item $p (Join-Path $Archive ("{0}.{1}.{2}" -f (Split-Path $p -Leaf), $stamp, $PID)) -Force
    }
}

# [2] 生成技能
Head "[2/5] 准备生成技能 (viz-deck / viz-charts$(if($WithBiz){' / biz-html-viz'}))"
if($FromGithub){
    Write-Host "  -> clone $GhRepo ..."
    git clone --depth 1 $GhRepo (Join-Path $Tmp "repo") 2>$null
    $Ccs = Join-Path $Tmp "repo\claude-code-skills"
} else {
    $Ccs = $LocalCcs
}
if(-not (Test-Path $Ccs)){ Err "找不到 $Ccs"; exit 1 }

function Install-Skill($zip, $name){
    if(Test-Path $zip){
        Expand-Archive -Path $zip -DestinationPath $Extract -Force
        $src = Join-Path $Extract ".claude\skills\$name"
        if(Test-Path $src){
            Archive-Existing (Join-Path $Target $name)
            Copy-Item $src (Join-Path $Target $name) -Recurse -Force
            Ok $name
        } else { Warn "zip 内没找到 .claude/skills/$name" }
    } else { Warn "找不到 $zip" }
}

Install-Skill (Join-Path $Ccs "viz-deck\viz-deck.zip") "viz-deck"
Install-Skill (Join-Path $Ccs "viz-charts\viz-charts.zip") "viz-charts"
# gzh-design(公众号排版)是纯文件夹,无 zip,直接拷
$gzhSrc = Join-Path $Ccs "gzh-design"
if(Test-Path $gzhSrc){
    Archive-Existing (Join-Path $Target "gzh-design")
    Copy-Item $gzhSrc (Join-Path $Target "gzh-design") -Recurse -Force
    Ok "gzh-design (公众号排版)"
} else { Warn "找不到 $gzhSrc(公众号排版跳过)" }
if($WithBiz){
    Install-Skill (Join-Path $Ccs "biz-decision-stack\biz-decision-stack.zip") "biz-html-viz"
    $agSrc = Join-Path $Extract ".claude\agents"
    if(Test-Path $agSrc){
        $ag = Join-Path (Split-Path $Target -Parent) "agents"
        New-Item -ItemType Directory -Force -Path $ag | Out-Null
        Copy-Item (Join-Path $agSrc "*") $ag -Recurse -Force
        Ok "biz subagents → $ag"
    }
}
Write-Host ""

# [3] 频道交付技能
Head "[3/5] 频道交付技能 viz-channel + gzh-channel"
foreach($ch in @("viz-channel","gzh-channel")){
    $fdcSrc = Join-Path $Here "skills\$ch"
    if(Test-Path $fdcSrc){
        Archive-Existing (Join-Path $Target $ch)
        Copy-Item $fdcSrc (Join-Path $Target $ch) -Recurse -Force
        Ok "$ch → $Target\$ch"
    } else { Err "找不到 $fdcSrc"; exit 1 }
}
Write-Host ""

# [4] 依赖
Head "[4/5] 依赖"
try { python -m pip install --quiet requests pyyaml; Ok "python: requests + pyyaml(频道投递·飞书adapter)" }
catch { Warn "pip 装 requests/pyyaml 失败(投递需要)" }

if(-not $Minimal){
    $nodeDir = Join-Path $Target "viz-charts\renderers\node"
    if(Test-Path $nodeDir){
        Write-Host "  -> viz-charts 离线渲染 npm install ..."
        try { Push-Location $nodeDir; npm install --silent 2>$null; Pop-Location; Ok "viz-charts 离线渲染就绪" }
        catch { Warn "失败(inline CDN 模式仍可用)" }
    }
}

if($WithBridges){
    $huashu = Join-Path $Target "huashu-design"
    if(-not (Test-Path $huashu)){
        Write-Host "  -> clone huashu-design ..."
        git clone --depth=1 https://github.com/alchaincyf/huashu-design.git $huashu 2>$null
        if(Test-Path $huashu){
            @'
{ "name":"huashu-design-runtime","version":"1.0.0","private":true,
  "dependencies":{"playwright":"^1.48.0","sharp":"^0.33.5","pptxgenjs":"^3.12.0","pdf-lib":"^1.17.1"} }
'@ | Out-File -FilePath (Join-Path $huashu "package.json") -Encoding utf8
            try { Push-Location $huashu; npm install --silent 2>$null; npx playwright install chromium 2>$null; Pop-Location; Ok "huashu-design" }
            catch { Warn "huashu npm/playwright 部分失败" }
        }
    } else { Ok "huashu-design 已存在" }

    $pptm = Join-Path $Target "ppt-master"
    if(-not (Test-Path $pptm)){
        Write-Host "  -> clone ppt-master ..."
        git clone --depth=1 https://github.com/hugohe3/ppt-master.git $pptm 2>$null
        if(Test-Path $pptm){
            try {
                Push-Location $pptm; python -m venv .venv
                & ".venv\Scripts\pip.exe" install --quiet python-pptx edge-tts svglib reportlab Pillow numpy
                Pop-Location; Ok "ppt-master"
            } catch { Warn "ppt-master venv 部分失败" }
        }
    } else { Ok "ppt-master 已存在" }
} else {
    Warn "桥接跳过(动效 HTML 不需要;要 MP4/可编辑PPTX 加 -WithBridges)"
}
Write-Host ""

# [5] 清理(移动而非删除)+ 自检
if(Test-Path $Tmp){
    New-Item -ItemType Directory -Force -Path $Archive | Out-Null
    Move-Item $Tmp (Join-Path $Archive "_install-tmp.$PID") -Force -ErrorAction SilentlyContinue
}
Head "[5/5] 自检"
foreach($s in @("viz-deck","viz-charts","viz-channel","gzh-design","gzh-channel")){
    if(Test-Path (Join-Path $Target $s)){ Ok "$Target\$s" } else { Err "$Target\$s 缺失" }
}
try { python (Join-Path $Target "viz-channel\scripts\channel_deliver.py") --help *> $null; Ok "channel_deliver.py 可运行" }
catch { Warn "channel_deliver.py 自检失败(检查 requests)" }
try { python (Join-Path $Target "gzh-channel\scripts\gzh_card_send.py") --help *> $null; Ok "gzh_card_send.py 可运行" }
catch { Warn "gzh_card_send.py 自检失败(检查 requests)" }
Write-Host ""
Head "━━━ 完成 ━━━"
Write-Host "在你的频道(如飞书)@机器人 试一句:「做一份云度科技 Q2 业绩的动效 HTML 汇报,做完发我」"
Write-Host "也可做成 cron/webhook 自动化。细节见: $Target\viz-channel\references\hermes-channel.md"
