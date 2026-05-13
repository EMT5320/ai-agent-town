from __future__ import annotations

import json
import re
from typing import Any


def parse_provider_output(result: dict[str, Any]) -> dict[str, Any]:
    """解析 Provider 输出，保留自然语言兜底能力。"""
    if result.get("parsed"):
        return result["parsed"]
    raw = str(result.get("rawText", "")).strip()
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {"speech": raw or "沉默片刻，继续观察小镇。", "action": "remember", "args": {}, "memory_to_save": (raw[:120] if raw else "我进行了一次沉默观察。")}
