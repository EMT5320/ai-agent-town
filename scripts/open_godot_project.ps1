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
$candidates += "D:\Work\tools\godot\4.6.2\Godot_v4.6.2-stable_win64.exe"

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
