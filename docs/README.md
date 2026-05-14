# Agent Valley 文档索引

本目录用于沉淀 `ai-agent-town-lab` 从观察台原型升级为生活模拟游戏原型的核心共识。当前推进目标是把 `Agent Valley` 做成具备长期扩展能力的正式游戏骨架，首版垂直切片只是第一章可玩闭环。

## 推荐阅读顺序

1. [`project_vision.md`](./project_vision.md)：最高优先级推进依据，定义项目愿景、边界、成功标准和完整游戏推进原则。
2. [`current_status.md`](./current_status.md)：当前代码状态、可复用模块、主要缺口、开发前约束。
3. [`vertical_slice_spec.md`](./vertical_slice_spec.md)：第一版可玩切片规格、数据契约、验收边界和扩展性要求。
4. [`art_direction.md`](./art_direction.md)：二次元轻幻想轻异世界美术风格、角色设定、资产清单和生图顺序。
5. [`asset_generation_prompts.md`](./asset_generation_prompts.md)：首版生图提示词包，方便直接产出对接资产。
6. [`architecture_blueprint.md`](./architecture_blueprint.md)：整体架构、模块职责、数据流、客户端与后端协作方式。
7. [`implementation_plan.md`](./implementation_plan.md)：初版垂直切片执行方案、批次任务、验收标准。
8. [`open_questions.md`](./open_questions.md)：已确认决策、剩余验证点、下一轮讨论入口。

## 当前决策摘要

- 项目方向升级为“LLM 驱动 NPC 的二次元轻幻想轻异世界田园生活模拟 RPG 垂直切片”。
- 项目按正式游戏骨架推进，重要节点需要考虑后续 NPC、地点、事件、资产、系统玩法和 Debug 能力扩展。
- Python Agent Runtime 继续承担世界、Agent、记忆、事件、Provider 与调试记录。
- Godot 确定作为主要游戏客户端，负责地图、玩家操作、NPC 表现、对话与游戏 UI。
- 首版裁剪为 6 个 NPC、3 个地点、1 个完整游戏日和 1 个小镇事件。
- 玩家身份是新搬来的偏少女农场主，Debug / 研究控制台保留研究院视角。
- 首版同步推进可移动地图层和 Visual Novel 对话层，并开始恋爱铺垫。
- 首版直接接入 LLM 做测试，DeepSeek V4 Flash 作为优先低成本模型，RuleBasedProvider 保留为 fallback。
- 首版视觉路线采用二次元轻幻想轻异世界田园风，像素风暂时只作为小人占位或后续专项方向。
- 现有网页前端后续收敛为 Debug / 研究控制台。
- Codex 应用内生图能力用于开发期美术资产生产，游戏运行时不接入图片生成 API。

