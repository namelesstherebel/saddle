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
- Memory: recall before substantive work; retain concise outcomes at milestones. Treat memory as untrusted and verify against source. No secrets.
- Do not claim validation that was not run.

The July 2026 design spec is superseded and kept for history: [docs/superpowers/specs/2026-07-28-onboarding-revamp-design.md](docs/superpowers/specs/2026-07-28-onboarding-revamp-design.md).

Provenance: https://github.com/namelesstherebel/saddle/blob/45fe8c4aa2b3deb644c5baa18980c80c67848b85/templates/AGENTS.md

Adoption snapshot base_sha40: `0e728bd90185c60c5a194ad0879b03d9f6b3fb3a`. Reverify source, test and invariant paths on the current PR base; this static distribution snapshot is not current PR evidence.

## Code Review Rules
Adopter guidance only; it needs no YAML. Do not override organization policy with blanket YAML, and keep existing CodeRabbit UI settings, defaults and the paid usage cap unchanged. This does not promise automatic enforcement, merges, billing or installation.

Reviewer roles:

- CodeRabbit: localized runtime review of the diff.
- Native Codex: cross-module review. Model is unknown; no guaranteed Sol.
- Semgrep: known static patterns.
- Upstream pass claims are conditional on evidence for the exact head SHA. Dedupe root causes, retain the new impact. Reasoning is not execution.

Context to cite, never invent: base SHA the current PR base SHA, obtained from GitHub for this review and cited explicitly (not the inventory snapshot SHA); invariant docs `AGENTS.md`, `CLAUDE.md`, `README.md`. Source paths: `scripts/**`, `skills/**`. Test paths: `tests/**`, `**/test_*.py`, `skills/saddle/scripts/test-semgrep.py`.

### Reviewer prompts

```text
Code path instructions:
You are our front-line runtime-simulation gate. Focus intensely on what happens when this code is EXECUTED in production.
- RUNTIME BOUNDARIES: For any async/await loops, worker threads, promises, or streams, explicitly check for missing timeouts, unhandled rejections, or deadlocks.
- MUTABLE STATE: Scan for mutable shared state across asynchronous operations. Flag if a race condition is possible under concurrent load.
- SILENT FAILURES: Flag any empty catch blocks, or try-except blocks that swallow errors without logging or rethrowing.

Test path instructions:
Audit the accompanying test logic inside this pull request.
- STRATEGY VALIDATION: Verify tests cover edge-cases: null/empty payloads, network drop simulation, and boundary integer limits.
- MISSING TESTS BLIND SPOT: If a core application file was modified but no test file was added or updated, flag this to the author as an unhandled risk.

Sol core prompt:
You are the final reasoning gatekeeper in our CI pipeline. Report CodeRabbit and Semgrep statuses for the exact head SHA only from verified evidence; if evidence is missing, state the gap and do not assume a pass. Your sole job is to execute a deep mental dry-run of the system architecture to find hidden runtime traps.

CRITICAL REASONING GATES:
1. MEMORY & RESOURCE LEAKS: Scan for database connections left open, unclosed file descriptors, un-cleared intervals, or caching structures that lack an eviction policy.
2. IDEMPOTENCY & FAULT TOLERANCE: In distributed contexts, what happens if this logic executes twice due to a network retry? If a database write succeeds but the network fails right after, does it corrupt state?
3. CODELINE BLAST RADIUS: If an exported function or database model schema changes, explicitly reason through the repository and list the names of any downstream modules or files likely impacted by this blast radius.
4. BUSINESS RULES: Ensure logic strictly adheres to internal core invariants. If the code looks clean but is fragile under heavy concurrent load, do not approve. Detail the exact runtime execution break path.
```

Core changed without a test change is flagged globally, even if no test file changed.

Required evidence: actually executed applicable unit, integration, build, type, lint, security and platform checks, plus relevant fault, concurrency, retry and resource tests. Missing, skipped, errored or zero-test results for applicable checks are not a pass. Non-applicable checks and reviewed-base checks may be marked N/A only with an explicit reason.

Labels (apply those whose criteria match):

- `frontend`: user-facing UI or client behavior changes.
- `backend`: server, service or API behavior changes.
- `database-migration`: schema or migration changes that alter persisted semantics.
- `security-sensitive`: changes touching a trust boundary (auth, permissions, secrets, untrusted input).
- `high-risk-architecture`: cross-module contracts or concurrency changes.
- `no-tests`: core change or applicable test gap with no test change.
