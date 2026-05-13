from __future__ import annotations

import json
from typing import Any


class RuleBasedProvider:
    """离线可运行的规则 Provider，用于低成本验证 Agent 闭环。"""

    name = "RuleBasedProvider"

    def decide(self, context: dict[str, Any], _messages: list[dict[str, str]]) -> dict[str, Any]:
        agent = context["agent"]
        nearby = context["nearby"]
        clock = context["clock"]
        if agent["status"]["energy"] < 35:
            response = {"speech": f"{agent['name']}觉得有点累，决定先恢复精力。", "action": "rest", "args": {}, "memory_to_save": "我今天意识到需要保留体力。"}
        elif nearby and agent["status"]["social"] < 72:
            target = nearby[(clock["tick"] + len(agent["id"])) % len(nearby)]
            response = {"speech": f"{target['name']}，今天小镇的气氛有些不同，我们聊聊近况吧。", "action": "talkTo", "args": {"npc": target["id"], "topic": "daily_check", "message": "今天感觉怎么样？如果需要帮助可以告诉我。"}, "memory_to_save": f"我主动和 {target['name']} 交流了今日近况。"}
        elif "医生" in agent["job"]:
            response = {"speech": "我需要巡查看看老人和孩子的健康状况。", "action": "careFor", "args": {"npc": "orren"}, "memory_to_save": "我把公共健康放在今天的优先级。"}
        elif any(keyword in agent["job"] for keyword in ["店主", "木匠", "农夫"]):
            response = {"speech": "先把工作处理好，小镇稳定需要每个人尽责。", "action": "work", "args": {"job": agent["job"]}, "memory_to_save": "我完成了一段职业工作。"}
        else:
            destinations = ["plaza", "shop", "clinic", "tavern", "home-north"]
            response = {"speech": "我想换个地方观察大家今天的状态。", "action": "moveTo", "args": {"location": destinations[(clock["tick"] + len(agent["name"])) % len(destinations)]}, "memory_to_save": "我根据小镇气氛调整了当前位置。"}
        return {"provider": self.name, "rawText": json.dumps(response, ensure_ascii=False), "parsed": response, "usage": {"tokens": 0, "cost": 0, "latencyMs": 1}}
