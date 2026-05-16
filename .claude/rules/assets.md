---
paths:
  - "assets/**"
  - "clients/godot/assets/**"
  - "docs/art_direction.md"
  - "docs/asset_generation_prompts.md"
  - "docs/map_sprite_*.md"
---

# Asset pipeline rules

- Register new assets in `assets/manifests/asset_manifest.json` with source, usage, status, prompt reference, and license note.
- Do not promote map sprites to `source_selected` before Godot real-window review.
- Keep prompt-only or unverified material out of final-source status.
- Validate asset changes with `npm.cmd run asset:check`; use `npm.cmd run check` before handoff when code paths are affected.
