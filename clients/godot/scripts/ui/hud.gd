class_name WorldHud
extends CanvasLayer

var _clock_label: Label
var _status_label: Label


func _ready() -> void:
	# 用最小控件展示世界时钟、暂停和倍速按钮。
	var panel := PanelContainer.new()
	panel.name = "HudPanel"
	panel.offset_left = 16.0
	panel.offset_top = 16.0
	panel.offset_right = 330.0
	panel.offset_bottom = 170.0
	add_child(panel)

	var root := VBoxContainer.new()
	root.name = "HudVBox"
	panel.add_child(root)

	_clock_label = Label.new()
	_clock_label.text = "Clock: --"
	root.add_child(_clock_label)

	_status_label = Label.new()
	_status_label.text = "Status: Ready"
	root.add_child(_status_label)

	var speed_row := HBoxContainer.new()
	root.add_child(speed_row)

	var pause_btn := Button.new()
	pause_btn.text = "Pause/Resume"
	pause_btn.pressed.connect(_on_pause_pressed)
	speed_row.add_child(pause_btn)

	for speed_value in [1.0, 2.0, 4.0]:
		var btn := Button.new()
		btn.text = "%sx" % int(speed_value)
		btn.pressed.connect(_on_speed_pressed.bind(speed_value))
		speed_row.add_child(btn)

	_connect_bus_signals()
	_connect_clock_signals()


func _connect_bus_signals() -> void:
	if not has_node("/root/EventBusService"):
		return
	var event_bus := get_node("/root/EventBusService") as EventBus
	if event_bus == null:
		return
	if not event_bus.tick_clock_updated.is_connected(_on_tick_clock_updated):
		event_bus.tick_clock_updated.connect(_on_tick_clock_updated)


func _connect_clock_signals() -> void:
	if not has_node("/root/WorldClockService"):
		return
	var world_clock := get_node("/root/WorldClockService") as WorldClock
	if world_clock == null:
		return
	if not world_clock.paused_changed.is_connected(_on_pause_changed):
		world_clock.paused_changed.connect(_on_pause_changed)
	if not world_clock.speed_changed.is_connected(_on_speed_changed):
		world_clock.speed_changed.connect(_on_speed_changed)
	if not world_clock.tick_failed.is_connected(_on_tick_failed):
		world_clock.tick_failed.connect(_on_tick_failed)


func _on_pause_pressed() -> void:
	if has_node("/root/WorldClockService"):
		var world_clock := get_node("/root/WorldClockService") as WorldClock
		if world_clock != null:
			world_clock.toggle_paused()


func _on_speed_pressed(next_speed: float) -> void:
	if has_node("/root/WorldClockService"):
		var world_clock := get_node("/root/WorldClockService") as WorldClock
		if world_clock != null:
			world_clock.set_speed(next_speed)


func _on_tick_clock_updated(clock: Dictionary) -> void:
	var day := int(clock.get("day", 1))
	var hour := int(clock.get("hour", 0))
	var minute := int(clock.get("minute", 0))
	var phase := str(clock.get("phase", "unknown"))
	_clock_label.text = "Clock: Day %d %02d:%02d %s" % [day, hour, minute, phase]


func _on_pause_changed(is_paused: bool) -> void:
	_status_label.text = "Status: %s" % ("Paused" if is_paused else "Running")


func _on_speed_changed(new_speed: float) -> void:
	_status_label.text = "Status: %.1fx" % new_speed


func _on_tick_failed(error_message: String) -> void:
	_status_label.text = "Status: %s" % error_message
