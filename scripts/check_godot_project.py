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
    "asset registry map sprites": "npc_orren_map_idle.png" in asset_registry and "player_farmer_map_idle.png" in asset_registry,
    "asset registry interaction markers": "interaction_marker_talk.png" in asset_registry and "interaction_marker_event.png" in asset_registry,
    "world sync class": "class_name WorldSync" in world_sync,
    "world sync interactions": "get_available_interactions" in world_sync and "find_event_choice_interaction" in world_sync,
    "main asset registry": "AssetRegistryScript" in main_script,
    "main background texture": "background_rect" in main_script,
    "main map character layer": "map_character_layer" in main_script and "_render_map_characters" in main_script,
    "main local move feedback": "player_local_target" in main_script and "_tick_local_player_motion" in main_script,
    "main continuous input move": "Input.get_vector" in main_script and "PLAYER_LOCAL_KEY_STEP" not in main_script,
    "main proximity feedback": "_update_map_proximity_feedback" in main_script and "MapMoveHint" in main_script,
    "main wasd input move": "_ensure_local_input_actions" in main_script and "_read_local_move_axis" in main_script and "move_left" in main_script and "move_down" in main_script,
    "main direct map click target": "_on_map_character_layer_gui_input" in main_script and "gui_input.connect" in main_script,
    "main ui click-through": "mouse_filter = Control.MOUSE_FILTER_IGNORE" in main_script and "Control.FOCUS_NONE" in main_script,
    "main single proximity target": "nearest_npc_actor" in main_script and "nearest_event_marker" in main_script,
    "main separated player spawn": "_player_spawn_for_location" in main_script and "_scene_stage_center" in main_script,
    "main scene slot anchors": "MAP_NPC_SLOT_RATIOS" in main_script and "_scene_npc_anchor" in main_script and "_scene_anchor_from_ratio" in main_script,
    "main compact interact radius": "PLAYER_LOCAL_INTERACT_RADIUS := 86.0" in main_script,
    "main proximity hysteresis": "PLAYER_LOCAL_INTERACT_EXIT_MARGIN" in main_script and "current_near_npc_id" in main_script and "current_near_event_id" in main_script,
    "main clamped click target": "target_was_clamped" in main_script and "bounds.has_point(world_point)" not in main_script,
    "main wider dynamic map bounds": "viewport_size.x * 0.10" in main_script and "side_margin" in main_script,
    "main safe player spawn": "MAP_PLAYER_SPAWN_RATIO := Vector2(0.50, 0.66)" in main_script,
    "main clear near focus on location change": "current_near_npc_id = \"\"" in main_script and "selected_location_id != previous_location_id" in main_script,
    "main npc sprite remains clickable": "sprite_button.disabled = false" in main_script,
    "main no npc selection location drift": "selected_location_id = str(npc.get(\"locationId\"" not in main_script,
    "main no npc center cluster": "MAP_CLUSTER_OFFSETS" not in main_script and "_cluster_offset" not in main_script,
    "main current-scene actor filter": "npc_location != selected_location_id" in main_script and "event_location != selected_location_id" in main_script,
    "main wider walk area": "_clamp_point_to_walk_area" in main_script and "PLAYER_LOCAL_ZONE_RADIUS" not in main_script,
    "main click target marker": "PlayerMoveTarget" in main_script,
    "main no sprite halo background": '"Halo"' not in main_script,
    "main backend interactions": "give_gift" in main_script and "find_interaction" in main_script,
    "main no anchorId contract": "anchorId" not in main_script,
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
    GODOT_ROOT / "assets" / "sprites" / "player_farmer_map_idle.png",
    GODOT_ROOT / "assets" / "sprites" / "npc_mira_map_idle.png",
    GODOT_ROOT / "assets" / "sprites" / "npc_tomas_map_idle.png",
    GODOT_ROOT / "assets" / "sprites" / "npc_orren_map_idle.png",
    GODOT_ROOT / "assets" / "sprites" / "npc_lena_map_idle.png",
    GODOT_ROOT / "assets" / "sprites" / "npc_kai_map_idle.png",
    GODOT_ROOT / "assets" / "sprites" / "npc_bram_map_idle.png",
    GODOT_ROOT / "assets" / "sprites" / "interaction_marker_talk.png",
    GODOT_ROOT / "assets" / "sprites" / "interaction_marker_gift.png",
    GODOT_ROOT / "assets" / "sprites" / "interaction_marker_event.png",
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
