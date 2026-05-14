"""跨平台检查脚本：编译 Python 后端、检查前端 JS、运行 smoke test。"""

from pathlib import Path
import py_compile
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

# Windows 上仓库内的 __pycache__ 可能被权限或占用状态卡住。
# 检查脚本只需要验证 Python 文件能编译通过，因此把字节码写到临时目录，避免污染源码树。
with tempfile.TemporaryDirectory(prefix="agent-town-check-") as cache_dir:
    cache_root = Path(cache_dir)
    for path in sorted((ROOT / "backend" / "app").rglob("*.py")):
        relative = path.relative_to(ROOT).with_suffix(".pyc")
        cfile = cache_root / relative
        cfile.parent.mkdir(parents=True, exist_ok=True)
        py_compile.compile(str(path), cfile=str(cfile), doraise=True)

frontend_check = subprocess.run(["node", "--check", "frontend/app.js"], cwd=ROOT)
if frontend_check.returncode != 0:
    raise SystemExit(frontend_check.returncode)

smoke = subprocess.run([sys.executable, "scripts/smoke_test.py"], cwd=ROOT)
if smoke.returncode != 0:
    raise SystemExit(smoke.returncode)
