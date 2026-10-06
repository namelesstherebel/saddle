# saddle

A lean, coding-tool-agnostic project standard, plus a skill that onboards a repo to it and reports its status.

A saddled repo has:

- **`AGENTS.md`**: canonical project instructions, readable by any coding tool.
- **`CLAUDE.md`**, optionally: a compatibility pointer to `AGENTS.md` for clients that need it.
- **`.hindsight/project.json`**: a tracked memory identity descriptor (`schema_version`, `bank_id`, `canonical_remote`).

The full standard is in [docs/project-standard.md](docs/project-standard.md). Starting points are in [templates/AGENTS.md](templates/AGENTS.md) and [templates/project.json](templates/project.json).

Git onboarding and CI/CD setup guidance is in [docs/git-ci-cd.md](docs/git-ci-cd.md), with a fill-in [checklist](templates/git-ci-checklist.md). It is documentation only and enforces nothing. It includes an automatic ready-for-review convention: unfinished work stays draft; on authorized delivery, agents push the final head (no force-push), verify the intended PR and passing required pre-review checks on that exact SHA, then mark only that PR ready unless held. Ready is not a review verdict, merge, or deploy. Adopted repos get this when Saddle is applied; existing repos are not changed retroactively.

Optional Semgrep adoption: `python3 -I skills/saddle/scripts/wire-semgrep.py ROOT` installs a repo-local scan (`--check` to verify). Local scanner 1.179.0 (engine pinned, dependencies not locked) with 84 local rules: 79 vendored GitLab MIT rules (68 Python, 11 JS/TS) pinned to a `sast-rules` commit, plus 5 custom Saddle rules (Python input-to-shell taint, shell audit, JS eval/exec, PHP eval). PHP is custom eval only. No Rust/Dart/Swift/C++/SQL/Shell/Astro coverage, SCA, secrets or cross-file analysis. Every finding stays visible: ERROR findings block, WARNING/INFO are audit (not automatically harmless), and one upstream rule is audit-only. Exit 0 means no blocking findings, not clean. No account, token or runtime Registry download; metrics, version-check and trace are off and no source is uploaded. CI uses a hosted runner with an exact-SHA action and does not execute PR helpers. Details: [template README](skills/saddle/templates/semgrep/README.md).

## Use

The skill is [skills/saddle/SKILL.md](skills/saddle/SKILL.md).

- `/saddle`: onboard the current repo. It preserves existing instructions, infers intent, and asks only about blockers. It checks identity, then checks recall and retain with an authorized, non-sensitive probe.
- `/saddle status`: report instruction files, descriptor validity, origin match, and the last observed memory mode.

## Boundaries

- Saddle does not create banks, install software, or publish during onboarding. Authorized project delivery may push and mark a PR ready under the policy above; it never merges or deploys automatically.
- It ships no identity CLI and no client. The private [hindsight-agent-setup companion](https://github.com/namelesstherebel/hindsight-agent-setup) owns normalization, the local root registry, hooks, auth, and transport (repository access required).
- Hooks and automatic context injection are not promised in ordinary desktop or cloud chats. Each environment is reported as tested, instruction-only, or unavailable.
- The descriptor is not access authorization.

## Legacy

Earlier versions specified a vault-pattern harness (`logs/`, `graphify-out/`). Existing OpenViking memory is also outside this change. Those are preserved, never silently deleted, and repo-local logs are historical evidence. See the migration note in the standard. The July 2026 [design spec](docs/superpowers/specs/2026-07-28-onboarding-revamp-design.md) is superseded.

## License

MIT. Copyright (c) 2026 Stefan Kuczynski
