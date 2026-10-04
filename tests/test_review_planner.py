"""Mock end-to-end tests with synthetic normalized fixtures (no live proof)."""
import copy
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import review_planner as rp  # noqa: E402

REPO, ACTOR, APP, PH = "o/r", 7, 11, "a" * 64
BASE = "b" * 40


def sha(c):
    return c * 40


POLICY = {"repository": REPO, "actor_id": ACTOR, "required_checks": {"tests": APP},
          "required_kinds": ["code", "security"], "policy_hash": PH,
          "files": {"allow": ["docs/*", "src/*"], "deny": [], "max_files": 5, "max_lines": 100}}
FILES = [{"filename": "src/a.py", "status": "modified", "additions": 3, "deletions": 1}]


def evidence(head, findings=0, unresolved=0, base=BASE):
    return {"complete": True, "head_sha": head, "current_head_sha": head,
            "base_sha": base, "current_base_sha": base, "checks": [
                {"name": "tests", "tested_sha": head, "base_sha": base, "app_id": APP,
                 "status": "completed", "conclusion": "success"}],
            "reviews": [{"kind": k, "reviewer_actor_id": ACTOR, "reviewed_sha": head,
                         "base_sha": base, "status": "completed", "run_id": "r" + k,
                         "findings_count": findings if k == "code" else 0}
                        for k in ("code", "security")],
            "unresolved_count": unresolved, "changes_requested": False}


def snap(head, ev=None, **kw):
    s = {"repository": REPO, "pr": 5, "head_sha": head, "base_sha": BASE, "state": "open",
         "draft": False, "fork": False, "files": copy.deepcopy(FILES),
         "evidence": ev if ev is not None else evidence(head)}
    s.update(kw)
    return s


def assess(head, **kw):
    a = {"head_sha": head, "base_sha": BASE, "policy_hash": PH, "tier": "small_internal_fix",
         "excluded": []}
    a.update(kw)
    return a


def D(s, a=None, p=POLICY):
    return rp.decide(s, p, a if a is not None else assess(s["head_sha"]))


class PlannerTests(unittest.TestCase):
    def test_lifecycle_and_retry_cap(self):
        with tempfile.TemporaryDirectory() as d:
            db = os.path.join(d, "r.db")
            h1, h2, h3, h4 = sha("1"), sha("2"), sha("3"), sha("4")
            s1 = snap(h1, evidence(h1, findings=2))
            self.assertEqual(D(s1), rp.FIX)
            self.assertEqual(rp.reserve_fix(s1, POLICY, assess(h1), db), 1)
            stale = snap(h2, evidence(h1, findings=2))  # new head, old evidence
            self.assertEqual(D(stale), rp.BLOCKED)
            self.assertIsNone(rp.reserve_fix(stale, POLICY, assess(h2), db))
            self.assertEqual(D(snap(h2)), rp.MERGE)
            s3 = snap(h3, evidence(h3, findings=1))
            self.assertEqual(rp.reserve_fix(s3, POLICY, assess(h3), db), 2)
            s4 = snap(h4, evidence(h4, findings=1))
            self.assertEqual(D(s4), rp.FIX)
            self.assertIsNone(rp.reserve_fix(s4, POLICY, assess(h4), db))

    def test_non_fix_does_not_reserve(self):
        with tempfile.TemporaryDirectory() as d:
            db = os.path.join(d, "r.db")
            for _ in range(3):
                self.assertIsNone(rp.reserve_fix(snap(sha("1")), POLICY, assess(sha("1")), db))
            s = snap(sha("2"), evidence(sha("2"), findings=1))
            self.assertEqual(rp.reserve_fix(s, POLICY, assess(sha("2")), db), 1)

    def test_owner_paths(self):
        h = sha("1")
        ev = evidence(h, findings=1)
        ev["changes_requested"] = True
        self.assertEqual(D(snap(h, ev)), rp.OWNER)
        self.assertEqual(D(snap(h), assess(h, excluded=["x"])), rp.OWNER)
        self.assertEqual(D(snap(h), assess(h, tier="other")), rp.OWNER)
        self.assertEqual(D(snap(h), assess(sha("9"))), rp.OWNER)
        self.assertEqual(D(snap(h), assess(h, policy_hash="c" * 64)), rp.OWNER)
        self.assertEqual(D(snap(h), {}), rp.OWNER)
        api = copy.deepcopy(FILES)
        api[0]["publicAPI"] = True
        self.assertEqual(D(snap(h, files=api)), rp.OWNER)
        gh = [dict(FILES[0], filename=".github/workflows/x.yml")]
        self.assertEqual(D(snap(h, files=gh)), rp.OWNER)
        ren = [dict(FILES[0], status="renamed", previous_filename="src/b.py")]
        self.assertEqual(D(snap(h, files=ren)), rp.OWNER)
        old = evidence(h, findings=0, unresolved=2)
        self.assertEqual(D(snap(h, old)), rp.OWNER)

    def test_blocked_paths(self):
        h = sha("1")
        self.assertEqual(D(snap(h, fork=True)), rp.BLOCKED)
        self.assertEqual(D(snap(h, draft=True)), rp.BLOCKED)
        self.assertEqual(D(snap(h, state="closed")), rp.BLOCKED)
        self.assertEqual(D(snap(h, pr=True)), rp.BLOCKED)
        self.assertEqual(D(snap(h, repository="x/y")), rp.BLOCKED)
        self.assertEqual(rp.decide(None, POLICY, assess(h)), rp.BLOCKED)
        ev = evidence(h)
        ev["reviews"][0]["reviewer_actor_id"] = 99
        self.assertEqual(D(snap(h, ev)), rp.BLOCKED)
        ev = evidence(h, findings=1)
        ev["reviews"] = [r for r in ev["reviews"] if r["kind"] != "security"]
        self.assertEqual(D(snap(h, ev)), rp.BLOCKED)
        ev = evidence(h, findings=1)
        ev["checks"][0]["status"] = "in_progress"
        self.assertEqual(D(snap(h, ev)), rp.BLOCKED)
        ev = evidence(h, findings=1)
        ev["checks"][0]["conclusion"] = "failure"
        self.assertEqual(D(snap(h, ev)), rp.BLOCKED)
        self.assertEqual(D(snap(h, evidence(h, findings=1, base=sha("e")))), rp.BLOCKED)
        ev = evidence(h, findings=1)
        ev["reviews"].append(copy.deepcopy(ev["reviews"][0]))
        self.assertEqual(D(snap(h, ev)), rp.BLOCKED)

    def test_policy_override_rejects_spoofed_checks(self):
        h = sha("1")
        ev = evidence(h)
        ev["required_checks"] = {}
        self.assertEqual(D(snap(h, ev)), rp.MERGE)
        ev["checks"] = []
        self.assertNotEqual(D(snap(h, ev)), rp.MERGE)
        ev["required_checks"] = {"tests": APP}
        self.assertNotEqual(D(snap(h, ev)), rp.MERGE)
        pol = dict(POLICY, required_checks={})
        self.assertEqual(D(snap(h), p=pol), rp.BLOCKED)

    def test_malformed_findings(self):
        h = sha("1")
        for bad in (True, -1, "1", 1.0, None):
            ev = evidence(h, findings=1)
            ev["reviews"][0]["findings_count"] = bad
            self.assertEqual(D(snap(h, ev)), rp.BLOCKED, bad)
        for bad in (True, -1, "1"):
            ev = evidence(h, findings=1)
            ev["unresolved_count"] = bad
            self.assertEqual(D(snap(h, ev)), rp.BLOCKED, bad)

    def test_input_not_mutated(self):
        h = sha("1")
        s = snap(h, evidence(h, findings=1, unresolved=1))
        before = copy.deepcopy(s)
        self.assertEqual(D(s), rp.FIX)
        self.assertEqual(s, before)


if __name__ == "__main__":
    unittest.main()
