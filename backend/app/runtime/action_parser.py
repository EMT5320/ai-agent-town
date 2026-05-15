from __future__ import annotations

import json
import re
from typing import Any


def parse_provider_output(result: dict[str, Any], fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    """解析 Provider 输出，优先结构化 JSON，失败时回落到自然语言。"""
    fallback_payload = dict(fallback or {})
    parsed = result.get("parsed")
    if isinstance(parsed, dict):
        return _merge_with_fallback(parsed, fallback_payload)

    raw = str(result.get("rawText", "")).strip()
    json_text = _extract_json_text(raw)
    if json_text:
        try:
            decoded = json.loads(json_text)
            if isinstance(decoded, dict):
                return _merge_with_fallback(decoded, fallback_payload)
        except json.JSONDecodeError:
            # 模型可能输出半截 JSON 或带解释文字，继续走自然语言兜底。
            pass

    natural = _natural_language_payload(raw)
    return _merge_with_fallback(natural, fallback_payload)


def _extract_json_text(raw: str) -> str | None:
    """从模型原文中提取 JSON 对象，兼容 ```json 代码块。"""
    if not raw:
        return None
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw, re.IGNORECASE)
    candidate = fenced.group(1).strip() if fenced else raw
    if candidate.startswith("{") and candidate.endswith("}"):
        return candidate
    match = re.search(r"\{[\s\S]*\}", candidate)
    return match.group(0) if match else None


def _natural_language_payload(raw: str) -> dict[str, Any]:
    """把自然语言输出包装成通用行动结构，保证调用方总能继续执行。"""
    text = raw or "沉默片刻，继续观察小镇。"
    return {
        "speech": text,
        "action": "remember",
        "args": {},
        "memory_to_save": text[:120] if raw else "我进行了一次沉默观察。",
        "naturalLanguageFallback": True,
    }


def _merge_with_fallback(parsed: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    """用兜底字段补齐缺省值，同时保留模型解析结果。"""
    merged = dict(fallback)
    merged.update(parsed)
    return merged
