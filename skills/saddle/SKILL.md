---
name: saddle
description: >
  /saddle: onboard the current repo to the Saddle project standard (canonical AGENTS.md, optional compatibility pointer,
  .hindsight/project.json identity, recall/retain check). /saddle status: report project-standard health.
  Also triggers on "saddle this repo", "onboard this repo", "set up project memory for this repo".
---

# Saddle: Project Standard Onboarding

Normative detail lives in [the standard](../../docs/project-standard.md). Do not restate it here. Templates: [AGENTS.md](../../templates/AGENTS.md), [project.json](../../templates/project.json).

**Arguments:** none → Onboard. `status` → Status.

## Onboard

1. **Read first.** Read existing `AGENTS.md`, `CLAUDE.md`, `.hindsight/project.json`, and the README. Preserve existing instructions. Merge into `AGENTS.md`; never overwrite. If `CLAUDE.md` has real content, preserve the original privately, move its useful instructions into `AGENTS.md`, then reduce it to a pointer, and tell the user what moved.
2. **Infer intent** from the repo. Ask only questions that block progress, in one batch.
3. **Identity.**
   - Descriptor exists → validate exactly `schema_version: 1`, `bank_id`, `canonical_remote`. Keep `bank_id` as is; never re-derive it.
   - No descriptor → inspect the authorized companion registry or resolve the existing bank with the owner first. Missing file is not proof of a new identity. Read actual local `origin`; refuse missing/ambiguous/conflicting identity. For a genuinely new project only, suggest the standard's deterministic ID. Record the resolved choice; do not ask again if already authorized.
   - Descriptor exists but origin does not match → refuse unless the companion validates an explicitly approved alias. Forks/renames require an identity decision. Worktrees share the chosen bank but each local root needs companion registration.
   - Offline: use local git only. The descriptor is not access authorization.
4. **Recall/retain check.** Within existing authorization and available memory tools, recall relevant context and retain one non-sensitive probe in the verified bank. Do not repeat approval questions already answered. A tested result requires acknowledged completion, not a queued write; report client/date/evidence. Report the mode as `tested`, `instruction-only`, or `unavailable`, and report failures or pending retains honestly. Do not promise hooks or automatic injection.
5. **Never** create a bank, install anything, or publish during onboarding (later authorized project delivery follows step 6). Do not delete or migrate legacy `logs/`, `graphify-out/`, or OpenViking memory; mention them as historical evidence and leave them.
6. **Git/CI/CD.** Follow [the Git/CI/CD guide](../../docs/git-ci-cd.md) and fill in [the checklist](../../templates/git-ci-checklist.md) as needed: inspect actual repo, index, `origin` and branch state; discover existing test/lint/build commands; record gate evidence with SHA. Inspect before any Git change. Initialize a repo only if it is genuinely new (never nested inside an existing repo), and add or retarget a remote only when the task explicitly authorizes it; never retarget silently. Do not re-ask for authorization the task already gave. Executable CI is a separately assigned pipeline task: do not add workflows, change protections or credentials, or deploy implicitly. Onboarding does not publish. For adopted projects, record the ready-for-review convention (draft while unfinished; on authorized delivery, push without force, verify intended remote PR/head and passing required pre-review checks on that exact SHA, recheck, then mark only that PR ready unless held; never merge or deploy) as in the guide's section 3; it applies once Saddle is actually applied, not retroactively, and grants no new authority.
7. **Summarize** what changed, the memory mode, Git/CI/CD state (`not configured` / `not run` where true), and what was not verified.

## Status

Report each item as pass/warn/fail, from what was actually observed:

- `AGENTS.md` present; any applicable `CLAUDE.md` is a pointer to it (absence is not a failure)
- `.hindsight/project.json` valid under the standard (exact keys, integer schema 1, stable bank ID, accepted HTTPS/SSH remote)
- local `origin` matches `canonical_remote` after normalization (lowercase GitHub, SSH = HTTPS, no `.git`)
- last observed memory mode (`tested` / `instruction-only` / `unavailable`), or "not checked"
- Git state (branch, upstream, dirty/index), CI gates (command, SHA, result) and CD approval: observed value, `not configured`, or `not run`; docs alone are not enforcement
- legacy artifacts present (`logs/`, `graphify-out/`), noted only, never flagged for deletion

No instruction file and no descriptor → "Not saddled. Run /saddle."
