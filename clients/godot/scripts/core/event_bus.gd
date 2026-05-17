class_name EventBus
extends Node

signal tick_payload_received(payload: Dictionary)
signal tick_events_received(events: Array)
signal tick_clock_updated(clock: Dictionary)
signal tick_agents_updated(agents: Array)
signal event_received(event_type: String, event_payload: Dictionary)
signal npc_motion_event(npc_id: String, event_type: String, event_payload: Dictionary)
signal npc_action_event(npc_id: String, event_type: String, event_payload: Dictionary)


func _ready() -> void:
	# 自动消费 WorldClock 的 tick 回包事件。
	var clock_node := _resolve_world_clock()
	if clock_node == null:
		return
	if not clock_node.tick_received.is_connected(_on_world_clock_tick_received):
		clock_node.tick_received.connect(_on_world_clock_tick_received)


func _resolve_world_clock() -> WorldClock:
	if has_node("/root/WorldClockService"):
		return get_node("/root/WorldClockService") as WorldClock
	return null


func _on_world_clock_tick_received(payload: Dictionary) -> void:
	tick_payload_received.emit(payload)

	var clock = payload.get("clock", {})
	if clock is Dictionary:
		tick_clock_updated.emit(clock)

	var agents = payload.get("agents", [])
	if agents is Array:
		tick_agents_updated.emit(agents)

	var events = payload.get("events", [])
	if not (events is Array):
		return

	tick_events_received.emit(events)
	for item in events:
		if not (item is Dictionary):
			continue
		_dispatch_event(item)


func _dispatch_event(event_payload: Dictionary) -> void:
	var event_type := str(event_payload.get("type", ""))
	var event_data := _normalize_event_payload(event_payload, event_type)
	event_received.emit(event_type, event_data)

	var npc_id := str(event_data.get("npcId", ""))
	if npc_id == "":
		return

	if event_type.begins_with("npc.move") or event_type == "npc.arrived":
		npc_motion_event.emit(npc_id, event_type, event_data)
		return

	if event_type.begins_with("npc.action"):
		npc_action_event.emit(npc_id, event_type, event_data)


func _normalize_event_payload(event_payload: Dictionary, event_type: String) -> Dictionary:
	# 后端 EventStore 会把业务字段放在 payload 下，Godot 场景只消费扁平事件。
	var nested_payload = event_payload.get("payload", {})
	var event_data: Dictionary = {}
	if nested_payload is Dictionary:
		event_data = nested_payload.duplicate(true)
	else:
		event_data = event_payload.duplicate(true)
	event_data["type"] = event_type
	if event_payload.has("id"):
		event_data["eventId"] = event_payload["id"]
	if event_payload.has("createdAt"):
		event_data["createdAt"] = event_payload["createdAt"]
	return event_data
