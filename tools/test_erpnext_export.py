#!/usr/bin/env python3
"""Unit tests for tools/erpnext_export.py — no live instance required (A04)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import erpnext_export  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]


class FakeCompleted:
    def __init__(self, stdout="", returncode=0):
        self.stdout = stdout
        self.stderr = ""
        self.returncode = returncode


def fake_run(outputs):
    calls = []

    def _run(cmd, cwd=None, check=True):
        calls.append(cmd)
        key = " ".join(cmd)
        for pattern, value in outputs.items():
            if pattern in key:
                if isinstance(value, Exception):
                    raise value
                return FakeCompleted(stdout=value)
        return FakeCompleted()

    return _run, calls


class TestOwnership(unittest.TestCase):
    def test_parses(self):
        rows = erpnext_export.read_ownership(REPO_ROOT / "src" / "ownership.csv")
        self.assertTrue(any(r["doctype"] == "Email Account" and r["secret_fields"] == ["password"] for r in rows))


class TestMaskSecrets(unittest.TestCase):
    def test_masks_declared_fields(self):
        doclist = [{"doctype": "Email Account", "name": "X", "password": "supersecret", "email_id": "a@b"}]
        masked = erpnext_export.mask_secrets(doclist, ["password"])
        self.assertEqual(masked[0]["password"], "<REDACTED>")
        self.assertEqual(masked[0]["email_id"], "a@b")
        self.assertEqual(doclist[0]["password"], "supersecret")  # input untouched

    def test_empty_and_missing_fields_untouched(self):
        doclist = [{"name": "X", "password": ""}, {"name": "Y"}]
        masked = erpnext_export.mask_secrets(doclist, ["password"])
        self.assertEqual(masked[0]["password"], "")
        self.assertNotIn("password", masked[1])

    def test_no_secret_value_in_serialized_output(self):
        doclist = [{"password": "hunter2"}]
        text = json.dumps(erpnext_export.mask_secrets(doclist, ["password"]))
        self.assertNotIn("hunter2", text)


class TestMirror(unittest.TestCase):
    def test_add_update_remove(self):
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as dst:
            s, d = Path(src), Path(dst)
            (s / "config" / "A").mkdir(parents=True)
            (s / "config" / "A" / "A.json").write_text("new", encoding="utf-8")
            (d / "config").mkdir()
            (d / "config" / "old.json").write_text("stale", encoding="utf-8")
            (s / "keep.json").write_text("same", encoding="utf-8")
            (d / "keep.json").write_text("same", encoding="utf-8")
            added, updated, removed = erpnext_export.mirror(s, d)
            self.assertEqual((added, updated, removed), (1, 0, 1))
            self.assertTrue((d / "config" / "A" / "A.json").exists())
            self.assertFalse((d / "config" / "old.json").exists())

    def test_update_counts_content_diff(self):
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as dst:
            s, d = Path(src), Path(dst)
            (s / "a.json").write_text("v2", encoding="utf-8")
            (d / "a.json").write_text("v1", encoding="utf-8")
            self.assertEqual(erpnext_export.mirror(s, d), (0, 1, 0))


class TestGuardRails(unittest.TestCase):
    def test_refuses_wrong_branch(self):
        runner, _ = fake_run({"rev-parse --abbrev-ref HEAD": "trurl\n"})
        with tempfile.TemporaryDirectory() as repo, patch.object(erpnext_export, "run", runner):
            with self.assertRaises(RuntimeError):
                erpnext_export.ensure_clean_branch(Path(repo), "main", pull=False)

    def test_refuses_dirty_tree(self):
        runner, _ = fake_run({
            "rev-parse --abbrev-ref HEAD": "main\n",
            "status --porcelain": " M file\n",
        })
        with tempfile.TemporaryDirectory() as repo, patch.object(erpnext_export, "run", runner):
            with self.assertRaises(RuntimeError):
                erpnext_export.ensure_clean_branch(Path(repo), "main", pull=False)

    def test_clean_branch_passes(self):
        runner, _ = fake_run({
            "rev-parse --abbrev-ref HEAD": "main\n",
            "status --porcelain": "",
        })
        with tempfile.TemporaryDirectory() as repo, patch.object(erpnext_export, "run", runner):
            erpnext_export.ensure_clean_branch(Path(repo), "main", pull=False)


class TestEmptyExportAbort(unittest.TestCase):
    def test_empty_export_aborts_before_mirror(self):
        runner, calls = fake_run({
            "rev-parse --abbrev-ref HEAD": "main\n",
            "status --porcelain": "",
            "export-fixtures": "",
        })

        def empty_export(*a, **kw):
            return 0

        with tempfile.TemporaryDirectory() as repo:
            repo = Path(repo)
            (repo / "src").mkdir()
            (repo / "src" / "ownership.csv").write_text("doctype,owner,export,apply_order,secret_fields\n", encoding="utf-8")
            with patch.object(erpnext_export, "run", runner), \
                 patch.object(erpnext_export, "docker_exec", return_value=FakeCompleted()), \
                 patch.object(erpnext_export, "export_json_docs", empty_export), \
                 patch.object(erpnext_export, "export_fixtures", empty_export):
                with self.assertRaises(RuntimeError):
                    erpnext_export.export(repo, "c", "s", "main", push=False, pull=False, dry_run=True)


if __name__ == "__main__":
    unittest.main()
