class_name TownMap
extends Node2D

const STAGE_WIDTH := 960.0
const STAGE_HEIGHT := 540.0
const STAGE_ORDER := ["farm", "plaza", "tavern"]
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
	"mira": "tavern_door",
	"tomas": "plaza_fountain",
	"orren": "plaza_fountain",
	"lena": "plaza_fountain",
	"kai": "tavern_stage",
	"bram": "farm_field",
}

@onready var stage_layer: Node2D = $StageLayer
@onready var npc_layer: Node2D = $NpcLayer

var _stage_origins: Dictionary = {}
var _anchor_positions: Dictionary = {}
var _anchor_graph: Dictionary = {}
var _npc_nodes: Dictionary = {}


func _ready() -> void:
	# 三场景横向拼图占位骨架。
	_build_stage_placeholders()
	_build_anchor_graph()
	_spawn_demo_npcs()
	_connect_event_bus()


func _build_stage_placeholders() -> void:
	for i in range(STAGE_ORDER.size()):
		var stage_id := str(STAGE_ORDER[i])
		var origin := Vector2(float(i) * STAGE_WIDTH, 0.0)
		_stage_origins[stage_id] = origin

		var tile := ColorRect.new()
		tile.name = "Stage_%s" % stage_id
		tile.position = origin
		tile.size = Vector2(STAGE_WIDTH, STAGE_HEIGHT)
		tile.color = _stage_color(stage_id)
		stage_layer.add_child(tile)

		var title := Label.new()
		title.name = "Title_%s" % stage_id
		title.text = stage_id.capitalize()
		title.position = origin + Vector2(16.0, 12.0)
		stage_layer.add_child(title)


func _build_anchor_graph() -> void:
	for stage_item in STAGE_ORDER:
		var stage_id := str(stage_item)
		var origin: Vector2 = _stage_origins.get(stage_id, Vector2.ZERO)
		var stage_anchors: Dictionary = STAGE_ANCHORS.get(stage_id, {})
		for anchor_key in stage_anchors.keys():
			var anchor_id := str(anchor_key)
			var ratio := stage_anchors[anchor_id] as Vector2
			_anchor_positions[anchor_id] = origin + Vector2(ratio.x * STAGE_WIDTH, ratio.y * STAGE_HEIGHT)

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

	# 场景之间只连接边缘锚点，形成横向可达图。
	_anchor_graph["farm_house_door"].append("plaza_gate")
	_anchor_graph["plaza_gate"].append("farm_house_door")
	_anchor_graph["market_stall"].append("tavern_door")
	_anchor_graph["tavern_door"].append("market_stall")


func _spawn_demo_npcs() -> void:
	for npc_key in DEMO_SPAWN_ANCHORS.keys():
		var npc_id := str(npc_key)
		var node := _ensure_npc_controller(npc_id)
		node.set_anchor_position(str(DEMO_SPAWN_ANCHORS[npc_id]))


func _connect_event_bus() -> void:
	var event_bus := _get_event_bus()
	if event_bus == null:
		return
	if not event_bus.npc_motion_event.is_connected(_on_npc_motion_event):
		event_bus.npc_motion_event.connect(_on_npc_motion_event)
	if not event_bus.npc_action_event.is_connected(_on_npc_action_event):
		event_bus.npc_action_event.connect(_on_npc_action_event)


func _on_npc_motion_event(npc_id: String, _event_type: String, event_payload: Dictionary) -> void:
	var node := _ensure_npc_controller(npc_id)
	node.apply_tick_event(event_payload)


func _on_npc_action_event(npc_id: String, _event_type: String, event_payload: Dictionary) -> void:
	var node := _ensure_npc_controller(npc_id)
	node.apply_tick_event(event_payload)


func _ensure_npc_controller(npc_id: String) -> NpcController:
	if _npc_nodes.has(npc_id):
		return _npc_nodes[npc_id] as NpcController

	var controller := NpcController.new()
	controller.name = "Npc_%s" % npc_id
	controller.npc_id = npc_id
	controller.configure_anchor_graph(_anchor_graph, _anchor_positions)
	npc_layer.add_child(controller)
	_npc_nodes[npc_id] = controller
	return controller


func _get_event_bus() -> EventBus:
	if has_node("/root/EventBusService"):
		return get_node("/root/EventBusService") as EventBus
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
