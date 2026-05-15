"""检查 Godot 客户端骨架是否满足当前数据契约要求。"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GODOT_ROOT = ROOT / "clients" / "godot"


def read(path: Path) -> str:
    """按 UTF-8 读取项目文件。"""
    return path.read_text(encoding="utf-8")


required_files = [
    GODOT_ROOT / "project.godot",
    GODOT_ROOT / "README.md",
    GODOT_ROOT / "scenes" / "main.tscn",
    GODOT_ROOT / "scripts" / "asset_registry.gd",
    GODOT_ROOT / "scripts" / "main.gd",
    GODOT_ROOT / "scripts" / "api_client.gd",
    GODOT_ROOT / "scripts" / "world_sync.gd",
]

for file_path in required_files:
    if not file_path.exists():
        raise RuntimeError(f"Godot 客户端缺少必要文件：{file_path}")

project = read(GODOT_ROOT / "project.godot")
scene = read(GODOT_ROOT / "scenes" / "main.tscn")
asset_registry = read(GODOT_ROOT / "scripts" / "asset_registry.gd")
api_client = read(GODOT_ROOT / "scripts" / "api_client.gd")
main_script = read(GODOT_ROOT / "scripts" / "main.gd")
world_sync = read(GODOT_ROOT / "scripts" / "world_sync.gd")

checks = {
    "project main scene": 'run/main_scene="res://scenes/main.tscn"' in project,
    "scene script": 'path="res://scripts/main.gd"' in scene,
    "world state endpoint": '"/api/world/state"' in api_client,
    "player action endpoint": '"/api/player/action"' in api_client,
    "api class": "class_name ApiClient" in api_client,
    "asset registry class": "class_name AssetRegistry" in asset_registry,
    "asset registry backgrounds": "farm_day_anime.png" in asset_registry and "tavern_evening_anime.png" in asset_registry,
    "asset registry portraits": "npc_orren_neutral.png" in asset_registry and "player_farmer_neutral.png" in asset_registry,
    "world sync class": "class_name WorldSync" in world_sync,
    "main asset registry": "AssetRegistryScript" in main_script,
    "main background texture": "background_rect" in main_script,
    "main portrait texture": "portrait_rect" in main_script,
    "main refresh": "_refresh_world" in main_script,
}

failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise RuntimeError(f"Godot 客户端骨架检查失败：{', '.join(failed)}")

required_assets = [
    GODOT_ROOT / "assets" / "locations" / "farm_day_anime.png",
    GODOT_ROOT / "assets" / "locations" / "plaza_day_anime.png",
    GODOT_ROOT / "assets" / "locations" / "tavern_evening_anime.png",
    GODOT_ROOT / "assets" / "characters" / "player_farmer_neutral.png",
    GODOT_ROOT / "assets" / "characters" / "npc_mira_neutral.png",
    GODOT_ROOT / "assets" / "characters" / "npc_tomas_neutral.png",
    GODOT_ROOT / "assets" / "characters" / "npc_orren_neutral.png",
    GODOT_ROOT / "assets" / "characters" / "npc_lena_neutral.png",
    GODOT_ROOT / "assets" / "characters" / "npc_kai_neutral.png",
    GODOT_ROOT / "assets" / "characters" / "npc_bram_neutral.png",
]
missing_assets = [str(path.relative_to(GODOT_ROOT)) for path in required_assets if not path.exists()]
if missing_assets:
    raise RuntimeError(f"Godot 客户端缺少首批视觉资产：{', '.join(missing_assets)}")

missing_imports = [
    str(path.with_name(path.name + ".import").relative_to(GODOT_ROOT))
    for path in required_assets
    if not path.with_name(path.name + ".import").exists()
]
if missing_imports:
    raise RuntimeError(f"Godot 客户端缺少首批视觉资产导入元数据：{', '.join(missing_imports)}")

print("[godot-check] ok", {"files": len(required_files)})
