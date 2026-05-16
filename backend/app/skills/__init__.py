"""事件技能数据结构与注册表。"""

from app.skills.event_skill_registry import (
    STARLIGHT_FESTIVAL_SHORTAGE_SKILL,
    STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID,
    find_event_choice_outcome,
    find_event_option,
    get_event_skill,
    list_event_skills,
)
from app.skills.event_skill_schema import (
    ConsequenceType,
    EventAssetHint,
    EventChoiceOutcome,
    EventConsequence,
    EventDialogueFallback,
    EventMemoryTemplate,
    EventParticipantDelta,
    EventPlayerOption,
    EventReflectionSeed,
    EventSkillSchema,
    EventSkillDebugField,
    EventTriggerCondition,
)

__all__ = [
    "ConsequenceType",
    "EventAssetHint",
    "EventChoiceOutcome",
    "EventConsequence",
    "EventDialogueFallback",
    "EventMemoryTemplate",
    "EventParticipantDelta",
    "EventPlayerOption",
    "EventReflectionSeed",
    "EventSkillSchema",
    "EventSkillDebugField",
    "EventTriggerCondition",
    "STARLIGHT_FESTIVAL_SHORTAGE_SKILL",
    "STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID",
    "find_event_choice_outcome",
    "find_event_option",
    "get_event_skill",
    "list_event_skills",
]
