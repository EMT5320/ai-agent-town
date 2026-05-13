"""跨平台检查脚本：编译 Python 后端、检查前端 JS、运行 smoke test。"""

from pathlib import Path
import py_compile
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

for path in sorted((ROOT / "backend" / "app").rglob("*.py")):
    py_compile.compile(str(path), doraise=True)

frontend_check = subprocess.run(["node", "--check", "frontend/app.js"], cwd=ROOT)
if frontend_check.returncode != 0:
    raise SystemExit(frontend_check.returncode)

smoke = subprocess.run([sys.executable, "scripts/smoke_test.py"], cwd=ROOT)
if smoke.returncode != 0:
    raise SystemExit(smoke.returncode)
