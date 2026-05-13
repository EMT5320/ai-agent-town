from __future__ import annotations

import os
from typing import Any

from app.config.model_config import ModelConfigStore
from app.events.event_store import EventStore
from app.providers.cloud_api_provider import CloudApiProvider
from app.providers.context_builder import build_agent_context, build_prompt_messages
from app.providers.rule_based_provider import RuleBasedProvider
from app.runtime.action_executor import execute_action, maybe_population_event
from app.runtime.action_parser import parse_provider_output
from app.world.world_state import advance_clock, create_initial_world, living_agents, public_world


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

    def _debug_profile(self, profile: dict[str, Any]) -> dict[str, Any]:
        """Debug 展示模型配置时隐藏实际密钥。"""
        safe_profile = dict(profile)
        safe_profile.pop("apiKey", None)
        if safe_profile.get("apiKeyEnv"):
            safe_profile["apiKeyConfigured"] = bool(os.getenv(str(safe_profile["apiKeyEnv"])))
        return safe_profile
