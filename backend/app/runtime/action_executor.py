from __future__ import annotations

from typing import Any

from app.memory.memory_store import remember
from app.world.world_state import adjust_relation, clamp, living_agents


def execute_action(world: dict[str, Any], agent: dict[str, Any], action: dict[str, Any], event_store: Any) -> dict[str, Any]:
    """执行 Agent 行动，并把结果写入事件流。"""
    action_type = action.get("action", "remember")
    args = action.get("args") or {}
    speech = action.get("speech", "")
    summary = ""

    if action_type == "moveTo" and args.get("location") in world["locations"]:
        source = agent["locationId"]
        agent["locationId"] = args["location"]
        agent["status"]["energy"] = clamp(agent["status"]["energy"] - 4)
        summary = f"{agent['name']} 从 {world['locations'][source]['name']} 移动到 {world['locations'][agent['locationId']]['name']}"
    elif action_type == "talkTo" and args.get("npc") in world["agents"]:
        target = world["agents"][args["npc"]]
        agent["status"]["social"] = clamp(agent["status"]["social"] + 9)
        target["status"]["social"] = clamp(target["status"]["social"] + 5)
        adjust_relation(world, agent["id"], target["id"], {"affection": 2, "trust": 1, "conflict": -1})
        summary = f"{agent['name']} 对 {target['name']} 说：“{args.get('message') or speech}”"
    elif action_type == "work":
        agent["status"]["money"] = clamp(agent["status"]["money"] + 7, 0, 999)
        agent["status"]["energy"] = clamp(agent["status"]["energy"] - 11)
        world["townStats"]["economy"] = clamp(world["townStats"]["economy"] + 1)
        summary = f"{agent['name']} 完成了 {args.get('job') or agent['job']} 的工作"
    elif action_type == "buy":
        agent["status"]["money"] = clamp(agent["status"]["money"] - 4, 0, 999)
        agent["status"]["mood"] = clamp(agent["status"]["mood"] + 3)
        world["townStats"]["economy"] = clamp(world["townStats"]["economy"] + 1)
        summary = f"{agent['name']} 购买了 {args.get('item', '生活用品')}"
    elif action_type == "rest":
        agent["status"]["energy"] = clamp(agent["status"]["energy"] + 18)
        agent["status"]["stress"] = clamp(agent["status"]["stress"] - 8)
        summary = f"{agent['name']} 休息并恢复精力"
    elif action_type == "careFor" and args.get("npc") in world["agents"]:
        target = world["agents"][args["npc"]]
        target["status"]["health"] = clamp(target["status"]["health"] + 5)
        target["status"]["mood"] = clamp(target["status"]["mood"] + 4)
        agent["status"]["energy"] = clamp(agent["status"]["energy"] - 6)
        adjust_relation(world, agent["id"], target["id"], {"affection": 3, "trust": 3})
        summary = f"{agent['name']} 照顾了 {target['name']}"
    elif action_type == "attendEvent":
        agent["status"]["mood"] = clamp(agent["status"]["mood"] + 2)
        world["townStats"]["harmony"] = clamp(world["townStats"]["harmony"] + 1)
        summary = f"{agent['name']} 参加了 {args.get('event', '小镇公共事件')}"
    else:
        summary = f"{agent['name']} 记录了一次想法"

    if action.get("memory_to_save"):
        remember(agent, action["memory_to_save"], tick=world["clock"]["tick"], importance=0.55, tags=[action_type])
    if speech:
        event_store.append("dialogue", {"agentId": agent["id"], "agentName": agent["name"], "speech": speech, "action": action_type})
    return event_store.append("action.executed", {"agentId": agent["id"], "agentName": agent["name"], "type": action_type, "args": args, "summary": summary})


def maybe_population_event(world: dict[str, Any], event_store: Any) -> None:
    """首版人口事件触发器，后续会扩展成独立规则引擎。"""
    tick = world["clock"]["tick"]
    if tick > 0 and tick % 9 == 0:
        elder = next((agent for agent in living_agents(world) if agent["lifeStage"] == "elder" and agent["status"]["health"] < 65), None)
        if elder:
            elder["status"]["health"] = clamp(elder["status"]["health"] - 2)
            event_store.append("population.health_risk", {"agentId": elder["id"], "agentName": elder["name"], "message": f"{elder['name']} 的健康状况需要关注。"})
    if tick > 0 and tick % 14 == 0:
        world["population"]["growthEvents"] += 1
        world["townStats"]["curiosity"] = clamp(world["townStats"]["curiosity"] + 2)
        event_store.append("population.growth", {"message": "孩子们在新的一天学会了新的表达方式，社区开始讨论教育计划。"})
