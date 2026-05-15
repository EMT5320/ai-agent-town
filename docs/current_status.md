# 当前项目状态与开发前约束

> 状态更新时间：2026-05-15
> 本文用于承接 `Agent Valley` 正式开发前的状态盘点、迁移边界和工程约束。开发时优先参考 `project_vision.md` 的长期目标，再参考本文判断当前阶段应处理的实际缺口。

## 当前阶段判断

项目已经完成从 `AI Agent 小镇观察台` 到 `Agent Valley` 生活模拟 RPG 的方向升级。

当前仓库具备一个可运行的早期 Agent 观察台原型：后端能推进小镇时间、调度多个 Agent、记录事件、展示 Debug 信息，并支持规则 Provider 与云端 Provider 配置。新的目标是把这些能力逐步沉淀为可玩的正式游戏骨架。

首版垂直切片承担两类职责：

1. 验证玩家、NPC Agent、记忆、关系和事件的闭环体验。
2. 建立后续扩展 NPC、地点、事件、资产、剧情和系统玩法时可以复用的工程结构。

## 已确认方向

- 对外项目名使用 `Agent Valley`。
- 游戏类型定位为 LLM NPC 驱动的二次元轻幻想轻异世界田园生活模拟 RPG。
- Godot 作为主游戏客户端，第一阶段以 Windows 桌面 Demo 为目标。
- Python Agent Server 继续作为权威世界状态和 Agent Runtime。
- Web 前端逐步收敛为 Debug / 研究控制台。
- 首版聚焦 6 个 NPC、3 个地点、1 个完整游戏日和 1 个小镇事件。
- 玩家身份是新搬来的偏少女农场主。
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
- `docs/agentic_game_design.md` 已沉淀多层 Agent 游戏系统定调，覆盖 Director System、Event Skill、Director Beat、异步队列、模型分工和记忆/RAG 方向。
- `docs/architecture_blueprint.md` 已定义 Godot、Python Server、Director System、Event Skill、Web Debug 和资产管线的职责。
- `docs/implementation_plan.md` 已定义批次 0 到批次 5 的推进顺序。
- `docs/open_questions.md` 已记录已确认决策和剩余验证点。
- `docs/vertical_slice_spec.md` 进一步约束第一天可玩切片的实现规格。
- `docs/art_direction.md` 已定义二次元轻幻想轻异世界美术风格、角色设定、资产清单和生图顺序。
- `docs/asset_generation_prompts.md` 已提供首版可复制的生图提示词和 manifest 登记模板。

## 当前主要缺口

### 游戏客户端缺口

- 已有 `clients/godot/` 项目骨架，仍缺少可移动地图场景、玩家节点、NPC 节点和正式对话 UI。
- Godot 与 Python 后端已有最小状态读取链路，仍需在编辑器窗口中验证主场景运行体验和同步频率。
- 已有正式资产源目录 `assets/source/`，并完成风格锁定图、玩家与 6 个首发 NPC reference sheet、3 张地点背景、1 张星灯祭事件 CG，以及玩家与 6 个首发 NPC 的 `neutral` 半身立绘。
- 已增加 `assets/manifests/asset_manifest.json` 登记与 `scripts/check_asset_manifest.py` 校验入口，首批场景图和 `neutral` 半身立绘已同步到 `clients/godot/assets/` 并填写 `godotPath`。
- Godot 主场景已通过 `AssetRegistry` 接入 3 张地点背景和玩家 + 6 个首发 NPC 的 `neutral` 半身立绘，支持地点背景切换、NPC 选择和聊天动作提交。
- 已增加 `npm.cmd run client:run` / `client:run:check`，可一条命令直接运行 P0 游戏窗口或检查运行入口。
- 仍需补地图小人、剩余表情差分和更正式的地图/Visual Novel 分层场景结构。

### 后端游戏 API 缺口

- 已有 `GET /api/world/state` 游戏客户端状态接口，返回 `player`、`locations`、`npcs`、`activeEvents`、`recentEvents` 和 `townStats`。
- 已有最小 `PlayerState`，包含位置、背包、已认识 NPC、任务标记、行动历史和玩家记忆。
- 已有 `POST /api/player/action` 玩家动作入口，当前支持 `move`、`talk`、`give_gift`、`inspect` 和 `attend_event`。
- 玩家 `talk` 和 `give_gift` 已写入事件、关系变化、NPC 记忆和 Debug 决策记录。
- 仍需根据 Godot Spike 继续调整同步频率、字段裁剪和客户端缓存策略。
- 已落地星灯祭供应短缺事件的查看、选择、关系变化、即时记忆和夜间反思种子。
- 仍需扩展 Director Beat 队列、Event Skill 数据化、更细的物品喜好规则、事件分支 UI、事件反应 LLM Profile 和夜间反思 LLM Profile。

### 内容系统缺口

- Godot 游戏状态已裁剪为首发 6 个 NPC 和首版 3 个地点；旧 Web Debug 仍可观察完整 10 NPC 原型。
- 星灯祭供应短缺事件已落成可执行事件规格，支持 `donate_crop`、`mediate`、`support_kai`、`support_bram` 和 `observe`。
- 夜间反思已有规则种子，仍需明确正式夜晚触发时机、LLM 输入上下文和输出结构。
- 角色卡、幻想显示名、性别认同、视觉原型、说话风格、日程、喜好、冲突关系、恋爱铺垫标签和资产引用需要结构化。
- 多层 Agent 游戏系统方向已确定，下一步需要把当前硬编码事件迁移为 Event Skill schema，并实现规则版 Director v0。

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
- `backend/app/director/`：后续新增 Director Beat、WorldDigest、TensionDetector、SkillRouter、Validator 和 QueueManager。
- `backend/app/skills/`：后续新增 Event Skill schema 与数据化事件定义。
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

当前已进入正式开发阶段，第一轮已完成：

1. `GET /api/world/state` 兼容接口。
2. 最小 `PlayerState`。
3. `POST /api/player/action` 的 `move`、`talk` 和 `give_gift` 链路。
4. 玩家动作的事件、关系、记忆和 Debug 记录。

第二轮已完成：

1. 创建 `clients/godot/` Godot 4.x 项目骨架。
2. 增加 `ApiClient`，读取 `GET /api/world/state` 并提交测试对话动作。
3. 增加 `WorldSync`，缓存玩家、地点、NPC 和最近事件。
4. 增加主场景文本面板，显示玩家、地点、NPC 和事件数据。
5. 增加 `scripts/check_godot_project.py`，让 `npm.cmd run check` 覆盖 Godot 骨架文件和 API 契约。

客户端环境准备已完成：

- 已安装 Godot 4.6.2 标准版。
- Godot 由脚本自动检测，当前机器优先命中 winget 安装目录。
- 已增加 `npm.cmd run client:env`，用于检查 Godot 版本和项目 headless 打开能力。
- 已增加 `npm.cmd run client:open`，用于打开 `clients/godot/project.godot` 编辑器。
- 已增加 `npm.cmd run client:run`，用于直接运行当前主场景。
- 新手环境说明见 `docs/game_client_environment.md`。

当前已通过 Godot headless 项目检查。后续仍需要在真实游戏窗口里确认背景、立绘、地点切换、NPC 选择和聊天动作体验。

下一轮建议继续：

1. 用 `npm.cmd run start` + `npm.cmd run client:run` 验收真实窗口内背景、立绘、地点按钮、NPC 按钮和聊天动作体验。
2. 继续生成玩家与 6 个首发 NPC 的 `happy` / `troubled` 表情差分，并检查同角色发型、服饰、瞳色和配饰一致性。
3. 生成并接入地图小人、对话/送礼/事件交互标记，让地图层从背景切换推进到可移动角色节点。
4. 将 Godot 当前图片背景 + 立绘面板重构为正式的地图层和 Visual Novel 对话层。
5. 实现规则版 Director v0：生成 WorldDigest，检测星灯祭触发条件，产出可验证 Director Beat。
6. 将星灯祭供应短缺迁移为 Event Skill 数据结构，再由 Runtime 加载和结算。
7. 在 Godot 中接入 `inspect` / `attend_event` 交互 UI，并把星灯祭结算结果展示到 VN 对话层。
8. 将事件反应和夜间反思从规则摘要升级为可配置 LLM Profile。
9. 根据 Godot 实测调整 `GET /api/world/state` 的字段体积和同步频率。
