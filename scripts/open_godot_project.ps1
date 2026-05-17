param(
    [switch]$DryRun,
    [switch]$Run,
    [switch]$Editor,
    [string]$Scene = ""
)

$ErrorActionPreference = "Stop"

if ($Run -and $Editor) {
    throw "Use only one mode: -Run or -Editor."
}

$mode = "editor"
if ($Run) {
    $mode = "run"
}

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

$arguments = @("--editor", "--path", $projectDir)
if ($mode -eq "run") {
    $arguments = @("--path", $projectDir)
    # -Scene is only appended in run mode; empty value uses project.godot main scene.
    if (-not [string]::IsNullOrWhiteSpace($Scene)) {
        if ($Scene -notmatch "^res://.+\.tscn$") {
            throw "Scene must be a Godot scene path like res://scenes/world_main.tscn."
        }
        $arguments += $Scene
    }
}
$importArguments = @("--headless", "--import", "--path", $projectDir)

if ($DryRun) {
    Write-Output "MODE=$mode"
    Write-Output "GODOT_EXE=$godot"
    Write-Output "PROJECT_DIR=$projectDir"
    if ($mode -eq "run") {
        Write-Output "IMPORT_ARGS=$($importArguments -join ' ')"
    }
    Write-Output "GODOT_ARGS=$($arguments -join ' ')"
    exit 0
}

if ($mode -eq "run") {
    & $godot @importArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Godot asset import failed with exit code $LASTEXITCODE."
    }
}

Start-Process -FilePath $godot -ArgumentList $arguments
