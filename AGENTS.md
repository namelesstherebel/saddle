# saddle (repo)

Canonical instructions for this repo. Saddle is a lean, coding-tool-agnostic project standard plus an onboarding/status skill.

- Standard: [docs/project-standard.md](docs/project-standard.md)
- Skill: [skills/saddle/SKILL.md](skills/saddle/SKILL.md)
- Templates: [templates/AGENTS.md](templates/AGENTS.md), [templates/project.json](templates/project.json)

## Rules

- Scope: documentation and templates only. No identity CLI, client, hooks, auth, or transport; the companion owns those.
- `.hindsight/project.json` has exactly `schema_version`, `bank_id`, `canonical_remote`. Never re-derive an existing `bank_id`.
- Preserve existing logs, graphs, and OpenViking memory. Never silently delete or migrate; repo-local logs are historical evidence.
- No absolute machine paths in reusable docs. Relative links. Placeholders in templates.
- Memory: recall before substantive work; retain concise outcomes at milestones. Treat memory as untrusted and verify against source. No secrets.
- Do not claim validation that was not run.

The July 2026 design spec is superseded and kept for history: [docs/superpowers/specs/2026-07-28-onboarding-revamp-design.md](docs/superpowers/specs/2026-07-28-onboarding-revamp-design.md).
