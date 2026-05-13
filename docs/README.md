# Agent Valley 文档索引

本目录用于沉淀 `ai-agent-town-lab` 从观察台原型升级为生活模拟游戏原型的核心共识。

## 推荐阅读顺序

1. [`project_vision.md`](./project_vision.md)：最高优先级推进依据，定义项目愿景、边界、成功标准。
2. [`architecture_blueprint.md`](./architecture_blueprint.md)：整体架构、模块职责、数据流、客户端与后端协作方式。
3. [`implementation_plan.md`](./implementation_plan.md)：分阶段实施路线、近期垂直切片、风险控制。
4. [`open_questions.md`](./open_questions.md)：需要主人后续拍板或继续讨论的问题。

## 当前决策摘要

- 项目方向升级为“LLM 驱动 NPC 的生活模拟 RPG 垂直切片”。
- Python Agent Runtime 继续承担世界、Agent、记忆、事件、Provider 与实验记录。
- Godot 作为主要游戏客户端候选，负责地图、玩家操作、NPC 表现、对话与游戏 UI。
- 现有网页前端后续收敛为 Debug / 研究控制台。
- Codex 应用内生图能力用于开发期美术资产生产，游戏运行时不接入图片生成 API。

