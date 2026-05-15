class_name AssetRegistry
extends Node

const LOCATION_BACKGROUNDS := {
	"farm": "res://assets/locations/farm_day_anime.png",
	"plaza": "res://assets/locations/plaza_day_anime.png",
	"tavern": "res://assets/locations/tavern_evening_anime.png",
}

const EVENT_CGS := {
	"starlight_festival_shortage": "res://assets/cg/starlight_festival_shortage_event.png",
}

const PORTRAITS := {
	"player": {"neutral": "res://assets/characters/player_farmer_neutral.png"},
	"mira": {"neutral": "res://assets/characters/npc_mira_neutral.png"},
	"tomas": {"neutral": "res://assets/characters/npc_tomas_neutral.png"},
	"orren": {"neutral": "res://assets/characters/npc_orren_neutral.png"},
	"lena": {"neutral": "res://assets/characters/npc_lena_neutral.png"},
	"kai": {"neutral": "res://assets/characters/npc_kai_neutral.png"},
	"bram": {"neutral": "res://assets/characters/npc_bram_neutral.png"},
}

# 首版约定的表情键；后续补图时在 PORTRAITS 对应角色下补同名键即可。
const SUPPORTED_PORTRAIT_EXPRESSIONS := ["neutral", "happy", "troubled"]
const PORTRAIT_NEUTRAL_EXPRESSION := "neutral"

var _texture_cache: Dictionary = {}


func has_location_background(location_id: String) -> bool:
	return LOCATION_BACKGROUNDS.has(location_id)


func has_portrait(owner_id: String, expression: String = "neutral") -> bool:
	return not _resolve_portrait_path(owner_id, expression).is_empty()


func has_event_cg(event_id: String) -> bool:
	return EVENT_CGS.has(event_id)


func get_location_background(location_id: String) -> Texture2D:
	return _load_texture(LOCATION_BACKGROUNDS.get(location_id, ""))


func get_event_cg(event_id: String) -> Texture2D:
	return _load_texture(EVENT_CGS.get(event_id, ""))


func get_portrait(owner_id: String, expression: String = "neutral") -> Texture2D:
	return _load_texture(_resolve_portrait_path(owner_id, expression))


func normalize_portrait_expression(expression: String) -> String:
	var normalized := expression.strip_edges().to_lower()
	if SUPPORTED_PORTRAIT_EXPRESSIONS.has(normalized):
		return normalized
	return PORTRAIT_NEUTRAL_EXPRESSION


func _resolve_portrait_path(owner_id: String, expression: String) -> String:
	if not PORTRAITS.has(owner_id):
		return ""

	var variants: Dictionary = PORTRAITS[owner_id]
	var requested_expression := normalize_portrait_expression(expression)
	var requested_path := str(variants.get(requested_expression, ""))
	if not requested_path.is_empty():
		return requested_path

	# 目标表情缺图时回退 neutral，保证主流程可显示。
	return str(variants.get(PORTRAIT_NEUTRAL_EXPRESSION, ""))


func _load_texture(path: String) -> Texture2D:
	if path.is_empty():
		return null
	if _texture_cache.has(path):
		return _texture_cache[path]

	var resource := load(path)
	if resource is Texture2D:
		_texture_cache[path] = resource
		return resource

	var image := Image.new()
	var error := image.load(path)
	if error != OK:
		push_warning("Texture load failed: %s (%s)" % [path, error])
		return null

	var texture := ImageTexture.create_from_image(image)
	_texture_cache[path] = texture
	return texture
