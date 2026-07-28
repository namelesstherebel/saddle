# saddle

Rig a repo with a vault-pattern harness. Personal skill — not distributed.

v2 replaces the retired MemPalace/LightRAG stack — repo-level vault memory, graphify graphs, locker tool inventory.

## Use

`/saddle` in any repo — the skill lives at `skills/saddle/SKILL.md`, symlinked into `~/.claude/skills/saddle`.

- `/saddle` — five phases: Intent → Tool inventory (locker/skills/CLIs/MCPs) → Research (delegated to fleet, token-gated) → Generate → Hygiene (auto `/prune` + `/brainscan`)
- `/saddle status` — harness health: scratchpad freshness, graph node count, gitignore coverage, pointer resolution, newest vault session log

## What Gets Generated

- **`CLAUDE.md`** — scope/persona, session discipline block (graphify query before exploring → work → vault session log at milestones → gated graphify extract → scratchpad overwrite at session end), recall formation rules, Tools section. Pointers, never duplicated docs.
- **`.claude/scratchpad.md`** — seeded current state, open items, pointers to relevant vault session logs and wiki notes.
- **`graphify-out/`** — bootstrap knowledge graph over repo source + `docs/research/`. Gitignored.

## Stack Assumptions

- graphify CLI
- `~/pi-agent-locker`
- the RAG vault with `Sessions/` logs
- smart-connections MCP
- `/prune` and `/brainscan` skills

## License

MIT — Copyright (c) 2026 Stefan Kuczynski
