from __future__ import annotations

from typing import Any

from app.memory.memory_store import remember
from app.world.world_state import clamp


def apply_developer_command(runtime: Any, command: dict[str, Any]) -> dict[str, Any]:
    """执行开发者通道命令。"""
    world = runtime.world
    event_store = runtime.event_store
    command_type = command.get("type")
    if command_type == "pause":
        world["clock"]["paused"] = True
    elif command_type == "resume":
        world["clock"]["paused"] = False
    elif command_type == "focus":
        world["activeFocus"] = command.get("agentId")
    elif command_type == "injectEvent":
        event_store.append(command.get("eventType") or "developer.injected", {"message": command.get("message") or "开发者注入了一个实验事件。", "payload": command.get("payload") or {}}, {"actor": "developer"})
    elif command_type == "adjustAgent" and command.get("agentId") in world["agents"]:
        agent = world["agents"][command["agentId"]]
        for key, value in (command.get("status") or {}).items():
            agent["status"][key] = clamp(int(value), 0, 999)
        remember(agent, command.get("memory") or "开发者调整了我的实验状态。", tick=world["clock"]["tick"], importance=0.75, tags=["developer"])
        event_store.append("developer.adjust_agent", {"agentId": agent["id"], "status": agent["status"]})
    return runtime.get_public_state()
