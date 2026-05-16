---
paths:
  - "clients/godot/**"
---

# Godot client rules

- Godot is presentation and interaction glue; do not duplicate backend settlement rules in GDScript.
- Before client changes, read `docs/game_client_environment.md` and `docs/gameplay_system_architecture.md` on demand.
- Use `npm.cmd run client:env` and `npm.cmd run client:run:check` for command validation.
- Real window UX still needs manual `npm.cmd run start` plus `npm.cmd run client:run` verification.
