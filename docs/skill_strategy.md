# Agent Valley 项目 Skill 策略草案

> 更新时间：2026-05-15
> 用途：设计后续专用 Skill 的轻量结构，帮助新对话快速加载项目上下文和开发线规则。

## 1. 设计目标

- 让新对话快速进入 `Agent Valley` 项目状态。
- 让无人值守开发按开发线加载最小必要上下文。
- 让 Skill 保持轻量，只做路由、加载流程和判断规则。
- 动态状态统一读取 `docs/agent_context.md` 和 `docs/goal_board.md`。
- 避免把长篇愿景、规格、状态全文复制进 Skill。

## 2. 非目标

- 不安装全局 Skill。
- 不替代 `docs/project_vision.md`、`docs/current_status.md`、`docs/vertical_slice_spec.md` 等源文档。
- 不把密钥、模型私有配置或本地路径写进 Skill。
- 不让 Skill 自动修改后端、Godot 或资产文件。

## 3. 建议目录结构

```text
agent-valley/
├── SKILL.md
└── references/
    ├── backend-director.md
    ├── godot-client.md
    ├── asset-pipeline.md
    └── debug-console.md
```

## 4. `SKILL.md` 职责

`SKILL.md` 只保留三类信息：

1. 加载流程。
2. 开发线判断规则。
3. 安全边界和验收要求。

建议内容：

```markdown
# Agent Valley Skill

## 何时使用

- 用户在 `ai-agent-town-lab` 中开发 Agent Valley。
- 用户要求新对话接续项目上下文。
- 用户要求无人值守开发、并行子代理、Godot、Director、资产或 Debug 相关任务。

## 加载流程

1. 先读 `docs/agent_context.md`。
2. 如需并行分工，再读 `docs/goal_board.md`。
3. 根据任务类型选择一个 `references/*.md`。
4. 需要产品方向时读 `docs/project_vision.md`。
5. 需要切片验收时读 `docs/vertical_slice_spec.md`。
6. 最后查看 `git status --short`。

## 开发线判断

- Director、Event Skill、WorldDigest、记忆/RAG：读 `references/backend-director.md`。
- Godot、地图、VN 对话、窗口运行：读 `references/godot-client.md`。
- 生图、manifest、Godot 资产引用：读 `references/asset-pipeline.md`。
- Provider、Prompt、Debug Console、fallback：读 `references/debug-console.md`。

## 边界

- 后端保持权威世界状态。
- Godot 只做表现层和交互缓存。
- 资产必须进入 manifest。
- 密钥只读本地 overlay 或环境变量。
- 新增 API、事件、玩家动作、资产字段前先确认数据契约。

## 验收

- 默认运行 `npm.cmd run check`。
- 资产线追加 `npm.cmd run asset:check`。
- Godot 线追加 `npm.cmd run client:run:check`。
- 提交前运行 `git diff --check`。
```

## 5. `references/backend-director.md` 草案

用途：后端多层 Agent、Director、Event Skill、记忆/RAG 任务。

应包含：

- 必读文档：
  - `docs/agent_context.md`
  - `docs/agentic_game_design.md`
  - `docs/vertical_slice_spec.md`
  - `docs/current_status.md`
- 主要写入：
  - `backend/app/director/`
  - `backend/app/skills/`
  - `backend/app/memory/`
  - `backend/app/events/`
  - 相关测试
- 关键原则：
  - Runtime 持有权威世界状态。
  - LLM 输出只作为计划或工具调用意图。
  - `DirectorBeat` 必须可校验、可过期、可取消。
  - Event Skill 提供情境、参与者、约束、工具权限、后果类型和 Debug 字段。
  - 每个关键变化进入 EventStore。
- 最小验收：
  - 规则版 Director v0 能生成 1 个 `activate_event_skill` Beat。
  - Beat 过期或世界版本不匹配时不能改动世界状态。
  - 星灯祭链路保持玩家查看、选择、关系变化、记忆和夜间反思。
  - `npm.cmd run check` 通过。

## 6. `references/godot-client.md` 草案

用途：Godot 客户端、地图层、Visual Novel 对话层、真实窗口验证任务。

应包含：

- 必读文档：
  - `docs/agent_context.md`
  - `docs/game_client_environment.md`
  - `docs/vertical_slice_spec.md`
  - `docs/current_status.md`
- 主要写入：
  - `clients/godot/`
  - 必要时 `clients/godot/assets/`
- 关键原则：
  - Godot 读取 `GET /api/world/state`。
  - Godot 通过 `POST /api/player/action` 提交动作。
  - Godot 不保存权威世界状态。
  - 客户端错误提示要服务演示和调试。
  - 地图层和 VN 对话层保持清晰分工。
- 最小验收：
  - `npm.cmd run client:run:check` 通过。
  - `npm.cmd run check` 通过。
  - 如进行真实窗口验证，记录启动命令、观察结果和剩余缺口。

## 7. `references/asset-pipeline.md` 草案

用途：美术资产、生图、处理、manifest、Godot 引用任务。

应包含：

- 必读文档：
  - `docs/agent_context.md`
  - `docs/art_direction.md`
  - `docs/asset_generation_prompts.md`
  - `docs/vertical_slice_spec.md`
- 主要写入：
  - `assets/source/`
  - `assets/processed/`
  - `assets/manifests/`
  - 必要时 `clients/godot/assets/`
- 关键原则：
  - Codex 生图用于开发期资产生产。
  - 游戏运行时只读取静态资产。
  - 所有入库资产必须有 manifest 记录。
  - 资产记录包含用途、来源、提示词摘要、处理路径、Godot 引用、授权备注。
  - 先补表现语法资产，再追求特殊剧情资产。
- 最小验收：
  - `npm.cmd run asset:check` 通过。
  - `npm.cmd run check` 通过。

## 8. `references/debug-console.md` 草案

用途：Provider、Prompt、模型 profile、Debug Console、fallback 和可解释性任务。

应包含：

- 必读文档：
  - `docs/agent_context.md`
  - `docs/agentic_game_design.md`
  - `docs/current_status.md`
  - `config/models.example.json`
- 主要写入：
  - `backend/app/providers/`
  - Debug 决策记录结构
  - 迁移期 `frontend/`
  - 后续 `web-admin/`
- 关键原则：
  - 密钥只来自本地 overlay 或环境变量。
  - RuleBasedProvider 保持可用。
  - CloudApiProvider 失败时 Demo 可继续推进。
  - 高价值 LLM 调用记录 profile、messages、rawText、parsed、executed、usage、latencyMs、fallbackReason。
  - Debug / 研究控制台保留研究视角，不泄漏到主游戏叙事。
- 最小验收：
  - `npm.cmd run check` 通过。
  - 真实模型测试需要记录模型 profile、触发动作、输出摘要、fallback 情况和调试记录位置。

## 9. 动态状态读取策略

- Skill 每次启动都读 `docs/agent_context.md` 获取当前 brief。
- 并行任务每次启动都读 `docs/goal_board.md` 获取开发线状态。
- 只在需要深挖时读取源文档。
- references 只保存稳定规则和路径边界。
- 当前实现状态、最近下一步和验收结果只更新 docs，不写入 Skill。

## 10. 后续落地步骤

1. 保持本文作为草案，不安装全局 Skill。
2. 等项目治理文档稳定后，在本地 Skill 目录按上述结构创建 `agent-valley/`。
3. 先只放 `SKILL.md` 和 4 个 references。
4. 用一次后端 Director 任务、一轮 Godot 任务和一次资产任务试运行。
5. 根据试运行结果缩短 references，避免 Skill 膨胀。
