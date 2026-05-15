extends Control

const ApiClientScript := preload("res://scripts/api_client.gd")
const AssetRegistryScript := preload("res://scripts/asset_registry.gd")
const WorldSyncScript := preload("res://scripts/world_sync.gd")

var api_client: Node
var asset_registry
var world_sync: Node
var background_rect: TextureRect
var status_label: Label
var player_label: Label
var location_list: VBoxContainer
var npc_list: VBoxContainer
var event_list: VBoxContainer
var portrait_rect: TextureRect
var speaker_label: Label
var dialogue_label: Label
var selected_location_id := "farm"
var selected_npc_id := "orren"
var selected_expression := "neutral"


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
	_build_top_layer()
	_build_dialogue_layer()


func _build_background() -> void:
	background_rect = TextureRect.new()
	background_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	background_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	background_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	background_rect.texture = asset_registry.get_location_background(selected_location_id)
	add_child(background_rect)


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
	event_title.text = "最近事件"
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

	dialogue_label = Label.new()
	dialogue_label.text = "选择一个居民后，这里会显示对应立绘和后端返回的对话。"
	dialogue_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dialogue_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	text_box.add_child(dialogue_label)

	var actions := HBoxContainer.new()
	actions.add_theme_constant_override("separation", 10)
	text_box.add_child(actions)

	var talk_button := Button.new()
	talk_button.text = "聊天"
	talk_button.pressed.connect(_on_talk_pressed)
	actions.add_child(talk_button)

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
	var previous_location_id := selected_location_id
	selected_location_id = location_id
	_set_status("正在移动到 %s ..." % location_id)
	var response = await api_client.post_player_action({"type": "move", "locationId": location_id})
	if not response.get("ok", false):
		selected_location_id = previous_location_id
		_render_world()
		_set_status("移动失败：%s" % response.get("error", "unknown"))
		return
	world_sync.apply_state(response["data"]["state"])
	_render_world()
	_set_status("已到达：%s" % _get_location_name(location_id))


func _on_talk_pressed() -> void:
	if selected_npc_id.is_empty():
		_set_status("请先选择一个居民。")
		return
	_set_status("正在和 %s 聊天..." % selected_npc_id)
	var response = await api_client.post_player_action({
		"type": "talk",
		"targetId": selected_npc_id,
		"locationId": selected_location_id,
		"topic": "first_meeting",
		"message": "你好，我刚搬到晨露农场，想认识一下小镇。"
	})
	if not response.get("ok", false):
		_set_status("对话动作失败：%s" % response.get("error", "unknown"))
		return
	world_sync.apply_state(response["data"]["state"])
	var dialogue: Array = response["data"]["result"].get("dialogue", [])
	if not dialogue.is_empty():
		dialogue_label.text = str(dialogue[0].get("text", "对方微笑着点头。"))
	_render_world()
	_set_status("对话完成：%s" % world_sync.get_clock_label())


func _on_npc_pressed(npc_id: String) -> void:
	selected_npc_id = npc_id
	var npc := _find_npc(npc_id)
	_render_portrait(npc)
	dialogue_label.text = "%s 正在 %s。选择聊天后会请求后端生成回应。" % [
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
	world_sync.apply_state(response["data"])
	selected_location_id = str(response["data"].get("player", {}).get("locationId", selected_location_id))
	_ensure_selected_npc()
	_render_world()
	_set_status("世界状态已同步：%s" % world_sync.get_clock_label())


func _render_world() -> void:
	player_label.text = world_sync.get_player_label()
	_render_background()
	_render_locations()
	_render_npcs()
	_render_events()
	_render_portrait(_find_npc(selected_npc_id))


func _render_background() -> void:
	var texture: Texture2D = asset_registry.get_location_background(selected_location_id)
	if texture == null:
		texture = asset_registry.get_location_background("farm")
	background_rect.texture = texture


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
	var events: Array = world_sync.get_recent_events().duplicate()
	events = events.slice(max(0, events.size() - 5))
	events.reverse()
	if events.is_empty():
		var empty_item := Label.new()
		empty_item.text = "暂无事件"
		event_list.add_child(empty_item)
		return
	for event in events:
		var item := Label.new()
		item.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		var payload: Dictionary = event.get("payload", {})
		item.text = "%s\n%s" % [event.get("type", "event"), payload.get("summary", payload.get("message", payload.get("speech", "")))]
		event_list.add_child(item)


func _render_portrait(npc: Dictionary) -> void:
	if npc.is_empty():
		portrait_rect.texture = asset_registry.get_portrait("player", selected_expression)
		speaker_label.text = "新来的农场主"
		return
	var npc_id := str(npc.get("id", selected_npc_id))
	var texture: Texture2D = asset_registry.get_portrait(npc_id, selected_expression)
	portrait_rect.texture = texture
	speaker_label.text = "%s · %s" % [npc.get("name", npc_id), npc.get("job", "居民")]


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
	dialogue_label.text = "%s 正在 %s。点击聊天后会请求后端生成 first_meeting 回应。" % [
		npc.get("name", selected_npc_id),
		_get_location_name(str(npc.get("locationId", "unknown")))
	]


func _find_npc(npc_id: String) -> Dictionary:
	for npc in world_sync.get_npcs():
		if str(npc.get("id", "")) == npc_id:
			return npc
	return {}


func _get_location_name(location_id: String) -> String:
	for location in world_sync.get_locations():
		if str(location.get("id", "")) == location_id:
			return str(location.get("name", location_id))
	return location_id


func _clear_column(column: VBoxContainer) -> void:
	for child in column.get_children():
		child.queue_free()


func _set_status(text: String) -> void:
	if status_label != null:
		status_label.text = text
