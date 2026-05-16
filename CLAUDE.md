@AGENTS.md

## Claude Code 补充规则

- 项目共享规则以 `AGENTS.md` 为主；本文件只放 Claude Code 适配说明。
- 大任务开始前，先说明将读取哪些项目文档，再进入修改。
- 不要把所有 `docs/` 文档一次性读入上下文，按 `AGENTS.md` 的任务线路由逐步加载。
- `.claude/rules/` 已放置路径规则；触发对应路径时再按规则加载 lane 文档，避免无条件加载过多内容。
