# 白天整合交接与后续路线准备

> 日期：2026-05-16
> 范围：白天后端 agent 线与美术资产线整合到 `main`，并为晚上客户端线、LLM 线准备可直接开工的目标。

## 1. 已完成整合

| 线别 | 来源分支 | 主仓库整合提交 | 结果 |
| --- | --- | --- | --- |
| 后端 agent 线 | `codex/day-backend-agent` | `a61a16c merge: integrate day backend agent line` | Debug / Memory API、RAG-lite evidence、玩家影响链、Godot action contract 检查已进入 `main`。 |
| 美术资产线 | `codex/day-art-assets` | `6e77406 merge: integrate day art asset line` | 7 张地图小人、3 张交互标记、prompt、manifest、Godot 资源镜像已进入 `main`。 |
| Godot import 元数据 | 整合后本地导入 | `1de91f6 chore: import Godot map sprite metadata` | 新增 sprite 的 `.png.import` 已跟随 Godot 项目提交，避免下一次打开项目产生未跟踪差异。 |

当前 `main` 保留两个白天 worktree 分支作为可追溯来源，后续开发请从已整合后的 `main` 新开分支或 worktree。

## 2. 整体验收证据

已在主仓库运行：

```powershell
npm.cmd run check
npm.cmd run asset:check
npm.cmd run client:env
npm.cmd run client:run:check
git diff --check HEAD~2..HEAD
```

验收结果：

- `[python-smoke] ok`，包含 10 agents、59 events、RAG-lite follow-up evidence、11 条 influence events、2 条 fallback items。
- `[asset-manifest-check] ok`。
- `[godot-check] ok {'files': 7}`。
- `client:env` 识别到 Godot `4.6.2.stable.official.71f334935`。
- `client:run:check` DryRun 通过，确认运行入口和 Godot 参数。
- `llm-smoke` 因未配置本地 key / overlay 跳过；这仍是晚上 LLM 线的人工配置前置项。

## 3. 当前资产状态

`assets/manifests/asset_manifest.json` 当前共有 31 条记录：

- `source_selected`：21 条。
- `style_anchor_candidate`：3 条，即第一批地图小人锚点。
- `pending_review`：7 条，即四张重画地图小人和三张交互标记。

地图小人当前判断：

- `player_farmer_map_idle`、`npc_mira_map_idle`、`npc_tomas_map_idle` 是风格锚点候选。
- `npc_orren_map_idle`、`npc_lena_map_idle`、`npc_kai_map_idle`、`npc_bram_map_idle` 已重画到可验收方向。
- 所有新增地图小人暂时保持 `pending_review` 或 `style_anchor_candidate`，等待主人在 Godot 实机窗口确认后再晋级 `source_selected`。

## 4. 晚上优先路线

### 路线 A：Godot 客户端地图层接入

目标：把白天产出的地图小人真正放进可运行窗口，形成“地图观察 + NPC 交互入口 + VN 结果层”的首版完整体验。

建议写入范围：

- `clients/godot/`
- `clients/godot/assets/sprites/`
- 必要时更新 `scripts/check_godot_project.py`

核心任务：

1. 在主场景增加基础地图角色层，放置玩家和 6 个首发 NPC 的 `map_idle` sprite。
2. 给 NPC 节点绑定后端 `agentId`、当前位置、可交互状态。
3. 点击 NPC 或附近按钮时复用现有 `talk` / `give_gift` / `inspect` / `attend_event` 后端动作。
4. 使用 `interaction_marker_talk` / `gift` / `event` 做轻量交互提示，实机确认可读性。
5. 继续保持后端权威状态，客户端只显示与提交动作。

验收：

```powershell
npm.cmd run client:env
npm.cmd run client:run:check
npm.cmd run check
```

人工窗口检查：

```powershell
npm.cmd run start
npm.cmd run client:run
```

确认点：

- 地图中能看到玩家和 6 个 NPC。
- NPC 角色主体在默认窗口缩放下可读。
- 点击 NPC 后能进入现有 VN 对话层。
- 事件 marker 能引导玩家查看星灯祭事件。
- 后端 state 刷新后客户端不会丢失当前选中/展示状态。

### 路线 B：LLM 真实 smoke 与 Debug 视图准备

目标：配置本地 key 后跑一次真实 cloud provider 链路，确认 dialogue / event_reaction / night_reflection 的输出质量、延迟、fallback 和成本字段。

建议写入范围：

- `config/models.example.json` 仅在需要新增模板字段时改。
- `backend/app/providers/`
- `backend/app/providers/context_builder.py`
- `scripts/smoke_test.py`
- 需要时补 `docs/model_profile_template_guide.md`

禁止提交：

- `config/models.local.json`
- API key
- 任何包含真实密钥的日志

验收：

```powershell
npm.cmd run smoke
npm.cmd run check
```

人工记录点：

- 使用的 provider / model profile。
- 三类 feature 的延迟范围。
- 是否出现 fallbackReason。
- NPC 台词是否符合二次元轻幻想田园语气。
- 夜间反思是否能稳定写入可解释 memory。

### 路线 C：后端 Skill 数据化第二步

目标：继续把星灯祭事件的结算模板、记忆模板、fallback 台词从 Runtime 硬编码迁入 Event Skill 数据。

建议在客户端首轮实机后再开工，因为客户端会暴露最直接的契约缺口。

验收：

```powershell
npm.cmd run smoke
npm.cmd run check
```

## 5. 推荐 worktree / goal 拆分

晚上推荐从当前 `main` 新开两条互不重叠的开发线：

| 开发线 | 建议分支 | 写入范围 | 目标 |
| --- | --- | --- | --- |
| 客户端地图线 | `codex/evening-client-map` | `clients/godot/`、`scripts/check_godot_project.py` | 首版地图小人可见、可点击、可触发 VN 交互。 |
| LLM Debug 线 | `codex/evening-llm-debug` | `backend/app/providers/`、`backend/app/providers/context_builder.py`、`scripts/smoke_test.py`、相关 docs | 完成真实 LLM smoke 和 Debug 证据记录。 |

两条线同时跑时不要共同修改 `docs/current_status.md`、`docs/goal_board.md`，统一由主对话在收口阶段更新。

## 6. 第一轮可直接投喂的 goal

### 客户端地图线 goal

```text
在当前 Agent Valley 主仓库基础上推进 Godot 客户端地图层。只修改 clients/godot/ 和必要的 Godot 检查脚本。目标是把 player_farmer_map_idle 与 6 个 NPC map_idle sprite 放入主场景地图层，保留现有 VN 对话层和后端 API 契约；点击或选择 NPC 时能复用现有 talk/give_gift/inspect/attend_event 流程。交互 marker 可作为 pending_review 视觉提示使用。完成后运行 npm.cmd run client:env、npm.cmd run client:run:check、npm.cmd run check，并报告人工窗口需要检查的点。
```

### LLM Debug 线 goal

```text
在当前 Agent Valley 主仓库基础上推进真实 LLM smoke 和 Debug 准备。不要提交任何密钥或 config/models.local.json。先检查现有 provider/profile/context_builder/debug 字段，补齐真实 cloud provider 验收所需的最小检查和文档说明。若本地没有 API key，保持离线 smoke 通过，并提供明确的手动配置与验证步骤。完成后运行 npm.cmd run smoke、npm.cmd run check，并报告真实 LLM 验收仍需主人提供或设置的本地环境变量。
```
