"""Offline exact-head evidence validator.

Trust boundary: the caller supplies authenticated API snapshots; JSON flags
alone cannot authenticate a reviewer. An empty result is validation only and
is never authorization. Reason codes are fixed strings; input is never echoed.
"""
import re

_SHA = re.compile(r"[0-9a-f]{40}\Z")
KINDS = ("code", "security")


def _sha(v):
    return isinstance(v, str) and bool(_SHA.match(v))


def _int(v, minimum):
    return type(v) is int and v >= minimum


def _checks(ev, head, base, out):
    req = ev.get("required_checks")
    checks = ev.get("checks")
    if not isinstance(req, dict) or not req or not all(
            isinstance(k, str) and k and _int(v, 1) for k, v in req.items()):
        out.append("required_checks_invalid")
        return
    if not isinstance(checks, list):
        out.append("checks_invalid")
        return
    for name, app in req.items():
        got = [c for c in checks if isinstance(c, dict) and c.get("name") == name]
        if len(got) != 1:
            out.append("check_missing_or_duplicate")
            continue
        c = got[0]
        if not (c.get("tested_sha") == head and c.get("base_sha") == base
                and c.get("app_id") == app and type(c.get("app_id")) is int
                and c.get("status") == "completed"
                and c.get("conclusion") == "success"):
            out.append("check_not_passing")


def _reviews(ev, head, base, actor, kinds, out):
    reviews = ev.get("reviews")
    if not isinstance(reviews, list):
        out.append("reviews_invalid")
        return
    for kind in kinds:
        got = [r for r in reviews if isinstance(r, dict) and r.get("kind") == kind]
        if len(got) != 1:
            out.append("review_missing_or_duplicate")
            continue
        r = got[0]
        run = r.get("run_id")
        if not (type(r.get("reviewer_actor_id")) is int
                and r.get("reviewer_actor_id") == actor
                and r.get("reviewed_sha") == head and r.get("base_sha") == base
                and r.get("status") == "completed"
                and isinstance(run, str) and run
                and type(r.get("findings_count")) is int
                and r.get("findings_count") == 0):
            out.append("review_not_passing")


def validate(evidence, expected_head, expected_base, expected_actor, required_kinds):
    """Return a list of fixed reason codes; empty iff evidence is complete."""
    if not (_sha(expected_head) and _sha(expected_base) and _int(expected_actor, 1)):
        return ["expected_invalid"]
    if (not isinstance(required_kinds, (list, tuple, set, frozenset))
            or not required_kinds
            or not all(isinstance(k, str) and k in KINDS for k in required_kinds)
            or len(set(required_kinds)) != len(required_kinds)
            or "code" not in required_kinds):
        return ["required_kinds_invalid"]
    if not isinstance(evidence, dict):
        return ["evidence_invalid"]
    out = []
    if evidence.get("complete") is not True:
        out.append("evidence_incomplete")
    for key, want in (("head_sha", expected_head), ("current_head_sha", expected_head),
                      ("base_sha", expected_base), ("current_base_sha", expected_base)):
        if evidence.get(key) != want:
            out.append("sha_mismatch:" + key)
    _checks(evidence, expected_head, expected_base, out)
    _reviews(evidence, expected_head, expected_base, expected_actor,
             sorted(required_kinds), out)
    n = evidence.get("unresolved_count")
    if not _int(n, 0):
        out.append("unresolved_count_invalid")
    elif n:
        out.append("unresolved_threads")
    cr = evidence.get("changes_requested")
    if not isinstance(cr, bool):
        out.append("changes_requested_invalid")
    elif cr:
        out.append("changes_requested")
    return out
