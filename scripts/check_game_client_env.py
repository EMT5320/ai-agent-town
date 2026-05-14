"""检查本机 Godot 客户端开发环境。"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GODOT_APPDATA_DIR = Path(os.getenv("GODOT_APPDATA_DIR", str(PROJECT_ROOT / ".run" / "godot-appdata")))
KNOWN_GODOT_PATHS = [
    Path(r"D:\Work\tools\godot\4.6.2\Godot_v4.6.2-stable_win64.exe"),
]


def find_godot() -> Path | None:
    """按环境变量、PATH 和本机固定安装路径寻找 Godot。"""
    env_path = os.getenv("GODOT_EXE")
    if env_path and Path(env_path).exists():
        return Path(env_path)

    for command in ["godot", "godot4", "godot4_console"]:
        found = shutil.which(command)
        if found:
            return Path(found)

    for path in KNOWN_GODOT_PATHS:
        if path.exists():
            return path
    return None


def main() -> None:
    """输出 Godot 版本，并用 headless 模式验证项目能打开。"""
    godot = find_godot()
    if not godot:
        raise SystemExit("未找到 Godot。请先安装 Godot，或设置 GODOT_EXE 指向 Godot 可执行文件。")

    # Codex 沙箱不能稳定写入用户 AppData，因此检查时把 Godot 用户目录切到临时目录。
    GODOT_APPDATA_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["APPDATA"] = str(GODOT_APPDATA_DIR)

    version = subprocess.run([str(godot), "--version"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True, env=env)
    project_check = subprocess.run([str(godot), "--headless", "--path", "clients/godot", "--quit", "--verbose"], cwd=PROJECT_ROOT, text=True, capture_output=True, env=env)
    if project_check.returncode != 0:
        raise SystemExit(project_check.stderr or project_check.stdout or "Godot 项目 headless 检查失败。")
    project_output = f"{project_check.stdout}\n{project_check.stderr}"
    fatal_markers = ["SCRIPT ERROR", "Parse Error", "Failed to load script"]
    for marker in fatal_markers:
        if marker in project_output:
            raise SystemExit(project_output)

    print("[client-env] ok", {"godot": str(godot), "version": version.stdout.strip()})


if __name__ == "__main__":
    main()
