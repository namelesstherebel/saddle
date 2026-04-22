# *onboard

Build a harness for a new agent — or resume an in-progress one.

## Behavior

Check state before doing anything:

1. **No `ONBOARDING_STATE.md`** → start fresh at Phase 1 (Classify)
2. **`Status: In Progress`** → resume from recorded phase, do not re-ask answered questions
3. **`Status: Complete`** → report complete, suggest `*status`

## Workflow

Execute `skills/agent-onboarding/SKILL.md`:

- **Phase 1** — Classify: 5 questions → route to Simple or Complex
- **Phase 2S** (Simple) — Gather corpus/memory/retrieval info → generate harness files
- **Phase 2C** (Complex) — Reason expert set → per-expert gather → generate all harnesses

## Signals

| Signal | Action |
|--------|--------|
| `ready` / `next` | Confirm current phase output, advance |
| `skip` | Accept defaults for current phase, advance |
| `pause` | Write `ONBOARDING_STATE.md`, stop cleanly |
| `back` | Return to previous phase |
