"""Read-only paginated review audit collector (standard library only).

Audit input for a FUTURE trusted reviewer adapter, not a merge gate.
Transport authentication/authorization belongs to the trusted runtime that
supplies `get` and `threads`; this pure code cannot validate credentials.
The snapshot is not atomic; final merge must use protected GitHub enforcement.
Successful audits are always ineligible (review_attestation_missing): mutable
summaries/reactions do not prove immutable completed code+security review.
PR text is never interpreted and never emitted.
"""
import hashlib
import json
import re

_REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
_SHA = re.compile(r"[0-9a-f]{40}")


class _Bad(Exception):
    pass


def _need(ok):
    if not ok:
        raise _Bad()


def _int(v, lo=1):
    return type(v) is int and v >= lo


def _fail(code):
    return {"eligible": False, "reasons": [code]}


def _pr_state(p, repo, pr):
    _need(isinstance(p, dict) and _int(p.get("id")))
    _need(p.get("number") == pr and _int(p.get("number")))
    h, b = p.get("head"), p.get("base")
    _need(isinstance(h, dict) and isinstance(b, dict))
    for s in (h.get("sha"), b.get("sha")):
        _need(isinstance(s, str) and _SHA.fullmatch(s))
    hr, br = h.get("repo"), b.get("repo")
    _need(isinstance(hr, dict) and isinstance(br, dict))
    _need(hr.get("full_name") == repo and br.get("full_name") == repo)
    _need(p.get("state") == "open" and p.get("draft") is False)
    _need(_int(p.get("changed_files"), 0))
    return {"id": p["id"], "number": pr, "repo": repo, "head": h["sha"], "base": b["sha"],
            "state": "open", "draft": False, "changed_files": p["changed_files"]}


def _pages(get, path, key, wrap=False):
    items, total = [], None
    for n in range(1, 101):
        d = get("%s?per_page=100&page=%d" % (path, n))
        if wrap:
            _need(isinstance(d, dict) and _int(d.get("total_count"), 0))
            _need(total in (None, d["total_count"]))
            total, d = d["total_count"], d.get("check_runs")
        _need(isinstance(d, list) and len(d) <= 100)
        _need(all(isinstance(x, dict) for x in d))
        items += d
        if len(d) < 100:
            break
    else:
        raise _Bad()  # truncated at the 100 page bound
    if wrap:
        _need(len(items) == total)
    if key == "filename":
        ids = [x.get("filename") for x in items]
        _need(all(isinstance(i, str) and i for i in ids))
    else:
        ids = [x.get(key) for x in items]
        _need(all(_int(i) for i in ids))
    _need(len(set(ids)) == len(ids))
    return items


def _check_threads(threads, comments):
    _need(isinstance(threads, list))
    rest = {c["id"] for c in comments}
    parent = {c["id"]: c.get("in_reply_to_id") for c in comments}
    roots = {c["id"] for c in comments if c.get("in_reply_to_id") is None}
    # replies must carry an exact positive int pointing at a top-level comment
    _need(all(p is None or (_int(p) and p in roots) for p in parent.values()))
    seen_t, seen_c = set(), set()
    for t in threads:
        _need(isinstance(t, dict) and isinstance(t.get("is_resolved"), bool))
        _need(isinstance(t.get("is_outdated"), bool))
        tid = t.get("id")
        _need(isinstance(tid, (str, int)) and not isinstance(tid, bool) and tid != "")
        _need(tid not in seen_t)
        seen_t.add(tid)
        cs = t.get("comments")
        _need(isinstance(cs, list) and cs and all(isinstance(c, dict) for c in cs))
        ids = [c.get("database_id") for c in cs]
        _need(all(_int(i) for i in ids) and not seen_c & set(ids))
        _need(len(set(ids)) == len(ids))
        seen_c |= set(ids)
        _need(len(roots & set(ids)) == 1)
        # every reply must point at this thread's own root
        root = next(iter(roots & set(ids)))
        _need(all(parent.get(i) in (None, root) for i in ids if i in parent))
    _need(seen_c == rest)


def _collect(get, threads, repo, pr):
    _need(isinstance(repo, str) and repo.isascii() and _REPO.fullmatch(repo))
    _need(not any(p in (".", "..") for p in repo.split("/")))
    _need(_int(pr))
    base = "/repos/%s/pulls/%d" % (repo, pr)
    before = _pr_state(get(base), repo, pr)
    comments = _pages(get, base + "/comments", "id")
    reviews = _pages(get, base + "/reviews", "id")
    files = _pages(get, base + "/files", "filename")
    issue = _pages(get, "/repos/%s/issues/%d/comments" % (repo, pr), "id")
    checks = _pages(get, "/repos/%s/commits/%s/check-runs" % (repo, before["head"]),
                    "id", wrap=True)
    th = threads(repo, pr)
    _check_threads(th, comments)
    _need(len(files) == before["changed_files"])
    _need(_pr_state(get(base), repo, pr) == before)
    snap = {"pr": before, "comments": comments, "reviews": reviews, "files": files,
            "issue_comments": issue, "check_runs": checks, "threads": th}
    digest = hashlib.sha256(json.dumps(
        snap, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    keep = ("filename", "status", "additions", "deletions", "changes",
            "previous_filename")
    return {"eligible": False, "reasons": ["review_attestation_missing"],
            "repo": repo, "pr": pr, "head_sha": before["head"],
            "base_sha": before["base"], "snapshot_sha256": digest,
            "counts": {"review_comments": len(comments), "reviews": len(reviews),
                       "files": len(files), "issue_comments": len(issue),
                       "check_runs": len(checks), "threads": len(th)},
            "unresolved_count": sum(not t["is_resolved"] for t in th),
            "changes_requested": sum(r.get("state") == "CHANGES_REQUESTED"
                                     for r in reviews),
            "files": [{k: f.get(k) for k in keep} for f in files]}


def collect(get, threads, repo, pr):
    """Return a redacted audit dict; never raises, never leaks error details."""
    try:
        return _collect(get, threads, repo, pr)
    except _Bad:
        return _fail("invalid_audit_data")
    except Exception:
        return _fail("collection_failed")
