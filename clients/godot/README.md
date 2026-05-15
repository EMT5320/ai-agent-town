# Agent Valley Godot 客户端

这是 `Agent Valley` 的首版 Godot 游戏客户端骨架。当前目标是验证 Godot 能读取 Python Agent Server 的权威世界状态，并在游戏窗口中显示玩家、地点、NPC 和最近事件。

## 当前能力

- 主场景：`scenes/main.tscn`
- API 客户端：`scripts/api_client.gd`
- 资产注册：`scripts/asset_registry.gd`
- 世界状态缓存：`scripts/world_sync.gd`
- 运行后读取：`GET /api/world/state`
- 可触发一次测试对话：`POST /api/player/action`
- 已能加载 3 张地点背景和玩家 + 6 个首发 NPC 的 `neutral` 半身立绘
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

   如果需要进入编辑器：

   ```powershell
   npm.cmd run client:open
   ```

   也可以手动用 Godot 4.x 打开：

   ```text
   clients/godot/project.godot
   ```

4. 确认窗口中能看到：

   - 玩家位置。
   - 世界时间。
   - 农场、广场、酒馆背景切换。
   - 玩家与首发 NPC 的 `neutral` 半身立绘。
   - 最近事件。

## 下一步

- 把当前列表式地点/NPC 交互替换为基础地图表现。
- 将 6 个首发 NPC 和 3 个首发地点映射到可视化节点。
- 增加玩家移动输入。
- 增加 NPC 交互区域和对话面板。

更完整的新手环境说明见：

```text
docs/game_client_environment.md
```
