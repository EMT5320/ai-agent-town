# 游戏客户端开发环境入门

> 本文面向第一次接触 Godot / 游戏客户端开发的本机环境。当前项目使用 Godot 标准版 + GDScript，不使用 C# / Mono 版。

## 已准备环境

当前机器已具备：

| 工具 | 当前用途 |
| --- | --- |
| Python 3.12 | 后端 Agent Server、检查脚本 |
| Node.js / npm | 统一启动和检查入口 |
| Git | 版本管理 |
| Godot 4.6.2 标准版 | 游戏客户端编辑器和运行环境 |

Godot 当前安装路径：

```text
D:\Work\tools\godot\4.6.2\Godot_v4.6.2-stable_win64.exe
```

## 必须知道的最少概念

### 1. Godot 是游戏编辑器和运行器

Godot 类似一个轻量游戏开发环境。我们会用它来做：

- 游戏窗口。
- 地图显示。
- 玩家输入。
- NPC 显示。
- 对话框。
- 事件 UI。

### 2. `.tscn` 是场景文件

场景可以理解为游戏里的一个画面或一组节点。

当前入口场景：

```text
clients/godot/scenes/main.tscn
```

### 3. `.gd` 是 GDScript 脚本

GDScript 是 Godot 自带脚本语言，语法接近 Python。

当前关键脚本：

```text
clients/godot/scripts/main.gd
clients/godot/scripts/api_client.gd
clients/godot/scripts/world_sync.gd
```

### 4. Python 后端仍是权威世界

Godot 客户端只负责表现和交互。真正的世界状态仍在 Python 后端：

```text
GET  /api/world/state
POST /api/player/action
```

## 常用命令

### 检查本机 Godot 环境

```powershell
npm.cmd run client:env
```

该命令会用 headless 模式打开 Godot 项目，检查时生成的 Godot 用户数据会放在仓库 `.run/` 目录下，已被 Git 忽略。

### 启动后端

```powershell
npm.cmd run start
```

默认地址：

```text
http://127.0.0.1:8787
```

### 打开 Godot 项目

另开一个 PowerShell：

```powershell
npm.cmd run client:open
```

如果只想检查打开命令会使用哪个 Godot 和项目目录：

```powershell
npm.cmd run client:open:check
```

也可以手动打开：

```text
D:\Work\tools\godot\4.6.2\Godot_v4.6.2-stable_win64.exe
```

然后选择：

```text
clients/godot/project.godot
```

## 第一次运行流程

1. 在仓库根目录执行：

   ```powershell
   npm.cmd run start
   ```

2. 另开一个 PowerShell，执行：

   ```powershell
   npm.cmd run client:open
   ```

3. Godot 打开后，运行主场景。

4. 看到文本面板后，确认里面有：

   - 玩家位置。
   - 世界时间。
   - 地点列表。
   - NPC 列表。
   - 最近事件。

5. 点击“向奥蕾娅打招呼”，确认后端会返回 NPC 回复。

## 当前项目阶段

当前 Godot 客户端仍是文本面板骨架，用于验证 API 契约。下一步会逐步替换成：

- 基础地图。
- 玩家角色节点。
- NPC 节点。
- 对话面板。
- 事件卡片。
- 调试信息入口。

## 常见问题

### 打开 Godot 后看不到状态

先确认后端已经启动：

```powershell
npm.cmd run start
```

浏览器访问：

```text
http://127.0.0.1:8787/api/world/state
```

如果能看到 JSON，说明后端正常。

### PowerShell 不认识 Godot 命令

当前没有把 Godot 加入系统 PATH。请使用：

```powershell
npm.cmd run client:open
```

或直接打开：

```text
D:\Work\tools\godot\4.6.2\Godot_v4.6.2-stable_win64.exe
```

### `client:open` 出现 PowerShell 乱码或引号解析错误

旧脚本里有中文字符串时，Windows PowerShell 5.1 可能按本机代码页读取文件，导致脚本解析失败。当前脚本已改成 ASCII 安全写法。遇到类似问题时先执行：

```powershell
npm.cmd run client:open:check
```

### Godot 生成 `.godot/` 目录

这是 Godot 的本地导入缓存，已经在 `.gitignore` 里忽略，不需要提交。

### 检查命令生成 `.run/` 目录

`npm.cmd run client:env` 会生成临时运行数据，已经在 `.gitignore` 里忽略，不需要提交。
