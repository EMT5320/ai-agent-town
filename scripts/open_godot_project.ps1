param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$projectDir = Join-Path $projectRoot "clients\godot"

$candidates = @()
if (-not [string]::IsNullOrWhiteSpace($env:GODOT_EXE)) {
    $candidates += $env:GODOT_EXE
}
$candidates += "D:\Work\tools\godot\4.6.2\Godot_v4.6.2-stable_win64_console.exe"
$candidates += "D:\Work\tools\godot\4.6.2\Godot_v4.6.2-stable_win64.exe"
$wingetRoot = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
if (Test-Path -LiteralPath $wingetRoot) {
    $candidates += Get-ChildItem -LiteralPath $wingetRoot -Recurse -Filter "Godot*_console.exe" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
    $candidates += Get-ChildItem -LiteralPath $wingetRoot -Recurse -Filter "Godot*.exe" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
}
$commands = @("godot_console", "godot")
foreach ($command in $commands) {
    $found = Get-Command $command -ErrorAction SilentlyContinue
    if ($found) {
        $candidates += $found.Source
    }
}

$godot = $null
foreach ($candidate in $candidates) {
    if ($candidate -and (Test-Path -LiteralPath $candidate)) {
        $godot = $candidate
        break
    }
}

if (-not $godot) {
    throw "Godot executable was not found. Run npm.cmd run client:env or set GODOT_EXE."
}

if ($DryRun) {
    Write-Output "GODOT_EXE=$godot"
    Write-Output "PROJECT_DIR=$projectDir"
    exit 0
}

Start-Process -FilePath $godot -ArgumentList @("--path", $projectDir)
