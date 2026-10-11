#!/usr/bin/env python3
"""Apply Git-declared ERPNext site state (L1-L4) via bench in the backend container.

Runs on the ERPNext host against `docker exec -u frappe <container>`.
Standard library only (D05). Direction is Git -> site (D08); idempotent:
site_config keys are overwritten, the setup wizard only runs on a fresh site
(no Company), install-app/migrate no-op when nothing changed, import-doc upserts.

Layers (intent.md):
  L2  site_config keys      src/site_config.template.json -> bench set-config
  L1  bootstrap             src/bootstrap/setup_wizard.json -> setup_complete
                            (fresh sites only; secrets travel via temp file,
                            never on the command line)
  L3  app + fixtures        install-app wit (if missing) + bench migrate
  L4  declared records      config/<DocType>/*.json -> bench import-doc,
                            ordered by src/ownership.csv apply_order;
                            <ENV:VAR> placeholders are set afterwards via
                            frappe.client.set_value from the environment

Exit codes: 0 success, 1 failure.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
CONFIG_DIR = REPO_ROOT / "config"
OWNERSHIP_CSV = SRC_DIR / "ownership.csv"
BOOTSTRAP_JSON = SRC_DIR / "bootstrap" / "setup_wizard.json"
SITE_CONFIG_TEMPLATE = SRC_DIR / "site_config.template.json"

BENCH_HOME = "/home/frappe/frappe-bench"
CONTAINER_TMP = "/tmp/wit-iac"
SETUP_COMPLETE = "erpnext.setup.setup_wizard.setup_wizard.setup_complete"

DEFAULT_CONTAINER = os.environ.get("ERPNEXT_CONTAINER", "erpnext_backend")
DEFAULT_SITE = os.environ.get("ERPNEXT_SITE", "frontend")

ENV_PLACEHOLDER = re.compile(r"<ENV:([A-Za-z_][A-Za-z0-9_]*)>")

log = logging.getLogger("erpnext_apply")


def load_env(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def substitute_env(value: object, source: str = "") -> object:
    """Recursively replace <ENV:VAR> placeholders; raise on missing variables."""
    if isinstance(value, str):
        def repl(match: re.Match) -> str:
            name = match.group(1)
            if name not in os.environ:
                raise ValueError(f"{source}: environment variable {name} is not set")
            return os.environ[name]
        return ENV_PLACEHOLDER.sub(repl, value)
    if isinstance(value, list):
        return [substitute_env(v, source) for v in value]
    if isinstance(value, dict):
        return {k: substitute_env(v, source) for k, v in value.items()}
    return value


def env_references(value: object) -> set[str]:
    """All variable names referenced via <ENV:VAR> in a JSON structure."""
    found: set[str] = set()
    if isinstance(value, str):
        found.update(ENV_PLACEHOLDER.findall(value))
    elif isinstance(value, list):
        for item in value:
            found.update(env_references(item))
    elif isinstance(value, dict):
        for item in value.values():
            found.update(env_references(item))
    return found


def read_ownership(path: Path = OWNERSHIP_CSV) -> list[dict]:
    """Parse ownership.csv into row dicts. `#` comment lines are ignored."""
    rows: list[dict] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(line for line in handle if not line.lstrip().startswith("#"))
        for row in reader:
            rows.append({
                "doctype": (row.get("doctype") or "").strip(),
                "owner": (row.get("owner") or "").strip(),
                "export": (row.get("export") or "").strip(),
                "apply_order": (row.get("apply_order") or "").strip(),
                "secret_fields": [f.strip() for f in (row.get("secret_fields") or "").split(";") if f.strip()],
            })
    return rows


def l4_doctypes(rows: list[dict]) -> list[dict]:
    """git-owned export-json rows, sorted by apply_order then doctype."""
    declared = [r for r in rows if r["owner"] == "git" and r["export"] == "export-json"]
    return sorted(declared, key=lambda r: (int(r["apply_order"]), r["doctype"]))


def docker_exec(container: str, command: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a shell command as frappe inside the backend container."""
    cmd = ["docker", "exec", "-u", "frappe", container, "bash", "-lc", command]
    log.debug("$ %s", " ".join(cmd))
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def docker_cp(container: str, src: Path, dest: str) -> subprocess.CompletedProcess[str]:
    cmd = ["docker", "cp", str(src), f"{container}:{dest}"]
    log.debug("$ %s", " ".join(cmd))
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def bench(site: str, args: str) -> str:
    """`cd bench && bench --site <site> <args>` — args must be pre-quoted."""
    return f"cd {BENCH_HOME} && bench --site {shlex.quote(site)} {args}"


def python_on_site(site: str, code: str) -> str:
    """frappe.init+connect, run code, commit — the explicit form of bench execute."""
    script = (
        "import frappe; frappe.init(site=%s); frappe.connect(); %s; frappe.db.commit()"
        % (repr(site), code)
    )
    return f"cd {BENCH_HOME} && env/bin/python -c {shlex.quote(script)}"


def plan_steps(rows: list[dict]) -> list[str]:
    """Human-readable apply plan for --dry-run."""
    steps = [f"L2 set-config {key} <- site_config.template.json" for key in load_json(SITE_CONFIG_TEMPLATE)]
    steps.append("L1 bootstrap setup_complete (fresh sites only — probe: no Company exists)")
    steps.append("L3 install-app wit (if missing) + bench migrate")
    for row in l4_doctypes(rows):
        files = sorted((CONFIG_DIR / row["doctype"]).glob("*.json")) if (CONFIG_DIR / row["doctype"]).is_dir() else []
        if files:
            steps.append(f"L4 import-doc {row['doctype']} ({len(files)} file(s): {', '.join(f.name for f in files)})")
        else:
            steps.append(f"L4 import-doc {row['doctype']} (no config/{row['doctype']}/ files — skipped)")
    return steps


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{path.name}: invalid JSON — {error}") from None


def apply_site_config(container: str, site: str, dry_run: bool) -> None:
    template = substitute_env(load_json(SITE_CONFIG_TEMPLATE), SITE_CONFIG_TEMPLATE.name)
    for key, value in template.items():
        if isinstance(value, str):
            args = f"set-config {shlex.quote(key)} {shlex.quote(value)}"
        else:
            args = f"set-config -p {shlex.quote(key)} {shlex.quote(json.dumps(value))}"
        log.info("set-config %s", key)
        if not dry_run:
            docker_exec(container, bench(site, args))


def site_is_fresh(container: str, site: str) -> bool:
    result = docker_exec(container, bench(site, "execute \"frappe.db.count('Company')\""))
    out = result.stdout.strip()
    try:
        return int(out) == 0
    except ValueError:
        raise RuntimeError(f"unexpected Company probe output: {out!r}") from None


def apply_bootstrap(container: str, site: str, dry_run: bool) -> None:
    args = substitute_env(load_json(BOOTSTRAP_JSON), BOOTSTRAP_JSON.name)
    if dry_run:
        log.info("bootstrap probe + setup_complete (fresh sites only)")
        return
    if not site_is_fresh(container, site):
        log.info("site already set up (Company exists) — skipping bootstrap")
        return
    docker_exec(container, f"mkdir -p {CONTAINER_TMP}")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(args, tmp)
        tmp_path = Path(tmp.name)
    try:
        docker_cp(container, tmp_path, f"{CONTAINER_TMP}/setup_wizard.json")
        docker_exec(container, python_on_site(
            site,
            f"import json; from {SETUP_COMPLETE.rsplit('.', 1)[0]} import setup_complete; "
            f"setup_complete(json.load(open('{CONTAINER_TMP}/setup_wizard.json')))",
        ))
        log.info("setup wizard completed")
    finally:
        tmp_path.unlink(missing_ok=True)
        docker_exec(container, f"rm -f {CONTAINER_TMP}/setup_wizard.json", check=False)


def apply_app(container: str, site: str, dry_run: bool) -> None:
    if dry_run:
        log.info("install-app wit (if missing) + migrate")
        return
    result = docker_exec(container, bench(site, "list-apps"))
    if "wit" not in result.stdout.split():
        docker_exec(container, bench(site, "install-app wit"))
        log.info("installed app wit")
    docker_exec(container, bench(site, "migrate"))
    log.info("migrate done")


def secret_fields_for(rows: list[dict], doctype: str) -> list[str]:
    return next((r["secret_fields"] for r in rows if r["doctype"] == doctype), [])


def collect_secrets(doclist: list, doctype: str, declared: list[str]) -> list[tuple[str, str, str]]:
    """(docname, fieldname, env var) for every declared secret field carrying <ENV:>."""
    secrets = []
    for doc in doclist:
        for field in declared:
            value = doc.get(field)
            if isinstance(value, str):
                match = ENV_PLACEHOLDER.search(value)
                if match:
                    secrets.append((doc.get("name") or doctype, field, match.group(1)))
    return secrets


def apply_l4(container: str, site: str, rows: list[dict], dry_run: bool) -> None:
    pending_secrets: list[tuple[str, str, str, str]] = []  # (doctype, name, field, env var)
    for row in l4_doctypes(rows):
        doctype_dir = CONFIG_DIR / row["doctype"]
        files = sorted(doctype_dir.glob("*.json")) if doctype_dir.is_dir() else []
        if not files:
            log.warning("config/%s/ missing or empty — skipped", row["doctype"])
            continue
        for path in files:
            doclist = load_json(path)
            if not isinstance(doclist, list):
                raise ValueError(f"{path.name}: expected a doclist (JSON list of docs)")
            for doc_name, field, var in collect_secrets(doclist, row["doctype"], row["secret_fields"]):
                pending_secrets.append((row["doctype"], doc_name, field, var))
            clean = substitute_env(doclist, path.name)
            log.info("import-doc %s/%s", row["doctype"], path.name)
            if not dry_run:
                docker_exec(container, f"mkdir -p {shlex.quote(CONTAINER_TMP + '/config/' + row['doctype'])}")
                with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
                    json.dump(clean, tmp)
                    tmp_path = Path(tmp.name)
                try:
                    docker_cp(container, tmp_path, f"{CONTAINER_TMP}/config/{row['doctype']}/{path.name}")
                    docker_exec(container, bench(site, f"import-doc {CONTAINER_TMP}/config/{shlex.quote(row['doctype'])}/{path.name}"))
                finally:
                    tmp_path.unlink(missing_ok=True)
    if not dry_run:
        for doctype, name, field, var in pending_secrets:
            if var not in os.environ:
                raise RuntimeError(f"secret placeholder <ENV:{var}> but {var} is not set")
            docker_exec(container, python_on_site(
                site,
                f"import os; frappe.client.set_value({doctype!r}, {name!r}, {field!r}, os.environ[{var!r}])",
            ))
            log.info("set secret field %s on %s %s from env %s", field, doctype, name, var)
        docker_exec(container, f"rm -rf {CONTAINER_TMP}/config", check=False)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--container", default=DEFAULT_CONTAINER, help="backend container name (env ERPNEXT_CONTAINER)")
    parser.add_argument("--site", default=DEFAULT_SITE, help="site name (env ERPNEXT_SITE)")
    parser.add_argument("--dry-run", action="store_true", help="print the ordered plan, execute nothing")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")
    load_env(REPO_ROOT / ".env")
    try:
        rows = read_ownership()
        for row in l4_doctypes(rows):
            for path in sorted((CONFIG_DIR / row["doctype"]).glob("*.json")):
                refs = env_references(load_json(path))
                missing = [v for v in refs if v not in os.environ]
                if missing and not args.dry_run:
                    raise RuntimeError(f"{path.name}: missing env vars: {', '.join(missing)} (put them in .env)")
        if args.dry_run:
            log.info("plan (dry run):")
            for step in plan_steps(rows):
                log.info("  %s", step)
            return 0
        apply_site_config(args.container, args.site, dry_run=False)
        apply_bootstrap(args.container, args.site, dry_run=False)
        apply_app(args.container, args.site, dry_run=False)
        apply_l4(args.container, args.site, rows, dry_run=False)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        if isinstance(error, subprocess.CalledProcessError):
            detail = "\n".join(part for part in (error.stdout.strip(), error.stderr.strip()) if part) or "(no output)"
            log.error("command failed (%d): %s\n%s", error.returncode, " ".join(error.cmd), detail)
        else:
            log.error("%s", error)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
