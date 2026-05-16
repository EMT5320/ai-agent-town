# 第二批地图小人和交互标记 64x64 / 32x32 对比检查

日期：2026-05-16
范围：`npc_orren_map_idle`、`npc_lena_map_idle`、`npc_kai_map_idle`、`npc_bram_map_idle` 四张静态 `idle_front` 地图小人，以及 `interaction_marker_talk`、`interaction_marker_gift`、`interaction_marker_event` 三个交互标记。

## 输出文件

| 资产 ID | source | processed | Godot 同步 | Manifest 状态 |
| --- | --- | --- | --- | --- |
| `npc_orren_map_idle` | `assets/source/sprites/npc_orren_map_idle.png` | `assets/processed/sprites/npc_orren_map_idle.png` | `clients/godot/assets/sprites/npc_orren_map_idle.png` | `pending_review` |
| `npc_lena_map_idle` | `assets/source/sprites/npc_lena_map_idle.png` | `assets/processed/sprites/npc_lena_map_idle.png` | `clients/godot/assets/sprites/npc_lena_map_idle.png` | `pending_review` |
| `npc_kai_map_idle` | `assets/source/sprites/npc_kai_map_idle.png` | `assets/processed/sprites/npc_kai_map_idle.png` | `clients/godot/assets/sprites/npc_kai_map_idle.png` | `pending_review` |
| `npc_bram_map_idle` | `assets/source/sprites/npc_bram_map_idle.png` | `assets/processed/sprites/npc_bram_map_idle.png` | `clients/godot/assets/sprites/npc_bram_map_idle.png` | `pending_review` |
| `interaction_marker_talk` | `assets/source/sprites/interaction_marker_talk.png` | `assets/processed/sprites/interaction_marker_talk.png` | `clients/godot/assets/sprites/interaction_marker_talk.png` | `pending_review` |
| `interaction_marker_gift` | `assets/source/sprites/interaction_marker_gift.png` | `assets/processed/sprites/interaction_marker_gift.png` | `clients/godot/assets/sprites/interaction_marker_gift.png` | `pending_review` |
| `interaction_marker_event` | `assets/source/sprites/interaction_marker_event.png` | `assets/processed/sprites/interaction_marker_event.png` | `clients/godot/assets/sprites/interaction_marker_event.png` | `pending_review` |

对比图：`assets/processed/sprites/map_sprite_second_batch_64_32_check.png`

## 处理方式

1. 沿用二次元 Q 版低像素地图小人规范，输出 `64x64` 透明 PNG。
2. 使用 `assets/manifests/prompts/*_map_idle.txt` 约束 4 个后续 NPC。
3. 使用 `assets/manifests/prompts/interaction_marker_*.txt` 约束交互标记，保持小尺寸 UI 可读性。
4. 同步到 `assets/source/sprites/`、`assets/processed/sprites/`、`clients/godot/assets/sprites/`。
5. `asset_manifest.json` 全部保持 `pending_review`，本轮没有提升为 `source_selected`。

## 单图检查结论

| 资产 ID | 64px 读感 | 32px 读感 | 结论 |
| --- | --- | --- | --- |
| `npc_orren_map_idle` | 银发、绿色外套和书卷感清楚，长者身份成立。 | 32px 仍能读出银发长者和绿色主色，书本细节弱化。 | 继续保持 `pending_review`。 |
| `npc_lena_map_idle` | 医生白 coat、青绿色头发和冷静姿态清楚。 | 32px 仍能读出医生白色轮廓和青绿色头发。 | 继续保持 `pending_review`。 |
| `npc_kai_map_idle` | 红发、酒馆乐手披肩和活泼气质成立。 | 32px 仍能读出红发与酒馆暖色主色。 | 继续保持 `pending_review`。 |
| `npc_bram_map_idle` | 草帽、农场主棕色工作服和木箱道具清楚。 | 32px 仍能读出草帽与农场主剪影。 | 继续保持 `pending_review`。 |
| `interaction_marker_talk` | 对话气泡清楚，星点装饰贴合轻幻想风。 | 32px 仍能读出对话标记。 | 继续保持 `pending_review`。 |
| `interaction_marker_gift` | 礼盒与作物色块清楚。 | 32px 仍能读出礼物标记。 | 继续保持 `pending_review`。 |
| `interaction_marker_event` | 星灯/事件符号清楚，适合作为事件入口标记。 | 32px 仍能读出星形事件提示。 | 继续保持 `pending_review`。 |

## 后续人工评审关注点

- `npc_orren_map_idle` 的书本和银发在 32px 下会合并，需要窗口内确认长者读感。
- `npc_kai_map_idle` 的乐手道具较弱，后续可通过站位或 UI 名牌补足身份。
- `npc_bram_map_idle` 的木箱占比偏高，若后续需要行走动画，可改成腰侧小农具。
- 交互标记当前适合静态 UI 和地图提示，接入 Godot 后再判断是否需要高亮、描边或呼吸动画。
