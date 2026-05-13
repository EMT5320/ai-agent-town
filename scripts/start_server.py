"""启动 Python 后端开发服务器。"""

from pathlib import Path
import os
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.main import run_server  # noqa: E402

run_server(int(os.getenv("PORT", "8787")))
