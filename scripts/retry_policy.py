"""Retry ledger and conservative path/size policy (standard library only)."""
import os
import re
import sqlite3
from fnmatch import fnmatchcase

_FLAGS = {"auth", "security", "migration", "dependency", "publicapi", "productbehavior"}
_REPO = re.compile(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+")
_SHA40 = re.compile(r"[0-9a-f]{40}")
_SHA64 = re.compile(r"[0-9a-f]{64}")
MAX_RESERVATIONS = 2


def _int(v):
    return type(v) is int and v >= 0


def _path_ok(p):
    if not isinstance(p, str) or not p or not p.isascii() or "\\" in p:
        return False
    if any(ord(c) < 32 or ord(c) == 127 for c in p):
        return False
    parts = p.split("/")
    return not any(x in ("", ".", "..") for x in parts) and not p.startswith("/")


def _globs(v):
    return isinstance(v, list) and all(isinstance(g, str) and g for g in v)


def classify(files, policy):
    """Return True only if changed files pass path and size bounds.

    This classifier bounds paths/size ONLY. A default path allow is not
    semantic certification; a separate trusted semantic owner assessment is
    required before any auto fixing.
    """
    try:
        if not isinstance(policy, dict) or not isinstance(files, list) or not files:
            return False
        allow, deny = policy["allow"], policy["deny"]
        if not (_globs(allow) and _globs(deny) and allow):
            return False
        if not (_int(policy["max_files"]) and _int(policy["max_lines"])):
            return False
        if len(files) > policy["max_files"]:
            return False
        seen, lines = set(), 0
        for f in files:
            if not isinstance(f, dict):
                return False
            name = f["filename"]
            if not _path_ok(name) or name in seen:
                return False
            seen.add(name)
            if f["status"] not in ("modified", "added"):
                return False
            if f.get("previous_filename") is not None:
                return False
            if not (_int(f["additions"]) and _int(f["deletions"])):
                return False
            lines += f["additions"] + f["deletions"]
            for k, v in f.items():
                if isinstance(k, str) and k.lower().replace("_", "") in _FLAGS and v is not False:
                    return False
            if name.split("/")[0].lower() == ".github":
                return False
            if any(fnmatchcase(name, g) for g in deny):
                return False
            if not any(fnmatchcase(name, g) for g in allow):
                return False
        return lines <= policy["max_lines"]
    except (KeyError, TypeError, ValueError):
        return False


def reserve(db_path, repo, pr, root_head, attempt_head, policy_hash):
    """Consume one of two lifetime slots per repo+PR; return id or None.

    Slots are never reset, crashes stay consumed. A reservation is not merge
    authority; fresh evidence and independent re-review are still required.
    """
    if not isinstance(repo, str) or not _REPO.fullmatch(repo):
        raise ValueError("bad repo")
    if any(c in (".", "..") for c in repo.split("/")):
        raise ValueError("bad repo")
    repo = repo.lower()
    if type(pr) is not int or pr <= 0:
        raise ValueError("bad pr")
    for h in (root_head, attempt_head):
        if not isinstance(h, str) or not _SHA40.fullmatch(h):
            raise ValueError("bad head")
    if not isinstance(policy_hash, str) or not _SHA64.fullmatch(policy_hash):
        raise ValueError("bad policy hash")
    if not isinstance(db_path, (str, os.PathLike)):
        raise ValueError("bad db_path")
    db_file = os.fspath(db_path)
    if not isinstance(db_file, str) or not db_file or "\0" in db_file or not os.path.isabs(db_file):
        raise ValueError("bad db_path")
    con = sqlite3.connect(db_file, timeout=30, isolation_level=None)
    try:
        con.execute("BEGIN IMMEDIATE")
        try:
            con.execute(
                "CREATE TABLE IF NOT EXISTS attempts (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                " repo TEXT NOT NULL, pr INTEGER NOT NULL, root_head TEXT NOT NULL,"
                " attempt_head TEXT NOT NULL, policy_hash TEXT NOT NULL,"
                " UNIQUE (repo, pr, attempt_head))")
            dup = con.execute(
                "SELECT 1 FROM attempts WHERE repo=? AND pr=? AND attempt_head=?",
                (repo, pr, attempt_head)).fetchone()
            n = con.execute("SELECT COUNT(*) FROM attempts WHERE repo=? AND pr=?",
                            (repo, pr)).fetchone()[0]
            if dup or n >= MAX_RESERVATIONS:
                con.execute("ROLLBACK")
                return None
            rid = con.execute(
                "INSERT INTO attempts (repo, pr, root_head, attempt_head, policy_hash)"
                " VALUES (?,?,?,?,?)",
                (repo, pr, root_head, attempt_head, policy_hash)).lastrowid
            con.execute("COMMIT")
            return rid
        except BaseException:
            if con.in_transaction:
                con.execute("ROLLBACK")
            raise
    finally:
        con.close()
