# Onboarding Plugin Revamp — Design

Date: 2026-07-28
Status: Approved pending user spec review

## Purpose

Revamp the `agent-onboarding` plugin (renamed **`onboarding`**) from the retired MemPalace/LightRAG harness stack to Stefan's current stack: vault-pattern memory at repo level, graphify knowledge graphs, locker/skill tool inventory, prune + brainscan hygiene.

**Audience: personal tool.** No public migration path, no stack-agnostic slots. Encodes the current stack directly.

## What Died and Why

| Old | Status | Replacement |
|-----|--------|-------------|
| MemPalace / `fmp` CLI | Dead (2026-04-23) | `.claude/scratchpad.md` + vault session logs |
| LightRAG per-agent corpus | Retired from harness recipe | Repo graphify graph (`graphify-out/graph.json`) |
| Per-turn pre/post gates | Dropped | Session discipline (log at milestones, extract with gates, scratchpad overwrite at end) |
| Complex path (orchestrator + expert dirs) | Dropped | Simple only. Delegation decided at spec stage by the writing agent; plugin records available tools, not routing rules |
| `*reflect`, `*review` | Deleted | Nothing to promote without MemPalace |
| `RUNTIME.md` | Deleted | Discipline block lives in generated CLAUDE.md |
| `ONBOARDING_STATE.md` machine | Dropped | Single-sitting flow; scratchpad is the resume state |
| Harness dirs `core/ memory/ retrieval/ observability/` | Deleted | 3 artifacts (below) |

## Commands

Two survive: `*onboard`, `*status`.

## `*onboard` — Four Phases

### Phase 1 — Intent

One batched question set:

1. What does this agent/repo do, and for whom? Non-goals? (one sentence each)
2. Intent split: primarily answer/assist, or produce artifacts/execute tasks? (shapes the discipline block)
3. 3–5 typical tasks or queries → become **recall formation rules**: how prompts translate into `graphify query` terms against the repo graph (successor to old QUERY-FORMATION, retargeted)
4. Persona: tone, style, hard format preferences

### Phase 2 — Tool Inventory

Automatic sweep, then user confirms:

- Locker roster: `~/pi-agent-locker/scripts/run-agent.sh --list`
- Skill arsenal: `~/.claude/skills-registry.md`
- Match roster + arsenal against Phase 1 intent → propose shortlist ("these skills / locker agents look useful for this harness")
- Confirmed picks → **Tools** section in generated CLAUDE.md: name + one-line when-to-use. Pointers only — never duplicate the tool's own docs.
- Gap found ("no locker agent fits") → flag agent worth creating per token-economy rule. Do not default to Claude subagents.

Plugin records *which* tools exist for this repo. *When* to dispatch is decided later, at spec/plan stage, by the writing agent.

### Phase 3 — Generate

Three artifacts in the target repo:

1. **`CLAUDE.md`** — scope/persona + session discipline block + recall formation rules + Tools section.
   Discipline block encodes: graphify query before exploring → work → session log to vault at milestones (`Sessions/YYYY-MM-DD-<repo>-<topic>.md`) → graphify extract with gates before final response → overwrite `.claude/scratchpad.md` at session end.
2. **`.claude/scratchpad.md`** — seeded: current state, open items, pointers to relevant vault session logs + wiki notes. Candidates suggested via smart-connections lookup, user confirms.
3. **`graphify-out/`** — bootstrap extract run during onboard (DeepSeek-backed, global CLAUDE.md recipe, extraction gates enforced). `graphify-out/` gitignored.

### Phase 4 — Hygiene (automatic)

- `/prune` pass over the generated CLAUDE.md — lean gate before it ships
- `/brainscan` over the repo — verify memory layer wired correctly; fix findings
- Both run at end of onboard; results reported in the completion summary

## `*status`

Checks: scratchpad exists + fresh (fresh = mtime ≥ newest vault session log for this repo; older → warn "scratchpad stale, session-end overwrite missed") · `graphify-out/graph.json` present, node count > 0 · gitignore covers `graphify-out/` · CLAUDE.md pointers resolve · newest vault session log for this repo. Offers full `brainscan` rerun for deep audit.

## Plugin Repo Changes

- **Rename**: plugin `agent-onboarding` → `onboarding` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`; skill dir `skills/agent-onboarding/` → `skills/onboarding/`. GitHub repo/dir rename optional, decided at implementation.
- **Rewrite**: `README.md`, `skills/onboarding/SKILL.md`, `commands/onboard.md`, `commands/status.md`, `CLAUDE.md`, `agents/onboarding-agent.md`
- **Delete**: `commands/reflect.md`, `commands/review.md`, `RUNTIME.md`
- **Keep**: `AGENTS.md` ("See CLAUDE.md"), uncommitted CLAUDE.md slimdown (update command list to two)

## Non-Goals

- No fleet-routing duplication (global CLAUDE.md + fleet-routing skill own that)
- No per-turn gates
- No LightRAG / fmp / MemPalace anywhere
- No public-user migration path
- No multi-expert orchestration structures
