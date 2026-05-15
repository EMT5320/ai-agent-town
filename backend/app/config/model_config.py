from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
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
            "timeoutSeconds": 60,
        },
        "rule_fallback": {"provider": "rule"},
    },
    "npcProfiles": {},
    "featureProfiles": {"agent_decision": "default_deepseek"},
    "fallbackProfile": "rule_fallback",
}


class ModelConfigStore:
    """模型配置中心，负责按功能和 NPC 解析最终模型 Profile。"""

    def __init__(self, config_path: str | None = None) -> None:
        self.config_path = Path(config_path or os.getenv("AGENT_TOWN_MODEL_CONFIG", "config/models.json"))
        self.local_config_path = self.config_path.with_name("models.local.json")
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """读取 JSON 配置，并叠加本地私密覆盖文件。"""
        config = deepcopy(DEFAULT_CONFIG)
        if self.config_path.exists():
            config = self._deep_merge(config, self._read_json(self.config_path))
        if self.local_config_path.exists():
            config = self._deep_merge(config, self._read_json(self.local_config_path))
        return config

    def _read_json(self, path: Path) -> dict[str, Any]:
        """读取 UTF-8/UTF-8 BOM JSON 文件。"""
        with path.open("r", encoding="utf-8-sig") as file:
            return json.load(file)

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """递归合并配置，支持只覆盖某个 profile 的少数字段。"""
        result = deepcopy(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = deepcopy(value)
        return result

    def active_provider(self) -> str:
        """读取当前全局 Provider 模式，环境变量拥有最高优先级。"""
        return os.getenv("AGENT_TOWN_PROVIDER", self.config.get("activeProvider", "rule"))

    def resolve_profile(self, agent_id: str | None = None, feature: str = "agent_decision") -> dict[str, Any]:
        """按 NPC > 功能 > 默认 的顺序选择模型 Profile。"""
        profiles = self.config.get("profiles", {})
        profile_name = None
        if agent_id:
            profile_name = self.config.get("npcProfiles", {}).get(agent_id)
        if not profile_name:
            profile_name = self.config.get("featureProfiles", {}).get(feature)
        if not profile_name:
            profile_name = self.config.get("defaultProfile")
        profile = deepcopy(profiles.get(profile_name, {}))
        if not profile:
            fallback_name = self.config.get("fallbackProfile", "rule_fallback")
            profile = deepcopy(profiles.get(fallback_name, {"provider": "rule"}))
            profile_name = fallback_name
        profile["profileName"] = profile_name
        return self._apply_env_overrides(profile)

    def fallback_profile(self) -> dict[str, Any]:
        """返回规则兜底 Profile。"""
        fallback_name = self.config.get("fallbackProfile", "rule_fallback")
        profile = deepcopy(self.config.get("profiles", {}).get(fallback_name, {"provider": "rule"}))
        profile["profileName"] = fallback_name
        return profile

    def public_config(self) -> dict[str, Any]:
        """输出可展示配置，隐藏密钥，仅保留密钥是否已配置。"""
        config = deepcopy(self.config)
        config["configPath"] = str(self.config_path)
        config["localConfigPath"] = str(self.local_config_path)
        config["localConfigLoaded"] = self.local_config_path.exists()
        for profile in config.get("profiles", {}).values():
            has_inline_key = bool(profile.pop("apiKey", None))
            env_name = profile.get("apiKeyEnv")
            env_configured = bool(os.getenv(env_name)) if env_name else False
            if profile.get("provider") == "cloud":
                env_configured = env_configured or bool(os.getenv("OPENAI_API_KEY"))
            profile["apiKeyConfigured"] = has_inline_key or env_configured
        return config

    def _apply_env_overrides(self, profile: dict[str, Any]) -> dict[str, Any]:
        """兼容早期环境变量，方便主人临时覆盖模型。"""
        if profile.get("provider") == "cloud":
            profile["baseUrl"] = os.getenv("AGENT_TOWN_BASE_URL", profile.get("baseUrl", "https://api.deepseek.com"))
            profile["model"] = os.getenv("AGENT_TOWN_MODEL", profile.get("model", "deepseek-chat"))
            if os.getenv("AGENT_TOWN_TEMPERATURE"):
                profile["temperature"] = float(os.getenv("AGENT_TOWN_TEMPERATURE", "0.8"))
        return profile
