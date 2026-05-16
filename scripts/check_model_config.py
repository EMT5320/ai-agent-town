"""模型配置结构检查：只校验本地文件，不发起真实 LLM 请求。"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.config.model_config import ModelConfigStore  # noqa: E402


PUBLIC_CONFIG_FILES = (PROJECT_ROOT / "config" / "models.example.json",)


def read_json(path: Path) -> dict[str, Any]:
    """读取 UTF-8/UTF-8 BOM JSON，方便 Windows 编辑器保存后继续校验。"""
    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} 根节点必须是对象")
    return data


def find_inline_api_key_paths(value: Any, prefix: str = "") -> list[str]:
    """检查公开配置中是否误写 apiKey 字段，避免真实密钥进入仓库。"""
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{prefix}.{key}" if prefix else str(key)
            if key == "apiKey":
                paths.append(child_path)
            paths.extend(find_inline_api_key_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(find_inline_api_key_paths(child, f"{prefix}[{index}]"))
    return paths


for public_path in PUBLIC_CONFIG_FILES:
    if not public_path.exists():
        raise SystemExit(f"[model-config] missing: {public_path}")
    inline_key_paths = find_inline_api_key_paths(read_json(public_path))
    if inline_key_paths:
        raise SystemExit(f"[model-config] 公开配置禁止包含 apiKey 字段：{public_path} -> {inline_key_paths}")

store = ModelConfigStore()
public_config = store.public_config()
validation = public_config["validation"]
if not validation["ok"]:
    raise SystemExit("[model-config] invalid: " + json.dumps(validation["errors"], ensure_ascii=False))

print(
    "[model-config] ok",
    {
        "providerMode": store.active_provider(),
        "profiles": len(public_config.get("profiles", {})),
        "localConfigLoaded": public_config["localConfigLoaded"],
        "warnings": len(validation["warnings"]),
    },
)
