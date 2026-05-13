"""Python 后端 smoke test。"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.main import create_town_app  # noqa: E402

app = create_town_app(provider_mode="rule")
initial = app.get_public_state()
if len(initial["agents"]) != 10:
    raise RuntimeError(f"期望 10 个初始 Agent，实际得到 {len(initial['agents'])}")

step = app.step_simulation({"actorId": "smoke-test"})
state = step["state"]
if state["clock"]["tick"] != 1:
    raise RuntimeError(f"期望 tick=1，实际得到 {state['clock']['tick']}")
if len(state["events"]) < 3:
    raise RuntimeError("推进一轮后事件数量异常")

print("[python-smoke] ok", {"agents": len(state["agents"]), "events": len(state["events"]), "tick": state["clock"]["tick"]})
