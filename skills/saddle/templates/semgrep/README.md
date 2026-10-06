# Semgrep (Saddle starter)

Repo-local Semgrep Community Edition scan, pinned to Semgrep 1.179.0 (Python 3.12 recommended).
CI: `.github/workflows/semgrep.yml` (GitHub-hosted `ubuntu-latest`, read-only, no secrets, nothing uploaded).

## Limited coverage
Starter rules in `rules.yml` (MIT, local only, no registry) are high-confidence and few:

| Rule | Language | Severity |
|---|---|---|
| `saddle.python.subprocess-shell-true` | Python | ERROR |
| `saddle.javascript.eval` | JS/TS | ERROR |
| `saddle.javascript.child-process-exec` | JS/TS | WARNING (explicit `child_process.exec` / `require("child_process").exec` only) |
| `saddle.php.eval` | PHP | ERROR |

Uncovered: Rust (no robust shell-execution rule), every other language, secrets, dependencies (no SCA),
and cross-file analysis (CE analyses one function at a time). A clean run is **not** proof the code is
safe. Add rules deliberately; do not claim more than they detect.

Rust, Dart, Swift, Shell, SQL and Astro have no coverage. Semgrep prefilters files that contain no
rule-relevant tokens, so unparsable code may go unreported; this is not a syntax validator. Keep
running language-native checks (compiler, linter, tests).

## Scanner and privacy
Only the Semgrep engine is pinned (1.179.0); its dependencies are not locked. No account or token is
needed. Rules are local; metrics, version-check and trace are off; no source is uploaded. The local script
writes no report files, but Semgrep itself may write local logs or settings. The CI workflow uses a
GitHub-hosted runner, an exact-SHA action pin and inline isolated Python, and never runs PR-provided helpers.
Only if a Mac sandbox yields empty trust anchors, set `SSL_CERT_FILE=/etc/ssl/cert.pem`. Never disable TLS.

## Ignored files
`.semgrepignore` (created only if absent) excludes `node_modules/`, `vendor/`, `.venv/`, `build/`, `dist/`.
Tests are scanned. `.gitignore` is respected. An existing `.semgrepignore` is never changed.

## Run locally (local use only; CI never runs this helper)
```
python3 -m venv .venv-semgrep && .venv-semgrep/bin/pip install semgrep==1.179.0   # needs network
PATH="$PWD/.venv-semgrep/bin:$PATH" python3 .semgrep/scan.py                       # offline
```
Install `.venv-semgrep` outside the repo or gitignore it. Exit codes: 0 clean, 1 findings, 2 errors,
wrong version, zero files scanned, malformed output or scanner failure. Output has counts and
`path:line [severity] rule-id` only, no source snippets. `SEMGREP_APP_TOKEN` is removed and metrics are off.
