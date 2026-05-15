from __future__ import annotations

from app.skills.event_skill_schema import (
    EventAssetHint,
    EventConsequence,
    EventParticipantDelta,
    EventPlayerOption,
    EventSkillSchema,
    EventTriggerCondition,
)

STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID = "event.starlight_festival_shortage"

STARLIGHT_FESTIVAL_SHORTAGE_SKILL = EventSkillSchema(
    skill_id=STARLIGHT_FESTIVAL_SHORTAGE_SKILL_ID,
    event_id="starlight_festival_shortage",
    title="星灯祭供应短缺",
    brief="月猫酒馆准备星灯祭前夜小聚时，食材紧缺引发凯娅与布兰娜的欠账争执。",
    trigger=EventTriggerCondition(
        phase="evening",
        location_id="tavern",
        required_status="available",
        required_active_event_id="starlight_festival_shortage",
    ),
    participants=("player", "kai", "bram", "mira", "lena", "orren", "tomas"),
    player_options=(
        EventPlayerOption(
            option_id="donate_crop",
            label="拿出新鲜芜菁帮酒馆渡过今晚",
            brief="玩家直接补齐食材，立刻缓解供应压力。",
            requires_player_item_id="fresh_turnip",
            consequences=(
                EventConsequence(
                    consequence_type="supply",
                    brief="食材短缺被立刻补上，庆典流程可以继续推进。",
                ),
                EventConsequence(
                    consequence_type="help",
                    brief="玩家同时安抚凯娅与布兰娜，冲突强度快速下降。",
                    deltas=(
                        EventParticipantDelta(participant_id="kai", affection=5, trust=4, conflict=-5),
                        EventParticipantDelta(participant_id="bram", affection=2, trust=3, conflict=-4),
                    ),
                ),
            ),
        ),
        EventPlayerOption(
            option_id="mediate",
            label="调解凯娅和布兰娜的欠账冲突",
            brief="玩家主持对话，优先稳定关系与后续供货秩序。",
            consequences=(
                EventConsequence(
                    consequence_type="help",
                    brief="双方接受先还款再供货的临时安排。",
                ),
                EventConsequence(
                    consequence_type="mediate",
                    brief="关系摩擦下降，镇民对玩家调解能力建立信任。",
                    deltas=(
                        EventParticipantDelta(participant_id="kai", affection=3, trust=4, conflict=-4),
                        EventParticipantDelta(participant_id="bram", affection=3, trust=4, conflict=-5),
                    ),
                ),
            ),
        ),
        EventPlayerOption(
            option_id="support_kai",
            label="优先支持凯娅维持节日气氛",
            brief="玩家偏向酒馆侧，让庆典氛围先保持热闹。",
            consequences=(
                EventConsequence(
                    consequence_type="atmosphere",
                    brief="节日现场情绪回暖，凯娅获得即时支持。",
                    deltas=(EventParticipantDelta(participant_id="kai", affection=5, trust=2, conflict=-2),),
                ),
                EventConsequence(
                    consequence_type="support",
                    brief="布兰娜对欠账问题更不满，后续供货关系更紧张。",
                    deltas=(EventParticipantDelta(participant_id="bram", affection=-1, trust=-1, conflict=4),),
                ),
            ),
        ),
        EventPlayerOption(
            option_id="support_bram",
            label="优先支持布兰娜守住供货底线",
            brief="玩家偏向农场侧，优先明确欠账与供货纪律。",
            consequences=(
                EventConsequence(
                    consequence_type="supply",
                    brief="供货底线被确认，后续补货风险下降。",
                    deltas=(EventParticipantDelta(participant_id="bram", affection=5, trust=3, conflict=-2),),
                ),
                EventConsequence(
                    consequence_type="stability",
                    brief="酒馆气氛短时降温，凯娅情绪出现反弹。",
                    deltas=(EventParticipantDelta(participant_id="kai", affection=-1, trust=0, conflict=3),),
                ),
            ),
        ),
        EventPlayerOption(
            option_id="observe",
            label="先旁观并记录大家的反应",
            brief="玩家收集现场信息，等待后续介入窗口。",
            consequences=(
                EventConsequence(
                    consequence_type="observe",
                    brief="玩家获得冲突全貌，核心矛盾被记录用于后续决策。",
                ),
                EventConsequence(
                    consequence_type="relationship",
                    brief="奥蕾娅和莉娜认可玩家保持克制，建立基础信任。",
                    deltas=(
                        EventParticipantDelta(participant_id="orren", trust=1),
                        EventParticipantDelta(participant_id="lena", trust=1),
                    ),
                ),
            ),
        ),
    ),
    asset_hints=(
        EventAssetHint(
            hint_id="starlight_shortage_scene",
            asset_type="event_scene",
            brief="月猫酒馆夜景，祭灯、空食材箱、争执中的凯娅与布兰娜。",
            tags=("festival", "night", "supply_shortage", "tavern"),
        ),
        EventAssetHint(
            hint_id="starlight_shortage_ui_card",
            asset_type="ui_event_card",
            brief="事件卡面包含供应告急标识、酒馆与农场对立信息。",
            tags=("event_card", "supply", "decision"),
        ),
        EventAssetHint(
            hint_id="starlight_shortage_choice_icons",
            asset_type="icon_set",
            brief="为捐赠、调解、站队、观察四类选项准备视觉图标。",
            tags=("choice", "donate", "mediate", "observe"),
        ),
    ),
)

_EVENT_SKILL_REGISTRY: dict[str, EventSkillSchema] = {
    STARLIGHT_FESTIVAL_SHORTAGE_SKILL.skill_id: STARLIGHT_FESTIVAL_SHORTAGE_SKILL,
}


def list_event_skills() -> tuple[EventSkillSchema, ...]:
    """返回已注册事件技能列表。"""
    return tuple(_EVENT_SKILL_REGISTRY.values())


def get_event_skill(skill_id: str) -> EventSkillSchema:
    """按 skill id 获取事件技能定义。"""
    try:
        return _EVENT_SKILL_REGISTRY[skill_id]
    except KeyError as error:
        raise KeyError(f"未知事件技能：{skill_id}") from error


def find_event_option(skill_id: str, option_id: str) -> EventPlayerOption:
    """按选项 id 读取玩家选项，供 attend_event 参数校验与 UI 使用。"""
    skill = get_event_skill(skill_id)
    for option in skill.player_options:
        if option.option_id == option_id:
            return option
    raise KeyError(f"事件技能 {skill_id} 中不存在选项：{option_id}")
