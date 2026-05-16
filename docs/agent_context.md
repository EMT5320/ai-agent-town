---
status: active
owner_lane: context-governance
last_verified: 2026-05-16
startup_load: first-read
source_of_truth: true
scope: new-session entrypoint, boundaries, commands, and next steps
---

# Agent Valley 新对话入口

> 更新时间：2026-05-16
> 用途：下一轮新对话、无人值守开发、并行子代理任务的第一入口。

## 1. 当前入口

- 先读本文，再按任务线读取源文档。
- 长期方向以 `docs/project_vision.md` 为准。
- 当前事实以 `docs/current_status.md` 为准。
- 并行写入范围以 `docs/goal_board.md` 为准。
- 游戏内容剧本线以 `docs/game_content_storyline.md` 为准。
- 多层 Agent 设计细节见 `docs/agentic_game_design.md`。
- 视觉和资产细节见 `docs/art_direction.md`、`docs/asset_generation_prompts.md`、`assets/manifests/asset_manifest.json`。

## 2. 一句话定位

`Agent Valley` 是一个由 Godot 承担玩家体验、Python Agent Server 承担权威世界状态与 LLM NPC 的二次元轻幻想田园生活模拟 RPG。当前目标是把早期多 Agent 观察台收束成可玩、可扩展、可调试的第一天垂直切片。

## 3. 当前已验证事实

### 后端 Runtime / Director

- Python Agent Server 仍是权威世界状态入口。
- 已有 `GET /api/world/state`、`POST /api/player/action`、`/api/state`、`/api/model-config`、`POST /api/model-config/reload`、`/api/events`、`/api/developer`。
- 玩家动作已覆盖 `move`、`talk`、`give_gift`、`inspect`、`attend_event`。
- `backend/app/director/v0.py` 已落地 `WorldDigest`、`TensionDetector`、`SkillRouter`、`DirectorBeat`、`DirectorValidator`、`DirectorQueueManager`。
- Runtime 会运行规则版 Director v0，并写入 `director.digest_created`、`director.beat_created`、`director.beat_validated`、`director.beat_consumed`、`director.beat_discarded`。
- 已有单个 Event Skill：`event.starlight_festival_shortage`，定义位于 `backend/app/skills/event_skill_registry.py`。
- 星灯祭事件当前支持查看、选择、关系变化、记忆写入、事件反应、夜间反思和结算记录。

### Content Codex / NPC 深度卡

- 已新增 NPC 深度卡数据契约：`docs/npc_deep_card_spec.md`。
- 已新增写作工作流：`.windsurf/workflows/author-npc-deep-card.md`。
- 已新增内容数据层：`backend/app/content/`，当前包含 `kai`、`bram`、`mira`、`tomas`、`orren`、`lena` 6 份首发 NPC 深度卡。
- Runtime 初始化会把深度卡挂到 `agent.deepCard`；玩家对话 Prompt 会读取 `voiceStyle`、`archetype`、`speechQuirks`、`innerContradiction`。
- 送礼会根据深度卡 `giftReactions` 匹配反应档，玩家对话与送礼结果会返回 `relationshipStage`。
- `npm.cmd run content:check` 与 `npm.cmd run check` 已覆盖 NPC 深度卡结构、seed membership、资产引用 warning 和 smoke 集成。

### LLM / Debug

- 已有 `RuleBasedProvider` 和 OpenAI-compatible `CloudApiProvider`。
- 已有按 NPC / feature 选择 profile 的配置路径：`config/models.example.json` 为提交模板，`config/models.json` 和 `config/models.local.json` 为本机忽略配置；当前本机 `model:check` 显示 `activeProvider=cloud`、6 个 profiles、`localConfigLoaded=False`。
- Web 观察台已有 LLM 配置卡片，可查看 profile、路由、key 状态，支持热重载与一次对话 smoke。
- Debug 记录已包含 `providerMode`、`profileName`、`apiKeyConfigured`、`messages`、`rawText`、`parsed`、`executed`、`usage`、`latency`、`fallbackReason`。
- 前序验收已有一次 `CloudApiProvider` 真实 smoke 记录；本轮普通 `npm.cmd run check` 在当前沙箱触发 socket 权限 fallback，并通过 `[llm-smoke] fallback` 明示原因；提交态不包含密钥，fresh env 或无 key 沙箱会按规则跳过真实 LLM 调用。

### Godot 客户端

- `clients/godot/` 是 Godot 4.x 项目骨架。
- 已有 `ApiClient`、`WorldSync`、`AssetRegistry`。
- 主场景已接入 3 张地点背景、星灯祭事件 CG，以及玩家 + 6 个首发 NPC 的 `neutral` 半身立绘。
- 已支持地点按钮、背景切换、NPC 选择、VN 风格底部对话面板、聊天动作提交。
- 已新增事件区：展示 `activeEvents`、调用 `inspect` 查看星灯祭事件、渲染 choices、调用 `attend_event` 并展示 NPC 台词、关系变化、记忆写入和夜间反思摘要。
- 已接入地图角色层：玩家和 6 个首发 NPC 的 `map_idle` 小人、talk / gift / event 交互 marker、NPC 点击入口均已进入主场景。
- `npm.cmd run client:env` 和 `npm.cmd run client:run:check` 已通过；2026-05-16 主人已完成真实窗口人工验收，基本可用，未报告阻断问题。

### 资产与文档治理

- `assets/manifests/asset_manifest.json` 当前登记 31 条资产：21 条 `source_selected`、3 条 `style_anchor_candidate`、7 条 `pending_review`。
- 已同步到 Godot 的资产包括 3 张地点背景、星灯祭事件 CG、玩家 + 6 个首发 NPC 的 `neutral` 立绘、7 张地图小人和 3 张交互标记。
- `AssetRegistry` 已支持 `happy` / `troubled` 表情键兜底，缺图时回退 `neutral`。
- 表情差分、道具图标和拆分 UI 组件尚未进入 manifest 或 Godot registry。
- `AGENTS.md`、`CLAUDE.md`、`docs/README.md`、`docs/agent_context.md`、`docs/goal_board.md`、`docs/current_status.md`、`docs/open_questions.md` 是当前治理入口。

## 4. 当前边界

- 后端持有权威世界状态；Godot 只做表现层、本地交互缓存和 API 调用。
- LLM 只生成文本、结构化建议或工具意图；世界状态变更必须经过 Runtime 规则和校验。
- 密钥只放 `config/models.local.json` 或环境变量，不写入仓库。
- 资产入库必须登记来源、提示词引用、用途、状态、授权备注和 Godot 引用。
- 未在当前轮次复验的云端 LLM、表情差分、资产晋级和新增玩法循环只能记录为待验证项。
- `frontend/` 继续作为迁移期 Debug 观察台；正式 Web Debug 后续再收敛到 `web-admin/`。

## 5. 常用命令

```powershell
npm.cmd run context:check
npm.cmd run context:brief
npm.cmd run check
npm.cmd run content:check
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

- `npm.cmd run context:check` 校验 `AGENTS.md` / `CLAUDE.md`、核心文档元信息、任务线路由路径和明显状态冲突。
- `npm.cmd run context:brief` 生成下一轮新对话 brief。
- `npm.cmd run check` 覆盖 Python 编译、前端 JS、后端 smoke、资产 manifest、Godot 项目结构。
- `npm.cmd run content:check` 校验 6 份 NPC 深度卡、关系阶段、送礼反应、独白种子和资产引用。
- `npm.cmd run smoke` 重点验证后端 Runtime、Director v0、Event Skill、Debug 字段和 LLM smoke 跳过/执行/fallback 状态；强制真实云端通过时设置 `AGENT_TOWN_REQUIRE_REAL_LLM_SMOKE=1`。
- `npm.cmd run asset:check` 校验资产路径、prompt 引用、PNG 尺寸和 Godot 引用。
- `npm.cmd run client:env` 会用 Godot headless 打开项目，能捕获一部分脚本加载问题。
- `npm.cmd run client:run:check` 只检查 Godot 运行入口，不打开真实游戏窗口。
- `npm.cmd run client:run` 会打开真实 Godot 游戏窗口，适合人工验收。

## 6. 下一轮最短开发入口

1. 固定离线基线：运行 `npm.cmd run context:check`、`npm.cmd run check`、`npm.cmd run smoke`、`npm.cmd run asset:check`、`npm.cmd run client:env`、`npm.cmd run client:run:check`。
2. 文档收口：真实 Godot 窗口已由主人验收，状态文档需记录为 `manual accepted`，并把主要卡点切到玩法深度和内容驱动。
3. Godot 玩法线：把当前“背景图 + 简单 UI 点击”推进为可移动地图、角色站位、靠近交互、行动反馈和日程可视化。
4. 内容线：NPC 深度卡首批已入库，下一步优先把 `monologueSeeds` 接入夜间反思/RAG，或把 `gossipHooks` 接入谣言传播原型。
5. 后端线：把星灯祭事件的结算表、记忆模板和对话 fallback 继续收进 Event Skill 数据层，减少 Runtime 硬编码。
6. LLM / Debug 线：如切换模型、key 或 profile，重新跑真实 dialogue / event_reaction / night_reflection smoke，并记录延迟、fallback、成本估计。
7. 资产线：优先完成 batch 1b 的 `happy` / `troubled` 表情差分、UI 组件和玩法反馈图标。
