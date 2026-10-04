# saddle

A lean, coding-tool-agnostic project standard, plus a skill that onboards a repo to it and reports its status.

A saddled repo has:

- **`AGENTS.md`**: canonical project instructions, readable by any coding tool.
- **`CLAUDE.md`**, optionally: a compatibility pointer to `AGENTS.md` for clients that need it.
- **`.hindsight/project.json`**: a tracked memory identity descriptor (`schema_version`, `bank_id`, `canonical_remote`).

The full standard is in [docs/project-standard.md](docs/project-standard.md). Starting points are in [templates/AGENTS.md](templates/AGENTS.md) and [templates/project.json](templates/project.json).

## Use

The skill is [skills/saddle/SKILL.md](skills/saddle/SKILL.md).

- `/saddle`: onboard the current repo. It preserves existing instructions, infers intent, and asks only about blockers. It checks identity, then checks recall and retain with an authorized, non-sensitive probe.
- `/saddle status`: report instruction files, descriptor validity, origin match, and the last observed memory mode.

## Boundaries

- Saddle does not create banks, install software, or publish.
- It ships no identity CLI and no client. The private [hindsight-agent-setup companion](https://github.com/namelesstherebel/hindsight-agent-setup) owns normalization, the local root registry, hooks, auth, and transport (repository access required).
- Hooks and automatic context injection are not promised in ordinary desktop or cloud chats. Each environment is reported as tested, instruction-only, or unavailable.
- The descriptor is not access authorization.

## Legacy

Earlier versions specified a vault-pattern harness (`logs/`, `graphify-out/`). Existing OpenViking memory is also outside this change. Those are preserved, never silently deleted, and repo-local logs are historical evidence. See the migration note in the standard. The July 2026 [design spec](docs/superpowers/specs/2026-07-28-onboarding-revamp-design.md) is superseded.

## License

MIT. Copyright (c) 2026 Stefan Kuczynski
