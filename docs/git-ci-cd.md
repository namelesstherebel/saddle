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

- Open a draft PR and keep it draft while scoped work is unfinished.
- Merge-ready requires an independent review verdict at the exact unchanged head SHA, and passing required checks at that same SHA.
- Any new commit invalidates earlier checks and review; re-run and re-review the new head.
- Merge-ready is not merge permission. Merging needs separate authorization.

### Automatic ready-for-review

When authorized delivery is complete, the agent pushes the final task-branch head (never a force-push) and then marks only the intended PR ready for review, automatically, unless an explicit user hold/draft instruction or repository policy prevents it. Before the transition:

1. Verify the remote branch and PR are the intended ones and that the remote PR head equals the pushed SHA.
2. Verify every required, applicable pre-review check (test, lint, build) passed on that exact SHA. Failing, pending, missing, unknown or skipped required checks block. A missing check-set configuration or absent reports is not vacuous success: report the blocker and do not weaken gates.
3. Recheck the PR head and state immediately before the transition. A changed head invalidates the evidence; restart from step 1.

Notes:

- Ready requests the configured review. It does not guarantee a reviewer exists or runs, and it is not an independent review verdict. Pre-review checks are distinct from downstream review triggered by ready; do not wait on review before marking ready (circular wait).
- An already-ready PR needs no duplicate transition.
- If CI or review integration is unavailable, report that accurately and keep the PR draft. Offline mode is not a bypass.
- This convention grants no new repository, access or settings authority; respect the existing publication scope. It never force-pushes, merges implicitly, or deploys to production. Merge-ready still needs independent review and required checks at the current unchanged head, plus separate merge authorization.
- Inheritance: a repo receives this behavior only when Saddle is actually applied to it (for example by adopting the `AGENTS.md` template). Existing repos are not changed retroactively.

## 4. Small-fix loop

For failing gates, at most 2 attempts, each limited to scoped, deterministic issues. After each: rerun the affected gates and review the new head.

Stop and escalate on a repeat failure, uncertain diagnosis, security concern, schema change, or a large change. Never loosen tests, checks or permissions to pass.

## 5. CD

CI does not deploy. Deployment needs a separate, explicit approval naming:

- the target and environment;
- the exact reviewed artifact or commit;
- the relevant passing gates for that commit;
- a rollback plan and a verification step.

No implicit production release, no credentials handling, and no new persistent access. Deployment and merging are never automatic. Onboarding itself does not publish; pushing and the ready-for-review transition happen only as authorized project delivery (section 3).

## 6. Status reporting

Onboarding and status report each area as observed: Git state, CI gates, review, CD. Use "not configured" when nothing exists and "not run" when it exists but has no result. Do not claim enforcement where only documentation exists.

## 7. Optional CodeRabbit setup

Only when the task asks for it. Documentation only; no APIs, executables, settings changes or app installation. Template: [coderabbit.yaml](../templates/coderabbit.yaml). Official docs: [auto-review](https://docs.coderabbit.ai/configuration/auto-review), [inheritance](https://docs.coderabbit.ai/configuration/configuration-inheritance), [YAML configuration](https://docs.coderabbit.ai/getting-started/yaml-configuration).

- Coverage: check the actual App installation selection read-only. OAuth scopes, subscription, and absent bot comments do not prove coverage. Respect a 403 and report unknown.
- Inspect existing YAML and effective UI/global overrides first. `inheritance: true` preserves parent settings, but arrays merge and global overrides win.
- The default branch is included in auto-review target matching; it does not guarantee a review, because installation, enabled/drafts/filters and plan eligibility still apply. Anchored patterns (for example `^staging$`) add only verified, approved additional PR targets; never an all-branches wildcard.
- YAML is read from the PR feature head, so old PR branches need separately coordinated updates. A copied template is not live shared config.
- Emit the template only where existing task authorization covers that specific repo; no future-repo grant.
- Do not change installation, permissions or billing, post bot commands, or publish during onboarding.
- Report coverage, config, targets and exact-head review evidence, or unknown.
