class_name WorldSync
extends Node

var current_state: Dictionary = {}


func apply_state(state: Dictionary) -> void:
	# 保留一份深拷贝，后续地图、角色和 UI 都从这里读取。
	current_state = state.duplicate(true)


func get_clock_label() -> String:
	var clock: Dictionary = current_state.get("clock", {})
	return "Day %s · %02d:00 · %s" % [clock.get("day", 1), int(clock.get("hour", 0)), clock.get("phase", "unknown")]


func get_player_label() -> String:
	var player: Dictionary = current_state.get("player", {})
	return "%s · 位置：%s" % [player.get("name", "Player"), player.get("locationId", "unknown")]


func get_locations() -> Array:
	return current_state.get("locations", [])


func get_npcs() -> Array:
	return current_state.get("npcs", [])


func get_recent_events() -> Array:
	return current_state.get("recentEvents", [])
