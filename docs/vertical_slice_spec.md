# 第一版可玩垂直切片规格

> 本文定义 `Agent Valley` 第一版可玩切片的内容、数据契约和验收边界。该切片按正式游戏的第一章骨架推进，后续章节、系统和资产应能在同一结构上扩展。

## 切片目标

完成一个可运行、可录屏、可讲解的第一天体验：

- 玩家以新搬来的偏少女农场主身份进入小镇。
- 玩家能在农场、广场和酒馆之间移动。
- 玩家能与 NPC 聊天、送礼、参与小镇事件。
- 玩家从可移动地图层进入 Visual Novel 对话层，再回到地图继续行动。
- NPC 会基于人设、日程、关系、记忆和当天事件作出差异化回应。
- 部分 NPC 会通过对话、送礼和记忆表现恋爱铺垫级别的好感变化。
- 星灯祭供应短缺事件会影响多个 NPC 的主观记忆和后续态度。
- Debug Console 能完整解释玩家动作、NPC 决策、模型调用、记忆写入和关系变化。

## 体验范围

### 时间范围

- 游戏内第 1 天。
- 起始时间：08:00。
- 结束时间：夜晚反思完成后。
- 时间段建议：
  - 早晨：搬入农场。
  - 上午：广场认识居民。
  - 下午：准备礼物或作物。
  - 傍晚：酒馆事件。
  - 夜晚：NPC 日记和记忆沉淀。

### 地点范围

| 地点 ID | 名称 | 首版用途 | 后续扩展方向 |
| --- | --- | --- | --- |
| `farm` | 玩家农场 | 玩家出生点、初始作物、送礼来源 | 农场经营、作物系统、房屋升级 |
| `plaza` | 中央广场 | 认识居民、公告、公共事件入口 | 节日、市场、镇民集会 |
| `tavern` | 月猫酒馆 | 社交、冲突、星灯祭事件 | 夜间活动、演出、委托任务 |

旧观察台中的住宅区、商店和诊所暂时转为背景关系或后续扩展地点。首版数据结构应允许这些地点恢复为可探索区域。

### 玩家动作范围

| 动作 | 首版用途 | 后续扩展方向 |
| --- | --- | --- |
| `move` | 移动到地点或交互区域 | 地图格子、寻路、室内外切换 |
| `talk` | 与 NPC 对话 | 话题系统、任务分支、多人对话 |
| `give_gift` | 送出作物或小礼物 | 物品喜好、稀有礼物、节日礼物 |
| `attend_event` | 参与星灯祭事件 | 节日、危机、支线事件 |
| `inspect` | 查看地点或事件提示 | 收集、调查、环境叙事 |

首版可以先实现 `move`、`talk` 和 `give_gift`，但 API 和事件记录需要为其他动作预留类型字段。

## 首发 NPC 规格

### 首发名单

| NPC ID | 游戏内显示名 | 职业 | 首版功能 | 核心张力 | 恋爱铺垫 |
| --- | --- | --- | --- | --- | --- |
| `mira` | 米娅·星麦 | 杂货铺店主 | 经济与生活物资视角 | 店铺压力与家庭照顾 | 温柔照顾线 |
| `tomas` | 托玛·榆庭 | 木匠 | 家庭与修缮视角 | 沉默保护欲与表达不足 | 沉默守护线 |
| `orren` | 奥伦·星历 | 退休教师 | 历史与传统视角 | 健康风险与固执观念 | 不作为候选 |
| `lena` | 莉娜·白桦 | 医生 | 健康与理性判断 | 过度疲惫与公共责任 | 理性克制线 |
| `kai` | 凯伊·月弦 | 酒馆乐手 | 社交和节日氛围 | 浪漫冲动与欠账冲突 | 热情直球线 |
| `bram` | 布拉姆·麦垄 | 农夫 | 农场主题和供应线 | 直率记仇与酒馆欠账 | 不作为候选 |

### 扩展池

| NPC ID | 名称 | 首版状态 | 后续用途 |
| --- | --- | --- | --- |
| `nina` | 妮娜 | 作为家庭背景存在 | 家庭成长系统 |
| `sana` | 萨娜 | 作为镇长背景存在 | 治理事件、公告、镇民任务 |
| `rio` | 里奥 | 作为扩展 NPC 暂缓 | 青少年支线、学校线 |
| `ivy` | 艾薇 | 作为 Debug 叙事候选暂缓 | 研究员视角、元叙事、观察任务 |

### NPC 数据最低字段

```text
id
name
displayName
shortName
age
job
locationId
homeId
personality[]
longTermGoals[]
todaySchedule[]
likes[]
dislikes[]
relationships{}
romanceTags[]
status{}
memories[]
visualArchetype
speechStyle
mapSpriteRef
portraitRefs{}
expressionRefs{}
assetRefs{}
```

首版可以只填必要字段，但字段命名应靠近未来数据文件结构。

## 第一天主线流程

### 1. 早晨：搬入农场

目标：

- 展示玩家身份。
- 给玩家一个初始目标。
- 让玩家获得可送出的初始物品。

建议内容：

- 玩家醒来或到达农场。
- 系统提示：今天去广场认识居民。
- 背包获得 `fresh_turnip` 或 `farm_flower`。

### 2. 上午：广场认识居民

目标：

- 展示 NPC 基础人设。
- 验证 `talk` 动作。
- 写入“第一次见面”记忆。

建议内容：

- 米娅·星麦、奥伦·星历、莉娜·白桦可出现在广场或附近。
- 玩家至少和 2 个 NPC 对话。
- NPC 对玩家身份做出不同反应。

### 3. 下午：准备礼物或作物

目标：

- 验证玩家背包和 `give_gift` 动作。
- 建立关系变化和礼物偏好。

建议内容：

- 玩家回农场取作物或选择已有礼物。
- 玩家可以把作物给布拉姆·麦垄、米娅·星麦或凯伊·月弦。
- 礼物结果写入双方记忆和事件流。

### 4. 傍晚：星灯祭供应短缺

目标：

- 触发首个多人事件。
- 验证事件参与和 NPC 主观反应。

事件梗概：

- 月猫酒馆准备举行星灯祭前夜小聚。
- 凯伊·月弦希望活动热闹进行，但节日食材不足。
- 布拉姆·麦垄认为酒馆欠账未清，拒绝继续供应农产品。
- 玩家可以交出作物、调解冲突、支持其中一方或旁观。
- 米娅·星麦、莉娜·白桦、奥伦·星历和托玛·榆庭从各自角度评价事件。

### 5. 夜晚：主观记忆与日记

目标：

- 验证夜间反思。
- 让白天选择影响 NPC 的长期印象。

最低要求：

- 至少 3 个 NPC 生成不同主观记忆。
- 至少 1 个 NPC 的第二次对话能体现白天事件。
- Debug Console 能看到夜间反思输入和输出摘要。

## 核心数据契约草案

### `GET /api/world/state`

用途：Godot 拉取权威世界状态。

返回字段建议：

```json
{
  "clock": {
    "day": 1,
    "hour": 8,
    "phase": "morning",
    "paused": false
  },
  "player": {
    "id": "player",
    "name": "新来的少女农场主",
    "locationId": "farm",
    "inventory": [],
    "knownNpcs": [],
    "questFlags": {},
    "actionHistory": []
  },
  "locations": [],
  "npcs": [],
  "activeEvents": [],
  "recentEvents": []
}
```

### `POST /api/player/action`

用途：Godot 提交玩家动作。

请求字段建议：

```json
{
  "type": "talk",
  "actorId": "player",
  "targetId": "mira",
  "locationId": "plaza",
  "topic": "first_meeting",
  "itemId": null,
  "message": "你好，我刚搬到农场。"
}
```

响应字段建议：

```json
{
  "ok": true,
  "result": {
    "dialogue": [],
    "relationshipDeltas": [],
    "memoryWrites": [],
    "eventIds": []
  },
  "state": {}
}
```

### 事件记录

玩家动作和 NPC 反应至少需要写入以下事件类型：

```text
player.moved
player.talked
player.gift_given
player.event_choice
npc.dialogue
npc.memory_created
relationship.changed
town.event_started
town.event_resolved
debug.turn_recorded
```

### Debug 决策记录

关键 LLM 调用至少记录：

```text
turnId
actorId
feature
profileName
messages
rawText
parsed
executed
memoryWrites
relationshipDeltas
usage
latencyMs
fallbackReason
```

## LLM 使用边界

首版优先在高价值节点使用 LLM：

- 玩家主动聊天。
- 星灯祭事件中的 NPC 反应。
- 夜间日记和反思。
- 重要关系变化后的后续对话。

以下内容可先用规则或缓存：

- 高频移动。
- 普通时间推进。
- 无剧情含义的状态刷新。
- 地点提示和固定 UI 文案。

所有 LLM 输出需要支持结构化 JSON 解析，并保留自然语言兜底。

## 资产规格

### 首批资产清单

```text
assets/source/style/style_key_art_agent_valley.png
assets/source/style/style_character_lineup_day1.png
assets/source/locations/farm_day_anime.png
assets/source/locations/plaza_day_anime.png
assets/source/locations/tavern_evening_anime.png
assets/source/characters/player_farmer_neutral.png
assets/source/characters/player_farmer_happy.png
assets/source/characters/player_farmer_troubled.png
assets/source/characters/npc_mira_neutral.png
assets/source/characters/npc_mira_happy.png
assets/source/characters/npc_mira_troubled.png
assets/source/characters/npc_tomas_neutral.png
assets/source/characters/npc_tomas_happy.png
assets/source/characters/npc_tomas_troubled.png
assets/source/characters/npc_orren_neutral.png
assets/source/characters/npc_orren_happy.png
assets/source/characters/npc_orren_troubled.png
assets/source/characters/npc_lena_neutral.png
assets/source/characters/npc_lena_happy.png
assets/source/characters/npc_lena_troubled.png
assets/source/characters/npc_kai_neutral.png
assets/source/characters/npc_kai_happy.png
assets/source/characters/npc_kai_troubled.png
assets/source/characters/npc_bram_neutral.png
assets/source/characters/npc_bram_happy.png
assets/source/characters/npc_bram_troubled.png
assets/source/sprites/player_farmer_map_idle.png
assets/source/sprites/npc_mira_map_idle.png
assets/source/sprites/npc_tomas_map_idle.png
assets/source/sprites/npc_orren_map_idle.png
assets/source/sprites/npc_lena_map_idle.png
assets/source/sprites/npc_kai_map_idle.png
assets/source/sprites/npc_bram_map_idle.png
assets/source/sprites/interaction_marker_talk.png
assets/source/sprites/interaction_marker_gift.png
assets/source/sprites/interaction_marker_event.png
assets/source/cg/starlight_festival_shortage_event.png
assets/source/icons/item_fresh_turnip.png
assets/source/icons/item_farm_flower.png
assets/source/icons/item_starlight_lantern.png
assets/source/ui/anime_dialogue_panel_style.png
assets/source/ui/dialogue_box_anime.png
assets/source/ui/nameplate_anime.png
assets/source/ui/choice_button_anime.png
assets/source/ui/memory_card_anime.png
```

### 资产清单字段

```text
id
path
type
ownerId
usage
variantGroup
expression
style
promptSummary
fullPromptRef
sourceTool
createdAt
sourceSize
processedPath
godotPath
licenseNote
status
reviewNotes
```

## 目录约束

正式开发后推荐演进为：

```text
ai-agent-town-lab/
├── backend/
├── clients/
│   └── godot/
├── web-admin/
├── frontend/
├── assets/
│   ├── source/
│   ├── processed/
│   └── manifests/
├── docs/
├── experiments/
└── scripts/
```

`frontend/` 在迁移期保留。`web-admin/` 建立后，新的 Debug Console 功能优先进入 `web-admin/`。

## 验收标准

### 体验验收

- 玩家可以进入游戏场景并移动。
- 玩家可以看到 3 个地点和 6 个 NPC 的基础表现。
- 玩家和 NPC 在地图层都有小人或占位小人表现。
- 对话界面可以展示二次元半身立绘和至少 1 种表情。
- 玩家可以与至少 3 个 NPC 对话。
- 玩家可以送出至少 1 个物品。
- 至少 2 个恋爱候选 NPC 的后续对话能体现轻微好感变化。
- 星灯祭供应短缺事件可以触发和完成。
- 夜晚能看到 NPC 记忆或日记结果。

### 技术验收

- Godot 通过 `GET /api/world/state` 获取状态。
- 玩家动作通过 `POST /api/player/action` 进入后端。
- 后端写入玩家动作、NPC 反应、关系变化和记忆事件。
- Debug Console 能解释至少 1 条完整玩家互动链路。
- LLM 失败时可以 fallback，游戏流程继续推进。

### 扩展性验收

- 新增一个 NPC 不需要改动 Godot 主流程。
- 新增一个地点不需要改动 Agent Runtime 核心循环。
- 新增一个玩家动作有明确 API 类型、事件类型和 Debug 记录位置。
- 新增一张资产可以进入资产清单并被 Godot 引用。
- 首版事件结构能复用到后续节日、冲突、委托和危机事件。

## 开发启动顺序

1. 修复本地检查命令。
2. 增加 `PlayerState`。
3. 增加 `GET /api/world/state`。
4. 增加 `POST /api/player/action` 的 `talk` 最小链路。
5. 创建 Godot 空项目并读取后端状态。
6. 裁剪首版 6 NPC 和 3 地点数据。
7. 接入星灯祭供应短缺事件。
8. 接入夜间反思。
9. 导入第一批视觉资产。
10. 打磨 Debug Console 的互动链路视图。
