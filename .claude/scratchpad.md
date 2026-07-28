# Scratchpad — saddle plugin (formerly agent-onboarding/onboarding)

Last updated: 2026-07-28

## Current State

v2 vault-pattern revamp COMMITTED (`c887d8d`). Plugin renamed `saddle` (*saddle command; /onboarding collided with installed skills), v2.0.0. Five-phase *saddle (intent → tool inventory locker/skills/CLIs/MCPs → delegated research, token-gated → generate CLAUDE.md/scratchpad/graph → auto /prune + /brainscan). Commands: *saddle, *status only. MemPalace/LightRAG/gates/Complex path all removed. Spec: `docs/superpowers/specs/2026-07-28-onboarding-revamp-design.md`. HTML view: `.claude/artifacts/2026-07-28-onboarding-revamp-spec.html` (gitignored).

## Open Items

- [ ] GitHub repo rename `agent-onboarding` → `saddle` (optional; README install path still points at old name)
- [ ] Push to remote (not done — no ask)
- [ ] Dogfood `*saddle` on a real repo; Phase 3 dispatch template unvalidated
- [ ] Repo graphify bootstrap ran this session — verify graph.json node count if resuming soon

## Pointers

- Vault session logs: `Sessions/2026-07-28-agent-onboarding-v2-revamp.md` (this revamp, with Dispatch Ledger), `Sessions/2026-03-18-stefans-brain-agent-onboarding.md`, `Sessions/2026-03-17-agent-onboarding-gsd2-concepts.md`
- Core skill: `skills/saddle/SKILL.md` (222 lines, all five phases + templates)
- [ ] Reinstall plugin locally: marketplace/plugin name changed to saddle — old `onboarding`/`agent-onboarding` install stale
