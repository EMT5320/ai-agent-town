# Agent Valley 文档索引

本目录用于沉淀 `ai-agent-town-lab` 从观察台原型升级为生活模拟游戏原型的核心共识。当前推进目标是把 `Agent Valley` 做成具备长期扩展能力的正式游戏骨架，首版垂直切片只是第一章可玩闭环。

## 推荐阅读顺序

1. [`project_vision.md`](./project_vision.md)：最高优先级推进依据，定义项目愿景、边界、成功标准和完整游戏推进原则。
2. [`agentic_game_design.md`](./agentic_game_design.md)：多层 Agent 游戏系统定调，定义 Director System、Event Skill、异步 Director Beat、记忆/RAG 和模型分工。
3. [`gameplay_system_architecture.md`](./gameplay_system_architecture.md)：游戏本体架构定调，定义地图主循环、软日程 NPC、玩法系统闭环和 Godot / 后端边界。
4. [`current_status.md`](./current_status.md)：当前代码状态、可复用模块、主要缺口、开发前约束。
5. [`daytime_integration_handoff.md`](./daytime_integration_handoff.md)：2026-05-16 白天整合结果、验收证据和晚上客户端 / LLM 线开工目标。
6. [`vertical_slice_spec.md`](./vertical_slice_spec.md)：第一版可玩切片规格、数据契约、验收边界和扩展性要求。
7. [`art_direction.md`](./art_direction.md)：二次元轻幻想轻异世界美术风格、角色设定、资产清单和生图顺序。
8. [`asset_generation_prompts.md`](./asset_generation_prompts.md)：首版生图提示词包，方便直接产出对接资产。
9. [`initial_asset_generation_plan.md`](./initial_asset_generation_plan.md)：正式资产生成批次、优先级和 Godot 接入路线。
10. [`architecture_blueprint.md`](./architecture_blueprint.md)：整体架构、模块职责、数据流、客户端与后端协作方式。
11. [`implementation_plan.md`](./implementation_plan.md)：初版垂直切片执行方案、批次任务、验收标准。
12. [`open_questions.md`](./open_questions.md)：已确认决策、剩余验证点、下一轮讨论入口。

## 当前决策摘要

- 项目方向升级为“LLM 驱动 NPC 的二次元轻幻想轻异世界田园生活模拟 RPG 垂直切片”。
- 核心系统定调为“多层 Agent 游戏系统”：World / Simulation 层持有权威状态，Director System 低频规划节奏和事件 Skill，NPC Agents 在自身记忆与 brief 内自主行动。
- 游戏本体定调为“涌现式田园生活模拟”：玩家主要在地图上移动、靠近对象并触发交互；NPC 出现和行动由软日程权重、世界约束、导演层节奏、Event Skill 和 NPC 自主判断共同生成。
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
- 2026-05-16 白天整合后，后端 agent 线和地图小人资产线已进入 `main`；地图小人仍需 Godot 实机窗口确认后再晋级正式资产状态。
- 现有网页前端后续收敛为 Debug / 研究控制台。
- Codex 应用内生图能力用于开发期美术资产生产，游戏运行时不接入图片生成 API。
