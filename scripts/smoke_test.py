"""Python 后端 smoke test。"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.director import DirectorBeat, WorldDigest  # noqa: E402
from app.main import create_town_app  # noqa: E402
from app.skills import STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID  # noqa: E402

app = create_town_app(provider_mode="rule")
initial = app.get_public_state()
if len(initial["agents"]) != 10:
    raise RuntimeError(f"期望 10 个初始 Agent，实际得到 {len(initial['agents'])}")

game_state = app.get_game_state()
if game_state["player"]["locationId"] != "farm":
    raise RuntimeError("玩家初始位置应为 farm")
if len(game_state["npcs"]) != 6:
    raise RuntimeError(f"游戏状态应只暴露首发 6 个 NPC，实际得到 {len(game_state['npcs'])}")
if {location["id"] for location in game_state["locations"]} != {"farm", "plaza", "tavern"}:
    raise RuntimeError("游戏状态应只暴露首版 3 个地点")
if not any(location["id"] == "farm" for location in game_state["locations"]):
    raise RuntimeError("游戏状态缺少玩家农场地点")
if not any(event["id"] == "starlight_festival_shortage" for event in game_state["activeEvents"]):
    raise RuntimeError("游戏状态缺少星灯祭供应短缺事件")

director_app = create_town_app(provider_mode="rule")
director_step = director_app.step_simulation({"actorId": "director-smoke"})
director_events = director_step["state"]["events"]
for event_type in (
    "director.digest_created",
    "director.beat_created",
    "director.beat_validated",
    "director.beat_consumed",
):
    if not any(event["type"] == event_type for event in director_events):
        raise RuntimeError(f"Director v0 应写入 {event_type}")
consumed = next(event for event in director_events if event["type"] == "director.beat_consumed")
if consumed["payload"]["beat"]["beatType"] != "activate_event_skill":
    raise RuntimeError("Director Beat 类型应为 activate_event_skill")
if consumed["payload"]["beat"]["payload"]["skillId"] != STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID:
    raise RuntimeError("Director Beat 应激活星灯祭供应短缺 Event Skill")

current_digest = WorldDigest.from_world(director_app.runtime.world)
expired_beat = DirectorBeat(
    worldVersion=current_digest.world_version,
    validFromTick=0,
    expiresAtTick=0,
    targetAgents=["kai"],
    allowedSkills=[STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID],
)
director_app.runtime.director_queue.enqueue(expired_beat)
director_app.runtime._consume_director_queue(current_digest)
if not any(event["type"] == "director.beat_discarded" and event["payload"].get("reason") == "expired" for event in director_app.get_public_state()["events"]):
    raise RuntimeError("Director 队列应丢弃过期 Beat")

mismatch_beat = DirectorBeat(
    worldVersion=current_digest.world_version + 1,
    validFromTick=current_digest.tick,
    expiresAtTick=current_digest.tick + 2,
    targetAgents=["kai"],
    allowedSkills=[STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID],
)
director_app.runtime.director_queue.enqueue(mismatch_beat)
director_app.runtime._consume_director_queue(current_digest)
if not any(event["type"] == "director.beat_discarded" and event["payload"].get("reason") == "world_version_mismatch" for event in director_app.get_public_state()["events"]):
    raise RuntimeError("Director 队列应丢弃世界版本不匹配 Beat")

talk = app.player_action({"type": "talk", "targetId": "orren", "locationId": "plaza", "topic": "first_meeting", "message": "你好，我刚搬到晨露农场。"})
if not talk["ok"]:
    raise RuntimeError("玩家对话动作应执行成功")
if "orren" not in talk["state"]["player"]["knownNpcs"]:
    raise RuntimeError("玩家对话后应记录已认识 NPC")
if not talk["result"]["dialogue"]:
    raise RuntimeError("玩家对话后应返回 NPC 回复")
if not any(event["type"] == "debug.turn_recorded" for event in talk["state"]["recentEvents"]):
    raise RuntimeError("玩家对话后应写入 Debug 决策记录")

inspect = app.player_action({"type": "inspect", "eventId": "starlight_festival_shortage"})
if not inspect["ok"]:
    raise RuntimeError("事件查看动作应执行成功")
if not inspect["result"]["inspect"]["choices"]:
    raise RuntimeError("事件查看应返回可选项")

event_result = app.player_action({"type": "attend_event", "eventId": "starlight_festival_shortage", "choice": "donate_crop"})
if not event_result["ok"]:
    raise RuntimeError("星灯祭事件参与动作应执行成功")
if event_result["result"]["eventResult"]["choice"] != "donate_crop":
    raise RuntimeError("星灯祭事件结算选项异常")
if not event_result["state"]["nightReflections"]:
    raise RuntimeError("星灯祭事件后应生成夜间反思摘要")
if not any(event["type"] == "town.event_resolved" for event in event_result["state"]["recentEvents"]):
    raise RuntimeError("星灯祭事件后应写入事件结算记录")

step = app.step_simulation({"actorId": "smoke-test"})
state = step["state"]
if state["clock"]["tick"] != 1:
    raise RuntimeError(f"期望 tick=1，实际得到 {state['clock']['tick']}")
if len(state["events"]) < 3:
    raise RuntimeError("推进一轮后事件数量异常")

print("[python-smoke] ok", {"agents": len(state["agents"]), "events": len(state["events"]), "tick": state["clock"]["tick"]})
