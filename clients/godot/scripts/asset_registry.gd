class_name AssetRegistry
extends Node

const LOCATION_BACKGROUNDS := {
	"farm": "res://assets/locations/farm_day_anime.png",
	"plaza": "res://assets/locations/plaza_day_anime.png",
	"tavern": "res://assets/locations/tavern_evening_anime.png",
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

var _texture_cache: Dictionary = {}


func has_location_background(location_id: String) -> bool:
	return LOCATION_BACKGROUNDS.has(location_id)


func has_portrait(owner_id: String, expression: String = "neutral") -> bool:
	if not PORTRAITS.has(owner_id):
		return false
	return PORTRAITS[owner_id].has(expression) or PORTRAITS[owner_id].has("neutral")


func get_location_background(location_id: String) -> Texture2D:
	return _load_texture(LOCATION_BACKGROUNDS.get(location_id, ""))


func get_portrait(owner_id: String, expression: String = "neutral") -> Texture2D:
	if not PORTRAITS.has(owner_id):
		return null
	var variants: Dictionary = PORTRAITS[owner_id]
	return _load_texture(variants.get(expression, variants.get("neutral", "")))


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
