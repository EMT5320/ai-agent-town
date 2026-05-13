from __future__ import annotations

import json
import os
import time
import urllib.request
from typing import Any


class CloudApiProvider:
    """OpenAI-compatible 云端 Provider，按模型 Profile 发起调用。"""

    name = "CloudApiProvider"

    def decide(self, _context: dict[str, Any], messages: list[dict[str, str]], profile: dict[str, Any] | None = None) -> dict[str, Any]:
        """使用传入 Profile 调用模型，支持不同 NPC 或功能使用不同模型。"""
        profile = profile or {}
        api_key_env = profile.get("apiKeyEnv") or "DEEPSEEK_API_KEY"
        api_key = profile.get("apiKey") or os.getenv(api_key_env) or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(f"CloudApiProvider 缺少 API Key，请设置 {api_key_env} 或 OPENAI_API_KEY。")

        base_url = str(profile.get("baseUrl") or "https://api.deepseek.com").rstrip("/")
        model = profile.get("model") or "deepseek-chat"
        timeout = int(profile.get("timeoutSeconds", 60))
        payload_data = {
            "model": model,
            "messages": messages,
            "temperature": float(profile.get("temperature", 0.8)),
        }
        if profile.get("maxTokens"):
            # OpenAI-compatible 接口常用 max_tokens 字段。
            payload_data["max_tokens"] = int(profile["maxTokens"])

        started = time.time()
        payload = json.dumps(payload_data, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=payload,
            headers={"content-type": "application/json", "authorization": f"Bearer {api_key}"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        raw_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {
            "provider": self.name,
            "rawText": raw_text,
            "parsed": None,
            "usage": {
                "tokens": data.get("usage", {}).get("total_tokens", 0),
                "cost": 0,
                "latencyMs": int((time.time() - started) * 1000),
                "model": model,
                "profileName": profile.get("profileName"),
            },
        }
