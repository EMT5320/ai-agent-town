# Agent Valley 文档索引

本目录用于沉淀 `ai-agent-town-lab` 从观察台原型升级为生活模拟游戏原型的核心共识。

## 推荐阅读顺序

1. [`project_vision.md`](./project_vision.md)：最高优先级推进依据，定义项目愿景、边界、成功标准。
2. [`architecture_blueprint.md`](./architecture_blueprint.md)：整体架构、模块职责、数据流、客户端与后端协作方式。
3. [`implementation_plan.md`](./implementation_plan.md)：初版垂直切片执行方案、批次任务、验收标准。
4. [`open_questions.md`](./open_questions.md)：已确认决策、剩余验证点、下一轮讨论入口。

## 当前决策摘要

- 项目方向升级为“LLM 驱动 NPC 的生活模拟 RPG 垂直切片”。
- Python Agent Runtime 继续承担世界、Agent、记忆、事件、Provider 与调试记录。
- Godot 确定作为主要游戏客户端，负责地图、玩家操作、NPC 表现、对话与游戏 UI。
- 首版裁剪为 6 个 NPC、3 个地点、1 个完整游戏日和 1 个小镇事件。
- 玩家身份是新搬来的农场主，Debug / 研究控制台保留研究院视角。
- 首版直接接入 LLM 做测试，DeepSeek V4 Flash 作为优先低成本模型，RuleBasedProvider 保留为 fallback。
- 首版视觉路线采用温暖绘本风，像素风暂时只作为小人占位或后续专项方向。
- 现有网页前端后续收敛为 Debug / 研究控制台。
- Codex 应用内生图能力用于开发期美术资产生产，游戏运行时不接入图片生成 API。

