#!/usr/bin/env python3
"""Integration tests for wire-semgrep.py and the scanner template.

Run: python3 -I test-semgrep.py   (scanner tests FAIL, not skip, if semgrep 1.179.0 is not on PATH)
All fixtures live in temporary directories outside the repo; repos are real `git init` repos.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIRE = HERE / "wire-semgrep.py"
TPL = HERE.parent / "templates" / "semgrep"
INSTALLED = [".semgrep/rules.yml", ".semgrep/scan.py", ".semgrep/README.md",
             ".github/workflows/semgrep.yml", ".semgrepignore"]


def run(*args, cwd=None):
    return subprocess.run([sys.executable, "-I", *map(str, args)], capture_output=True, text=True, cwd=cwd)


def git_init(path):
    path.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True, env=env)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        # realpath: the installer refuses symlinked path components (e.g. macOS /var -> /private/var)
        self.base = Path(os.path.realpath(self.tmp.name))
        self.repo = self.base / "repo"
        git_init(self.repo)


class InstallerTests(Base):
    def test_install_idempotent_and_exact(self):
        self.assertEqual(run(WIRE, "--check", self.repo).returncode, 1)
        self.assertEqual(run(WIRE, self.repo).returncode, 0)
        for rel in INSTALLED:
            self.assertTrue((self.repo / rel).is_file(), rel)
        self.assertEqual((self.repo / ".semgrep/scan.py").read_bytes(), (TPL / "scan.py").read_bytes())
        self.assertEqual((self.repo / ".github/workflows/semgrep.yml").read_bytes(),
                         (TPL / "workflow.yml").read_bytes())
        before = {r: (self.repo / r).read_bytes() for r in INSTALLED}
        self.assertEqual(run(WIRE, self.repo).returncode, 0)
        self.assertEqual(run(WIRE, "--check", self.repo).returncode, 0)
        self.assertEqual(before, {r: (self.repo / r).read_bytes() for r in INSTALLED})

    def test_requires_git_root(self):
        plain = self.base / "plain"
        plain.mkdir()
        self.assertEqual(run(WIRE, plain).returncode, 2)
        self.assertFalse((plain / ".semgrep").exists())

    def test_fake_git_dir_rejected(self):
        fake = self.base / "fake"
        (fake / ".git").mkdir(parents=True)
        self.assertEqual(run(WIRE, fake).returncode, 2)
        self.assertFalse((fake / ".semgrep").exists())

    def test_subdirectory_of_repo_rejected(self):
        sub = self.repo / "sub"
        sub.mkdir()
        self.assertEqual(run(WIRE, sub).returncode, 2)
        self.assertFalse((sub / ".semgrep").exists())

    def test_conflict_preflight_writes_nothing(self):
        (self.repo / ".github/workflows").mkdir(parents=True)
        custom = self.repo / ".github/workflows/semgrep.yml"
        custom.write_text("custom\n")
        r = run(WIRE, self.repo)
        self.assertEqual(r.returncode, 1)
        self.assertIn("CONFLICT", r.stderr)
        self.assertEqual(custom.read_text(), "custom\n")
        self.assertFalse((self.repo / ".semgrep").exists())
        self.assertFalse((self.repo / ".semgrepignore").exists())

    def test_existing_semgrepignore_preserved(self):
        ign = self.repo / ".semgrepignore"
        ign.write_text("mine/\n")
        self.assertEqual(run(WIRE, self.repo).returncode, 0)
        self.assertEqual(ign.read_text(), "mine/\n")

    def test_symlink_refused(self):
        target = self.base / "elsewhere"
        target.mkdir()
        (self.repo / ".semgrep").symlink_to(target)
        r = run(WIRE, self.repo)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(list(target.iterdir()), [])
        self.assertFalse((self.repo / ".github").exists())

    def test_root_symlink_refused(self):
        link = self.base / "link"
        link.symlink_to(self.repo)
        r = run(WIRE, link)
        self.assertEqual(r.returncode, 2)
        self.assertFalse((self.repo / ".semgrep").exists())
        self.assertFalse((self.repo / ".github").exists())

    def test_root_parent_symlink_refused(self):
        real = self.base / "real"
        git_init(real / "inner")
        link = self.base / "plink"
        link.symlink_to(real)
        r = run(WIRE, link / "inner")
        self.assertEqual(r.returncode, 2)
        self.assertFalse((real / "inner" / ".semgrep").exists())

    def test_github_regular_file_preflight(self):
        (self.repo / ".github").write_text("not a dir\n")
        for args in ((self.repo,), ("--check", self.repo)):
            r = run(WIRE, *args)
            self.assertEqual(r.returncode, 1, r.stderr)
            self.assertIn("CONFLICT", r.stderr)
        self.assertEqual((self.repo / ".github").read_text(), "not a dir\n")
        self.assertFalse((self.repo / ".semgrep").exists())
        self.assertFalse((self.repo / ".semgrepignore").exists())


class ScannerTests(Base):
    def setUp(self):
        super().setUp()
        self.assertEqual(run(WIRE, self.repo).returncode, 0)
        self.scan = self.repo / ".semgrep/scan.py"

    def scan_with(self, name, content):
        src = self.base / "src"
        src.mkdir(exist_ok=True)
        for old in src.iterdir():
            old.unlink()
        if name:
            (src / name).write_text(content)
        return run(self.scan, src)

    def test_semgrep_available(self):
        v = subprocess.run(["semgrep", "--version"], capture_output=True, text=True)
        self.assertEqual(v.stdout.strip().splitlines()[-1], "1.179.0")

    def check_pair(self, clean, bad, rule, marker):
        r = self.scan_with(*clean)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = self.scan_with(*bad)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn(rule, r.stdout)
        self.assertNotIn(marker, r.stdout)

    def test_python(self):
        self.check_pair(("ok.py", "import subprocess\nsubprocess.run(['ls'])\n"),
                        ("bad.py", "import subprocess\nsubprocess.run('ls', shell=True)\n"),
                        "saddle.python.subprocess-shell-true", "shell=True")

    def test_javascript(self):
        self.check_pair(("ok.js", "console.log(JSON.parse('1'));\n"),
                        ("bad.js", "eval(process.argv[2]);\n"),
                        "saddle.javascript.eval", "process.argv")

    def test_php(self):
        self.check_pair(("ok.php", "<?php\necho 1;\n"),
                        ("bad.php", "<?php\neval($_GET['x']);\n"),
                        "saddle.php.eval", "_GET")

    def test_zero_eligible_source_errors(self):
        r = self.scan_with(None, "")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        r = self.scan_with("notes.txt", "nothing to scan\n")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_syntax_error_returns_2(self):
        # Semgrep prefilters files with no rule-relevant tokens, so a bare 'def (:' is never parsed.
        # The relevant call forces parsing; errors must outrank the finding (2, not 1).
        r = self.scan_with("broken.py", 'import subprocess\nsubprocess.run("x", shell=True)\ndef (:\n')
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_config_error_returns_2(self):
        (self.repo / ".semgrep/rules.yml").write_text("rules: [not valid\n")
        r = self.scan_with("ok.py", "x = 1\n")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
