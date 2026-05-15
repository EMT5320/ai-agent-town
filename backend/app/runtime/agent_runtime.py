from __future__ import annotations

import json
import os
from typing import Any

from app.config.model_config import ModelConfigStore
from app.director import DirectorBeat, DirectorQueueManager, DirectorValidator, SkillRouter, TensionDetector, WorldDigest
from app.events.event_store import EventStore
from app.memory.memory_store import remember
from app.providers.cloud_api_provider import CloudApiProvider
from app.providers.context_builder import (
    build_agent_context,
    build_event_reaction_context,
    build_event_reaction_messages,
    build_night_reflection_context,
    build_night_reflection_messages,
    build_player_dialogue_context,
    build_player_dialogue_messages,
    build_prompt_messages,
)
from app.providers.rule_based_provider import RuleBasedProvider
from app.runtime.action_executor import execute_action, maybe_population_event
from app.runtime.action_parser import parse_provider_output
from app.skills import STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID, EventSkillSchema, get_event_skill, list_event_skills
from app.world.seed_data import DAY1_EVENT_ID
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
        self.event_skills = {skill.skill_id: skill for skill in list_event_skills()}
        self.tension_detector = TensionDetector()
        self.skill_router = SkillRouter()
        self.director_validator = DirectorValidator(
            allowed_skill_registry=list(self.event_skills),
            valid_target_agents=["player", *self.world["agents"].keys()],
        )
        self.director_queue = DirectorQueueManager(self.director_validator)
        self.world.setdefault("directorState", {"activatedEventSkills": [], "consumedBeatIds": []})
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
        elif action_type == "inspect":
            result = self._handle_player_inspect(payload)
        elif action_type == "attend_event":
            result = self._handle_player_attend_event(payload)
        else:
            raise ValueError(f"未知玩家动作：{action_type}")
        return {"ok": True, "result": result, "state": self.get_game_state()}

    def step(self, actor_id: str = "developer") -> dict[str, Any]:
        if self.world["clock"].get("paused"):
            return {"skipped": True, "reason": "paused", "state": self.get_public_state()}
        self._run_director_v0()
        actors = self.pick_actors()
        decisions = []
        for agent in actors:
            context = build_agent_context(self.world, agent, self.event_store)
            messages = build_prompt_messages(context)
            profile = self.model_config.resolve_profile(agent_id=agent["id"], feature="agent_decision")
            result, fallback_reason = self._call_profile_provider(
                feature="agent_decision",
                agent=agent,
                context=context,
                messages=messages,
                profile=profile,
                rule_call=lambda: self.rule_provider.decide(context, messages),
            )
            parsed = parse_provider_output(result)
            executed = execute_action(self.world, agent, parsed, self.event_store)
            debug = self._build_provider_debug(
                feature="agent_decision",
                profile=profile,
                messages=messages,
                result=result,
                parsed=parsed,
                fallback_reason=fallback_reason,
                executed=executed["payload"],
            )
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

    def _run_director_v0(self) -> None:
        """运行规则版 Director v0，并把摘要、Beat 和队列结果写入 Debug 事件流。"""
        digest = WorldDigest.from_world(self.world)
        self.event_store.append("director.digest_created", self._director_digest_payload(digest))

        skill = get_event_skill(STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID)
        if self._should_activate_event_skill(skill):
            beat = self._create_activate_event_skill_beat(digest, skill)
            self.event_store.append("director.beat_created", beat.to_dict())
            validation = self.director_validator.validate(beat, current_world_version=digest.world_version)
            self.event_store.append(
                "director.beat_validated",
                {"beatId": beat.beatId, "ok": validation.ok, "errors": list(validation.errors), "beat": beat.to_dict()},
            )
            if validation.ok:
                enqueue_result = self.director_queue.enqueue(beat, current_world_version=digest.world_version)
                if enqueue_result.discarded:
                    self.event_store.append("director.beat_discarded", enqueue_result.discarded.to_event_payload())
            else:
                self.event_store.append(
                    "director.beat_discarded",
                    {"beatId": beat.beatId, "reason": "validation_failed", "detail": "; ".join(validation.errors), "beat": beat.to_dict()},
                )

        self._consume_director_queue(digest)

    def _consume_director_queue(self, digest: WorldDigest | None = None) -> None:
        """消费 Director 队列，并记录已消费或丢弃的 Beat。"""
        digest = digest or WorldDigest.from_world(self.world)
        consume_result = self.director_queue.consume(digest)
        for beat in consume_result.ready:
            active_focus = self._apply_director_beat(beat)
            self.event_store.append("director.beat_consumed", {"beat": beat.to_dict(), "activeFocus": active_focus})
        for discarded in consume_result.discarded:
            self.event_store.append("director.beat_discarded", discarded.to_event_payload())

    def _director_digest_payload(self, digest: WorldDigest) -> dict[str, Any]:
        """把 WorldDigest 转成 EventStore 友好的调试载荷。"""
        return {
            "worldVersion": digest.world_version,
            "tick": digest.tick,
            "livingAgentIds": list(digest.living_agent_ids),
            "activeEventCount": digest.active_event_count,
            "avgStress": digest.avg_stress,
        }

    def _should_activate_event_skill(self, skill: EventSkillSchema) -> bool:
        """检测星灯祭供应短缺候选，避免同一个事件技能重复激活。"""
        director_state = self.world.setdefault("directorState", {"activatedEventSkills": [], "consumedBeatIds": []})
        if skill.skill_id in director_state.setdefault("activatedEventSkills", []):
            return False
        trigger = skill.trigger
        required_event_id = trigger.required_active_event_id or skill.event_id
        for event in self.world.get("activeEvents", []):
            if event.get("id") != required_event_id:
                continue
            if event.get("status") != trigger.required_status:
                continue
            if event.get("locationId") != trigger.location_id:
                continue
            if event.get("phase") != trigger.phase:
                continue
            return True
        return False

    def _create_activate_event_skill_beat(self, digest: WorldDigest, skill: EventSkillSchema) -> DirectorBeat:
        """把事件技能候选转为 activate_event_skill Beat。"""
        tension = self.tension_detector.detect(digest)
        target_agents = [agent_id for agent_id in skill.participants if agent_id != "player" and agent_id in self.world["agents"]]
        allowed_skills = [skill.skill_id]
        routed_skills = self.skill_router.route(tension, target_agents, candidate_skills=allowed_skills)
        if not routed_skills:
            routed_skills = allowed_skills
        return DirectorBeat(
            beatType="activate_event_skill",
            worldVersion=digest.world_version,
            validFromTick=digest.tick,
            expiresAtTick=digest.tick + 2,
            targetAgents=target_agents,
            allowedSkills=routed_skills,
            payload={
                "skillId": skill.skill_id,
                "eventId": skill.event_id,
                "title": skill.title,
                "brief": skill.brief,
                "trigger": {
                    "phase": skill.trigger.phase,
                    "locationId": skill.trigger.location_id,
                    "requiredStatus": skill.trigger.required_status,
                    "requiredActiveEventId": skill.trigger.required_active_event_id,
                },
                "playerOptions": [
                    {
                        "id": option.option_id,
                        "label": option.label,
                        "brief": option.brief,
                        "requiresPlayerItemId": option.requires_player_item_id,
                        "consequenceTypes": [consequence.consequence_type for consequence in option.consequences],
                    }
                    for option in skill.player_options
                ],
                "assetHints": [
                    {"id": hint.hint_id, "type": hint.asset_type, "brief": hint.brief, "tags": list(hint.tags)}
                    for hint in skill.asset_hints
                ],
                "tension": {"level": tension.level, "score": tension.score, "evidence": tension.evidence},
            },
        )

    def _apply_director_beat(self, beat: DirectorBeat) -> dict[str, Any]:
        """把已消费 Beat 写入世界的轻量 Director 状态，供后续层读取。"""
        director_state = self.world.setdefault("directorState", {"activatedEventSkills": [], "consumedBeatIds": []})
        director_state.setdefault("consumedBeatIds", []).append(beat.beatId)
        payload = dict(beat.payload)
        skill_id = str(payload.get("skillId") or "")
        if skill_id:
            activated = director_state.setdefault("activatedEventSkills", [])
            if skill_id not in activated:
                activated.append(skill_id)
        active_focus = {
            "type": beat.beatType,
            "beatId": beat.beatId,
            "skillId": skill_id,
            "eventId": payload.get("eventId"),
            "brief": payload.get("brief"),
            "targetAgents": list(beat.targetAgents),
            "validFromTick": beat.validFromTick,
            "expiresAtTick": beat.expiresAtTick,
        }
        self.world["activeFocus"] = active_focus
        return active_focus

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
        provider_result, profile, fallback_reason = self._decide_player_dialogue(target, payload, context, messages)
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

        debug = self._build_provider_debug(
            feature="dialogue",
            profile=profile,
            messages=messages,
            result=provider_result,
            parsed=parsed,
            fallback_reason=fallback_reason,
            executed={"speech": speech},
            extra={
                "turnId": dialogue_event["id"],
                "actorId": target["id"],
                "memoryWrites": [memory_payload],
                "relationshipDeltas": [relationship_payload],
            },
        )
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

    def _handle_player_inspect(self, payload: dict[str, Any]) -> dict[str, Any]:
        """查看地点或事件提示，给 Godot 地图层提供轻量调查动作。"""
        event_id = str(payload.get("eventId") or "")
        location_id = str(payload.get("locationId") or self.world["player"].get("locationId") or "")
        if event_id:
            event = self._get_active_event(event_id)
            inspect_payload = {
                "subjectType": "event",
                "subjectId": event["id"],
                "title": event["title"],
                "summary": event["summary"],
                "locationId": event["locationId"],
                "status": event["status"],
                "choices": event.get("choices", []),
            }
        else:
            if location_id not in self.world["locations"]:
                raise ValueError(f"未知地点：{location_id}")
            location = self.world["locations"][location_id]
            nearby = [agent for agent in living_agents(self.world) if agent.get("locationId") == location_id]
            inspect_payload = {
                "subjectType": "location",
                "subjectId": location_id,
                "title": location["name"],
                "summary": location["description"],
                "nearbyNpcs": [{"id": agent["id"], "name": agent["name"], "job": agent["job"]} for agent in nearby],
            }

        event = self.event_store.append("player.inspected", {"playerId": "player", **inspect_payload})
        self.world["player"].setdefault("questFlags", {})[f"inspected_{inspect_payload['subjectId']}"] = True
        self._record_player_history("inspect", payload, [event["id"]])
        return {
            "dialogue": [{"speakerId": "system", "speakerName": "旁白", "text": inspect_payload["summary"]}],
            "relationshipDeltas": [],
            "memoryWrites": [],
            "inspect": inspect_payload,
            "eventIds": [event["id"]],
        }

    def _handle_player_attend_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        """处理星灯祭供应短缺事件选择，并写入关系、记忆和夜间反思种子。"""
        event_id = str(payload.get("eventId") or DAY1_EVENT_ID)
        choice = str(payload.get("choice") or "mediate")
        event = self._get_active_event(event_id)
        if event.get("status") == "resolved":
            raise ValueError(f"事件已结算：{event_id}")
        if choice == "donate_crop":
            donated_item = self._take_player_item("fresh_turnip")
        else:
            donated_item = None

        self.world["player"]["locationId"] = event["locationId"]
        outcome = self._starlight_outcome(choice, donated_item)
        choice_event = self.event_store.append(
            "player.event_choice",
            {
                "playerId": "player",
                "eventId": event_id,
                "choice": choice,
                "choiceLabel": outcome["choiceLabel"],
                "summary": outcome["summary"],
            },
        )

        relationship_events: list[dict[str, Any]] = []
        relationship_payloads: list[dict[str, Any]] = []
        for target_id, delta in outcome["relationDeltas"].items():
            if target_id in self.world["agents"]:
                payload_delta = self._apply_player_relation_delta(target_id, delta)
                relationship_payloads.append(payload_delta)
                relationship_events.append(self.event_store.append("relationship.changed", payload_delta))

        memory_payloads, memory_events = self._write_starlight_memories(choice, outcome)
        dialogue_payloads, dialogue_events = self._write_starlight_dialogue(event, choice, outcome)
        reflection_payloads, reflection_events = self._write_starlight_reflections(event, choice, outcome)

        event["status"] = "resolved"
        event["resolution"] = {"choice": choice, "summary": outcome["summary"], "resolvedTick": self.world["clock"]["tick"]}
        self.world.setdefault("completedEvents", []).append(dict(event))
        self.world["player"].setdefault("questFlags", {})["starlight_shortage"] = f"resolved_{choice}"
        resolved_event = self.event_store.append("town.event_resolved", {"eventId": event_id, "choice": choice, "summary": outcome["summary"]})

        event_ids = (
            [choice_event["id"]]
            + [item["id"] for item in relationship_events]
            + [item["id"] for item in memory_events]
            + [item["id"] for item in dialogue_events]
            + [item["id"] for item in reflection_events]
            + [resolved_event["id"]]
        )
        self._record_player_history("attend_event", payload, event_ids)
        return {
            "dialogue": dialogue_payloads,
            "relationshipDeltas": relationship_payloads,
            "memoryWrites": memory_payloads + reflection_payloads,
            "eventResult": {"eventId": event_id, "choice": choice, "summary": outcome["summary"]},
            "eventIds": event_ids,
        }

    def _get_active_event(self, event_id: str) -> dict[str, Any]:
        """按 id 读取当前可交互事件。"""
        for event in self.world.get("activeEvents", []):
            if event.get("id") == event_id:
                return event
        raise ValueError(f"未知事件：{event_id}")

    def _starlight_outcome(self, choice: str, donated_item: dict[str, Any] | None) -> dict[str, Any]:
        """返回星灯祭供应短缺事件的规则结算表。"""
        item_name = donated_item["name"] if donated_item else "农场作物"
        outcomes: dict[str, dict[str, Any]] = {
            "donate_crop": {
                "choiceLabel": f"拿出{item_name}帮酒馆渡过今晚",
                "summary": f"玩家拿出{item_name}补上节日食材，凯娅松了一口气，布兰娜也承认这份帮忙很实在。",
                "relationDeltas": {
                    "kai": {"affection": 5, "trust": 4, "conflict": -5},
                    "bram": {"affection": 2, "trust": 3, "conflict": -4},
                    "mira": {"affection": 1, "trust": 2, "conflict": -1},
                    "lena": {"affection": 1, "trust": 1, "conflict": -1},
                    "orren": {"affection": 1, "trust": 2, "conflict": -1},
                    "tomas": {"affection": 1, "trust": 1, "conflict": -1},
                },
            },
            "mediate": {
                "choiceLabel": "调解凯娅和布兰娜的欠账冲突",
                "summary": "玩家请凯娅先确认还款安排，也帮布兰娜保住供货底线，争执被暂时压了下来。",
                "relationDeltas": {
                    "kai": {"affection": 3, "trust": 4, "conflict": -4},
                    "bram": {"affection": 3, "trust": 4, "conflict": -5},
                    "mira": {"affection": 1, "trust": 2, "conflict": -1},
                    "lena": {"affection": 1, "trust": 2, "conflict": -1},
                    "orren": {"affection": 1, "trust": 2, "conflict": -1},
                },
            },
            "support_kai": {
                "choiceLabel": "优先支持凯娅维持节日气氛",
                "summary": "玩家站在凯娅这边让星灯祭继续热闹，但布兰娜对酒馆旧账更加不满。",
                "relationDeltas": {
                    "kai": {"affection": 5, "trust": 2, "conflict": -2},
                    "bram": {"affection": -1, "trust": -1, "conflict": 4},
                    "mira": {"trust": 1},
                    "orren": {"trust": 1},
                },
            },
            "support_bram": {
                "choiceLabel": "优先支持布兰娜守住供货底线",
                "summary": "玩家支持布兰娜先把欠账说清，酒馆气氛短暂降温，但供货压力被认真看见了。",
                "relationDeltas": {
                    "kai": {"affection": -1, "trust": 0, "conflict": 3},
                    "bram": {"affection": 5, "trust": 3, "conflict": -2},
                    "mira": {"trust": 1},
                    "lena": {"trust": 1},
                },
            },
            "observe": {
                "choiceLabel": "先旁观并记录大家的反应",
                "summary": "玩家没有立刻介入，只观察到凯娅的焦虑、布兰娜的压力，以及旁观居民的担心。",
                "relationDeltas": {
                    "orren": {"trust": 1},
                    "lena": {"trust": 1},
                },
            },
        }
        if choice not in outcomes:
            raise ValueError(f"未知星灯祭事件选项：{choice}")
        return outcomes[choice]

    def _apply_player_relation_delta(self, target_id: str, delta: dict[str, int | str]) -> dict[str, Any]:
        """调整玩家与 NPC 的关系并返回 Debug 友好的差值记录。"""
        target = self.world["agents"][target_id]
        before_relation = get_relation(self.world, "player", target_id)
        adjust_relation(self.world, "player", target_id, delta)
        after_relation = get_relation(self.world, "player", target_id)
        return {
            "sourceId": "player",
            "targetId": target_id,
            "targetName": target["name"],
            "delta": self._relation_diff(before_relation, after_relation),
            "after": after_relation,
        }

    def _write_starlight_memories(self, choice: str, outcome: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """让参与者写入对星灯祭事件的即时主观记忆。"""
        memory_templates = {
            "kai": "星灯祭前夜差点因为食材短缺冷场，玩家的选择让我重新看见节日还能继续发光。",
            "bram": "酒馆欠账和供货压力被摆到台面上，玩家的处理方式让我重新评估这个新农场主。",
            "mira": "今晚的供应短缺让我担心小镇账目，但玩家让局面没有继续恶化。",
            "lena": "争执让大家都紧绷，玩家的介入至少让晚上的情绪风险降了下来。",
            "orren": "星灯祭的传统需要年轻人接住，玩家今晚给这段传统留下了新的注脚。",
            "tomas": "我在旁边修灯架时看见玩家处理争执，这个人也许愿意认真守护小镇。",
        }
        payloads: list[dict[str, Any]] = []
        events: list[dict[str, Any]] = []
        for agent_id, text in memory_templates.items():
            agent = self.world["agents"][agent_id]
            memory_text = f"{text} 结局：{outcome['summary']}"
            remember(agent, memory_text, tick=self.world["clock"]["tick"], importance=0.8, tags=["starlight_shortage", choice])
            payload = {"agentId": agent_id, "agentName": agent["name"], "text": memory_text, "tags": ["starlight_shortage", choice]}
            payloads.append(payload)
            events.append(self.event_store.append("npc.memory_created", payload))
        return payloads, events

    def _write_starlight_dialogue(self, event: dict[str, Any], choice: str, outcome: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """按 event_reaction profile 生成事件结算时玩家能看到的关键 NPC 台词。"""
        context = build_event_reaction_context(self.world, event, outcome, choice, self.event_store)
        messages = build_event_reaction_messages(context)
        profile = self.model_config.resolve_profile(feature="event_reaction")
        rule_result = self._rule_event_reaction(choice, outcome)
        provider_result, fallback_reason = self._call_profile_provider(
            feature="event_reaction",
            agent=None,
            context=context,
            messages=messages,
            profile=profile,
            rule_call=lambda: rule_result,
        )
        parsed = parse_provider_output(provider_result, fallback=rule_result["parsed"])
        payloads = self._normalise_dialogue_payloads(parsed, rule_result["parsed"]["dialogue"])
        if not any(item.get("speakerId") == "system" and item.get("text") == outcome["summary"] for item in payloads):
            payloads.append({"speakerId": "system", "speakerName": "旁白", "text": outcome["summary"]})

        events: list[dict[str, Any]] = []
        for payload in payloads:
            agent_id = payload.get("speakerId")
            if agent_id in self.world["agents"]:
                agent = self.world["agents"][str(agent_id)]
                events.append(
                    self.event_store.append(
                        "npc.dialogue",
                        {"agentId": agent_id, "agentName": agent["name"], "targetId": "player", "speech": payload["text"], "topic": "starlight_shortage"},
                    )
                )

        debug = self._build_provider_debug(
            feature="event_reaction",
            profile=profile,
            messages=messages,
            result=provider_result,
            parsed=parsed,
            fallback_reason=fallback_reason,
            executed={"dialogue": payloads},
            extra={"eventId": event.get("id"), "choice": choice},
        )
        events.append(self.event_store.append("debug.turn_recorded", {"agentId": "system", "agentName": event.get("title", "事件"), "debug": debug}))
        return payloads, events

    def _write_starlight_reflections(self, event: dict[str, Any], choice: str, outcome: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """按 night_reflection profile 生成夜间反思摘要，失败时保留规则反思。"""
        context = build_night_reflection_context(self.world, event, outcome, choice, self.event_store)
        messages = build_night_reflection_messages(context)
        profile = self.model_config.resolve_profile(feature="night_reflection")
        rule_result = self._rule_night_reflection(choice, outcome)
        provider_result, fallback_reason = self._call_profile_provider(
            feature="night_reflection",
            agent=None,
            context=context,
            messages=messages,
            profile=profile,
            rule_call=lambda: rule_result,
        )
        parsed = parse_provider_output(provider_result, fallback=rule_result["parsed"])
        payloads = self._normalise_reflection_payloads(parsed, rule_result["parsed"]["reflections"], choice)

        events: list[dict[str, Any]] = []
        for payload in payloads:
            agent = self.world["agents"][payload["agentId"]]
            remember(agent, payload["text"], tick=self.world["clock"]["tick"], importance=0.86, tags=payload["tags"])
            self.world.setdefault("nightReflections", []).append(payload)
            events.append(self.event_store.append("npc.night_reflection", payload))

        debug = self._build_provider_debug(
            feature="night_reflection",
            profile=profile,
            messages=messages,
            result=provider_result,
            parsed=parsed,
            fallback_reason=fallback_reason,
            executed={"reflections": payloads},
            extra={"eventId": event.get("id"), "choice": choice},
        )
        events.append(self.event_store.append("debug.turn_recorded", {"agentId": "system", "agentName": event.get("title", "事件"), "debug": debug}))
        return payloads, events

    def _decide_player_dialogue(self, target: dict[str, Any], payload: dict[str, Any], context: dict[str, Any], messages: list[dict[str, str]]) -> tuple[dict[str, Any], dict[str, Any], str | None]:
        """按 dialogue profile 生成玩家对话回复，失败时退回规则回复。"""
        profile = self.model_config.resolve_profile(agent_id=target["id"], feature="dialogue")
        provider_result, fallback_reason = self._call_profile_provider(
            feature="dialogue",
            agent=target,
            context=context,
            messages=messages,
            profile=profile,
            rule_call=lambda: self._rule_player_dialogue(target, payload),
        )
        return provider_result, profile, fallback_reason

    def _call_profile_provider(
        self,
        *,
        feature: str,
        agent: dict[str, Any] | None,
        context: dict[str, Any],
        messages: list[dict[str, str]],
        profile: dict[str, Any],
        rule_call: Any,
    ) -> tuple[dict[str, Any], str | None]:
        """统一按 profile 调用云端或规则 Provider，并记录云端失败原因。"""
        provider_mode = self._effective_provider_mode(profile)
        if provider_mode == "cloud" and profile.get("provider") == "cloud":
            try:
                return self.cloud_provider.decide(context, messages, profile), None
            except Exception as error:
                fallback_profile = self.model_config.fallback_profile()
                fallback_reason = self._safe_error_message(error)
                self.event_store.append(
                    "provider.fallback",
                    {
                        "agentId": agent.get("id") if agent else None,
                        "agentName": agent.get("name") if agent else None,
                        "feature": feature,
                        "providerMode": provider_mode,
                        "profileName": profile.get("profileName"),
                        "error": fallback_reason,
                        "fallbackProfile": fallback_profile.get("profileName"),
                    },
                )
                return rule_call(), fallback_reason
        if provider_mode == "cloud" and profile.get("provider") != "cloud":
            return rule_call(), "profile_provider_rule"
        return rule_call(), None

    def _rule_event_reaction(self, choice: str, outcome: dict[str, Any]) -> dict[str, Any]:
        """生成离线可用的事件反应 JSON，供 event_reaction fallback 使用。"""
        lines_by_choice = {
            "donate_crop": [
                ("kai", "你真的把农场作物拿来了？今晚的星灯不会暗下去了，谢谢你！"),
                ("bram", "哼，至少你知道作物不是凭空来的。这份人情我记下。"),
            ],
            "mediate": [
                ("kai", "好啦好啦，我会把账单写清楚。谢谢你没有让今晚变成吵架大会。"),
                ("bram", "能把话说到点子上，比单纯站队强。新来的，你有点分寸。"),
            ],
            "support_kai": [
                ("kai", "我就知道有人懂星灯祭的重要！今晚先让大家笑起来吧。"),
                ("bram", "热闹不能抵账。你今天的选择我看见了。"),
            ],
            "support_bram": [
                ("bram", "总算有人听见供货人的难处。节日也得先把账算明白。"),
                ("kai", "我知道她辛苦，可今晚的灯要是灭了，大家都会难过的。"),
            ],
            "observe": [
                ("orren", "观察也是选择。你至少看见了节日背后的裂缝。"),
                ("lena", "先不急着介入也可以，但今晚需要有人继续照看大家的情绪。"),
            ],
        }
        dialogue = [{"agentId": agent_id, "speech": speech} for agent_id, speech in lines_by_choice[choice]]
        response = {"dialogue": dialogue, "memory_to_save": f"事件结算：{outcome['summary']}"}
        return {"provider": "RuleEventReactionProvider", "rawText": json.dumps(response, ensure_ascii=False), "parsed": response, "usage": {"tokens": 0, "cost": 0, "latencyMs": 1}}

    def _rule_night_reflection(self, choice: str, outcome: dict[str, Any]) -> dict[str, Any]:
        """生成离线可用的夜间反思 JSON，供 night_reflection fallback 使用。"""
        response = {
            "reflections": [
                {"agentId": "kai", "text": f"如果不是玩家选择“{outcome['choiceLabel']}”，我可能会把节日压力全推给别人。明天要认真面对欠账。"},
                {"agentId": "bram", "text": "这个新来的农场主没有把供应当成理所当然。无论是否站在我这边，至少看见了农场人的压力。"},
                {"agentId": "lena", "text": "今晚的冲突证明节日压力会影响健康和关系。玩家的选择值得继续观察。"},
            ]
        }
        return {"provider": "RuleNightReflectionProvider", "rawText": json.dumps(response, ensure_ascii=False), "parsed": response, "usage": {"tokens": 0, "cost": 0, "latencyMs": 1}}

    def _normalise_dialogue_payloads(self, parsed: dict[str, Any], fallback_dialogue: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """把模型输出统一整理成前端可消费的 dialogue payload。"""
        if parsed.get("naturalLanguageFallback") and parsed.get("speech"):
            items = [{"agentId": "system", "speech": parsed["speech"]}]
        else:
            items = parsed.get("dialogue")
        if isinstance(items, str):
            items = [{"agentId": "system", "speech": items}]
        if not isinstance(items, list) or not items:
            speech = parsed.get("speech")
            items = [{"agentId": "system", "speech": speech}] if speech else fallback_dialogue

        payloads: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            speaker_id = str(item.get("agentId") or item.get("speakerId") or "system")
            text = str(item.get("speech") or item.get("text") or "").strip()
            if not text:
                continue
            if speaker_id in self.world["agents"]:
                speaker_name = self.world["agents"][speaker_id]["name"]
            else:
                speaker_id = "system"
                speaker_name = str(item.get("speakerName") or "旁白")
            payloads.append({"speakerId": speaker_id, "speakerName": speaker_name, "text": text})
        if payloads:
            return payloads
        return self._normalise_dialogue_payloads({"dialogue": fallback_dialogue}, [])

    def _normalise_reflection_payloads(self, parsed: dict[str, Any], fallback_reflections: list[dict[str, Any]], choice: str) -> list[dict[str, Any]]:
        """把模型输出统一整理成 nightReflections 与记忆系统可写入的 payload。"""
        if parsed.get("naturalLanguageFallback") and parsed.get("speech"):
            items = [{"agentId": fallback_reflections[0]["agentId"], "text": parsed["speech"]}]
        else:
            items = parsed.get("reflections")
        if isinstance(items, str):
            items = [{"agentId": fallback_reflections[0]["agentId"], "text": items}]
        if not isinstance(items, list) or not items:
            speech = parsed.get("speech")
            items = [{"agentId": fallback_reflections[0]["agentId"], "text": speech}] if speech else fallback_reflections

        payloads: list[dict[str, Any]] = []
        tags = ["night_reflection", "starlight_shortage", choice]
        for item in items:
            if not isinstance(item, dict):
                continue
            agent_id = str(item.get("agentId") or "")
            text = str(item.get("text") or item.get("reflection") or item.get("speech") or "").strip()
            if agent_id not in self.world["agents"] or not text:
                continue
            agent = self.world["agents"][agent_id]
            payloads.append({"agentId": agent_id, "agentName": agent["name"], "text": text, "tags": tags})
        if payloads:
            return payloads
        return self._normalise_reflection_payloads({"reflections": fallback_reflections}, fallback_reflections, choice)

    def _build_provider_debug(
        self,
        *,
        feature: str,
        profile: dict[str, Any],
        messages: list[dict[str, str]],
        result: dict[str, Any],
        parsed: dict[str, Any],
        fallback_reason: str | None,
        executed: dict[str, Any] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """构建三类 LLM 验证共用的 Debug 记录，字段保持扁平可查。"""
        debug_profile = self._debug_profile(profile)
        usage = result.get("usage", {}) if isinstance(result.get("usage"), dict) else {}
        debug = {
            "tick": self.world["clock"]["tick"],
            "feature": feature,
            "provider": result.get("provider"),
            "providerMode": self._effective_provider_mode(profile),
            "profileName": debug_profile.get("profileName"),
            "apiKeyConfigured": bool(debug_profile.get("apiKeyConfigured")),
            "profile": debug_profile,
            "messages": messages,
            "rawText": result.get("rawText", ""),
            "parsed": parsed,
            "executed": executed or {},
            "usage": usage,
            "latency": usage.get("latencyMs", result.get("latencyMs")),
            "fallbackReason": fallback_reason,
        }
        if extra:
            debug.update(extra)
        return debug

    def _effective_provider_mode(self, profile: dict[str, Any]) -> str:
        """解析当前调用实际采用的 Provider 模式。"""
        return self.provider_mode if self.provider_mode != "auto" else str(profile.get("provider", "rule"))

    def _safe_error_message(self, error: Exception) -> str:
        """保留错误摘要，避免把请求头或密钥写入事件流。"""
        message = str(error)
        for env_name in ("OPENAI_API_KEY", "DEEPSEEK_API_KEY", "AGENT_TOWN_API_KEY"):
            secret = os.getenv(env_name)
            if secret:
                message = message.replace(secret, "[REDACTED_SECRET]")
        return message

    def _rule_player_dialogue(self, target: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        """生成离线可用的 NPC 回复，方便没有云端密钥时继续开发游戏流程。"""
        topic = str(payload.get("topic") or "free_talk")
        message = str(payload.get("message") or "你好，我刚搬到小镇。")
        if "医生" in target["job"]:
            speech = "欢迎来到小镇。刚搬家别太劳累，如果农场生活让你不适应，可以来白桦诊所找我。"
        elif "酒馆" in target["job"] or target["id"] == "kai":
            speech = "新来的农场主？太好了，月猫酒馆今晚也许会有新故事。等你有空，来听我弹一曲吧。"
        elif "农夫" in target["job"] or "农场主" in target["job"]:
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
        has_inline_key = bool(safe_profile.pop("apiKey", None))
        env_configured = False
        if safe_profile.get("apiKeyEnv"):
            env_configured = bool(os.getenv(str(safe_profile["apiKeyEnv"])))
        if safe_profile.get("provider") == "cloud":
            env_configured = env_configured or bool(os.getenv("OPENAI_API_KEY"))
        safe_profile["apiKeyConfigured"] = has_inline_key or env_configured
        return safe_profile
