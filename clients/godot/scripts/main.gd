extends Control

var api_client: ApiClient
var world_sync: WorldSync
var status_label: Label
var player_label: Label
var location_list: VBoxContainer
var npc_list: VBoxContainer
var event_list: VBoxContainer


func _ready() -> void:
	api_client = ApiClient.new()
	world_sync = WorldSync.new()
	add_child(api_client)
	add_child(world_sync)
	_build_layout()
	await _refresh_world()


func _build_layout() -> void:
	# 当前阶段用文本面板验证数据契约，后续再替换为正式地图和角色节点。
	var margin := MarginContainer.new()
	margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 24)
	margin.add_theme_constant_override("margin_right", 24)
	margin.add_theme_constant_override("margin_top", 18)
	margin.add_theme_constant_override("margin_bottom", 18)
	add_child(margin)

	var root := VBoxContainer.new()
	root.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.size_flags_vertical = Control.SIZE_EXPAND_FILL
	margin.add_child(root)

	var title := Label.new()
	title.text = "Agent Valley · Godot 客户端骨架"
	title.add_theme_font_size_override("font_size", 26)
	root.add_child(title)

	status_label = Label.new()
	status_label.text = "等待同步..."
	root.add_child(status_label)

	player_label = Label.new()
	player_label.text = "玩家状态等待同步..."
	root.add_child(player_label)

	var actions := HBoxContainer.new()
	root.add_child(actions)

	var refresh_button := Button.new()
	refresh_button.text = "刷新世界状态"
	refresh_button.pressed.connect(_on_refresh_pressed)
	actions.add_child(refresh_button)

	var talk_button := Button.new()
	talk_button.text = "向奥伦打招呼"
	talk_button.pressed.connect(_on_test_talk_pressed)
	actions.add_child(talk_button)

	var columns := HBoxContainer.new()
	columns.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(columns)

	location_list = _create_column(columns, "地点")
	npc_list = _create_column(columns, "NPC")
	event_list = _create_column(columns, "最近事件")


func _create_column(parent: HBoxContainer, title_text: String) -> VBoxContainer:
	var panel := PanelContainer.new()
	panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	parent.add_child(panel)

	var box := VBoxContainer.new()
	box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	box.size_flags_vertical = Control.SIZE_EXPAND_FILL
	panel.add_child(box)

	var title := Label.new()
	title.text = title_text
	title.add_theme_font_size_override("font_size", 18)
	box.add_child(title)
	return box


func _on_refresh_pressed() -> void:
	await _refresh_world()


func _on_test_talk_pressed() -> void:
	_set_status("正在提交玩家对话动作...")
	var response := await api_client.post_player_action({
		"type": "talk",
		"targetId": "orren",
		"locationId": "plaza",
		"topic": "first_meeting",
		"message": "你好，我刚搬到晨露农场。"
	})
	if not response.get("ok", false):
		_set_status("对话动作失败：%s" % response.get("error", "unknown"))
		return
	world_sync.apply_state(response["data"]["state"])
	_render_world()
	_set_status("对话动作完成：%s" % world_sync.get_clock_label())


func _refresh_world() -> void:
	_set_status("正在读取 /api/world/state ...")
	var response := await api_client.get_world_state()
	if not response.get("ok", false):
		_set_status("世界状态读取失败：%s" % response.get("error", "unknown"))
		return
	world_sync.apply_state(response["data"])
	_render_world()
	_set_status("世界状态已同步：%s" % world_sync.get_clock_label())


func _render_world() -> void:
	player_label.text = world_sync.get_player_label()
	_render_locations()
	_render_npcs()
	_render_events()


func _render_locations() -> void:
	_clear_column(location_list)
	for location in world_sync.get_locations():
		var item := Label.new()
		item.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		item.text = "%s [%s]\n%s" % [location.get("name", location.get("id", "unknown")), location.get("id", "unknown"), location.get("description", "")]
		location_list.add_child(item)


func _render_npcs() -> void:
	_clear_column(npc_list)
	for npc in world_sync.get_npcs():
		var item := Label.new()
		item.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		var status: Dictionary = npc.get("status", {})
		item.text = "%s · %s\n位置：%s  心情：%s  精力：%s" % [
			npc.get("name", npc.get("id", "unknown")),
			npc.get("job", "居民"),
			npc.get("locationId", "unknown"),
			status.get("mood", "-"),
			status.get("energy", "-")
		]
		npc_list.add_child(item)


func _render_events() -> void:
	_clear_column(event_list)
	for event in world_sync.get_recent_events():
		var item := Label.new()
		item.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		var payload: Dictionary = event.get("payload", {})
		item.text = "%s\n%s" % [event.get("type", "event"), payload.get("summary", payload.get("message", payload.get("speech", "")))]
		event_list.add_child(item)


func _clear_column(column: VBoxContainer) -> void:
	# 保留第一行标题，清理旧数据行。
	for index in range(column.get_child_count() - 1, 0, -1):
		column.get_child(index).queue_free()


func _set_status(text: String) -> void:
	if status_label != null:
		status_label.text = text
