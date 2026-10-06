# Semgrep (Saddle baseline)

Repo-local Semgrep Community Edition scan, pinned to Semgrep 1.179.0 (Python 3.12 recommended).
CI: `.github/workflows/semgrep.yml` (GitHub-hosted `ubuntu-latest`, read-only, no secrets, nothing uploaded).

## Limited coverage
84 local rules, all MIT, no runtime Registry download:

- **79 upstream GitLab rules** (68 Python, 11 JS/TS) from
  <https://gitlab.com/gitlab-org/security-products/sast-rules> pinned to commit
  `53bf5cf6df3c51b6c02110f5a638b5e6213666cd`. Each upstream YAML file carries an explicit
  `# License: MIT (c) GitLab Inc.` header. `gitlab-rules.yml` mechanically aggregates their unchanged
  parsed mappings. `LICENSE.gitlab` keeps the notice; `gitlab-manifest.json` records upstream paths,
  SHA256 per file and the aggregate hash. `rules/gitlab` (EE), `rules/lgpl*` and all restricted sources
  are excluded.
- **5 custom Saddle rules**: Python input-to-shell taint (`saddle.python.input-to-shell`), Python
  `shell=True` audit (WARNING), shell audit, JS eval/exec, and PHP `eval`.

Covered: Python TLS certificate verification, unsafe deserialization, dynamic SQL construction, SSH,
tempfile and weak crypto; JS/TS eval, path/dynamic require, ReDoS, React/mustache XSS and buffers. Many
JS upstream warnings are audit under the upstream severity policy. PHP is the custom `eval` rule only,
not broad coverage. JS/TS script portions outside `.astro` files may be covered; `.astro` is not scanned.

Uncovered: Rust, Dart, Swift, C++, SQL, Shell and Astro templates, secrets, dependencies (no SCA) and
interfile analysis (CE analyses one function at a time). A clean run is **not** proof the code is
safe. Add rules deliberately; do not claim more than they detect.

Semgrep prefilters files that contain no rule-relevant tokens, so unparsable code may go unreported; this
is not a syntax validator. Keep native compilers, linters and tests.

## Blocking policy
Every finding stays visible. ERROR findings block. WARNING and INFO are audit, not automatically harmless;
serious warnings still need review. One exact upstream rule,
`python_exec_rule-subprocess-popen-shell-true`, is audit-only: generic wrapper parameters may receive only
constants, and CE single-function analysis cannot prove interprocedural flow. The custom `shell=True` rule is a
WARNING audit. `saddle.python.input-to-shell` blocks real Python `input()` / `sys.argv` flowing into
`shell=True` or `os.system` within one function (not every possible source, nor cross-function flow).

## Upgrading rules
1. Fetch the new upstream revision in a scratch directory.
2. Review each file's own license (the root license is not sufficient); select MIT rules explicitly.
3. Preserve the notice; record each path and raw SHA256.
4. Aggregate, check semantic equality with the upstream parsed mappings, and compute the bundle hash.
5. Validate configs, upstream fixtures, clean/vulnerable/error tests, and full-scan reports on exact heads.
6. Review the policy before adopting the update.

The installer never replaces a differing repo config; it reports the conflict for a reviewed upgrade and has
no silent force option. It installs no machine hooks and registers no runners.

## Test status
Upstream fixtures currently pass for 64/64 Python and 8/8 JS test groups. Some rules have no upstream
annotated cases, so not all 79 are individually regression tested. 17 earlier integration tests passed; new
tests are pending, so no new pass count is recorded here.

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
Install `.venv-semgrep` outside the repo or gitignore it. Exit codes: 0 no blocking findings (audit-only findings may exist; not "clean"), 1 blocking
findings, 2 errors, wrong version, zero files scanned, malformed output or abnormal scanner exit. Output has counts and
`path:line [severity] rule-id` only, no source snippets. `SEMGREP_APP_TOKEN` is removed and metrics are off.
