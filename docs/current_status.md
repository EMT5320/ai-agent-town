---
status: active
owner_lane: project-status
last_verified: 2026-05-16
startup_load: after-agent-context
source_of_truth: true
scope: current implementation facts, verification state, and work constraints
---

# 当前项目状态与开发前约束

> 状态更新时间：2026-05-16
> 本文只记录当前仓库中已核对、命令已检或明确标注人工未验收的事实。长期方向见 `docs/project_vision.md`，系统设计细节见 `docs/agentic_game_design.md`。

## 1. 当前阶段判断

项目已经从早期 `AI Agent 小镇观察台` 进入 `Agent Valley` 第一版垂直切片收束阶段。当前仓库具备：

- 可运行的 Python Agent Server。
- Godot 4.x P0 客户端骨架，已接入事件查看、事件选择、地图角色层和交互 marker；真实窗口已由主人验收，基本可用。
- 首批静态视觉资产、地图小人候选与 manifest 校验。
- 规则版 Director v0 + 单个 Event Skill 的最小闭环。
- LLM profile、fallback、Debug 字段记录路径，以及 Debug / Memory / influence 查询 API。
- 首发 6 名 NPC 的深度卡、关系阶段、送礼反应和写作工作流。
- 新对话入口与目标看板。

本阶段已经具备可人工验收的一天游戏闭环雏形；当前重点转为补足玩法深度，让体验从背景图和简单 UI 点击推进到地图移动、空间交互、生活行动反馈和内容驱动节奏。

## 2. 本轮核对结果

游戏内容剧本线的讨论、四层方案、当前实现与后续主线拆分已沉淀到 `docs/game_content_storyline.md`。

| 开发线 | 当前状态 | 已验证事实 | 仍需验证或实现 |
| --- | --- | --- | --- |
| 后端 Director / Event Skill | 部分完成 | `WorldDigest`、`DirectorBeat`、`TensionDetector`、`SkillRouter`、`DirectorValidator`、`DirectorQueueManager` 已落地；Runtime 会生成、校验、消费或丢弃 `activate_event_skill` Beat；星灯祭单技能已注册；玩家画像证据模板与事件反应记忆模板已迁入 Event Skill；Debug / Memory / influence 查询 API 已由 smoke 走真实 HTTP 路由验证 | Event Skill 仍只有一个；星灯祭仍有部分结算、fallback 台词和 asset hints 留在 Runtime；通用 DirectorPlanner 和多事件 Skill 尚未完成 |
| Content Codex / NPC 深度卡 | 已完成首批 | `docs/npc_deep_card_spec.md` 已定义数据契约；`.windsurf/workflows/author-npc-deep-card.md` 已定义批量写作流程；`backend/app/content/data/npc/` 已入库 `kai`、`bram`、`mira`、`tomas`、`orren`、`lena` 6 份卡；`monologueSeeds` 已接入夜间反思上下文、compact evidence 和规则 fallback；`npm.cmd run content:check` 通过；smoke 覆盖 `deepCard`、对话 Prompt、送礼、关系阶段和 monologue evidence | `gossipHooks` 尚未接入谣言传播玩法；后续批量 Event Skill 工作流未开始 |
| Godot 客户端 | 部分完成 | 代码已接入：地点背景层、NPC 选择、底部 VN 对话层、聊天提交、进行中事件区、`inspect`、choices、`attend_event`、VN 结果展示；地图角色层已渲染玩家与 6 个 NPC 的 `map_idle` 小人和 marker；新增按住方向键持续移动、点击地图落点、靠近高亮和 MapMoveHint；已移除小人淡黄色矩形背景；命令已检：`client:env` 与 `client:run:check` 通过；主人已完成上一版真实窗口人工验收 | 新移动手感和去背景效果仍需主人复验；本地移动只做表现层；服务端锚点/交互半径契约、行动反馈、日程可视化和更自然的内容节奏仍待推进 |
| 资产管线 | 部分完成 | manifest 当前有 31 条资产；3 张地图小人为 `style_anchor_candidate`；4 张重画地图小人和 3 张交互标记为 `pending_review`；3 张背景、1 张事件 CG、玩家 + 6 NPC neutral 立绘已登记；`AssetRegistry` 已支持表情回退；地图小人与交互 marker 已进入 Godot 场景显示链路 | `happy` / `troubled` 表情差分、道具图标、拆分 UI 组件、玩法反馈图标尚未进 manifest 或 Godot registry；地图小人是否晋级 `source_selected` 仍需主人明确筛选结论 |
| LLM / Debug | 部分完成 | 代码已接入：OpenAI-compatible cloud provider、profile 解析、本地 overlay 示例、Debug 字段记录、规则 fallback、`model:check` 配置校验、Web LLM 配置卡片和热重载接口；2026-05-16 已用当前本机 `config/models.json` 跑通真实 `CloudApiProvider` smoke，dialogue / event_reaction / night_reflection 均为 `deepseek-v4-flash` 且 `fallbackReason=None`；smoke 覆盖 compact Debug payload、RAG-lite memory search、玩家影响链 | 提交态不包含真实 API key；fresh env 或无 key 沙箱会跳过真实 LLM 调用；`debug_analysis` profile 只在配置中存在；切换模型、key 或 profile 后需重新刷新真实延迟、成本和失败率 |
| 文档治理 | 已完成本轮入口 | `AGENTS.md`、`CLAUDE.md`、`docs/README.md`、`agent_context`、`goal_board`、`current_status`、`open_questions` 已形成新对话入口、分层索引和状态看板 | 后续每轮只记录已验证变化，避免复制源设计长文 |

## 3. 当前已实现能力

### 后端 Runtime

- Python HTTP 服务入口已存在。
- 世界状态初始化、10 个初始 NPC、5 个地点、关系图谱、基础状态数值和 Agent 记忆列表已存在。
- 时间推进、Agent 轮换调度、事件记录和公开状态导出已存在。
- 玩家游戏 API 已存在：`GET /api/world/state`、`POST /api/player/action`。
- 玩家动作已覆盖 `move`、`talk`、`give_gift`、`inspect`、`attend_event`。
- 星灯祭供应短缺事件已有查看、选择、关系变化、即时记忆、事件反应、夜间反思和结算记录。
- `/api/player/action` 的根节点、`result` 和 `state` 均带有 Godot 可直接展示的 `memoryEvidence`、`relationshipEvidence`、`playerProfile`、`currentObjective`、`availableInteractions`。

### Director / Skill

- `backend/app/director/v0.py` 已包含规则版 Director v0 的摘要、张力检测、路由、Beat、校验和队列组件。
- `backend/app/skills/event_skill_schema.py` 已定义事件技能结构。
- `backend/app/skills/event_skill_registry.py` 已注册 `event.starlight_festival_shortage`。
- `EventChoiceOutcome` 已承载玩家画像证据模板和事件反应记忆模板，Runtime 继续负责格式化、事件写入和 fallback 执行。
- Runtime 会把 Director 关键步骤写入事件流，便于 Debug Console 读取。

### Content Codex / NPC 深度卡

- `backend/app/content/codex_schema.py` 定义 NPC 深度卡 dataclass 契约。
- `backend/app/content/codex_loader.py` 负责读取 `data/npc/*.json`、交叉校验关系阶段与 unlock 引用，并提供 runtime 字典转换。
- `backend/app/content/data/npc/` 已包含 6 份首发 NPC 卡，每份包含秘密、喜好/厌恶、5 段关系阶段、8 条以上独白种子、送礼四档反应和谣言钩子。
- `create_initial_world()` 会把深度卡挂载到对应 `agent.deepCard`。
- 对话 Prompt 已读取深度卡语气锚点；送礼会匹配深度卡 `giftReactions`；玩家对话和送礼结果会返回 `relationshipStage`。
- 夜间反思会读取 `monologueSeeds`，并把 compact `npc_monologue_seed` evidence 暴露给 Debug；规则 fallback 不依赖云端模型也能引用独白素材。
- `scripts/check_npc_codex.py` 已加入 `npm.cmd run content:check` 和 `npm.cmd run check`，并校验独白素材覆盖 morning / afternoon / evening、post_event、high_mood / low_mood。

### Provider / Debug

- `RuleBasedProvider` 用于离线开发、测试夹具和异常兜底。
- `CloudApiProvider` 支持 OpenAI-compatible API 形态。
- `config/models.example.json` 默认 `activeProvider=rule`，保证无密钥也可检查。
- `config/models.json` 是本机实际联调配置，已加入 gitignore；未配置本地密钥时运行链路会依赖 fallback。
- `npm.cmd run model:check` 会校验 profile 引用、结构和公开配置是否误写 `apiKey`。
- `/api/model-config/reload` 支持开发期热重载模型配置；Web 观察台已能展示 profile、路由、key 状态和触发对话 smoke。
- Debug 记录已包含 profile、provider、messages、rawText、parsed、executed、usage、latency 和 fallbackReason。
- 已提供 `/api/debug`、`/api/debug/director`、`/api/debug/skills`、`/api/debug/turns`、`/api/debug/influence`、`/api/debug/skill`、`/api/memory/summary`、`/api/memory/search` 查询入口。
- Debug 列表响应会压缩长 prompt / raw text，保留预览、长度和 message 数，便于 Web Debug Console 或 Godot 调试层读取。

### Godot 客户端

- `clients/godot/` 已有 Godot 4.x 项目、主场景、`ApiClient`、`WorldSync`、`AssetRegistry`。
- 主场景代码已能读取世界状态、渲染背景、列出地点和 NPC、展示半身立绘、提交聊天动作。
- 主场景已能渲染地图角色层，显示玩家和 6 个首发 NPC 的小人，并提供 talk / gift / event 交互 marker。
- 主场景已新增本地地图移动与靠近反馈：按住方向键持续移动、点击地图设置落点、玩家小人平滑移动、靠近 NPC / 事件后高亮交互；该坐标不写回后端。
- 角色小人淡黄色矩形背景已移除，选中或靠近状态改用 sprite tint 与 marker 状态表达。
- 主场景已能列出 `activeEvents`，点击“查看事件”调用 `inspect`，渲染事件标题、摘要和 choices。
- 主场景已能点击事件选项调用 `attend_event`，并在 VN 面板中展示 NPC 台词、关系变化、记忆写入和夜间反思摘要。
- `AssetRegistry` 已接入星灯祭事件 CG，并支持 `happy` / `troubled` 表情缺图时回退 `neutral`。
- `scripts/check_godot_project.py` 会检查主场景、脚本、API 字符串、首批资产和 `.import` 元数据。
- `clients/godot/assets/sprites/` 已包含玩家和 6 个 NPC 的 `map_idle` PNG，以及 talk / gift / event 三类交互标记和对应 `.import`。
- 2026-05-16 主人已完成真实窗口人工验收，基本可用；后续人工验收重点转为玩法深度、地图操作手感和内容节奏。

### 资产管线

- `assets/source/` 是正式资产源目录。
- `assets/manifests/asset_manifest.json` 是当前资产登记入口。
- `scripts/check_asset_manifest.py` 会校验字段、源图、prompt 文件、PNG 尺寸和 Godot 引用。
- 当前 manifest 共有 31 条资产：21 条 `source_selected`、3 条 `style_anchor_candidate`、7 条 `pending_review`。
- 当前已进入 Godot registry 的资产是 3 张地点背景、星灯祭事件 CG、玩家 + 6 个首发 NPC 的 `neutral` 半身立绘、玩家 + 6 个首发 NPC 的地图小人和 3 类交互标记。
- 地图小人和交互标记已进入 Godot 资产目录、`AssetRegistry` 与主场景地图角色层。
- 本轮没有新增表情差分、道具图标和拆分 UI 组件。

## 4. 当前主要缺口

1. **玩法深度主线**：真实窗口基础链路已通过，持续按键移动、点击落点、靠近反馈和去背景已落地；仍需要主人复验新手感，并继续推进服务端锚点契约、行动反馈、生活行动循环和日程可视化。
2. **Content Codex 二阶段接入**：`monologueSeeds` 已接入夜间反思/RAG；`gossipHooks` 仍需接入谣言传播。
3. **Event Skill 数据化深度**：当前已有 schema 和单技能注册表，画像证据与事件反应记忆模板已迁入 Skill；更多结算模板、asset hints 和复用测试仍需推进。
4. **真实 LLM 证据刷新**：当前本机 `config/models.json` 已跑通真实 smoke；切换模型、key 或 profile 后，需要重新验证 DeepSeek / OpenAI-compatible profile 的真实延迟、成本、错误和 fallback。
5. **资产补齐**：表情差分、UI 组件、道具图标、玩法反馈图标仍待生成、筛选、登记和接入；地图小人晋级状态需主人确认。
6. **Debug Console 扩展**：后端已有 Debug / Memory 查询 API，Web 侧仍需展示 Director 队列、Skill 激活、fallback 和成本字段。

## 5. 开发前硬性约束

- 权威世界状态只由后端 Runtime 修改。
- Godot 客户端只读状态、提交玩家动作、展示结果。
- LLM 输出必须经过解析、校验、fallback 和事件记录后才能影响可见结果。
- 密钥只允许放本地 overlay 或环境变量。
- 新增资产必须更新 manifest；新增 Godot 可用资产必须同步 registry 或检查脚本。
- 新增 API、存档字段、事件类型、资产目录、Debug 字段前先写清数据契约。
- 未由代码、命令或人工窗口验证的能力只能写入缺口或待验证项。

## 6. 当前可运行命令

```powershell
npm.cmd run check
npm.cmd run context:check
npm.cmd run content:check
npm.cmd run smoke
npm.cmd run asset:check
npm.cmd run client:env
npm.cmd run client:run:check
npm.cmd run start
npm.cmd run client:run
git diff --check
```

本轮收口要求的完整验收命令为：

```powershell
npm.cmd run check
npm.cmd run context:check
npm.cmd run content:check
npm.cmd run smoke
npm.cmd run asset:check
npm.cmd run client:env
npm.cmd run client:run:check
git diff --check
```

白天整合交接和晚上开工目标见：

```powershell
Get-Content docs\daytime_integration_handoff.md
```

## 7. 人工验收状态

2026-05-16，主人已运行真实 Godot 窗口并确认当前基础体验基本无问题。该结论覆盖：地点切换、背景切换、NPC 选择、`talk` 提交、星灯祭事件查看、choices 展示和事件结算展示。

仍需人工未验收的内容：后续新增的可移动地图、靠近交互、行动反馈、表情差分、UI 组件和真实 LLM profile 切换。

## 8. 下一轮建议

1. 文档治理已把真实窗口验收记录为已人工确认；后续每轮继续只更新已验证事实、剩余缺口和下一步。
2. Godot 玩法线先复验持续移动和去背景效果，再推进服务端锚点契约、行动反馈、生活行动按钮和日程可视化。
3. 内容线优先把 `gossipHooks` 做成第一版谣言传播数据源。
4. 后端线继续收紧 Event Skill 数据化：用 Skill 定义驱动更多结算模板、asset hints 和复用测试。
5. LLM / Debug 线在切换模型、key 或 profile 后刷新真实 smoke，记录 dialogue / event_reaction / night_reflection 的真实输出、延迟和 fallback。
6. 资产线按玩法需要推进表情差分、UI 组件、道具图标和行动反馈图标，地图小人晋级状态等待主人筛选结论。
7. Web Debug 追加 Director / Skill / fallback 视图，保持旧观察台服务调试和回放。
