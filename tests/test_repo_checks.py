"""Regression tests for publication boundaries; all fixture contents are synthetic."""

import contextlib
import io
import secrets
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_secrets
import repo_checks


class PublicPathTests(unittest.TestCase):
    def test_private_paths_include_nested_case_and_backup_variants(self):
        rejected = [
            ".env", ".env.production", ".env.backup", "nested/.ENV.production",
            "nested/.env.example.bak", ".codex", ".agents/config", "x/.aws/config",
            "x/credentials.json", "x/service-token.json", "x/secrets.yaml.bak",
            "x/id_ed25519", "x/id_rsa.old", "x/key.PEM", "x/file.pfx",
            "x/saves/world.zip", "x/artifacts/output.json", "x/logs/run.txt",
            "nested/player-data.json", "nested/server-settings.json", "../outside",
            ".claude/settings.json", "nested/.vscode/settings.json", ".idea/workspace.xml",
            "x/.cache/entry", ".tools/gitleaks", "x/.pytest_cache/entry", ".ruff_cache/entry",
            "results/score.json", "x/factorio/data.txt", "downloads/package.txt",
            "recording.mp4", "nested/recording.WEBM", ".secrets/private.txt", "backup.tar",
        ]
        for name in rejected:
            with self.subTest(name=name):
                self.assertTrue(repo_checks.disallowed_path(name))

    def test_public_templates_and_documentation_are_allowed(self):
        for name in (".env.example", "nested/.env.template", "SECURITY.md", "docs/secrets.md", "scripts/check_secrets.py"):
            with self.subTest(name=name):
                self.assertFalse(repo_checks.disallowed_path(name))


class RepositoryFixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="factorio-bench-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        repo_checks.git(self.root, "init", "--quiet")

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


class RepositoryBoundaryTests(RepositoryFixture):
    def test_forced_ignored_file_is_still_rejected(self):
        self.write(".gitignore", ".env\n")
        self.write(".env", "synthetic fixture\n")
        self.assertNotIn(".env", repo_checks.candidates(self.root))
        repo_checks.git(self.root, "add", "--force", ".env")
        with self.assertRaises(RuntimeError):
            repo_checks.safe_files(self.root)

    def test_forced_runtime_and_editor_files_are_still_rejected(self):
        self.write(".gitignore", ".vscode/\nresults/\n")
        self.write(".vscode/settings.json", "{}\n")
        self.write("results/score.json", "{}\n")
        self.assertNotIn("results/score.json", repo_checks.candidates(self.root))
        repo_checks.git(self.root, "add", "--force", ".vscode/settings.json", "results/score.json")
        with self.assertRaises(RuntimeError):
            repo_checks.safe_files(self.root)

    def test_index_snapshot_cannot_be_hidden_by_working_tree_edit(self):
        self.write("example.txt", "staged synthetic content\n")
        repo_checks.git(self.root, "add", "example.txt")
        self.write("example.txt", "different working content\n")
        with tempfile.TemporaryDirectory(prefix="factorio-bench-index-test-") as temporary:
            destination = Path(temporary)
            check_secrets.snapshot_index(self.root, destination)
            self.assertEqual((destination / "example.txt").read_text(), "staged synthetic content\n")

    def test_symlink_cannot_pull_external_content_into_scan(self):
        (self.root / "link.md").symlink_to(Path(__file__).resolve())
        with self.assertRaises(RuntimeError):
            repo_checks.safe_files(self.root)

    def test_links_cannot_escape_repository(self):
        problems = repo_checks.markdown_problems(self.root, "README.md", "[x](../outside.md)\n")
        self.assertEqual(len(problems), 1)

    def test_link_examples_in_fences_are_not_file_dependencies(self):
        problems = repo_checks.markdown_problems(self.root, "README.md", "```md\n[x](missing.md)\n```\n")
        self.assertEqual(problems, [])


class TimingTests(unittest.TestCase):
    def example(self):
        return {
            "schema_version": "factorio-bench.task.v1",
            "clock": {"simulation_tick_budget": 140},
            "objective": {"evaluation_start_tick": 100, "evaluation_end_tick": 140, "window_ticks": 10, "window_count": 4},
            "termination_policy": "fixed-horizon-with-voluntary-handoff",
        }

    def test_timing_check_uses_declared_values(self):
        self.assertIsNone(repo_checks.json_problem(self.example()))

    def test_inconsistent_windows_and_short_horizon_fail(self):
        value = self.example()
        value["objective"]["window_count"] = 5
        self.assertIsNotNone(repo_checks.json_problem(value))
        value = self.example()
        value["clock"]["simulation_tick_budget"] = 130
        self.assertIsNotNone(repo_checks.json_problem(value))


class ScannerOutputTests(unittest.TestCase):
    def test_scanner_output_never_reaches_caller(self):
        result = subprocess.CompletedProcess([], 1, b"synthetic sensitive stdout", b"synthetic sensitive stderr")
        output = io.StringIO()
        with patch.object(check_secrets.subprocess, "run", return_value=result) as run:
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                self.assertFalse(check_secrets.scan(["gitleaks"], {}))
        self.assertEqual(output.getvalue(), "")
        self.assertTrue(run.call_args.kwargs["capture_output"])

    def test_missing_scanner_fails_closed(self):
        with patch.object(check_secrets.shutil, "which", return_value=None):
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(check_secrets.check(), 1)


@unittest.skipUnless(shutil.which("gitleaks"), "Gitleaks not installed; real scanner regression skipped")
class ScannerCoverageTests(RepositoryFixture):
    def test_history_index_and_new_files_are_scanned_independently(self):
        # Generated test strings are never credentials and never leave this fixture.
        fake = "gh" + "p_" + secrets.token_hex(18)
        self.write("example.txt", "value = " + fake + "\n")
        repo_checks.git(self.root, "add", "example.txt")
        self.write("example.txt", "clean working content\n")
        self.assert_failed_surface("exact index")
        repo_checks.git(
            self.root, "-c", "user.name=Repository checks", "-c", "user.email=checks@example.invalid",
            "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
            "commit", "--quiet", "-m", "Synthetic test fixture",
        )
        repo_checks.git(self.root, "add", "example.txt")
        self.assert_failed_surface("reachable history")
        self.write("new.txt", "value = " + fake + "\n")
        self.assert_failed_surface("prospective files")

    def assert_failed_surface(self, label):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            self.assertEqual(check_secrets.check(self.root), 1)
        self.assertIn("Secret scan failed: " + label + ";", errors.getvalue())
        self.assertNotIn("value =", output.getvalue() + errors.getvalue())


if __name__ == "__main__":
    unittest.main()
