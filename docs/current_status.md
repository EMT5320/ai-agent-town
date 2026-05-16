# 当前项目状态与开发前约束

> 状态更新时间：2026-05-16
> 本文只记录当前仓库中已核对、命令已检或明确标注人工未验收的事实。长期方向见 `docs/project_vision.md`，系统设计细节见 `docs/agentic_game_design.md`。

## 1. 当前阶段判断

项目已经从早期 `AI Agent 小镇观察台` 进入 `Agent Valley` 第一版垂直切片收束阶段。当前仓库具备：

- 可运行的 Python Agent Server。
- Godot 4.x P0 客户端骨架，已接入事件查看与事件选择 UI；地图小人资源已入库，真实窗口体验仍需人工验收。
- 首批静态视觉资产、地图小人候选与 manifest 校验。
- 规则版 Director v0 + 单个 Event Skill 的最小闭环。
- LLM profile、fallback、Debug 字段记录路径，以及 Debug / Memory / influence 查询 API。
- 新对话入口与目标看板。

本阶段重点是把“可运行原型”收紧成“可人工验收的一天游戏闭环”。

## 2. 本轮核对结果

| 开发线 | 当前状态 | 已验证事实 | 仍需验证或实现 |
| --- | --- | --- | --- |
| 后端 Director / Event Skill | 部分完成 | `WorldDigest`、`DirectorBeat`、`TensionDetector`、`SkillRouter`、`DirectorValidator`、`DirectorQueueManager` 已落地；Runtime 会生成、校验、消费或丢弃 `activate_event_skill` Beat；星灯祭单技能已注册；Debug / Memory / influence 查询 API 已由 smoke 走真实 HTTP 路由验证 | Event Skill 仍只有一个；星灯祭结算、记忆模板和 fallback 台词仍有 Runtime 硬编码；通用 DirectorPlanner 和多事件 Skill 尚未完成 |
| Godot 客户端 | 部分完成 | 代码已接入：地点背景层、NPC 选择、底部 VN 对话层、聊天提交、进行中事件区、`inspect` 查看、choices 渲染、`attend_event` 提交、VN 结果展示；地图小人 PNG 与 `.import` 已同步到 Godot 资产目录；命令已检：`client:env` 与 `client:run:check` 通过 | 人工未验收：真实窗口体验；地图小人尚未实际放入地图角色层；事件 UI 的布局、可读性和错误提示需要窗口内确认 |
| 资产管线 | 部分完成 | manifest 当前有 31 条资产；3 张地图小人为 `style_anchor_candidate`；4 张重画地图小人和 3 张交互标记为 `pending_review`；3 张背景、1 张事件 CG、玩家 + 6 NPC neutral 立绘已登记；`AssetRegistry` 已支持表情回退 | `happy` / `troubled` 表情差分、道具图标、拆分 UI 组件尚未进 manifest 或 Godot registry；地图小人需实机确认后再晋级 |
| LLM / Debug | 部分完成 | 代码已接入：OpenAI-compatible cloud provider、profile 解析、本地 overlay 示例、Debug 字段记录、规则 fallback、`model:check` 配置校验、Web LLM 配置卡片和热重载接口；命令已检：smoke 覆盖 dialogue / event_reaction / night_reflection Debug 字段、compact Debug payload、RAG-lite memory search、玩家影响链 | 人工/外部配置未验收：本机当前没有真实 API key 配置，`llm-smoke` 会跳过；`debug_analysis` profile 只在配置中存在；真实延迟、成本、失败率待测 |
| 文档治理 | 已完成本轮入口 | `agent_context`、`goal_board`、`current_status`、`open_questions` 已形成新对话入口和状态看板 | 后续每轮只记录已验证变化，避免复制源设计长文 |

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
- Runtime 会把 Director 关键步骤写入事件流，便于 Debug Console 读取。

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
- 主场景已能列出 `activeEvents`，点击“查看事件”调用 `inspect`，渲染事件标题、摘要和 choices。
- 主场景已能点击事件选项调用 `attend_event`，并在 VN 面板中展示 NPC 台词、关系变化、记忆写入和夜间反思摘要。
- `AssetRegistry` 已接入星灯祭事件 CG，并支持 `happy` / `troubled` 表情缺图时回退 `neutral`。
- `scripts/check_godot_project.py` 会检查主场景、脚本、API 字符串、首批资产和 `.import` 元数据。
- `clients/godot/assets/sprites/` 已包含玩家和 6 个 NPC 的 `map_idle` PNG，以及 talk / gift / event 三类交互标记和对应 `.import`。
- 真实窗口体验仍需主人手动验收。

### 资产管线

- `assets/source/` 是正式资产源目录。
- `assets/manifests/asset_manifest.json` 是当前资产登记入口。
- `scripts/check_asset_manifest.py` 会校验字段、源图、prompt 文件、PNG 尺寸和 Godot 引用。
- 当前 manifest 共有 31 条资产：21 条 `source_selected`、3 条 `style_anchor_candidate`、7 条 `pending_review`。
- 当前已进入 Godot registry 的资产是 3 张地点背景、星灯祭事件 CG、玩家 + 6 个首发 NPC 的 `neutral` 半身立绘。
- 地图小人和交互标记已进入 Godot 资产目录，尚未接入 `AssetRegistry` 或主场景地图角色层。
- 本轮没有新增表情差分、道具图标和拆分 UI 组件。

## 4. 当前主要缺口

1. **真实 Godot 窗口验收**：需要用 `npm.cmd run start` + `npm.cmd run client:run` 人工确认窗口中的背景、NPC 选择、聊天提交、事件查看、事件选择、异常提示和同步频率。
2. **基础地图层**：Godot 已具备地图小人图片资源，仍需要推进地图节点、角色站位、交互区域和玩家移动输入。
3. **Event Skill 数据化深度**：当前已有 schema 和单技能注册表，结算细节还需要继续从 Runtime 规则表迁入数据层。
4. **真实 LLM smoke**：需要本地 key 或 overlay 后验证 DeepSeek / OpenAI-compatible profile 的真实延迟、成本、错误和 fallback。
5. **资产补齐**：表情差分、UI 组件、道具图标仍待生成、筛选、登记和接入；地图小人需窗口确认后定版。
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

## 7. 人工验收清单

```powershell
npm.cmd run start
npm.cmd run client:run
```

窗口内确认：

- 地点切换、背景切换可用。
- NPC 选择、`talk` 提交可用。
- 事件区能看到“星灯祭供应短缺”。
- 点击“查看事件”后能看到标题、摘要、choices。
- 点击任一选项后能看到 NPC 台词、关系变化、记忆写入、夜间反思摘要。

## 8. 下一轮建议

1. 主人先完成 Godot 真实窗口人工验收，并记录 UI、交互、错误提示和同步体验问题。
2. 客户端优先接入地图小人角色层、角色站位、交互 marker 和点击入口。
3. 配置一次真实 LLM smoke，确认 dialogue / event_reaction / night_reflection 的真实输出、延迟和 fallback。
4. 按客户端窗口效果决定地图小人是否晋级 `source_selected`，只修正实机暴露的资产问题。
5. 收紧 Event Skill 数据化：用 Skill 定义驱动选项、后果预览、asset hints 和部分结算模板。
6. Web Debug 追加 Director / Skill / fallback 视图，保持旧观察台不阻塞 Godot 主体验。
