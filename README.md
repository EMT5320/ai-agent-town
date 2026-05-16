# AI Agent 小镇实验室

> 用游戏小镇作为可视化沙盒，观察多个 AI Agent 的决策、协作、冲突、记忆和工具调用过程。

## 2026-05-14 方向更新：Agent Valley

项目当前已从“多 Agent 观察台”升级为 `Agent Valley`：一个由 LLM NPC 驱动的生活模拟 RPG 垂直切片。

最新推进口径以 [`docs/project_vision.md`](docs/project_vision.md)、[`docs/implementation_plan.md`](docs/implementation_plan.md) 和 [`docs/open_questions.md`](docs/open_questions.md) 为准：

- 主游戏客户端确定使用 Godot。
- 首版聚焦 6 个 NPC、3 个地点、1 个完整游戏日和 1 个小镇事件。
- 玩家身份是新搬来的农场主，Debug / 研究控制台保留研究院视角。
- 首版直接接入 LLM 测试，DeepSeek V4 Flash 作为低成本优先模型，规则 Provider 作为 fallback。
- 视觉风格采用温暖绘本风，像素风暂作地图小人占位或后续专项方向。
- 当前项目与论文无关，运行数据主要服务于调试、回放和作品集讲解。

## 早期项目定位（观察台阶段）

这是一个偏 AI Agent 实验的平台。小镇地图和 NPC 是外层表现，核心目标是让主人能清楚观察 Agent 的运行链路：输入状态、生成计划、自由交流、选择行动、影响世界、写入记忆。

玩家默认是旁观者，主要观察小镇如何自行运转；同时保留开发者通道，用于必要时注入事件、调整状态、触发实验场景。

## 核心观察链路

```text
世界状态 -> Agent 上下文 -> 云端模型/规则决策 -> 对话或行动 -> 世界状态变化 -> 记忆更新 -> Debug 日志/回放
```

## 早期观察台设计决策（历史口径）

- 首版 Agent 数量定为 10 个，形成更接近真实小镇的社交网络。
- 小镇人口支持动态变化：孩子出生、老人去世、新居民迁入、居民迁出。
- 动态人口事件会成为关键观察点，用于观察其他 NPC 的情绪、关系和行为反应。
- 云端 API 优先，本地模型作为备选 Provider。
- 云端 API 初步优先考虑 DeepSeek，原因是成本优势、长上下文潜力，以及角色扮演类指令适配度高。
- Agent 输出不强制全部走工具调用，NPC 之间允许自然对话交流。
- 玩家是旁观者；开发者通道保留世界干预能力。
- Debug 面板展示完整上下文、完整模型输入、完整模型输出、解析结果和执行结果。

## MVP 范围

- 10 个初始 NPC Agent。
- 5 个地点：住宅区、广场、商店、诊所、酒馆。
- 每个 Agent 有角色卡、家庭关系、今日目标、短期记忆、关系数据、可用行动。
- 时间按回合推进，每回合部分 Agent 根据状态做决策，避免 10 个 Agent 同时请求模型导致成本过高。
- 后端优先实现完整 Agent Runtime：世界状态、调度器、Provider、记忆、事件、日志和实验记录。
- 支持 `RuleBasedProvider`，保证无模型时也能跑通后端闭环。
- 优先实现 `CloudApiProvider`，本地模型 Provider 保留接口。
- 前端定位为观察台和开发者控制台，展示小镇状态、Agent 状态、对话记录、行动记录、事件日志、人口变化和每日总结。
- Debug 面板完整展示 Provider 输入/输出，便于观察 Agent 行为。

## 人口动态设计

### 1. 人口事件类型

- 出生：家庭新增孩子，亲属关系自动更新。
- 死亡：老人或高风险角色离世，触发哀悼、继承、关系重排。
- 迁入：新居民带着背景、目标和关系空白进入小镇。
- 迁出：居民因冲突、经济压力或目标变化离开小镇。
- 成长：孩子逐渐长大，性格和目标发生变化。

### 2. 观察重点

- 亲友是否主动安慰相关 NPC。
- 敌对关系是否因重大事件缓和或恶化。
- 孩子出生是否改变家庭成员的工作和社交选择。
- 老人去世是否影响社区记忆、财产和长期关系。
- 新居民是否能被小镇接纳。

## Agent 数据草案

- 基础信息：姓名、年龄、生命阶段、职业、当前位置、性格。
- 家庭信息：父母、配偶、子女、同居者。
- 目标系统：今日目标、长期目标、当前意图。
- 状态数值：精力、心情、金钱、健康、社交需求、压力。
- 记忆系统：最近事件、重要人物、承诺、冲突、人生大事。
- 关系系统：好感、信任、矛盾值、亲密度、亲属关系。
- 决策记录：输入上下文、模型输出、解析动作、执行结果。

## 行动与对话系统草案

NPC 输出可以是自然对话、行动意图或二者组合。系统会尝试把输出解析为可执行事件，同时保留原始文本。

### 行动类型

- `moveTo(location)`：移动到目标地点。
- `talkTo(npc, topic, message)`：和指定 NPC 交谈，保留自然语言内容。
- `work(job)`：执行职业相关工作并影响金钱/精力。
- `buy(item)`：在商店购买物品。
- `rest()`：恢复精力并推进时间。
- `careFor(npc)`：照顾孩子、老人或生病居民。
- `attendEvent(event)`：参加葬礼、庆祝会、集会等小镇事件。
- `remember(event)`：写入短期或重要记忆。
- `planDay()`：生成当天行动计划。

## Provider 抽象

```text
AgentProvider
├── CloudApiProvider        # 优先路线，初步考虑 DeepSeek / OpenAI-compatible endpoint
├── RuleBasedProvider       # 规则决策，用于无模型开发、离线测试和成本控制
└── LocalModelProvider      # 备选路线，例如 Ollama / llama.cpp / OpenAI-compatible local server
```

### Provider 输入草案

- 当前 Agent 角色卡。
- 当前世界状态。
- 当前地点和附近 NPC。
- Agent 近期记忆和关键长期记忆。
- 家庭与关系摘要。
- 最近发生的人口事件或重大事件。
- 可用行动 schema。
- 上一轮行动结果。

### Provider 输出草案

Agent 输出不强制 JSON。系统支持以下几类结果：

1. 自然语言对话：直接作为 NPC 发言进入事件日志。
2. 结构化 JSON：直接执行对应行动。
3. 混合输出：保留原始文本，并尝试抽取行动意图。

```json
{
  "speech": "Mira，我听说你家添了孩子，今晚需要我帮忙看店吗？",
  "action": "talkTo",
  "args": { "npc": "Mira", "topic": "new_child", "message": "今晚需要我帮忙看店吗？" },
  "memory_to_save": "Mira 家新添了孩子，我主动提出帮忙。"
}
```

## 开发者通道

开发者通道用于实验，不作为普通玩家玩法核心。

- 注入事件：出生、死亡、失业、冲突、节日、灾害。
- 修改状态：调整 NPC 心情、健康、金钱、关系。
- 指定观察目标：重点追踪某个 NPC、家庭或事件链。
- 暂停/单步推进：方便查看每一轮 Agent 输入输出。
- 导出实验记录：保存完整 prompt、输出、事件和状态快照。

## Debug 面板构思

- 完整 Prompt / messages。
- 完整模型原始输出。
- 解析后的行动或对话。
- 工具/行动执行结果。
- 本轮状态差异。
- 写入的记忆。
- Token / 成本 / 延迟统计。
- 错误与重试记录。

## 首版技术路线候选

项目从第一版开始按完整后端 Agent 系统设计，前端负责观察、调试和必要干预。

### 1. 后端优先

- 建立 Agent Runtime，负责时间推进、Agent 调度、Provider 调用、行动解析、世界状态更新和日志落盘。
- 建立 World State 层，统一管理 NPC、地点、家庭、关系、人口事件、记忆和每日摘要。
- 建立 Event Store，保存完整事件流，便于回放、调试和后续实验分析。
- 建立 Provider 层，优先适配云端 OpenAI-compatible API，DeepSeek 作为优先候选；本地模型作为后续备选。
- 建立 Developer API，支持暂停、单步推进、注入事件、修改状态、导出实验记录。

### 2. 前端观察台

- 前端作为 Agent 运行观察台，不承担核心模拟逻辑。
- 展示小镇地图、NPC 状态、对话、行动、事件流、人口变化、Debug 信息和成本统计。
- 支持开发者通道操作：暂停、继续、单步、注入事件、选择观察对象。

### 3. 推荐技术形态

- 后端：Python 优先，当前采用标准库 HTTP 适配器承载 REST / SSE，核心 Runtime 与 API 层解耦，后续可平滑切到 FastAPI。
- 存储：开发期可先用 SQLite，事件流和状态快照都能落盘。
- 前端：轻量 Web 控制台，后续再考虑更强的小镇可视化。
- 通信：REST API 起步，实时日志可用 Server-Sent Events 或 WebSocket。

### 4. 接入策略

- 先实现 `RuleBasedProvider`，验证后端 Agent 循环和事件流。
- 随后实现 `CloudApiProvider`，优先适配 OpenAI-compatible API 形态。
- DeepSeek 具体模型名、上下文长度、角色扮演指令和 API 参数在接入前按官方文档核查。
- 本地模型 Provider 保留接口，等云端链路稳定后再接 Ollama / llama.cpp / 本地 OpenAI-compatible server。

## 建议后端模块划分

```text
backend/
├── runtime/          # Agent 调度、时间推进、回合循环
├── world/            # NPC、地点、家庭、关系、人口事件、世界状态
├── providers/        # RuleBasedProvider、CloudApiProvider、LocalModelProvider
├── memory/           # 短期记忆、长期记忆、重要事件沉淀
├── events/           # 事件流、状态快照、回放数据
├── developer/        # 开发者通道 API：注入事件、单步、状态修改
└── api/              # HTTP/SSE/WebSocket 接口
```

## 当前待细化问题

1. 10 个初始 NPC 的职业、家庭结构和年龄分布。
2. 人口动态在 MVP 里是真实自动触发，还是先通过开发者通道注入。
3. 云端 API 密钥和模型配置放在前端本地配置，还是起一个轻量后端代理。
4. Agent 每回合调用模型的频率和成本控制策略。
5. 首版 UI 是偏地图可视化，还是偏调试仪表盘。

## 下一步

先确定 10 个初始 NPC、世界规则和后端技术栈，再搭建 Agent Runtime 骨架。



## 第一版已落地模块

### 后端 Agent 系统

- `backend/app/main.py`：Python HTTP 服务，提供静态前端、REST API 和 SSE 事件流。
- `backend/app/runtime/`：Agent 调度、回合推进、行动解析、行动执行和人口事件触发。
- `backend/app/world/`：5 个地点、10 个初始 NPC、家庭关系、关系图谱和公开状态视图。
- `backend/app/providers/`：`RuleBasedProvider` 可离线跑通闭环，`CloudApiProvider` 预留 OpenAI-compatible 云端接入。
- `backend/app/memory/`：短期记忆写入和摘要。
- `backend/app/events/`：事件流、快照和 SSE 推送。
- `backend/app/developer/`：暂停、继续、聚焦、注入事件、调整 Agent 状态。

### 前端观察台

- `frontend/index.html`：小镇观察台页面。
- `frontend/style.css`：暗色玻璃质感界面、小镇地图、卡片面板和响应式布局。
- `frontend/app.js`：调用后端状态、单步推进、自动运行、开发者事件注入、Debug 展示。

### 本地运行

```powershell
cd D:\Work\fun-projects-lab\projects\ai-agent-town-lab
npm start
```

打开：`http://localhost:8787`

### 验证

```powershell
npm run check
```

验证内容包括：后端入口语法检查、前端脚本语法检查、核心 Runtime smoke test。

### 云端 Provider 配置

第一版默认使用 `RuleBasedProvider`，无需 API Key。若要尝试 OpenAI-compatible 云端 Provider，可设置：

```powershell
$env:AGENT_TOWN_PROVIDER = 'cloud'
$env:DEEPSEEK_API_KEY = '<your-key>'
$env:AGENT_TOWN_BASE_URL = 'https://api.deepseek.com'
$env:AGENT_TOWN_MODEL = 'deepseek-chat'
npm start
```

具体模型名和参数在正式接入前需要按官方文档再次核查。

## 2026-04-26 架构调整：后端转向 Python

为了降低后续 Agent 系统维护成本，第一版后端已经从纯 JS Runtime 调整为 Python 分层架构。前端仍然复用 `frontend/` 观察台，API 形状保持兼容。

### 当前目录结构

```text
backend/
└── app/
    ├── main.py                  # Python HTTP/SSE 入口
    ├── runtime/                 # Agent Runtime、调度、行动解析和执行
    ├── world/                   # 世界状态、地点、NPC、关系图谱
    ├── providers/               # RuleBasedProvider / CloudApiProvider
    ├── memory/                  # 记忆写入和摘要
    ├── events/                  # EventStore 与 SSE 事件队列
    └── developer/               # 开发者通道命令
legacy_backend_js/               # 旧 JS 后端归档，只作参考
frontend/                        # 观察台前端
scripts/                         # 启动、检查、smoke test
```

### 为什么当前先用 Python 标准库 HTTP

- 核心 Agent Runtime 已经是 Python，后续接 SQLite、向量记忆、实验分析、异步任务会更自然。
- HTTP 层保持轻量，当前无需安装依赖即可运行。
- Runtime、Provider、World、EventStore 已和 HTTP 适配器解耦，后续迁到 FastAPI 时主要替换 `backend/app/main.py` 的 API 外壳。

### 启动方式

```powershell
cd D:\Work\fun-projects-lab\projects\ai-agent-town-lab
npm start
```

等价于：

```powershell
python scripts/start_server.py
```

### 检查方式

```powershell
npm run check
```

检查内容：Python 后端编译、前端 JS 语法检查、Python Runtime smoke test。

## 模型配置文件

本机实际模型配置位于：

```text
config/models.json
```

`config/models.json` 已加入 gitignore，首次使用时可从 `config/models.example.json` 复制一份。后续可以在 `models.json` 里配置不同 NPC 和不同功能使用的模型。

### 关键字段

```json
{
  "activeProvider": "rule",
  "defaultProfile": "default_deepseek",
  "profiles": {
    "default_deepseek": {
      "provider": "cloud",
      "baseUrl": "https://api.deepseek.com",
      "apiKeyEnv": "DEEPSEEK_API_KEY",
      "model": "deepseek-chat",
      "temperature": 0.8,
      "maxTokens": 900,
      "timeoutSeconds": 60
    }
  },
  "npcProfiles": {
    "kai": "creative_dialogue"
  },
  "featureProfiles": {
    "agent_decision": "default_deepseek",
    "daily_summary": "cheap_daily"
  },
  "fallbackProfile": "rule_fallback"
}
```

### 启用云端模型

把 `config/models.json` 里的：

```json
"activeProvider": "cloud"
```

然后在 PowerShell 设置密钥：

```powershell
$env:DEEPSEEK_API_KEY = "你的 API Key"
npm start
```

### Profile 选择优先级

```text
npcProfiles[agentId] > featureProfiles[feature] > defaultProfile > fallbackProfile
```

Debug 面板会显示本轮实际使用的 `profile`、`model`、`baseUrl`、`temperature`、`maxTokens` 和 `apiKeyConfigured`，不会显示真实 API Key。

也可以通过 `GET /api/model-config` 查看当前可公开展示的配置。

开发期推荐先跑结构检查：

```powershell
npm.cmd run model:check
```

启动服务后，迁移期 Web 观察台右侧的 **LLM 配置** 卡片会展示当前运行模式、profiles、NPC / feature 路由、key 是否已配置和校验结果。修改 `config/models.json` 或本地 overlay 后，可点击“重载配置”热重载；点击“对话 Smoke”会触发一次玩家对话，用于快速确认真实模型输出或 fallback 情况。
