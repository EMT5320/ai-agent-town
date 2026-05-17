"""导出 prompt_ready 资产批次清单，供生图执行与人工筛选使用。"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "assets" / "manifests" / "asset_manifest.json"
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "asset_batches"
EXPORT_JSON_PATH = "prompt_ready_export.json"
EXPORT_MARKDOWN_PATH = "prompt_ready_export.md"


def load_manifest() -> list[dict[str, Any]]:
    """加载 manifest 并返回对象数组。"""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(manifest, list):
        raise RuntimeError("asset_manifest.json 顶层必须是数组")
    return manifest


def parse_prompt_ref(prompt_ref: str) -> tuple[str, str]:
    """解析 prompt 文档路径与锚点。"""
    base_ref, _, anchor = prompt_ref.partition("#")
    return base_ref, anchor


def collect_prompt_ready_batches(manifest: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """收集 prompt_ready 条目并按批次分组。"""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for entry in manifest:
        if entry.get("status") != "prompt_ready":
            continue
        asset_id = str(entry.get("id", "")).strip()
        prompt_batch_id = str(entry.get("promptBatchId", "")).strip()
        prompt_ref = str(entry.get("fullPromptRef", "")).strip()
        _, anchor = parse_prompt_ref(prompt_ref)
        usage = str(entry.get("usage", "")).strip()
        godot_target_path = str(entry.get("godotTargetPath", "")).strip()
        godot_target_slot = str(entry.get("godotTargetSlot", "")).strip()

        # 导出时做一次轻量防呆，避免写出不可执行的空清单。
        if not asset_id or not prompt_batch_id or not prompt_ref or not anchor:
            raise RuntimeError(f"{asset_id or '<unknown>'} 缺少批次或 prompt 锚点信息")
        if not usage or not godot_target_path or not godot_target_slot:
            raise RuntimeError(f"{asset_id} 缺少 usage 或 Godot 接入目标")

        grouped[prompt_batch_id].append(
            {
                "id": asset_id,
                "type": entry.get("type"),
                "usage": usage,
                "path": entry.get("path"),
                "promptRef": prompt_ref,
                "promptAnchor": anchor,
                "promptSummary": entry.get("promptSummary"),
                "godotTargetPath": godot_target_path,
                "godotTargetSlot": godot_target_slot,
                "reviewNotes": entry.get("reviewNotes"),
            }
        )

    return dict(sorted(grouped.items(), key=lambda item: item[0]))


def write_export_json(output_dir: Path, batches: dict[str, list[dict[str, Any]]]) -> Path:
    """写出机器可读的导出清单。"""
    output_path = output_dir / EXPORT_JSON_PATH
    payload = {
        "generatedAt": date.today().isoformat(),
        "sourceManifest": str(MANIFEST_PATH.relative_to(ROOT)).replace("\\", "/"),
        "batchCount": len(batches),
        "assetCount": sum(len(items) for items in batches.values()),
        "batches": [
            {
                "batchId": batch_id,
                "assetCount": len(items),
                "assets": items,
            }
            for batch_id, items in batches.items()
        ],
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path


def build_review_markdown_lines(batches: dict[str, list[dict[str, Any]]]) -> list[str]:
    """构建人工筛选用 Markdown 清单内容。"""
    lines: list[str] = []
    lines.append("---")
    lines.append("status: active")
    lines.append("owner_lane: asset-pipeline")
    lines.append(f"last_verified: {date.today().isoformat()}")
    lines.append("startup_load: on-demand")
    lines.append("source_of_truth: false")
    lines.append("scope: prompt_ready batch execution and manual review checklist")
    lines.append("---")
    lines.append("")
    lines.append("# prompt_ready 资产批次导出清单")
    lines.append("")
    lines.append(f"> 导出日期：{date.today().isoformat()}。")
    lines.append("> 说明：本清单只覆盖 `status=prompt_ready` 的 backlog，未声明任何已生成结果。")
    lines.append("")
    lines.append("## 使用步骤")
    lines.append("")
    lines.append("1. 先按 `batchId` 逐批次执行生图。")
    lines.append("2. 每张图通过人工筛选后再更新 manifest 状态。")
    lines.append("3. 仅在源图真实存在且评审通过时写入 `processedPath` 与 `godotPath`。")
    lines.append("")

    for batch_id, items in batches.items():
        lines.append(f"## {batch_id}")
        lines.append("")
        lines.append("| 资产ID | 用途 | Prompt 锚点 | Godot 目标路径 | Godot 接入槽位 | 人工筛选 |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for item in items:
            lines.append(
                f"| `{item['id']}` | `{item['usage']}` | `{item['promptRef']}` | "
                f"`{item['godotTargetPath']}` | `{item['godotTargetSlot']}` | ☐ 待筛选 |"
            )
        lines.append("")
        lines.append("### 批次内执行检查")
        lines.append("")
        lines.append("- [ ] 角色身份和风格与 `neutral/reference` 一致。")
        lines.append("- [ ] 64x64 / 32x32 可读性检查（图标与 UI 组件必做）。")
        lines.append("- [ ] 无水印、无不可控文字、透明背景可用。")
        lines.append("- [ ] 通过后再推进 Godot 接入路径与槽位。")
        lines.append("")

    return lines


def write_review_markdown(output_dir: Path, batches: dict[str, list[dict[str, Any]]]) -> Path:
    """写出人工筛选用 Markdown 清单。"""
    output_path = output_dir / EXPORT_MARKDOWN_PATH
    markdown_text = "\n".join(build_review_markdown_lines(batches)).rstrip() + "\n"
    output_path.write_text(markdown_text, encoding="utf-8")
    return output_path


def format_log_path(path: Path) -> str:
    """格式化导出日志路径；仓库外目录直接显示绝对路径。"""
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def main() -> None:
    """程序入口。"""
    parser = argparse.ArgumentParser(description="导出 prompt_ready 资产批次清单")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="导出目录，默认 docs/asset_batches",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest()
    batches = collect_prompt_ready_batches(manifest)
    if not batches:
        raise RuntimeError("当前 manifest 没有 prompt_ready 条目，未生成导出清单")

    json_path = write_export_json(output_dir, batches)
    markdown_path = write_review_markdown(output_dir, batches)
    print(
        "[prompt-ready-export] ok "
        f"batches={len(batches)} assets={sum(len(items) for items in batches.values())} "
        f"json={format_log_path(json_path)} md={format_log_path(markdown_path)}"
    )


if __name__ == "__main__":
    main()
