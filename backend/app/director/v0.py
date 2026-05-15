from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence
from uuid import uuid4


@dataclass(slots=True)
class WorldDigest:
    """Director 使用的世界摘要，保持轻量并便于在 runtime 中构建。"""

    world_version: int
    tick: int
    living_agent_ids: tuple[str, ...]
    active_event_count: int
    avg_stress: float

    @classmethod
    def from_world(cls, world: Mapping[str, Any]) -> "WorldDigest":
        """从现有 world_state 快速提取调度关键信息。"""
        clock = world.get("clock") if isinstance(world.get("clock"), Mapping) else {}
        agents = world.get("agents") if isinstance(world.get("agents"), Mapping) else {}
        active_events = world.get("activeEvents") if isinstance(world.get("activeEvents"), Sequence) else []

        living_ids: list[str] = []
        stress_values: list[float] = []
        for agent_id, raw_agent in agents.items():
            if not isinstance(raw_agent, Mapping):
                continue
            if raw_agent.get("alive", True):
                living_ids.append(str(agent_id))
            status = raw_agent.get("status")
            if isinstance(status, Mapping):
                stress_values.append(float(status.get("stress", 0.0)))

        avg_stress = (sum(stress_values) / len(stress_values)) if stress_values else 0.0
        raw_world_version = world.get("worldVersion", world.get("world_version", 0))
        return cls(
            world_version=int(raw_world_version),
            tick=int(clock.get("tick", 0)),
            living_agent_ids=tuple(living_ids),
            active_event_count=len(active_events),
            avg_stress=avg_stress,
        )


@dataclass(slots=True)
class TensionSignal:
    """紧张度检测输出，供 SkillRouter 和后续策略层消费。"""

    level: str
    score: int
    evidence: dict[str, Any] = field(default_factory=dict)


class TensionDetector:
    """规则版紧张度检测器，先用可解释规则，后续可替换为模型。"""

    def detect(self, digest: WorldDigest) -> TensionSignal:
        """根据摘要输出 low / medium / high 三档紧张度。"""
        score = 0
        if digest.avg_stress >= 70:
            score += 2
        elif digest.avg_stress >= 45:
            score += 1

        if digest.active_event_count >= 3:
            score += 1

        if score >= 3:
            level = "high"
        elif score >= 1:
            level = "medium"
        else:
            level = "low"

        return TensionSignal(
            level=level,
            score=score,
            evidence={
                "avgStress": digest.avg_stress,
                "activeEventCount": digest.active_event_count,
                "livingAgentCount": len(digest.living_agent_ids),
            },
        )


class SkillRouter:
    """将紧张度映射到规则技能集合，保持接口简单。"""

    _level_to_skills: dict[str, tuple[str, ...]] = {
        "high": ("deescalate_conflict", "supportive_dialogue"),
        "medium": ("social_visit", "quest_hint"),
        "low": ("routine_chat", "daily_routine"),
    }

    def route(
        self,
        tension: TensionSignal,
        target_agents: Sequence[str],
        candidate_skills: Sequence[str] | None = None,
    ) -> list[str]:
        """返回可分配给目标 Agent 的技能名列表。"""
        _ = target_agents  # v0 先保留参数，后续可按角色画像细分。
        default_skills = list(self._level_to_skills.get(tension.level, ("routine_chat",)))
        if candidate_skills is None:
            return default_skills

        candidate_set = {str(skill) for skill in candidate_skills}
        return [skill for skill in default_skills if skill in candidate_set]


@dataclass(slots=True)
class DirectorBeat:
    """Director 下发给主代理的调度单元。"""

    worldVersion: int
    validFromTick: int
    expiresAtTick: int
    targetAgents: list[str]
    allowedSkills: list[str]
    beatType: str = "activate_event_skill"
    beatId: str = field(default_factory=lambda: f"beat_{uuid4().hex}")
    payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "DirectorBeat":
        """兼容 dict 输入，方便从 API 或持久层恢复。"""
        return cls(
            beatType=str(data.get("beatType") or data.get("type") or "activate_event_skill"),
            beatId=str(data.get("beatId") or f"beat_{uuid4().hex}"),
            worldVersion=int(data.get("worldVersion", 0)),
            validFromTick=int(data.get("validFromTick", 0)),
            expiresAtTick=int(data.get("expiresAtTick", 0)),
            targetAgents=[str(agent_id) for agent_id in data.get("targetAgents", [])],
            allowedSkills=[str(skill) for skill in data.get("allowedSkills", [])],
            payload=dict(data.get("payload", {})) if isinstance(data.get("payload"), Mapping) else {},
        )

    def to_dict(self) -> dict[str, Any]:
        """输出稳定字典结构，便于 EventStore 或 API 透传。"""
        return {
            "beatId": self.beatId,
            "beatType": self.beatType,
            "worldVersion": self.worldVersion,
            "validFromTick": self.validFromTick,
            "expiresAtTick": self.expiresAtTick,
            "targetAgents": list(self.targetAgents),
            "allowedSkills": list(self.allowedSkills),
            "payload": dict(self.payload),
        }


@dataclass(slots=True)
class DirectorValidationResult:
    """Beat 校验输出。"""

    ok: bool
    errors: list[str] = field(default_factory=list)


class DirectorValidator:
    """统一校验入口，确保 beat 合法后再入队。"""

    def __init__(self, allowed_skill_registry: Sequence[str] | None = None, valid_target_agents: Sequence[str] | None = None) -> None:
        self.allowed_skill_registry = {str(skill) for skill in allowed_skill_registry} if allowed_skill_registry else None
        self.valid_target_agents = {str(agent_id) for agent_id in valid_target_agents} if valid_target_agents else None

    def validate(self, beat: DirectorBeat, current_world_version: int | None = None) -> DirectorValidationResult:
        """覆盖 v0 必需字段与基础约束。"""
        errors: list[str] = []

        if not beat.beatType:
            errors.append("beatType must not be empty")
        if beat.worldVersion < 0:
            errors.append("worldVersion must be >= 0")
        if beat.validFromTick < 0:
            errors.append("validFromTick must be >= 0")
        if beat.expiresAtTick < beat.validFromTick:
            errors.append("expiresAtTick must be >= validFromTick")

        if not beat.targetAgents:
            errors.append("targetAgents must not be empty")
        elif any(not isinstance(agent_id, str) or not agent_id for agent_id in beat.targetAgents):
            errors.append("targetAgents must contain non-empty string")

        if not beat.allowedSkills:
            errors.append("allowedSkills must not be empty")
        elif any(not isinstance(skill, str) or not skill for skill in beat.allowedSkills):
            errors.append("allowedSkills must contain non-empty string")

        if self.allowed_skill_registry is not None:
            unknown_skills = [skill for skill in beat.allowedSkills if skill not in self.allowed_skill_registry]
            if unknown_skills:
                errors.append(f"allowedSkills contains unknown skill: {','.join(unknown_skills)}")

        if self.valid_target_agents is not None:
            unknown_agents = [agent_id for agent_id in beat.targetAgents if agent_id not in self.valid_target_agents]
            if unknown_agents:
                errors.append(f"targetAgents contains unknown agent: {','.join(unknown_agents)}")

        if current_world_version is not None and beat.worldVersion != current_world_version:
            errors.append("worldVersion does not match current world version")

        return DirectorValidationResult(ok=not errors, errors=errors)


@dataclass(slots=True)
class DirectorBeatDiscard:
    """被丢弃 beat 的原因记录，供 EventStore 写 director.beat_discarded。"""

    beat: DirectorBeat
    reason: str
    detail: str

    def to_event_payload(self) -> dict[str, Any]:
        """转换为事件载荷。"""
        payload = self.beat.to_dict()
        payload.update({"reason": self.reason, "detail": self.detail})
        return payload


@dataclass(slots=True)
class EnqueueResult:
    """入队结果。"""

    accepted: bool
    beat: DirectorBeat | None = None
    discarded: DirectorBeatDiscard | None = None


@dataclass(slots=True)
class ConsumeResult:
    """消费结果。"""

    ready: list[DirectorBeat] = field(default_factory=list)
    discarded: list[DirectorBeatDiscard] = field(default_factory=list)


class DirectorQueueManager:
    """Director beat 队列：负责入队、消费、过期与版本冲突清理。"""

    def __init__(self, validator: DirectorValidator | None = None) -> None:
        self.validator = validator or DirectorValidator()
        self._pending: list[DirectorBeat] = []

    @property
    def pending(self) -> tuple[DirectorBeat, ...]:
        """只读查看当前待消费队列。"""
        return tuple(self._pending)

    def enqueue(self, beat: DirectorBeat | Mapping[str, Any], current_world_version: int | None = None) -> EnqueueResult:
        """入队时做结构校验，失败会返回可落事件的丢弃原因。"""
        normalized_beat = DirectorBeat.from_dict(beat) if isinstance(beat, Mapping) else beat
        validation = self.validator.validate(normalized_beat, current_world_version=current_world_version)
        if not validation.ok:
            discard = DirectorBeatDiscard(
                beat=normalized_beat,
                reason="validation_failed",
                detail="; ".join(validation.errors),
            )
            return EnqueueResult(accepted=False, discarded=discard)

        self._pending.append(normalized_beat)
        return EnqueueResult(accepted=True, beat=normalized_beat)

    def consume(self, digest: WorldDigest) -> ConsumeResult:
        """消费当前 tick 可执行 beat，并清理过期或版本不匹配项。"""
        ready: list[DirectorBeat] = []
        discarded: list[DirectorBeatDiscard] = []
        remained: list[DirectorBeat] = []

        for beat in self._pending:
            if beat.worldVersion != digest.world_version:
                discarded.append(
                    DirectorBeatDiscard(
                        beat=beat,
                        reason="world_version_mismatch",
                        detail=f"beat={beat.worldVersion}, current={digest.world_version}",
                    )
                )
                continue

            if beat.expiresAtTick < digest.tick:
                discarded.append(
                    DirectorBeatDiscard(
                        beat=beat,
                        reason="expired",
                        detail=f"expiresAtTick={beat.expiresAtTick}, currentTick={digest.tick}",
                    )
                )
                continue

            if beat.validFromTick <= digest.tick <= beat.expiresAtTick:
                ready.append(beat)
                continue

            remained.append(beat)

        self._pending = remained
        return ConsumeResult(ready=ready, discarded=discarded)
