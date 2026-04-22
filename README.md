# agent-onboarding

Build a harness for any Claude agent — single expert or multi-expert orchestrated system.

---

## Quick Install

```bash
claude plugin marketplace add namelesstherebel/agent-onboarding && claude plugin install agent-onboarding
```

Then open Claude Code in your project and type `*onboard`.

---

## What It Does

The plugin classifies your agent and builds a **harness** — the infrastructure that gives it durable memory, grounded retrieval, and a built-in improvement loop.

**Two architectures:**

- **Simple** — one Claude instance with a LightRAG corpus (what it knows cold) and a MemPalace memory store (what it learns). For chatbots, assistants, and single-domain agents.
- **Complex** — an orchestrator Claude plus N expert Claude instances, each with their own isolated corpus and memory. For agents that require genuinely different domain expertise working together.

**Self-improvement is the gate pattern.** Every turn: pre-gate retrieves relevant knowledge and memory → Claude responds → post-gate persists new facts and insights. The agent improves by doing its job.

---

## How It Works

**`*onboard`** — Classify and build. Five questions determine the architecture. Then targeted questions fill in the domain knowledge (LightRAG corpus), memory categories (MemPalace write taxonomy), and retrieval rules. Output is a directory of harness files the agent loads at runtime.

**`*reflect`** — Review MemPalace health: surface provisional insights, stale derivations, corpus gaps.

**`*review`** — Process provisional MemPalace items: promote confirmed insights to active, deprecate stale ones.

**`*status`** — Harness health report: memory stats, LightRAG status, gate health.

---

## What Gets Generated

```
[agent-name]/
├── CLAUDE.md                     ← harness entry point: persona + gate protocol + memory pointers
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
    └── HEALTH.md                 ← health metrics and alert thresholds
```

Complex agents also get:

```
└── subagents/
    ├── ORCHESTRATOR.md           ← routing rules, authority boundaries
    ├── TOPOLOGY.md               ← expert list + connection pattern
    └── experts/
        └── [expert-name]/        ← same structure as above, per expert
```

---

## Install & Update

**Install:**

```bash
claude plugin marketplace add namelesstherebel/agent-onboarding && claude plugin install agent-onboarding
```

**Update:**

```bash
claude plugin marketplace remove agent-onboarding
claude plugin marketplace add namelesstherebel/agent-onboarding
claude plugin install agent-onboarding
```

**Verify:**

```bash
claude plugin list
```

`agent-onboarding` should appear with status `installed`.

---

## Memory Architecture

The harness uses two stores:

| Store | Purpose | Characteristics |
|-------|---------|-----------------|
| **LightRAG** | Domain knowledge the agent knows cold | Static, ingested once, queried via direct chunk retrieval |
| **MemPalace** | What the agent learns about users and context | Dynamic, grows every turn, scoped per agent |

Every MemPalace item carries metadata: timestamp, source, confidence, status, and provenance for derived insights. Superseded items stay in the store for audit — they're just filtered from default retrieval.

---

## License

MIT — Copyright (c) 2026 Stefan Kuczynski
