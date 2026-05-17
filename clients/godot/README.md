# Agent Valley Godot 客户端

这是 `Agent Valley` 的首版 Godot 游戏客户端骨架。当前目标是验证 Godot 能读取 Python Agent Server 的权威世界状态，并在游戏窗口中显示玩家、地点、NPC、进行中事件和 VN 结果回执。

## 当前能力

- 主场景：`scenes/main.tscn`
- API 客户端：`scripts/api_client.gd`
- 资产注册：`scripts/asset_registry.gd`
- 世界状态缓存：`scripts/world_sync.gd`
- 运行后读取：`GET /api/world/state`
- 玩家动作统一通过：`POST /api/player/action`
- 已能加载 3 张地点背景和玩家 + 6 个首发 NPC 的 `neutral` 半身立绘
- 已能展示 `activeEvents` 中的星灯祭供应短缺事件，并通过 `inspect` / `attend_event` 展示选择结果
- 已支持地图上下文交互：靠近锚点 / 交互体 / 居民 / 事件后显示候选动作，`E`/`Space` 执行，`Tab`/`Q` 切换
- 可通过一条命令直接运行当前 P0 游戏窗口

## 本地启动

1. 在仓库根目录检查 Godot 环境：

   ```powershell
   npm.cmd run client:env
   ```

2. 启动后端：

   ```powershell
   npm.cmd run start
   ```

3. 直接运行游戏窗口：

   ```powershell
   npm.cmd run client:run
   ```

   该命令会先执行 Godot 资源导入，再打开游戏窗口。

   如果需要进入编辑器：

   ```powershell
   npm.cmd run client:open
   ```

   也可以手动用 Godot 4.x 打开：

   ```text
   clients/godot/project.godot
   ```

## 人工验收步骤（本轮）

> 以下内容是人工验收步骤与检查项，需在真实窗口中逐项确认。

1. 在仓库根目录启动后端：

   ```powershell
   npm.cmd run start
   ```

2. 另开一个 PowerShell 运行游戏窗口：

   ```powershell
   npm.cmd run client:run
   ```

3. 在游戏窗口内人工检查：

   - 地点切换与背景切换可用。
   - WASD 与空地点击移动可用，靠近目标后能看到上下文候选动作。
   - `E`/`Space` 可提交当前候选动作，`Tab`/`Q` 可切换候选。
   - 侧栏“场景行动”只作为调试兜底，地图上下文交互是主路径。
   - 事件区可看到 `activeEvents` 中的“星灯祭供应短缺”。

4. 点击“查看事件”后人工检查：

   - 能看到事件标题。
   - 能看到事件摘要。
   - 能看到 `choices` 列表。

5. 点击任一选择后人工检查：

   - 能看到 NPC 台词。
   - 能看到关系变化。
   - 能看到记忆写入结果。
   - 能看到夜间反思摘要。

## 下一步

- 在真实窗口复验三场景移动稳定性、地图上下文候选、快捷键执行和行动反馈。
- 将后端 `npcSchedules` / `lifeActionPlan` 做成轻量日程可视化。
- 接入背包物品选择，让送礼和事件消耗从固定兜底走向玩家选择。
- 等行动反馈图标和生活 UI 组件通过人工筛选后，再接入 `AssetRegistry`。

更完整的新手环境说明见：

```text
docs/game_client_environment.md
```
