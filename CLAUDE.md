# Agent Onboarding Plugin

## Commands

`*onboard` — Build or resume a harness. Read `commands/onboard.md`, then execute.
`*reflect` — Review MemPalace health: provisional items, stale derivations, corpus gaps. Read `commands/reflect.md`, then execute.
`*review` — Process provisional MemPalace items: promote or deprecate. Read `commands/review.md`, then execute.
`*status` — Report harness health: memory stats, LightRAG status, gate health. Read `commands/status.md`, then execute.

Do not ask for clarification on any of these — just execute.

## Onboarding State

- No `ONBOARDING_STATE.md` → start fresh at Phase 1 (Classify).
- `Status: In Progress` → resume from recorded phase. Don't re-ask answered questions.
- `Status: Complete` → report complete, suggest `*status`.

## Rules

- Never generate harness files without routing through Phase 1 (Classify) first.
- Confirm each phase output before advancing.
- Never modify a generated CLAUDE.md's gate protocol without user instruction.
- Never persist in-session working state to MemPalace in generated instructions.
