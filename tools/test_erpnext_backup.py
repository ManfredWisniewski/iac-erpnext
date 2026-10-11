#!/usr/bin/env python3
"""Unit tests for tools/erpnext_backup.py — no live instance required (A05)."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import erpnext_backup  # noqa: E402


class FakeCompleted:
    def __init__(self, stdout="", returncode=0):
        self.stdout = stdout
        self.stderr = ""
        self.returncode = returncode


REMOTE_FILES = (
    "20261001_020000-frontend-database.sql.gz\n"
    "20261001_020000-frontend-files.tar\n"
    "20261001_020000-frontend-private-files.tar\n"
    "20261002_020000-frontend-database.sql.gz\n"
    "20261002_020000-frontend-files.tar\n"
    "20261002_020000-frontend-private-files.tar\n"
    "20261002_020000-frontend-site_config_backup.json\n"
)


class TestGrouping(unittest.TestCase):
    def test_groups_by_stamp(self):
        groups = erpnext_backup.group_by_stamp(REMOTE_FILES.splitlines())
        self.assertEqual(sorted(groups), ["20261001_020000", "20261002_020000"])
        self.assertEqual(len(groups["20261002_020000"]), 4)

    def test_skips_non_stamp_files(self):
        groups = erpnext_backup.group_by_stamp(["readme.txt", "20261002_020000-x-database.sql.gz"])
        self.assertEqual(list(groups), ["20261002_020000"])

    def test_newest_stamp(self):
        groups = erpnext_backup.group_by_stamp(REMOTE_FILES.splitlines())
        self.assertEqual(erpnext_backup.newest_stamp(groups), "20261002_020000")

    def test_newest_stamp_empty_raises(self):
        with self.assertRaises(RuntimeError):
            erpnext_backup.newest_stamp({})


class TestBackupFlow(unittest.TestCase):
    def test_copies_newest_set_and_prunes(self):
        commands = []
        copies = []

        def fake_docker(container, command):
            commands.append(command)
            if "backup --with-files" in command:
                return FakeCompleted()
            if command.startswith("ls -1"):
                return FakeCompleted(stdout=REMOTE_FILES)
            raise AssertionError(f"unexpected docker cmd {command}")

        def fake_run(cmd, check=True):
            if cmd[:2] == ["docker", "cp"]:
                copies.append(cmd)
                src_name = cmd[2].split("/")[-1]
                Path(cmd[3]).write_bytes(b"x")
                return FakeCompleted()
            raise AssertionError(f"unexpected run {cmd}")

        with tempfile.TemporaryDirectory() as dest:
            dest = Path(dest)
            # pre-seed two older sets so rotation has something to prune
            for stamp in ("20260928_020000", "20260929_020000"):
                (dest / f"{stamp}-frontend-database.sql.gz").write_bytes(b"old")
            with patch.object(erpnext_backup, "docker_exec", fake_docker), \
                 patch.object(erpnext_backup, "run", fake_run):
                self.assertEqual(erpnext_backup.backup("c", "frontend", dest, keep=2, dry_run=False), 0)
            self.assertTrue(any("backup --with-files" in c for c in commands))
            self.assertEqual(len(copies), 4)  # newest remote set has 4 files
            stamps = sorted(erpnext_backup.group_by_stamp(p.name for p in dest.iterdir()))
            self.assertEqual(stamps, ["20260929_020000", "20261002_020000"])  # keep=2, oldest pruned

    def test_dry_run_changes_nothing(self):
        commands = []

        def fake_docker(container, command):
            commands.append(command)
            return FakeCompleted(stdout=REMOTE_FILES)

        with tempfile.TemporaryDirectory() as dest:
            with patch.object(erpnext_backup, "docker_exec", fake_docker):
                self.assertEqual(erpnext_backup.backup("c", "frontend", Path(dest), keep=14, dry_run=True), 0)
            self.assertFalse(any("backup --with-files" in c for c in commands))
            self.assertEqual(list(Path(dest).iterdir()), [])


class TestConfigOnly(unittest.TestCase):
    def test_delegates_to_export(self):
        calls = []
        with patch.object(erpnext_backup, "run", lambda cmd, check=True: calls.append(cmd) or FakeCompleted()):
            self.assertEqual(erpnext_backup.config_only(), 0)
        self.assertEqual(len(calls), 1)
        self.assertIn("erpnext_export.py", calls[0][1] if len(calls[0]) > 1 else calls[0][0])


if __name__ == "__main__":
    unittest.main()
