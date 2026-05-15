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
   - NPC 选择可用。
   - `talk` 提交可用。
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

- 把当前列表式地点/NPC 交互替换为基础地图表现。
- 将 6 个首发 NPC 和 3 个首发地点映射到可视化节点。
- 增加玩家移动输入。
- 增加 NPC 交互区域和对话面板。

更完整的新手环境说明见：

```text
docs/game_client_environment.md
```
