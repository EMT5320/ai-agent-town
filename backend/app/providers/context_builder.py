from __future__ import annotations

import json
from typing import Any

from app.memory.memory_store import memory_summary
from app.world.world_state import living_agents


def build_agent_context(world: dict[str, Any], agent: dict[str, Any], event_store: Any) -> dict[str, Any]:
    """构建单个 Agent 本轮决策所需上下文。"""
    nearby = [
        {"id": other["id"], "name": other["name"], "job": other["job"], "mood": other["status"]["mood"]}
        for other in living_agents(world)
        if other["id"] != agent["id"] and other["locationId"] == agent["locationId"]
    ]
    return {
        "agent": {"id": agent["id"], "name": agent["name"], "age": agent["age"], "job": agent["job"], "personality": agent["personality"], "goals": agent["todayGoals"], "status": agent["status"], "intent": agent["currentIntent"]},
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
