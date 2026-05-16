from __future__ import annotations

import json
from typing import Any

from app.memory.memory_store import memory_summary
from app.providers.provider_support import FEATURE_DIALOGUE, FEATURE_EVENT_REACTION, FEATURE_NIGHT_REFLECTION
from app.world.world_state import get_relation, living_agents


_PHASE_TO_MONOLOGUE_TAGS: dict[str, tuple[str, ...]] = {
    "morning": ("morning",),
    "noon": ("afternoon",),
    "afternoon": ("afternoon",),
    "evening": ("evening",),
    "night": ("evening",),
}


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
    deep_card = npc.get("deepCard") if isinstance(npc.get("deepCard"), dict) else None
    deep_identity = (deep_card or {}).get("identity") or {}
    deep_personality = (deep_card or {}).get("personality") or {}
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
            "voiceStyle": deep_identity.get("voiceStyle", ""),
            "archetype": deep_identity.get("archetype", ""),
            "speechQuirks": list(deep_personality.get("speechQuirks", [])),
            "innerContradiction": deep_personality.get("innerContradiction", ""),
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
            "memory_evidence_used": "可选；如果引用了 memoryEvidence，请返回被引用的来源、文本摘要和标签",
        },
    }


def build_player_dialogue_messages(context: dict[str, Any]) -> list[dict[str, str]]:
    """玩家对话专用 Prompt，要求模型优先返回可解析 JSON。"""
    system_prompt = build_structured_system_prompt(
        feature=FEATURE_DIALOGUE,
        required_fields=("speech", "memory_to_save"),
        extra_rules=[
            "speech 需像 NPC 当下直接说的话，长度控制在 1-3 句。",
            "memory_to_save 需是 NPC 第一人称主观记忆，长度控制在 1 句。",
            "如果使用了 memoryEvidence，请额外返回 memory_evidence_used，便于客户端展示 NPC 记忆影响。",
        ],
    )
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": json.dumps(context, ensure_ascii=False, indent=2)}]


def build_event_reaction_context(
    world: dict[str, Any],
    event: dict[str, Any],
    outcome: dict[str, Any],
    choice: str,
    event_store: Any,
) -> dict[str, Any]:
    """构建事件结算后 NPC 即时反应所需上下文。"""
    participant_ids = [agent_id for agent_id in event.get("participants", []) if agent_id in world["agents"]]
    return {
        "feature": FEATURE_EVENT_REACTION,
        "event": {
            "id": event.get("id"),
            "title": event.get("title"),
            "summary": event.get("summary"),
            "choice": choice,
            "choiceLabel": outcome.get("choiceLabel"),
            "outcomeSummary": outcome.get("summary"),
        },
        "player": {"id": world["player"]["id"], "name": world["player"]["name"], "questFlags": world["player"].get("questFlags", {})},
        "participants": [_agent_brief(world["agents"][agent_id]) for agent_id in participant_ids],
        "relationsWithPlayer": {agent_id: get_relation(world, "player", agent_id) for agent_id in participant_ids},
        "clock": world["clock"],
        "recentEvents": event_store.list()[-10:],
        "expectedOutput": {
            "dialogue": [{"agentId": "参与事件的 NPC id", "speech": "NPC 对玩家或现场说的话"}],
        },
    }


def build_event_reaction_messages(context: dict[str, Any]) -> list[dict[str, str]]:
    """事件反应 Prompt，要求输出可解析的多 NPC 台词 JSON。"""
    system_prompt = build_structured_system_prompt(
        feature=FEATURE_EVENT_REACTION,
        required_fields=("dialogue",),
        extra_rules=[
            "dialogue 必须是数组，长度 1-3。",
            "数组项必须包含 agentId 和 speech。",
            "speech 保持短句风格，贴合角色语气。",
        ],
    )
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": json.dumps(context, ensure_ascii=False, indent=2)}]


def build_night_reflection_context(
    world: dict[str, Any],
    event: dict[str, Any],
    outcome: dict[str, Any],
    choice: str,
    event_store: Any,
) -> dict[str, Any]:
    """构建夜间反思所需上下文，用于写入长期记忆。"""
    target_ids = [agent_id for agent_id in event.get("participants", []) if agent_id in world["agents"]][:4]
    phase = str(world.get("clock", {}).get("phase", ""))
    event_location_id = str(event.get("locationId") or "")
    agent_briefs = [
        _agent_brief(
            world["agents"][agent_id],
            night_reflection_hints={"phase": phase, "eventLocationId": event_location_id},
        )
        for agent_id in target_ids
    ]
    monologue_evidence = [
        {
            "agentId": brief.get("id"),
            "agentName": brief.get("name"),
            "seeds": brief.get("nightReflectionMonologueSeeds", []),
        }
        for brief in agent_briefs
        if brief.get("nightReflectionMonologueSeeds")
    ]
    return {
        "feature": FEATURE_NIGHT_REFLECTION,
        "event": {
            "id": event.get("id"),
            "title": event.get("title"),
            "choice": choice,
            "choiceLabel": outcome.get("choiceLabel"),
            "outcomeSummary": outcome.get("summary"),
        },
        "agents": agent_briefs,
        "monologueEvidence": monologue_evidence,
        "relationsWithPlayer": {agent_id: get_relation(world, "player", agent_id) for agent_id in target_ids},
        "clock": world["clock"],
        "recentEvents": event_store.list()[-10:],
        "expectedOutput": {
            "reflections": [{"agentId": "需要写入反思的 NPC id", "text": "一段第一人称夜间反思"}],
            "monologue_used": "可选；如果引用了 monologueEvidence，请返回被引用的独白种子 id",
        },
    }


def build_night_reflection_messages(context: dict[str, Any]) -> list[dict[str, str]]:
    """夜间反思 Prompt，要求输出适合记忆系统保存的 JSON。"""
    system_prompt = build_structured_system_prompt(
        feature=FEATURE_NIGHT_REFLECTION,
        required_fields=("reflections",),
        extra_rules=[
            "reflections 必须是数组，长度 2-4。",
            "数组项必须包含 agentId 和 text。",
            "text 需为第一人称主观反思，控制在 1-3 句。",
            "优先参考 monologueEvidence 或 agents[].nightReflectionMonologueSeeds，让反思贴合角色内在独白。",
        ],
    )
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": json.dumps(context, ensure_ascii=False, indent=2)}]


def build_structured_system_prompt(
    *,
    feature: str,
    required_fields: tuple[str, ...],
    extra_rules: list[str] | None = None,
) -> str:
    """统一生成结构化输出系统提示词，降低多功能 Prompt 维护成本。"""
    field_list = "、".join(required_fields)
    rules = extra_rules or []
    rules_text = "\n".join(f"- {item}" for item in rules)
    base = [
        "你是生活模拟 RPG《Agent Valley》中的居民智能体。",
        f"当前功能：{feature}。",
        f"请仅输出 JSON 对象，必须包含字段：{field_list}。",
        "禁止输出 Markdown 代码块、解释文本和多余键名。",
    ]
    if rules_text:
        base.append("补充规则：")
        base.append(rules_text)
    return "\n".join(base)


def _agent_brief(agent: dict[str, Any], *, night_reflection_hints: dict[str, Any] | None = None) -> dict[str, Any]:
    """提取 Prompt 所需的 NPC 摘要，避免把完整运行态塞进 messages。"""
    brief: dict[str, Any] = {
        "id": agent["id"],
        "name": agent["name"],
        "job": agent["job"],
        "personality": agent.get("personality", []),
        "status": agent.get("status", {}),
        "goals": agent.get("todayGoals", []),
        "memory": memory_summary(agent),
    }
    deep_card = agent.get("deepCard")
    if isinstance(deep_card, dict):
        identity = deep_card.get("identity") or {}
        personality = deep_card.get("personality") or {}
        brief["voiceStyle"] = identity.get("voiceStyle", "")
        brief["archetype"] = identity.get("archetype", "")
        brief["speechQuirks"] = list(personality.get("speechQuirks", []))
        brief["innerContradiction"] = personality.get("innerContradiction", "")
        if night_reflection_hints is not None:
            brief["nightReflectionMonologueSeeds"] = _select_night_reflection_monologues(
                agent,
                phase=str(night_reflection_hints.get("phase", "")),
                event_location_id=str(night_reflection_hints.get("eventLocationId", "")),
            )
    return brief


def _select_night_reflection_monologues(
    agent: dict[str, Any],
    *,
    phase: str,
    event_location_id: str,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """按时段、地点和情绪筛出夜间反思可用的独白种子。"""
    deep_card = agent.get("deepCard") if isinstance(agent.get("deepCard"), dict) else {}
    seeds = deep_card.get("monologueSeeds") if isinstance(deep_card.get("monologueSeeds"), list) else []
    if not seeds:
        return []

    location_id = str(agent.get("locationId") or event_location_id or "")
    mood = str(agent.get("status", {}).get("mood", "")).lower()
    mood_tag = "high_mood" if mood in {"happy", "excited", "calm"} else "low_mood"
    phase_tags = set(_PHASE_TO_MONOLOGUE_TAGS.get(phase, (phase,)))
    scored: list[tuple[int, dict[str, Any]]] = []
    for item in seeds:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        tags = {str(tag) for tag in item.get("contextTags", [])}
        score = 0
        if "post_event" in tags:
            score += 3
        if phase_tags.intersection(tags):
            score += 2
        if location_id and location_id in tags:
            score += 2
        if mood_tag in tags:
            score += 1
        if "any" in tags:
            score += 1
        scored.append(
            (
                score,
                {
                    "id": str(item.get("id", "")),
                    "contextTags": sorted(tags),
                    "text": text,
                },
            )
        )

    if not scored:
        return []

    scored.sort(key=lambda item: (item[0], item[1].get("id", "")), reverse=True)
    picked = [item for score, item in scored if score > 0][:limit]
    if picked:
        return picked
    return [item for _, item in scored[:limit]]
