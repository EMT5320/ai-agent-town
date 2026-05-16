# 第二批地图小人质量回退与交互标记保留记录

日期：2026-05-16
范围：`npc_orren_map_idle`、`npc_lena_map_idle`、`npc_kai_map_idle`、`npc_bram_map_idle` 四张静态 `idle_front` 地图小人，以及 `interaction_marker_talk`、`interaction_marker_gift`、`interaction_marker_event` 三个交互标记。

## 本轮结论

1. 停止扩展生成：本轮不生成新图，不新增地图角色资产，不修改 Godot 代码或后端代码。
2. 第一批 `player_farmer_map_idle`、`npc_mira_map_idle`、`npc_tomas_map_idle` 在 `asset_manifest.json` 中标为 `style_anchor_candidate`，作为当前地图小人风格候选锚点。
3. 第二批四个地图小人全部评审失败，在 `asset_manifest.json` 中标为 `redraw_required`。
4. `redraw_required` 是正式地图角色层的硬阻断状态；这些文件可留作失败样本和重画参照，不能接入正式地图角色层。
5. `interaction_marker_talk`、`interaction_marker_gift`、`interaction_marker_event` 保留为 `pending_review` 图标候选，仅用于后续 UI / 地图提示图标评审。

## 输出文件与回退状态

| 资产 ID | source | processed | Godot 同步文件 | Manifest 状态 | 接入结论 |
| --- | --- | --- | --- | --- | --- |
| `npc_orren_map_idle` | `assets/source/sprites/npc_orren_map_idle.png` | `assets/processed/sprites/npc_orren_map_idle.png` | `clients/godot/assets/sprites/npc_orren_map_idle.png` | `redraw_required` | 禁止接入正式地图角色层 |
| `npc_lena_map_idle` | `assets/source/sprites/npc_lena_map_idle.png` | `assets/processed/sprites/npc_lena_map_idle.png` | `clients/godot/assets/sprites/npc_lena_map_idle.png` | `redraw_required` | 禁止接入正式地图角色层 |
| `npc_kai_map_idle` | `assets/source/sprites/npc_kai_map_idle.png` | `assets/processed/sprites/npc_kai_map_idle.png` | `clients/godot/assets/sprites/npc_kai_map_idle.png` | `redraw_required` | 禁止接入正式地图角色层 |
| `npc_bram_map_idle` | `assets/source/sprites/npc_bram_map_idle.png` | `assets/processed/sprites/npc_bram_map_idle.png` | `clients/godot/assets/sprites/npc_bram_map_idle.png` | `redraw_required` | 禁止接入正式地图角色层 |
| `interaction_marker_talk` | `assets/source/sprites/interaction_marker_talk.png` | `assets/processed/sprites/interaction_marker_talk.png` | `clients/godot/assets/sprites/interaction_marker_talk.png` | `pending_review` | 仅保留为 talk 图标候选 |
| `interaction_marker_gift` | `assets/source/sprites/interaction_marker_gift.png` | `assets/processed/sprites/interaction_marker_gift.png` | `clients/godot/assets/sprites/interaction_marker_gift.png` | `pending_review` | 仅保留为 gift 图标候选 |
| `interaction_marker_event` | `assets/source/sprites/interaction_marker_event.png` | `assets/processed/sprites/interaction_marker_event.png` | `clients/godot/assets/sprites/interaction_marker_event.png` | `pending_review` | 仅保留为 event 图标候选 |

对比图保留：`assets/processed/sprites/map_sprite_second_batch_64_32_check.png`

> 说明：`clients/godot/assets/sprites/` 中的同步 PNG 只代表文件已存在；正式地图角色层需要额外代码或配置引用。本轮不修改 Godot 代码，并把第二批四个地图小人的 manifest 状态改成 `redraw_required`，用于阻断后续正式接入。

## 失败判定基准

当前候选锚点为第一批三张地图小人：

- `player_farmer_map_idle`：绿色玩家农场主轮廓、种子挎包和大头 Q 版比例可作为主角地图小人参照。
- `npc_mira_map_idle`：栗色头发、暖橙围裙、账本 / 种子店主读感可作为女性 NPC 地图小人参照。
- `npc_tomas_map_idle`：蓝色工作衫、腰带工具、男性木匠剪影可作为男性 NPC 地图小人参照。

后续小人需要先贴近上述锚点的：

1. 64px 下的二次元 Q 版低像素比例。
2. 32px 下仍能识别的主色、发型和职业道具。
3. 稳定外轮廓线宽和低细节块面组织。
4. 从角色参考图 / neutral 立绘继承身份信息的能力。

## 单图失败原因

| 资产 ID | 主要失败点 | 32px 风险 | 回退处理 |
| --- | --- | --- | --- |
| `npc_orren_map_idle` | 银发、书本、绿色外套在当前图中容易合并，长者读感依赖局部细节；整体比例和第一批候选锚点的 Q 版地图小人不够统一。 | 银发与书本压缩成相近浅色块，身份会变成泛用绿衣角色。 | 标记 `redraw_required`；重画时优先放大头部银发轮廓，弱化书本道具体积，统一线宽。 |
| `npc_lena_map_idle` | 医生白 coat 面积过大，角色主体在小尺寸下变成白色块面；医疗身份和青绿色发型缺少稳定轮廓区分。 | 32px 下白 coat 抢占主体，职业读感和发型识别都不稳定。 | 标记 `redraw_required`；重画时压缩白 coat 面积，保留青绿色发型大轮廓和更清楚的医疗标志。 |
| `npc_kai_map_idle` | 乐手身份道具读感弱，红发和暖色披肩更接近泛用酒馆村民；与第一批锚点相比，身份继承不够直接。 | 32px 下只剩红发和暖色服装块，难以稳定读成乐手。 | 标记 `redraw_required`；重画时强化乐器或音符形职业符号，并减少服装碎细节。 |
| `npc_bram_map_idle` | 木箱道具占比过高，视觉重心从角色主体移到外部道具；农场主剪影不利于后续 idle / 行走帧扩展。 | 32px 下草帽与木箱比人物主体更显眼，角色身份会被道具遮蔽。 | 标记 `redraw_required`；重画时缩小或移除木箱，把草帽、农具和工作服整合进角色主体。 |

## 交互标记保留规则

| 资产 ID | 当前用途 | 保留条件 | 后续评审重点 |
| --- | --- | --- | --- |
| `interaction_marker_talk` | talk 地图提示 / UI 图标候选 | 保持 `pending_review`，只按图标资产评审。 | 32px 对话气泡轮廓、描边和地图背景对比度。 |
| `interaction_marker_gift` | gift 地图提示 / UI 图标候选 | 保持 `pending_review`，只按图标资产评审。 | 礼盒 / 作物符号在 32px 下的可读性和色彩区分。 |
| `interaction_marker_event` | event 地图提示 / UI 图标候选 | 保持 `pending_review`，只按图标资产评审。 | 星灯 / 事件符号是否会和普通星光装饰混淆。 |

## 后续重画准备

1. 以第一批三张 `style_anchor_candidate` 作为地图小人提示词和评审参照。
2. 重画前先收紧提示词：减少外部道具体积，固定角色可见尺寸，强调 32px 身份读感。
3. 新一轮生成后继续先登记为 `pending_review`，完成 64px / 32px 对比检查后再决定是否晋级。
4. 当前四张 `redraw_required` 小人不得被导入正式角色层、地图出生点、NPC 行走逻辑或展示配置。
