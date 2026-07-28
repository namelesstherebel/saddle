---
name: onboarding
description: >
  Use when a user wants to turn a repo into a vault-pattern agent harness. Triggers: "onboard this repo",
  "build a harness for this repo", "set up this repo as an agent", "*onboard". Runs five phases — intent,
  tool inventory, delegated research, generate, hygiene — and produces three artifacts in the target repo:
  a `CLAUDE.md` (scope, persona, session discipline, recall formation rules, tools), a seeded
  `.claude/scratchpad.md` (working memory), and a bootstrapped `graphify-out/` repo knowledge graph.
---

# Repo Harness Onboarding

**What this builds:** a repo that an agent can pick up cold — a graph to query instead of exploring, a
scratchpad holding current state, a vault write habit, and a named tool inventory.

**Pointer discipline is the rule.** Generated files point at the global CLAUDE.md recipes and the
`fleet-routing` skill. They never copy commands, model tables, or tool docs inline. Copied snapshots go
stale and silently reintroduce retired model names.

Single sitting, five phases, one stop for approval (Phase 3).

---

## Phase 1 — Intent

Ask all four at once. Do not split across turns.

1. What does this agent/repo do, and for whom? Non-goals? (one sentence each)
2. Primarily answer/assist, or produce artifacts/execute tasks? (shapes the discipline block)
3. 3–5 typical tasks or queries you'll bring to it.
4. Persona: tone, style, hard format preferences.

Answer 3 is load-bearing. Each typical task becomes a row in the **recall formation** table: a prompt
pattern on the left, the `graphify query` terms to run against the repo graph on the right. Write the terms
as the vocabulary that actually appears in this repo's code and docs, not as a restatement of the prompt.

---

## Phase 2 — Tool Inventory

Four sweeps, automatic, before proposing anything:

- **Locker roster** — `~/pi-agent-locker/scripts/run-agent.sh --list`
- **Skill arsenal** — `~/.claude/skills-registry.md`
- **CLIs on PATH** — headroom, rtk, graphify, lb, browser-harness, gh, plus anything domain-specific this
  repo's stack implies
- **MCP servers** — the session's connected server list plus `claude mcp`

Match all four against Phase 1 intent. Propose a shortlist: "these skills / locker agents / CLIs / MCPs look
useful for this harness." User confirms, edits, or cuts.

Confirmed picks become the **Tools** section of the generated CLAUDE.md: name + one line of when-to-use.
Pointers only — never duplicate a tool's own docs into the harness.

Gap found ("nothing in the locker fits this") → flag it as *worth creating a locker agent or skill*, and
carry it into Phase 3 as a research question. Never resolve a gap by defaulting to a Claude subagent.

This phase records *which* tools exist for this repo. *When* to dispatch is decided later, at spec/plan
stage, by the writing agent.

---

## Phase 3 — Research (delegated)

Derive questions from Phase 1 intent + Phase 2 gaps, across three axes:

- **Domain best practices** — patterns, conventions, pitfalls for what this repo does
- **Dependencies** — libraries/services the work needs; current versions, known gotchas
- **Tooling gaps** — useful tools absent from locker/arsenal; candidates for new skills or locker agents

**Present the plan as ONE batch and STOP.** Question + assigned agent for each, in a single message. Wait
for approval or edits. This is the token gate — nothing dispatches before it clears.

Dispatch per the `fleet-routing` skill (invoke it; do not restate its model tables here). Announce each
dispatch in one visible line: model, task, why.

### Dispatch prompt template

````
<task>
[Single concern. One question, one deliverable. Do not bundle.]
</task>

<constraints>
- Where a fact is unknown or unavailable, write an em dash. Never invent a version number, API,
  benchmark, or citation.
- No preamble, no summary, no "here's what I found" wrapper. Output the template and nothing else.
- Write your output to `docs/research/<topic>.md` using your write tool. Do not return it on stdout.
</constraints>

<output_template>
[Exact section headings and field names, placed at the very END of the prompt.]
</output_template>
````

**Verify every result in the main session** before accepting it: open the written file, check claims that
carry weight, check the em dashes are honest gaps and not silent omissions. Delegated output always gets a
main-session pass.

Distill:

- load-bearing facts → pointers in the generated CLAUDE.md (never prose dumps)
- open questions → Open Items in the scratchpad
- tooling gaps → named skill / locker-agent candidates in the completion summary

`docs/research/` stays in the repo so the Phase 4 extract ingests it into the graph.

---

## Phase 4 — Generate

Three artifacts.

### (a) `CLAUDE.md`

````markdown
# [Repo Name]

## Scope
[One sentence: what this repo/agent does. One sentence: what it explicitly does not do.]

## Persona
[Tone, style, hard format preferences from Phase 1.]

## Session Discipline

1. **Query before exploring.** `graphify query "<terms>" --graph graphify-out/graph.json` — one
   budget-capped query beats an exploration budget. Read `.claude/scratchpad.md` first for current state.
2. **Work.** Delegate execution per the `fleet-routing` skill — invoke the skill, do not guess models.
3. **Log at milestones.** Write `Sessions/YYYY-MM-DD-[repo]-<topic>.md` to the RAG vault when a milestone
   lands or the session winds down. Sections and Dispatch Ledger rules: global CLAUDE.md § RAG Vault Writes.
4. **Extract before the final response.** Run the extract command from global CLAUDE.md § RAG Vault Writes —
   copy it from that file at run time, never from a snapshot pasted here or injected into context. Enforce
   its gates: ≥1 `re-extracted`, node count rising, note reachable. Freshness is not proof of extraction.
5. **Overwrite `.claude/scratchpad.md` at session end.** Scratchpad is RAM; session logs + graph are disk.

## Recall Formation

| Prompt pattern | → `graphify query` terms |
|----------------|--------------------------|
| [pattern from Phase 1 task 1] | [repo-vocabulary terms] |
| [pattern] | [terms] |

No pattern matches → query the raw prompt as one term, then explore.

## Tools

- **[name]** — [one line: when to reach for it]
- **[name]** — [when to reach for it]

Pointers only. Each tool's own docs are the reference; read them on demand.

## Never Do Without Asking
[One action per line.]
````

### (b) `.claude/scratchpad.md`

Working memory. The vault-context-loader hook injects it verbatim at session start.

````markdown
# Scratchpad — [Repo Name]

Last updated: [date]

## Current State
[Where the work stands right now. Overwrite this every session end — it is not a log.]

## Open Items
- [ ] [Unresolved question or next action]

## Pointers
- Vault session logs: `Sessions/[...]`
- Wiki notes: `[...]`
````

Suggest pointer candidates with `mcp__smart-connections__lookup` against the repo's subject matter; Read the
hits before proposing them. User confirms which stay.

### (c) `graphify-out/`

Bootstrap extract per global CLAUDE.md § Repo Knowledge Graphs — DeepSeek-backed, run the command from that
file. Cover repo source plus `docs/research/`. Enforce the extraction gates: ≥1 `re-extracted` and a rising
node count; a `wrote graph.json` line alone proves nothing. If a run reports `0 docs changed` after a
failure, evict the poisoned `manifest.json` entries per the same section, then re-run.

Start it with Bash `run_in_background` and wait for the harness completion notification. Do not poll, do not
read liveness from `ps` or an empty log, and never start a second extract alongside a running one.

Add `graphify-out/` to `.gitignore`.

---

## Phase 5 — Hygiene

Automatic. Do not ask.

1. `/prune` over the generated `CLAUDE.md` — lean gate before it ships.
2. `/brainscan` over the repo — verifies the memory layer is wired.

Fix what either turns up. Report both results in the completion summary.

---

## Resume

No state file. If onboarding is interrupted, progress lives in `.claude/scratchpad.md` — write what's done
and what's next into Current State and Open Items before stopping. The next `*onboard` reads the scratchpad
and continues from there; it does not re-ask answered questions.

---

## Completion

Done when:

- `CLAUDE.md`, `.claude/scratchpad.md`, and `graphify-out/graph.json` all exist, the graph has nodes, and
  `graphify-out/` is gitignored
- `/prune` and `/brainscan` have run and their findings are fixed
- The summary reports both hygiene results plus any skill / locker-agent candidates found in Phases 2–3

`*status` verifies harness health afterward.
