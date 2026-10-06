#!/usr/bin/env python3
"""Install the Saddle Semgrep templates into a git repo.

Usage: wire-semgrep.py [--check] [repo]
Exit 0 ok / installed / already installed, 1 conflict or not installed (--check), 2 usage/safety error.
Copies exact template bytes; never overwrites differing files; all conflicts are checked before writes.
The repo path must be a git root (verified with read-only `git rev-parse`) and must not contain symlinks.
"""
import os
import stat
import subprocess
import sys
from pathlib import Path

T = Path(__file__).resolve().parent.parent / "templates" / "semgrep"
FILES = [
    ("rules.yml", ".semgrep/rules.yml"),
    ("gitlab-rules.yml", ".semgrep/gitlab-rules.yml"),
    ("LICENSE.gitlab", ".semgrep/LICENSE.gitlab"),
    ("gitlab-manifest.json", ".semgrep/gitlab-manifest.json"),
    ("scan.py", ".semgrep/scan.py"),
    ("README.md", ".semgrep/README.md"),
    ("workflow.yml", ".github/workflows/semgrep.yml"),
]
IGNORE = (b"# Saddle Semgrep: dependency/build output only. Tests are scanned.\n"
          b"node_modules/\nvendor/\n.venv/\nbuild/\ndist/\n")


def unresolved_root(arg):
    """Absolute path without resolving; refuse any symlink component. Returns (path, error)."""
    p = os.path.abspath(arg)
    cur = os.path.sep
    for part in [x for x in p.split(os.path.sep) if x]:
        cur = os.path.join(cur, part)
        try:
            st = os.lstat(cur)
        except OSError as e:
            return None, "cannot inspect %s: %s" % (cur, e)
        if stat.S_ISLNK(st.st_mode):
            return None, "symlink in repo path: %s" % cur
        if not stat.S_ISDIR(st.st_mode):
            return None, "not a directory: %s" % cur
    return p, None


def is_git_root(root):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        r = subprocess.run(["git", "--no-optional-locks", "-C", root, "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, env=env, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0 and os.path.realpath(r.stdout.strip()) == os.path.realpath(root)


def inspect(root, rel, data, exact):
    """Return (conflict_or_None, needs_write). Uses lstat on every component; no writes."""
    cur = Path(root)
    parts = rel.parts
    for i, part in enumerate(parts):
        cur = cur / part
        try:
            st = os.lstat(cur)
        except FileNotFoundError:
            return None, True  # nothing below can exist
        except OSError as e:
            return "%s: cannot inspect %s: %s" % (rel, part, e), False
        if stat.S_ISLNK(st.st_mode):
            return "%s: symlink at %s" % (rel, Path(*parts[:i + 1])), False
        last = i == len(parts) - 1
        if not last and not stat.S_ISDIR(st.st_mode):
            return "%s: parent %s is not a directory" % (rel, Path(*parts[:i + 1])), False
        if last:
            if not stat.S_ISREG(st.st_mode):
                return "%s: not a regular file" % rel, False
            if exact and cur.read_bytes() != data:
                return "%s: differs from template; review manually" % rel, False
            return None, False
    return None, True


def main(argv):
    args = argv[1:]
    check = "--check" in args
    args = [a for a in args if a != "--check"]
    if len(args) > 1:
        print("usage: wire-semgrep.py [--check] [repo]", file=sys.stderr)
        return 2
    root, err = unresolved_root(args[0] if args else ".")
    if err:
        print("refusing: " + err, file=sys.stderr)
        return 2
    if not is_git_root(root):
        print("not a git root: %s" % root, file=sys.stderr)
        return 2
    missing = [src for src, _ in FILES if not (T / src).is_file()]
    if missing:
        print("missing template files (broader rule bundle must be present): " + ", ".join(missing),
              file=sys.stderr)
        return 2
    plan = [(Path(dst), (T / src).read_bytes(), True) for src, dst in FILES]
    plan.append((Path(".semgrepignore"), IGNORE, False))  # presence only
    conflicts, todo = [], []
    for rel, data, exact in plan:
        conflict, write = inspect(root, rel, data, exact)
        if conflict:
            conflicts.append(conflict)
        elif write:
            todo.append((rel, data))
    for c in conflicts:
        print("CONFLICT " + c, file=sys.stderr)
    if conflicts:
        return 1
    if check:
        for rel, _ in todo:
            print("missing " + str(rel))
        print("semgrep: not installed" if todo else "semgrep: installed")
        return 1 if todo else 0
    for rel, data in todo:
        path = Path(root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "xb") as f:
            f.write(data)
        if path.name == "scan.py":
            os.chmod(path, 0o755)
        print("wrote " + str(rel))
    if not todo:
        print("semgrep: already installed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
