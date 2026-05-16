from __future__ import annotations

import json
import os
import time
import urllib.request
from typing import Any, Callable


class CloudApiProvider:
    """OpenAI-compatible 云端 Provider，按模型 Profile 发起调用。"""

    name = "CloudApiProvider"

    def decide(
        self,
        _context: dict[str, Any],
        messages: list[dict[str, str]],
        profile: dict[str, Any] | None = None,
        output_parser: Callable[[str], dict[str, Any] | None] | None = None,
    ) -> dict[str, Any]:
        """使用传入 Profile 调用模型，支持不同 NPC 或功能使用不同模型。"""
        profile = profile or {}
        api_key_env = profile.get("apiKeyEnv") or "DEEPSEEK_API_KEY"
        # 兼容本地配置把真实 key 误填到 apiKeyEnv 的情况；公开接口会负责脱敏展示。
        inline_api_key = str(api_key_env) if self._looks_like_inline_secret(api_key_env) else None
        api_key = profile.get("apiKey") or inline_api_key or os.getenv(str(api_key_env)) or os.getenv("OPENAI_API_KEY")
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

    def _looks_like_inline_secret(self, value: Any) -> bool:
        """识别常见 API key 前缀，避免误填 apiKeyEnv 时真实调用失败。"""
        text = str(value or "")
        return text.startswith(("sk-", "sk_", "sk-proj-"))
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
        latency_ms = int((time.time() - started) * 1000)
        usage_data = data.get("usage", {})
        parsed = output_parser(raw_text) if output_parser else None
        return {
            "provider": self.name,
            "rawText": raw_text,
            "parsed": parsed,
            "usage": {
                "tokens": usage_data.get("total_tokens", 0),
                "promptTokens": usage_data.get("prompt_tokens", 0),
                "completionTokens": usage_data.get("completion_tokens", 0),
                "cost": 0,
                "latencyMs": latency_ms,
                "model": model,
                "profileName": profile.get("profileName"),
            },
        }
