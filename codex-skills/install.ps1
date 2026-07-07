# codex-skills one-shot installer (PowerShell, Windows)
#
# Drops the five skills into $HOME\.codex\skills\ and the 9 subagents into $HOME\.codex\agents\.
# Idempotent: re-running upgrades in place.
#
# Usage:
#   .\install.ps1                            # install all five + agents
#   .\install.ps1 -Skill viz-deck            # install just one skill
#   .\install.ps1 -NoAgents                  # all skills, but skip the TOML agents
#   .\install.ps1 -DryRun                    # show what would be done

[CmdletBinding()]
param(
    [string]$Skill = "",
    [switch]$NoAgents,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$homeSkills = Join-Path $HOME ".codex\skills"
$homeCodexAgents = Join-Path $HOME ".codex\agents"

function Invoke-Step($action) {
    if ($DryRun) { Write-Host "DRY: $action" } else { & $action }
}

function Expand-Skill($repoDir, $name) {
    $zip = Join-Path $scriptDir "$repoDir\$repoDir.zip"
    if (-not (Test-Path $zip)) {
        Write-Host "  warn: $zip not found, skipping" -ForegroundColor Yellow
        return
    }
    Write-Host "  unzip $repoDir.zip -> $HOME"
    if (-not $DryRun) {
        Expand-Archive -Path $zip -DestinationPath $HOME -Force
    }
    Write-Host "  [ok] $name"
}

Write-Host "[codex-skills] target: $homeSkills + $homeCodexAgents"
Invoke-Step { New-Item -ItemType Directory -Force -Path $homeSkills | Out-Null }
Invoke-Step { New-Item -ItemType Directory -Force -Path $homeCodexAgents | Out-Null }

if ($Skill -eq "" -or $Skill -eq "biz-decision-stack") {
    Expand-Skill "biz-decision-stack" "biz-html-viz + 9 subagents"
}
if ($Skill -eq "" -or $Skill -eq "viz-deck") {
    Expand-Skill "viz-deck" "viz-deck"
}
if ($Skill -eq "" -or $Skill -eq "viz-charts") {
    Expand-Skill "viz-charts" "viz-charts"
}
if ($Skill -eq "" -or $Skill -eq "zima-html-ppt") {
    Expand-Skill "zima-html-ppt" "zima-html-ppt"
}
if ($Skill -eq "" -or $Skill -eq "gzh-design") {
    Expand-Skill "gzh-design" "gzh-design"
}

if ($NoAgents) {
    Write-Host "[codex-skills] -NoAgents passed, archiving freshly-extracted agents"
    if (-not $DryRun) {
        $archive = Join-Path $homeCodexAgents (".archive\no-agents-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
        New-Item -ItemType Directory -Force -Path $archive | Out-Null
        Get-ChildItem -Path $homeCodexAgents -Filter "0[0-8]-*.toml" -ErrorAction SilentlyContinue |
            Move-Item -Destination $archive -Force
    }
}

Write-Host ""
Write-Host "[codex-skills] installed at:"
Write-Host "  $homeSkills  (skill bodies)"
if (-not $NoAgents) {
    Write-Host "  $homeCodexAgents  (9 TOML subagents)"
}
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1) In Codex CLI run /skills to confirm the five skills appear"
Write-Host "  2) (Optional) Install ppt-master to unlock v3 editable-PPTX:"
Write-Host "       git clone https://github.com/hugohe3/ppt-master `"$homeSkills\ppt-master`""
Write-Host "       cd `"$homeSkills\ppt-master`"; python -m venv .venv"
Write-Host "       .venv\Scripts\pip install python-pptx edge-tts svglib reportlab Pillow numpy"
Write-Host "  3) (Optional) Install huashu-design to unlock v2 motion/video/PPTX:"
Write-Host "       git clone https://github.com/alchaincyf/huashu-design `"$homeSkills\huashu-design`""
Write-Host "       (see INSTALL.md for the package.json + ffmpeg setup)"
