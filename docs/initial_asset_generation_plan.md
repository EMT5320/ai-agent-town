---
status: snapshot
owner_lane: asset-pipeline
last_verified: 2026-05-17
startup_load: on-demand
source_of_truth: false
scope: initial asset generation batches and historical asset sequencing
---

# 初版游戏资产生成执行计划

> 状态更新时间：2026-05-15
> 本文承接 `art_direction.md`、`asset_generation_prompts.md` 与 `vertical_slice_spec.md`，用于把已经确定的美术方向推进到可进入 Godot 的正式资产批次。

## 当前结论

项目已经完成风格锁定层：

- `assets/source/style/style_key_art_agent_valley.png`
- `assets/source/style/style_character_lineup_day1.png`
- `assets/source/ui/anime_dialogue_panel_style.png`
- 玩家农场主与 6 个首发 NPC 的 reference sheet

这些资产适合继续作为风格、角色比例、服饰复杂度和 UI 形状语言的基线。当前缺口集中在正式游戏可消费资源：happy/troubled 半身立绘差分、行动反馈图标、生活行动 UI 小组件，以及后续可直接导入的地点背景与事件 CG。

代码层仍保留旧观察台的 10 NPC / 6 地点种子数据；首版正式资产按文档冻结的 6 NPC / 3 地点执行。旧 NPC 和旧地点先作为扩展池，不进入本轮正式资产生成。

## 首版资产范围

### 必需资产

| 类别 | 数量 | 用途 | 优先级 |
| --- | ---: | --- | --- |
| 地点背景 | 3 | 农场、广场、酒馆；用于地图/VN 背景和截图展示 | P0 |
| 事件 CG | 1 | 星灯祭供应短缺关键演出 | P0 |
| 玩家半身立绘 | 3 | `neutral`、`happy`、`troubled` 对话层 | P1 |
| NPC 半身立绘 | 18 | 6 NPC x 3 表情 | P1 |
| 地图小人 | 7 | 玩家 + 6 NPC 的地图层表现 | P1 |
| 互动标记 | 3 | 对话、送礼、事件入口 | P2 |
| 道具图标 | 3 | 芜菁、小花、星灯灯笼 | P2 |
| 行动反馈图标 | 5 | move/talk/gift/inspect/event 的即时反馈 | P1 |
| 生活行动 UI 小组件 | 5 | 生活行动按钮、日程条、结果浮层 | P1 |
| UI 组件 | 4 | 对话框、名牌、选择按钮、记忆卡片 | P2 |

### 扩展池资产

以下资产暂缓到首版闭环稳定后生成：

- 妮娜、萨娜、里奥、艾薇的头像、立绘和小人。
- 北街住宅区、星露杂货铺、白桦诊所的地点背景。
- 完整 UI 皮肤、夜间日记面板、礼物确认面板、关系变化徽章。
- 星灯祭第二张交付选择 CG。

## 生成顺序

### 批次 1A：首屏场景资产

本批次先生成 4 张最能提升可玩画面的资产：

1. `assets/source/locations/farm_day_anime.png`
2. `assets/source/locations/plaza_day_anime.png`
3. `assets/source/locations/tavern_evening_anime.png`
4. `assets/source/cg/starlight_festival_shortage_event.png`

原因：

- 它们不依赖角色差分一致性，生成风险较低。
- Godot 当前还没有图片接入，地点背景最适合作为第一批 `TextureRect` 资产。
- 事件 CG 可直接服务作品集截图和后续剧情演出。

### 批次 1B：对话层角色资产

先生成玩家与 6 NPC 的 `neutral` 半身立绘，确认角色 reference sheet 到 VN portrait 的转换质量，再补 `happy`、`troubled` 差分。

角色生成时必须参考现有 reference sheet 的设定摘要：

- 发型、瞳色、服饰主色和标志物保持一致。
- 同一角色差分只改变表情和轻微姿态。
- 透明背景优先；若工具路径不能直接保证透明，则先以可裁切的纯色背景进入后处理。

### 批次 1C：地图层资产

生成玩家与 6 NPC 的静态地图小人，以及 `talk`、`gift`、`event` 三个交互标记。首版先用静态小人验证可玩闭环，行走动画和多方向 Sprite Sheet 后续专项处理。

### 批次 1D：道具和 UI 组件

生成 3 个道具图标与 4 个 UI 组件。UI 组件后续可以在 Godot 中重建为 Control + Theme；生成图主要提供形状语言、边框、色彩和星灯纹样参考。

### 批次 2A：表情差分与生活行动反馈（prompt-ready）

本批次在不伪造源图的前提下，先把 backlog 写成可校验 manifest 条目：

1. 14 张角色差分：玩家 + 6 NPC 的 `happy` / `troubled`。
2. 5 张行动反馈图标：`move`、`talk`、`gift`、`inspect`、`event`。
3. 5 张生活行动 UI 小组件：3 个行动按钮 + 日程条 + 结果浮层。

执行约束：

- manifest 状态统一标记为 `prompt_ready`，禁止提前标记 `source_selected`。
- `fullPromptRef` 使用 `docs/asset_generation_prompts.md` 的锚点段落，便于校验。
- `processedPath` 与 `godotPath` 保持 `null`，直到源图真实生成并筛选通过。

## 资产登记规则

每张筛选进入首版的图需要登记到 `assets/manifests/asset_manifest.json`：

- `path` 指向 `assets/source/...`。
- `fullPromptRef` 已生成资产指向 `assets/manifests/prompts/...txt`；prompt 计划条目可指向 `docs/asset_generation_prompts.md#...` 锚点。
- 已生成并通过筛选的条目使用 `source_selected`；仅完成 prompt 计划的条目使用 `prompt_ready`。
- `prompt_ready` 条目必须保持 `processedPath=null`、`godotPath=null`。
- `reviewNotes` 记录是否能承载对话 UI、是否有不可控文字、是否需要重生成。

## 质量门槛

生成后至少检查：

- 场景无可读文字、无水印、无明显现代都市或暗黑偏移。
- 背景中央和下方可叠加半身立绘与对话框。
- 地点之间有明显辨识度：农场是晨露与作物，广场是公共空间，酒馆是暖光和社交。
- 事件 CG 中凯娅、布兰娜、玩家的位置关系清楚，能看出供应短缺冲突。
- 文件名保持 lowercase snake_case。

## Godot 接入路线

1. 首批源图进入 `assets/source/...` 并登记 manifest。
2. 后续处理脚本复制或压缩到 `clients/godot/assets/...`。
3. Manifest 的 `godotPath` 填 `res://assets/...`。
4. Godot 侧新增资产 registry，按 `location.id`、`npc.id`、`expression` 读取对应纹理。

首版可以先将 3 张地点背景接到主场景文本面板后方，再逐步替换为正式地图层和 VN 对话层。
