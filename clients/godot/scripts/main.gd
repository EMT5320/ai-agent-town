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
	world_sync.apply_state(response["data"]["state"])
	_render_world()
	_set_status("已到达：%s" % _get_location_name(location_id))


func _on_talk_pressed() -> void:
	if selected_npc_id.is_empty():
		_set_status("请先选择一个居民。")
		return
	_clear_event_focus()
	_set_status("正在和 %s 聊天..." % selected_npc_id)
	var response = await api_client.post_player_action({
		"type": "talk",
		"targetId": selected_npc_id,
		"locationId": selected_location_id,
		"topic": "first_meeting",
		"message": "你好，我刚搬到晨露农场，想认识一下小镇。"
	})
	if not _is_action_response_ok(response):
		_set_status("对话动作失败：%s" % _response_error(response))
		return
	world_sync.apply_state(response["data"]["state"])
	var dialogue: Array = response["data"]["result"].get("dialogue", [])
	if not dialogue.is_empty():
		dialogue_label.text = str(dialogue[0].get("text", "对方微笑着点头。"))
	_render_world()
	_set_status("对话完成：%s" % world_sync.get_clock_label())


func _on_inspect_event_pressed(event_id: String, event_location: String) -> void:
	selected_event_id = event_id
	selected_event_location_id = event_location
	_set_status("正在查看事件：%s ..." % event_id)
	# 事件查看只通过后端 inspect 获取可见信息，客户端不复制事件规则。
	var response = await api_client.post_player_action({
		"type": "inspect",
		"eventId": event_id,
		"locationId": event_location,
	})
	if not _is_action_response_ok(response):
		_set_status("查看事件失败：%s" % _response_error(response))
		return
	world_sync.apply_state(response["data"]["state"])
	var inspect_payload: Dictionary = response["data"].get("result", {}).get("inspect", {})
	_render_world()
	_render_inspect_result(inspect_payload)
	_set_status("已获取事件线索：%s" % inspect_payload.get("title", event_id))


func _on_attend_event_choice_pressed(event_id: String, event_location: String, choice_id: String) -> void:
	_set_status("正在提交事件选择：%s ..." % choice_id)
	# 玩家选择统一提交后端，事件结算、关系变化和记忆写入都由 Runtime 返回。
	var response = await api_client.post_player_action({
		"type": "attend_event",
		"eventId": event_id,
		"choice": choice_id,
		"locationId": event_location,
	})
	if not _is_action_response_ok(response):
		_set_status("事件结算失败：%s" % _response_error(response))
		return
	world_sync.apply_state(response["data"]["state"])
	_render_world()
	_render_attend_result(response["data"].get("result", {}))
	_set_status("事件已提交：%s" % choice_id)


func _on_npc_pressed(npc_id: String) -> void:
	_clear_event_focus()
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
	_sync_event_focus_with_world()
	_render_world()
	_set_status("世界状态已同步：%s" % world_sync.get_clock_label())


func _render_world() -> void:
	player_label.text = world_sync.get_player_label()
	_render_background()
	_render_locations()
	_render_npcs()
	_render_events()
	_render_focus_visual()


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
		var button := Button.new()
		button.text = choice_label
		button.disabled = choice_id.is_empty()
		button.pressed.connect(_on_attend_event_choice_pressed.bind(selected_event_id, selected_event_location_id, choice_id))
		event_choice_list.add_child(button)


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


func _set_status(text: String) -> void:
	if status_label != null:
		status_label.text = text
