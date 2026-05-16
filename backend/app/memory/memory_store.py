from __future__ import annotations

from typing import Any


def remember(agent: dict[str, Any], text: str, tick: int = 0, importance: float = 0.5, tags: list[str] | None = None) -> None:
    """写入 Agent 记忆，并限制首版内存长度。"""
    agent.setdefault("memories", []).append({"tick": tick, "importance": importance, "tags": tags or [], "text": text})
    if len(agent["memories"]) > 30:
        agent["memories"].pop(0)


def memory_summary(agent: dict[str, Any]) -> str:
    """把最近记忆压缩成 Provider 上下文。"""
    return "\n".join(f"D{item.get('tick', 0)}: {item.get('text', '')}" for item in agent.get("memories", [])[-6:])


def memory_summary_payload(agent_id: str, agent: dict[str, Any], limit: int = 6) -> dict[str, Any]:
    """输出 Debug Console 可直接展示的单个 Agent 记忆摘要。"""
    memories = list(agent.get("memories", []))[-limit:]
    return {
        "agentId": agent_id,
        "agentName": agent.get("name", agent_id),
        "memoryCount": len(agent.get("memories", [])),
        "summary": "\n".join(f"D{item.get('tick', 0)}: {item.get('text', '')}" for item in memories),
        "recent": [_memory_payload(agent_id, agent, item) for item in memories],
    }


def world_memory_summaries(world: dict[str, Any], agent_id: str | None = None, limit: int = 6) -> dict[str, Any]:
    """按 Agent 输出轻量 Memory Summary，供 API 和 Debug 查询复用。"""
    summaries = [
        memory_summary_payload(owner_id, owner, limit=limit)
        for owner_id, owner in _iter_memory_owners(world)
        if agent_id is None or owner_id == agent_id
    ]
    return {"agentId": agent_id, "limit": limit, "items": summaries}


def rag_lite_search(
    world: dict[str, Any],
    query: str = "",
    agent_id: str | None = None,
    tags: list[str] | str | None = None,
    limit: int = 8,
) -> dict[str, Any]:
    """用标签、关键词和重要度做首版 RAG-lite 检索。"""
    normalized_tags = _normalize_tags(tags)
    terms = _query_terms(query)
    results: list[dict[str, Any]] = []

    for owner_id, owner in _iter_memory_owners(world):
        if agent_id and owner_id != agent_id:
            continue
        for memory in owner.get("memories", []):
            memory_tags = [str(tag) for tag in memory.get("tags", [])]
            if normalized_tags and not all(tag in memory_tags for tag in normalized_tags):
                continue

            matched_terms = _matched_terms(memory, terms)
            if terms and not matched_terms:
                continue

            matched_tags = [tag for tag in normalized_tags if tag in memory_tags]
            score = _memory_score(memory, matched_terms, matched_tags)
            item = _memory_payload(owner_id, owner, memory)
            item["match"] = {"score": score, "terms": matched_terms, "tags": matched_tags}
            results.append(item)

    results.sort(key=lambda item: (item["match"]["score"], item.get("tick", 0)), reverse=True)
    return {"query": query, "agentId": agent_id, "tags": normalized_tags, "limit": limit, "items": results[:limit]}


def _iter_memory_owners(world: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """收集玩家和 NPC 的记忆宿主，保持 Debug 输出顺序稳定。"""
    owners: list[tuple[str, dict[str, Any]]] = []
    player = world.get("player")
    if isinstance(player, dict):
        owners.append((str(player.get("id", "player")), player))
    agents = world.get("agents", {})
    if isinstance(agents, dict):
        owners.extend((str(agent_id), agent) for agent_id, agent in agents.items() if isinstance(agent, dict))
    return owners


def _memory_payload(agent_id: str, agent: dict[str, Any], memory: dict[str, Any]) -> dict[str, Any]:
    """把内部记忆条目转成 API 安全结构。"""
    return {
        "agentId": agent_id,
        "agentName": agent.get("name", agent_id),
        "tick": int(memory.get("tick", 0)),
        "importance": float(memory.get("importance", 0.0)),
        "tags": [str(tag) for tag in memory.get("tags", [])],
        "text": str(memory.get("text", "")),
    }


def _normalize_tags(tags: list[str] | str | None) -> list[str]:
    """兼容逗号字符串和数组标签参数。"""
    if tags is None:
        return []
    if isinstance(tags, str):
        raw_tags = tags.split(",")
    else:
        raw_tags = tags
    return [str(tag).strip() for tag in raw_tags if str(tag).strip()]


def _query_terms(query: str) -> list[str]:
    """把查询拆成小写词；中文无空格时保留整句作为关键词。"""
    normalized = str(query or "").strip().lower()
    if not normalized:
        return []
    return [term for term in normalized.split() if term] or [normalized]


def _matched_terms(memory: dict[str, Any], terms: list[str]) -> list[str]:
    """计算某条记忆命中的查询词。"""
    text = str(memory.get("text", "")).lower()
    tags = " ".join(str(tag).lower() for tag in memory.get("tags", []))
    return [term for term in terms if term in text or term in tags]


def _memory_score(memory: dict[str, Any], matched_terms: list[str], matched_tags: list[str]) -> float:
    """给 RAG-lite 结果打一个可解释分数。"""
    importance = float(memory.get("importance", 0.0))
    tick = int(memory.get("tick", 0))
    return importance * 10 + len(matched_terms) * 5 + len(matched_tags) * 3 + tick * 0.01
