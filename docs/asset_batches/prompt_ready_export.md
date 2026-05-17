---
status: active
owner_lane: asset-pipeline
last_verified: 2026-05-17
startup_load: on-demand
source_of_truth: false
scope: prompt_ready batch execution and manual review checklist
---

# prompt_ready 资产批次导出清单

> 导出日期：2026-05-17。
> 说明：本清单只覆盖 `status=prompt_ready` 的 backlog，未声明任何已生成结果。

## 使用步骤

1. 先按 `batchId` 逐批次执行生图。
2. 每张图通过人工筛选后再更新 manifest 状态。
3. 仅在源图真实存在且评审通过时写入 `processedPath` 与 `godotPath`。

## batch-8a-expression-delta

| 资产ID | 用途 | Prompt 锚点 | Godot 目标路径 | Godot 接入槽位 | 人工筛选 |
| --- | --- | --- | --- | --- | --- |
| `player_farmer_happy` | `dialogue_portrait` | `docs/asset_generation_prompts.md#batch-8-expression-delta` | `res://assets/characters/player_farmer_happy.png` | `asset_registry.portraits.player.happy` | ☐ 待筛选 |
| `player_farmer_troubled` | `dialogue_portrait` | `docs/asset_generation_prompts.md#batch-8-expression-delta` | `res://assets/characters/player_farmer_troubled.png` | `asset_registry.portraits.player.troubled` | ☐ 待筛选 |
| `npc_mira_happy` | `dialogue_portrait` | `docs/asset_generation_prompts.md#batch-8-expression-delta` | `res://assets/characters/npc_mira_happy.png` | `asset_registry.portraits.mira.happy` | ☐ 待筛选 |
| `npc_mira_troubled` | `dialogue_portrait` | `docs/asset_generation_prompts.md#batch-8-expression-delta` | `res://assets/characters/npc_mira_troubled.png` | `asset_registry.portraits.mira.troubled` | ☐ 待筛选 |
| `npc_tomas_happy` | `dialogue_portrait` | `docs/asset_generation_prompts.md#batch-8-expression-delta` | `res://assets/characters/npc_tomas_happy.png` | `asset_registry.portraits.tomas.happy` | ☐ 待筛选 |
| `npc_tomas_troubled` | `dialogue_portrait` | `docs/asset_generation_prompts.md#batch-8-expression-delta` | `res://assets/characters/npc_tomas_troubled.png` | `asset_registry.portraits.tomas.troubled` | ☐ 待筛选 |
| `npc_orren_happy` | `dialogue_portrait` | `docs/asset_generation_prompts.md#batch-8-expression-delta` | `res://assets/characters/npc_orren_happy.png` | `asset_registry.portraits.orren.happy` | ☐ 待筛选 |
| `npc_orren_troubled` | `dialogue_portrait` | `docs/asset_generation_prompts.md#batch-8-expression-delta` | `res://assets/characters/npc_orren_troubled.png` | `asset_registry.portraits.orren.troubled` | ☐ 待筛选 |
| `npc_lena_happy` | `dialogue_portrait` | `docs/asset_generation_prompts.md#batch-8-expression-delta` | `res://assets/characters/npc_lena_happy.png` | `asset_registry.portraits.lena.happy` | ☐ 待筛选 |
| `npc_lena_troubled` | `dialogue_portrait` | `docs/asset_generation_prompts.md#batch-8-expression-delta` | `res://assets/characters/npc_lena_troubled.png` | `asset_registry.portraits.lena.troubled` | ☐ 待筛选 |
| `npc_kai_happy` | `dialogue_portrait` | `docs/asset_generation_prompts.md#batch-8-expression-delta` | `res://assets/characters/npc_kai_happy.png` | `asset_registry.portraits.kai.happy` | ☐ 待筛选 |
| `npc_kai_troubled` | `dialogue_portrait` | `docs/asset_generation_prompts.md#batch-8-expression-delta` | `res://assets/characters/npc_kai_troubled.png` | `asset_registry.portraits.kai.troubled` | ☐ 待筛选 |
| `npc_bram_happy` | `dialogue_portrait` | `docs/asset_generation_prompts.md#batch-8-expression-delta` | `res://assets/characters/npc_bram_happy.png` | `asset_registry.portraits.bram.happy` | ☐ 待筛选 |
| `npc_bram_troubled` | `dialogue_portrait` | `docs/asset_generation_prompts.md#batch-8-expression-delta` | `res://assets/characters/npc_bram_troubled.png` | `asset_registry.portraits.bram.troubled` | ☐ 待筛选 |

### 批次内执行检查

- [ ] 角色身份和风格与 `neutral/reference` 一致。
- [ ] 64x64 / 32x32 可读性检查（图标与 UI 组件必做）。
- [ ] 无水印、无不可控文字、透明背景可用。
- [ ] 通过后再推进 Godot 接入路径与槽位。

## batch-8b-action-feedback-icons

| 资产ID | 用途 | Prompt 锚点 | Godot 目标路径 | Godot 接入槽位 | 人工筛选 |
| --- | --- | --- | --- | --- | --- |
| `action_feedback_move` | `move_feedback` | `docs/asset_generation_prompts.md#batch-8-action-feedback-icons` | `res://assets/icons/action_feedback_move.png` | `asset_registry.action_feedback.move_feedback` | ☐ 待筛选 |
| `action_feedback_talk` | `talk_feedback` | `docs/asset_generation_prompts.md#batch-8-action-feedback-icons` | `res://assets/icons/action_feedback_talk.png` | `asset_registry.action_feedback.talk_feedback` | ☐ 待筛选 |
| `action_feedback_gift` | `gift_feedback` | `docs/asset_generation_prompts.md#batch-8-action-feedback-icons` | `res://assets/icons/action_feedback_gift.png` | `asset_registry.action_feedback.gift_feedback` | ☐ 待筛选 |
| `action_feedback_inspect` | `inspect_feedback` | `docs/asset_generation_prompts.md#batch-8-action-feedback-icons` | `res://assets/icons/action_feedback_inspect.png` | `asset_registry.action_feedback.inspect_feedback` | ☐ 待筛选 |
| `action_feedback_event` | `event_feedback` | `docs/asset_generation_prompts.md#batch-8-action-feedback-icons` | `res://assets/icons/action_feedback_event.png` | `asset_registry.action_feedback.event_feedback` | ☐ 待筛选 |

### 批次内执行检查

- [ ] 角色身份和风格与 `neutral/reference` 一致。
- [ ] 64x64 / 32x32 可读性检查（图标与 UI 组件必做）。
- [ ] 无水印、无不可控文字、透明背景可用。
- [ ] 通过后再推进 Godot 接入路径与槽位。

## batch-8c-life-ui-widgets

| 资产ID | 用途 | Prompt 锚点 | Godot 目标路径 | Godot 接入槽位 | 人工筛选 |
| --- | --- | --- | --- | --- | --- |
| `ui_life_action_button_farm` | `life_action_button` | `docs/asset_generation_prompts.md#batch-8-life-ui-widgets` | `res://assets/ui/ui_life_action_button_farm.png` | `asset_registry.life_ui.ui_life_action_button_farm` | ☐ 待筛选 |
| `ui_life_action_button_chat` | `life_action_button` | `docs/asset_generation_prompts.md#batch-8-life-ui-widgets` | `res://assets/ui/ui_life_action_button_chat.png` | `asset_registry.life_ui.ui_life_action_button_chat` | ☐ 待筛选 |
| `ui_life_action_button_rest` | `life_action_button` | `docs/asset_generation_prompts.md#batch-8-life-ui-widgets` | `res://assets/ui/ui_life_action_button_rest.png` | `asset_registry.life_ui.ui_life_action_button_rest` | ☐ 待筛选 |
| `ui_life_action_schedule_strip` | `life_action_schedule` | `docs/asset_generation_prompts.md#batch-8-life-ui-widgets` | `res://assets/ui/ui_life_action_schedule_strip.png` | `asset_registry.life_ui.ui_life_action_schedule_strip` | ☐ 待筛选 |
| `ui_life_action_result_toast` | `life_action_feedback` | `docs/asset_generation_prompts.md#batch-8-life-ui-widgets` | `res://assets/ui/ui_life_action_result_toast.png` | `asset_registry.life_ui.ui_life_action_result_toast` | ☐ 待筛选 |

### 批次内执行检查

- [ ] 角色身份和风格与 `neutral/reference` 一致。
- [ ] 64x64 / 32x32 可读性检查（图标与 UI 组件必做）。
- [ ] 无水印、无不可控文字、透明背景可用。
- [ ] 通过后再推进 Godot 接入路径与槽位。
