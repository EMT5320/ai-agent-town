from __future__ import annotations

import json
from typing import Any

from app.memory.memory_store import memory_summary
from app.world.world_state import get_relation, living_agents


def build_agent_context(world: dict[str, Any], agent: dict[str, Any], event_store: Any) -> dict[str, Any]:
    """构建单个 Agent 本轮决策所需上下文。"""
    nearby = [
        {"id": other["id"], "name": other["name"], "job": other["job"], "mood": other["status"]["mood"]}
        for other in living_agents(world)
        if other["id"] != agent["id"] and other["locationId"] == agent["locationId"]
    ]
    return {
        "agent": {
            "id": agent["id"],
            "name": agent["name"],
            "genderIdentity": agent.get("genderIdentity"),
            "age": agent["age"],
            "job": agent["job"],
            "personality": agent["personality"],
            "goals": agent["todayGoals"],
            "status": agent["status"],
            "intent": agent["currentIntent"],
        },
        "clock": world["clock"],
        "location": world["locations"][agent["locationId"]],
        "nearby": nearby,
        "memory": memory_summary(agent),
        "townStats": world["townStats"],
        "recentEvents": event_store.list()[-8:],
        "actions": ["moveTo", "talkTo", "work", "buy", "rest", "careFor", "attendEvent", "remember", "planDay"],
    }


def build_prompt_messages(context: dict[str, Any]) -> list[dict[str, str]]:
    """云端 Provider 使用 OpenAI-compatible messages，同时用于完整 debug。"""
    return [
        {"role": "system", "content": "你是 AI Agent 小镇实验中的居民。请根据角色、关系、记忆和当前地点，自然地选择一个行动或说一句话。输出可为 JSON，也可为自然语言。"},
        {"role": "user", "content": json.dumps(context, ensure_ascii=False, indent=2)},
    ]


def build_player_dialogue_context(world: dict[str, Any], npc: dict[str, Any], player_action: dict[str, Any], event_store: Any) -> dict[str, Any]:
    """构建玩家主动对话时 NPC 回复所需上下文。"""
    player = world["player"]
    location_id = player_action.get("locationId") or player.get("locationId") or npc.get("locationId")
    location = world["locations"].get(location_id) or world["locations"][npc["locationId"]]
    return {
        "feature": "player_dialogue",
        "npc": {
            "id": npc["id"],
            "name": npc["name"],
            "genderIdentity": npc.get("genderIdentity"),
            "age": npc["age"],
            "job": npc["job"],
            "personality": npc["personality"],
            "goals": npc["todayGoals"],
            "status": npc["status"],
            "memory": memory_summary(npc),
        },
        "player": {
            "id": player["id"],
            "name": player["name"],
            "locationId": player["locationId"],
            "knownNpcs": player.get("knownNpcs", []),
            "questFlags": player.get("questFlags", {}),
        },
        "playerAction": {
            "type": player_action.get("type", "talk"),
            "topic": player_action.get("topic") or "free_talk",
            "message": player_action.get("message") or "你好，我刚搬到小镇。",
        },
        "clock": world["clock"],
        "location": location,
        "relationshipWithPlayer": get_relation(world, "player", npc["id"]),
        "recentEvents": event_store.list()[-8:],
        "expectedOutput": {
            "speech": "NPC 对玩家说的话",
            "memory_to_save": "NPC 应写入的一句话主观记忆",
        },
    }


def build_player_dialogue_messages(context: dict[str, Any]) -> list[dict[str, str]]:
    """玩家对话专用 Prompt，要求模型优先返回可解析 JSON。"""
    return [
        {
            "role": "system",
            "content": (
                "你是生活模拟 RPG《Agent Valley》中的小镇居民。"
                "请根据 NPC 人设、地点、关系和玩家发言生成自然回复。"
                "输出 JSON，字段为 speech 和 memory_to_save。"
            ),
        },
        {"role": "user", "content": json.dumps(context, ensure_ascii=False, indent=2)},
    ]
