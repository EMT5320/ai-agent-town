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
