# Onboarding Plugin Revamp — Design

Date: 2026-07-28
Status: **Superseded** by [the project standard](../../project-standard.md) — kept as historical text. Previously: Implemented, partially superseded (Amendment 1).

> **Superseded.** Saddle is now a lean, coding-tool-agnostic project standard (canonical `AGENTS.md`, `CLAUDE.md` pointer, `.hindsight/project.json`). The vault/graphify harness described below is no longer the design. Nothing below was deleted; existing logs, graphs, and memory are preserved as historical evidence.

---

## Amendment 1 — the scratchpad is dead (2026-07-30)

**`.claude/scratchpad.md` was retired 2026-07-29, the day after this spec was approved.**
Everything below that names it as an artifact, a session-discipline step, or a status
check is superseded. The shipped `/saddle` skill was corrected on 2026-07-30; this spec is
annotated rather than rewritten so the original reasoning stays readable.

**Why it died.** It was a second store of "what is true now", and it drifted from the
session log within hours — on the day it was retired, one scratchpad told the next session
to run a script that had been deleted earlier that same day. In four days only 1 of 6
projects ever grew one, while every project had session logs.

**What replaced it.** The vault session log is the only store of current state.
vault-context-loader injects the newest matching `Sessions/` log's **Resumption Prompt**
and **Open Items** at session start; those two sections are the working-memory contract.
Mid-session state goes to `Sessions/SESSION-YYYY-MM-DD-<task-slug>.md` at ~60% context.

**Net effect on this spec:**

| This spec says | Now |
|---|---|
| Phase 4 produces **three** artifacts | **Two** — `CLAUDE.md` and `graphify-out/` |
| Artifact 2 is `.claude/scratchpad.md` | Removed. Its *pointers* moved into `CLAUDE.md`, where they belong — pointers are durable, not per-session state |
| Discipline ends "overwrite scratchpad at session end" | Ends "write the session log's Resumption Prompt + Open Items for the next session" |
| `*status` checks scratchpad freshness | Checks the newest session log carries **both** required sections, **and warns if a stray `.claude/scratchpad.md` still exists** — repos saddled before 2026-07-30 have one |
| "scratchpad is the resume state" | An interrupted onboard writes `Sessions/SESSION-YYYY-MM-DD-saddle-<repo>.md` |

The rest of the design — five phases, the token gate at Phase 3, delegated research landing
as repo docs, graphify-as-recall, prune + brainscan hygiene — is unchanged and shipped.

---

## Purpose

Revamp the `agent-onboarding` plugin (renamed **`onboarding`**) from the retired MemPalace/LightRAG harness stack to Stefan's current stack: vault-pattern memory at repo level, graphify knowledge graphs, locker/skill tool inventory, prune + brainscan hygiene.

**Audience: personal tool.** No public migration path, no stack-agnostic slots. Encodes the current stack directly.

## What Died and Why

| Old | Status | Replacement |
|-----|--------|-------------|
| MemPalace / `fmp` CLI | Dead (2026-04-23) | ~~`.claude/scratchpad.md` +~~ vault session logs *(scratchpad retired 2026-07-29 — Amendment 1)* |
| LightRAG per-agent corpus | Retired from harness recipe | Repo graphify graph (`graphify-out/graph.json`) |
| Per-turn pre/post gates | Dropped | Session discipline (log at milestones, extract with gates, ~~scratchpad overwrite at end~~ → Resumption Prompt + Open Items for the next session) |
| Complex path (orchestrator + expert dirs) | Dropped | Simple only. Delegation decided at spec stage by the writing agent; plugin records available tools, not routing rules |
| `*reflect`, `*review` | Deleted | Nothing to promote without MemPalace |
| `RUNTIME.md` | Deleted | Discipline block lives in generated CLAUDE.md |
| `ONBOARDING_STATE.md` machine | Dropped | Single-sitting flow; ~~scratchpad is the resume state~~ → an interrupted onboard writes a `SESSION-` log (Amendment 1) |
| Harness dirs `core/ memory/ retrieval/ observability/` | Deleted | ~~3~~ **2** artifacts (below) |

## Commands

Two survive: `*onboard`, `*status`.

## `*onboard` — Five Phases

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
- CLIs: relevant installed CLI tools (headroom, rtk, graphify, lb, browser-harness, gh, plus domain-specific ones on PATH)
- MCP servers: connected/configured servers relevant to the intent (check session MCP list + `claude mcp`)
- Match roster + arsenal + CLIs + MCPs against Phase 1 intent → propose shortlist ("these skills / locker agents / CLIs / MCPs look useful for this harness")
- Confirmed picks → **Tools** section in generated CLAUDE.md: name + one-line when-to-use. Pointers only — never duplicate the tool's own docs.
- Gap found ("no locker agent fits") → flag agent worth creating per token-economy rule. Do not default to Claude subagents.

Plugin records *which* tools exist for this repo. *When* to dispatch is decided later, at spec/plan stage, by the writing agent.

### Phase 3 — Research (delegated)

Systematic lookup of what the harness needs to know, executed by locker agents / pi fleet per fleet-routing — not inline.

1. **Derive research questions** from Phase 1 intent + Phase 2 gaps. Standard axes:
   - Domain best practices (patterns, conventions, pitfalls for what this agent/repo does)
   - Dependencies (libraries/services the work will need; current versions, known gotchas)
   - Tooling gaps (useful tools not in locker/arsenal — candidates for new skills or locker agents)
2. **Confirm before dispatch** — present the research plan (questions + which agent gets each) as one batch; user approves/edits. Token spend is gated here.
3. **Dispatch** per fleet-routing skill; announce each dispatch (model, task, why).
4. **Land results as repo docs** — `docs/research/<topic>.md` — so the Phase 4 graphify extract ingests them into the repo graph.
5. **Main-session verification pass** on all delegated output before accepting (delegate-by-default rule).
6. Distilled outcomes: load-bearing facts → generated CLAUDE.md (pointers, not prose dumps); open questions → ~~scratchpad open items~~ **Open Items in the session log**; tooling gaps → flagged as skill/locker-agent candidates.

### Phase 4 — Generate

~~Three~~ **Two** artifacts in the target repo *(Amendment 1)*:

1. **`CLAUDE.md`** — scope/persona + session discipline block + recall formation rules + Pointers + Tools section.
   Discipline block encodes: graphify query before exploring → work → session log to vault at milestones (`Sessions/YYYY-MM-DD-<repo>-<topic>.md`) → graphify extract with gates before final response → ~~overwrite `.claude/scratchpad.md` at session end~~ **write the Resumption Prompt + Open Items for the next session**.
2. ~~**`.claude/scratchpad.md`** — seeded: current state, open items, pointers to relevant vault session logs + wiki notes.~~ **Retired 2026-07-29.** The pointers it carried moved into `CLAUDE.md`; candidates still suggested via smart-connections lookup, user confirms.
3. **`graphify-out/`** — bootstrap extract run during onboard (DeepSeek-backed, global CLAUDE.md recipe, extraction gates enforced). Covers repo source + `docs/research/`. `graphify-out/` gitignored. *(Now artifact 2 of 2.)*

### Phase 5 — Hygiene (automatic)

- `/prune` pass over the generated CLAUDE.md — lean gate before it ships
- `/brainscan` over the repo — verify memory layer wired correctly; fix findings
- Both run at end of onboard; results reported in the completion summary

## `*status`

Checks *(revised by Amendment 1)*: **working memory** — newest vault session log for this repo carries BOTH a `Resumption Prompt` and an `Open Items` section; missing either → warn "session log present but not a working-memory handoff" · `graphify-out/graph.json` present, node count > 0 · gitignore covers `graphify-out/` · CLAUDE.md pointers resolve · **stray scratchpad** — `.claude/scratchpad.md` must NOT exist; present → warn "retired mechanism present; fold into the session log and delete". Offers full `brainscan` rerun for deep audit.

~~Original check: scratchpad exists + fresh (mtime ≥ newest vault session log; older → warn "scratchpad stale, session-end overwrite missed").~~

## Plugin Repo Changes

- **Rename**: plugin `agent-onboarding` → `onboarding` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`; skill dir `skills/agent-onboarding/` → `skills/onboarding/`. GitHub repo/dir rename optional, decided at implementation.
- **Rewrite**: `README.md`, `skills/onboarding/SKILL.md`, `commands/onboard.md`, `commands/status.md`, `CLAUDE.md`, `agents/onboarding-agent.md`
- **Delete**: `commands/reflect.md`, `commands/review.md`, `RUNTIME.md`
- **Keep**: `AGENTS.md` ("See CLAUDE.md"), uncommitted CLAUDE.md slimdown (update command list to two)

## Non-Goals

- No fleet-routing duplication (global CLAUDE.md + fleet-routing skill own that)
- No per-turn gates
- **No repo scratchpad** (`.claude/scratchpad.md`) — retired 2026-07-29, added here 2026-07-30 so it is
  not reintroduced. The session log is the only store of current state; a second one drifts within hours.
- No LightRAG / fmp / MemPalace anywhere
- No public-user migration path
- No multi-expert orchestration structures
