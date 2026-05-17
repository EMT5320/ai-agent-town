"""校验美术资产 manifest 与 prompt 引用。"""

from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "assets" / "manifests" / "asset_manifest.json"
PLAN_PATH = ROOT / "assets" / "manifests" / "initial_asset_plan.json"

REQUIRED_FIELDS = {
    "id",
    "path",
    "type",
    "ownerId",
    "usage",
    "variantGroup",
    "expression",
    "style",
    "promptSummary",
    "fullPromptRef",
    "sourceTool",
    "createdAt",
    "sourceSize",
    "processedPath",
    "godotPath",
    "licenseNote",
    "status",
    "reviewNotes",
}

ALLOWED_STATUSES = {
    "style_anchor_candidate",
    "prompt_ready",
    "pending_review",
    "source_selected",
}


def load_json(path: Path) -> Any:
    """读取 JSON 文件并附带路径上下文。"""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"JSON 解析失败：{path}: {exc}") from exc


def read_png_size(path: Path) -> tuple[int, int]:
    """读取 PNG IHDR 尺寸，避免额外图像依赖。"""
    with path.open("rb") as file:
        header = file.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise RuntimeError(f"资产不是有效 PNG：{path}")
    return struct.unpack(">II", header[16:24])


def parse_size(value: str) -> tuple[int, int]:
    """解析 manifest 中的 1024x1536 尺寸字段。"""
    if "x" not in value:
        raise RuntimeError(f"sourceSize 需使用 WIDTHxHEIGHT 格式：{value}")
    width, height = value.lower().split("x", 1)
    return int(width), int(height)


def validate_prompt_ref(asset_id: str, prompt_ref: str, status: str) -> None:
    """校验 prompt 引用路径，支持 Markdown 锚点计划引用。"""
    base_ref, _, anchor = prompt_ref.partition("#")
    prompt_path = ROOT / base_ref
    if not prompt_path.exists():
        raise RuntimeError(f"{asset_id} 缺少 prompt 文件：{prompt_path}")

    if anchor:
        markdown_text = prompt_path.read_text(encoding="utf-8")
        anchor_patterns = (
            f'id="{anchor}"',
            f"id='{anchor}'",
        )
        if not any(pattern in markdown_text for pattern in anchor_patterns):
            raise RuntimeError(f"{asset_id} 的 prompt 锚点不存在：{prompt_ref}")

    if status == "prompt_ready" and not anchor:
        raise RuntimeError(f"{asset_id} 为 prompt_ready 时必须引用文档锚点：{prompt_ref}")


def validate_manifest() -> None:
    """校验已筛选资产的路径、字段和尺寸。"""
    manifest = load_json(MANIFEST_PATH)
    if not isinstance(manifest, list):
        raise RuntimeError("asset_manifest.json 顶层必须是数组")

    seen_ids: set[str] = set()
    for entry in manifest:
        if not isinstance(entry, dict):
            raise RuntimeError("manifest 条目必须是对象")
        missing = sorted(REQUIRED_FIELDS - set(entry))
        if missing:
            raise RuntimeError(f"{entry.get('id', '<unknown>')} 缺少字段：{', '.join(missing)}")

        asset_id = str(entry["id"])
        if asset_id in seen_ids:
            raise RuntimeError(f"重复资产 id：{asset_id}")
        seen_ids.add(asset_id)

        status = str(entry["status"])
        if status not in ALLOWED_STATUSES:
            raise RuntimeError(f"{asset_id} 使用了未登记状态：{status}")

        validate_prompt_ref(asset_id, str(entry["fullPromptRef"]), status)

        if status == "source_selected":
            asset_path = ROOT / str(entry["path"])
            if not asset_path.exists():
                raise RuntimeError(f"{asset_id} 缺少源图：{asset_path}")
            actual_size = read_png_size(asset_path)
            declared_size = parse_size(str(entry["sourceSize"]))
            if actual_size != declared_size:
                raise RuntimeError(f"{asset_id} 尺寸不匹配：manifest={declared_size}, actual={actual_size}")

        for optional_path_field in ("processedPath", "godotPath"):
            value = entry.get(optional_path_field)
            if value and str(value).startswith("assets/") and not (ROOT / str(value)).exists():
                raise RuntimeError(f"{asset_id} 的 {optional_path_field} 不存在：{value}")
            if value and str(value).startswith("res://"):
                godot_asset_path = ROOT / "clients" / "godot" / str(value).removeprefix("res://")
                if not godot_asset_path.exists():
                    raise RuntimeError(f"{asset_id} 的 Godot 资源不存在：{value}")


def validate_plan() -> None:
    """轻量校验资产批次计划，确保后续自动化有稳定入口。"""
    if not PLAN_PATH.exists():
        return
    plan = load_json(PLAN_PATH)
    if not isinstance(plan, dict):
        raise RuntimeError("initial_asset_plan.json 顶层必须是对象")
    batches = plan.get("batches")
    if not isinstance(batches, list) or not batches:
        raise RuntimeError("initial_asset_plan.json 需要非空 batches")
    seen_batches: set[str] = set()
    for batch in batches:
        batch_id = str(batch.get("id", ""))
        if not batch_id:
            raise RuntimeError("资产批次缺少 id")
        if batch_id in seen_batches:
            raise RuntimeError(f"重复资产批次 id：{batch_id}")
        seen_batches.add(batch_id)
        assets = batch.get("assets")
        if not isinstance(assets, list) or not assets:
            raise RuntimeError(f"{batch_id} 需要非空 assets")


def main() -> None:
    """执行资产 manifest 校验。"""
    validate_manifest()
    validate_plan()
    print("[asset-manifest-check] ok")


if __name__ == "__main__":
    main()
