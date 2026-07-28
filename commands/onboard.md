# *onboard

Build a repo harness in one sitting.

## Behavior

No state file machine. Check `.claude/scratchpad.md` before doing anything:

1. **Exists with onboarding-in-progress notes** → resume from what it records, do not re-ask answered questions
2. **Missing or no in-progress notes** → start at Phase 1

## Workflow

Execute `skills/onboarding/SKILL.md`:

- **Phase 1** — Intent: what the repo does and for whom, intent split, recall formation rules, persona
- **Phase 2** — Tool inventory: sweep locker/skills/CLIs/MCPs, match against intent, confirm shortlist
- **Phase 3** — Research (delegated): derive questions, dispatch to fleet, land results as `docs/research/`
- **Phase 4** — Generate: `CLAUDE.md` + `.claude/scratchpad.md` + `graphify-out/` bootstrap extract
- **Phase 5** — Hygiene (automatic): `/prune` + `/brainscan`, results in completion summary

## Hard gates

- **Research dispatch** — present the research plan (questions + agent per question) as one batch; user confirms before any dispatch. Token spend gated here.
- **Hygiene** — Phase 5 runs `/prune` and `/brainscan` automatically and reports results. Not skippable.

## Signals

| Signal | Action |
|--------|--------|
| `ready` / `next` | Confirm phase output, advance |
| `skip` | Accept defaults, advance |
| `pause` | Write progress to `.claude/scratchpad.md`, stop cleanly |
