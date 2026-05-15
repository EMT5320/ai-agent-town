# Agent Valley 目标看板

> 更新时间：2026-05-16
> 用途：为无人值守开发、并行子代理和下一轮收口提供状态、写入范围和验收命令。

## 1. 状态标记

- `done`：本轮已核对，当前目标完成。
- `partial`：最小闭环已落地，仍有明确后续缺口。
- `blocked`：需要人工配置、真实窗口、API key 或上游资产后继续。
- `watch`：当前只读跟踪，暂不作为主线扩写。

## 2. 本轮验收证据

- `npm.cmd run check`：通过，包含 `[python-smoke] ok`、`[asset-manifest-check] ok`、`[godot-check] ok`；`llm-smoke` 因无本地 key / overlay 明确跳过。
- `npm.cmd run smoke`：通过，Director v0、Event Skill、Debug 字段链路可离线跑通；`llm-smoke` 明确跳过。
- `npm.cmd run asset:check`：通过。
- `npm.cmd run client:env`：通过，Godot 4.6.2 headless 项目打开检查通过。
- `npm.cmd run client:run:check`：通过 DryRun，只验证运行入口和 Godot 参数。
- `git diff --check`：通过；当前仅有 CRLF/LF 提示，不阻塞。

## 3. 本轮收口状态

### 已完成

- 文档治理入口已落地：`docs/agent_context.md`、`docs/goal_board.md`、`docs/current_status.md`、`docs/open_questions.md`。
- 规则版 Director v0 最小闭环已落地并由 smoke 覆盖。
- 单个星灯祭 Event Skill schema / registry 已落地。
- LLM profile、provider fallback 和 Debug 字段记录路径已落地。
- Godot P0 客户端已接入背景、neutral 立绘、NPC 选择和聊天提交。
- Godot 事件交互代码已接入：`activeEvents` 事件区、`inspect` 查看、choices 渲染、`attend_event` 提交、VN 结果展示。
- Godot `AssetRegistry` 已接入星灯祭事件 CG，并支持 `happy` / `troubled` 表情回退到 `neutral`。
- 资产 manifest 和 Godot registry 已覆盖首批背景、事件 CG 与 neutral 立绘。

### 部分完成

- Godot 事件交互已通过代码检查、headless 检查和 dry-run，真实窗口体验仍待主人手动验收。
- Godot 地图层仍是背景 + 按钮层，尚未升级为正式地图小人/节点交互。
- Event Skill 仍只有星灯祭单技能，结算逻辑仍有 Runtime 硬编码。
- LLM profile 可配置，真实云端 smoke 尚未执行。
- 资产批次只完成到首批背景、事件 CG、neutral 立绘和风格参考；batch 1b 尚未入库。

### 阻塞项

- 真实 LLM 验证需要本地 `config/models.local.json` 或环境变量 API key。
- 真实 Godot 窗口体验需要人工运行 `npm.cmd run start` + `npm.cmd run client:run`。
- 表情差分、地图小人、UI 组件需要继续生成和人工筛选。

## 4. 开发线看板

| 开发线 | 当前状态 | 下一步 | 主要写入范围 | 禁止/谨慎范围 | 验收命令 |
| --- | --- | --- | --- | --- | --- |
| Godot 客户端 | partial | 按人工窗口验收结果修体验问题；随后推进基础地图节点、角色站位、交互区域 | `clients/godot/`、必要时 `clients/godot/assets/` | 不在客户端保存权威世界状态；不把后端结算规则复制进 GDScript | `npm.cmd run client:env`、`npm.cmd run client:run:check`、`npm.cmd run check`，人工 `client:run` |
| 后端 Director / Event Skill | partial | 将星灯祭结算表、记忆模板和 fallback 台词继续迁入 Event Skill 数据；补 Skill 复用测试 | `backend/app/director/`、`backend/app/skills/`、`backend/app/runtime/agent_runtime.py`、相关测试 | 不让 LLM 直接改世界状态；不破坏旧 `/api/state` 与 Debug 观察台 | `npm.cmd run smoke`、`npm.cmd run check` |
| 资产管线 | partial | 完成 batch 1b 表情差分，随后补地图小人与 UI 组件；先补 prompt/manifest，再生成或筛选图 | `assets/source/`、`assets/processed/`、`assets/manifests/`、`clients/godot/assets/` | 不覆盖原图；不提交来源不清的资产；不把未生成资产标成 `source_selected` | `npm.cmd run asset:check`、`npm.cmd run check` |
| LLM / Debug | partial | 配置本地 key 后执行真实 dialogue / event_reaction / night_reflection smoke；记录延迟、成本、fallback | `backend/app/providers/`、`backend/app/providers/context_builder.py`、Debug 记录结构、迁移期 `frontend/` | 不提交密钥；不隐藏 token、延迟、错误；不把跳过的 live smoke 写成通过 | `npm.cmd run smoke`、真实 LLM 手动记录 |
| Web Debug Console | watch | 等事件 UI 和 Skill 链路更稳定后展示 Director 队列、Skill、fallback、成本 | 迁移期 `frontend/`，后续 `web-admin/` | 不阻塞 Godot 主体验；不泄漏玩家叙事视角 | `npm.cmd run check` |
| 文档与治理 | done | 每轮结束只更新入口、状态、下一步和仍需验证问题 | `docs/agent_context.md`、`docs/goal_board.md`、`docs/current_status.md`、`docs/open_questions.md` | 不复制源设计长文；不把未验证能力写成完成 | `npm.cmd run check`、`git diff --check` |

## 5. 人工验收清单

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

## 6. 并行任务拆分建议

- Godot worker：只改 `clients/godot/`，目标是根据人工验收结果修 UI 体验，并推进基础地图节点。
- 后端 worker：只改 Director / Skill / Runtime 相关最小范围，目标是减少星灯祭硬编码并补测试。
- 资产 worker：只改资产目录、manifest 和必要 Godot asset mirror，目标是 batch 1b。
- Reviewer：只读核对契约、过标表述、验收输出和工作区状态。

不要让多个 worker 同时修改 `docs/current_status.md`、`docs/agent_context.md`、`docs/goal_board.md`。

## 7. 每轮交接格式

```markdown
## 本轮开发线

- 线别：
- 写入范围：
- 已完成：
- 部分完成：
- 阻塞项：
- 验收命令：
- 风险：
- 下一步：
```

## 8. 下一轮推荐排程

1. 主人先做 Godot 真实窗口人工验收。
2. Godot 客户端：按人工反馈修交互体验，再推进基础地图节点。
3. 资产：batch 1b 表情差分入 prompt/manifest，随后生成或筛选图片。
4. 后端：星灯祭 Skill 数据化第二步，减少 Runtime 硬编码。
5. LLM / Debug：配置本地 key 后完成一次真实 smoke。
