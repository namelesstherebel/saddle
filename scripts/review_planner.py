"""Dry-run review planner: a pure decision state machine.

It is NOT authorization or execution. Policy, assessment and evidence must come
from a future authenticated host adapter; PR JSON/prose is never consulted.
Template deploymentTarget remains null and GitHub branch protection stays the
final authority. Callers must re-read head/base before any future effect.
"""
import copy
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exact_head  # noqa: E402
import retry_policy  # noqa: E402

BLOCKED, OWNER, FIX, MERGE = "blocked", "owner_required", "fix_candidate", "merge_candidate"
_SHA40 = re.compile(r"[0-9a-f]{40}")
_SHA64 = re.compile(r"[0-9a-f]{64}")
_TIERS = ("editorial", "small_internal_fix")


def _sha(v, rx=_SHA40):
    return isinstance(v, str) and bool(rx.fullmatch(v))


def _nn(v):
    return type(v) is int and v >= 0


def _policy_ok(p):
    return (isinstance(p, dict) and isinstance(p.get("repository"), str) and p["repository"]
            and type(p.get("actor_id")) is int and p["actor_id"] >= 1
            and isinstance(p.get("required_checks"), dict)
            and isinstance(p.get("required_kinds"), list)
            and isinstance(p.get("files"), dict) and _sha(p.get("policy_hash"), _SHA64))


def _snap_ok(s, p):
    return (isinstance(s, dict) and s.get("repository") == p["repository"]
            and type(s.get("pr")) is int and s["pr"] > 0
            and _sha(s.get("head_sha")) and _sha(s.get("base_sha"))
            and s.get("state") == "open" and s.get("draft") is False
            and s.get("fork") is False and isinstance(s.get("files"), list)
            and isinstance(s.get("evidence"), dict))


def _assessment_ok(a, s, p):
    return (isinstance(a, dict) and a.get("head_sha") == s["head_sha"]
            and a.get("base_sha") == s["base_sha"]
            and a.get("policy_hash") == p["policy_hash"]
            and a.get("tier") in _TIERS and a.get("excluded") == [])


def decide(snapshot, policy, assessment):
    """Return one of blocked, owner_required, fix_candidate, merge_candidate."""
    try:
        return _decide(snapshot, policy, assessment)
    except Exception:  # malformed input fails closed
        return BLOCKED


def _decide(snapshot, policy, assessment):
    if not _policy_ok(policy) or not _snap_ok(snapshot, policy):
        return BLOCKED
    if not _assessment_ok(assessment, snapshot, policy):
        return OWNER
    if retry_policy.classify(snapshot["files"], policy["files"]) is not True:
        return OWNER
    head, base = snapshot["head_sha"], snapshot["base_sha"]
    ev = copy.deepcopy(snapshot["evidence"])
    ev["required_checks"] = dict(policy["required_checks"])  # host override
    args = (head, base, policy["actor_id"], policy["required_kinds"])
    if not exact_head.validate(ev, *args):
        return MERGE
    # Fix path: validate counts first, then re-validate with them zeroed.
    unresolved, reviews = ev.get("unresolved_count"), ev.get("reviews")
    if not _nn(unresolved) or not isinstance(reviews, list):
        return BLOCKED
    total = 0
    for r in reviews:
        if not isinstance(r, dict) or not _nn(r.get("findings_count")):
            return BLOCKED
        if r.get("kind") in policy["required_kinds"]:
            total += r["findings_count"]
    zeroed = copy.deepcopy(ev)
    zeroed["unresolved_count"] = 0
    for r in zeroed["reviews"]:
        r["findings_count"] = 0
    errors = exact_head.validate(zeroed, *args)
    if any(e != "changes_requested" for e in errors):
        return BLOCKED
    if ev.get("changes_requested") is not False:
        return OWNER
    return FIX if total > 0 else OWNER


def reserve_fix(snapshot, policy, assessment, db_path):
    """Consume a retry slot only for fix_candidate; return id or None.

    Never executes a fix. Reserve before any external action; afterwards fresh
    evidence, assessment, tests and independent review are required.
    """
    if decide(snapshot, policy, assessment) != FIX:
        return None
    return retry_policy.reserve(db_path, policy["repository"], snapshot["pr"],
                                snapshot["head_sha"], snapshot["head_sha"],
                                policy["policy_hash"])
