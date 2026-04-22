# Agent Runtime

**Installed by:** Agent Onboarding Workflow

This file signals that onboarding is complete and the harness is active. Read at the start of every session.

---

## What the Harness Does

The agent improves by doing its job. No separate learning mechanism.

**Every turn:**
- **Pre-gate** — retrieve relevant knowledge (LightRAG) and memory (MemPalace), validate freshness, surface contradictions
- **Post-gate** — extract facts and insights from the exchange, assign confidence, persist to MemPalace before emitting output

**Over time:**
- MemPalace accumulates what the agent learns about users and context
- LightRAG grows when new domain documents are ingested
- Provisional insights get promoted as they're verified; stale facts get superseded

That's the loop. No friction queue. No proposal system.

---

## Session Start Protocol

1. Read `CLAUDE.md` — loads persona, gate protocol, memory pointers
2. Pre-gate runs automatically before first response

---

## Commands

**`*reflect`** — Review MemPalace health: surface provisional items, stale derivations, and corpus gaps. Read `commands/reflect.md`.

**`*review`** — Process provisional MemPalace items: promote confirmed insights, deprecate stale ones. Read `commands/review.md`.

**`*status`** — Report harness health: memory store stats, LightRAG corpus status, gate health. Read `commands/status.md`.

---

## What the Runtime Does NOT Do

- Track friction or generate improvement proposals
- Auto-modify CLAUDE.md or any harness config file
- Persist in-session working state to MemPalace
