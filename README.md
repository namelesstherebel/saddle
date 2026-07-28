# onboarding

Turn a repo into a vault-pattern harness.

v2 replaces the retired MemPalace/LightRAG stack — repo-level vault memory, graphify graphs, locker tool inventory.

---

## Quick Install

```bash
claude plugin marketplace add namelesstherebel/agent-onboarding && claude plugin install onboarding
```

Then open Claude Code in your project and type `*onboard`.

---

## What It Does

`*onboard` runs five phases:

1. **Intent** — one batched question set: what the repo does and for whom, non-goals, answer-vs-produce intent split, 3–5 typical tasks, persona. The tasks become recall formation rules.
2. **Tool inventory** — automatic sweep of the locker roster, skills registry, CLIs, and MCP servers. Matches them against intent, proposes a shortlist, user confirms. Records which tools exist — not when to dispatch.
3. **Research (delegated)** — derives research questions (domain practices, dependencies, tooling gaps), presents the plan as one batch for approval, dispatches to locker agents / pi fleet, lands results in `docs/research/`, verifies all delegated output in the main session.
4. **Generate** — writes the three harness artifacts (below) into the target repo.
5. **Hygiene (automatic)** — `/prune` the generated CLAUDE.md, `/brainscan` the repo, fix findings, report results in the completion summary.

---

## What Gets Generated

- **`CLAUDE.md`** — scope/persona, session discipline block (graphify query before exploring → work → vault session log at milestones → graphify extract with gates before final response → scratchpad overwrite at session end), recall formation rules, Tools section. Pointers to tools and logs — never duplicated docs.
- **`.claude/scratchpad.md`** — seeded current state, open items, pointers to relevant vault session logs and wiki notes (candidates via smart-connections lookup, user confirms).
- **`graphify-out/`** — bootstrap knowledge graph over repo source + `docs/research/`. Gitignored.

---

## Commands

- `*onboard` — run the five phases, generate the harness.
- `*status` — harness health: scratchpad freshness, graph node count, gitignore coverage, pointer resolution, newest vault session log.

---

## Stack Assumptions

Personal tool. Assumes present:

- graphify CLI
- `~/pi-agent-locker`
- the RAG vault with `Sessions/` logs
- smart-connections MCP
- `/prune` and `/brainscan` skills

No migration path from v1.

---

## License

MIT — Copyright (c) 2026 Stefan Kuczynski
