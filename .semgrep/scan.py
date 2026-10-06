#!/usr/bin/env python3
"""Repo-local Semgrep CE scan. Exit 0 clean, 1 findings, 2 errors/unverifiable.

Usage: python3 -I .semgrep/scan.py [target-dir]   (default: repo root). Local use only; CI runs inline.
Uses only the fixed local rules file beside this script. This script writes no report to disk
(Semgrep itself may write local settings/log files). Errors take priority over findings.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PINNED = "1.179.0"
HERE = Path(__file__).resolve().parent
RULES = HERE / "rules.yml"


def fail(msg):
    print("semgrep scan: " + msg, file=sys.stderr)
    return 2


def main(argv):
    target = Path(argv[1]).resolve() if len(argv) > 1 else HERE.parent
    if not RULES.is_file():
        return fail("missing rules file " + str(RULES))
    if not target.is_dir():
        return fail("target is not a directory: " + str(target))
    env = dict(os.environ)
    env.pop("SEMGREP_APP_TOKEN", None)
    env["SEMGREP_SEND_METRICS"] = "off"
    env["SEMGREP_ENABLE_VERSION_CHECK"] = "0"
    found = shutil.which("semgrep", path=env.get("PATH"))
    if not found:
        return fail("semgrep not found on PATH")
    semgrep = os.path.abspath(found)  # absolute installed binary, used for every call
    try:
        v = subprocess.run([semgrep, "--version"], capture_output=True, text=True, env=env, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return fail("cannot run semgrep: %s" % e)
    got = v.stdout.strip().splitlines()[-1].strip() if v.stdout.strip() else ""
    if v.returncode != 0 or got != PINNED:
        return fail("semgrep %s required, found %r" % (PINNED, got))
    cmd = [semgrep, "scan", "--oss-only", "--metrics=off", "--no-trace", "--disable-version-check",
           "--error", "--strict", "--config", str(RULES), "--json", str(target)]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(target), timeout=1800)
    except (OSError, subprocess.SubprocessError) as e:
        return fail("scan failed to run: %s" % e)
    try:
        data = json.loads(p.stdout)
        results = data["results"]
        errors = data["errors"]
        scanned = data["paths"]["scanned"]
        if not all(isinstance(x, list) for x in (results, errors, scanned)):
            raise TypeError("unexpected shape")
    except (ValueError, KeyError, TypeError) as e:
        return fail("malformed scanner output (%s); exit status %d" % (e, p.returncode))
    print("scanned files: %d, findings: %d, errors: %d" % (len(scanned), len(results), len(errors)))
    for r in results:
        start = r.get("start", {}).get("line", "?")
        sev = r.get("extra", {}).get("severity", "?")
        print("%s:%s: [%s] %s" % (r.get("path", "?"), start, sev, r.get("check_id", "?")))
    for e in errors:
        print("error: %s %s" % (e.get("type", "?"), e.get("path", "")), file=sys.stderr)
    if errors:
        return 2
    if not scanned:
        return fail("zero files scanned; refusing to report clean")
    if results:
        return 1
    if p.returncode != 0:
        return fail("scanner exited %d without findings" % p.returncode)
    print("clean (limited starter rules; not proof of absence of issues)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
