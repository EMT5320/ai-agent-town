---
status: active
owner_lane: context-governance
last_verified: 2026-05-16
startup_load: index
source_of_truth: true
scope: 文档分层索引与渐进式读取路线
---

# Agent Valley 文档索引

本目录用于沉淀 `ai-agent-town-lab` 从观察台原型升级为生活模拟游戏原型的核心共识。当前治理原则是：新对话先读短入口，再按任务线渐进加载源文档。

## 1. 新对话最小读取

1. [`../AGENTS.md`](../AGENTS.md)：所有开发助手共享的启动协议、任务线路由和验收规则。
2. [`agent_context.md`](./agent_context.md)：下一轮对话第一入口，记录当前边界、命令和最近下一步。
3. [`current_status.md`](./current_status.md)：当前实现事实、主要缺口、开发前硬性约束和人工验收清单。
4. [`goal_board.md`](./goal_board.md)：开发线看板、写入范围、并行任务拆分和交接格式。

## 2. 决策源文档

- [`project_vision.md`](./project_vision.md)：最高优先级产品愿景，定义长期方向、体验目标和成功标准。
- [`open_questions.md`](./open_questions.md)：已确认决策、剩余问题和实现中验证点。
- [`vertical_slice_spec.md`](./vertical_slice_spec.md)：第一版可玩切片规格、数据契约、验收边界和扩展性要求。

## 3. 按开发线读取

### Backend / Director / Event Skill

- [`agentic_game_design.md`](./agentic_game_design.md)：多层 Agent 游戏系统定调，覆盖 Director System、Event Skill、异步 Director Beat、记忆/RAG 和模型分工。
- [`architecture_blueprint.md`](./architecture_blueprint.md)：整体架构、模块职责、数据流、客户端与后端协作方式。
- [`vertical_slice_spec.md`](./vertical_slice_spec.md)：事件、对话、世界状态和切片验收边界。

### Godot 客户端

- [`gameplay_system_architecture.md`](./gameplay_system_architecture.md)：游戏本体架构、地图主循环、软日程 NPC、玩法系统闭环和 Godot / 后端边界。
- [`game_client_environment.md`](./game_client_environment.md)：Godot 客户端环境、启动方式和检查命令。
- [`../clients/godot/README.md`](../clients/godot/README.md)：Godot 工程本地说明。

### 内容 / NPC 深度卡

- [`game_content_storyline.md`](./game_content_storyline.md)：游戏内容、第一天剧情和小镇叙事线。
- [`npc_deep_card_spec.md`](./npc_deep_card_spec.md)：NPC 深度卡字段、写作规范和验证重点。

### LLM / Debug

- [`model_profile_template_guide.md`](./model_profile_template_guide.md)：模型 profile、本地覆盖文件和配置模板。
- [`agentic_game_design.md`](./agentic_game_design.md)：模型分工、低频强模型规划和 NPC 运行策略。

### 资产管线

- [`art_direction.md`](./art_direction.md)：二次元轻幻想轻异世界美术风格、角色设定、资产清单和生图顺序。
- [`asset_generation_prompts.md`](./asset_generation_prompts.md)：首版生图提示词包。
- [`initial_asset_generation_plan.md`](./initial_asset_generation_plan.md)：正式资产生成批次、优先级和 Godot 接入路线。
- [`map_sprite_style_guide.md`](./map_sprite_style_guide.md)：地图小人风格规则。
- [`map_sprite_first_batch_review.md`](./map_sprite_first_batch_review.md)、[`map_sprite_second_batch_review.md`](./map_sprite_second_batch_review.md)：小人资产批次复盘。

### 上下文治理 / 助手适配

- [`skill_strategy.md`](./skill_strategy.md)：项目专用 Skill 策略草案。
- [`../CLAUDE.md`](../CLAUDE.md)：Claude Code 适配层，导入根目录 `AGENTS.md`。
- [`../.claude/rules/`](../.claude/rules/)：Claude Code 路径规则，按 docs、backend、Godot、assets 渐进加载。
- [`../scripts/build_agent_context.py`](../scripts/build_agent_context.py)：上下文 brief 生成和治理校验脚本。

## 4. 历史快照

- [`implementation_plan.md`](./implementation_plan.md)：初版垂直切片执行方案和批次任务，读取时需结合 `current_status.md` 判断是否过期。
- [`daytime_integration_handoff.md`](./daytime_integration_handoff.md)：2026-05-16 白天整合结果和当时验收证据，作为阶段快照使用。
- 根目录 [`README.md`](../README.md)：保留早期观察台阶段和项目演进背景，当前事实以 `docs/current_status.md` 为准。

## 5. 文档状态表

| 文档 | 状态 | 开发线 | 加载策略 | 事实源 |
| --- | --- | --- | --- | --- |
| [`agent_context.md`](./agent_context.md) | active | context-governance | first-read | true |
| [`agentic_game_design.md`](./agentic_game_design.md) | active | backend-director | on-demand | true |
| [`architecture_blueprint.md`](./architecture_blueprint.md) | active | architecture | on-demand | true |
| [`art_direction.md`](./art_direction.md) | active | asset-pipeline | on-demand | true |
| [`asset_generation_prompts.md`](./asset_generation_prompts.md) | active | asset-pipeline | on-demand | true |
| [`current_status.md`](./current_status.md) | active | project-status | after-agent-context | true |
| [`daytime_integration_handoff.md`](./daytime_integration_handoff.md) | snapshot | handoff | on-demand | false |
| [`game_client_environment.md`](./game_client_environment.md) | active | godot-client | on-demand | true |
| [`game_content_storyline.md`](./game_content_storyline.md) | active | content-codex | on-demand | true |
| [`gameplay_system_architecture.md`](./gameplay_system_architecture.md) | active | godot-client | on-demand | true |
| [`goal_board.md`](./goal_board.md) | active | planning | after-agent-context | true |
| [`implementation_plan.md`](./implementation_plan.md) | snapshot | planning | on-demand | false |
| [`initial_asset_generation_plan.md`](./initial_asset_generation_plan.md) | snapshot | asset-pipeline | on-demand | false |
| [`map_sprite_first_batch_review.md`](./map_sprite_first_batch_review.md) | snapshot | asset-pipeline | on-demand | false |
| [`map_sprite_second_batch_review.md`](./map_sprite_second_batch_review.md) | snapshot | asset-pipeline | on-demand | false |
| [`map_sprite_style_guide.md`](./map_sprite_style_guide.md) | active | asset-pipeline | on-demand | true |
| [`model_profile_template_guide.md`](./model_profile_template_guide.md) | active | llm-debug | on-demand | true |
| [`npc_deep_card_spec.md`](./npc_deep_card_spec.md) | active | content-codex | on-demand | true |
| [`open_questions.md`](./open_questions.md) | active | decisions | on-demand | true |
| [`project_vision.md`](./project_vision.md) | active | vision | on-demand | true |
| [`README.md`](./README.md) | active | context-governance | index | true |
| [`skill_strategy.md`](./skill_strategy.md) | active | context-governance | on-demand | false |
| [`vertical_slice_spec.md`](./vertical_slice_spec.md) | active | architecture | on-demand | true |

说明：`active` 可作为当前参考，`snapshot` 只代表当时阶段证据；`source_of_truth=false` 的文档不得覆盖当前状态文档或对应 active 规格。

## 6. 当前决策摘要

- 项目方向升级为“LLM 驱动 NPC 的二次元轻幻想轻异世界田园生活模拟 RPG 垂直切片”。
- 核心系统定调为“多层 Agent 游戏系统”：World / Simulation 层持有权威状态，Director System 低频规划节奏和事件 Skill，NPC Agents 在自身记忆与 brief 内自主行动。
- 游戏本体定调为“涌现式田园生活模拟”：玩家在地图上移动、靠近对象并触发交互；NPC 出现和行动由软日程权重、世界约束、导演层节奏、Event Skill 和 NPC 自主判断共同生成。
- 项目按正式游戏骨架推进，重要节点需要考虑后续 NPC、地点、事件、资产、系统玩法和 Debug 能力扩展。
- Python Agent Runtime 继续承担世界、Agent、记忆、事件、Provider 与调试记录。
- 事件按 Skill 渐进式加载：平时只暴露触发条件，满足条件后加载完整事件 brief、工具、约束、后果类型和资产提示。
- 导演层定位为异步节奏规划器，生成可验证、可过期的 Director Beat；强模型只用于低频高价值规划。
- Godot 确定作为主要游戏客户端，负责地图、玩家操作、NPC 表现、对话与游戏 UI。
- 首版裁剪为 6 个 NPC、3 个地点、1 个完整游戏日和 1 个小镇事件。
- 首版 NPC 性别比例为 5 女 1 男，只保留托玛·榆庭作为男性首发 NPC；后续扩展默认女性占多数，并自然支持多元家庭和配偶关系。
- 玩家身份是新搬来的偏少女农场主，Debug / 研究控制台保留研究院视角。
- 首版同步推进可移动地图层和 Visual Novel 对话层，并开始恋爱铺垫。
- 首版直接接入 LLM 做测试，DeepSeek V4 Flash 作为优先低成本模型，RuleBasedProvider 保留为 fallback。
- 首版视觉路线采用二次元轻幻想轻异世界田园风，像素风暂时只作为小人占位或后续专项方向。
- 现有网页前端后续收敛为 Debug / 研究控制台。
- Codex 应用内生图能力用于开发期美术资产生产，游戏运行时不接入图片生成 API。

## 7. 文档维护规则

- `agent_context.md` 保持短入口，不堆长篇设计。
- `current_status.md` 只写当前已核对事实，未人工验收内容必须显式标注。
- `goal_board.md` 记录当前开发线、验收证据和下一轮排程。
- 长期愿景和阶段事实冲突时，先更新事实文档，再决定是否需要修订愿景或规格。
- 每次调整上下文治理后运行：

```powershell
npm.cmd run context:check
git diff --check
```
