# Agent Valley 新对话入口

> 更新时间：2026-05-15
> 用途：下一轮新对话、无人值守开发、并行子代理任务的第一入口。

## 1. 当前入口

- 先读本文，再按任务线读取源文档。
- 长期方向以 `docs/project_vision.md` 为准。
- 当前事实以 `docs/current_status.md` 为准。
- 并行写入范围以 `docs/goal_board.md` 为准。
- 多层 Agent 设计细节见 `docs/agentic_game_design.md`。
- 视觉和资产细节见 `docs/art_direction.md`、`docs/asset_generation_prompts.md`、`assets/manifests/asset_manifest.json`。

## 2. 一句话定位

`Agent Valley` 是一个由 Godot 承担玩家体验、Python Agent Server 承担权威世界状态与 LLM NPC 的二次元轻幻想田园生活模拟 RPG。当前目标是把早期多 Agent 观察台收束成可玩、可扩展、可调试的第一天垂直切片。

## 3. 当前已验证事实

### 后端 Runtime / Director

- Python Agent Server 仍是权威世界状态入口。
- 已有 `GET /api/world/state`、`POST /api/player/action`、`/api/state`、`/api/model-config`、`/api/events`、`/api/developer`。
- 玩家动作已覆盖 `move`、`talk`、`give_gift`、`inspect`、`attend_event`。
- `backend/app/director/v0.py` 已落地 `WorldDigest`、`TensionDetector`、`SkillRouter`、`DirectorBeat`、`DirectorValidator`、`DirectorQueueManager`。
- Runtime 会运行规则版 Director v0，并写入 `director.digest_created`、`director.beat_created`、`director.beat_validated`、`director.beat_consumed`、`director.beat_discarded`。
- 已有单个 Event Skill：`event.starlight_festival_shortage`，定义位于 `backend/app/skills/event_skill_registry.py`。
- 星灯祭事件当前支持查看、选择、关系变化、记忆写入、事件反应、夜间反思和结算记录。

### LLM / Debug

- 已有 `RuleBasedProvider` 和 OpenAI-compatible `CloudApiProvider`。
- 已有按 NPC / feature 选择 profile 的配置路径：`config/models.json`、`config/models.example.json`、`config/models.local.example.json`。
- Debug 记录已包含 `providerMode`、`profileName`、`apiKeyConfigured`、`messages`、`rawText`、`parsed`、`executed`、`usage`、`latency`、`fallbackReason`。
- 当前本机未检测到 `config/models.local.json` 或 API key 时，真实 LLM smoke 会跳过。

### Godot 客户端

- `clients/godot/` 是 Godot 4.x 项目骨架。
- 已有 `ApiClient`、`WorldSync`、`AssetRegistry`。
- 主场景已接入 3 张地点背景和玩家 + 6 个首发 NPC 的 `neutral` 半身立绘。
- 已支持地点按钮、NPC 选择、VN 风格底部对话面板、聊天动作提交。
- 事件当前主要展示 `recentEvents` 文本，尚未形成独立可点击事件 UI。

### 资产与文档治理

- `assets/manifests/asset_manifest.json` 当前登记 21 条已筛选资产。
- 已同步到 Godot 的资产包括 3 张地点背景和玩家 + 6 个首发 NPC 的 `neutral` 立绘。
- 表情差分、地图小人、道具图标和拆分 UI 组件仍在后续批次。
- `docs/agent_context.md`、`docs/goal_board.md`、`docs/current_status.md`、`docs/open_questions.md` 已作为治理入口。

## 4. 当前边界

- 后端持有权威世界状态；Godot 只做表现层、本地交互缓存和 API 调用。
- LLM 只生成文本、结构化建议或工具意图；世界状态变更必须经过 Runtime 规则和校验。
- 密钥只放 `config/models.local.json` 或环境变量，不写入仓库。
- 资产入库必须登记来源、提示词引用、用途、状态、授权备注和 Godot 引用。
- 未真实验证的云端 LLM、真实窗口体验、事件 UI、地图小人和表情差分不得写成已完成。
- `frontend/` 继续作为迁移期 Debug 观察台；正式 Web Debug 后续再收敛到 `web-admin/`。

## 5. 常用命令

```powershell
npm.cmd run check
npm.cmd run smoke
npm.cmd run asset:check
npm.cmd run client:run:check
npm.cmd run client:env
npm.cmd run start
npm.cmd run client:run
git status --short
git branch --show-current
git log --oneline -8
git worktree list
git diff --check
```

说明：

- `npm.cmd run check` 覆盖 Python 编译、前端 JS、后端 smoke、资产 manifest、Godot 项目结构。
- `npm.cmd run smoke` 重点验证后端 Runtime、Director v0、Event Skill、Debug 字段和 LLM smoke 跳过/执行状态。
- `npm.cmd run asset:check` 校验资产路径、prompt 引用、PNG 尺寸和 Godot 引用。
- `npm.cmd run client:run:check` 只检查 Godot 运行入口，不打开真实游戏窗口。
- `npm.cmd run client:run` 会打开真实 Godot 游戏窗口，适合人工验收。

## 6. 下一轮最短开发入口

1. 固定离线基线：运行 `npm.cmd run check`、`npm.cmd run smoke`、`npm.cmd run asset:check`、`npm.cmd run client:run:check`。
2. Godot 线：用 `npm.cmd run start` + `npm.cmd run client:run` 人工验收真实窗口，补 `inspect` / `attend_event` 事件按钮和 VN 结果展示。
3. 后端线：把星灯祭事件的结算表、记忆模板和对话 fallback 继续收进 Event Skill 数据层，减少 Runtime 硬编码。
4. LLM 线：配置本地 `models.local.json` 或 `DEEPSEEK_API_KEY` 后跑 1 次真实 dialogue / event_reaction / night_reflection smoke，并记录延迟、fallback、成本估计。
5. 资产线：优先完成 batch 1b 的 `happy` / `troubled` 表情差分，再做地图小人和 UI 组件。
6. 文档线：每轮只更新 `agent_context`、`goal_board`、`current_status`、`open_questions` 中与已验证事实相关的最小内容。