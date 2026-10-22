# <Project name>

<One sentence: what this project does. One sentence: what it does not do.>

## Working agreements

- <Build/test commands: placeholder>
- <Style or format preferences: placeholder>
- Ask before: <actions needing approval>
- Git/CI/CD: work on an isolated branch, stage named paths, record gate results with the tested SHA, and never deploy without separate approval. Keep unfinished scoped work as a draft PR. When authorized delivery is complete, push the final head (no force-push), verify the remote PR/head is the intended one and all required pre-review checks passed on that exact SHA, recheck the head just before, then mark only that PR ready for review unless the user or repository policy says hold/draft. Failing, pending, missing, unknown or skipped required checks block (report; do not weaken gates). If CI/review integration is unavailable, report it and keep draft. Ready is not review approval; never merge or deploy without separate authorization. See [Git, CI and CD guide](../docs/git-ci-cd.md) and [checklist](git-ci-checklist.md). These links resolve from `templates/`; when copying this template into another repository, adjust them to where the Saddle docs live.

## Code Review Rules

Adopter guidance only; it needs no YAML. Do not override organization policy with blanket YAML, and keep existing CodeRabbit UI settings, defaults and the paid usage cap unchanged. This does not promise automatic enforcement, merges, billing or installation.

Reviewer roles:

- CodeRabbit: localized runtime review of the diff.
- Native Codex: cross-module review. Model is unknown; no guaranteed Sol.
- Semgrep: known static patterns.
- Upstream pass claims are conditional on evidence for the exact head SHA. Dedupe root causes, retain the new impact. Reasoning is not execution.

Context to cite, never invent: current PR base SHA `<current PR base SHA>`, obtained from GitHub for this review and cited explicitly. Re-verify invariant docs `<verified invariant doc paths>`, source paths `<verified source paths>` and test paths `<verified test paths>` against the current PR for every review; onboarding values are snapshots, not current review evidence.

### Reviewer prompts

```text
Code path instructions:
You are our front-line runtime-simulation gate. Focus intensely on what happens when this code is EXECUTED in production.
- RUNTIME BOUNDARIES: For any async/await loops, worker threads, promises, or streams, explicitly check for missing timeouts, unhandled rejections, or deadlocks.
- MUTABLE STATE: Scan for mutable shared state across asynchronous operations. Flag if a race condition is possible under concurrent load.
- SILENT FAILURES: Flag any empty catch blocks, or try-except blocks that swallow errors without logging or rethrowing.

Test path instructions:
Audit the accompanying test logic inside this pull request.
- STRATEGY VALIDATION: Verify tests cover edge cases applicable to the changed code’s inputs and risks (for example, null/empty payloads, network drops, or boundary integer limits).
- MISSING TESTS BLIND SPOT: For core application changes, assess existing and changed tests against the affected behavior; flag only an actual coverage gap.

Sol core prompt:
You are the final reasoning gatekeeper for this review. Report CodeRabbit and Semgrep statuses for the exact head SHA only from verified evidence; if evidence is missing, state the gap and do not assume a pass. Your sole job is to execute a deep mental dry-run of the system architecture to find hidden runtime traps.

CRITICAL REASONING GATES:
1. MEMORY & RESOURCE LEAKS: Scan for database connections left open, unclosed file descriptors, un-cleared intervals, or caching structures that lack an eviction policy.
2. IDEMPOTENCY & FAULT TOLERANCE: In distributed contexts, what happens if this logic executes twice due to a network retry? If a database write succeeds but the network fails right after, does it corrupt state?
3. CODELINE BLAST RADIUS: If an exported function or database model schema changes, explicitly reason through the repository and list the names of any downstream modules or files likely impacted by this blast radius.
4. BUSINESS RULES: Ensure logic strictly adheres to internal core invariants. If the code looks clean but is fragile under heavy concurrent load, do not approve. Detail the exact runtime execution break path.
```

Assess coverage for every core change, even if no test file changed; existing tests can satisfy coverage. Flag only an actual gap.

Required evidence: actually executed applicable unit, integration, build, type, lint, security and platform checks, plus relevant fault, concurrency, retry and resource tests. Missing, skipped, errored or zero-test results for applicable checks are not a pass. Non-applicable checks and reviewed-base checks may be marked N/A only with an explicit reason.

Labels (apply those whose criteria match):

- `frontend`: user-facing UI or client behavior changes.
- `backend`: server, service or API behavior changes.
- `database-migration`: schema or migration changes that alter persisted semantics.
- `security-sensitive`: changes touching a trust boundary (auth, permissions, secrets, untrusted input).
- `high-risk-architecture`: cross-module contracts or concurrency changes.
- `no-tests`: an unaddressed applicable test coverage gap.

## Project records

Use the assigned work records and repository evidence for current context. Memory enrollment, descriptors, recall/retain probes and memory receipts are not onboarding or completion requirements. Preserve existing historical data; do not silently reactivate retired integrations. An existing client memory integration requires its own explicit current project authorization and instructions.

## Pointers

- <relative link to docs>
