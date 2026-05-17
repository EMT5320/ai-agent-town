from __future__ import annotations

from copy import deepcopy
from typing import Any


# 首版动作持续时间规则，后续可替换为配置化表。
ACTION_DURATION_SECONDS = {
    "tend_farm": 300.0,
    "chat_with": 120.0,
    "tend_shop": 600.0,
}
DEFAULT_ACTION_DURATION_SECONDS = 180.0
# 位置距离按“横向舞台单位”估算：同场景用 0..1 屏幕比例，跨场景叠加舞台偏移。
LOCATION_STAGE_OFFSETS = {"farm": 0.0, "plaza": 1.0, "tavern": 2.0, "shop": 1.0, "clinic": 1.0, "home-north": 3.0}
MOVE_SPEED_PER_SECOND = 0.08
ACTION_TICK_INTERVAL_SECONDS = 30.0


class LifeActionExecutor:
    """规则驱动推进 lifeActionPlan.selectedActions，输出最小事件和 NPC 差异。"""

    def tick(
        self,
        *,
        world: dict[str, Any],
        selected_actions: list[dict[str, Any]],
        delta_seconds: float,
    ) -> dict[str, Any]:
        if delta_seconds <= 0:
            return {"events": [], "agents": [], "completedActions": []}
        runtime_state = world.setdefault("lifeActionRuntime", {})
        presence_index = self._presence_index(world)
        events: list[dict[str, Any]] = []
        agent_diffs: list[dict[str, Any]] = []
        completed_actions: list[dict[str, Any]] = []

        for selected in selected_actions:
            npc_id = str(selected.get("npcId") or "")
            agent = world.get("agents", {}).get(npc_id)
            presence = presence_index.get(npc_id)
            target_anchor_id = str(selected.get("targetAnchorId") or "")
            target_location_id = str(selected.get("targetLocationId") or "")
            if not npc_id or not isinstance(agent, dict) or not isinstance(presence, dict) or not target_anchor_id or not target_location_id:
                continue
            anchor = world.get("anchors", {}).get(target_anchor_id)
            if not isinstance(anchor, dict):
                continue
            state = runtime_state.setdefault(npc_id, {})
            self._reset_state_if_needed(
                state=state,
                selected=selected,
                current_anchor_id=str(presence.get("anchorId") or ""),
                target_anchor_id=target_anchor_id,
                target_location_id=target_location_id,
            )
            before = self._agent_snapshot(agent, presence, state)
            if state.get("phase") == "moving":
                self._advance_move(
                    world=world,
                    presence=presence,
                    agent=agent,
                    selected=selected,
                    state=state,
                    delta_seconds=delta_seconds,
                    events=events,
                )
            if state.get("phase") == "performing":
                self._advance_action(
                    selected=selected,
                    state=state,
                    delta_seconds=delta_seconds,
                    events=events,
                    completed_actions=completed_actions,
                )
            after = self._agent_snapshot(agent, presence, state)
            if after != before:
                agent_diffs.append(after)

        return {"events": events, "agents": agent_diffs, "completedActions": completed_actions}

    def _reset_state_if_needed(
        self,
        *,
        state: dict[str, Any],
        selected: dict[str, Any],
        current_anchor_id: str,
        target_anchor_id: str,
        target_location_id: str,
    ) -> None:
        action_id = str(selected.get("actionId") or "")
        changed = (
            state.get("actionId") != action_id
            or state.get("targetAnchorId") != target_anchor_id
            or state.get("targetLocationId") != target_location_id
        )
        if not changed:
            return
        state.clear()
        state.update(
            {
                "actionId": action_id,
                "targetAnchorId": target_anchor_id,
                "targetLocationId": target_location_id,
                "summary": str(selected.get("summary") or ""),
                "relatedNpcIds": list(selected.get("relatedNpcIds") or []),
                "phase": "performing" if current_anchor_id == target_anchor_id else "moving",
                "moveProgress": 0.0,
                "moveStarted": False,
                "actionStarted": False,
                "actionElapsedSeconds": 0.0,
                "actionDurationSeconds": self._duration_for_action(action_id),
                "actionTickAccumulator": 0.0,
            }
        )

    def _advance_move(
        self,
        *,
        world: dict[str, Any],
        presence: dict[str, Any],
        agent: dict[str, Any],
        selected: dict[str, Any],
        state: dict[str, Any],
        delta_seconds: float,
        events: list[dict[str, Any]],
    ) -> None:
        source_anchor_id = str(presence.get("anchorId") or "")
        source_location_id = str(presence.get("locationId") or "")
        target_anchor_id = str(state.get("targetAnchorId") or "")
        target_location_id = str(state.get("targetLocationId") or "")
        if not state.get("moveStarted"):
            state["moveStarted"] = True
            events.append(
                {
                    "type": "npc.move_started",
                    "npcId": str(selected.get("npcId") or ""),
                    "actionId": str(state.get("actionId") or ""),
                    "fromAnchorId": source_anchor_id,
                    "fromLocationId": source_location_id,
                    "toAnchorId": target_anchor_id,
                    "toLocationId": target_location_id,
                    "from": self._anchor_ref(world, source_anchor_id),
                    "to": self._anchor_ref(world, target_anchor_id),
                }
            )

        source_anchor = world.get("anchors", {}).get(source_anchor_id)
        target_anchor = world.get("anchors", {}).get(target_anchor_id)
        if not isinstance(source_anchor, dict) or not isinstance(target_anchor, dict):
            return
        distance = self._anchor_distance(source_anchor, target_anchor)
        if distance <= 0.0001:
            new_progress = 1.0
        else:
            progress_delta = (delta_seconds * MOVE_SPEED_PER_SECOND) / distance
            new_progress = min(1.0, float(state.get("moveProgress", 0.0)) + progress_delta)
        state["moveProgress"] = new_progress
        events.append(
            {
                "type": "npc.move_progress",
                "npcId": str(selected.get("npcId") or ""),
                "actionId": str(state.get("actionId") or ""),
                "fromAnchorId": source_anchor_id,
                "fromLocationId": source_location_id,
                "toAnchorId": target_anchor_id,
                "toLocationId": target_location_id,
                "progress": round(new_progress, 3),
            }
        )
        if new_progress < 1.0:
            return
        presence["anchorId"] = str(state.get("targetAnchorId") or "")
        presence["locationId"] = str(state.get("targetLocationId") or "")
        presence["intent"] = str(selected.get("summary") or "") or str(agent.get("currentIntent") or "")
        agent["anchorId"] = presence["anchorId"]
        agent["locationId"] = presence["locationId"]
        agent["currentIntent"] = presence["intent"]
        state["phase"] = "performing"
        events.append(
            {
                "type": "npc.arrived",
                "npcId": str(selected.get("npcId") or ""),
                "actionId": str(state.get("actionId") or ""),
                "anchorId": presence["anchorId"],
                "locationId": presence["locationId"],
            }
        )

    def _advance_action(
        self,
        *,
        selected: dict[str, Any],
        state: dict[str, Any],
        delta_seconds: float,
        events: list[dict[str, Any]],
        completed_actions: list[dict[str, Any]],
    ) -> None:
        npc_id = str(selected.get("npcId") or "")
        action_id = str(state.get("actionId") or "")
        duration = float(state.get("actionDurationSeconds") or DEFAULT_ACTION_DURATION_SECONDS)
        if not state.get("actionStarted"):
            state["actionStarted"] = True
            events.append(
                {
                    "type": "npc.action_started",
                    "npcId": npc_id,
                    "actionId": action_id,
                    "durationSeconds": duration,
                    "summary": str(state.get("summary") or ""),
                }
            )
        elapsed = min(duration, float(state.get("actionElapsedSeconds", 0.0)) + delta_seconds)
        state["actionElapsedSeconds"] = elapsed
        state["actionTickAccumulator"] = float(state.get("actionTickAccumulator", 0.0)) + delta_seconds
        if elapsed < duration and state["actionTickAccumulator"] >= ACTION_TICK_INTERVAL_SECONDS:
            state["actionTickAccumulator"] = 0.0
            events.append(
                {
                    "type": "npc.action_tick",
                    "npcId": npc_id,
                    "actionId": action_id,
                    "elapsedSeconds": round(elapsed, 2),
                    "progress": round(elapsed / duration, 3),
                }
            )
        if elapsed < duration:
            return
        events.append(
            {
                "type": "npc.action_completed",
                "npcId": npc_id,
                "actionId": action_id,
                "durationSeconds": duration,
            }
        )
        completed_actions.append(
            {
                "npcId": npc_id,
                "actionId": action_id,
                "summary": str(state.get("summary") or ""),
                "targetAnchorId": str(state.get("targetAnchorId") or ""),
                "targetLocationId": str(state.get("targetLocationId") or ""),
                "relatedNpcIds": deepcopy(state.get("relatedNpcIds") or []),
            }
        )
        state["actionStarted"] = False
        state["actionElapsedSeconds"] = 0.0
        state["actionTickAccumulator"] = 0.0

    def _duration_for_action(self, action_id: str) -> float:
        lowered = action_id.lower()
        for key, value in ACTION_DURATION_SECONDS.items():
            if key in lowered:
                return value
        if "chat" in lowered or "talk" in lowered:
            return ACTION_DURATION_SECONDS["chat_with"]
        if "farm" in lowered:
            return ACTION_DURATION_SECONDS["tend_farm"]
        if "shop" in lowered or "market" in lowered:
            return ACTION_DURATION_SECONDS["tend_shop"]
        return DEFAULT_ACTION_DURATION_SECONDS

    def _presence_index(self, world: dict[str, Any]) -> dict[str, dict[str, Any]]:
        index: dict[str, dict[str, Any]] = {}
        for presence in world.get("npcPresence", []):
            if not isinstance(presence, dict):
                continue
            npc_id = str(presence.get("agentId") or "")
            if npc_id:
                index[npc_id] = presence
        return index

    def _anchor_ref(self, world: dict[str, Any], anchor_id: str) -> dict[str, Any]:
        anchor = world.get("anchors", {}).get(anchor_id)
        if not isinstance(anchor, dict):
            return {"anchorId": anchor_id, "locationId": "", "screenPosition": {"x": 0.0, "y": 0.0}}
        return {
            "anchorId": anchor_id,
            "locationId": str(anchor.get("locationId") or ""),
            "screenPosition": deepcopy(anchor.get("screenPosition") or {"x": 0.0, "y": 0.0}),
        }

    def _anchor_distance(self, source_anchor: dict[str, Any], target_anchor: dict[str, Any]) -> float:
        source_pos = source_anchor.get("screenPosition") if isinstance(source_anchor.get("screenPosition"), dict) else {}
        target_pos = target_anchor.get("screenPosition") if isinstance(target_anchor.get("screenPosition"), dict) else {}
        source_offset = LOCATION_STAGE_OFFSETS.get(str(source_anchor.get("locationId") or ""), 0.0)
        target_offset = LOCATION_STAGE_OFFSETS.get(str(target_anchor.get("locationId") or ""), source_offset)
        source_x = source_offset + float(source_pos.get("x", 0.0))
        source_y = float(source_pos.get("y", 0.0))
        target_x = target_offset + float(target_pos.get("x", 0.0))
        target_y = float(target_pos.get("y", 0.0))
        return ((source_x - target_x) ** 2 + (source_y - target_y) ** 2) ** 0.5

    def _agent_snapshot(self, agent: dict[str, Any], presence: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        return {
            "npcId": str(agent.get("id") or ""),
            "locationId": str(presence.get("locationId") or agent.get("locationId") or ""),
            "anchorId": str(presence.get("anchorId") or agent.get("anchorId") or ""),
            "lifeAction": {
                "actionId": str(state.get("actionId") or ""),
                "phase": str(state.get("phase") or ""),
                "moveProgress": round(float(state.get("moveProgress", 0.0)), 3),
                "elapsedSeconds": round(float(state.get("actionElapsedSeconds", 0.0)), 2),
                "durationSeconds": round(float(state.get("actionDurationSeconds", 0.0)), 2),
            },
        }
