# Rebuild codex-skills zip packages with current Codex paths.

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Add-DirectoryToZip($zip, $sourceDir, $archiveRoot, $zipPath) {
    $sourcePath = (Resolve-Path -LiteralPath $sourceDir).Path
    Get-ChildItem -LiteralPath $sourcePath -Recurse -File | ForEach-Object {
        if ($_.FullName -eq $zipPath -or $_.FullName -like "*.zip.bak") {
            return
        }
        $relative = $_.FullName.Substring($sourcePath.Length).TrimStart('\', '/')
        $entryName = ($archiveRoot.TrimEnd('/') + '/' + ($relative -replace '\\', '/'))
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $_.FullName, $entryName, [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
    }
}

function New-SkillPackage($repoDir, $skillDir, $skillName, [switch]$IncludeAgents) {
    $zipPath = Join-Path $scriptDir "$repoDir\$repoDir.zip"

    $stream = [System.IO.File]::Open($zipPath, [System.IO.FileMode]::Create)
    $zip = New-Object System.IO.Compression.ZipArchive($stream, [System.IO.Compression.ZipArchiveMode]::Create)
    try {
        Add-DirectoryToZip $zip (Join-Path $scriptDir "$repoDir\$skillDir") ".codex/skills/$skillName" $zipPath
        $samplesDir = Join-Path $scriptDir "$repoDir\samples"
        if (Test-Path -LiteralPath $samplesDir) {
            Add-DirectoryToZip $zip $samplesDir ".codex/skills/$skillName/samples" $zipPath
        }
        if ($IncludeAgents) {
            Add-DirectoryToZip $zip (Join-Path $scriptDir "$repoDir\agents-toml") ".codex/agents" $zipPath
        }
    }
    finally {
        $zip.Dispose()
        $stream.Dispose()
    }
    Write-Host "built $zipPath"
}

New-SkillPackage "biz-decision-stack" "biz-html-viz" "biz-html-viz" -IncludeAgents
New-SkillPackage "viz-deck" "viz-deck" "viz-deck"
New-SkillPackage "viz-charts" "viz-charts" "viz-charts"
New-SkillPackage "zima-html-ppt" "." "zima-html-ppt"
New-SkillPackage "gzh-design" "." "gzh-design"
New-SkillPackage "zima-design" "." "zima-design"
