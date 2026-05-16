---
paths:
  - "backend/**/*.py"
  - "scripts/*.py"
---

# Backend rules

- Backend owns authoritative world state; Godot submits actions and displays results.
- Preserve `RuleBasedProvider` fallback when changing LLM, Director, Runtime, or Skill code.
- For Director or Event Skill work, read `docs/agentic_game_design.md` and `docs/vertical_slice_spec.md` on demand.
- Validate backend changes with the smallest relevant command first, then `npm.cmd run smoke` or `npm.cmd run check`.
