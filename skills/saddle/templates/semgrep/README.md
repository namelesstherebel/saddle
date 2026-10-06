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
- **5 custom Saddle rules**: Python `shell=True` audit (WARNING), Python input-to-shell taint
  (`saddle.python.input-to-shell`), JS `eval`, JS `child_process.exec`, and PHP `eval`.

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
Scans run with `--disable-nosem` (CI and local), so `nosemgrep` comments cannot suppress any finding,
including input-to-shell.

## Upgrading rules
1. Fetch the new upstream revision in a scratch directory.
2. Review each file's own license (the root license is not sufficient); select MIT rules explicitly.
3. Preserve the notice; record each path and raw SHA256.
4. Aggregate, check semantic equality with the upstream parsed mappings, and compute the bundle hash.
5. Validate configs, upstream fixtures, clean/vulnerable/error tests, and full-scan reports on exact heads.
6. Review the policy before adopting the update.

The Saddle installer (an external adopter source, not necessarily present in each adopter repo) never
replaces a differing repo config; it reports the conflict for a reviewed upgrade and has no silent force
option. It rejects unknown option tokens with usage and exit 2. It installs no machine hooks and registers
no runners.

## Test status
Upstream fixtures currently pass for 64/64 Python and 8/8 JS test groups. Some rules have no upstream
annotated cases, so not all 79 are individually regression tested. The reviewed coverage corrections
passed 30/30 tested regressions; this is a local checkpoint recorded at policy commit
`f860066c2ef3269bae105c00488694215a9a973a`, not a guarantee for future remote changes.

Coverage notes: the Python sink rule matches both positional and keyword `args=` forms. The local scan
helper rejects surplus scanner arguments (exit 2).

## CI trusted policy
CI fetches `namelesstherebel/saddle` at the fixed public commit
`f860066c2ef3269bae105c00488694215a9a973a` into `.semgrep-policy` (same pinned checkout action,
`persist-credentials: false`); the PR head stays checked out in the root. Both rule files load only from the
policy checkout, after SHA256 verification (`rules.yml` `e26005346a43b83bb7f0ba00586f7e10600803bdb120b0c818705d13986469f6`,
`gitlab-rules.yml` `01e5294fec95488f7b89b4e5810b5cd987c56eb80379ab2a219a5bbde3f87c35`, unchanged; the trusted
`.semgrepignore` `5c368ad2f54a6f9424f5d80f4f0d66f056ae2711533cdcf34f72259d9a77e982` is verified too). A missing,
unavailable or corrupted policy fails clearly. No code from the policy checkout or the PR project is executed.
Pin and digests are intentionally fixed; upgrades need review.

Before scanning, PR `.semgrepignore` files (nested and symlinked too; symlinks, `.git` and the policy checkout
are not traversed) are neutralized in the ephemeral checkout and the trusted ignore is copied to the root.
App source is unchanged. CI passes `--no-git-ignore`, so Git-ignore rules cannot hide tracked files.
Fixed excludes are root-anchored: `/.semgrep`, `/.semgrep-policy`, `/skills/saddle/templates/semgrep`,
`/.venv-semgrep`; these cover only scanner tooling, templates and dependencies. Nested same-name app
directories (e.g. `src/.semgrep`) are still scanned, as are tests and app source. Other trusted dependency
exclusions come from the trusted `.semgrepignore` and are unchanged.
`--max-target-bytes 0` disables Semgrep's silent file-size filter, so large files are scanned; timeouts and
scanner errors still fail the run (exit 2).

Boundary: CI is not tamperproof against a PR that edits the workflow itself; human review remains necessary
unless branch protections are separately authorized. No new security settings or `pull_request_target`.
Local runs use the repo's local policies instead, and only on trusted target directories.

## Scanner and privacy
Only the Semgrep engine is pinned (1.179.0); its dependencies are not locked. No account or token is
needed. Rules are local; metrics, version-check and trace are off; no source is uploaded. The local script
writes no report files, but Semgrep itself may write local logs or settings. The CI workflow uses a
GitHub-hosted runner, an exact-SHA action pin and inline isolated Python, and never runs PR-provided helpers.
Only if a Mac sandbox yields empty trust anchors, set `SSL_CERT_FILE=<path-to-trusted-CA-bundle>` (platform-specific). Never disable TLS.

## Ignored files
`.semgrepignore` (created only if absent) excludes `node_modules/`, `vendor/`, `.venv/`, `build/`, `dist/`,
plus `.venv-semgrep/` and the tooling `.semgrep/`. Tests are scanned. An existing user `.semgrepignore` is
never changed. In CI the trusted ignore replaces PR ignores and git-ignore is disabled (see CI trusted policy).

## Run locally (local use only; CI never runs this helper)
```
python3 -I -m venv .venv-semgrep && .venv-semgrep/bin/python -I -m pip install semgrep==1.179.0   # needs network
PATH="$PWD/.venv-semgrep/bin:$PATH" python3 -I .semgrep/scan.py                                  # offline
```
Run only on a trusted target directory. `.venv-semgrep` and scanner tooling are excluded from scanning.
Local Git-ignore handling is explicit: trusted local runs use the local ignore files, but tracked files are
not hidden by Git-ignore; CI disables Git-ignore entirely (`--no-git-ignore`).
Exit codes: 0 no blocking findings (limited coverage; audit-only findings may exist; never "clean"), 1 blocking
findings, 2 errors, wrong version, no eligible non-tooling source file scanned, malformed output or abnormal scanner exit. Output has counts and
`path:line [severity] rule-id` only, no source snippets. `SEMGREP_APP_TOKEN` is removed and metrics are off.
`SEMGREP_BASELINE_COMMIT` and `SEMGREP_BASELINE_REF` are ignored (removed from the scan environment) by the
local helper, so local scans are always full scans, never baseline-only.
