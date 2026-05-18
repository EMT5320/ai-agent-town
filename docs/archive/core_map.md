---
status: active
owner_lane: planning
last_verified: 2026-05-18
startup_load: on-demand
source_of_truth: false
scope: user-authored comprehensive development direction after Phase 1 closeout
---

# Agent Valley 全面开发计划（Phase 1 收口后）（待进一步讨论）
制定时间：2026-05-18 核心判断：游戏内容（种田、物品、场景、交互）是 NPC Agent 的"工具集"和"行动空间"。没有丰富的行动空间，Agent 涌现无从谈起。当前最大缺口不是系统架构，而是 NPC 和玩家能做的事太少、世界状态实体太少、视觉表现太简陋。

1. 方向重申
Agent Valley 的核心是：每个 NPC 是一个独立 Agent，因动机驱动，调用工具完成目标，不断循环并自我进化。玩家作为参与者或旁观者融入这个世界。

要实现这个愿景，必须同时满足：

NPC 有足够多的"工具"可调用（种田、开店、做饭、社交、修缮……）
工具执行后世界状态真的变化（田里长出作物、店铺有货、房子修好了）
变化对玩家可见（美术资产 + 客户端表现）
三层缺一不可。当前项目在第一层（工具定义）只有"移动"和"说话"，第二层（世界实体）几乎为零，第三层（视觉表现）极度简陋。这是后续开发的主攻方向。

2. 世界实体设计（后端权威状态）
2.1 农田系统
FarmPlot:
  id: string
  ownerId: string (npc_id 或 "player")
  position: {x, y, zoneId}
  state: empty | tilled | planted | growing | harvestable | withered
  cropType: string | null
  growthProgress: float (0-1)
  waterLevel: float (0-1, 每日衰减)
  quality: normal | silver | gold
  plantedAt: gameTime
  lastWateredAt: gameTime
初版规模：

玩家农场：9 块地（3×3 网格）
布兰娜农场：6 块地
公共菜园（广场旁）：4 块地
初版作物（5 种）：

星麦（基础谷物，3 天成熟）
月莓（水果，4 天成熟，可送礼）
晨露草（药材，2 天成熟，莉娜需要）
金铃薯（蔬菜，3 天成熟，料理材料）
夜光花（观赏，5 天成熟，高价值礼物）
2.2 物品/背包系统
Item:
  id: string
  name: string
  category: seed | crop | tool | food | gift | material | misc
  tags: string[] (用于送礼匹配、NPC 偏好、料理配方)
  stackable: bool
  maxStack: int
  sellPrice: int
  description: string

Inventory:
  ownerId: string (npc_id 或 "player")
  slots: [{itemId, quantity}]
  capacity: int
初版物品（约 25 种）：

种子 ×5（对应 5 种作物）
收获作物 ×5
工具 ×4（锄头、水壶、镰刀、斧头）
料理 ×3（面包、果酱、药膏）
礼物 ×3（花束、手工品、书）
材料 ×3（木材、石头、铁矿）
杂货 ×2（灯油、绳子）
2.3 店铺/经济系统
Shop:
  id: string
  ownerId: string (npc_id)
  zoneId: string
  inventory: [{itemId, quantity, price}]
  gold: int
  restockSchedule: string (daily | weekly)
  demandTags: string[] (当前需求标签，影响收购价)

Economy:
  playerGold: int
  marketPrices: {itemId: {buy, sell}} (浮动)
初版店铺：

米娅杂货铺：卖种子、基础工具、日用品；收购作物
酒馆（凯娅）：卖食物饮料；收购食材
2.4 建筑/设施系统
Building:
  id: string
  type: house | shop | farm | public
  ownerId: string | null
  zoneId: string
  condition: float (0-1, 影响功能和外观)
  features: string[] (kitchen, bed, storage, workbench...)
  upgradeLevel: int

Interactable:
  id: string
  type: crop_plot | workbench | bed | stove | well | mailbox | notice_board...
  buildingId: string | null
  state: object (类型相关的状态)
  usableBy: string[] (谁能用)
初版建筑/设施：

玩家小屋（床、储物箱、简易厨房）
布兰娜农舍（农具间、大厨房）
米娅杂货铺（柜台、货架）
酒馆（吧台、舞台、桌椅）
广场公共设施（公告板、水井、长椅）
托玛工坊（工作台、木材堆）
2.5 时间/环境系统
WorldTime:
  day: int
  hour: int (0-23)
  minute: int
  phase: dawn | morning | afternoon | evening | night
  season: spring | summer | autumn | winter (首版只做 spring)
  weather: clear | cloudy | rain (影响浇水需求和 NPC 行为)

DayNightCycle:
  lightLevel: float (0-1)
  ambientColor: Color
  npcAwakeHours: {npcId: {wake, sleep}}
3. NPC 工具集（Agent 可调用的 Actions）
第一批：日常循环核心
工具	输入	世界效果	视觉表现
till_soil	plotId	地块 empty→tilled	翻土动画/状态图
plant_seed	plotId, seedItemId	地块 tilled→planted, 消耗种子	种子入土图
water_crop	plotId	waterLevel 恢复	浇水动画/水滴
harvest_crop	plotId	地块→empty, 获得作物	收获动画/物品飘出
open_shop	shopId	店铺状态→open	店铺亮灯/招牌
sell_item	itemId, quantity, buyerId	物品转移, 金币变化	交易气泡
buy_item	itemId, quantity, shopId	物品转移, 金币变化	交易气泡
cook_food	recipeId, ingredients[]	消耗材料, 获得食物	烹饪动画/烟雾
eat_food	itemId	消耗食物, 恢复体力/心情	进食动画
rest	bedId 或 locationId	恢复体力, 推进时间	休息姿态
sleep	bedId	结束当天, 触发夜间反思	熄灯/zzz
chat_with	targetNpcId, topic?	关系变化, 记忆写入, gossip 传播	对话气泡
give_gift	targetId, itemId	物品转移, 关系变化, 记忆	赠送动画
move_to	anchorId	位置变化	行走动画
第二批：丰富互动
工具	输入	世界效果	视觉表现
repair_building	buildingId, materialItems[]	condition 提升, 消耗材料	修缮动画/锤子
craft_item	recipeId, materials[]	消耗材料, 获得成品	制作动画
play_music	instrumentId, locationId	周围 NPC 心情提升	音符粒子
read_book	bookId	获得知识/技能点	翻书动画
post_notice	noticeBoard, content	公告板更新, 全镇可见	贴纸动画
attend_event	eventId	参与事件, 触发选择	事件场景
ask_for_help	targetId, taskDesc	生成合作任务	求助气泡
lend_item	targetId, itemId	物品暂时转移, 记录债务	借出动画
第三批：深度涌现
工具	输入	世界效果
borrow_gold	targetId, amount	债务关系建立
refuse_request	requestId, reason	关系紧张, 记忆
spread_rumor	targetId, content	gossip 网络扩散
hide_secret	secretId	秘密不进入 gossip
confess	targetId, secretId	关系大幅变化
compete_with	targetId, domain	竞争关系, 影响定价/声望
cooperate_with	targetId, taskId	合作关系, 共享收益
4. 美术资产方案（C 方案 + AI 生成优化）
4.1 总体策略
精美背景图 + 可交互物件层 + 简单动画

场景基底：AI 生成的高质量背景图（保持当前二次元轻幻想风格）
物件层：AI 生成的独立物件 PNG，叠加在背景上，有状态变化（多帧）
角色：AI 生成的 spritesheet 或多姿态立绘，客户端做简单帧切换
UI：AI 生成的 UI 组件图，Godot 内组装
4.2 适合 AI 生图的资产类型
资产类型	AI 生成策略	数量估算
场景背景（分层）	每个区域生成 3 层：远景/中景/近景，支持视差	3 区域 × 3 层 = 9 张
场景背景变体	日/夜/雨 各一套色调变体	9 × 3 = 27 张（可用后处理减少）
作物生长阶段	每种作物 5 个阶段的独立小图	5 作物 × 5 阶段 = 25 张
物件状态图	店铺开/关、工作台空/忙、床铺整/乱	约 20 组 × 2 状态 = 40 张
角色姿态	每个角色：idle/walk/action/sit/sleep × 正面/侧面	7 角色 × 5 姿态 × 2 方向 = 70 张
物品图标	统一风格的物品小图	25 种
表情差分	每个 NPC 的 happy/troubled/angry/shy	6 NPC × 4 = 24 张
UI 组件	背包框、按钮、面板、图标	约 15 张
行动效果	浇水水滴、收获星光、烹饪烟雾等粒子/帧	约 10 组
总计约 230-250 张独立资产。按 AI 批量生成 + 人工筛选的流程，分 5-6 个批次推进。

4.3 生成批次建议
批次	内容	优先级	预计产出
B1	角色姿态（idle + walk 正面/侧面，7 角色）	最高	28 张
B2	作物生长阶段 + 农田物件	最高	30 张
B3	场景背景分层重制（3 区域 × 3 层）	高	9 张
B4	物品图标全套	高	25 张
B5	表情差分 + 角色 action 姿态	中	36 张
B6	店铺/建筑物件状态 + UI 组件	中	55 张
B7	日夜变体 + 行动效果 + 剩余	后置	50+ 张
4.4 Godot 客户端表现方案
场景结构：
  ParallaxBackground (远景层)
  ParallaxBackground (中景层 - 主背景)
  InteractableLayer (物件层 - 农田、店铺、设施)
    ├─ CropPlot × N (Sprite2D + 状态切换)
    ├─ ShopFront (Sprite2D + 开/关状态)
    ├─ Workbench (Sprite2D + 空/忙状态)
    └─ ...
  CharacterLayer (角色层)
    ├─ PlayerController (AnimatedSprite2D, 多姿态)
    ├─ NpcController × 6 (AnimatedSprite2D, 多姿态)
    └─ ...
  ForegroundLayer (前景遮挡层)
  UILayer (HUD、背包、对话)
角色动画方案：

不做逐帧 spritesheet 动画（AI 生成一致性差）
改用多姿态静态图 + Tween 过渡：idle→walk 切图 + 位移 tween，walk→action 切图 + 简单缩放/旋转
辅以粒子效果（浇水水滴、收获星光）增加动感
5. 玩家模式
5.1 参与者模式（默认）
玩家拥有和 NPC 相同的工具集（种田、买卖、送礼、社交……）
玩家通过地图移动 + 靠近交互触发工具
玩家行为进入 Agent 系统，NPC 会观察、记忆、传播、反应
UI：背包、工具栏、金币、体力条、关系面板
5.2 观察者模式
玩家不参与世界交互，以上帝视角观察 NPC 社会运转
可加速/减速/暂停时间
可点击任何 NPC 查看其当前动机、记忆、关系、正在执行的工具
偶尔可"干预"：投放物品、触发事件、修改 NPC 情绪
UI：时间控制、NPC 信息面板、干预工具栏、事件日志
5.3 模式切换
游戏内可随时切换（比如按 Tab）
观察者模式下玩家角色"消失"或变为半透明幽灵
切回参与者模式时，玩家角色重新出现在上次位置
6. 开发线重新定义
6.1 世界实体线（后端核心）
目标：让世界有"东西"——农田、物品、店铺、建筑都是真实存在的数据实体。

任务：

设计并实现 FarmPlot、Item、Inventory、Shop、Building 数据模型
实现作物生长规则（随 tick 推进）
实现物品流转规则（买卖、消耗、赠送）
实现店铺经济规则（库存、定价、进货）
扩展 /api/world/state 暴露所有实体状态
扩展 /api/world/tick 推进作物生长、店铺进货等
6.2 NPC 工具线（Agent 系统核心）
目标：让 NPC Agent 有丰富的工具可调用。

任务：

定义统一的 Tool 接口（输入 schema、前置条件、世界效果、事件输出）
实现第一批 14 个工具
改造 LifeActionExecutor：从"规则表驱动固定行动"升级为"Agent 根据动机选择工具"
NPC 动机系统：需求（饥饿、疲劳、社交）+ 目标（赚钱、维护关系、完成任务）→ 工具选择
工具执行结果进入记忆和事件流
6.3 美术资产线
目标：让世界变化可见。

任务：

按批次生成资产（B1-B7）
建立 AI 生图的 prompt 模板和一致性控制方法
每批生成后人工筛选 → manifest 登记 → Godot 接入
场景分层重制（从单张背景图升级为多层可交互场景）
6.4 Godot 客户端线
目标：让玩家能看到、能操作。

任务：

场景重构：从单张背景 → 分层场景 + 物件层
角色动画系统：多姿态切换 + Tween
交互系统：靠近物件 → 显示可用工具 → 执行 → 看到结果
背包/工具栏 UI
农田 UI（地块状态可视化、种植/浇水/收获操作）
店铺 UI（买卖界面）
观察者模式 UI
日夜视觉变化（光照 tint + 背景切换）
6.5 游戏内容线
目标：填充世界的"血肉"。

任务：

物品数据（item_codex）：25 种物品的完整定义
配方数据：料理配方、制作配方
NPC 日程模板升级：从 lifeActionSeeds 升级为基于动机的行为模式
第二、第三个 Event Skill
30 天节奏年历草案
NPC 对话内容扩充（围绕新工具和世界状态的反应）
6.6 LLM/Agent 智能线
目标：让 NPC 的工具选择真正由 LLM 驱动。

任务：

NPC 动机 Prompt 设计：当前状态 + 需求 + 目标 + 可用工具 → LLM 选择下一步行动
工具调用频率和成本控制（规则预筛选 + LLM 决策）
Gossip 从校验到写入
夜间反思升级：总结今天做了什么、明天想做什么
Director 多事件调度
7. 并行开发排程
Week 1-2: Phase 1 收口 + 世界实体基础
  ├─ 主人窗口验收 → Phase 1 收口
  ├─ 后端：FarmPlot + Item + Inventory 数据模型
  ├─ 后端：5 种作物 + 25 种物品数据定义
  ├─ 美术：B1 角色姿态生成
  └─ Godot：背包 UI 骨架

Week 3-4: NPC 工具 + 场景重构
  ├─ 后端：第一批工具实现（种田4个 + 买卖2个 + 社交2个 + 生活2个）
  ├─ 后端：作物生长 tick 规则
  ├─ 美术：B2 作物 + 农田物件
  ├─ Godot：场景分层重构 + 农田物件层
  └─ Godot：种田交互流程（翻地→播种→浇水→收获）

Week 5-6: 经济循环 + 角色动画
  ├─ 后端：Shop 模型 + 买卖工具 + 经济规则
  ├─ 后端：NPC 动机系统雏形
  ├─ 美术：B3 场景分层 + B4 物品图标
  ├─ Godot：角色多姿态动画系统
  ├─ Godot：店铺交互 UI
  └─ 内容：item_codex + 配方数据

Week 7-8: Agent 驱动 + 观察者模式
  ├─ 后端：LifeActionExecutor 升级为工具选择器
  ├─ LLM：NPC 动机 Prompt + 工具选择测试
  ├─ 美术：B5 表情 + action 姿态
  ├─ Godot：观察者模式 UI
  ├─ Godot：日夜视觉变化
  └─ 内容：第二个 Event Skill

Week 9-10: 涌现验证 + 打磨
  ├─ 后端：Gossip 写入 + Director 多事件
  ├─ LLM：成本/延迟优化
  ├─ 美术：B6 + B7 剩余资产
  ├─ Godot：全流程打磨
  └─ 录制 Demo：展示 NPC 自主生活 + 玩家参与 + 涌现反应
8. 阶段验收标尺（更新）
阶段	名称	30 秒验收	状态
1	活着的世界	3 个 NPC 在地图上走动做事	收口中
2	可玩的一天	玩家完成种田→收获→卖货→社交→睡觉的完整日循环	pending
3	NPC 自主生活	NPC 自己种田、开店、做饭、社交，不需要玩家干预	pending
4	玩家成为变量	玩家送花给 A，第二天 B 在酒馆说起这件事	pending
5	涌现式叙事	第二天的小镇和第一天不一样	pending
6	生产化打磨	稳定可发的 Demo	pending
9. 与现有文档的关系
production_roadmap.md：需要更新阶段定义，把原 Phase 2-6 重新编排
gameplay_system_architecture.md：需要补充世界实体设计和工具集定义
agentic_game_design.md：NPC 工具系统是其"NPC Agent 可用工具"的具体化
game_content_storyline.md：物品、配方、NPC 日程模板是内容线的扩展
art_direction.md：需要补充分层场景方案和 AI 生图批次策略
npc_deep_card_spec.md：需要扩展 NPC 的"工具偏好"和"动机权重"字段
10. 关键原则
广度优先：初版每个系统都要有，哪怕每个系统只有最小内容量。避免再次出现"系统精巧但无内容"的问题。
工具即内容：每新增一个 NPC 工具，就是新增一种游戏内容。工具数量决定了世界的丰富度。
AI 生产友好：美术方案选择"多姿态静态图 + Tween"而非"逐帧动画"，因为 AI 生成静态图的一致性远好于动画帧。
后端权威不变：所有世界实体状态由后端持有，Godot 只做表现和输入。
NPC 和玩家共享工具接口：同一套 Tool 定义，NPC 通过 Agent 调用，玩家通过 UI 操作调用。