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


func get_player() -> Dictionary:
	return current_state.get("player", {})


func get_player_anchor() -> Dictionary:
	var anchor = current_state.get("playerAnchor", {})
	if anchor is Dictionary:
		return anchor
	return {}


func get_anchors() -> Array:
	return current_state.get("anchors", [])


func get_interactables() -> Array:
	return current_state.get("interactables", [])


func get_farm_plots() -> Array:
	return current_state.get("farmPlots", [])


func get_npcs() -> Array:
	return current_state.get("npcs", [])


func get_recent_events() -> Array:
	return current_state.get("recentEvents", [])


func get_active_events() -> Array:
	return current_state.get("activeEvents", [])


func get_available_interactions() -> Array:
	return current_state.get("availableInteractions", [])


func get_current_objective() -> Dictionary:
	var objective = current_state.get("currentObjective", {})
	if objective is Dictionary:
		return objective
	return {}


func find_active_event(event_id: String) -> Dictionary:
	for event in get_active_events():
		if str(event.get("id", "")) == event_id:
			return event
	return {}


func find_interaction(action_type: String, target_kind: String, target_id: String) -> Dictionary:
	for interaction in get_available_interactions():
		if not (interaction is Dictionary):
			continue
		if str(interaction.get("type", "")) != action_type:
			continue
		var target = interaction.get("target", {})
		if not (target is Dictionary):
			continue
		if str(target.get("kind", "")) == target_kind and str(target.get("id", "")) == target_id:
			return interaction
	return {}


func find_interaction_by_id(interaction_id: String) -> Dictionary:
	for interaction in get_available_interactions():
		if not (interaction is Dictionary):
			continue
		if str(interaction.get("id", "")) == interaction_id:
			return interaction
	return {}


func find_anchor(anchor_id: String) -> Dictionary:
	for anchor in get_anchors():
		if not (anchor is Dictionary):
			continue
		if str(anchor.get("id", "")) == anchor_id:
			return anchor
	return {}


func find_interactable(interactable_id: String) -> Dictionary:
	for interactable in get_interactables():
		if not (interactable is Dictionary):
			continue
		if str(interactable.get("id", "")) == interactable_id:
			return interactable
	return {}


func find_event_choice_interaction(event_id: String, choice_id: String) -> Dictionary:
	for interaction in get_available_interactions():
		if not (interaction is Dictionary):
			continue
		if str(interaction.get("type", "")) != "attend_event":
			continue
		var target = interaction.get("target", {})
		var payload = interaction.get("payload", {})
		if not (target is Dictionary) or not (payload is Dictionary):
			continue
		if str(target.get("kind", "")) == "event" and str(target.get("id", "")) == event_id and str(payload.get("choice", "")) == choice_id:
			return interaction
	return {}
