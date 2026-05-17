---
status: active
owner_lane: planning
last_verified: 2026-05-17
startup_load: on-demand
source_of_truth: true
scope: production roadmap, axis decision, phase 1 deep design
---

# Agent Valley 生产化路线图

> 制定时间：2026-05-17
> 触发原因：项目当前体验被诊断为"UI 点击看板"——后端有厚实的 Director / Skill / NPC 深度卡 / 记忆 / gossip schema，但客户端只是"表单提交+状态展示"，玩家做的事不在 NPC 之间传播，时间是回合制按钮，NPC 不在地图上"做事"。本文档作为新的事实源，取代 `docs/implementation_plan.md` 作为路线执行依据。
> 适用边界：本文档定义阶段轴、阶段验收和阶段 1 详细技术方案；阶段 2-6 只给方向，等触发时再细化。

## 1. 方向决策（2026-05-17）

四条主流派路线中，本项目选定 **A+C 复合**：

- **主轴 C：沙盒导演 / 操纵**——玩家小动作能引爆 NPC 社会的连锁反应。
- **副轴 A：社会模拟**——支撑主轴的"涌现"基础，让 NPC 真的在生活。
- 暂缓的轴：B（陪伴/恋爱深度互动）保留为阶段 4 自然涌现的副产物，不另起系统；D（强叙事沉浸）保留为 Director / Event Skill 的能力延伸。

### 1.1 30 秒 Demo 验收标尺

任何"已达成阶段 N"的论断，必须能在 30 秒视频内向不懂技术的观众证明该阶段的玩家体感。
具体指标见每阶段"玩家体感验收"段。

### 1.2 客户端推翻范围

- 推翻：`main.gd` / `main.tscn` 的 UI 主导布局（页签 + NPC 列表 + 事件列表 + VN 面板）、"按钮切换地点"概念、`end_phase` 回合制按钮。
- 保留：`api_client.gd` / `world_sync.gd` / `asset_registry.gd` 三个底层组件、全部资产、`.import` 元数据、Debug API / Web 观察台、后端 Director / Skill / 深度卡 / 记忆 / gossip schema。
- 推翻策略：**并行新建 `world_main.tscn`**，旧 `main.tscn` / `main.gd` 保留原路径并标记为 legacy，对应引用不迁移；通过 `project.godot` 切主场景即可一键回滚。

### 1.3 时间预算

2 周冲刺看到阶段 1（"活着的世界"）可演示原型。
后续阶段按里程碑式推进，不绑定固定周期。

## 2. 六阶段路线总览

| 阶段 | 名称 | 核心问题 | 玩家体感验收（30 秒标尺） | 状态 |
| --- | --- | --- | --- | --- |
| **0** | 战略对齐 | 主轴选定、客户端推翻范围、阶段验收标准 | —— | done（本文档落地） |
| **1** | 活着的世界 | 抛弃回合制 + 推翻 UI 主导客户端，NPC 真的在地图上做事 | 玩家不操作，30 秒内能看到至少 3 个 NPC 在地图上走动、做事 | pending |
| **2** | 玩家成为变量 | 玩家行为在 NPC 之间传播，社会因果可见 | 玩家送花给 A，第二天 B 在酒馆说起这件事 | pending |
| **3** | 涌现式叙事 | Director 同时调度多条压力线，事件互相影响 | 第二天的小镇和第一天不一样，因为昨天那场风波 | pending |
| **4** | 玩家工具感 | 农场/经济/恋爱有真实反馈循环 | 玩家能复述出"我在玩什么" | pending |
| **5** | Agent 系统作为玩点 | 把 LLM 驱动可解释性变成传播资产 | 玩家自发想截屏分享 | pending |
| **6** | 生产化打磨 | 性能、成本、存档、打包 | 稳定可发的 Demo 版本 | pending |

## 3. 阶段 1 详细技术设计（2 周冲刺执行依据）

### 3.1 架构变化

当前范式：
```text
玩家点按钮 ──► POST /api/player/action ──► Runtime ──► 返回 state
                                                          │
                                                          ▼
                                                main.gd 把字段塞 UI
```

阶段 1 目标范式：
```text
                          ┌─ 后端 tick：推进 NPC、生成事件
WorldClock(前端) ──tick──►│
   ▲                      └─► EventStore + tick events ──► EventBus(前端)
   │                                                           │
   └─ 玩家暂停/加速                                            ▼
                                                   NPC Controller × N (前端)
                                                   │ 状态机：Idle / Walking / Performing
                                                   │ 阶段 1 寻路：anchor graph + 直线插值
                                                   │ 动画：sprite tween + 头顶工具图标
                                                   ▼
                                                玩家看到 NPC "在生活"
```

核心切换：**"请求/响应"范式 → "事件驱动 + 客户端时间预测"范式**。
客户端职责升级为玩家可感知的表现世界；后端继续持有时间、位置、关系、记忆、事件和结算的权威事实。

### 3.2 关键技术决策（2026-05-17 锁定）

| 决策 | 选定 | 理由 |
| --- | --- | --- |
| 时间驱动模型 | **客户端驱动 tick；tick response events 为阶段 1 主通道，SSE 为可选增强** | 玩家暂停即冻结，调试容易；Godot 先通过 `/api/world/tick` 响应消费事件，避免阶段 1 被长连接稳定性牵制 |
| 客户端策略 | **并行新建 `world_main.tscn`，旧 `main.tscn` / `main.gd` 原路径保留** | 安全可随时回滚；旧场景留 legacy 备查，避免移动脚本导致引用断裂 |
| NPC 表现精度 | **sprite 插值 + 头顶动作图标 + idle bobbing** | "在生活"的最低视觉门槛，2 周可达 |
| NPC 决策来源 | **完全规则驱动，不上 LLM** | LLM 调用频率/成本不允许在阶段 1 上 NPC 自主；LLM 仅在玩家对话/事件选择时触发 |
| 寻路实现 | **anchor graph + 直线插值首选，Godot Navigation2D 后置增强** | 2 周目标优先证明 NPC 迁徙体感，减少 nav polygon 配置风险 |
| 地图布局 | **三场景横向拼图大画布 + 相机自由跟随玩家** | 取代"按钮切场景"，是体感最关键改造 |

### 3.3 后端改造（最小集）

#### 3.3.1 新建 `backend/app/simulation/life_action_executor.py`

- 输入：world、`lifeActionPlan.selectedActions`、`deltaSeconds`
- 职责：
  - 对每个 NPC，根据当前 `activeLifeAction` 推进状态
  - NPC 不在目标 anchor → 生成 `npc.move_started` / `npc.move_progress` / `npc.arrived` 事件
  - 到达 anchor → 生成 `npc.action_started`，按 action 类型分配持续时间（首版用规则表，例如 `tend_farm=300s`、`chat_with=120s`、`tend_shop=600s`）
  - 持续期间生成低频 `npc.action_tick`
  - 到达持续时间 → 生成 `npc.action_completed`，按现有 Runtime 路径写入关系/记忆/物品
- 关键约束：**所有动作进度只用游戏时间，不用墙钟**。客户端不调 tick = 世界冻结。

#### 3.3.2 改造 `runtime.step()`

- 现有 `step(actor_id=...)` 保留，继续给 Debug Console 单步调试用。
- 新增 `runtime.tick(delta_seconds: float) -> dict`：
  - 调用顺序：`life_action_executor.tick() → director.tick(轻量) → event_store.append(events)`
  - 返回紧凑 state diff + 事件列表

#### 3.3.3 新增 `POST /api/world/tick`

请求：
```json
{ "deltaSeconds": 5.0, "speed": 1.0 }
```

响应：
```json
{
  "clock": { "day": 1, "hour": 8, "minute": 25, "phase": "morning" },
  "events": [
    { "type": "npc.move_started", "npcId": "tomas", "from": {...}, "to": {...} },
    { "type": "npc.action_started", "npcId": "kai", "actionId": "...", "duration": 300 }
  ],
  "agents": [ /* 简化 NPC 位置/状态变化 */ ]
}
```

### 3.4 前端改造（推翻 UI，保留底层）

#### 3.4.1 保留

- `scripts/api_client.gd`（升级支持 `tick()`；SSE 订阅使用独立节点或后续增强，不复用会取消请求的同一个 `HTTPRequest`）
- `scripts/asset_registry.gd`（不动）
- `scripts/world_sync.gd`（变薄，只缓存 clock、静态信息和后端 diff；动态表现位置由 NPC Controller 管）
- 所有资产、`.import` 元数据
- Web Debug 观察台

#### 3.4.2 推翻（逻辑冻结为 legacy，不在阶段 1 继续扩写）

- `main.gd` 的 UI 主导布局
- `main.tscn` 的页签结构（旧 scene 和脚本保留原路径，可一键回滚）
- "按钮切场景"概念

#### 3.4.3 新建

- `scripts/core/world_clock.gd`（autoload）—— 持有游戏时间，定时调用 `/api/world/tick`
- `scripts/core/event_bus.gd`（autoload）—— 先把 tick response events 分发为 Godot signal；SSE 后续作为独立长连接增强
- `scripts/world/npc_controller.gd`（每 NPC 一个实例）—— 状态机 + anchor graph / 直线插值 + 动画
- `scripts/world/player_controller.gd`—— WASD 移动 + E 键交互
- `scripts/world/town_map.gd`—— 主场景，三场景背景按地理布局横向拼图
- `scripts/ui/hud.gd`—— 简洁顶部 HUD（时钟、速率控制 1x/2x/暂停、当前位置）
- `scripts/ui/vn_panel.gd`—— VN 对话模块（弹出式）

### 3.5 "小镇全景图"的关键性

当前"按钮切场景"是体感"看板化"的最大根源——玩家永远看不到 NPC 之间的迁徙。
阶段 1 必须改为：**三张地点背景在一张大画布上拼接 + 相机自由跟随玩家**。

资产侧不需要重画，只是布局重排：

```text
[农场]--[广场]--[酒馆]   ← 三张背景横向拼接成一张大地图
   ↑      ↑      ↑
   NPC 可在三地之间真实迁徙，玩家在广场能远远看到铁匠从酒馆走出来
```

这是 2 周内能做到的"最小但震撼"的视觉切换。

### 3.6 2 周冲刺拆分（按天）

| 天 | 后端 | 前端 | 验收 |
| --- | --- | --- | --- |
| D1 | 设计 + 写 `LifeActionExecutor` 雏形（规则驱动，3 种动作类型） | 新建 `core/world_clock.gd` + `event_bus.gd` autoload | unit test：NPC A 从 anchor X 走到 Y，事件序列正确 |
| D2 | `/api/world/tick` 上线，整合到 step 旁路 | `api_client.gd` 增加 `tick()`，`event_bus.gd` 消费 tick response events | 客户端能调 tick，并把响应事件分发到前端 |
| D3 | NPC 行动持续时间表 + `npc.action_*` 事件全套 | 新建 `town_map.gd` 三场景横向拼图 | 浏览器能 hit `/api/world/tick`，state 推进正常 |
| D4 | 玩家行动复用现有路径，但事件改走 EventStore | 新建 `npc_controller.gd` 状态机（Idle/Walking/Performing） | NPC 在场景里能根据后端事件移动 |
| D5 | Director 整合（保留现有，不变形） | anchor graph 路线与直线插值打磨；记录 Navigation2D 后置清单 | 6 个 NPC 在大地图上各自走动 |
| D6 | 测试 + 1Hz 长跑稳定性 | 玩家相机自由跟随 + 速率控制 HUD | 静置 5 分钟无错误、无内存涨 |
| D7 | **里程碑 1：自主世界**——玩家不操作 NPC 自己活 | 同左 | 录屏：30 秒内能看到至少 3 个 NPC 在做事 |
| D8 | 玩家 talk 走新事件流 | VN 弹出模块（按 E 触发，脱离页签结构） | E 键弹 VN，对话能跑通 |
| D9 | NPC `action_completed` 写关系/记忆（复用现有 Runtime） | NPC sprite tween + 简单 idle 动画 | 玩家送礼后，事件出现在事件流，NPC 反应可见 |
| D10 | 星灯祭事件接入新事件流（"远处发生"） | 事件触发时地图上有视觉提示（图标飘过） | 玩家在农场能看到广场有事件正在发生 |
| D11 | 性能测试 + LLM 调用日志检查 | 旧 `main.tscn` / `main.gd` 保持原路径并标记 legacy，重检入口完整 | 帧率 ≥ 30，LLM 调用频率符合预期 |
| D12 | 文档：本文档阶段 1 收口 | 入口/HUD/相机收尾打磨 | `npm.cmd run check` 全绿 |
| D13 | 人工验收准备：录屏脚本、Demo 说明 | 视觉抛光（动作图标、对话气泡） | 主人窗口验收 |
| D14 | 缓冲日 + 文档归档 | 缓冲日 | 阶段 1 收口 |

### 3.7 阶段 1 玩家体感验收

录一段不超过 60 秒的视频，必须能展示：

1. 玩家进入游戏后 30 秒内**不做任何操作**，能看到至少 3 个 NPC 在地图上走动、做事；
2. 玩家能控制角色在大地图上自由移动，看到 NPC 从一个地点走到另一个地点；
3. 玩家靠近 NPC 按 E 键能弹出 VN 对话，对话流程跑通；
4. 暂停按钮按下后，所有 NPC 立即静止，再次按下恢复；
5. 顶部 HUD 显示游戏时间正在流逝。

任何一项不达成，阶段 1 视为未完成。

### 3.8 必须接受的硬妥协

- **NPC 决策完全规则驱动**，不上 LLM。LLM 调用频率和 latency 在阶段 1 不允许；LLM 上 NPC 自主行动放阶段 2。
- **没有寻路冲突解决**，NPC 互相穿模可接受（占位优先）。
- **没有作息真实表**，先用 `lifeActionSeeds` 的 phase 粗映射。
- **没有恋爱线/经济线**——阶段 4 的内容。
- **VN 面板视觉不重新设计**，先复用现有 layout（搬到弹出模块）。

### 3.9 风险与应对

| 风险 | 概率 | 应对 |
| --- | --- | --- |
| SSE 长连接和 tick 请求并发时出现连接管理复杂度 | 中 | 阶段 1 先用 tick response events；SSE 作为独立节点后置验证，后端当前已使用 `ThreadingHTTPServer` |
| Godot 4 Navigation2D 配置成本高 | 中 | 阶段 1 使用 anchor graph + 直线插值；Navigation2D 进入后置增强清单 |
| `main.gd` 2358 行继续扩写导致新旧逻辑耦合 | 高 | 旧 scene 和脚本原路径冻结；新建独立 `world_main.tscn`；通过 `project.godot` 切主场景 |
| LLM 玩家对话调用过慢导致 NPC 卡住 | 中 | NPC 行动不阻塞玩家请求；玩家请求独立线程处理 |
| Runtime 现有 `step()` 是 Agent 轮换调度，改为时间驱动可能破坏 Director | 中 | 不改 step；新建 `runtime.tick(delta_seconds)`；step 继续给 Debug Console 用 |
| 三场景横向拼图大地图导致首屏负担/视觉割裂 | 中 | 三背景间用过渡色块/草地拼接；优先保证 NPC 迁徙可见 |

## 4. 阶段 2-6 概述（待激活时细化）

### 阶段 2 · 玩家成为变量

- 核心：把 `gossip.propagation_validated` 从"校验事件"升级为"真的写入 NPC 记忆 + 关系扩散"
- NPC 行动选择把"目击玩家行为"作为输入
- 引入"在场感"：哪些 NPC 在哪个地点、能看到什么
- 验收：玩家送花给 A，B 看到了，30 游戏分钟后 C 在酒馆议论

### 阶段 3 · 涌现式叙事

- 写第 2、3、4 个 Event Skill（情人冲突、店铺危机、流浪商人到访）
- Director Beat 队列引入优先级、衰减、冲突解决
- "今日新闻"UI 元素让玩家感知导演在工作
- 验收：第二天小镇和第一天不一样

### 阶段 4 · 玩家工具感

- 农场地块状态 + 时间生长 + 收成
- 简单市场：玩家供给影响 NPC 行为
- 恋爱线作为"长期关系阶段"的具象化，不另起系统
- 验收：玩家能复述"我在玩什么"

### 阶段 5 · Agent 系统作为玩点

- 日记本/小镇志 UI，叙事化呈现 NPC 记忆
- "可分享时刻"导出（30 秒 GIF + 字幕）
- Debug 控制台保持研究院视角
- 验收：玩家自发想截屏分享

### 阶段 6 · 生产化打磨

- LLM 成本分层：强模型用于 Director，便宜模型用于背景 NPC，规则用于 fallback
- 存档、断线恢复、windowed Demo 模式
- 作品集页面
- 验收：稳定可发的 Demo 版本

## 5. 与现有文档的关系

| 文档 | 关系处理 |
| --- | --- |
| `docs/project_vision.md` | 不变，本文档完全在愿景边界内执行 |
| `docs/agentic_game_design.md` | 不变，作为 Director / Skill / NPC Agent 的设计源 |
| `docs/gameplay_system_architecture.md` | 不变，本文档实现其中"涌现式田园生活模拟"目标 |
| `docs/vertical_slice_spec.md` | 保留为切片规格参考；切片定义不变（6 NPC / 3 地点 / 1 完整日 / 1 事件） |
| `docs/implementation_plan.md` | 标记为 snapshot（已是 snapshot 状态），本文档取代其执行依据角色 |
| `docs/current_status.md` | 不变，继续记录当前已验证事实；阶段 1 推进后该文档更新事实 |
| `docs/goal_board.md` | 保留为开发线看板；阶段 1 推进期间新增 "Phase 1 sprint" 开发线 |
| `docs/agent_context.md` | 阶段 1 启动时更新"下一轮最短开发入口"指向本文档 |

## 6. 验收命令

每次推进 + 文档收口时运行：

```powershell
npm.cmd run context:check
npm.cmd run check
npm.cmd run smoke
npm.cmd run asset:check
npm.cmd run client:env
npm.cmd run client:run:check
git diff --check
```

阶段 1 内新增建议命令（具体实现后落地）：

```powershell
# 验证 tick API 路径稳定
curl.exe -X POST http://localhost:8787/api/world/tick -H "Content-Type: application/json" -d "{\"deltaSeconds\":5}"
# 验证 SSE 事件流
curl.exe -N http://localhost:8787/api/events
```

## 7. 立即接续步骤

1. **本文档落地后**：运行 `npm.cmd run context:check` 验证 frontmatter 兼容性；运行 `git diff --check` 检查空白。
2. **D1 启动条件**：`docs/agent_context.md` 第 6 节已指向本文档；`docs/goal_board.md` 已新增 "Phase 1 sprint" 开发线。
3. **D1 第一个具体动作**：新建 `backend/app/simulation/life_action_executor.py` 雏形 + 对应单元测试；并行新建 `clients/godot/scripts/core/world_clock.gd`、`event_bus.gd` 与 `world_main.tscn` 骨架。
4. **任何阶段 1 推进前**：先确认本文档"3.2 关键技术决策"未发生变化，避免开发线漂移。

## 8. 维护规则

- 本文档是阶段 1 内的"路线源"，**不复制源设计长文**。
- 阶段 1 推进过程中如有决策调整，先更新 "3.2 关键技术决策" 表格，再开始实施。
- 任何已完成项必须有命令验证证据；任何未验证项必须显式标注 `manual unverified`。
- 阶段 2-6 在被激活前不细化，避免规划幻觉。
