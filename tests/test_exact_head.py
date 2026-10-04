import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from exact_head import validate  # noqa: E402

H, B = "a" * 40, "b" * 40


def good():
    rev = lambda k: {"kind": k, "reviewer_actor_id": 7, "reviewed_sha": H,
                     "base_sha": B, "status": "completed", "run_id": "r1",
                     "findings_count": 0}
    return {"complete": True, "head_sha": H, "base_sha": B,
            "current_head_sha": H, "current_base_sha": B,
            "reviews": [rev("code"), rev("security")],
            "checks": [{"name": "unit", "tested_sha": H, "base_sha": B,
                        "app_id": 9, "status": "completed",
                        "conclusion": "success"}],
            "required_checks": {"unit": 9}, "unresolved_count": 0,
            "changes_requested": False}


def mut(fn):
    def apply(e):
        fn(e)
        return e
    return apply


def setk(k, v):
    return mut(lambda e: e.__setitem__(k, v))


def delk(k):
    return mut(lambda e: e.pop(k))


def chk(k, v):
    return mut(lambda e: e["checks"][0].__setitem__(k, v))


def rev(k, v, i=0):
    return mut(lambda e: e["reviews"][i].__setitem__(k, v))


NEG = {
    "missing_head": delk("head_sha"), "null_base": setk("base_sha", None),
    "not_complete": setk("complete", False), "int_head": setk("head_sha", 5),
    "shortsha": setk("head_sha", H[:7]), "wrong_base": setk("base_sha", "c" * 40),
    "wrong_current_head": setk("current_head_sha", "c" * 40),
    "wrong_current_base": setk("current_base_sha", "c" * 40),
    "no_checks": setk("checks", []), "checks_not_list": setk("checks", None),
    "empty_required": setk("required_checks", {}),
    "bool_app_required": setk("required_checks", {"unit": True}),
    "duplicate_check": mut(lambda e: e["checks"].append(copy.deepcopy(e["checks"][0]))),
    "spoof_app": chk("app_id", 10), "check_wrong_sha": chk("tested_sha", "c" * 40),
    "skipped": chk("conclusion", "skipped"), "neutral": chk("conclusion", "neutral"),
    "check_pending": chk("status", "in_progress"),
    "spoof_actor": rev("reviewer_actor_id", 8),
    "bool_actor": rev("reviewer_actor_id", True),
    "pending_review": rev("status", "in_progress"),
    "cancelled_review": rev("status", "cancelled"),
    "review_short_sha": rev("reviewed_sha", H[:7]),
    "missing_review": mut(lambda e: e["reviews"].pop(1)),
    "reaction_only": setk("reviews", [{"kind": "code", "reaction": "+1"}]),
    "duplicate_review": mut(lambda e: e["reviews"].append(copy.deepcopy(e["reviews"][0]))),
    "no_run_id": rev("run_id", ""), "findings": rev("findings_count", 1),
    "bool_findings": rev("findings_count", False),
    "unresolved": setk("unresolved_count", 1),
    "bool_unresolved": setk("unresolved_count", False),
    "changes_requested": setk("changes_requested", True),
    "not_dict": lambda e: [],
}


class ExactHeadTest(unittest.TestCase):
    def test_pass_code_and_security(self):
        self.assertEqual(validate(good(), H, B, 7, ["code", "security"]), [])

    def test_pass_code_only_ignores_extras(self):
        e = good()
        e["reviews"].append({"kind": "other"})
        e["checks"].append("junk")
        self.assertEqual(validate(e, H, B, 7, ("code",)), [])

    def test_negative(self):
        for name, fn in NEG.items():
            with self.subTest(name):
                out = validate(fn(good()), H, B, 7, ["code", "security"])
                self.assertTrue(out)
                self.assertTrue(all(isinstance(c, str) and H not in c for c in out))

    def test_bad_inputs(self):
        for name, args in {"upper": (H.upper(), B, 7, ["code"]),
                           "bool_actor": (H, B, True, ["code"]),
                           "zero_actor": (H, B, 0, ["code"]),
                           "empty_kinds": (H, B, 7, []),
                           "dup_kinds": (H, B, 7, ["code", "code"]),
                           "no_code": (H, B, 7, ["security"]),
                           "unknown_kind": (H, B, 7, ["code", "x"])}.items():
            with self.subTest(name):
                self.assertTrue(validate(good(), *args))


if __name__ == "__main__":
    unittest.main()
