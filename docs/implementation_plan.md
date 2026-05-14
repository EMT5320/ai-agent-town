# 初版实施计划

本计划面向 `Agent Valley` 第一版可玩垂直切片。目标是在当前仓库原地演进，用 Godot 承担玩家体验，用 Python Agent Server 承担世界状态、LLM NPC、记忆、事件和 Debug 数据。

## 初版目标

完成一个可录屏、可讲解、可继续扩展的“第一天”Demo：

- 玩家作为新搬来的农场主进入小镇。
- 小镇包含 3 个地点：农场、广场、酒馆。
- 首发 6 个 NPC，有人设、日程、关系、喜好、记忆和对玩家的持续反应。
- 玩家可以移动、聊天、送礼、触发小镇事件。
- NPC 使用 LLM 生成关键对话、事件反应和夜间反思。
- Debug / 研究控制台可以看到 Prompt、模型输出、行动解析、记忆写入和关系变化。

## 首版范围冻结

### 必须进入首版

- Godot Windows 桌面客户端。
- Python 后端继续作为权威世界状态。
- `GET /api/world/state`：给 Godot 拉取地图、玩家、NPC、时间和事件。
- `POST /api/player/action`：处理玩家聊天、送礼和事件互动。
- LLM Provider 接入 DeepSeek V4 Flash 测试。
- 6 个 NPC 的首日角色卡、日程和关系。
- 3 个地点的静态资产与交互区域。
- 1 个小镇事件。
- 夜晚 NPC 日记 / 反思摘要。
- Web Debug 控制台保留并逐步迁移到 `web-admin/`。

### 明确暂缓

- 完整农场经营。
- 四季、天气、作物生长循环。
- 恋爱结婚系统。
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

`星灯节筹备 + 农场供应短缺`

- 酒馆计划晚上举办星灯节小聚。
- 布拉姆因供应短缺和凯发生争执。
- 玩家可以选择把农场作物交给酒馆、安抚冲突、支持某一方或旁观。
- 米拉会从经济角度评价，蕾娜会关注压力与健康，奥伦会把事件联系到小镇传统。
- 夜晚不同 NPC 写入不同记忆，第二天对玩家态度产生差异。

## 首发 NPC 裁剪方案

首版建议使用以下 6 个 NPC：

| NPC | 首版作用 | 核心张力 |
| --- | --- | --- |
| 米拉 | 杂货铺店主，负责生活物资与经济线 | 照顾家庭与维持店铺之间的压力 |
| 托马斯 | 木匠，负责修缮与家庭线 | 沉默保护欲与表达不足 |
| 奥伦 | 退休教师，负责小镇历史与传统 | 健康风险与固执观念 |
| 蕾娜 | 医生，负责健康与理性判断 | 过度疲惫与公共责任 |
| 凯 | 酒馆乐手，负责社交与节日氛围 | 浪漫冲动与欠账冲突 |
| 布拉姆 | 农夫，负责农场主题与供应线 | 直率记仇与酒馆欠账 |

暂缓 NPC 作为扩展池：妮娜、萨娜、里奥、艾薇。

## 视觉资产计划

首版主风格：温暖绘本风生活模拟。

`gpt-image-2` 更适合生成插画化角色、场景、事件 CG 和 UI 风格参考；像素风首版只作为地图小人占位或后续专项资产方向。

### 第一批资产

- `locations/farm_day.png`：农场白天背景。
- `locations/plaza_day.png`：广场白天背景。
- `locations/tavern_evening.png`：酒馆傍晚背景。
- `characters/player_farmer.png`：玩家概念图。
- `characters/npc_mira.png`
- `characters/npc_tomas.png`
- `characters/npc_orren.png`
- `characters/npc_lena.png`
- `characters/npc_kai.png`
- `characters/npc_bram.png`
- `cg/starlight_shortage_event.png`：星灯节供应短缺事件 CG。
- `ui/storybook_panel_style.png`：绘本风 UI 面板参考。

### 资产规则

- 原始图进入 `assets/source/`。
- 裁切、压缩、导入图进入 `assets/processed/` 或 `clients/godot/assets/`。
- 资产清单进入 `assets/manifests/asset_manifest.json`。
- 每张资产记录用途、生成提示词摘要、生成日期和是否进入 Godot。

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

验收：

- Godot 客户端能启动到可移动场景。
- 能从 Python 后端读取 NPC 状态。
- NPC 名称、位置、当前状态能显示在游戏内。

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
- 星灯节事件能让多个 NPC 写入不同记忆。
- LLM 调用失败时 Demo 不崩溃。

### 批次 4：第一天内容落地

目标：完成一条可玩的主线体验。

任务：

1. 裁剪世界到 6 个首发 NPC 和 3 个地点。
2. 为 6 个 NPC 写首日角色卡、日程、喜好和冲突关系。
3. 实现基础送礼和关系变化。
4. 实现星灯节供应短缺事件。
5. 实现夜晚反思与日记摘要。
6. 在 Debug 控制台增加事件链路视图。

验收：

- 玩家能完整玩完第一天。
- 至少一次玩家选择会影响后续 NPC 对话。
- 夜晚能看到 6 个 NPC 中至少 3 个产生不同主观记忆。

### 批次 5：视觉与演示打磨

目标：让 Demo 具备作品集截图与录屏价值。

任务：

1. 生成并筛选第一批绘本风资产。
2. 导入 Godot 并统一命名。
3. 完成对话框、角色头像、事件 CG 展示。
4. 为 Debug 控制台整理清晰的决策记录视图。
5. 写一份 Demo 讲解脚本。
6. 录制 1 条 2-3 分钟演示视频。

验收：

- Demo 第一屏能看出“温暖小镇生活模拟”气质。
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

1. 修正本地检查命令：优先让 `python3 scripts/smoke_test.py`、`python3 -m compileall` 稳定，再处理 Windows Node / WSL Node 差异。
2. 新建 `clients/godot/` 空项目骨架。
3. 增加 `GET /api/world/state` 兼容接口。
4. 增加 `POST /api/player/action` 的最小对话链路。
5. 配置 DeepSeek V4 Flash Profile，并用 1 个 NPC 做真实 LLM 对话测试。
