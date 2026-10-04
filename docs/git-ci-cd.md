# Git, CI and CD Onboarding

Tool-agnostic guidance for Git onboarding and CI/CD setup in a saddled repo. This guide is documentation only: it enforces nothing. Report enforcement only when it was actually observed (for example a configured, running check), never because this guide describes it. Use the [checklist](../templates/git-ci-checklist.md) to record state. See also the [standard](project-standard.md).

Do not include private contents, machine paths or credentials in repo docs or evidence.

## 1. Git onboarding

Inspect the actual state before acting:

- Repository and worktree: confirm you are in the intended repo or worktree. Never `git init` inside an existing repo (no nested repos).
- Dirty and index state: note modified, untracked and staged files. Preserve unrelated edits.
- Remote: verify the fetch and push URLs of `origin`, and that they match the intended target. Do not retarget a remote silently.
- Default branch and upstream: identify the default branch and the current branch's upstream, if any.
- Offline checks (local config, status, refs) are distinct from remote verification (reachability, remote default branch). Say which was done; do not fetch to decide offline questions.

Rules:

- A new repo or new remote requires explicit task authorization.
- No destructive reset, no blanket staging (`git add -A` or `.`), no implicit force-push. Stage named paths only.
- Work on an isolated task branch created from a verified intended base commit.
- Use the existing configured author identity; do not invent or change it.
- Make scoped commits containing only the task's files.
- Ignore build output and local secret artifacts via ignore rules; never commit them.

## 2. CI discovery and gates

Discover before defining: existing scripts, toolchain, and lockfiles. Record the exact test, lint and build commands, and for each whether it applies, with a rationale.

Gate evidence carries:

| Field | Meaning |
|---|---|
| command or check name | Exact command or required check name |
| tested commit SHA | The commit the result applies to |
| result | passed, failed, pending, skipped, missing, unknown, or N/A |
| evidence reference | Where the result can be inspected |

Interpretation:

- A required gate that is failed, pending, missing or unknown blocks.
- Skipped is not passed.
- N/A is valid only with documented applicability rationale.
- A gate never run is "not run"; an absent pipeline is "not configured".

Ownership: a pipeline worker owns executable CI. Docs and onboarding do not add workflows, credentials, or branch/protection changes.

## 3. Review and merge readiness

- Open a draft PR.
- Merge-ready requires an independent review verdict at the exact unchanged head SHA, and passing required checks at that same SHA.
- Any new commit invalidates earlier checks and review; re-run and re-review the new head.
- Merge-ready is not merge permission. Merging needs separate authorization.

## 4. Small-fix loop

For failing gates, at most 2 attempts, each limited to scoped, deterministic issues. After each: rerun the affected gates and review the new head.

Stop and escalate on a repeat failure, uncertain diagnosis, security concern, schema change, or a large change. Never loosen tests, checks or permissions to pass.

## 5. CD

CI does not deploy. Deployment needs a separate, explicit approval naming:

- the target and environment;
- the exact reviewed artifact or commit;
- the relevant passing gates for that commit;
- a rollback plan and a verification step.

No implicit production release, no credentials handling, and no new persistent access. Publication and deployment are never automatic.

## 6. Status reporting

Onboarding and status report each area as observed: Git state, CI gates, review, CD. Use "not configured" when nothing exists and "not run" when it exists but has no result. Do not claim enforcement where only documentation exists.
