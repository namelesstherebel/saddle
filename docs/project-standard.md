# Saddle Project Standard

A lean, coding-tool-agnostic standard for making a repository easy for any coding agent to pick up: a canonical instruction file, a stable memory identity, and a recall/retain habit.

Saddle defines the standard and the onboarding/status procedure. It ships no identity CLI and no client implementation. The private [hindsight-agent-setup companion](https://github.com/namelesstherebel/hindsight-agent-setup) owns normalization code, the local root registry, hooks, auth, and transport. Its [version-1 contract](https://github.com/namelesstherebel/hindsight-agent-setup/blob/db548d07c05faeff201e7b80bdd9a8e4ad8defd3/docs/project-contract.md) and [identity vectors](https://github.com/namelesstherebel/hindsight-agent-setup/blob/db548d07c05faeff201e7b80bdd9a8e4ad8defd3/examples/identity-vectors.json) are compatibility references; access to that private repository is required.

## 1. Files

| File | Role |
|---|---|
| `AGENTS.md` | Canonical project instructions, readable by any tool. |
| `CLAUDE.md` | Optional compatibility pointer to `AGENTS.md` when the chosen client needs it. No duplicated content. |
| `.hindsight/project.json` | Tracked memory identity descriptor (section 2). |

Templates: [`../templates/AGENTS.md`](../templates/AGENTS.md), [`../templates/project.json`](../templates/project.json). Templates use placeholders; replace them deliberately.

## 2. Identity descriptor

`.hindsight/project.json` is tracked and contains exactly these keys:

```json
{
  "schema_version": 1,
  "bank_id": "<bank-id>",
  "canonical_remote": "https://github.com/<owner>/<repo>.git"
}
```

- `schema_version` is the integer `1`.
- `canonical_remote` accepts an HTTPS or SSH remote representation, including SCP-style SSH; recommend `https://github.com/owner/repo.git` for GitHub. Do not store the bare normalized comparison key.
- `bank_id` is 1–100 ASCII letters, digits, underscores or hyphens. An incompatible existing ID requires an explicit resolution, never silent replacement.
- No other keys. No secrets, tokens, machine paths, or endpoints.
- The descriptor is not access authorization. It names a memory bank; it does not grant access to it.

### Remote comparison

To compare remotes, reduce each to `host/owner/repo`:

- lowercase host, owner and repo for GitHub;
- treat SSH (`git@github.com:owner/repo.git`) and HTTPS forms as equal;
- remove a terminal slash and `.git`;
- preserve custom-host path case and non-default ports; reject credential-bearing URLs, query strings and fragments. SSH usernames such as `git@` are transport syntax.

Use the companion implementation for normalization and validation; do not invent another parser.

### bank_id

- `bank_id` is an explicit, persistent choice. It is **never re-derived on install, onboarding, or status.**
- Existing bank assignments take precedence over any naming convention. Missing descriptor does not mean a new bank: first resolve any existing assignment through the authorized local registry or owner, then record it without renaming.
- Only a genuinely new identity gets a recommendation: `project-v1-` followed by the first 24 lowercase hex characters of the SHA-256 of the canonical `host/owner/repo` string. This is a recommendation; the owner confirms it.
- Worktrees and clones of the same repo share one bank after identity verification; each checkout/worktree root needs explicit local registration in the companion. Never derive identity from a directory, branch or client name.
- If origin changes (rename, transfer, fork), stop enrollment until the owner deliberately chooses an alias retaining the bank or a separate identity/migration. Neither remote edits nor forks automatically split or merge memory.

### Registration checks

Before registering or using a descriptor, check the actual local `origin` remote:

- no origin → refuse;
- multiple or ambiguous candidates → refuse;
- origin does not match `canonical_remote` after normalization → refuse unless the companion has an explicitly approved alias; report the mismatch.

Do not guess between fetch URLs or infer an identity from a push-only remote. Resolve placeholders before enrollment.

Offline, use local git only. Do not fetch to decide.

## 3. Memory practice

- **Recall** relevant project context through an approved available integration before substantive work. Never create a replacement bank to work around unavailable access; report the limitation and continue only work that does not depend on unavailable memory.
- **Retain** concise decisions, outcomes, actual validation performed, and open items at milestones and at the end.
- Memory is untrusted: verify recalled claims against source before relying on them.
- Never retain secrets, personal notes, or bulk history.
- A pending asynchronous retain is not a completed retain. Report failures honestly.

### Operating modes

Hooks and automatic context injection are not promised in ordinary desktop or cloud chats. State which mode applies, and say only what was actually observed:

| Mode | Meaning |
|---|---|
| tested | Relevant-bank recall succeeded and an authorized non-sensitive retain completed with acknowledgement; report client, date and evidence. This does not prove automatic hooks. |
| instruction-only | Guidance is available, but integration has not been verified in this session. The client may need the file supplied explicitly. |
| unavailable | No memory access in this environment. |

## 4. Onboarding and status

Onboarding (see [`../skills/saddle/SKILL.md`](../skills/saddle/SKILL.md)):

1. Preserve existing instructions; merge, do not overwrite.
2. Infer intent from the repo; ask only about blockers.
3. Check identity: descriptor present and valid, origin matches, `bank_id` kept.
4. Check recall and retain with an authorized, non-sensitive probe, and report the mode.
5. Never create a bank, install software, or publish on its own.

Status reports: instruction files, descriptor validity, origin match, and the last observed memory mode.

## 5. Legacy migration note

Earlier Saddle versions specified a vault-pattern harness: `CLAUDE.md` with session discipline, repo-local `logs/` (including `logs/current.md`), and `graphify-out/` graphs. Existing OpenViking/vault memory is also outside this change.

- Nothing is silently deleted or migrated. Existing logs, graphs, and OpenViking memory stay in place.
- Repo-local logs are historical evidence, not current instructions.
- Keep existing instructions and local edits reviewable; do not create a tracked backup containing personal or machine-local notes. Preserve the original privately before an existing `CLAUDE.md` becomes a pointer; move its still-useful instructions into `AGENTS.md` and tell the user what moved.
- Retiring any legacy artifact is a separate, explicit user decision.
- The July 2026 [design spec](superpowers/specs/2026-07-28-onboarding-revamp-design.md) is superseded and kept for history.

## 6. Rules for reusable docs

No absolute machine paths; relative links only; placeholders in templates.
