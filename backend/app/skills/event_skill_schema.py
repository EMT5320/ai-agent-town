from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ConsequenceType = Literal[
    "supply",
    "help",
    "mediate",
    "support",
    "observe",
    "relationship",
    "atmosphere",
    "stability",
]


@dataclass(frozen=True, slots=True)
class EventTriggerCondition:
    """事件可触发条件，供 Runtime 或调试面板读取。"""

    phase: str
    location_id: str
    required_status: str = "available"
    required_active_event_id: str | None = None


@dataclass(frozen=True, slots=True)
class EventParticipantDelta:
    """选项对参与者关系产生的增减预览。"""

    participant_id: str
    affection: int = 0
    trust: int = 0
    conflict: int = 0


@dataclass(frozen=True, slots=True)
class EventConsequence:
    """事件选项可视化后果结构，可映射 supply/help 等语义。"""

    consequence_type: ConsequenceType
    brief: str
    deltas: tuple[EventParticipantDelta, ...] = ()


@dataclass(frozen=True, slots=True)
class EventPlayerOption:
    """玩家可见选项定义，保留和 attend_event 结算可映射的 id。"""

    option_id: str
    label: str
    brief: str
    consequences: tuple[EventConsequence, ...]
    requires_player_item_id: str | None = None


@dataclass(frozen=True, slots=True)
class EventAssetHint:
    """客户端或工具链可用的资源提示。"""

    hint_id: str
    asset_type: str
    brief: str
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EventSkillSchema:
    """事件技能定义。"""

    skill_id: str
    event_id: str
    title: str
    brief: str
    trigger: EventTriggerCondition
    participants: tuple[str, ...]
    player_options: tuple[EventPlayerOption, ...]
    asset_hints: tuple[EventAssetHint, ...]
