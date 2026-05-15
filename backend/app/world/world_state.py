from __future__ import annotations

from copy import deepcopy
from typing import Any

from .seed_data import AGENTS, DAY1_EVENTS, DAY1_LOCATION_IDS, DAY1_NPC_IDS, INITIAL_RELATIONS, LOCATIONS


def clamp(value: int | float, min_value: int = 0, max_value: int = 100) -> int:
    """限制状态数值范围，避免行动执行后出现非法状态。"""
    return int(max(min_value, min(max_value, value)))


def relation_key(a: str, b: str) -> str:
    """关系图使用无向 key，方便任意方向读取。"""
    return "::".join(sorted([a, b]))


def create_initial_world() -> dict[str, Any]:
    """创建首版小镇世界状态。"""
    agents = {agent["id"]: create_agent(agent) for agent in AGENTS}
    relations: dict[str, dict[str, Any]] = {}
    for a, b, affection, trust, conflict, kind in INITIAL_RELATIONS:
        relations[relation_key(a, b)] = {"affection": affection, "trust": trust, "conflict": conflict, "kind": kind}
    return {
        "clock": {"day": 1, "hour": 8, "tick": 0, "phase": "morning", "paused": False},
        "player": create_player(),
        "locations": {location["id"]: deepcopy(location) for location in LOCATIONS},
        "agents": agents,
        "relations": relations,
        "population": {"births": 0, "deaths": 0, "migrationsIn": 1, "migrationsOut": 0, "growthEvents": 0},
        "townStats": {"funds": 500, "harmony": 63, "economy": 58, "health": 72, "curiosity": 80},
        "activeEvents": deepcopy(DAY1_EVENTS),
        "completedEvents": [],
        "nightReflections": [],
        "activeFocus": None,
    }


def create_player() -> dict[str, Any]:
    """创建首版玩家状态，后续存档系统会直接围绕这些字段扩展。"""
    return {
        "id": "player",
        "name": "新来的农场主",
        "locationId": "farm",
        "inventory": [
            {"id": "fresh_turnip", "name": "新鲜芜菁", "quantity": 1, "tags": ["crop", "gift"]},
            {"id": "farm_flower", "name": "农场小花", "quantity": 1, "tags": ["flower", "gift"]},
        ],
        "knownNpcs": [],
        "questFlags": {"day1_intro": "started"},
        "actionHistory": [],
        "memories": [{"tick": 0, "importance": 0.6, "tags": ["arrival"], "text": "我搬进了晨露农场，准备认识这座小镇。"}],
    }


def create_agent(seed: dict[str, Any]) -> dict[str, Any]:
    """把种子数据扩展为运行期 Agent 状态。"""
    status = {
        "energy": 56 if seed["lifeStage"] == "elder" else 78,
        "mood": 82 if seed["lifeStage"] == "child" else 64,
        "stress": 38 if "轻微焦虑" in seed.get("personality", []) else 22,
        "social": 50,
        "money": seed["money"],
        "health": seed["health"],
    }
    agent = deepcopy(seed)
    agent.update(
        {
            "status": status,
            "currentIntent": "观察小镇今日变化",
            "todayGoals": seed["longTermGoals"][:2],
            "memories": [{"tick": 0, "importance": 0.6, "text": f"{seed['name']} 开始了小镇实验的第一天。"}],
            "decisionHistory": [],
            "alive": True,
        }
    )
    return agent


def living_agents(world: dict[str, Any]) -> list[dict[str, Any]]:
    """返回仍在小镇活动的居民。"""
    return [agent for agent in world["agents"].values() if agent.get("alive", True)]


def get_relation(world: dict[str, Any], a: str, b: str) -> dict[str, Any]:
    """读取两个 Agent 的关系，缺省为普通熟人。"""
    return world["relations"].get(relation_key(a, b), {"affection": 45, "trust": 45, "conflict": 0, "kind": "acquaintance"})


def adjust_relation(world: dict[str, Any], a: str, b: str, delta: dict[str, int | str]) -> None:
    """按行动结果调整关系。"""
    current = get_relation(world, a, b)
    world["relations"][relation_key(a, b)] = {
        "affection": clamp(current["affection"] + int(delta.get("affection", 0))),
        "trust": clamp(current["trust"] + int(delta.get("trust", 0))),
        "conflict": clamp(current["conflict"] + int(delta.get("conflict", 0))),
        "kind": str(delta.get("kind", current["kind"])),
    }


def advance_clock(world: dict[str, Any]) -> None:
    """推进世界时钟，每天从 08:00 到 21:00。"""
    clock = world["clock"]
    clock["tick"] += 1
    clock["hour"] += 1
    if clock["hour"] >= 22:
        clock["day"] += 1
        clock["hour"] = 8
    clock["phase"] = "morning" if clock["hour"] < 12 else "afternoon" if clock["hour"] < 18 else "evening"


def public_world(world: dict[str, Any]) -> dict[str, Any]:
    """输出前端需要的公开状态，裁剪长历史。"""
    view = deepcopy(world)
    view["locations"] = list(view["locations"].values())
    view["agents"] = list(view["agents"].values())
    view["player"]["actionHistory"] = view["player"].get("actionHistory", [])[-10:]
    view["player"]["memories"] = view["player"].get("memories", [])[-10:]
    for agent in view["agents"]:
        agent["memories"] = agent.get("memories", [])[-5:]
        agent["decisionHistory"] = agent.get("decisionHistory", [])[-3:]
    return view


def public_game_world(world: dict[str, Any], recent_events: list[dict[str, Any]]) -> dict[str, Any]:
    """输出 Godot 游戏客户端使用的状态契约，保留后续扩展字段。"""
    view = public_world(world)
    location_ids = set(DAY1_LOCATION_IDS)
    npc_ids = set(DAY1_NPC_IDS)
    return {
        "clock": view["clock"],
        "player": view["player"],
        "locations": [location for location in view["locations"] if location["id"] in location_ids],
        "npcs": [agent for agent in view["agents"] if agent["id"] in npc_ids],
        "activeEvents": view.get("activeEvents", []),
        "completedEvents": view.get("completedEvents", []),
        "nightReflections": view.get("nightReflections", [])[-10:],
        "recentEvents": recent_events[-20:],
        "slice": {"npcIds": DAY1_NPC_IDS, "locationIds": DAY1_LOCATION_IDS},
        "townStats": view["townStats"],
    }
