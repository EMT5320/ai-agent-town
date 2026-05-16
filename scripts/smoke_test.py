"""Python 后端 smoke test。"""

from pathlib import Path
from http.server import ThreadingHTTPServer
import json
import os
import sys
import tempfile
from threading import Thread
from urllib.parse import urlencode
from urllib.request import urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.director import DirectorBeat, WorldDigest  # noqa: E402
from app.main import create_handler, create_town_app  # noqa: E402
from app.skills import STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID  # noqa: E402

REQUIRED_DEBUG_FIELDS = {
    "providerMode",
    "profileName",
    "apiKeyConfigured",
    "messages",
    "rawText",
    "parsed",
    "usage",
    "latency",
    "fallbackReason",
}


def assert_feature_debug(state: dict, feature: str) -> dict:
    """确认指定 feature 生成了本轮 LLM 验证要求的 Debug 字段。"""
    debug_events = [
        event
        for event in state["recentEvents"]
        if event["type"] == "debug.turn_recorded" and event["payload"].get("debug", {}).get("feature") == feature
    ]
    if not debug_events:
        raise RuntimeError(f"{feature} 应写入 debug.turn_recorded")
    debug = debug_events[-1]["payload"]["debug"]
    missing = sorted(REQUIRED_DEBUG_FIELDS - set(debug))
    if missing:
        raise RuntimeError(f"{feature} Debug 缺少字段：{missing}")
    if not isinstance(debug["messages"], list) or not debug["messages"]:
        raise RuntimeError(f"{feature} Debug messages 应为非空数组")
    if not isinstance(debug["parsed"], dict):
        raise RuntimeError(f"{feature} Debug parsed 应为对象")
    if not isinstance(debug["usage"], dict):
        raise RuntimeError(f"{feature} Debug usage 应为对象")
    return debug


def has_real_llm_config() -> bool:
    """检测是否存在可用于真实 LLM smoke 的本地配置入口。"""
    return (PROJECT_ROOT / "config" / "models.local.json").exists() or any(
        os.getenv(name) for name in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY", "AGENT_TOWN_API_KEY")
    )


def assert_http_debug_endpoints(api_app) -> dict:
    """启动临时 HTTP 服务，确认 Debug / Memory 查询接口能走真实路由。"""
    server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(api_app, PROJECT_ROOT))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def fetch(path: str, query: dict[str, str] | None = None) -> dict:
        suffix = f"?{urlencode(query)}" if query else ""
        with urlopen(f"http://127.0.0.1:{server.server_port}{path}{suffix}", timeout=5) as response:  # noqa: S310 - 本地 smoke 服务
            return json.loads(response.read().decode("utf-8"))

    try:
        debug = fetch("/api/debug", {"skillId": STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID, "limit": "20"})
        skill = fetch("/api/debug/skill", {"skillId": STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID})
        memory = fetch("/api/memory/search", {"query": "玩家", "tags": "night_reflection", "limit": "5"})
        influence = fetch("/api/debug/influence", {"skillId": STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID, "agentId": "kai", "query": "星灯祭", "limit": "30"})
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    if not debug.get("skills", {}).get("items"):
        raise RuntimeError("/api/debug 应返回 Skill 快照")
    if "attend_event" not in skill.get("actions", {}):
        raise RuntimeError("/api/debug/skill 应解释 attend_event")
    if not memory.get("items"):
        raise RuntimeError("/api/memory/search 应返回 RAG-lite 命中")
    if not influence.get("memory", {}).get("retrieval", {}).get("items"):
        raise RuntimeError("/api/debug/influence 应解释相关 RAG-lite 记忆")
    if not influence.get("relations", {}).get("events"):
        raise RuntimeError("/api/debug/influence 应解释关系变化")
    if not influence.get("skill", {}).get("actions", {}).get("attend_event"):
        raise RuntimeError("/api/debug/influence 应解释事件 Skill")
    if not influence.get("playerProfile", {}).get("styleSummary"):
        raise RuntimeError("/api/debug/influence 应返回玩家风格摘要")
    return {"debugSkills": len(debug["skills"]["items"]), "memoryHits": len(memory["items"]), "influenceEvents": len(influence["events"]["items"])}


def assert_provider_fallback_debug() -> dict:
    """用临时无密钥配置强制云端转规则兜底，并确认 Debug API 可解释。"""
    previous_env = {name: os.environ.get(name) for name in ("AGENT_TOWN_MODEL_CONFIG", "OPENAI_API_KEY", "AGENT_TOWN_NEVER_SET_API_KEY")}
    with tempfile.TemporaryDirectory(prefix="agent-town-fallback-") as tmp_dir:
        config_path = Path(tmp_dir) / "models.json"
        config_path.write_text(
            json.dumps(
                {
                    "activeProvider": "cloud",
                    "defaultProfile": "no_key_cloud",
                    "profiles": {
                        "no_key_cloud": {
                            "provider": "cloud",
                            "baseUrl": "https://example.invalid",
                            "apiKeyEnv": "AGENT_TOWN_NEVER_SET_API_KEY",
                            "model": "debug-no-key",
                            "timeoutSeconds": 1,
                        },
                        "rule_fallback": {"provider": "rule"},
                    },
                    "featureProfiles": {"dialogue": "no_key_cloud"},
                    "fallbackProfile": "rule_fallback",
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        os.environ["AGENT_TOWN_MODEL_CONFIG"] = str(config_path)
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("AGENT_TOWN_NEVER_SET_API_KEY", None)
        try:
            fallback_app = create_town_app(provider_mode="cloud")
            fallback_talk = fallback_app.player_action({"type": "talk", "targetId": "mira", "locationId": "plaza", "topic": "fallback_check", "message": "测试无密钥兜底。"})
            fallback_debug = assert_feature_debug(fallback_talk["state"], "dialogue")
            if not fallback_debug.get("fallbackReason"):
                raise RuntimeError("cloud 无密钥时 dialogue Debug 应记录 fallbackReason")
            fallback_items = fallback_app.debug_influence({"feature": "dialogue"})["providerFallbacks"]["items"]
            if not fallback_items:
                raise RuntimeError("Debug influence 应能解释模型兜底")
            return {"fallbackReason": fallback_debug["fallbackReason"], "fallbackItems": len(fallback_items)}
        finally:
            for name, value in previous_env.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value


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
starlight_event = next(event for event in game_state["activeEvents"] if event["id"] == "starlight_festival_shortage")
if starlight_event.get("skillId") != STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID:
    raise RuntimeError("游戏状态中的星灯祭事件应叠加 Event Skill 数据")
if not all(choice.get("brief") and choice.get("consequences") for choice in starlight_event.get("choices", [])):
    raise RuntimeError("游戏状态中的事件选项应由 Skill 提供 brief 和 consequences")

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
dialogue_debug = assert_feature_debug(talk["state"], "dialogue")
if not talk["result"].get("playerProfile", {}).get("styleSummary"):
    raise RuntimeError("玩家对话后应更新 Player Profile")

gift = app.player_action({"type": "give_gift", "targetId": "kai", "locationId": "tavern", "itemId": "farm_flower"})
if not gift["ok"]:
    raise RuntimeError("玩家送礼动作应执行成功")
if not gift["result"]["relationshipDeltas"]:
    raise RuntimeError("送礼后应产生关系变化")
if not any("player_gift" in item.get("tags", []) for item in gift["result"]["memoryWrites"]):
    raise RuntimeError("送礼后应写入 NPC 礼物记忆")
if "礼物" not in gift["result"].get("playerProfile", {}).get("styleSummary", ""):
    raise RuntimeError("送礼后 Player Profile 应体现礼物风格")

inspect = app.player_action({"type": "inspect", "eventId": "starlight_festival_shortage"})
if not inspect["ok"]:
    raise RuntimeError("事件查看动作应执行成功")
if not inspect["result"]["inspect"]["choices"]:
    raise RuntimeError("事件查看应返回可选项")
if inspect["result"]["inspect"].get("skillId") != STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID:
    raise RuntimeError("事件查看结果应包含 Skill ID")
if not inspect["result"]["inspect"].get("debugFields"):
    raise RuntimeError("事件查看结果应包含 Skill Debug 字段")

event_result = app.player_action({"type": "attend_event", "eventId": "starlight_festival_shortage", "choice": "donate_crop"})
if not event_result["ok"]:
    raise RuntimeError("星灯祭事件参与动作应执行成功")
if event_result["result"]["eventResult"]["choice"] != "donate_crop":
    raise RuntimeError("星灯祭事件结算选项异常")
if event_result["result"]["eventResult"].get("skillId") != STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID:
    raise RuntimeError("星灯祭事件结算应返回 Skill ID")
if not event_result["result"]["eventResult"].get("debugFields"):
    raise RuntimeError("星灯祭事件结算应返回 Skill Debug 字段")
if not all(item.get("skillId") == STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID for item in event_result["result"]["memoryWrites"] if item.get("agentId") != "player"):
    raise RuntimeError("星灯祭记忆写入应记录来源 Skill")
if "直接帮忙" not in event_result["result"].get("playerProfile", {}).get("styleSummary", "") and "实际" not in event_result["result"].get("playerProfile", {}).get("styleSummary", ""):
    raise RuntimeError("星灯祭选择后 Player Profile 应体现选择风格")
if not event_result["state"]["nightReflections"]:
    raise RuntimeError("星灯祭事件后应生成夜间反思摘要")
if not any(event["type"] == "town.event_resolved" for event in event_result["state"]["recentEvents"]):
    raise RuntimeError("星灯祭事件后应写入事件结算记录")
event_reaction_debug = assert_feature_debug(event_result["state"], "event_reaction")
night_reflection_debug = assert_feature_debug(event_result["state"], "night_reflection")
if event_reaction_debug.get("skillId") != STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID or not event_reaction_debug.get("skillDebugFields"):
    raise RuntimeError("event_reaction Debug 应记录 Skill 字段")
if night_reflection_debug.get("skillId") != STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID or not night_reflection_debug.get("skillDebugFields"):
    raise RuntimeError("night_reflection Debug 应记录 Skill 字段")

follow_up = app.player_action({"type": "talk", "targetId": "kai", "locationId": "tavern", "topic": "starlight_follow_up", "message": "昨晚星灯祭之后，你怎么看我的选择？"})
if not follow_up["ok"]:
    raise RuntimeError("星灯祭后的第二次对话应执行成功")
follow_up_text = follow_up["result"]["dialogue"][0]["text"]
if "记得" not in follow_up_text and "星灯祭" not in follow_up_text:
    raise RuntimeError("第二次对话应引用既有记忆或星灯祭上下文")
follow_up_debug = assert_feature_debug(follow_up["state"], "dialogue")
if not follow_up_debug.get("memoryEvidenceUsed"):
    raise RuntimeError("第二次对话 Debug 应记录实际使用的记忆证据")
if follow_up_debug["memoryEvidenceUsed"].get("source") not in {"rag_lite", "memory_summary"}:
    raise RuntimeError("第二次对话应引用 Memory Summary 或 RAG-lite 命中")
if not follow_up_debug.get("memoryEvidence", {}).get("ragHits"):
    raise RuntimeError("第二次对话 Debug 应保留 RAG-lite 候选命中")

skill_debug = app.debug_skill_explain({"skillId": STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID})
for action_name in ("inspect", "attend_event", "event_reaction", "night_reflection"):
    if action_name not in skill_debug["actions"]:
        raise RuntimeError(f"Skill 解释接口应覆盖 {action_name}")
skill_lifecycle_stages = {item["stage"] for item in app.debug_skills({"skillId": STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID})["items"][0]["lifecycle"]}
for required_stage in ("registered", "inspect", "attend_event", "event_reaction_debug", "night_reflection_debug"):
    if required_stage not in skill_lifecycle_stages:
        raise RuntimeError(f"Skill 生命周期快照缺少阶段：{required_stage}")

debug_turns = app.debug_turns({"feature": "event_reaction", "skillId": STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID, "limit": "5"})
if not debug_turns["items"] or not debug_turns["items"][-1]["summary"]:
    raise RuntimeError("Debug turns 查询应能解释 event_reaction")
memory_summary = app.memory_summary({"agentId": "kai", "limit": "4"})
if not memory_summary["items"] or "星灯祭" not in memory_summary["items"][0]["summary"]:
    raise RuntimeError("Memory Summary 应包含星灯祭记忆")
memory_search = app.memory_search({"query": "玩家", "tags": "night_reflection", "limit": "5"})
if not memory_search["items"]:
    raise RuntimeError("RAG-lite 检索应能召回 night_reflection 记忆")
http_debug_summary = assert_http_debug_endpoints(app)
fallback_summary = assert_provider_fallback_debug()

step = app.step_simulation({"actorId": "smoke-test"})
state = step["state"]
if state["clock"]["tick"] != 1:
    raise RuntimeError(f"期望 tick=1，实际得到 {state['clock']['tick']}")
if len(state["events"]) < 3:
    raise RuntimeError("推进一轮后事件数量异常")

print(
    "[python-smoke] ok",
    {
        "agents": len(state["agents"]),
        "events": len(state["events"]),
        "tick": state["clock"]["tick"],
        "dialogueProfile": dialogue_debug["profileName"],
        "eventReactionProfile": event_reaction_debug["profileName"],
        "nightReflectionProfile": night_reflection_debug["profileName"],
        "followUpEvidence": follow_up_debug["memoryEvidenceUsed"]["source"],
        "debugSkills": http_debug_summary["debugSkills"],
        "memoryHits": http_debug_summary["memoryHits"],
        "influenceEvents": http_debug_summary["influenceEvents"],
        "fallbackItems": fallback_summary["fallbackItems"],
    },
)

if has_real_llm_config():
    llm_app = create_town_app()
    llm_talk = llm_app.player_action({"type": "talk", "targetId": "orren", "locationId": "plaza", "topic": "llm_smoke", "message": "能和我聊聊今晚的小镇吗？"})
    llm_debug = assert_feature_debug(llm_talk["state"], "dialogue")
    print(
        "[llm-smoke]",
        {
            "providerMode": llm_debug["providerMode"],
            "provider": llm_debug.get("provider"),
            "profileName": llm_debug["profileName"],
            "apiKeyConfigured": llm_debug["apiKeyConfigured"],
            "latency": llm_debug["latency"],
            "fallbackReason": llm_debug["fallbackReason"],
            "dialoguePreview": llm_talk["result"]["dialogue"][0]["text"][:80],
        },
    )
else:
    print("[llm-smoke] skipped: 未检测到 config/models.local.json 或 API key 环境变量；请参考 docs/model_profile_template_guide.md 配置后重跑。")
