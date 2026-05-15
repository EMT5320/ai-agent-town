# 初版实施计划

本计划面向 `Agent Valley` 第一版可玩垂直切片。目标是在当前仓库原地演进，用 Godot 承担玩家体验，用 Python Agent Server 承担世界状态、LLM NPC、记忆、事件和 Debug 数据。

## 初版目标

完成一个可录屏、可讲解、可继续扩展的“第一天”可玩章节：

- 玩家作为新搬来的偏少女农场主进入小镇。
- 小镇包含 3 个地点：农场、广场、酒馆。
- 首发 6 个 NPC，有幻想显示名、人设、日程、关系、喜好、记忆和对玩家的持续反应。
- 玩家可以移动、聊天、送礼、触发小镇事件。
- 首版同步具备可移动地图层和 Visual Novel 对话层。
- 关键 NPC 可以通过对话和送礼产生恋爱铺垫级别的好感变化。
- NPC 使用 LLM 生成关键对话、事件反应和夜间反思。
- Debug / 研究控制台可以看到 Prompt、模型输出、行动解析、记忆写入和关系变化。

## 开发总约束

首版按正式游戏骨架推进。每个批次除了完成当前体验目标，还要保护后续扩展路径：

- API 设计要能支持更多玩家动作和更多客户端视图。
- 世界状态要能支持更多地点、NPC、事件和任务。
- 内容数据要逐步靠近数据驱动，减少新增内容时修改核心循环。
- Debug 记录要能支持回放、问题定位和作品集讲解。
- 资产目录和 manifest 要能承载后续角色、场景、CG、UI 和图标。
- LLM Provider 调用要按功能 profile 管理，避免模型选择散落在业务逻辑里。

批次验收时需要同时检查“体验是否跑通”和“后续同类内容能否扩展”。

## 首版范围冻结

### 必须进入首版

- Godot Windows 桌面客户端。
- Python 后端继续作为权威世界状态。
- `GET /api/world/state`：给 Godot 拉取地图、玩家、NPC、时间和事件。
- `POST /api/player/action`：处理玩家聊天、送礼和事件互动。
- LLM Provider 接入 DeepSeek V4 Flash 测试。
- 6 个 NPC 的首日角色卡、幻想显示名、日程和关系。
- 3 个地点的静态资产与交互区域。
- 玩家与 NPC 地图小人静态资产。
- 角色半身立绘、基础表情差分和 Visual Novel 对话 UI。
- 1 个小镇事件。
- 夜晚 NPC 日记 / 反思摘要。
- Web Debug 控制台保留并逐步迁移到 `web-admin/`。

### 明确暂缓

- 完整农场经营。
- 四季、天气、作物生长循环。
- 完整恋爱、告白和结婚系统。
- 多年人口演化。
- 大地图和复杂寻路。
- 联机玩法。
- 运行时图片生成。

## 推荐叙事切片

### 玩家第一天主线

1. 早晨：玩家搬入农场，收到小镇欢迎任务。
2. 上午：去广场认识居民，选择 2 个 NPC 聊天。
3. 下午：把农场初始作物或礼物带到酒馆，触发送礼/交付。
4. 傍晚：酒馆或广场出现小镇事件。
5. 夜晚：NPC 根据当天互动生成主观记忆和日记摘要。

### 首个小镇事件建议

`星灯祭前夜 + 农场供应短缺`

- 月猫酒馆计划晚上准备星灯祭小聚和节日点心。
- 凯娅想维持节日气氛，但布兰娜因为旧欠账与供货压力拒绝继续供应农产品。
- 玩家可以选择把农场作物交给酒馆、安抚冲突、支持某一方或旁观。
- 米娅·星麦会从经济与供货角度评价，莉娜·白桦会关注压力与健康，奥蕾娅·星历会把事件联系到星灯祭传统，托玛·榆庭可以作为默默修理灯架的背景参与者。
- 夜晚不同 NPC 写入不同记忆，第二天对玩家态度产生差异。

## 首发 NPC 裁剪方案

首版建议使用以下 6 个 NPC，性别比例为 5 女 1 男。只保留托玛·榆庭作为男性首发 NPC；后续扩展默认沿用女性占多数的比例，等男性角色资产一致性被验证后再适当增加男性角色比重。小镇允许同性配偶、双母家庭、单亲、收养和其他多元家庭关系，这些关系按叙事需要正常存在。

| NPC | 首版作用 | 核心张力 | 恋爱铺垫 |
| --- | --- | --- | --- |
| 米娅·星麦（`mira`） | 杂货铺店主，负责生活物资与经济线 | 照顾家庭与维持店铺之间的压力 | 温柔照顾线 |
| 托玛·榆庭（`tomas`） | 木匠，负责修缮与家庭线 | 沉默保护欲与表达不足 | 沉默守护线 |
| 奥蕾娅·星历（`orren`） | 退休教师，负责小镇历史与传统 | 健康风险与固执观念 | 不作为候选 |
| 莉娜·白桦（`lena`） | 医生，负责健康与理性判断 | 过度疲惫与公共责任 | 理性克制线 |
| 凯娅·月弦（`kai`） | 酒馆乐手，负责社交与节日氛围 | 浪漫冲动与欠账冲突 | 热情直球线 |
| 布兰娜·麦垄（`bram`） | 农场主，负责农场主题与供应线 | 直率记仇与酒馆欠账 | 成熟直率线后续扩展 |

暂缓 NPC 作为扩展池：妮娜、萨娜、里奥、艾薇。

## 视觉资产计划

首版主风格：二次元轻幻想轻异世界田园生活模拟。

`gpt-image-2` 优先用于生成二次元角色半身立绘、表情差分、场景背景、星灯祭事件 CG、Visual Novel 风格 UI 参考和作品集配图。像素风首版只作为地图小人占位或后续专项资产方向。

详细美术风格、角色设定、提示词摘要和生成顺序见 [`art_direction.md`](./art_direction.md)，可复制提示词见 [`asset_generation_prompts.md`](./asset_generation_prompts.md)。

### 第一批资产

优先生成风格锁定资产：

- `style/style_key_art_agent_valley.png`：星灯谷整体风格图。
- `style/style_character_lineup_day1.png`：6 个 NPC 同框角色比例与风格参考。
- `ui/anime_dialogue_panel_style.png`：Visual Novel 风格 UI 参考。

正式首版资产：

- `locations/farm_day_anime.png`：晨露农场白天背景。
- `locations/plaza_day_anime.png`：中央广场白天背景。
- `locations/tavern_evening_anime.png`：月猫酒馆傍晚背景。
- `characters/player_farmer_neutral.png`：偏少女玩家农场主默认半身立绘。
- `characters/player_farmer_happy.png`：玩家农场主开心差分。
- `characters/player_farmer_troubled.png`：玩家农场主困惑差分。
- `characters/npc_mira_neutral.png`、`characters/npc_mira_happy.png`、`characters/npc_mira_troubled.png`
- `characters/npc_tomas_neutral.png`、`characters/npc_tomas_happy.png`、`characters/npc_tomas_troubled.png`
- `characters/npc_orren_neutral.png`、`characters/npc_orren_happy.png`、`characters/npc_orren_troubled.png`
- `characters/npc_lena_neutral.png`、`characters/npc_lena_happy.png`、`characters/npc_lena_troubled.png`
- `characters/npc_kai_neutral.png`、`characters/npc_kai_happy.png`、`characters/npc_kai_troubled.png`
- `characters/npc_bram_neutral.png`、`characters/npc_bram_happy.png`、`characters/npc_bram_troubled.png`
- `sprites/player_farmer_map_idle.png`：偏少女玩家农场主地图小人。
- `sprites/npc_mira_map_idle.png`、`sprites/npc_tomas_map_idle.png`、`sprites/npc_orren_map_idle.png`
- `sprites/npc_lena_map_idle.png`、`sprites/npc_kai_map_idle.png`、`sprites/npc_bram_map_idle.png`
- `sprites/interaction_marker_talk.png`、`sprites/interaction_marker_gift.png`、`sprites/interaction_marker_event.png`
- `cg/starlight_festival_shortage_event.png`：星灯祭供应短缺事件 CG。
- `icons/item_fresh_turnip.png`、`icons/item_farm_flower.png`、`icons/item_starlight_lantern.png`
- `ui/dialogue_box_anime.png`、`ui/nameplate_anime.png`、`ui/choice_button_anime.png`、`ui/memory_card_anime.png`

### 资产规则

- 原始图进入 `assets/source/`。
- 裁切、压缩、导入图进入 `assets/processed/` 或 `clients/godot/assets/`。
- 资产清单进入 `assets/manifests/asset_manifest.json`。
- 每张资产记录用途、生成提示词摘要、生成日期、表情差分、原始尺寸、处理路径和是否进入 Godot。
- 同一角色的所有差分必须保持发型、服饰、瞳色和配饰一致。

## 技术推进批次

### 批次 0：环境和路线冻结

目标：确保项目可以从当前观察台稳定进入游戏客户端开发。

任务：

1. 确认 Godot 版本并记录安装方式。
2. 处理本地检查命令的 Python/Node 入口差异。
3. 将 `config/models.json` 的真实使用方式梳理清楚，避免密钥进入仓库。
4. 确认 DeepSeek V4 Flash 的模型名、Base URL 和环境变量。

验收：

- Python smoke test 可运行。
- Godot 可启动空项目。
- 后端能在本地启动并返回世界状态。

### 批次 1：Godot 最小客户端 Spike

目标：验证 Godot 与 Python 后端的协作模式。

任务：

1. 创建 `clients/godot/`。
2. 搭建 `main.tscn`、`town_map.tscn`、`player.tscn`、`npc.tscn`。
3. 实现玩家 WASD / 方向键移动。
4. 实现 `api_client.gd`，从后端拉取世界状态。
5. 在场景里显示 3 个地点与 3 个测试 NPC。
6. 点击或靠近 NPC 时打开对话面板。
7. 对话面板支持半身立绘、表情字段和基础选择按钮占位。

验收：

- Godot 客户端能启动到可移动场景。
- 能从 Python 后端读取 NPC 状态。
- NPC 名称、位置、当前状态能显示在游戏内。
- 玩家可以从地图移动进入 VN 对话层，再返回地图继续移动。

### 批次 2：后端游戏 API

目标：让后端从观察台 API 扩展为游戏客户端 API。

任务：

1. 增加 `GET /api/world/state`，保留旧 `/api/state` 兼容观察台。
2. 增加玩家状态：位置、背包、已认识 NPC、当天行动记录。
3. 增加 `POST /api/player/action`。
4. 支持玩家动作：`talk`、`give_gift`、`attend_event`。
5. 将玩家动作写入 EventStore。
6. 将玩家动作对 NPC 关系和记忆的影响显式记录。

验收：

- 玩家和 NPC 对话能从 Godot 发到后端并返回。
- 事件流中能看到玩家动作、LLM 输出、关系变化和记忆写入。
- 旧 Web Debug 控制台能看到同一条交互链路。

### 批次 3：LLM 真实接入

目标：直接用 LLM 验证首版对话与事件反应，减少规则系统空转。

任务：

1. 配置 DeepSeek V4 Flash Profile。
2. 为玩家聊天设计 Prompt 模板。
3. 为小镇事件反应设计 Prompt 模板。
4. 为夜间反思设计 Prompt 模板。
5. 要求模型输出结构化 JSON，并保留自然语言兜底解析。
6. 记录 token、延迟、错误、fallback 和成本估算。

验收：

- 至少 3 个 NPC 能基于玩家行为生成差异化回应。
- 星灯祭事件能让多个 NPC 写入不同记忆。
- LLM 调用失败时 Demo 不崩溃。

### 批次 3.5：Director 与 Event Skill 最小原型

目标：把项目从单层 NPC 调度推进到多层 Agent 游戏系统，让事件由 Director Beat 和 Event Skill 驱动。

任务：

1. 定义 `WorldDigest`、`DirectorBeat` 和 `EventSkill` schema。
2. 增加规则版 `WorldDigestBuilder`，输出时间段、玩家位置、高张力关系、候选事件和关键记忆摘要。
3. 增加规则版 `TensionDetector` 和 `SkillRouter`，先覆盖星灯祭供应短缺触发。
4. 增加 `DirectorQueueManager`，支持 Beat 入队、过期、取消和按 tick 消费。
5. 增加 `DirectorValidator`，校验世界版本、生效窗口、目标 Agent、允许 Skill 和工具权限。
6. 将星灯祭供应短缺从硬编码事件迁移为 Event Skill 数据。
7. Debug Console 记录 Director Beat 输入、输出、校验结果、消费结果和 fallback。

验收：

- 规则版 Director v0 能根据世界摘要生成一个可消费的 `activate_event_skill` Beat。
- Beat 过期或世界版本不匹配时不会改动世界状态，并会进入 Debug 事件。
- 星灯祭供应短缺可由 Event Skill 加载，仍保持玩家查看、选择、关系变化、记忆和夜间反思链路。
- 不调用强模型时，完整 Demo 仍可离线运行。

### 批次 4：第一天内容落地

目标：完成一条可玩的主线体验。

任务：

1. 裁剪世界到 6 个首发 NPC 和 3 个地点。
2. 为 6 个 NPC 写首日角色卡、幻想显示名、视觉原型、说话风格、日程、喜好和冲突关系。
3. 实现基础送礼、关系变化和恋爱铺垫标签。
4. 实现星灯祭供应短缺事件。
5. 实现夜晚反思与日记摘要。
6. 在 Debug 控制台增加事件链路视图。

验收：

- 玩家能完整玩完第一天。
- 至少一次玩家选择会影响后续 NPC 对话。
- 至少 2 个恋爱候选 NPC 会在后续对话中体现轻微好感变化。
- 夜晚能看到 6 个 NPC 中至少 3 个产生不同主观记忆。

### 批次 5：视觉与演示打磨

目标：让 Demo 具备作品集截图与录屏价值。

任务：

1. 生成并筛选第一批二次元轻幻想轻异世界资产。
2. 导入 Godot 并统一命名。
3. 完成地图小人、对话框、角色头像、半身立绘、表情差分和事件 CG 展示。
4. 为 Debug 控制台整理清晰的决策记录视图。
5. 写一份 Demo 讲解脚本。
6. 录制 1 条 2-3 分钟演示视频。

验收：

- Demo 第一屏能看出“二次元田园轻幻想生活模拟”气质。
- 交互链路能被清楚讲解。
- 截图包含游戏画面、NPC 对话和 Debug 解释三类展示素材。

## 目录演进

```text
ai-agent-town/
├── backend/                 # Python Agent Server
├── clients/
│   └── godot/               # Godot 游戏客户端
├── web-admin/               # Debug / 研究控制台，后续从 frontend 迁移
├── frontend/                # 旧观察台，迁移期保留
├── assets/
│   ├── source/              # Codex 生图原始资产
│   ├── processed/           # 处理后资产
│   └── manifests/           # 资产清单
├── docs/
├── experiments/             # 可选：Demo 回放、运行日志、调试导出
└── scripts/
```

## 初版成功标准

### 体验标准

- 玩家 3 分钟内理解：这是一个由 AI 居民自主生活的小镇。
- 玩家至少能完成移动、聊天、送礼和参加事件。
- NPC 会记住玩家行为，并在后续对话里体现。

### 技术标准

- 每次关键 NPC 反应都有可追踪链路：上下文、模型输出、解析行动、执行结果、记忆写入。
- Godot 客户端不保存权威世界状态。
- 后端支持 LLM Provider 和规则 fallback。
- Debug 控制台可以用于现场解释。

### 工程标准

- Windows 本地启动步骤清晰。
- 核心检查脚本可运行。
- 资产有清单和来源记录。
- 新增 NPC、地点、事件和玩家动作有明确扩展路径。

## 最近一次工作建议

下一次正式实现优先做：

1. 按 [`art_direction.md`](./art_direction.md) 先生成 3 张风格锁定资产，并由主人确认主视觉方向。
2. 启动后端后，用 Godot 编辑器运行 `clients/godot/project.godot` 主场景并验证状态同步。
3. 裁剪首版 6 NPC 和 3 地点数据，并补齐幻想显示名、视觉资产引用和恋爱铺垫字段。
4. 接入星灯祭供应短缺事件的 `attend_event` 链路。
5. 根据 Godot 实测调整 `GET /api/world/state` 的字段体积和同步频率。
6. 配置 DeepSeek V4 Flash Profile，并用 1 个 NPC 做真实 LLM 对话测试。

已完成的正式开发第一轮：

- `GET /api/world/state` 游戏状态接口。
- 最小 `PlayerState`。
- `POST /api/player/action` 的 `move`、`talk` 和 `give_gift` 链路。
- 玩家对话后的事件、关系变化、NPC 记忆和 Debug 记录。

已完成的正式开发第二轮：

- `clients/godot/` Godot 4.x 项目骨架。
- `ApiClient` 读取世界状态并提交玩家动作。
- `WorldSync` 缓存玩家、地点、NPC 和最近事件。
- 主场景文本面板显示后端状态。
- `scripts/check_godot_project.py` 进入 `npm.cmd run check`。

已完成的客户端环境准备：

- 安装并验证 Godot 4.6.2 标准版。
- 增加 `npm.cmd run client:env` 检查本机 Godot 环境。
- 增加 `npm.cmd run client:open` 打开 Godot 项目。
- 增加 [`game_client_environment.md`](./game_client_environment.md) 新手环境说明。

## 正式开发前置文档

- [`current_status.md`](./current_status.md)：用于判断当前代码基线、主要缺口和硬性工程约束。
- [`vertical_slice_spec.md`](./vertical_slice_spec.md)：用于指导第一天可玩章节的数据契约、内容规格和扩展性验收。
