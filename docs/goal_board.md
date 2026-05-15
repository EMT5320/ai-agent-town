# Agent Valley 目标看板

> 更新时间：2026-05-15
> 用途：为无人值守开发和并行子代理分配清晰的开发线、写入范围和验收命令。

## 1. 状态标记

- `ready`：可直接开工，已有清晰输入和验收方式。
- `blocked`：缺少人工确认、环境验证或上游契约。
- `in-progress`：已有局部实现，下一轮继续收束。
- `watch`：当前可读可评审，暂不主动扩写。

## 2. 总体优先级

1. 保持 `npm.cmd run check` 可通过。
2. 先让 Godot 真实窗口和后端游戏 API 形成稳定闭环。
3. 再补规则版 Director v0 与 Event Skill 数据化。
4. LLM 接入优先服务聊天、事件反应和夜间反思三个高价值节点。
5. 资产管线持续补齐 manifest、Godot 引用和来源记录。

## 3. 开发线看板

| 开发线 | 当前状态 | 下一步 | 主要写入范围 | 禁止/谨慎范围 | 验收命令 |
| --- | --- | --- | --- | --- | --- |
| 后端多层 Agent | ready | 定义 `WorldDigest`、`DirectorBeat`、`EventSkill` schema；实现规则版 Director v0 | `backend/app/director/`、`backend/app/skills/`、`backend/app/memory/`、`backend/app/events/`、相关测试 | 不让 LLM 直接改世界状态；不破坏旧 `/api/state` 与 Debug 观察台 | `npm.cmd run check`、`npm.cmd run smoke` |
| Godot 客户端 | in-progress | 用真实窗口验证主场景；完善地图层、NPC 选择和 VN 对话层 | `clients/godot/`、必要时 `clients/godot/assets/` | 不在客户端保存权威世界状态；不把后端规则复制进 GDScript | `npm.cmd run client:run:check`、`npm.cmd run check` |
| 资产管线 | in-progress | 补地图小人、表情差分、UI 组件；维护 manifest | `assets/source/`、`assets/processed/`、`assets/manifests/`、必要时 `clients/godot/assets/` | 不接入运行时图片生成 API；不提交来源不清的资产 | `npm.cmd run asset:check`、`npm.cmd run check` |
| LLM / Debug | ready | 实测 DeepSeek V4 Flash profile；补聊天、事件反应、夜间反思 Prompt 与 Debug 字段 | `backend/app/providers/`、Debug 记录结构、迁移期 `frontend/` 或后续 `web-admin/` | 不提交密钥；不绕过 fallback；不隐藏 token/延迟/错误 | `npm.cmd run check`，必要时记录手动 LLM 测试结果 |
| 内容数据 | ready | 结构化 6 NPC、3 地点、首日事件、恋爱铺垫字段 | `backend/app/world/seed_data.py`、未来数据文件、事件 Skill 数据 | 新增内容前先确认数据契约；避免把内容写死进多个模块 | `npm.cmd run check`、相关 smoke |
| Web Debug Console | watch | 等 Director / Skill 链路稳定后补队列、Skill、fallback 视图 | 迁移期 `frontend/`，后续 `web-admin/` | 不阻塞 Godot 主体验；不泄漏主游戏叙事视角 | `npm.cmd run check` |
| 文档与治理 | ready | 保持 `agent_context`、`goal_board`、`skill_strategy` 更新 | `docs/agent_context.md`、`docs/goal_board.md`、`docs/skill_strategy.md`、`scripts/build_agent_context.py` | 不删除源设计文档；不把长文档复制到 Skill | `npm.cmd run check`、`git diff --check` |

## 4. 并行任务拆分建议

### 4.1 单轮最多并行

- 1 个后端多层 Agent worker。
- 1 个 Godot 客户端 worker。
- 1 个资产管线 worker。
- 1 个 reviewer 只读复核契约、篇幅和验收。

### 4.2 后端多层 Agent worker 输入

- 必读：`docs/agent_context.md`、`docs/agentic_game_design.md`、`docs/vertical_slice_spec.md`。
- 输出：schema、规则版组件、Debug 记录、测试。
- 验收：能离线生成并消费 1 个 `activate_event_skill` Beat。
- 重点：Beat 过期或世界版本不匹配时，不能改动世界状态。

### 4.3 Godot 客户端 worker 输入

- 必读：`docs/agent_context.md`、`docs/game_client_environment.md`、`docs/vertical_slice_spec.md`。
- 输出：真实窗口可验证的地图层、NPC 选择、聊天提交、错误提示。
- 验收：`client:run:check` 通过，必要时给出手动窗口验证记录。
- 重点：客户端只通过 API 读写后端。

### 4.4 资产管线 worker 输入

- 必读：`docs/art_direction.md`、`docs/asset_generation_prompts.md`、`docs/vertical_slice_spec.md`。
- 输出：资产文件、处理文件、manifest 记录、Godot 引用。
- 验收：`asset:check` 通过。
- 重点：每张资产都有来源、用途、提示词摘要和授权备注。

### 4.5 LLM / Debug worker 输入

- 必读：`docs/agent_context.md`、`docs/agentic_game_design.md`、`config/models.example.json`。
- 输出：功能 profile、Prompt 模板、结构化输出解析、Debug 字段。
- 验收：规则 fallback 可跑，真实模型测试有记录。
- 重点：密钥只来自本地 overlay 或环境变量。

## 5. 每轮交接格式

```markdown
## 本轮开发线

- 线别：
- 写入范围：
- 已完成：
- 未完成：
- 验收命令：
- 风险：
- 下一步：
```

## 6. 当前最近推荐排程

1. 文档治理线：完成本文、`agent_context` 和 `skill_strategy`。
2. Godot 客户端线：运行真实窗口，记录主场景仍缺的交互体验。
3. 后端多层 Agent 线：落地 `WorldDigest` / `DirectorBeat` / `EventSkill` 最小 schema。
4. 后端多层 Agent 线：规则版 Director v0 激活星灯祭 Event Skill。
5. LLM / Debug 线：1 个 NPC 聊天真实模型测试。
6. 资产管线线：补地图小人和表情差分。

## 7. 更新规则

- 新增开发线时，必须写清写入范围和验收命令。
- 状态变化时，同步更新“当前状态”和“下一步”。
- 完成无人值守任务后，把下一轮入口写回本文。
- 长期愿景变化需要先更新 `docs/project_vision.md`，再更新本文。
