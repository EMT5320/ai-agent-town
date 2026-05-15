# Agent Valley 新对话上下文入口

> 更新时间：2026-05-15
> 用途：后续新对话、无人值守开发、并行子代理任务的第一入口。

## 0. 使用方式

- 新对话先读本文，再按“推荐阅读顺序”补读源文档。
- 本文只保留项目 brief、边界和下一步，不复制长篇设计。
- 需要判断产品方向时，以 `docs/project_vision.md` 为最高优先级依据。
- 需要判断当前能改什么时，以 `docs/current_status.md` 和本文的写入边界为准。
- 需要开并行任务时，先看 `docs/goal_board.md`，再给每个代理限定写入范围。
- 需要设计项目 Skill 时，参考 `docs/skill_strategy.md`。

## 1. 当前项目一句话定位

`Agent Valley` 是一个由 Godot 承担玩家体验、Python Agent Server 承担权威世界状态与 LLM NPC 的二次元轻幻想田园生活模拟 RPG，目标是把早期多 Agent 观察台升级成可玩、可扩展、可调试的正式游戏骨架。

## 2. 当前已实现能力

### 2.1 后端 Runtime

- 已有 Python HTTP 服务入口。
- 已有世界状态初始化。
- 已有 10 个初始 NPC 和 5 个地点的观察台基线。
- 已有时间推进、Agent 轮换调度和事件记录。
- 已有行动解析与执行能力，覆盖移动、对话、工作、购买、休息、照顾和参加事件。
- 已有关系图谱、基础状态数值和 Agent 记忆列表。
- 已有人口事件雏形，例如老人健康风险和成长事件。
- 已有公开状态导出，供前端观察台展示。

### 2.2 Provider 与模型配置

- 已有 `RuleBasedProvider`，用于离线开发、测试夹具和异常兜底。
- 已有 `CloudApiProvider`，支持 OpenAI-compatible API 形态。
- 已有 `config/models.json`、`config/models.example.json` 和本地密钥 overlay 示例。
- 已有按 NPC 和功能选择模型 profile 的配置能力。
- 已有 Debug 信息展示 profile、provider、messages、rawText、parsed、executed 和 usage。

### 2.3 游戏 API 与玩家链路

- 已有 `GET /api/world/state` 游戏客户端状态接口。
- 返回字段包含 `player`、`locations`、`npcs`、`activeEvents`、`recentEvents` 和 `townStats`。
- 已有最小 `PlayerState`，包含位置、背包、已认识 NPC、任务标记、行动历史和玩家记忆。
- 已有 `POST /api/player/action` 玩家动作入口。
- 当前玩家动作支持 `move`、`talk`、`give_gift`、`inspect` 和 `attend_event`。
- 玩家 `talk` 和 `give_gift` 已写入事件、关系变化、NPC 记忆和 Debug 决策记录。
- 星灯祭供应短缺事件已有查看、选择、关系变化、即时记忆和夜间反思种子。

### 2.4 Godot 客户端

- 已有 `clients/godot/` Godot 4.x 项目骨架。
- 已有 `ApiClient` 读取世界状态并提交玩家动作。
- 已有 `WorldSync` 缓存玩家、地点、NPC 和最近事件。
- 主场景已能显示后端状态。
- 主场景已接入 3 张地点背景和玩家 + 6 个首发 NPC 的 `neutral` 半身立绘。
- 已支持地点背景切换、NPC 选择和聊天动作提交。
- 已有 `npm.cmd run client:env`、`client:open`、`client:run`、`client:run:check`。

### 2.5 资产与 Manifest

- 已有正式资产源目录 `assets/source/`。
- 已有 `assets/manifests/asset_manifest.json`。
- 已有 `scripts/check_asset_manifest.py` 校验入口。
- 已完成风格锁定图、玩家与 6 个首发 NPC reference sheet。
- 已有 3 张地点背景、1 张星灯祭事件 CG。
- 已有玩家与 6 个首发 NPC 的 `neutral` 半身立绘。
- 首批场景图和 `neutral` 半身立绘已同步到 `clients/godot/assets/` 并填写 `godotPath`。

### 2.6 Web Debug 与文档

- 已有 `frontend/` 轻量观察台。
- 已能显示小镇地图、居民状态、事件流和最近一次 Debug 决策。
- 已支持手动推进、自动推进、暂停/继续和注入事件。
- `docs/project_vision.md` 是最高优先级愿景。
- `docs/agentic_game_design.md` 已定义多层 Agent、Director System、Event Skill、Director Beat、异步队列、模型分工和记忆/RAG。
- `docs/vertical_slice_spec.md` 已定义第一天可玩切片的数据契约和验收边界。
- `docs/implementation_plan.md` 已定义批次 0 到批次 5 的推进路线。

## 3. 当前重点缺口

### 3.1 Godot 真实窗口验收

- 仍需用真实 Godot 窗口验证主场景运行体验。
- 需要验证背景切换、NPC 选择、聊天提交、同步频率和异常提示。
- 仍需补地图小人、剩余表情差分和更正式的地图 / Visual Novel 分层场景结构。

### 3.2 后端多层 Agent

- 需要定义 `WorldDigest`、`DirectorBeat` 和 `EventSkill` schema。
- 需要实现规则版 `WorldDigestBuilder`、`TensionDetector`、`SkillRouter`、`DirectorQueueManager` 和 `DirectorValidator`。
- 需要把星灯祭供应短缺从硬编码事件迁移为 Event Skill 数据。
- 需要让 Debug Console 记录 Director Beat 输入、输出、校验结果、消费结果和 fallback。

### 3.3 LLM 与 Debug

- 需要配置并实测 DeepSeek V4 Flash Profile。
- 需要为玩家聊天、事件反应、夜间反思分别设计 Prompt 模板。
- 所有高价值 LLM 输出需要结构化 JSON，并保留自然语言兜底解析。
- 需要记录 token、延迟、错误、fallback 和成本估算。

### 3.4 内容数据结构

- 首发 6 NPC 的角色卡、幻想显示名、性别认同、视觉原型、说话风格、日程、喜好、冲突关系、恋爱铺垫标签和资产引用仍需更结构化。
- NPC、地点、物品、事件和日程应逐步从硬编码迁向数据驱动。
- 每次新增内容都要靠近未来数据文件结构。

### 3.5 Web Debug 迁移

- 现有 `frontend/` 后续收敛为 Debug / 研究控制台。
- 建立 `web-admin/` 后，新的 Debug Console 功能优先进入 `web-admin/`。
- 关键玩家行为和 NPC 反应必须能追踪输入上下文、Prompt、模型输出、解析行动、执行结果、关系变化和记忆写入。

## 4. 开发硬性检查

### 4.1 完整游戏骨架推进

- 首版垂直切片是正式游戏的最小可玩章节。
- 每轮实现都要检查后续扩展路径，至少覆盖 NPC、地点、玩家动作、事件、记忆类型、资产、剧情任务和 Debug 视图。
- 如果某个改动只能服务一次性 Demo，需要先说明原因，并把后续替换路径写入交接记录。

### 4.2 重要节点扩展性检查

以下节点进入实现前必须做扩展性检查：

- 新增 API。
- 新增存档字段。
- 新增玩家动作。
- 新增 NPC 数据字段。
- 新增事件类型。
- 新增资产目录。
- 新增 Debug 数据。
- 改动 Provider 输出格式。

检查模板：

1. 未来新增同类内容是否只需要新增数据或小范围逻辑？
2. Godot、后端和 Debug Console 的职责是否清晰？
3. 调试、回放和作品集讲解是否能看到关键链路？

## 5. 推荐阅读顺序

1. `docs/agent_context.md`：新对话第一入口，快速确定现状和边界。
2. `docs/project_vision.md`：最高优先级方向，定义长期产品定位、边界和成功标准。
3. `docs/current_status.md`：确认当前代码基线、可复用模块、主要缺口和开发前约束。
4. `docs/goal_board.md`：确认并行开发线、写入范围和验收命令。
5. `docs/vertical_slice_spec.md`：确认第一天切片的数据契约、体验边界和验收标准。
6. `docs/agentic_game_design.md`：理解多层 Agent、Director、Event Skill、记忆/RAG 和 Debug 链路。
7. `docs/implementation_plan.md`：查看批次推进顺序和最近工作建议。
8. `docs/art_direction.md`：进入资产或视觉任务前阅读。
9. `docs/asset_generation_prompts.md`：进入生图任务前阅读。
10. `docs/open_questions.md`：需要处理未定方向时阅读。

## 6. 常用命令

```powershell
npm.cmd run check
npm.cmd run smoke
npm.cmd run start
npm.cmd run client:env
npm.cmd run client:open:check
npm.cmd run client:run:check
npm.cmd run client:run
npm.cmd run asset:check
git -c safe.directory=D:/Work/fun-projects-lab/projects/ai-agent-town-lab status --short
git diff --check
```

- `npm.cmd run check`：综合检查 Python 编译、前端 JS、smoke、资产 manifest、Godot 项目结构。
- `npm.cmd run smoke`：后端最小运行烟测。
- `npm.cmd run start`：启动 Python 服务。
- `npm.cmd run client:env`：检查本机 Godot 环境。
- `npm.cmd run client:run:check`：检查 Godot 运行入口。
- `npm.cmd run client:run`：运行 P0 游戏窗口。
- `npm.cmd run asset:check`：校验资产 manifest 与 prompt 引用。
- Windows Git 若出现 dubious ownership，使用上面的 `safe.directory` 参数。
- 文档统一使用 UTF-8 编码保存。

## 7. 并行开发线和写入边界

### 7.1 后端多层 Agent 线

- 目标：补齐 Director v0、Event Skill、WorldDigest 和 Debug 记录。
- 主要写入：`backend/app/director/`、`backend/app/skills/`、`backend/app/memory/`、`backend/app/events/`、相关测试。
- 可读取：`docs/agentic_game_design.md`、`docs/vertical_slice_spec.md`、`docs/current_status.md`。
- 边界：权威世界状态只由后端 Runtime 修改，LLM 只能提出计划或工具调用意图。
- 验收：`npm.cmd run check`，必要时追加 `npm.cmd run smoke`。

### 7.2 Godot 客户端线

- 目标：验证真实窗口体验，完善地图层和 Visual Novel 对话层。
- 主要写入：`clients/godot/`。
- 可读取：`docs/game_client_environment.md`、`docs/vertical_slice_spec.md`、`assets/manifests/asset_manifest.json`。
- 边界：Godot 只做表现层和本地交互缓存，通过 API 提交玩家动作。
- 验收：`npm.cmd run client:run:check`、`npm.cmd run check`，可手动运行 `npm.cmd run client:run`。

### 7.3 资产管线线

- 目标：补地图小人、表情差分、UI 组件和资产 manifest。
- 主要写入：`assets/source/`、`assets/processed/`、`assets/manifests/`、必要时 `clients/godot/assets/`。
- 可读取：`docs/art_direction.md`、`docs/asset_generation_prompts.md`、`docs/vertical_slice_spec.md`。
- 边界：所有入库资产必须记录用途、来源、提示词摘要、处理路径、Godot 引用和授权备注。
- 验收：`npm.cmd run asset:check`、`npm.cmd run check`。

### 7.4 LLM / Debug 线

- 目标：实测模型 profile、完善 Prompt、记录 token / 延迟 / fallback / 成本。
- 主要写入：`backend/app/providers/`、Debug 记录结构、后续 `web-admin/` 或迁移期 `frontend/`。
- 可读取：`config/models.example.json`、`docs/current_status.md`、`docs/agentic_game_design.md`。
- 边界：密钥只放本地 overlay 或环境变量，不写入仓库。
- 验收：`npm.cmd run check`，LLM 实测需记录可复现配置和 fallback 结果。

### 7.5 文档与治理线

- 目标：保持新对话入口、目标看板和 Skill 策略最新。
- 主要写入：`docs/agent_context.md`、`docs/goal_board.md`、`docs/skill_strategy.md`、必要时 `scripts/build_agent_context.py`。
- 边界：治理文档只沉淀现状、边界和下一步，不替代源设计文档。
- 验收：`npm.cmd run check`、`git diff --check`。

## 8. 最近下一步

1. 先运行 `npm.cmd run check`，确认基线干净。
2. 用 `npm.cmd run client:run:check` 和必要的真实窗口运行验证 Godot 主场景。
3. 后端线优先定义 `WorldDigest`、`DirectorBeat`、`EventSkill` schema。
4. 用规则版 Director v0 生成并消费一个 `activate_event_skill` Beat。
5. 将星灯祭供应短缺迁移为 Event Skill 数据，保持现有查看、选择、关系变化、记忆和夜间反思链路。
6. LLM 线用 1 个 NPC 先完成真实玩家聊天测试，记录 Debug 链路和 fallback。
7. 资产线补地图小人和表情差分，继续维护 manifest。
8. 每轮无人值守开发结束前更新 `docs/goal_board.md` 的状态与下一步。

## 9. 新对话开工检查清单

- 已读本文。
- 已确认本轮开发线和写入范围。
- 已查看 `git status --short`。
- 已确认仅修改本轮开发线允许目录。
- 已确认新增 API 或字段先写数据契约。
- 已完成重要节点扩展性三问。
- 已确认关键链路会进入 Debug 记录。
- 已确认资产变更会更新 manifest。
- 已确认文档变更保持 UTF-8 编码。
- 已确认最后运行对应验收命令。
