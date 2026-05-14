from __future__ import annotations

import json
import os
from typing import Any

from app.config.model_config import ModelConfigStore
from app.events.event_store import EventStore
from app.memory.memory_store import remember
from app.providers.cloud_api_provider import CloudApiProvider
from app.providers.context_builder import build_agent_context, build_player_dialogue_context, build_player_dialogue_messages, build_prompt_messages
from app.providers.rule_based_provider import RuleBasedProvider
from app.runtime.action_executor import execute_action, maybe_population_event
from app.runtime.action_parser import parse_provider_output
from app.world.world_state import advance_clock, adjust_relation, create_initial_world, get_relation, living_agents, public_game_world, public_world


class AgentRuntime:
    """后端核心运行时：时间、调度、Provider、行动、事件和 Debug 都由这里编排。"""

    def __init__(self, provider_mode: str | None = None, model_config_path: str | None = None) -> None:
        self.world = create_initial_world()
        self.event_store = EventStore()
        self.model_config = ModelConfigStore(model_config_path)
        self.rule_provider = RuleBasedProvider()
        self.cloud_provider = CloudApiProvider()
        self.provider_mode = provider_mode or os.getenv("AGENT_TOWN_PROVIDER") or self.model_config.active_provider()
        self.event_store.append("system.ready", {"message": "AI Agent 小镇 Python 运行时已启动。", "providerMode": self.provider_mode})

    def get_public_state(self) -> dict[str, Any]:
        state = public_world(self.world)
        state["events"] = self.event_store.list()
        state["snapshots"] = self.event_store.snapshots
        state["modelConfig"] = self.model_config.public_config()
        state["providerMode"] = self.provider_mode
        return state

    def get_game_state(self) -> dict[str, Any]:
        """输出游戏客户端状态，后续 Godot 只依赖这个契约。"""
        return public_game_world(self.world, self.event_store.list())

    def handle_player_action(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """处理玩家动作入口，所有结果都写入事件流和玩家行动历史。"""
        payload = payload or {}
        action_type = payload.get("type")
        if action_type == "move":
            result = self._handle_player_move(payload)
        elif action_type == "talk":
            result = self._handle_player_talk(payload)
        elif action_type == "give_gift":
            result = self._handle_player_gift(payload)
        else:
            raise ValueError(f"未知玩家动作：{action_type}")
        return {"ok": True, "result": result, "state": self.get_game_state()}

    def step(self, actor_id: str = "developer") -> dict[str, Any]:
        if self.world["clock"].get("paused"):
            return {"skipped": True, "reason": "paused", "state": self.get_public_state()}
        actors = self.pick_actors()
        decisions = []
        for agent in actors:
            context = build_agent_context(self.world, agent, self.event_store)
            messages = build_prompt_messages(context)
            profile = self.model_config.resolve_profile(agent_id=agent["id"], feature="agent_decision")
            provider_mode = self.provider_mode if self.provider_mode != "auto" else profile.get("provider", "rule")
            provider = self.cloud_provider if provider_mode == "cloud" and profile.get("provider") == "cloud" else self.rule_provider
            try:
                result = provider.decide(context, messages, profile) if provider is self.cloud_provider else provider.decide(context, messages)
            except Exception as error:
                fallback_profile = self.model_config.fallback_profile()
                result = self.rule_provider.decide(context, messages)
                self.event_store.append(
                    "provider.fallback",
                    {"agentId": agent["id"], "agentName": agent["name"], "profileName": profile.get("profileName"), "error": str(error), "fallbackProfile": fallback_profile.get("profileName")},
                )
            parsed = parse_provider_output(result)
            executed = execute_action(self.world, agent, parsed, self.event_store)
            debug = {
                "tick": self.world["clock"]["tick"],
                "provider": result["provider"],
                "profile": self._debug_profile(profile),
                "messages": messages,
                "rawText": result["rawText"],
                "parsed": parsed,
                "executed": executed["payload"],
                "usage": result.get("usage", {}),
            }
            agent.setdefault("decisionHistory", []).append(debug)
            agent["decisionHistory"] = agent["decisionHistory"][-10:]
            self.event_store.append("debug.decision", {"agentId": agent["id"], "agentName": agent["name"], "debug": debug})
            decisions.append(debug)
        maybe_population_event(self.world, self.event_store)
        advance_clock(self.world)
        self.event_store.add_snapshot(self.world)
        self.event_store.append("runtime.step", {"actorId": actor_id, "tick": self.world["clock"]["tick"], "day": self.world["clock"]["day"], "hour": self.world["clock"]["hour"], "actors": [agent["id"] for agent in actors]})
        return {"decisions": decisions, "state": self.get_public_state()}

    def pick_actors(self) -> list[dict[str, Any]]:
        agents = living_agents(self.world)
        count = min(3, len(agents))
        start = self.world["clock"]["tick"] % len(agents)
        return [agents[(start + index) % len(agents)] for index in range(count)]

    def _handle_player_move(self, payload: dict[str, Any]) -> dict[str, Any]:
        """移动玩家位置，为 Godot 地图切换保留统一事件记录。"""
        location_id = str(payload.get("locationId") or "")
        if location_id not in self.world["locations"]:
            raise ValueError(f"未知地点：{location_id}")
        player = self.world["player"]
        previous_location = player["locationId"]
        player["locationId"] = location_id
        event = self.event_store.append(
            "player.moved",
            {
                "playerId": player["id"],
                "fromLocationId": previous_location,
                "toLocationId": location_id,
                "summary": f"{player['name']} 前往 {self.world['locations'][location_id]['name']}。",
            },
        )
        self._record_player_history("move", payload, [event["id"]])
        return {"dialogue": [], "relationshipDeltas": [], "memoryWrites": [], "eventIds": [event["id"]]}

    def _handle_player_talk(self, payload: dict[str, Any]) -> dict[str, Any]:
        """处理玩家主动聊天，并让目标 NPC 生成可追踪回复。"""
        target = self._get_target_agent(payload)
        player = self.world["player"]
        self._sync_player_location(payload)
        self._mark_known_npc(target["id"])

        message = str(payload.get("message") or "你好，我刚搬到小镇。")
        topic = str(payload.get("topic") or "free_talk")
        player_event = self.event_store.append(
            "player.talked",
            {"playerId": player["id"], "targetId": target["id"], "targetName": target["name"], "topic": topic, "message": message},
        )

        before_relation = get_relation(self.world, "player", target["id"])
        adjust_relation(self.world, "player", target["id"], {"affection": 2, "trust": 1, "conflict": -1})
        after_relation = get_relation(self.world, "player", target["id"])
        relationship_payload = {
            "sourceId": "player",
            "targetId": target["id"],
            "targetName": target["name"],
            "delta": self._relation_diff(before_relation, after_relation),
            "after": after_relation,
        }
        relation_event = self.event_store.append("relationship.changed", relationship_payload)

        context = build_player_dialogue_context(self.world, target, payload, self.event_store)
        messages = build_player_dialogue_messages(context)
        provider_result, profile = self._decide_player_dialogue(target, payload, context, messages)
        parsed = parse_provider_output(provider_result)
        speech = str(parsed.get("speech") or provider_result.get("rawText") or f"{target['name']}向你点点头。")
        memory_text = str(parsed.get("memory_to_save") or f"我和新来的农场主聊了 {topic}。")

        remember(target, memory_text, tick=self.world["clock"]["tick"], importance=0.68, tags=["player_talk", topic])
        memory_payload = {"agentId": target["id"], "agentName": target["name"], "text": memory_text, "tags": ["player_talk", topic]}
        memory_event = self.event_store.append("npc.memory_created", memory_payload)
        dialogue_event = self.event_store.append(
            "npc.dialogue",
            {"agentId": target["id"], "agentName": target["name"], "targetId": "player", "speech": speech, "topic": topic},
        )

        debug = {
            "turnId": dialogue_event["id"],
            "actorId": target["id"],
            "feature": "player_dialogue",
            "profile": self._debug_profile(profile),
            "messages": messages,
            "rawText": provider_result.get("rawText", ""),
            "parsed": parsed,
            "executed": {"speech": speech},
            "memoryWrites": [memory_payload],
            "relationshipDeltas": [relationship_payload],
            "usage": provider_result.get("usage", {}),
        }
        target.setdefault("decisionHistory", []).append(debug)
        target["decisionHistory"] = target["decisionHistory"][-10:]
        debug_event = self.event_store.append("debug.turn_recorded", {"agentId": target["id"], "agentName": target["name"], "debug": debug})

        event_ids = [player_event["id"], relation_event["id"], memory_event["id"], dialogue_event["id"], debug_event["id"]]
        self._record_player_history("talk", payload, event_ids)
        return {
            "dialogue": [{"speakerId": target["id"], "speakerName": target["name"], "text": speech}],
            "relationshipDeltas": [relationship_payload],
            "memoryWrites": [memory_payload],
            "eventIds": event_ids,
        }

    def _handle_player_gift(self, payload: dict[str, Any]) -> dict[str, Any]:
        """处理首版送礼动作，先使用规则效果，后续可接入物品喜好表。"""
        target = self._get_target_agent(payload)
        item_id = str(payload.get("itemId") or "")
        item = self._take_player_item(item_id)
        before_relation = get_relation(self.world, "player", target["id"])
        adjust_relation(self.world, "player", target["id"], {"affection": 4, "trust": 2, "conflict": -1})
        after_relation = get_relation(self.world, "player", target["id"])
        relationship_payload = {
            "sourceId": "player",
            "targetId": target["id"],
            "targetName": target["name"],
            "delta": self._relation_diff(before_relation, after_relation),
            "after": after_relation,
        }
        gift_event = self.event_store.append("player.gift_given", {"playerId": "player", "targetId": target["id"], "item": item})
        relation_event = self.event_store.append("relationship.changed", relationship_payload)
        memory_text = f"新来的农场主送给我 {item['name']}，这让我对他多了一点好感。"
        remember(target, memory_text, tick=self.world["clock"]["tick"], importance=0.72, tags=["player_gift", item_id])
        memory_payload = {"agentId": target["id"], "agentName": target["name"], "text": memory_text, "tags": ["player_gift", item_id]}
        memory_event = self.event_store.append("npc.memory_created", memory_payload)
        dialogue_event = self.event_store.append("npc.dialogue", {"agentId": target["id"], "agentName": target["name"], "targetId": "player", "speech": f"谢谢你送来的{item['name']}，我会记住这份心意。", "topic": "gift"})
        event_ids = [gift_event["id"], relation_event["id"], memory_event["id"], dialogue_event["id"]]
        self._mark_known_npc(target["id"])
        self._record_player_history("give_gift", payload, event_ids)
        return {
            "dialogue": [{"speakerId": target["id"], "speakerName": target["name"], "text": dialogue_event["payload"]["speech"]}],
            "relationshipDeltas": [relationship_payload],
            "memoryWrites": [memory_payload],
            "eventIds": event_ids,
        }

    def _decide_player_dialogue(self, target: dict[str, Any], payload: dict[str, Any], context: dict[str, Any], messages: list[dict[str, str]]) -> tuple[dict[str, Any], dict[str, Any]]:
        """按模型配置生成玩家对话回复，失败时退回规则回复。"""
        profile = self.model_config.resolve_profile(agent_id=target["id"], feature="dialogue")
        provider_mode = self.provider_mode if self.provider_mode != "auto" else profile.get("provider", "rule")
        if provider_mode == "cloud" and profile.get("provider") == "cloud":
            try:
                return self.cloud_provider.decide(context, messages, profile), profile
            except Exception as error:
                fallback_profile = self.model_config.fallback_profile()
                self.event_store.append(
                    "provider.fallback",
                    {"agentId": target["id"], "agentName": target["name"], "feature": "player_dialogue", "profileName": profile.get("profileName"), "error": str(error), "fallbackProfile": fallback_profile.get("profileName")},
                )
                profile = fallback_profile
        return self._rule_player_dialogue(target, payload), profile

    def _rule_player_dialogue(self, target: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        """生成离线可用的 NPC 回复，方便没有云端密钥时继续开发游戏流程。"""
        topic = str(payload.get("topic") or "free_talk")
        message = str(payload.get("message") or "你好，我刚搬到小镇。")
        if "医生" in target["job"]:
            speech = "欢迎来到小镇。刚搬家别太劳累，如果农场生活让你不适应，可以来白桦诊所找我。"
        elif "酒馆" in target["job"] or target["id"] == "kai":
            speech = "新来的农场主？太好了，月猫酒馆今晚也许会有新故事。等你有空，来听我弹一曲吧。"
        elif "农夫" in target["job"]:
            speech = "晨露农场终于有人打理了。只要你踏实干活，小镇会慢慢接纳你。"
        elif "店主" in target["job"]:
            speech = "欢迎你，农场主。需要种子、食材或生活用品时，可以来星露杂货铺找我。"
        else:
            speech = f"欢迎来到 Agent Valley。我听见你说“{message}”，之后我们可以慢慢熟悉。"
        response = {"speech": speech, "action": "talkTo", "args": {"npc": "player", "topic": topic, "message": speech}, "memory_to_save": f"新来的农场主和我聊了 {topic}，他说：{message[:60]}"}
        return {"provider": "RuleDialogueProvider", "rawText": json.dumps(response, ensure_ascii=False), "parsed": response, "usage": {"tokens": 0, "cost": 0, "latencyMs": 1}}

    def _sync_player_location(self, payload: dict[str, Any]) -> None:
        """根据客户端上报地点同步玩家位置，减少 Godot 首版接入时的状态阻塞。"""
        location_id = payload.get("locationId")
        if location_id and location_id in self.world["locations"]:
            self.world["player"]["locationId"] = str(location_id)

    def _get_target_agent(self, payload: dict[str, Any]) -> dict[str, Any]:
        """读取玩家动作目标 NPC。"""
        target_id = str(payload.get("targetId") or "")
        target = self.world["agents"].get(target_id)
        if not target or not target.get("alive", True):
            raise ValueError(f"未知或不可交互 NPC：{target_id}")
        return target

    def _mark_known_npc(self, npc_id: str) -> None:
        """记录玩家已经认识的 NPC，供任务和对话分支使用。"""
        known = self.world["player"].setdefault("knownNpcs", [])
        if npc_id not in known:
            known.append(npc_id)

    def _record_player_history(self, action_type: str, payload: dict[str, Any], event_ids: list[str]) -> None:
        """记录玩家行动历史，后续可直接扩展为存档或任务条件。"""
        history = self.world["player"].setdefault("actionHistory", [])
        history.append({"tick": self.world["clock"]["tick"], "type": action_type, "payload": dict(payload), "eventIds": event_ids})
        self.world["player"]["actionHistory"] = history[-40:]

    def _take_player_item(self, item_id: str) -> dict[str, Any]:
        """从玩家背包扣除一个物品。"""
        if not item_id:
            raise ValueError("送礼动作缺少 itemId")
        inventory = self.world["player"].setdefault("inventory", [])
        for item in inventory:
            if item.get("id") == item_id and int(item.get("quantity", 0)) > 0:
                item["quantity"] = int(item["quantity"]) - 1
                return {"id": item["id"], "name": item.get("name", item["id"])}
        raise ValueError(f"玩家背包中没有可送出的物品：{item_id}")

    def _relation_diff(self, before: dict[str, Any], after: dict[str, Any]) -> dict[str, int]:
        """计算关系数值变化，便于 Debug Console 展示。"""
        return {
            "affection": int(after.get("affection", 0)) - int(before.get("affection", 0)),
            "trust": int(after.get("trust", 0)) - int(before.get("trust", 0)),
            "conflict": int(after.get("conflict", 0)) - int(before.get("conflict", 0)),
        }

    def _debug_profile(self, profile: dict[str, Any]) -> dict[str, Any]:
        """Debug 展示模型配置时隐藏实际密钥。"""
        safe_profile = dict(profile)
        safe_profile.pop("apiKey", None)
        if safe_profile.get("apiKeyEnv"):
            safe_profile["apiKeyConfigured"] = bool(os.getenv(str(safe_profile["apiKeyEnv"])))
        return safe_profile
