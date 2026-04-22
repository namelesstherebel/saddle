---
name: agent-onboarding
description: >
  Use when a user wants to set up a new agent — chatbot, assistant, tool, coding agent, or multi-expert system. Triggers: "build me an agent", "set up an agent for X", "onboard this as an agent", "make an agent that does Y". This skill classifies the agent (simple single-harness vs. complex orchestrated), asks targeted questions, then generates a fully configured harness: CLAUDE.md per agent/expert, LightRAG corpus config, MemPalace write taxonomy, query formation rules, and gate protocol. Self-improvement is built into the generated CLAUDE.md — no separate mechanism.
---

# Agent Harness Onboarding

**What this builds:** A harness — the infrastructure that gives a Claude agent durable memory, grounded retrieval, and a self-improving loop.

**Two architectures:**
- **Simple** — one Claude instance, one LightRAG corpus, one MemPalace. For agents that answer questions, assist with a domain, or execute work within a single knowledge area.
- **Complex** — an orchestrator Claude + N expert Claude instances, each with their own corpus and memory. For agents where different work requires genuinely isolated knowledge or memory.

**Self-improvement is the gate pattern.** Every turn: pre-gate retrieves relevant knowledge and memory → Claude responds → post-gate persists new facts and insights. No separate learning mechanism. The agent gets smarter by doing its job.

---

## State Check

Before asking anything:

- `ONBOARDING_STATE.md` exists + `Status: In Progress` → resume from recorded phase, do not re-ask answered questions
- `ONBOARDING_STATE.md` exists + `Status: Complete` → report complete, suggest `*status`
- No state file → start fresh at Phase 1

---

## Phase 1 — Classify

Ask all five questions at once. Do not split across turns.

1. What does this agent do and for whom? (one sentence)
2. Does it primarily answer questions and assist, or produce artifacts and execute tasks?
3. Does it need deep knowledge in more than one genuinely distinct domain? (e.g., both audio DSP *and* JUCE C++ programming — not just "software")
4. Should different areas of work use separate context, tools, and memory so they don't pollute each other?
5. Will this agent coordinate other agents, or be coordinated by one?

**Route:**
- Single domain, Q&A or task execution → **Simple**
- Multi-domain OR work that requires genuinely isolated expertise → **Complex**
- Unclear after five questions → ask one clarifying question, then route

---

## Simple Path — Phase 2S

Single harness. One CLAUDE.md, one LightRAG corpus, one MemPalace.

### Gather

Ask all at once:

1. What documents, sources, or knowledge bases form the domain? (PDFs, websites, API docs, books, internal docs — be specific)
2. What facts about users/context should persist across sessions? (situation, preferences, history, goals)
3. What should the agent derive and remember? (calculations it made, recommendations it gave, conclusions it reached)
4. Persona: name, tone, communication style, what it explicitly does NOT do
5. Does it execute multi-step work in a codebase? (yes → adds execution layer)
6. Describe 3–5 typical queries or tasks — these become retrieval formation rules

### Generate

Produce this structure in the target directory:

```
[agent-name]/
├── CLAUDE.md                     ← harness entry point
├── core/
│   ├── GATES.md                  ← pre/post gate rules
│   └── INVARIANTS.md             ← the five invariants
├── memory/
│   ├── LIGHTRAG.md               ← corpus sources + ingestion checklist
│   ├── MEMPALACE.md              ← what gets saved, when, confidence rules
│   └── WRITE-TAXONOMY.md         ← 5–8 MemPalace categories
├── retrieval/
│   ├── QUERY-FORMATION.md        ← how prompts become retrieval queries
│   └── GROUNDING.md              ← groundedness check rules
└── observability/
    └── HEALTH.md                 ← what to monitor, threshold alerts
```

If multi-step codebase work (question 5 = yes), add:

```
├── execution/
│   ├── EXECUTION-PROFILE.md      ← task types, stopping conditions, rollback rules
│   └── TASK-STATE.md             ← ephemeral task state schema
```

### CLAUDE.md template (simple agent)

```markdown
# [Agent Name]

## Scope
[One sentence: what this agent does and what it explicitly does not do]

## Persona
[Tone, communication style, any hard response format preferences]

## Gate Protocol

**Before every response — pre-gate:**
1. Form retrieval query from the prompt (skip if prompt < 10 chars or low-info: "hey", "thanks", "ok")
2. Search MemPalace: `fmp search "[query]"` — filter out superseded + deprecated items
3. Query LightRAG corpus: `curl -s localhost:[PORT]/query -d '{"query":"[terms]","top_k":5}'` — return raw chunks
4. Validate freshness: if a retrieved MemPalace item has provenance pointing to superseded items, drop it
5. Pass retrieved items + contradictions (if any) to response context

**After every response — post-gate:**
1. Scan prompt for user-asserted facts → save with `fmp add "[fact]" --wing [category]`
2. Scan response for agent-derived insights (chained through 2+ retrieved items) → save as provisional
3. Assign confidence: user facts = user_confirmed; hedged facts = inferred; tested insights = tested; reasoned insights = inferred/provisional
4. Apply supersession: if new write contradicts existing memory, link via supersedes field
5. Persist before emitting output — next turn must see this turn's writes

Gate rules: `core/GATES.md` | Invariants: `core/INVARIANTS.md`

## Memory

**Domain knowledge (LightRAG):** `memory/LIGHTRAG.md`
Corpus is read-only at runtime. Ingest new documents with: `lb ingest [path]` or the configured ingest command.

**Learned context (MemPalace):** `memory/MEMPALACE.md`
Write taxonomy: `memory/WRITE-TAXONOMY.md`
CLI: `fmp search "[query]"` / `fmp add "[fact]" --wing [category]`

## Retrieval
Query formation rules: `retrieval/QUERY-FORMATION.md`
Groundedness rules: `retrieval/GROUNDING.md`

## Observability
Health metrics: `observability/HEALTH.md`

## Never Do Without Asking
[Actions requiring explicit human approval — one per line]
```

### WRITE-TAXONOMY.md template

```markdown
# MemPalace Write Taxonomy — [Agent Name]

5–8 categories. Every MemPalace item belongs to one. Used for retrieval filtering.

## Categories

### [category_1]
What belongs here: [description]
Example facts: [1–2 examples]

### [category_2]
...

### insights
What belongs here: Agent-derived conclusions specific to this user or project.
Confidence rule: always provisional until verified by user or test output.
Example: "[agent calculated X based on Y and Z retrieved items]"
```

Fill in categories from question 2 and 3 of the gather phase. Default set if unclear:
- `user_situation` — facts about the user's context, role, or environment
- `goals` — what the user is trying to achieve
- `preferences` — how the user likes things done
- `history` — past decisions, discussions, or work referenced
- `insights` — agent-derived conclusions

For coding agents: `stack`, `conventions`, `project_history`, `bug_patterns`, `user_preferences`, `insights`

### QUERY-FORMATION.md template

```markdown
# Query Formation Rules — [Agent Name]

## Skip Conditions
Return empty query (no retrieval) when:
- Prompt < 10 characters
- Prompt matches low-info patterns: "hey", "thanks", "ok", "got it", "lol"

## Domain Patterns
Translate common prompt patterns to retrieval terms:

| Prompt contains | → Query terms |
|-----------------|--------------|
| [pattern from typical queries] | [retrieval terms] |
| [pattern] | [terms] |

## Fallback
If no pattern matches: use the raw prompt as a single query term.

## Intent Labels (optional)
[If this agent benefits from intent-aware retrieval, define labels here]
[Example: implement_feature | debug_failure | read_docs | other]
```

Fill the pattern table from question 6 of the gather phase.

### LIGHTRAG.md template

```markdown
# LightRAG Corpus — [Agent Name]

## Sources
[List each document/source with: name, type (PDF/URL/text), location, last ingested date]

## Ingestion Command
[The command to ingest a new document into this agent's LightRAG instance]

## Server
Port: [PORT]
Query endpoint: `POST localhost:[PORT]/query`
Use direct chunk retrieval — NOT aquery(). Return raw chunks to the agent for synthesis.

## What Does NOT Go Here
- Conversation history (→ MemPalace)
- User-specific facts (→ MemPalace)
- Frequently changing data (→ not here, use live tool calls)
```

---

## Complex Path — Phase 2C

Orchestrator + N expert harnesses. Each expert is a full harness with its own CLAUDE.md, LightRAG, and MemPalace.

### Step 1 — Reason the Expert Set

From the agent description, derive the expert domains. Present the proposed list:

> "Based on [description], I'd recommend these experts:
> - **[Expert 1]** — [one-line rationale for why this needs isolated knowledge/memory]
> - **[Expert 2]** — [rationale]
> - ...
>
> An expert only makes sense if it genuinely needs its own corpus and memory — not just for organizational clarity. Does this list match what you're building?"

Wait for confirmation. Add, remove, rename as instructed.

**Expert creation rule:** Create an expert harness only when:
- It needs a corpus the other experts would never query
- Its learned memory would pollute another expert's retrieval if shared
- Its context window should be isolated from other experts' work

### Step 2 — Per-Expert Gather

For each confirmed expert, ask:
1. Corpus sources (what it knows cold)
2. Memory categories (what it learns — 5–8)
3. 3–5 typical queries (retrieval formation)
4. Does it execute multi-step codebase work?

### Step 3 — Orchestrator Gather

1. Authority boundaries: what can the orchestrator decide directly vs. must delegate?
2. Result format: how do experts return results to the orchestrator?
3. Topology: pipeline (sequential) / fan-out (parallel) / dynamic routing?

### Generate

```
[agent-name]/
├── CLAUDE.md                         ← orchestrator: routing + authority
├── core/
│   ├── GATES.md
│   └── INVARIANTS.md
├── subagents/
│   ├── ORCHESTRATOR.md               ← routing rules, delegation logic
│   ├── TOPOLOGY.md                   ← expert list + connection pattern
│   ├── AUTHORITY.md                  ← what orchestrator decides vs. delegates
│   └── experts/
│       ├── [expert-1]/
│       │   ├── CLAUDE.md             ← expert persona + gate protocol
│       │   ├── memory/
│       │   │   ├── LIGHTRAG.md
│       │   │   ├── MEMPALACE.md
│       │   │   └── WRITE-TAXONOMY.md
│       │   └── retrieval/
│       │       ├── QUERY-FORMATION.md
│       │       └── GROUNDING.md
│       └── [expert-N]/
│           └── [same structure]
└── observability/
    └── HEALTH.md
```

Each expert CLAUDE.md uses the same template as the simple path, scoped to that expert's domain.

### Orchestrator CLAUDE.md template

```markdown
# [Agent Name] — Orchestrator

## Role
Route tasks to the correct expert. Synthesize results into a final response. Do not absorb expert-level domain knowledge — delegate it.

## Experts
[List each expert with: name, domain, what it's responsible for]

## Routing Rules
[How to decide which expert handles a task]
[If multiple experts are needed: how to sequence or fan-out]

## Authority
What I decide directly: [list]
What I always delegate: [list]
Full authority map: `subagents/AUTHORITY.md`

## Result Packets
Experts return results as: [format — JSON object / structured markdown / etc.]
I synthesize packets into the final response — I do not pass raw transcripts.

## Topology
`subagents/TOPOLOGY.md`
```

---

## Self-Improvement Protocol

The gate pattern IS the self-improvement. No additional mechanism.

**Turn-by-turn (post-gate):**
- User facts → MemPalace immediately, `status: active`
- Agent insights (backed by 2+ retrieved items) → MemPalace as `provisional`
- Provisional items promoted when: user confirms, test verifies, or observation supports
- Superseded items stay in store, filtered from default retrieval — audit trail preserved

**LightRAG growth:**
- New domain documents → ingest via configured command
- Re-ingest when corpus changes significantly
- Provenance hashes in derived MemPalace items auto-detect stale derivations on next retrieval

**What the agent never does:**
- Modify its own CLAUDE.md
- Modify GATES.md or INVARIANTS.md
- Persist in-session working state to MemPalace

---

## State Management

Write or update `ONBOARDING_STATE.md` at the end of any incomplete session:

```markdown
# Onboarding State

Status: In Progress / Complete
Last updated: [date]
Agent type: Simple / Complex
Current phase: [phase]
Experts confirmed: [list — complex only]
Next action: [exactly what to do on resume]
Open questions: [anything unresolved]
```

On session start: read this file before asking anything.

---

## Completion

Onboarding is complete when:
- All files generated and confirmed by user
- `ONBOARDING_STATE.md` updated to `Status: Complete`

After completion, `*status` verifies the harness is healthy.
