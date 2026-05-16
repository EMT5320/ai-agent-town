---
paths:
  - "AGENTS.md"
  - "CLAUDE.md"
  - "README.md"
  - "docs/**/*.md"
  - "scripts/build_agent_context.py"
---

# Context governance rules

- Treat `AGENTS.md` and `docs/agent_context.md` as the startup route.
- Check each doc frontmatter before using it: `active` is current, `snapshot` is stage evidence.
- Keep `docs/current_status.md` as current facts and `docs/project_vision.md` as long-term direction.
- After context or docs changes, run `npm.cmd run context:check` and `git diff --check`.
