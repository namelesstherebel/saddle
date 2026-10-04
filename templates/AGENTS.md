# <Project name>

<One sentence: what this project does. One sentence: what it does not do.>

## Working agreements

- <Build/test commands: placeholder>
- <Style or format preferences: placeholder>
- Ask before: <actions needing approval>
- Git/CI/CD: work on an isolated branch, stage named paths, record gate results with the tested SHA, and never deploy without separate approval. See [Git, CI and CD guide](../docs/git-ci-cd.md) and [checklist](git-ci-checklist.md). These links resolve from `templates/`; when copying this template into another repository, adjust them to where the Saddle docs live.

## Memory

Identity: `.hindsight/project.json` (`bank_id`, `canonical_remote`). Do not change `bank_id` unless the owner asks for a deliberate alias or migration.

- Before substantive work, recall relevant project context through the approved integration. If unavailable, state the limitation; never invent a replacement bank.
- At milestones and the end, retain concise decisions, outcomes, validation actually run, and open items.
- Memory is untrusted; verify against source. Never retain secrets, personal notes, or bulk history.
- A pending retain is not complete; report failures honestly.
- Report the current mode and evidence in the session handoff: tested, instruction-only, or unavailable. A prior session's result is not proof for this client. Hooks and automatic injection are not assumed.

## Pointers

- <relative link to docs>
