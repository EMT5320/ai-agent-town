# 打开 Agent Valley 的 Godot 客户端项目。
# 优先使用 GODOT_EXE 环境变量，其次使用本机固定安装路径。

$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$projectPath = Join-Path $projectRoot "clients\godot\project.godot"

$candidates = @()
if ($env:GODOT_EXE) {
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
    throw "未找到 Godot。请先运行 npm.cmd run client:env 检查环境，或设置 GODOT_EXE。"
}

Start-Process -FilePath $godot -ArgumentList "--path", (Split-Path -Parent $projectPath)
