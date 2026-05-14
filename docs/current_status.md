# 当前项目状态与开发前约束

> 状态更新时间：2026-05-14
> 本文用于承接 `Agent Valley` 正式开发前的状态盘点、迁移边界和工程约束。开发时优先参考 `project_vision.md` 的长期目标，再参考本文判断当前阶段应处理的实际缺口。

## 当前阶段判断

项目已经完成从 `AI Agent 小镇观察台` 到 `Agent Valley` 生活模拟 RPG 的方向升级。

当前仓库具备一个可运行的早期 Agent 观察台原型：后端能推进小镇时间、调度多个 Agent、记录事件、展示 Debug 信息，并支持规则 Provider 与云端 Provider 配置。新的目标是把这些能力逐步沉淀为可玩的正式游戏骨架。

首版垂直切片承担两类职责：

1. 验证玩家、NPC Agent、记忆、关系和事件的闭环体验。
2. 建立后续扩展 NPC、地点、事件、资产、剧情和系统玩法时可以复用的工程结构。

## 已确认方向

- 对外项目名使用 `Agent Valley`。
- 游戏类型定位为 LLM NPC 驱动的生活模拟 RPG。
- Godot 作为主游戏客户端，第一阶段以 Windows 桌面 Demo 为目标。
- Python Agent Server 继续作为权威世界状态和 Agent Runtime。
- Web 前端逐步收敛为 Debug / 研究控制台。
- 首版聚焦 6 个 NPC、3 个地点、1 个完整游戏日和 1 个小镇事件。
- 玩家身份是新搬来的农场主。
- Codex 应用内生图能力用于开发期资产生产，游戏运行时只读取静态资产。
- 当前项目成果服务于可玩 Demo、作品集展示、调试回放和后续产品化分析。

## 当前已实现能力

### 后端 Runtime

- 已有 Python HTTP 服务入口。
- 已有世界状态初始化。
- 已有 10 个初始 NPC 和 5 个地点。
- 已有关系图谱、基础状态数值、Agent 记忆列表。
- 已有时间推进、Agent 轮换调度和事件记录。
- 已有行动解析与执行能力，覆盖移动、对话、工作、购买、休息、照顾和参加事件。
- 已有人口事件雏形，例如老人健康风险和成长事件。
- 已有公开状态导出，供前端观察台展示。

### Provider 与模型配置

- 已有 `RuleBasedProvider`，可用于离线开发、测试夹具和异常兜底。
- 已有 `CloudApiProvider`，支持 OpenAI-compatible API 形态。
- 已有 `config/models.json`、`config/models.example.json` 和本地密钥 overlay 示例。
- 已有按 NPC 和功能选择模型 profile 的配置能力。
- 已有 Debug 信息展示 profile、provider、messages、rawText、parsed、executed 和 usage。

### Web 观察台

- 已有 `frontend/` 轻量控制台。
- 已能显示小镇地图、居民状态、事件流和最近一次 Debug 决策。
- 已支持手动推进、自动推进、暂停/继续和注入事件。

### 项目文档

- `docs/project_vision.md` 已定义最高优先级愿景。
- `docs/architecture_blueprint.md` 已定义 Godot、Python Server、Web Debug 和资产管线的职责。
- `docs/implementation_plan.md` 已定义批次 0 到批次 5 的推进顺序。
- `docs/open_questions.md` 已记录已确认决策和剩余验证点。
- `docs/vertical_slice_spec.md` 进一步约束第一天可玩切片的实现规格。

## 当前主要缺口

### 游戏客户端缺口

- 缺少 `clients/godot/` 项目。
- 缺少玩家移动、地图场景、NPC 表现和对话 UI。
- 缺少 Godot 与 Python 后端的稳定同步协议。
- 缺少正式游戏资产目录和 Godot 导入清单。

### 后端游戏 API 缺口

- 缺少 `GET /api/world/state` 游戏客户端状态接口。
- 缺少 `POST /api/player/action` 玩家动作入口。
- 缺少玩家状态：位置、背包、已认识 NPC、当天行动记录、任务进度。
- 缺少面向 Godot 的低频同步数据结构。
- 缺少玩家动作对关系、记忆和事件链路的标准写入规则。

### 内容系统缺口

- 10 个 NPC 仍需裁剪为首发 6 个 NPC 和扩展池。
- 5 个地点仍需裁剪为首发 3 个地点和扩展地点。
- 星灯节供应短缺事件需要落成可执行事件规格。
- 夜间反思需要明确触发时机、输入上下文和输出结构。
- 角色卡、日程、喜好、冲突关系和资产引用需要结构化。

### 工程稳定性缺口

- `npm.cmd run smoke` 当前可通过，输出示例为 `{'agents': 10, 'events': 11, 'tick': 1}`。
- `npm.cmd run check` 已改为把 Python 编译产物写入临时目录，避免 Windows 下仓库内 `__pycache__` 权限或占用问题。
- Git 会提示无法读取用户全局 ignore 文件：`C:\Users\Administrator/.config/git/ignore`，当前不阻塞仓库开发。

## 可复用模块

以下能力应尽量演进复用，避免推倒重写：

- `backend/app/runtime/agent_runtime.py`：保留为 Agent 调度和执行编排核心。
- `backend/app/world/world_state.py`：演进为权威世界状态层。
- `backend/app/world/seed_data.py`：短期可继续承载首版内容，后续迁到数据文件。
- `backend/app/events/event_store.py`：继续作为事件链路和调试回放基础。
- `backend/app/memory/memory_store.py`：扩展为事件记忆、关系记忆和夜间反思入口。
- `backend/app/providers/`：保留模型 Provider 抽象，补齐玩家对话、事件反应和夜间反思 profile。
- `frontend/`：迁移为 `web-admin/` 前的 Debug Console 原型。

## 开发前硬性约束

### 1. 按完整游戏骨架推进

首版垂直切片是正式游戏的最小可玩章节。所有关键实现都应保留后续扩展路径，包括：

- 新增 NPC。
- 新增地点。
- 新增玩家动作。
- 新增事件。
- 新增记忆类型。
- 新增资产。
- 新增剧情任务。
- 新增 Debug 视图。

### 2. 后端保持权威

Godot 只负责表现层和本地交互缓存。权威状态仍由 Python Agent Server 持有，包括：

- 玩家位置和背包。
- NPC 状态和位置。
- 时间推进。
- 关系变化。
- 记忆写入。
- 事件状态。
- LLM 调用链路。

### 3. 数据契约先行

新增功能优先明确数据结构和 API 契约，再进入 UI 或表现层实现。尤其是：

- `WorldState`
- `PlayerState`
- `NpcState`
- `LocationState`
- `EventState`
- `PlayerAction`
- `AgentDecisionRecord`
- `MemoryEntry`
- `RelationshipDelta`

### 4. 内容模块化

NPC、地点、物品、事件和日程应逐步从硬编码迁向数据驱动。首版可以保留 Python seed，但每次新增内容都要接近未来数据文件结构。

### 5. Debug 能力保留

Debug / 研究控制台是项目技术深度的展示窗口。任何关键玩家行为和 NPC 反应都要能追踪：

- 输入上下文。
- Prompt / messages。
- 模型原始输出。
- 解析后的行动。
- 执行结果。
- 关系变化。
- 记忆写入。
- token、延迟、fallback 和错误信息。

### 6. 资产来源可追踪

所有进入游戏的美术资源需要记录：

- 文件路径。
- 用途。
- 来源类型。
- 生成或处理日期。
- 提示词摘要。
- 是否已导入 Godot。
- 授权或使用备注。

### 7. 重要节点需要扩展性检查

以下节点进入实现前必须检查未来扩展性：

- 新增 API。
- 新增存档字段。
- 新增玩家动作。
- 新增 NPC 数据字段。
- 新增事件类型。
- 新增资产目录。
- 新增 Debug 数据。
- 改动 Provider 输出格式。

每个节点至少回答三个问题：

1. 未来新增同类内容是否只需要新增数据或小范围逻辑？
2. Godot、后端和 Debug Console 的职责是否清晰？
3. 调试、回放和作品集讲解是否能看到关键链路？

## 正式开发启动条件

满足以下条件后即可进入正式开发：

- 文档阅读顺序明确。
- 第一版垂直切片规格明确。
- 扩展性约束明确。
- 批次 0 阻塞项列表明确。
- 首个开发任务能直接落到代码。

当前文档整理完成后，建议第一个开发任务为：

1. 增加 `GET /api/world/state` 兼容接口。
2. 增加最小 `PlayerState`。
3. 增加 `POST /api/player/action` 的 `talk` 最小链路。
4. 创建 `clients/godot/` 空项目并读取后端状态。
5. 裁剪首版 6 NPC 和 3 地点数据。
