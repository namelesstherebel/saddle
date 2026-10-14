# Git / CI / CD Checklist

Copy and fill in per task. Detail: [Git, CI and CD guide](../docs/git-ci-cd.md). Use `not configured`, `not run`, or `unknown` honestly; this checklist does not itself enforce anything.

## Git

- [ ] Repo/worktree inspected (no nested `git init`)
- [ ] Dirty/index state noted; unrelated edits preserved
- [ ] `origin` fetch/push target verified: <result, offline or remote>
- [ ] Default branch and upstream: <value or none>
- [ ] New repo/remote authorized by task (if any): <yes / n/a>
- [ ] Isolated task branch from verified base: <branch @ base SHA>
- [ ] Existing author identity used
- [ ] Scoped commits; named-path staging only; no force-push
- [ ] Build/local-secret artifacts ignored

## CI gates

Required failed, pending, missing or unknown blocks. Skipped is not passed. N/A needs rationale.

| Command / check | Applies? (rationale) | Tested SHA | Result | Evidence ref |
|---|---|---|---|---|
| <tests> | <yes/N/A: why> | <sha> | <result> | <ref> |
| <lint> | | | | |
| <build> | | | | |

CI state: <not configured / configured / not run>

## Review

- [ ] Draft PR opened; kept draft while scoped work is unfinished
- [ ] Ready-for-review (automatic when delivery is complete, unless user hold/draft or repo policy): <transitioned / already ready / held: reason / blocked: reason>
  - [ ] Final head pushed, no force-push; remote PR/head matches intended: <sha>
  - [ ] All required pre-review checks passed on that exact SHA (no failing/pending/missing/unknown/skipped; absent check config is a blocker)
  - [ ] Head and state rechecked immediately before transition; only the intended PR changed
  - Ready requests review; it is not a review verdict. CI/review integration unavailable → report, keep draft.
- [ ] Test evidence (actually executed): executed <n> / passed <n> / failed <n> / errors <n> / skipped <n> (count unit: test cases as reported, not inferred assertion counts); provider job/run/attempt: <ids>; platform/runtime: <value>; report link: <ref>; head: <sha>. Zero tests, or any skip, failure, error or missing evidence, is not a pass; no new exemptions.
  - Evidence provenance: <provider-reported / script-reported / independently verified>. Provider-reported = taken from the CI provider's own record; script-reported = emitted by a project script or test runner output; independently verified = re-checked by a separate party or source. None is an immutable or trusted attestation.
- [ ] Code review status at head <sha>: <completed / pending / skipped / absent / error>; model: <known: name / unknown>
- [ ] Security review status at head <sha>: <completed / pending / skipped / absent / error>; model: <known: name / unknown>
  - Status and model are separate fields. Only `completed` at the exact current head counts as review; an unknown model alone does not invalidate a confirmed native review.
- [ ] Independent review verdict at head SHA: <sha, verdict>
- [ ] Required checks passing at that same SHA
- [ ] No commits since review/checks (otherwise rerun and re-review)
- Merge-ready is not merge permission: merge authorized? <no / yes, by whom>

## Small-fix loop

- Attempts used (max 2): <n>
- Stopped on repeat failure, uncertain diagnosis, security, schema or large change? <no / yes: reason>
- No test, check or permission loosened

## CD

CI does not deploy. Deployment: <not configured / not approved / approved>

- [ ] Explicit target and environment approval: <target/env>
- [ ] Exact reviewed artifact/commit: <sha or id>
- [ ] Relevant gates passed for that commit
- [ ] Rollback plan and verification step: <ref>
- [ ] No implicit production release, credentials or new persistent access
