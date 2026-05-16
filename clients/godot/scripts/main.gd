extends Control

const ApiClientScript := preload("res://scripts/api_client.gd")
const AssetRegistryScript := preload("res://scripts/asset_registry.gd")
const WorldSyncScript := preload("res://scripts/world_sync.gd")

const MAP_NODE_SIZE := Vector2(112, 138)
const MAP_SPRITE_SIZE := 64.0
const MAP_SPRITE_SCALE := 1.35
const MAP_MARKER_SCALE := 0.43
const MAP_EVENT_MARKER_SCALE := 0.68
const MAP_CLUSTER_OFFSETS := [
	Vector2(-72, -8),
	Vector2(0, -44),
	Vector2(72, -8),
	Vector2(-72, 72),
	Vector2(0, 46),
	Vector2(72, 72),
	Vector2(0, 118),
]

var api_client: Node
var asset_registry
var world_sync: Node
var background_rect: TextureRect
var map_character_layer: Control
var status_label: Label
var player_label: Label
var location_list: VBoxContainer
var npc_list: VBoxContainer
var event_list: VBoxContainer
var event_choice_list: VBoxContainer
var dialogue_scroll: ScrollContainer
var portrait_rect: TextureRect
var speaker_label: Label
var dialogue_label: Label
var selected_location_id := "farm"
var selected_npc_id := "orren"
var selected_expression := "neutral"
var selected_event_id := ""
var selected_event_location_id := ""


func _ready() -> void:
	api_client = ApiClientScript.new()
	asset_registry = AssetRegistryScript.new()
	world_sync = WorldSyncScript.new()
	add_child(api_client)
	add_child(asset_registry)
	add_child(world_sync)
	_build_layout()
	await _refresh_world()
	_show_selected_npc_hint()


func _build_layout() -> void:
	_build_background()
	_build_map_character_layer()
	_build_top_layer()
	_build_dialogue_layer()


func _build_background() -> void:
	background_rect = TextureRect.new()
	background_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	background_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	background_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	background_rect.texture = asset_registry.get_location_background(selected_location_id)
	add_child(background_rect)


func _build_map_character_layer() -> void:
	# 地图角色层只负责展示与提交动作，坐标和可交互状态都从后端状态派生。
	map_character_layer = Control.new()
	map_character_layer.name = "MapCharacterLayer"
	map_character_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	map_character_layer.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(map_character_layer)


func _build_top_layer() -> void:
	var margin := MarginContainer.new()
	margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 24)
	margin.add_theme_constant_override("margin_right", 24)
	margin.add_theme_constant_override("margin_top", 18)
	margin.add_theme_constant_override("margin_bottom", 260)
	add_child(margin)

	var columns := HBoxContainer.new()
	columns.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	columns.size_flags_vertical = Control.SIZE_EXPAND_FILL
	columns.add_theme_constant_override("separation", 18)
	margin.add_child(columns)

	var left_panel := _create_panel(columns, Vector2(300, 0))
	var title := Label.new()
	title.text = "Agent Valley"
	title.add_theme_font_size_override("font_size", 30)
	left_panel.add_child(title)

	status_label = Label.new()
	status_label.text = "等待同步..."
	status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	left_panel.add_child(status_label)

	player_label = Label.new()
	player_label.text = "玩家状态等待同步..."
	player_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	left_panel.add_child(player_label)

	var refresh_button := Button.new()
	refresh_button.text = "刷新世界状态"
	refresh_button.pressed.connect(_on_refresh_pressed)
	left_panel.add_child(refresh_button)

	var location_title := Label.new()
	location_title.text = "地点"
	location_title.add_theme_font_size_override("font_size", 18)
	left_panel.add_child(location_title)

	location_list = VBoxContainer.new()
	location_list.size_flags_vertical = Control.SIZE_EXPAND_FILL
	left_panel.add_child(location_list)

	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	columns.add_child(spacer)

	var right_panel := _create_panel(columns, Vector2(330, 0))
	var npc_title := Label.new()
	npc_title.text = "首发居民"
	npc_title.add_theme_font_size_override("font_size", 18)
	right_panel.add_child(npc_title)

	npc_list = VBoxContainer.new()
	npc_list.size_flags_vertical = Control.SIZE_EXPAND_FILL
	right_panel.add_child(npc_list)

	var event_title := Label.new()
	event_title.text = "进行中事件"
	event_title.add_theme_font_size_override("font_size", 18)
	right_panel.add_child(event_title)

	event_list = VBoxContainer.new()
	event_list.size_flags_vertical = Control.SIZE_EXPAND_FILL
	right_panel.add_child(event_list)


func _build_dialogue_layer() -> void:
	var dialogue_panel := PanelContainer.new()
	dialogue_panel.anchor_left = 0.0
	dialogue_panel.anchor_top = 1.0
	dialogue_panel.anchor_right = 1.0
	dialogue_panel.anchor_bottom = 1.0
	dialogue_panel.offset_left = 24
	dialogue_panel.offset_top = -238
	dialogue_panel.offset_right = -24
	dialogue_panel.offset_bottom = -18
	dialogue_panel.add_theme_stylebox_override("panel", _make_panel_style(Color(0.05, 0.06, 0.08, 0.82)))
	add_child(dialogue_panel)

	var content := HBoxContainer.new()
	content.add_theme_constant_override("separation", 20)
	dialogue_panel.add_child(content)

	portrait_rect = TextureRect.new()
	portrait_rect.custom_minimum_size = Vector2(220, 220)
	portrait_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	portrait_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	content.add_child(portrait_rect)

	var text_box := VBoxContainer.new()
	text_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	content.add_child(text_box)

	speaker_label = Label.new()
	speaker_label.text = "等待选择居民"
	speaker_label.add_theme_font_size_override("font_size", 22)
	text_box.add_child(speaker_label)

	dialogue_scroll = ScrollContainer.new()
	dialogue_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	text_box.add_child(dialogue_scroll)

	dialogue_label = Label.new()
	dialogue_label.text = "选择一个居民后，这里会显示对应立绘和后端返回的对话。"
	dialogue_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dialogue_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	dialogue_scroll.add_child(dialogue_label)

	var actions := HBoxContainer.new()
	actions.add_theme_constant_override("separation", 10)
	text_box.add_child(actions)

	var talk_button := Button.new()
	talk_button.text = "聊天"
	talk_button.pressed.connect(_on_talk_pressed)
	actions.add_child(talk_button)

	var gift_button := Button.new()
	gift_button.text = "送礼"
	gift_button.pressed.connect(_on_gift_pressed)
	actions.add_child(gift_button)

	var farm_button := Button.new()
	farm_button.text = "回农场"
	farm_button.pressed.connect(_on_location_pressed.bind("farm"))
	actions.add_child(farm_button)

	var plaza_button := Button.new()
	plaza_button.text = "去广场"
	plaza_button.pressed.connect(_on_location_pressed.bind("plaza"))
	actions.add_child(plaza_button)

	var tavern_button := Button.new()
	tavern_button.text = "去酒馆"
	tavern_button.pressed.connect(_on_location_pressed.bind("tavern"))
	actions.add_child(tavern_button)

	var choice_title := Label.new()
	choice_title.text = "事件选项"
	choice_title.add_theme_font_size_override("font_size", 18)
	text_box.add_child(choice_title)

	event_choice_list = VBoxContainer.new()
	event_choice_list.add_theme_constant_override("separation", 6)
	text_box.add_child(event_choice_list)
	_render_event_choice_buttons([])


func _create_panel(parent: Control, minimum_size: Vector2) -> VBoxContainer:
	var panel := PanelContainer.new()
	panel.custom_minimum_size = minimum_size
	panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	panel.add_theme_stylebox_override("panel", _make_panel_style(Color(0.03, 0.04, 0.06, 0.72)))
	parent.add_child(panel)

	var box := VBoxContainer.new()
	box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	box.size_flags_vertical = Control.SIZE_EXPAND_FILL
	box.add_theme_constant_override("separation", 8)
	panel.add_child(box)
	return box


func _make_panel_style(color: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = Color(1.0, 0.85, 0.45, 0.25)
	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1
	style.corner_radius_top_left = 8
	style.corner_radius_top_right = 8
	style.corner_radius_bottom_left = 8
	style.corner_radius_bottom_right = 8
	style.content_margin_left = 14
	style.content_margin_top = 12
	style.content_margin_right = 14
	style.content_margin_bottom = 12
	return style


func _on_refresh_pressed() -> void:
	await _refresh_world()


func _on_location_pressed(location_id: String) -> void:
	_clear_event_focus()
	var previous_location_id := selected_location_id
	selected_location_id = location_id
	_set_status("正在移动到 %s ..." % location_id)
	var response = await api_client.post_player_action({"type": "move", "locationId": location_id})
	if not _is_action_response_ok(response):
		selected_location_id = previous_location_id
		_render_world()
		_set_status("移动失败：%s" % _response_error(response))
		return
	_apply_authoritative_state(response["data"]["state"])
	_render_world()
	_set_status("已到达：%s" % _get_location_name(selected_location_id))


func _on_talk_pressed() -> void:
	await _submit_talk(selected_npc_id)


func _on_gift_pressed() -> void:
	await _submit_gift(selected_npc_id)


func _on_map_npc_pressed(npc_id: String) -> void:
	_select_npc(npc_id, true)
	_render_world()
	await _submit_talk(npc_id)


func _on_map_talk_marker_pressed(npc_id: String) -> void:
	_select_npc(npc_id, true)
	_render_world()
	await _submit_talk(npc_id)


func _on_map_gift_marker_pressed(npc_id: String) -> void:
	_select_npc(npc_id, true)
	_render_world()
	await _submit_gift(npc_id)


func _on_map_event_marker_pressed(event_id: String, event_location: String) -> void:
	await _on_inspect_event_pressed(event_id, event_location)


func _submit_talk(npc_id: String) -> void:
	if npc_id.is_empty():
		_set_status("请先选择一个居民。")
		return
	var npc := _find_npc(npc_id)
	if npc.is_empty():
		_set_status("居民已不在当前首发列表：%s" % npc_id)
		return
	_clear_event_focus()
	selected_npc_id = npc_id
	selected_location_id = str(npc.get("locationId", selected_location_id))
	_render_portrait(npc)
	var payload := _interaction_payload_or_fallback(
		"talk",
		"npc",
		npc_id,
		{"type": "talk", "targetId": npc_id, "locationId": selected_location_id, "topic": "first_meeting"}
	)
	payload["topic"] = str(payload.get("topic", "first_meeting"))
	payload["message"] = str(payload.get("message", "你好，我刚搬到晨露农场，想认识一下小镇。"))
	_set_status("正在和 %s 聊天..." % npc.get("name", npc_id))
	var response = await api_client.post_player_action(payload)
	if not _is_action_response_ok(response):
		_set_status("对话动作失败：%s" % _response_error(response))
		return
	_apply_authoritative_state(response["data"]["state"])
	_render_social_action_result("对话", response["data"].get("result", {}))
	_render_world()
	_set_status("对话完成：%s" % world_sync.get_clock_label())


func _submit_gift(npc_id: String) -> void:
	if npc_id.is_empty():
		_set_status("请先选择一个居民。")
		return
	var npc := _find_npc(npc_id)
	if npc.is_empty():
		_set_status("居民已不在当前首发列表：%s" % npc_id)
		return
	var gift_interaction: Dictionary = world_sync.find_interaction("give_gift", "npc", npc_id)
	if not gift_interaction.is_empty() and not _is_interaction_enabled(gift_interaction):
		_set_status("暂时不能送礼：%s" % _interaction_reason(gift_interaction))
		return
	_clear_event_focus()
	selected_npc_id = npc_id
	selected_location_id = str(npc.get("locationId", selected_location_id))
	_render_portrait(npc)
	var payload := _interaction_payload_or_fallback(
		"give_gift",
		"npc",
		npc_id,
		{"type": "give_gift", "targetId": npc_id, "locationId": selected_location_id, "itemId": _first_gift_item_id()}
	)
	if str(payload.get("itemId", "")).is_empty():
		_set_status("背包里暂时没有可送出的礼物。")
		return
	_set_status("正在给 %s 送礼..." % npc.get("name", npc_id))
	var response = await api_client.post_player_action(payload)
	if not _is_action_response_ok(response):
		_set_status("送礼动作失败：%s" % _response_error(response))
		return
	_apply_authoritative_state(response["data"]["state"])
	_render_social_action_result("送礼", response["data"].get("result", {}))
	_render_world()
	_set_status("送礼完成：%s" % world_sync.get_clock_label())


func _on_inspect_event_pressed(event_id: String, event_location: String) -> void:
	selected_event_id = event_id
	selected_event_location_id = event_location
	_set_status("正在查看事件：%s ..." % event_id)
	# 事件查看只通过后端 inspect 获取可见信息，客户端保持展示层职责。
	var payload := _interaction_payload_or_fallback(
		"inspect",
		"event",
		event_id,
		{"type": "inspect", "eventId": event_id, "locationId": event_location}
	)
	var response = await api_client.post_player_action(payload)
	if not _is_action_response_ok(response):
		_set_status("查看事件失败：%s" % _response_error(response))
		return
	_apply_authoritative_state(response["data"]["state"])
	var inspect_payload: Dictionary = response["data"].get("result", {}).get("inspect", {})
	_render_world()
	_render_inspect_result(inspect_payload)
	_set_status("已获取事件线索：%s" % inspect_payload.get("title", event_id))


func _on_attend_event_choice_pressed(event_id: String, event_location: String, choice_id: String) -> void:
	_set_status("正在提交事件选择：%s ..." % choice_id)
	# 玩家选择统一提交后端，事件结算、关系变化和记忆写入都由 Runtime 返回。
	var interaction: Dictionary = world_sync.find_event_choice_interaction(event_id, choice_id)
	if not interaction.is_empty() and not _is_interaction_enabled(interaction):
		_set_status("事件选项暂不可用：%s" % _interaction_reason(interaction))
		return
	var payload := _payload_from_interaction(interaction)
	if payload.is_empty():
		payload = {"type": "attend_event", "eventId": event_id, "choice": choice_id, "locationId": event_location}
	var response = await api_client.post_player_action(payload)
	if not _is_action_response_ok(response):
		_set_status("事件结算失败：%s" % _response_error(response))
		return
	_apply_authoritative_state(response["data"]["state"])
	_render_world()
	_render_attend_result(response["data"].get("result", {}))
	_set_status("事件已提交：%s" % choice_id)


func _on_npc_pressed(npc_id: String) -> void:
	_select_npc(npc_id, true)
	_render_world()
	var npc := _find_npc(npc_id)
	if npc.is_empty():
		return
	dialogue_label.text = "%s 正在 %s。点击地图小人或“聊天 / 送礼”按钮会向后端提交动作。" % [
		npc.get("name", npc_id),
		_get_location_name(str(npc.get("locationId", "unknown")))
	]
	_set_status("已选择居民：%s" % npc.get("name", npc_id))


func _refresh_world() -> void:
	_set_status("正在读取 /api/world/state ...")
	var response = await api_client.get_world_state()
	if not response.get("ok", false):
		_set_status("世界状态读取失败：%s" % response.get("error", "unknown"))
		return
	_apply_authoritative_state(response["data"])
	_render_world()
	_set_status("世界状态已同步：%s" % world_sync.get_clock_label())


func _apply_authoritative_state(state: Dictionary) -> void:
	# 所有动作回执都以 state 为准，客户端只保留当前选中项和 VN 展示文本。
	world_sync.apply_state(state)
	selected_location_id = str(state.get("player", {}).get("locationId", selected_location_id))
	_ensure_selected_npc()
	_sync_event_focus_with_world()


func _render_world() -> void:
	player_label.text = world_sync.get_player_label()
	_render_background()
	_render_map_characters()
	_render_locations()
	_render_npcs()
	_render_events()
	_render_focus_visual()


func _render_background() -> void:
	var texture: Texture2D = asset_registry.get_location_background(selected_location_id)
	if texture == null:
		texture = asset_registry.get_location_background("farm")
	background_rect.texture = texture


func _render_map_characters() -> void:
	if map_character_layer == null:
		return
	_clear_control_children(map_character_layer)
	var bounds := _map_bounds()
	_render_map_event_markers(bounds)

	var occupancy: Dictionary = {}
	var player: Dictionary = world_sync.get_player()
	var player_location := str(player.get("locationId", selected_location_id))
	_add_map_actor("player", str(player.get("name", "新来的农场主")), player_location, true, occupancy, bounds)
	for npc in world_sync.get_npcs():
		if not (npc is Dictionary):
			continue
		var npc_id := str(npc.get("id", ""))
		if npc_id.is_empty() or not asset_registry.has_map_sprite(npc_id):
			continue
		_add_map_actor(npc_id, str(npc.get("name", npc_id)), str(npc.get("locationId", selected_location_id)), false, occupancy, bounds)


func _render_map_event_markers(bounds: Rect2) -> void:
	for event_data in world_sync.get_active_events():
		if not (event_data is Dictionary):
			continue
		var event_id := str(event_data.get("id", ""))
		if event_id.is_empty() or str(event_data.get("status", "available")) == "resolved":
			continue
		var event_location := str(event_data.get("locationId", selected_location_id))
		var event_title := str(event_data.get("title", event_id))
		var anchor := _map_position_for_location(event_location, bounds) + Vector2(0, -118)
		var marker := TextureButton.new()
		marker.name = "MapEvent_%s" % event_id
		marker.texture_normal = asset_registry.get_interaction_marker("event")
		marker.scale = Vector2(MAP_EVENT_MARKER_SCALE, MAP_EVENT_MARKER_SCALE)
		marker.position = anchor - Vector2(MAP_SPRITE_SIZE * MAP_EVENT_MARKER_SCALE * 0.5, MAP_SPRITE_SIZE * MAP_EVENT_MARKER_SCALE * 0.5)
		marker.tooltip_text = "查看事件：%s" % event_title
		marker.set_meta("eventId", event_id)
		marker.set_meta("locationId", event_location)
		marker.set_meta("interactable", true)
		marker.pressed.connect(_on_map_event_marker_pressed.bind(event_id, event_location))
		if selected_event_id == event_id:
			marker.modulate = Color(1.0, 0.92, 0.45, 1.0)
		map_character_layer.add_child(marker)

		var label := _create_map_label(event_title, 160, 14)
		label.position = marker.position + Vector2(-58, 44)
		map_character_layer.add_child(label)


func _add_map_actor(owner_id: String, display_name: String, location_id: String, is_player: bool, occupancy: Dictionary, bounds: Rect2) -> void:
	var index := int(occupancy.get(location_id, 0))
	occupancy[location_id] = index + 1
	var anchor := _map_position_for_location(location_id, bounds) + _cluster_offset(index)
	var actor := _create_map_actor_node(owner_id, display_name, location_id, is_player, anchor)
	map_character_layer.add_child(actor)


func _create_map_actor_node(owner_id: String, display_name: String, location_id: String, is_player: bool, anchor: Vector2) -> Control:
	var actor := Control.new()
	actor.name = "MapActor_%s" % owner_id
	actor.position = anchor - Vector2(MAP_NODE_SIZE.x * 0.5, MAP_NODE_SIZE.y)
	actor.size = MAP_NODE_SIZE
	actor.set_meta("agentId", owner_id)
	actor.set_meta("locationId", location_id)
	actor.set_meta("interactable", not is_player)

	var halo := ColorRect.new()
	halo.position = Vector2(12, 34)
	halo.size = Vector2(88, 88)
	halo.color = Color(1.0, 0.86, 0.38, 0.22 if owner_id == selected_npc_id else 0.08)
	actor.add_child(halo)

	var sprite_button := TextureButton.new()
	sprite_button.name = "Sprite"
	sprite_button.texture_normal = asset_registry.get_map_sprite(owner_id)
	sprite_button.scale = Vector2(MAP_SPRITE_SCALE, MAP_SPRITE_SCALE)
	sprite_button.position = Vector2((MAP_NODE_SIZE.x - MAP_SPRITE_SIZE * MAP_SPRITE_SCALE) * 0.5, 38)
	sprite_button.disabled = is_player
	sprite_button.tooltip_text = "%s · %s" % [display_name, _get_location_name(location_id)]
	if not is_player:
		sprite_button.pressed.connect(_on_map_npc_pressed.bind(owner_id))
	actor.add_child(sprite_button)

	if is_player:
		var player_marker := _create_map_label("玩家", 52, 13)
		player_marker.position = Vector2(30, 9)
		actor.add_child(player_marker)
	else:
		var talk_interaction: Dictionary = world_sync.find_interaction("talk", "npc", owner_id)
		var gift_interaction: Dictionary = world_sync.find_interaction("give_gift", "npc", owner_id)
		var talk_enabled := _is_interaction_enabled_or_missing(talk_interaction)
		var gift_enabled := _is_interaction_enabled_or_missing(gift_interaction)
		actor.set_meta("interactable", talk_enabled or gift_enabled)

		var talk_marker := _create_actor_marker("talk", "聊天：%s" % display_name, talk_enabled)
		talk_marker.position = Vector2(6, 8)
		talk_marker.pressed.connect(_on_map_talk_marker_pressed.bind(owner_id))
		actor.add_child(talk_marker)

		var gift_marker := _create_actor_marker("gift", "送礼：%s" % display_name, gift_enabled)
		gift_marker.position = Vector2(78, 8)
		gift_marker.pressed.connect(_on_map_gift_marker_pressed.bind(owner_id))
		actor.add_child(gift_marker)

	var name_label := _create_map_label(display_name, int(MAP_NODE_SIZE.x), 14)
	name_label.position = Vector2(0, 116)
	actor.add_child(name_label)
	return actor


func _create_actor_marker(marker_id: String, tooltip: String, enabled: bool) -> TextureButton:
	var marker := TextureButton.new()
	marker.texture_normal = asset_registry.get_interaction_marker(marker_id)
	marker.scale = Vector2(MAP_MARKER_SCALE, MAP_MARKER_SCALE)
	marker.tooltip_text = tooltip
	marker.disabled = not enabled
	if not enabled:
		marker.modulate = Color(1, 1, 1, 0.34)
	return marker


func _create_map_label(text: String, width: int, font_size: int) -> Label:
	var label := Label.new()
	label.text = text
	label.size = Vector2(width, 24)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", Color(1, 0.96, 0.84, 1))
	label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
	label.add_theme_constant_override("shadow_offset_x", 1)
	label.add_theme_constant_override("shadow_offset_y", 1)
	return label


func _map_bounds() -> Rect2:
	var viewport_size := get_viewport_rect().size
	var left := 360.0
	var right = max(left + 420.0, viewport_size.x - 350.0)
	var top := 84.0
	var bottom = max(top + 270.0, viewport_size.y - 270.0)
	return Rect2(left, top, right - left, bottom - top)


func _map_position_for_location(location_id: String, bounds: Rect2) -> Vector2:
	var location := _find_location(location_id)
	var x_ratio := float(location.get("x", 50.0)) / 100.0 if not location.is_empty() else 0.5
	var y_ratio := float(location.get("y", 55.0)) / 100.0 if not location.is_empty() else 0.55
	return Vector2(bounds.position.x + bounds.size.x * x_ratio, bounds.position.y + bounds.size.y * y_ratio)


func _cluster_offset(index: int) -> Vector2:
	if index < MAP_CLUSTER_OFFSETS.size():
		return MAP_CLUSTER_OFFSETS[index]
	return Vector2((index % 4 - 1.5) * 58.0, 118.0 + int(index / 4) * 44.0)


func _render_locations() -> void:
	_clear_column(location_list)
	for location in world_sync.get_locations():
		var location_id := str(location.get("id", "unknown"))
		var location_name: String = str(location.get("name", location_id))
		var has_visual: bool = asset_registry.has_location_background(location_id)
		var current_marker: String = "（当前）" if location_id == selected_location_id else ""
		var button := Button.new()
		button.text = "%s%s\n%s" % [location_name, current_marker, location_id]
		button.disabled = not has_visual or location_id == selected_location_id
		button.tooltip_text = ("移动到 %s" % location_name) if has_visual else "首版暂未接入该地点背景"
		button.pressed.connect(_on_location_pressed.bind(location_id))
		location_list.add_child(button)


func _render_npcs() -> void:
	_clear_column(npc_list)
	for npc in world_sync.get_npcs():
		var npc_id := str(npc.get("id", "unknown"))
		if not asset_registry.has_portrait(npc_id, selected_expression):
			continue
		var selected_marker: String = "（选中）" if npc_id == selected_npc_id else ""
		var button := Button.new()
		button.text = "%s%s · %s\n%s" % [
			npc.get("name", npc_id),
			selected_marker,
			npc.get("job", "居民"),
			_get_location_name(str(npc.get("locationId", "unknown")))
		]
		button.pressed.connect(_on_npc_pressed.bind(npc_id))
		npc_list.add_child(button)


func _render_events() -> void:
	_clear_column(event_list)
	var active_events: Array = world_sync.get_active_events()
	if active_events.is_empty():
		var empty_item := Label.new()
		empty_item.text = "当前无进行中事件"
		event_list.add_child(empty_item)
	else:
		for event_data in active_events:
			var event_id := str(event_data.get("id", ""))
			var event_location := str(event_data.get("locationId", selected_location_id))
			var event_title := str(event_data.get("title", event_id))
			var event_status := str(event_data.get("status", "unknown"))
			var event_box := VBoxContainer.new()
			event_box.add_theme_constant_override("separation", 4)
			event_list.add_child(event_box)

			var header := Label.new()
			header.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			header.text = "%s（%s）" % [event_title, event_status]
			event_box.add_child(header)

			var summary := Label.new()
			summary.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			summary.text = str(event_data.get("summary", ""))
			event_box.add_child(summary)

			var inspect_button := Button.new()
			inspect_button.text = "查看事件"
			inspect_button.disabled = event_id.is_empty()
			inspect_button.pressed.connect(_on_inspect_event_pressed.bind(event_id, event_location))
			event_box.add_child(inspect_button)

	var history_title := Label.new()
	history_title.text = "最近事件日志"
	history_title.add_theme_font_size_override("font_size", 16)
	event_list.add_child(history_title)

	var history: Array = world_sync.get_recent_events().duplicate()
	history = history.slice(max(0, history.size() - 5))
	history.reverse()
	if history.is_empty():
		var history_empty := Label.new()
		history_empty.text = "暂无日志"
		event_list.add_child(history_empty)
		return
	for event in history:
		var item := Label.new()
		item.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		var payload: Dictionary = event.get("payload", {})
		item.text = "%s\n%s" % [event.get("type", "event"), payload.get("summary", payload.get("message", payload.get("speech", "")))]
		event_list.add_child(item)


func _render_focus_visual() -> void:
	if selected_event_id.is_empty():
		_render_portrait(_find_npc(selected_npc_id))
		return
	var event_texture: Texture2D = asset_registry.get_event_cg(selected_event_id)
	if event_texture == null:
		_render_portrait(_find_npc(selected_npc_id))
		return
	portrait_rect.texture = event_texture


func _render_inspect_result(inspect_payload: Dictionary) -> void:
	var title := str(inspect_payload.get("title", selected_event_id))
	var summary := str(inspect_payload.get("summary", "暂无事件描述。"))
	var location_name := _get_location_name(str(inspect_payload.get("locationId", selected_event_location_id)))
	var event_status := str(inspect_payload.get("status", "available"))
	speaker_label.text = "事件 · %s" % title
	dialogue_label.text = "%s\n地点：%s\n状态：%s\n\n%s" % [title, location_name, event_status, summary]
	if event_status == "resolved":
		dialogue_label.text += "\n\n事件已结算，不能再次提交选择。"
		_render_event_choice_buttons([])
	else:
		_render_event_choice_buttons(inspect_payload.get("choices", []))
	_render_focus_visual()


func _render_event_choice_buttons(choices: Array) -> void:
	if event_choice_list == null:
		return
	_clear_column(event_choice_list)
	if selected_event_id.is_empty() or choices.is_empty():
		var empty_hint := Label.new()
		empty_hint.text = "当前事件没有可提交选项。"
		event_choice_list.add_child(empty_hint)
		return
	for choice_data in choices:
		var choice_id := str(choice_data.get("id", ""))
		var choice_label := str(choice_data.get("label", choice_id))
		var interaction: Dictionary = world_sync.find_event_choice_interaction(selected_event_id, choice_id)
		var button := Button.new()
		button.text = choice_label
		button.disabled = choice_id.is_empty() or (not interaction.is_empty() and not _is_interaction_enabled(interaction))
		button.pressed.connect(_on_attend_event_choice_pressed.bind(selected_event_id, selected_event_location_id, choice_id))
		event_choice_list.add_child(button)


func _render_social_action_result(action_label: String, result: Dictionary) -> void:
	var lines: Array[String] = []
	var dialogue: Array = result.get("dialogue", [])
	if not dialogue.is_empty():
		var first_line: Dictionary = dialogue[0]
		lines.append(str(first_line.get("text", first_line.get("speech", "对方轻轻点头。"))))
		speaker_label.text = "%s · %s" % [action_label, first_line.get("speakerName", first_line.get("speakerId", selected_npc_id))]
	else:
		lines.append("动作已提交。")
		speaker_label.text = action_label
	var relationship_deltas: Array = result.get("relationshipDeltas", [])
	if not relationship_deltas.is_empty():
		lines.append("\n关系变化：")
		for delta in relationship_deltas:
			var change: Dictionary = delta.get("delta", {})
			lines.append(
				"- %s 亲密%+d / 信任%+d / 冲突%+d"
				% [
					delta.get("targetName", delta.get("targetId", "未知角色")),
					int(change.get("affection", 0)),
					int(change.get("trust", 0)),
					int(change.get("conflict", 0)),
				]
			)
	var memory_writes: Array = result.get("memoryWrites", [])
	if not memory_writes.is_empty():
		lines.append("\n记忆写入：")
		for memory in memory_writes.slice(0, 3):
			if memory is Dictionary:
				lines.append("- %s：%s" % [memory.get("agentName", memory.get("agentId", "系统")), memory.get("text", "")])
	dialogue_label.text = "\n".join(lines)


func _render_attend_result(result: Dictionary) -> void:
	var lines: Array[String] = []
	var event_result: Dictionary = result.get("eventResult", {})
	if not event_result.is_empty():
		lines.append("事件结果：%s" % str(event_result.get("summary", "")))
	var dialogue: Array = result.get("dialogue", [])
	if not dialogue.is_empty():
		lines.append("NPC 台词：")
		for item in dialogue:
			lines.append("- %s：%s" % [item.get("speakerName", item.get("speakerId", "未知角色")), item.get("text", "")])
	var relationship_deltas: Array = result.get("relationshipDeltas", [])
	if not relationship_deltas.is_empty():
		lines.append("关系变化：")
		for delta in relationship_deltas:
			var change: Dictionary = delta.get("delta", {})
			lines.append(
				"- %s 亲密%+d / 信任%+d / 冲突%+d"
				% [
					delta.get("targetName", delta.get("targetId", "未知角色")),
					int(change.get("affection", 0)),
					int(change.get("trust", 0)),
					int(change.get("conflict", 0)),
				]
			)
	var memory_writes: Array = result.get("memoryWrites", [])
	var immediate_memories: Array = []
	var night_reflections: Array = []
	for memory in memory_writes:
		if not (memory is Dictionary):
			continue
		if _memory_has_tag(memory, "night_reflection"):
			night_reflections.append(memory)
		else:
			immediate_memories.append(memory)
	if not immediate_memories.is_empty():
		lines.append("记忆写入：")
		for memory in immediate_memories:
			lines.append("- %s：%s" % [memory.get("agentName", memory.get("agentId", "系统")), memory.get("text", "")])
	if not night_reflections.is_empty():
		lines.append("夜间反思摘要：")
		for memory in night_reflections:
			lines.append("- %s：%s" % [memory.get("agentName", memory.get("agentId", "系统")), memory.get("text", "")])
	if lines.is_empty():
		lines.append("事件提交完成。")
	dialogue_label.text = "\n".join(lines)
	speaker_label.text = "事件结算回执"
	_clear_event_focus()


func _clear_event_focus() -> void:
	selected_event_id = ""
	selected_event_location_id = ""
	_render_event_choice_buttons([])


func _sync_event_focus_with_world() -> void:
	if selected_event_id.is_empty():
		return
	var current_event: Dictionary = world_sync.find_active_event(selected_event_id)
	if current_event.is_empty():
		_clear_event_focus()


func _memory_has_tag(memory: Dictionary, target_tag: String) -> bool:
	var tags: Array = memory.get("tags", [])
	for tag in tags:
		if str(tag) == target_tag:
			return true
	return false


func _render_portrait(npc: Dictionary) -> void:
	if npc.is_empty():
		portrait_rect.texture = asset_registry.get_portrait("player", selected_expression)
		speaker_label.text = "新来的农场主"
		return
	var npc_id := str(npc.get("id", selected_npc_id))
	var texture: Texture2D = asset_registry.get_portrait(npc_id, selected_expression)
	portrait_rect.texture = texture
	speaker_label.text = "%s · %s" % [npc.get("name", npc_id), npc.get("job", "居民")]


func _select_npc(npc_id: String, clear_event: bool) -> void:
	if clear_event:
		_clear_event_focus()
	selected_npc_id = npc_id
	var npc := _find_npc(npc_id)
	if npc.is_empty():
		return
	selected_location_id = str(npc.get("locationId", selected_location_id))
	_render_portrait(npc)


func _ensure_selected_npc() -> void:
	var selected_npc := _find_npc(selected_npc_id)
	if not selected_npc.is_empty() and asset_registry.has_portrait(selected_npc_id, selected_expression):
		return
	for npc in world_sync.get_npcs():
		var npc_id := str(npc.get("id", ""))
		if asset_registry.has_portrait(npc_id, selected_expression):
			selected_npc_id = npc_id
			return
	selected_npc_id = ""


func _show_selected_npc_hint() -> void:
	var npc := _find_npc(selected_npc_id)
	if npc.is_empty():
		dialogue_label.text = "后端已同步，但当前没有可交互居民。"
		return
	dialogue_label.text = "%s 正在 %s。点击地图小人会直接聊天，也可以使用 marker 快速聊天或送礼。" % [
		npc.get("name", selected_npc_id),
		_get_location_name(str(npc.get("locationId", "unknown")))
	]


func _find_npc(npc_id: String) -> Dictionary:
	for npc in world_sync.get_npcs():
		if str(npc.get("id", "")) == npc_id:
			return npc
	return {}


func _find_location(location_id: String) -> Dictionary:
	for location in world_sync.get_locations():
		if str(location.get("id", "")) == location_id:
			return location
	return {}


func _get_location_name(location_id: String) -> String:
	var location := _find_location(location_id)
	if not location.is_empty():
		return str(location.get("name", location_id))
	return location_id


func _interaction_payload_or_fallback(action_type: String, target_kind: String, target_id: String, fallback: Dictionary) -> Dictionary:
	var interaction: Dictionary = world_sync.find_interaction(action_type, target_kind, target_id)
	var payload := _payload_from_interaction(interaction)
	if not payload.is_empty():
		return payload
	return fallback.duplicate(true)


func _payload_from_interaction(interaction: Dictionary) -> Dictionary:
	if interaction.is_empty():
		return {}
	var payload = interaction.get("payload", {})
	if payload is Dictionary:
		var payload_data: Dictionary = payload
		return payload_data.duplicate(true)
	return {}


func _is_interaction_enabled(interaction: Dictionary) -> bool:
	if interaction.is_empty():
		return false
	return interaction.get("enabled", true) != false


func _is_interaction_enabled_or_missing(interaction: Dictionary) -> bool:
	if interaction.is_empty():
		return true
	return _is_interaction_enabled(interaction)


func _interaction_reason(interaction: Dictionary) -> String:
	var reason := str(interaction.get("reason", ""))
	if reason.is_empty():
		return "后端暂未开放该动作"
	return reason


func _first_gift_item_id() -> String:
	var player: Dictionary = world_sync.get_player()
	var inventory: Array = player.get("inventory", [])
	var fallback_id := ""
	for item in inventory:
		if not (item is Dictionary):
			continue
		if int(item.get("quantity", 0)) <= 0:
			continue
		var tags: Array = item.get("tags", [])
		if not tags.has("gift"):
			continue
		var item_id := str(item.get("id", ""))
		if item_id.is_empty():
			continue
		if item_id != "fresh_turnip":
			return item_id
		if fallback_id.is_empty():
			fallback_id = item_id
	return fallback_id


func _is_action_response_ok(response: Dictionary) -> bool:
	if not response.get("ok", false):
		return false
	var data: Dictionary = response.get("data", {})
	return data.get("ok", false) and data.has("state")


func _response_error(response: Dictionary) -> String:
	if not response.get("ok", false):
		return str(response.get("error", "unknown"))
	var data: Dictionary = response.get("data", {})
	return str(data.get("error", "unknown"))


func _clear_column(column: VBoxContainer) -> void:
	for child in column.get_children():
		child.queue_free()


func _clear_control_children(node: Control) -> void:
	for child in node.get_children():
		child.queue_free()


func _set_status(text: String) -> void:
	if status_label != null:
		status_label.text = text
