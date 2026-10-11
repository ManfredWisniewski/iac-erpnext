#!/usr/bin/env python3
"""Unit tests for tools/erpnext_apply.py — no live instance required (A03)."""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import erpnext_apply  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]


class FakeCompleted:
    def __init__(self, stdout="", returncode=0):
        self.stdout = stdout
        self.stderr = ""
        self.returncode = returncode


class TestOwnership(unittest.TestCase):
    def setUp(self):
        self.rows = erpnext_apply.read_ownership(REPO_ROOT / "src" / "ownership.csv")

    def test_csv_parses_and_ignores_comments(self):
        self.assertTrue(self.rows)
        self.assertTrue(all(r["doctype"] for r in self.rows))

    def test_owners_and_exports_are_known(self):
        for row in self.rows:
            self.assertIn(row["owner"], {"git", "ui", "data"})
            self.assertIn(row["export"], {"fixtures", "export-json", "none"})

    def test_l4_rows_have_integer_apply_order(self):
        for row in self.rows:
            if row["owner"] == "git" and row["export"] == "export-json":
                int(row["apply_order"])  # raises if not an int

    def test_secret_fields_exist_in_authored_config(self):
        for row in self.rows:
            if not row["secret_fields"]:
                continue
            for path in (REPO_ROOT / "config" / row["doctype"]).glob("*.json"):
                doc = json.loads(path.read_text(encoding="utf-8"))[0]
                for field in row["secret_fields"]:
                    self.assertIn(field, doc, f"{path}: secret field {field!r} not in doc")


class TestL4Ordering(unittest.TestCase):
    def test_parents_before_children(self):
        rows = [
            {"doctype": "B", "owner": "git", "export": "export-json", "apply_order": "30"},
            {"doctype": "A", "owner": "git", "export": "export-json", "apply_order": "10"},
            {"doctype": "X", "owner": "ui", "export": "none", "apply_order": ""},
            {"doctype": "W", "owner": "git", "export": "fixtures", "apply_order": ""},
        ]
        self.assertEqual([r["doctype"] for r in erpnext_apply.l4_doctypes(rows)], ["A", "B"])


class TestEnvSubstitution(unittest.TestCase):
    def test_substitutes_placeholder(self):
        with patch.dict(os.environ, {"MY_VAR": "secret123"}):
            self.assertEqual(erpnext_apply.substitute_env({"a": "<ENV:MY_VAR>"}), {"a": "secret123"})

    def test_missing_var_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                erpnext_apply.substitute_env("<ENV:DEFINITELY_MISSING>")

    def test_env_references_collects_all(self):
        refs = erpnext_apply.env_references({"a": ["<ENV:ONE>", {"b": "<ENV:TWO>"}]})
        self.assertEqual(refs, {"ONE", "TWO"})

    def test_authored_files_never_hold_secret_values(self):
        bootstrap = (REPO_ROOT / "src" / "bootstrap" / "setup_wizard.json").read_text(encoding="utf-8")
        self.assertIn("<ENV:", bootstrap)
        self.assertNotIn('"password": "admin', bootstrap.lower())


class TestSecrets(unittest.TestCase):
    def test_collect_secrets(self):
        doclist = [{"doctype": "Email Account", "name": "X", "password": "<ENV:PW>", "email_id": "a@b"}]
        secrets = erpnext_apply.collect_secrets(doclist, "Email Account", ["password"])
        self.assertEqual(secrets, [("X", "password", "PW")])

    def test_collect_secrets_ignores_undeclared(self):
        doclist = [{"name": "X", "token": "<ENV:T>"}]
        self.assertEqual(erpnext_apply.collect_secrets(doclist, "DT", ["password"]), [])


class TestCommandBuilding(unittest.TestCase):
    def test_site_is_fresh_parses_probe(self):
        with patch.object(erpnext_apply, "docker_exec", return_value=FakeCompleted(stdout="0\n")):
            self.assertTrue(erpnext_apply.site_is_fresh("c", "s"))
        with patch.object(erpnext_apply, "docker_exec", return_value=FakeCompleted(stdout="2\n")):
            self.assertFalse(erpnext_apply.site_is_fresh("c", "s"))

    def test_site_is_fresh_rejects_garbage(self):
        with patch.object(erpnext_apply, "docker_exec", return_value=FakeCompleted(stdout="oops")):
            with self.assertRaises(RuntimeError):
                erpnext_apply.site_is_fresh("c", "s")

    def test_python_on_site_wraps_and_commits(self):
        cmd = erpnext_apply.python_on_site("frontend", "pass")
        self.assertIn("frappe.init(site=", cmd)
        self.assertIn("frontend", cmd)
        self.assertIn("frappe.db.commit()", cmd)


class TestPlan(unittest.TestCase):
    def test_plan_covers_all_layers(self):
        rows = erpnext_apply.read_ownership(REPO_ROOT / "src" / "ownership.csv")
        steps = erpnext_apply.plan_steps(rows)
        joined = "\n".join(steps)
        self.assertIn("L2", joined)
        self.assertIn("L1", joined)
        self.assertIn("L3", joined)
        self.assertIn("L4", joined)

    def test_config_jsons_are_doclists(self):
        for path in (REPO_ROOT / "config").rglob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(data, list, f"{path} must be a doclist")
            self.assertTrue(data, f"{path} must not be empty")


if __name__ == "__main__":
    unittest.main()
