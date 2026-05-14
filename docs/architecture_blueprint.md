# 架构蓝图

## 总体结构

```text
Godot Game Client
  -> HTTP / WebSocket
Python Agent Server
  -> Provider / Memory / Event Store / World State
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
- 交互区域
- 对话 UI
- 送礼 UI
- 事件 CG 展示
- 时间、天气、地点状态展示
- 从后端同步 NPC 位置、状态和对话事件

客户端不保存权威世界状态。玩家看到的画面由后端状态驱动，本地只做表现层缓存。

### Python Agent Server

负责世界权威状态与 Agent Runtime：

- 时间推进
- 世界状态读写
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
- 注入事件
- 暂停、继续、单步推进
- 导出运行记录与调试记录

### Codex Visual Asset Pipeline

负责开发期美术生产：

- 使用 Codex 应用生图生成原始图
- 人工挑选可用图
- 裁切、压缩、统一命名
- 生成资产清单
- 导入 Godot
- 记录资产来源与提示词摘要

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

### Agent Profile

NPC 的长期身份信息：

- 姓名
- 年龄
- 职业
- 性格
- 背景故事
- 长期目标
- 喜好与厌恶
- 重要关系
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

- 首版直接使用 DeepSeek V4 Flash 验证关键体验。
- 高频移动和纯日程可以在后续回到规则或缓存。
- 玩家对话、重大事件反应和夜间反思优先使用 LLM。
- Debug 面板记录 token、成本和延迟。

### 美术一致性

缓解方式：

- 先确定统一美术风格。
- 每个 NPC 保存固定视觉设定。
- 每张资产记录提示词摘要和用途。
- 游戏内尽量使用静态图和少量差分。

