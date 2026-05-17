class_name TownMap
extends Node2D

const ApiClientScript := preload("res://scripts/api_client.gd")
const AssetRegistryScript := preload("res://scripts/asset_registry.gd")
const PlayerControllerScript := preload("res://scripts/world/player_controller.gd")
const VnPanelScript := preload("res://scripts/ui/vn_panel.gd")

const STAGE_WIDTH := 640.0
const STAGE_HEIGHT := 1080.0
const PLAYER_INTERACT_RADIUS := 128.0
const ROUTE_LINE_VISIBLE_MSEC := 2200
const STAGE_ORDER := ["farm", "plaza", "tavern"]
const STAGE_NAMES := {
	"farm": "Farm 农场",
	"plaza": "Plaza 广场",
	"tavern": "Tavern 酒馆",
}
const STAGE_ANCHORS := {
	"farm": {
		"farm_house_door": Vector2(0.26, 0.68),
		"farm_field": Vector2(0.58, 0.72),
	},
	"plaza": {
		"plaza_gate": Vector2(0.18, 0.76),
		"plaza_fountain": Vector2(0.54, 0.62),
		"market_stall": Vector2(0.72, 0.58),
	},
	"tavern": {
		"tavern_door": Vector2(0.22, 0.74),
		"tavern_stage": Vector2(0.62, 0.56),
	},
}
const DEMO_SPAWN_ANCHORS := {
	"mira": "market_stall",
	"tomas": "plaza_fountain",
	"orren": "plaza_fountain",
	"lena": "plaza_fountain",
	"kai": "tavern_stage",
	"bram": "farm_field",
}
const NPC_CROWD_OFFSETS := {
	"mira": Vector2(-22.0, 12.0),
	"tomas": Vector2(-36.0, 10.0),
	"orren": Vector2(0.0, -8.0),
	"lena": Vector2(34.0, 12.0),
	"kai": Vector2(-18.0, 8.0),
	"bram": Vector2(20.0, 10.0),
}
const NPC_DISPLAY_NAMES := {
	"mira": "Mira 米娅",
	"tomas": "Tomas 托玛",
	"orren": "Orren 奥蕾娅",
	"lena": "Lena 莉娜",
	"kai": "Kai 凯娅",
	"bram": "Bram 布兰娜",
}
const NPC_COLORS := {
	"mira": Color(1.0, 0.76, 0.88, 1.0),
	"tomas": Color(0.70, 0.90, 1.0, 1.0),
	"orren": Color(0.86, 0.78, 1.0, 1.0),
	"lena": Color(0.82, 1.0, 0.74, 1.0),
	"kai": Color(1.0, 0.90, 0.62, 1.0),
	"bram": Color(1.0, 0.72, 0.55, 1.0),
}

@onready var stage_layer: Node2D = $StageLayer
@onready var npc_layer: Node2D = $NpcLayer
@onready var debug_layer: Node2D = $DebugLayer

var _api_client: ApiClient
var _asset_registry: AssetRegistry
var _stage_origins: Dictionary = {}
var _anchor_positions: Dictionary = {}
var _anchor_graph: Dictionary = {}
var _npc_nodes: Dictionary = {}
var _route_lines: Dictionary = {}
var _route_line_expire_msec: Dictionary = {}
var _event_label: Label
var _player_controller
var _camera: Camera2D
var _vn_panel
var _nearest_npc_id := ""
var _talk_in_flight := false


func _ready() -> void:
	# 默认入口必须直接使用现有美术资源，纯色块只作为资源缺失 fallback。
	stage_layer.z_index = 0
	debug_layer.z_index = 5
	npc_layer.z_index = 10
	_api_client = ApiClientScript.new()
	_api_client.name = "WorldInteractionApiClient"
	add_child(_api_client)
	_asset_registry = AssetRegistryScript.new()
	_asset_registry.name = "WorldAssetRegistry"
	add_child(_asset_registry)
	_build_stage_visuals()
	_build_anchor_graph()
	_build_event_label()
	_spawn_demo_npcs()
	_spawn_player()
	_build_camera()
	_build_vn_panel()
	_connect_event_bus()
	_connect_world_clock()
	set_process(true)


func _process(_delta: float) -> void:
	_update_camera_target()
	_update_nearest_npc_hint()
	_expire_route_lines()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey:
		var key_event := event as InputEventKey
		if key_event.pressed and not key_event.echo and key_event.keycode == KEY_E:
			if _nearest_npc_id != "":
				_submit_talk(_nearest_npc_id)
				get_viewport().set_input_as_handled()


func _build_stage_visuals() -> void:
	for i in range(STAGE_ORDER.size()):
		var stage_id := str(STAGE_ORDER[i])
		var origin := Vector2(float(i) * STAGE_WIDTH, 0.0)
		_stage_origins[stage_id] = origin
		_build_stage_background(stage_id, origin)
		_build_stage_title(stage_id, origin)


func _build_stage_background(stage_id: String, origin: Vector2) -> void:
	var texture := _asset_registry.get_location_background(stage_id)
	if texture != null:
		var sprite := Sprite2D.new()
		sprite.name = "Stage_%s_Background" % stage_id
		sprite.texture = texture
		sprite.centered = false
		sprite.position = origin
		var texture_size := texture.get_size()
		if texture_size.x > 0.0 and texture_size.y > 0.0:
			sprite.scale = Vector2(STAGE_WIDTH / texture_size.x, STAGE_HEIGHT / texture_size.y)
		stage_layer.add_child(sprite)
	else:
		var tile := ColorRect.new()
		tile.name = "Stage_%s_Fallback" % stage_id
		tile.position = origin
		tile.size = Vector2(STAGE_WIDTH, STAGE_HEIGHT)
		tile.color = _stage_color(stage_id)
		stage_layer.add_child(tile)

	var veil := ColorRect.new()
	veil.name = "Stage_%s_ReadabilityVeil" % stage_id
	veil.position = origin
	veil.size = Vector2(STAGE_WIDTH, STAGE_HEIGHT)
	veil.color = Color(0.0, 0.0, 0.0, 0.10)
	veil.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stage_layer.add_child(veil)


func _build_stage_title(stage_id: String, origin: Vector2) -> void:
	var title := Label.new()
	title.name = "Title_%s" % stage_id
	title.text = "%s / %s" % [str(STAGE_NAMES.get(stage_id, stage_id)), stage_id]
	title.position = origin + Vector2(18.0, 18.0)
	title.add_theme_font_size_override("font_size", 24)
	title.add_theme_color_override("font_color", Color(1.0, 1.0, 1.0, 1.0))
	title.add_theme_color_override("font_shadow_color", Color(0.0, 0.0, 0.0, 0.75))
	title.add_theme_constant_override("shadow_offset_x", 2)
	title.add_theme_constant_override("shadow_offset_y", 2)
	stage_layer.add_child(title)


func _build_anchor_graph() -> void:
	for stage_item in STAGE_ORDER:
		var stage_id := str(stage_item)
		var origin: Vector2 = _stage_origins.get(stage_id, Vector2.ZERO)
		var stage_anchors: Dictionary = STAGE_ANCHORS.get(stage_id, {})
		for anchor_key in stage_anchors.keys():
			var anchor_id := str(anchor_key)
			var ratio := stage_anchors[anchor_id] as Vector2
			var anchor_position := origin + Vector2(ratio.x * STAGE_WIDTH, ratio.y * STAGE_HEIGHT)
			_anchor_positions[anchor_id] = anchor_position
			_build_anchor_marker(anchor_id, anchor_position)

	for stage_item in STAGE_ORDER:
		var stage_id := str(stage_item)
		var stage_anchor_ids: Array = _anchor_ids_for_stage(stage_id)
		for anchor_key in stage_anchor_ids:
			var anchor_id := str(anchor_key)
			var linked_ids: Array = []
			for other_anchor_key in stage_anchor_ids:
				var other_anchor_id := str(other_anchor_key)
				if other_anchor_id != anchor_id:
					linked_ids.append(other_anchor_id)
			_anchor_graph[anchor_id] = linked_ids

	# 阶段 1 先显式连通跨场景 anchor，让 NPC 迁徙路径可读。
	_anchor_graph["farm_house_door"].append("plaza_gate")
	_anchor_graph["plaza_gate"].append("farm_house_door")
	_anchor_graph["market_stall"].append("tavern_door")
	_anchor_graph["tavern_door"].append("market_stall")


func _build_anchor_marker(anchor_id: String, anchor_position: Vector2) -> void:
	var marker := Node2D.new()
	marker.name = "Anchor_%s" % anchor_id
	marker.position = anchor_position

	var dot := ColorRect.new()
	dot.name = "Dot"
	dot.position = Vector2(-5.0, -5.0)
	dot.size = Vector2(10.0, 10.0)
	dot.color = Color(1.0, 0.92, 0.28, 0.92)
	dot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	marker.add_child(dot)

	var label := Label.new()
	label.name = "Label"
	label.text = anchor_id.replace("_", " ")
	label.position = Vector2(10.0, -12.0)
	label.add_theme_font_size_override("font_size", 12)
	label.add_theme_color_override("font_color", Color(1.0, 0.96, 0.65, 0.92))
	label.add_theme_color_override("font_shadow_color", Color(0.0, 0.0, 0.0, 0.85))
	label.add_theme_constant_override("shadow_offset_x", 1)
	label.add_theme_constant_override("shadow_offset_y", 1)
	marker.add_child(label)

	debug_layer.add_child(marker)


func _build_event_label() -> void:
	_event_label = Label.new()
	_event_label.name = "WorldEventLabel"
	_event_label.position = Vector2(18.0, STAGE_HEIGHT - 96.0)
	_event_label.size = Vector2(900.0, 56.0)
	_event_label.text = "Waiting for /api/world/tick ..."
	_event_label.add_theme_font_size_override("font_size", 18)
	_event_label.add_theme_color_override("font_color", Color(1.0, 1.0, 1.0, 0.95))
	_event_label.add_theme_color_override("font_shadow_color", Color(0.0, 0.0, 0.0, 0.85))
	_event_label.add_theme_constant_override("shadow_offset_x", 2)
	_event_label.add_theme_constant_override("shadow_offset_y", 2)
	debug_layer.add_child(_event_label)


func _spawn_demo_npcs() -> void:
	for npc_key in DEMO_SPAWN_ANCHORS.keys():
		var npc_id := str(npc_key)
		var node := _ensure_npc_controller(npc_id)
		node.set_anchor_position(str(DEMO_SPAWN_ANCHORS[npc_id]))


func _spawn_player() -> void:
	_player_controller = PlayerControllerScript.new()
	_player_controller.name = "PlayerController"
	npc_layer.add_child(_player_controller)
	_player_controller.set_world_bounds(_player_world_bounds())
	var spawn_point = _anchor_positions.get("plaza_gate", Vector2(STAGE_WIDTH + STAGE_WIDTH * 0.35, STAGE_HEIGHT * 0.76))
	if spawn_point is Vector2:
		_player_controller.set_spawn_position(spawn_point)
	_player_controller.configure_appearance("Player", _asset_registry.get_map_sprite("player"))


func _build_camera() -> void:
	_camera = Camera2D.new()
	_camera.name = "PlayerCamera"
	_camera.position_smoothing_enabled = true
	_camera.position_smoothing_speed = 8.0
	_camera.limit_left = 0
	_camera.limit_top = 0
	_camera.limit_right = int(STAGE_WIDTH * float(STAGE_ORDER.size()))
	_camera.limit_bottom = int(STAGE_HEIGHT)
	add_child(_camera)
	_update_camera_target()
	_camera.make_current()


func _build_vn_panel() -> void:
	_vn_panel = VnPanelScript.new()
	_vn_panel.name = "WorldVnPanel"
	add_child(_vn_panel)


func _connect_event_bus() -> void:
	var event_bus := _get_event_bus()
	if event_bus == null:
		return
	if not event_bus.npc_motion_event.is_connected(_on_npc_motion_event):
		event_bus.npc_motion_event.connect(_on_npc_motion_event)
	if not event_bus.npc_action_event.is_connected(_on_npc_action_event):
		event_bus.npc_action_event.connect(_on_npc_action_event)


func _connect_world_clock() -> void:
	var world_clock := _get_world_clock()
	if world_clock == null:
		return
	if not world_clock.tick_received.is_connected(_on_tick_received):
		world_clock.tick_received.connect(_on_tick_received)
	if not world_clock.tick_failed.is_connected(_on_tick_failed):
		world_clock.tick_failed.connect(_on_tick_failed)


func _on_npc_motion_event(npc_id: String, event_type: String, event_payload: Dictionary) -> void:
	var node := _ensure_npc_controller(npc_id)
	node.apply_tick_event(event_payload)
	_update_route_line(npc_id, event_type, event_payload)
	_update_event_label(npc_id, event_type, event_payload)


func _on_npc_action_event(npc_id: String, event_type: String, event_payload: Dictionary) -> void:
	var node := _ensure_npc_controller(npc_id)
	node.apply_tick_event(event_payload)
	_update_event_label(npc_id, event_type, event_payload)


func _on_tick_received(payload: Dictionary) -> void:
	if _event_label == null:
		return
	var events = payload.get("events", [])
	if events is Array and events.is_empty():
		_event_label.text = "Tick received: no NPC motion event yet."


func _on_tick_failed(error_message: String) -> void:
	if _event_label == null:
		return
	_event_label.text = "Tick failed: %s" % error_message


func _ensure_npc_controller(npc_id: String) -> NpcController:
	if _npc_nodes.has(npc_id):
		return _npc_nodes[npc_id] as NpcController

	var controller := NpcController.new()
	controller.name = "Npc_%s" % npc_id
	controller.npc_id = npc_id
	controller.configure_anchor_graph(_anchor_graph, _anchor_positions)
	controller.configure_appearance(
		str(NPC_DISPLAY_NAMES.get(npc_id, npc_id)),
		_asset_registry.get_map_sprite(npc_id),
		NPC_COLORS.get(npc_id, Color(1.0, 1.0, 1.0, 1.0))
	)
	var crowd_offset: Vector2 = NPC_CROWD_OFFSETS.get(npc_id, Vector2.ZERO)
	controller.set_crowd_offset(crowd_offset)
	npc_layer.add_child(controller)
	_npc_nodes[npc_id] = controller
	return controller


func _update_route_line(npc_id: String, event_type: String, event_payload: Dictionary) -> void:
	var line := _ensure_route_line(npc_id)
	if event_type == "npc.arrived":
		line.visible = false
		_route_line_expire_msec.erase(npc_id)
		return

	var from_anchor := str(event_payload.get("fromAnchorId", ""))
	var to_anchor := str(event_payload.get("toAnchorId", ""))
	var from_point = _anchor_positions.get(from_anchor, null)
	var to_point = _anchor_positions.get(to_anchor, null)
	if from_point is Vector2 and to_point is Vector2:
		line.visible = true
		line.default_color = _route_debug_color(npc_id)
		line.points = PackedVector2Array([from_point, to_point])
		_route_line_expire_msec[npc_id] = Time.get_ticks_msec() + ROUTE_LINE_VISIBLE_MSEC


func _ensure_route_line(npc_id: String) -> Line2D:
	if _route_lines.has(npc_id):
		return _route_lines[npc_id] as Line2D

	var line := Line2D.new()
	line.name = "Route_%s" % npc_id
	line.width = 2.0
	line.default_color = _route_debug_color(npc_id)
	line.joint_mode = Line2D.LINE_JOINT_ROUND
	line.begin_cap_mode = Line2D.LINE_CAP_ROUND
	line.end_cap_mode = Line2D.LINE_CAP_ROUND
	line.z_index = 1
	line.visible = false
	debug_layer.add_child(line)
	_route_lines[npc_id] = line
	return line


func _route_debug_color(npc_id: String) -> Color:
	# 路线只做开发期运动说明，降低透明度，避免压过角色和背景。
	var route_color: Color = NPC_COLORS.get(npc_id, Color(0.8, 0.9, 1.0, 1.0))
	route_color.a = 0.42
	return route_color


func _expire_route_lines() -> void:
	var now := Time.get_ticks_msec()
	for npc_key in _route_line_expire_msec.keys():
		var npc_id := str(npc_key)
		var expires_at := int(_route_line_expire_msec[npc_id])
		if now < expires_at:
			continue
		var line = _route_lines.get(npc_id, null)
		if line is Line2D:
			line.visible = false
		_route_line_expire_msec.erase(npc_id)


func _update_event_label(npc_id: String, event_type: String, event_payload: Dictionary) -> void:
	if _event_label == null:
		return
	var npc_name := str(NPC_DISPLAY_NAMES.get(npc_id, npc_id))
	if event_type == "npc.move_progress":
		_event_label.text = "%s moving: %s -> %s  %.0f%%" % [
			npc_name,
			str(event_payload.get("fromAnchorId", "?")),
			str(event_payload.get("toAnchorId", "?")),
			float(event_payload.get("progress", 0.0)) * 100.0,
		]
		return
	if event_type == "npc.action_started":
		_event_label.text = "%s action: %s" % [npc_name, str(event_payload.get("actionId", "action"))]
		return
	if event_type == "player.talked":
		_event_label.text = "Player talked with %s" % npc_name
		return
	_event_label.text = "%s / %s" % [npc_name, event_type]


func _update_camera_target() -> void:
	if _camera == null or _player_controller == null:
		return
	_camera.global_position = _player_controller.global_position


func _update_nearest_npc_hint() -> void:
	if _player_controller == null or _vn_panel == null:
		return
	var nearest_id := ""
	var nearest_distance := INF
	var player_point: Vector2 = _player_controller.interaction_origin()
	for npc_key in _npc_nodes.keys():
		var npc_id := str(npc_key)
		var controller := _npc_nodes[npc_id] as NpcController
		if controller == null:
			continue
		var distance: float = player_point.distance_to(controller.global_position)
		if distance < nearest_distance:
			nearest_distance = distance
			nearest_id = npc_id
	if nearest_id != "" and nearest_distance <= PLAYER_INTERACT_RADIUS:
		_nearest_npc_id = nearest_id
		_vn_panel.show_hint("E: talk to %s  (%.0f px)" % [str(NPC_DISPLAY_NAMES.get(nearest_id, nearest_id)), nearest_distance], true)
		return
	_nearest_npc_id = ""
	_vn_panel.show_hint("WASD / Arrow move - get close to an NPC and press E to talk", false)


func _submit_talk(npc_id: String) -> void:
	if _talk_in_flight:
		return
	_talk_in_flight = true
	var npc_name := str(NPC_DISPLAY_NAMES.get(npc_id, npc_id))
	if _vn_panel != null:
		_vn_panel.show_busy(npc_name)
	var response := await _api_client.post_player_action({
		"type": "talk",
		"targetId": npc_id,
		"locationId": _stage_id_for_position(_player_controller.global_position),
		"topic": "world_map_greeting",
		"message": "我在小镇里靠近你，想听听你现在正在忙什么。",
	})
	_talk_in_flight = false
	if not bool(response.get("ok", false)):
		if _vn_panel != null:
			_vn_panel.show_error(str(response.get("error", "talk failed")))
		return
	var result = response.get("data", {})
	if not (result is Dictionary):
		if _vn_panel != null:
			_vn_panel.show_error("Talk response is not a dictionary.")
		return
	var dialogue_text := _dialogue_text(result)
	var status_text := _talk_status_text(result)
	if _vn_panel != null:
		_vn_panel.show_dialogue(npc_name, dialogue_text, status_text)
	_update_event_label(npc_id, "player.talked", result)


func _dialogue_text(result: Dictionary) -> String:
	var dialogue = result.get("dialogue", [])
	if dialogue is Array and not dialogue.is_empty():
		var lines: Array[String] = []
		for item in dialogue:
			if item is Dictionary:
				var speaker := str(item.get("speakerName", item.get("speakerId", "NPC")))
				var text := str(item.get("text", ""))
				if text != "":
					lines.append("%s: %s" % [speaker, text])
		if not lines.is_empty():
			return "\n".join(lines)
	var feedback = result.get("actionFeedback", {})
	if feedback is Dictionary and str(feedback.get("summary", "")) != "":
		return str(feedback.get("summary", ""))
	return "The NPC nods to you."


func _talk_status_text(result: Dictionary) -> String:
	var relation_count := _array_size(result.get("relationshipDeltas", []))
	var memory_count := _array_size(result.get("memoryWrites", []))
	var event_count := _array_size(result.get("eventIds", []))
	return "backend talk - relations=%d memories=%d events=%d" % [relation_count, memory_count, event_count]


func _array_size(value) -> int:
	if value is Array:
		return value.size()
	return 0


func _stage_id_for_position(point: Vector2) -> String:
	var index := int(clamp(floor(point.x / STAGE_WIDTH), 0.0, float(STAGE_ORDER.size() - 1)))
	return str(STAGE_ORDER[index])


func _player_world_bounds() -> Rect2:
	return Rect2(Vector2(48.0, 132.0), Vector2(STAGE_WIDTH * float(STAGE_ORDER.size()) - 96.0, STAGE_HEIGHT - 252.0))


func _get_event_bus() -> EventBus:
	if has_node("/root/EventBusService"):
		return get_node("/root/EventBusService") as EventBus
	return null


func _get_world_clock() -> WorldClock:
	if has_node("/root/WorldClockService"):
		return get_node("/root/WorldClockService") as WorldClock
	return null


func _anchor_ids_for_stage(stage_id: String) -> Array:
	var stage_anchors: Dictionary = STAGE_ANCHORS.get(stage_id, {})
	var ids: Array = []
	for anchor_key in stage_anchors.keys():
		ids.append(str(anchor_key))
	return ids


func _stage_color(stage_id: String) -> Color:
	match stage_id:
		"farm":
			return Color(0.63, 0.82, 0.56, 1.0)
		"plaza":
			return Color(0.72, 0.73, 0.78, 1.0)
		"tavern":
			return Color(0.64, 0.56, 0.52, 1.0)
		_:
			return Color(0.25, 0.25, 0.25, 1.0)
