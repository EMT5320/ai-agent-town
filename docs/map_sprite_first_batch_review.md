# 第一批地图小人 64x64 / 32x32 对比检查

日期：2026-05-16  
范围：仅 `player_farmer_map_idle`、`npc_mira_map_idle`、`npc_tomas_map_idle` 三张静态 `idle_front` 地图小人。

## 输出文件

| 资产 ID | source | processed | Godot 同步 | Manifest 状态 |
| --- | --- | --- | --- | --- |
| `player_farmer_map_idle` | `assets/source/sprites/player_farmer_map_idle.png` | `assets/processed/sprites/player_farmer_map_idle.png` | `clients/godot/assets/sprites/player_farmer_map_idle.png` | `pending_review` |
| `npc_mira_map_idle` | `assets/source/sprites/npc_mira_map_idle.png` | `assets/processed/sprites/npc_mira_map_idle.png` | `clients/godot/assets/sprites/npc_mira_map_idle.png` | `pending_review` |
| `npc_tomas_map_idle` | `assets/source/sprites/npc_tomas_map_idle.png` | `assets/processed/sprites/npc_tomas_map_idle.png` | `clients/godot/assets/sprites/npc_tomas_map_idle.png` | `pending_review` |

对比图：`assets/processed/sprites/map_idle_first_batch_64_32_check.png`

## 处理方式

1. 使用三份 `assets/manifests/prompts/*_map_idle.txt` 生成方图草稿。
2. 以纯 `#ff00ff` / 接近 magenta 的平底进行 chroma-key 去背。
3. 裁切可见像素并缩放到 `64x64` RGBA PNG，角色主体控制在约 `48x56` 安全框内，底部保留约 4px 落脚余量。
4. 同步到 `assets/source/sprites/`、`assets/processed/sprites/`、`clients/godot/assets/sprites/`。
5. `asset_manifest.json` 只登记为 `pending_review`，本轮没有提升为 `source_selected`。

## 单图检查结论

| 资产 ID | 头身 | 轮廓 | 身份继承 | 64x64 / 32x32 可读性 | 结论 |
| --- | --- | --- | --- | --- | --- |
| `player_farmer_map_idle` | 满足。大头 Q 版比例明显，角色可见尺寸约 `31x56`，头部占比接近目标区间。 | 满足。深色外轮廓清楚，内部线条保留发型、上衣、围裙和挎包。 | 满足。叶绿色与米白主色、种子挎包、小星灯挂饰保留；和米娅的橙色围裙区分明显。 | 64px 身份清晰；32px 仍可读出绿色玩家农场主，星灯细节会弱化。 | 通过本轮试生成，继续保持 `pending_review`。 |
| `npc_mira_map_idle` | 满足。更接近 2 头身的 Q 版形体，角色可见尺寸约 `37x56`。 | 满足。头发、围裙、账本块面清楚，线宽适合 64px。 | 满足。栗色头发、暖橙围裙、账本 / 种子店主读感保留；和玩家绿色主色区分明显。 | 64px 读感强；32px 橙色围裙和栗色头发可读，侧辫与账本细节会弱化。 | 通过本轮试生成，继续保持 `pending_review`。 |
| `npc_tomas_map_idle` | 满足。男性 Q 版比例稳定，角色可见尺寸约 `39x56`，头身在目标范围内。 | 满足。深色头发、蓝色工作衫、腰带工具形成明确剪影。 | 满足。深蓝工作衫、皮革工具腰带、木槌 / 尺子读感保留，未出现盔甲化或贵族化。 | 64px 木匠身份清楚；32px 仍能读出蓝衣男性木匠，工具细节简化为棕色块面。 | 通过本轮试生成，继续保持 `pending_review`。 |

## 后续人工评审关注点

- `player_farmer_map_idle` 的星灯挂饰在 32px 只作为黄色亮点出现，若后续要强化主角标志，可在二轮微调中加大挂饰或提高对比度。
- `npc_mira_map_idle` 的侧辫在 64px 可见，32px 主要依赖橙色围裙和栗色头发区分身份。
- `npc_tomas_map_idle` 的工具在 32px 会压缩为小色块，当前更适合作为静态 idle 首版；后续行走帧可让工具挂在腰带侧面保持稳定读感。
