import os
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from retry_policy import classify, reserve  # noqa: E402

H = ["%040x" % i for i in range(1, 6)]
P = "a" * 64
POL = {"allow": ["src/*", "docs/*"], "deny": ["src/secret*"], "max_files": 3, "max_lines": 20}


def F(name="src/a.py", **kw):
    d = {"filename": name, "status": "modified", "previous_filename": None,
         "additions": 1, "deletions": 1}
    d.update(kw)
    return d


class ClassifyTests(unittest.TestCase):
    def test_ok(self):
        self.assertIs(classify([F(), F("docs/x.md", status="added")], POL), True)

    def test_malformed_input(self):
        for files in (None, [], [None], "x", [{"filename": "src/a"}]):
            self.assertIs(classify(files, POL), False)
        self.assertIs(classify([F()], {"allow": ["*"]}), False)
        self.assertIs(classify([F()], None), False)

    def test_bad_paths(self):
        for p in ("/src/a", "src/../a", "src/./a", "src\\a", "src//a", "src/a\n", "src/é", "src/a/", ""):
            self.assertIs(classify([F(p)], POL), False, p)

    def test_deny_overrides_allow_and_github(self):
        self.assertIs(classify([F("src/secret.py")], POL), False)
        self.assertIs(classify([F(".github/w.yml")], {**POL, "allow": ["*"]}), False)

    def test_rename_remove(self):
        for kw in (dict(status="renamed", previous_filename="src/secret.py"),
                   dict(previous_filename="src/secret.py"), dict(status="removed")):
            self.assertIs(classify([F(**kw)], POL), False, kw)

    def test_limits_and_types(self):
        self.assertIs(classify([F(additions=10, deletions=10)], POL), True)
        for a in (11, True, -1, 1.0):
            self.assertIs(classify([F(additions=a, deletions=10)], POL), False, a)
        self.assertIs(classify([F("src/%d" % i) for i in range(4)], POL), False)
        self.assertIs(classify([F()], {**POL, "max_files": True}), False)
        self.assertIs(classify([F(), F()], POL), False)  # duplicate

    def test_semantic_flags_and_caveat(self):
        self.assertIs(classify([F(auth=False, publicAPI=False)], POL), True)
        for k in ("auth", "security", "migration", "dependency", "publicAPI", "productbehavior"):
            for v in (True, None):
                self.assertIs(classify([F(**{k: v})], POL), False, k)
        self.assertIn("semantic", classify.__doc__)  # path allow != certification


class ReserveTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.d.name, "l.db")

    def tearDown(self):
        self.d.cleanup()

    def r(self, head, root=H[4], pol=P, pr=1, repo="o/n"):
        return reserve(self.db, repo, pr, root, head, pol)

    def test_duplicate_no_extra_slot_and_restart(self):
        self.assertIsNotNone(self.r(H[0]))
        self.assertIsNone(self.r(H[0]))  # new connection == restart
        self.assertIsNotNone(self.r(H[1]))
        self.assertIsNone(self.r(H[1]))

    def test_third_blocked_no_reset(self):
        self.assertIsNotNone(self.r(H[0]))
        self.assertIsNotNone(self.r(H[1], root=H[3], pol="b" * 64))
        self.assertIsNone(self.r(H[2], root=H[2], pol="c" * 64))
        self.assertIsNone(self.r(H[3], root=H[0], pol=P))
        self.assertIsNotNone(self.r(H[0], pr=2))  # other PR independent
        self.assertIsNotNone(self.r(H[0], repo="o/m"))

    def test_concurrent(self):
        out = []
        ts = [threading.Thread(target=lambda h=h: out.append(self.r(h))) for h in H]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self.assertEqual(len([x for x in out if x is not None]), 2)
        self.assertEqual(len(out), 5)

    def test_repo_case_change_no_reset(self):
        self.assertIsNotNone(self.r(H[0], repo="Owner/Name"))
        self.assertIsNone(self.r(H[0], repo="owner/name"))  # duplicate across case
        self.assertIsNotNone(self.r(H[1], repo="OWNER/NAME"))
        self.assertIsNone(self.r(H[2], repo="oWnEr/nAmE"))
        self.assertIsNone(self.r(H[3], repo="owner/name"))

    def test_bad_db_paths(self):
        for p in (":memory:", "", "l.db", "./l.db", "file:l.db?mode=memory",
                  "file:///tmp/l.db", "file::memory:?cache=shared", None, 5):
            with self.assertRaises(ValueError, msg=repr(p)):
                reserve(p, "o/n", 1, H[4], H[0], P)
        self.assertFalse(os.path.exists(self.db))
        self.assertIsNotNone(reserve(self.db, "o/n", 1, H[4], H[0], P))

    def test_invalid(self):
        bad = [dict(repo="x"), dict(repo="a/b/c"), dict(pr=0), dict(pr=True), dict(pr="1"),
               dict(root="A" * 40), dict(head="A" * 40), dict(head="abc"),
               dict(repo="./n"), dict(repo="o/."), dict(repo=".."), dict(repo="../n"), dict(repo="o/.."), dict(pol="a" * 63)]
        for b in bad:
            kw = dict(repo="o/n", pr=1, root=H[0], head=H[1], pol=P, **{})
            kw.update(b)
            with self.assertRaises(ValueError, msg=str(b)):
                self.r(kw["head"], kw["root"], kw["pol"], kw["pr"], kw["repo"])
        self.assertIsNotNone(self.r(H[0]))  # invalid input consumed nothing


if __name__ == "__main__":
    unittest.main()
