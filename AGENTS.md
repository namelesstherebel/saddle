# saddle (repo)

Canonical instructions for this repo. Saddle is a lean, coding-tool-agnostic project standard plus an onboarding/status skill.

- Standard: [docs/project-standard.md](docs/project-standard.md)
- Skill: [skills/saddle/SKILL.md](skills/saddle/SKILL.md)
- Templates: [templates/AGENTS.md](templates/AGENTS.md), [templates/project.json](templates/project.json)

## Rules

- Scope: documentation and templates only. No identity CLI, client, hooks, auth, or transport; the companion owns those.
- Narrow exception, explicitly user-authorized: the optional Semgrep installer, its regression tests and its CI workflow (Saddle and adopters) may be executable. Nothing else in scope changes.
- Additional user-authorized exception: the existing review-tooling tests in `tests/` and the `scripts/` code they exercise may run in CI. No broader runtime scope change.
- `.hindsight/project.json` has exactly `schema_version`, `bank_id`, `canonical_remote`. Never re-derive an existing `bank_id`.
- Preserve existing logs, graphs, and OpenViking memory. Never silently delete or migrate; repo-local logs are historical evidence.
- No absolute machine paths in reusable docs. Relative links. Placeholders in templates.
- Hindsight is retired for this non-client repository. Do not enroll roots or require recall, retention or memory readiness. Preserve existing descriptors and historical data; do not reactivate legacy memory backends.
- Do not claim validation that was not run.

The July 2026 design spec is superseded and kept for history: [docs/superpowers/specs/2026-07-28-onboarding-revamp-design.md](docs/superpowers/specs/2026-07-28-onboarding-revamp-design.md).

Provenance: https://github.com/namelesstherebel/saddle/blob/45fe8c4aa2b3deb644c5baa18980c80c67848b85/templates/AGENTS.md

Adoption snapshot base_sha40: `0e728bd90185c60c5a194ad0879b03d9f6b3fb3a`. Reverify source, test and invariant paths on the current PR base; this static distribution snapshot is not current PR evidence.

## Review and validation

This repository has completed verified staged-cutover readiness. Automatic Pullfrog is the normal current-head expert reviewer, including security; GitHub Reviewer is a manual fallback when needed, not a mandatory second review. CodeRabbit automatic reviews are disabled by `.coderabbit.yaml`; manual `@coderabbitai review` remains available. Assess valid existing legacy findings, but general legacy reviewers are not mandatory additional providers. A provider name or skipped review is not evidence of coverage.

Before normal merge, require a successful `pullfrog-approval` verdict from trusted Pullfrog app `1768019` on the current head. Mac Ops must verify actual verdict emission and read back the required rule; readiness does not replace a fresh verdict after each push. The `pullfrog` workflow/job name alone is not that verdict, and an unverified or never-emitted check is not a gate. Preserve all other applicable checks and safety, visual, release and owner-acceptance gates. Do not bypass protections or change settings under these instructions.

The current branch writer handles material findings, inspects corrections, verifies applicable source/secret checks and actual resulting-head CI, then performs a normal merge pinned to the reviewed head. Report missing, skipped, errored and non-applicable checks accurately. Source scanning is not dependency-advisory coverage; saved configuration is not proof of live review or successful provider operation.

Preserve Cubic integration, reviews and checks entirely. Retain independent Codex security review as complementary coverage; do not narrow Pullfrog's security lenses or remove security checks as duplicates. Shared expert prompts and provider settings are maintained separately, not copied or changed here.

Pullfrog fixes are opt-in, bounded handoffs only. The sole writer must explicitly hand off a contained correction and pause their own branch edits, inspect the returned diff, then obtain resulting-head CI and fresh review before normal merge. No blanket or unattended autofix is authorized; product and larger changes retain their assigned implementation owner.

## Review context

Context to cite, never invent: base SHA the current PR base SHA, obtained from GitHub for this review and cited explicitly (not the inventory snapshot SHA); invariant docs `AGENTS.md`, `CLAUDE.md`, `README.md`. Source paths: `scripts/**`, `skills/**`. Test paths: `tests/**`, `**/test_*.py`, `skills/saddle/scripts/test-semgrep.py`. Re-verify invariant, source and test paths against the current PR for every review.

Assess existing and changed tests against the affected behavior. Existing coverage can be sufficient; flag concrete gaps rather than requiring test-file changes mechanically. Report actual applicable check outcomes and meaningful limits; missing, skipped or errored checks are not a pass.

Labels (apply those whose criteria match):

- `frontend`: user-facing UI or client behavior changes.
- `backend`: server, service or API behavior changes.
- `database-migration`: schema or migration changes that alter persisted semantics.
- `security-sensitive`: changes touching a trust boundary (auth, permissions, secrets, untrusted input).
- `high-risk-architecture`: cross-module contracts or concurrency changes.
- `no-tests`: an unaddressed applicable test coverage gap.
