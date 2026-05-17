class_name NpcController
extends Node2D

enum NpcState {
	IDLE,
	WALKING,
	PERFORMING,
}

const MOVE_EPSILON := 2.0

@export var npc_id: String = ""
@export var move_speed_pixels: float = 120.0

var current_state: NpcState = NpcState.IDLE
var current_anchor_id: String = ""
var target_anchor_id: String = ""
var anchor_graph: Dictionary = {}
var anchor_positions: Dictionary = {}
var move_target: Vector2 = Vector2.ZERO

var _sprite: ColorRect
var _action_label: Label


func _ready() -> void:
	# 占位体直接用色块与动作标签，后续可替换成正式 sprite。
	_sprite = ColorRect.new()
	_sprite.name = "NpcBody"
	_sprite.color = Color(0.94, 0.88, 0.62, 1.0)
	_sprite.size = Vector2(24.0, 36.0)
	_sprite.position = Vector2(-12.0, -18.0)
	add_child(_sprite)

	_action_label = Label.new()
	_action_label.name = "ActionLabel"
	_action_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_action_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_action_label.position = Vector2(-48.0, -48.0)
	_action_label.size = Vector2(96.0, 20.0)
	_action_label.text = "Idle"
	add_child(_action_label)


func _process(delta: float) -> void:
	if current_state != NpcState.WALKING:
		return

	var to_target := move_target - global_position
	if to_target.length() <= MOVE_EPSILON:
		global_position = move_target
		_enter_state(NpcState.IDLE, "Idle")
		return

	var step: float = minf(to_target.length(), move_speed_pixels * delta)
	global_position += to_target.normalized() * step


func configure_anchor_graph(graph: Dictionary, positions: Dictionary) -> void:
	# graph: {"anchor_a": ["anchor_b", ...]}，positions: {"anchor_a": Vector2(...)}。
	anchor_graph = graph.duplicate(true)
	anchor_positions = positions.duplicate(true)


func apply_tick_event(event_payload: Dictionary) -> void:
	var event_type := str(event_payload.get("type", ""))
	if event_type == "npc.move_started":
		_handle_move_started(event_payload)
		return
	if event_type == "npc.move_progress":
		_handle_move_progress(event_payload)
		return
	if event_type == "npc.arrived":
		_handle_arrived(event_payload)
		return
	if event_type == "npc.action_started":
		_enter_state(NpcState.PERFORMING, _action_label_from_event(event_payload, "Doing"))
		return
	if event_type == "npc.action_completed":
		_enter_state(NpcState.IDLE, "Idle")


func set_anchor_position(anchor_id: String) -> void:
	var point = anchor_positions.get(anchor_id, null)
	if point is Vector2:
		current_anchor_id = anchor_id
		target_anchor_id = anchor_id
		global_position = point


func _handle_move_started(event_payload: Dictionary) -> void:
	var from_anchor := str(event_payload.get("fromAnchorId", event_payload.get("from", "")))
	var to_anchor := str(event_payload.get("toAnchorId", event_payload.get("to", "")))
	if from_anchor != "" and current_anchor_id == "":
		set_anchor_position(from_anchor)
	if to_anchor == "":
		return
	_target_anchor_move(to_anchor)


func _handle_move_progress(event_payload: Dictionary) -> void:
	# 支持后端给定插值进度，也支持直接给位置。
	var position_payload = event_payload.get("position", null)
	if position_payload is Dictionary:
		var x := float(position_payload.get("x", global_position.x))
		var y := float(position_payload.get("y", global_position.y))
		global_position = Vector2(x, y)
		_enter_state(NpcState.WALKING, "Walking")
		return

	var progress := float(event_payload.get("progress", -1.0))
	if progress < 0.0:
		return

	var from_anchor := str(event_payload.get("fromAnchorId", current_anchor_id))
	var to_anchor := str(event_payload.get("toAnchorId", target_anchor_id))
	var from_point = anchor_positions.get(from_anchor, null)
	var to_point = anchor_positions.get(to_anchor, null)
	if from_point is Vector2 and to_point is Vector2:
		var from_vec: Vector2 = from_point
		var to_vec: Vector2 = to_point
		global_position = from_vec.lerp(to_vec, clamp(progress, 0.0, 1.0))
		_enter_state(NpcState.WALKING, "Walking")


func _handle_arrived(event_payload: Dictionary) -> void:
	var arrived_anchor := str(event_payload.get("anchorId", event_payload.get("toAnchorId", target_anchor_id)))
	if arrived_anchor != "":
		set_anchor_position(arrived_anchor)
	_enter_state(NpcState.IDLE, "Idle")


func _target_anchor_move(anchor_id: String) -> void:
	var target = anchor_positions.get(anchor_id, null)
	if not (target is Vector2):
		return
	var next_target := target as Vector2

	# 后端当前直接下发起点和终点，客户端先按权威事件直线插值。
	target_anchor_id = anchor_id
	move_target = next_target
	_enter_state(NpcState.WALKING, "Walking")


func _action_label_from_event(event_payload: Dictionary, fallback_text: String) -> String:
	var action_name := str(event_payload.get("actionName", ""))
	if action_name != "":
		return action_name
	var action_id := str(event_payload.get("actionId", ""))
	if action_id != "":
		return action_id
	return fallback_text


func _enter_state(next_state: NpcState, label_text: String) -> void:
	current_state = next_state
	_action_label.text = label_text
	match current_state:
		NpcState.IDLE:
			_sprite.color = Color(0.94, 0.88, 0.62, 1.0)
		NpcState.WALKING:
			_sprite.color = Color(0.69, 0.86, 1.0, 1.0)
		NpcState.PERFORMING:
			_sprite.color = Color(0.79, 1.0, 0.72, 1.0)
