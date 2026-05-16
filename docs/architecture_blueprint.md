---
status: active
owner_lane: architecture
last_verified: 2026-05-16
startup_load: on-demand
source_of_truth: true
scope: system architecture, module boundaries, and client-server data flow
---

# 架构蓝图

## 总体结构

```text
Godot Game Client
  -> HTTP / WebSocket
Python Agent Server
  -> Director System / Event Skill Layer / Provider / Memory / Event Store / World State
Web Debug Console
  -> HTTP / WebSocket
Codex Visual Asset Pipeline
  -> Static Game Assets
```

## 模块职责

### Godot Game Client

负责玩家直接体验：

- 地图渲染
- 玩家移动
- NPC 可视化
- 玩家和 NPC 地图小人表现
- 交互区域
- 对话 UI
- Visual Novel 半身立绘与表情层
- 送礼 UI
- 事件 CG 展示
- 时间、天气、地点状态展示
- 从后端同步 NPC 位置、状态和对话事件

客户端不保存权威世界状态。玩家看到的画面由后端状态驱动，本地只做表现层缓存。

### Python Agent Server

负责世界权威状态与 Agent Runtime：

- 时间推进
- 世界状态读写
- Director Beat 队列消费
- Event Skill 激活与结算
- NPC 调度
- 日程系统
- Agent 上下文构建
- LLM / 规则 Provider 调用
- 行动解析
- 工具行动执行
- 玩家动作处理
- 记忆写入与反思
- 关系变化
- 事件流广播
- 运行日志与调试记录落盘

### Director System

负责低频节奏规划和事件 Skill 调度。导演层由一组可校验的规划组件构成：

- `WorldDigestBuilder`：把世界状态、关系张力、近期事件和玩家位置压缩成稳定摘要。
- `TensionDetector`：扫描高冲突关系、资源短缺、健康风险和玩家附近压力源。
- `SkillRouter`：根据触发条件筛选候选事件 Skill。
- `DirectorPlanner`：在高价值节点调用强模型或规则规划下一组 Director Beat。
- `DirectorValidator`：校验 Director Beat schema、权限、世界版本和生效窗口。
- `DirectorQueueManager`：把可执行 Beat 放入队列，按 tick 或时间段消费。

Director System 只提出阶段性目标、候选事件和 NPC brief。世界状态仍由 Runtime 执行合法工具后修改。

### Event Skill Layer

负责把传统固定剧情拆成可运行情境模块：

- 常驻轻量 Skill Manifest：触发条件、参与者、标签、资产提示。
- 触发后完整 Skill：导演 brief、NPC brief、玩家动作、工具权限、约束边界、后果类型。
- 生命周期：`dormant -> candidate -> loaded -> active -> resolved -> reflected -> archived`。

事件 Skill 给 Agent 提供情境压力，不强制 NPC 走固定结局。

### Web Debug Console

负责研究、调试与演示讲解：

- 查看世界快照
- 查看 NPC 状态
- 查看 Prompt / messages
- 查看模型原始输出
- 查看解析后的行动
- 查看工具执行结果
- 查看记忆写入
- 查看关系变化
- 查看 Director Beat 队列
- 查看事件 Skill 触发条件与加载结果
- 注入事件
- 暂停、继续、单步推进
- 导出运行记录与调试记录

### Codex Visual Asset Pipeline

负责开发期美术生产：

- 按 `docs/art_direction.md` 生成二次元轻幻想轻异世界原始图
- 先生成风格锁定图，再生成角色、场景、CG 和 UI
- 人工挑选可用图
- 裁切、压缩、统一命名
- 生成资产清单
- 导入 Godot
- 记录资产来源、提示词摘要、表情差分和审稿备注

游戏运行时只读取本地静态资产。

## 数据流

### 初始加载

```text
Godot Client
  -> GET /api/world/state
Python Server
  -> 返回地图、地点、NPC、玩家、时间、当前事件
Godot Client
  -> 根据状态实例化角色与 UI
```

### 玩家与 NPC 对话

```text
玩家点击 NPC
  -> Godot 打开交互菜单
玩家选择聊天主题
  -> POST /api/player/action
Python Server
  -> 构建 NPC 上下文
  -> 调用 Provider
  -> 解析回复与行动
  -> 更新关系与记忆
  -> 写入事件流
  -> 返回对话结果
Godot Client
  -> 显示对话气泡与角色表情
Web Debug Console
  -> 展示 Prompt、输出、记忆与关系变化
```

### NPC 自主行动

```text
游戏时间推进
  -> Scheduler 选择需要决策的 NPC
  -> 构建上下文
  -> LLM Provider 生成计划或行动
  -> Action Executor 执行
  -> World State 更新
  -> Event Store 记录
  -> WebSocket 推送给 Godot 和 Debug Console
```

### Director Beat 异步规划

```text
时间段开始 / 关键玩家行为 / 事件结束
  -> WorldDigestBuilder 生成摘要
  -> TensionDetector 找到关系张力和候选压力源
  -> SkillRouter 筛选候选 Event Skills
  -> DirectorPlanner 低频生成 Director Beat
  -> DirectorValidator 校验 schema、世界版本、生效窗口和权限
  -> DirectorQueueManager 入队
  -> Runtime 在合适 tick 消费 Beat
  -> 相关 NPC 收到局势 brief 和可用工具
```

如果 Director Beat 返回太晚、世界版本落后、过期或命中取消条件，Runtime 会丢弃或降级为建议，并把原因写入 Debug 事件。

### Event Skill 渐进式加载

```text
常驻 Skill Manifest
  -> 只暴露 trigger、participants、tags、assetHints
触发条件满足
  -> 加载完整 Skill
  -> 分发 directorBrief 和 npcBriefs
  -> 开放该事件允许的工具行动
  -> 事件结算后写入关系变化、记忆和反思
```

### 夜间反思

```text
进入夜晚
  -> 收集每个 NPC 当天相关事件
  -> 生成日记 / 反思摘要
  -> 更新长期记忆
  -> 更新关系趋势
  -> 生成每日小镇摘要
```

## 核心后端概念

### World State

保存权威世界状态：

- 当前日期与时间段
- 天气
- 地点列表
- NPC 列表
- 玩家状态
- 物品状态
- 事件状态
- 关系图谱

### Director Beat

导演层的基本输出单位，代表一个异步生成、可验证、可过期的阶段性世界指令。

关键字段：

- `directiveId`
- `worldVersion`
- `validFromTick`
- `expiresAtTick`
- `priority`
- `beatType`
- `targetAgents`
- `goal`
- `allowedSkills`
- `directorBrief`
- `npcBriefs`
- `constraints`
- `cancelIf`
- `assetHints`

Director Beat 不直接改世界，只进入队列，由 Runtime 在合法时间窗口消费。

### Event Skill

事件 Skill 是情境模块，提供可运行局势、工具边界和后果类型。

最低字段：

- `skillId`
- `title`
- `trigger`
- `participants`
- `tags`
- `directorBrief`
- `npcBriefs`
- `playerActions`
- `tools`
- `outcomeTypes`
- `constraints`
- `assetHints`
- `debugFields`

### Agent Profile

NPC 的长期身份信息：

- 姓名
- 游戏内显示名
- 简称
- 年龄
- 性别认同
- 职业
- 性格
- 背景故事
- 长期目标
- 喜好与厌恶
- 重要关系
- 恋爱铺垫标签
- 视觉原型
- 说话风格
- 地图小人引用
- 半身立绘引用
- 表情差分引用
- 视觉资产引用

### Agent Runtime State

NPC 的动态状态：

- 当前位置
- 当前行动
- 今日计划
- 情绪
- 体力
- 金钱
- 健康
- 当前关注对象
- 最近交互对象

### Memory Store

建议分三层：

1. **事件记忆**：原始事件或压缩事件。
2. **关系记忆**：某 NPC 对另一个角色的长期印象。
3. **自我反思**：夜间生成的日记、总结和目标调整。

### Event Store

统一记录所有可回放事件：

- 玩家动作
- NPC 行动
- NPC 对话
- 工具调用
- 记忆写入
- 关系变化
- 世界状态变化
- Provider 调用摘要
- 事件 CG 触发记录

## API 草案

### REST

```text
GET  /api/world/state
GET  /api/npcs
GET  /api/npcs/{npc_id}
GET  /api/npcs/{npc_id}/memories
GET  /api/events/recent
POST /api/player/action
POST /api/dev/tick
POST /api/dev/pause
POST /api/dev/resume
POST /api/dev/inject-event
GET  /api/debug/turns/{turn_id}
GET  /api/export/run-log
```

### WebSocket

```text
WS /api/stream
```

推送事件类型：

```text
world.tick
npc.moved
npc.spoke
npc.action_started
npc.action_finished
memory.created
relationship.changed
event.created
debug.turn_recorded
```

## Godot 客户端结构草案

```text
clients/godot/
├── project.godot
├── scenes/
│   ├── main.tscn
│   ├── town_map.tscn
│   ├── player.tscn
│   ├── npc.tscn
│   ├── dialogue_box.tscn
│   └── event_card.tscn
├── scripts/
│   ├── api_client.gd
│   ├── world_sync.gd
│   ├── player_controller.gd
│   ├── npc_view.gd
│   ├── dialogue_controller.gd
│   └── event_bus.gd
├── assets/
│   ├── characters/
│   ├── locations/
│   ├── ui/
│   └── cg/
└── data/
    └── asset_manifest.json
```

## 仓库演进建议

```text
ai-agent-town-lab/
├── backend/                 # Python Agent Server
│   ├── app/director/         # Director Beat、WorldDigest、Skill 路由和队列
│   └── app/skills/           # Event Skill schema 与事件数据
├── clients/
│   └── godot/               # Godot 游戏客户端
├── web-admin/               # Debug / 研究控制台
├── frontend/                # 旧观察台，迁移期保留
├── assets/
│   ├── source/              # Codex 生图原始资产
│   ├── processed/           # 处理后资产
│   └── manifests/           # 资产清单
├── docs/
├── experiments/
└── scripts/
```

## 架构风险

### Godot 学习成本

缓解方式：

- 先做 2～3 天 Spike。
- Godot 只承担表现层。
- 复杂规则继续在 Python 后端。

### 网络同步复杂度

缓解方式：

- 第一版采用低频同步。
- NPC 移动可以离散化到地点级或格子级。
- 优先保证可解释性和稳定性。

### LLM 调用成本

缓解方式：

- 强模型只用于低频高价值导演规划、复杂事件复盘和多角色冲突判断。
- 高频移动、纯日程、合法性校验和简单触发检测使用规则或缓存。
- 玩家对话、普通 NPC 反应和摘要优先使用低延迟模型。
- Director Beat 异步生成，过期或世界版本不匹配时丢弃或降级为建议。
- Debug 面板记录 token、成本和延迟。

### 导演层单点风险

缓解方式：

- Director System 拆成摘要、张力检测、Skill 路由、规划、校验和队列多个部件。
- 模型只能输出 Director Beat，不能直接修改 World State。
- 每个 Beat 带 `worldVersion`、生效窗口、取消条件和约束。
- Runtime 使用纯代码 Validator 和工具权限系统控制落地。
- 强模型失败时继续使用当前 brief、规则 fallback 或跳过本轮规划。

### 美术一致性

缓解方式：

- 先以 `docs/art_direction.md` 固定二次元轻幻想轻异世界美术风格。
- 每个 NPC 保存固定视觉设定、主色、标志物和表情差分规则。
- 同一角色的立绘、头像和表情差分必须保持发型、服饰、瞳色和配饰一致。
- 每张资产记录提示词摘要、用途、生成工具、审稿备注和 Godot 导入路径。
- 游戏内尽量使用静态图和少量差分。
