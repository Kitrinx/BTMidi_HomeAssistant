param(
    [string]$Source = "src\\custom_components\\murobox_midi",
    [string]$Destination = "custom_components\\murobox_midi"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourcePath = Join-Path $repoRoot $Source
$destinationPath = Join-Path $repoRoot $Destination

if (-not (Test-Path $sourcePath)) {
    Write-Error "Source path not found: $sourcePath"
    exit 1
}

New-Item -ItemType Directory -Force (Split-Path -Parent $destinationPath) | Out-Null

if (Test-Path $destinationPath) {
    Remove-Item -Recurse -Force $destinationPath
}

Copy-Item -Recurse -Force $sourcePath $destinationPath

Get-ChildItem -Path $destinationPath -Recurse -Directory -Filter "__pycache__" |
    Remove-Item -Recurse -Force
