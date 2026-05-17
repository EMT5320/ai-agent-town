---
status: active
owner_lane: asset-pipeline
last_verified: 2026-05-17
startup_load: on-demand
source_of_truth: false
scope: prompt_ready backlog batches and export artifacts
---

# 资产批次导出目录

本目录用于沉淀 `status=prompt_ready` 的可生产批次与人工筛选清单。

- `prompt_ready_backlog_batches.json`：批次计划源文件，定义批次、用途、prompt 锚点、Godot 接入目标前缀。
- `prompt_ready_export.json`：机器可读导出，适合脚本流水线消费。
- `prompt_ready_export.md`：导出主表，按批次展示待生产与待筛选条目。
- `prompt_ready_review_checklist.md`：`prompt_ready_export.md` 的兼容别名，供旧流程继续读取。

更新命令：

```powershell
python scripts/export_prompt_ready_assets.py
```

更新前建议先运行：

```powershell
npm.cmd run asset:check
```
