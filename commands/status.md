# *status

Report harness health.

## Behavior

Run each check, report pass/warn:

1. **Scratchpad** — `.claude/scratchpad.md` exists + fresh. Fresh = mtime ≥ newest vault session log for this repo. Older → warn "scratchpad stale, session-end overwrite missed"
2. **Graph** — `graphify-out/graph.json` present, node count > 0
3. **Gitignore** — `.gitignore` covers `graphify-out/`
4. **Pointers** — `CLAUDE.md` pointers resolve
5. **Session log** — newest vault session log for this repo located and reported

## Output

```
Harness Status — [repo name]
Checked: [date]

Scratchpad    [✓ fresh | ⚠ stale, session-end overwrite missed | ✗ missing]
Graph         [✓ N nodes | ✗ graph.json missing | ✗ 0 nodes]
Gitignore     [✓ graphify-out/ covered | ⚠ graphify-out/ not ignored]
Pointers      [✓ CLAUDE.md resolves | ⚠ N broken pointers]
Session log   [✓ Sessions/YYYY-MM-DD-<repo>-<topic>.md | ⚠ none found]
```

After the report, offer a full `brainscan` rerun for deep audit.

## If Not Onboarded

No `.claude/scratchpad.md` AND no `graphify-out/`:

```
Harness not installed. Run *onboard to build one.
```
