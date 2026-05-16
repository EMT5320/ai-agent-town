"""校验 NPC 深度卡（npc codex）数据契约。

执行步骤：
1. 遍历 backend/app/content/data/npc/*.json，使用 codex_loader 解析校验。
2. 交叉校验 NPC id 必须存在于 backend/app/world/seed_data.AGENTS。
3. 交叉校验 assetRefs 引用 id 是否落在 assets/manifests/asset_manifest.json，
   缺失只产生 warning，不阻塞 CI（resemble check_asset_manifest.py 的友好策略）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = ROOT / "backend"
NPC_CODEX_PATH = BACKEND_PATH / "app" / "content" / "data" / "npc"
MANIFEST_PATH = ROOT / "assets" / "manifests" / "asset_manifest.json"

if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app.content.codex_loader import (  # noqa: E402  允许在 sys.path 修改后导入
    CodexValidationError,
    load_all_npc_deep_cards,
)
from app.world.seed_data import AGENTS  # noqa: E402  同上


def _load_manifest_ids() -> set[str]:
    """读取资产 manifest 的 id 集合，用于交叉引用 warning。"""
    if not MANIFEST_PATH.exists():
        return set()
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    if not isinstance(manifest, list):
        return set()
    return {str(entry.get("id")) for entry in manifest if isinstance(entry, dict) and entry.get("id")}


def _check_seed_membership(npc_ids: set[str]) -> None:
    """NPC 深度卡 id 必须在 seed_data.AGENTS 中，避免出现游离卡。"""
    seed_ids = {agent["id"] for agent in AGENTS}
    unknown = sorted(npc_ids - seed_ids)
    if unknown:
        raise SystemExit(f"[npc-codex-check] NPC id 未在 seed_data.AGENTS 中：{', '.join(unknown)}")


def _warn_missing_assets(card_id: str, refs: dict, manifest_ids: set[str]) -> list[str]:
    """检查资产引用是否命中 manifest，缺失给 warning。"""
    warnings: list[str] = []
    if not manifest_ids:
        return warnings
    portrait = refs.get("portrait", "")
    if portrait and portrait not in manifest_ids:
        warnings.append(f"{card_id}.assetRefs.portrait 未在 asset_manifest.json：{portrait}")
    for emotion, asset_id in (refs.get("expressions") or {}).items():
        if asset_id and asset_id not in manifest_ids:
            warnings.append(f"{card_id}.assetRefs.expressions.{emotion} 未在 asset_manifest.json：{asset_id}")
    map_sprite = refs.get("mapSprite", "")
    if map_sprite and map_sprite not in manifest_ids:
        warnings.append(f"{card_id}.assetRefs.mapSprite 未在 asset_manifest.json：{map_sprite}")
    return warnings


def _check_monologue_seed_readiness(cards: dict) -> None:
    """确保每位 NPC 都有可用于夜间反思的独白素材。"""
    for npc_id, card in cards.items():
        seeds = list(getattr(card, "monologue_seeds", ()))
        if not seeds:
            raise SystemExit(f"[npc-codex-check] {npc_id} 缺少 monologueSeeds，夜间反思无素材可用")

        tags = {tag for seed in seeds for tag in seed.context_tags}
        missing_tags = [tag for tag in ("morning", "afternoon", "evening") if tag not in tags]
        if missing_tags:
            raise SystemExit(f"[npc-codex-check] {npc_id} monologueSeeds 缺少时段标签：{', '.join(missing_tags)}")
        if "post_event" not in tags:
            raise SystemExit(f"[npc-codex-check] {npc_id} monologueSeeds 缺少 post_event 标签，夜间反思素材不足")
        if not {"high_mood", "low_mood"}.issubset(tags):
            raise SystemExit(f"[npc-codex-check] {npc_id} monologueSeeds 需同时覆盖 high_mood 和 low_mood")


def _check_gossip_hook_readiness(cards: dict) -> None:
    """确保每位 NPC 的 gossipHooks 可作为首版谣言传播素材直接消费。"""
    seed_ids = {agent["id"] for agent in AGENTS}
    valid_visibility = {"hidden", "town_known"}
    for npc_id, card in cards.items():
        hooks = list(getattr(card, "gossip_hooks", ()))
        if not hooks:
            raise SystemExit(f"[npc-codex-check] {npc_id} 缺少 gossipHooks，谣言传播无素材可用")

        seen_hook_ids: set[str] = set()
        has_town_known = False
        for hook in hooks:
            hook_id = str(getattr(hook, "hook_id", "")).strip()
            summary = str(getattr(hook, "summary", "")).strip()
            visibility = str(getattr(hook, "visibility", "")).strip()
            spread_affinity = {str(agent_id).strip() for agent_id in getattr(hook, "spread_affinity", ()) if str(agent_id).strip()}

            if not hook_id:
                raise SystemExit(f"[npc-codex-check] {npc_id} 存在空 gossipHooks.id")
            if hook_id in seen_hook_ids:
                raise SystemExit(f"[npc-codex-check] {npc_id} gossipHooks.id 重复：{hook_id}")
            seen_hook_ids.add(hook_id)

            if not summary:
                raise SystemExit(f"[npc-codex-check] {npc_id}.{hook_id} gossipHooks.summary 不能为空")
            if visibility not in valid_visibility:
                raise SystemExit(f"[npc-codex-check] {npc_id}.{hook_id} gossipHooks.visibility 非法：{visibility}")
            if visibility == "town_known":
                has_town_known = True

            if not spread_affinity:
                raise SystemExit(f"[npc-codex-check] {npc_id}.{hook_id} gossipHooks.spreadAffinity 至少 1 项")
            unknown_affinity = sorted(spread_affinity - seed_ids)
            if unknown_affinity:
                raise SystemExit(
                    f"[npc-codex-check] {npc_id}.{hook_id} gossipHooks.spreadAffinity 包含未知 NPC：{', '.join(unknown_affinity)}"
                )
            if npc_id in spread_affinity:
                raise SystemExit(f"[npc-codex-check] {npc_id}.{hook_id} gossipHooks.spreadAffinity 不应包含自己")

        if not has_town_known:
            raise SystemExit(f"[npc-codex-check] {npc_id} gossipHooks 至少需要 1 条 town_known 话题")


def main() -> None:
    """串联结构校验、seed 一致性、资产引用 warning。"""
    if not NPC_CODEX_PATH.exists():
        print("[npc-codex-check] ok (no codex files yet)")
        return

    try:
        cards = load_all_npc_deep_cards(base_dir=NPC_CODEX_PATH)
    except CodexValidationError as error:
        raise SystemExit(f"[npc-codex-check] {error}") from error

    if not cards:
        print("[npc-codex-check] ok (empty)")
        return

    _check_seed_membership(set(cards))
    _check_monologue_seed_readiness(cards)
    _check_gossip_hook_readiness(cards)

    manifest_ids = _load_manifest_ids()
    warnings: list[str] = []
    for npc_id, card in cards.items():
        from dataclasses import asdict

        refs = asdict(card.asset_refs)
        warnings.extend(
            _warn_missing_assets(
                npc_id,
                {
                    "portrait": refs["portrait"],
                    "expressions": refs["expressions"],
                    "mapSprite": refs["map_sprite"],
                },
                manifest_ids,
            )
        )

    for warning in warnings:
        print(f"[npc-codex-check] warning: {warning}")

    print(f"[npc-codex-check] ok ({len(cards)} card{'s' if len(cards) != 1 else ''})")


if __name__ == "__main__":
    main()
