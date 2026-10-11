#!/usr/bin/env python3
"""Export git-owned ERPNext site configuration from the backend container into Git.

Site -> Git mirror (D08): `bench export-json` for every `git`/`export-json`
doctype in src/ownership.csv (covers Singles and all named docs) plus
`bench export-fixtures --app wit` for the fixture lane. Files land in exports/
and are committed only on change. Declared secret fields are masked to
<REDACTED> before writing (D04).

Runs daily via cron on the ERPNext host. Standard library only (D05).
This file is also the drift detector: a UI change on an owned doctype shows
up as a diff in exports/.

Exit codes: 0 success (with or without changes), 1 failure, 2 already running.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import logging
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORTS_DIR = REPO_ROOT / "exports"
BENCH_HOME = "/home/frappe/frappe-bench"
CONTAINER_EXPORT_DIR = "/tmp/wit-export"
FIXTURES_CONTAINER_DIR = f"{BENCH_HOME}/apps/wit/wit/fixtures"

DEFAULT_REPO = Path(os.environ.get("ERPNEXT_BACKUP_REPO", str(REPO_ROOT)))
DEFAULT_CONTAINER = os.environ.get("ERPNEXT_CONTAINER", "erpnext_backend")
DEFAULT_SITE = os.environ.get("ERPNEXT_SITE", "frontend")
DEFAULT_BRANCH = os.environ.get("ERPNEXT_BACKUP_BRANCH", "main")

log = logging.getLogger("erpnext_export")


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    log.debug("$ %s", " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd, check=check, text=True, capture_output=True)


def docker_exec(container: str, command: str) -> subprocess.CompletedProcess[str]:
    return run(["docker", "exec", "-u", "frappe", container, "bash", "-lc", command])


def bench(site: str, args: str) -> str:
    return f"cd {BENCH_HOME} && bench --site {shlex.quote(site)} {args}"


def read_ownership(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(line for line in handle if not line.lstrip().startswith("#"))
        for row in reader:
            rows.append({
                "doctype": (row.get("doctype") or "").strip(),
                "owner": (row.get("owner") or "").strip(),
                "export": (row.get("export") or "").strip(),
                "secret_fields": [f.strip() for f in (row.get("secret_fields") or "").split(";") if f.strip()],
            })
    return rows


def mask_secrets(doclist: list, secret_fields: list[str]) -> list:
    """Return a copy of doclist with declared secret fields replaced by <REDACTED>."""
    masked = []
    for doc in doclist:
        clone = dict(doc)
        for field in secret_fields:
            if clone.get(field) not in (None, "", "<REDACTED>"):
                clone[field] = "<REDACTED>"
        masked.append(clone)
    return masked


def export_json_docs(container: str, site: str, rows: list[dict], staging: Path) -> int:
    """export-json every git/export-json doctype; returns file count written."""
    docker_exec(container, f"mkdir -p {CONTAINER_EXPORT_DIR} && rm -f {CONTAINER_EXPORT_DIR}/*.json")
    try:
        count = 0
        for row in rows:
            target = staging / row["doctype"] / f"{row['doctype']}.json"
            remote = f"{CONTAINER_EXPORT_DIR}/{row['doctype']}.json"
            docker_exec(container, bench(site, f"export-json {shlex.quote(row['doctype'])} {shlex.quote(remote)}"))
            raw = json.loads(run(["docker", "exec", container, "cat", remote]).stdout)
            doclist = mask_secrets(raw, row["secret_fields"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(doclist, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
            count += 1
        return count
    finally:
        docker_exec(container, f"rm -rf {CONTAINER_EXPORT_DIR}")


def export_fixtures(container: str, site: str, staging: Path) -> int:
    """export-fixtures --app wit, then docker cp the fixtures dir out."""
    docker_exec(container, bench(site, "export-fixtures --app wit"))
    try:
        run(["docker", "cp", f"{container}:{FIXTURES_CONTAINER_DIR}/.", str(staging)])
    except subprocess.CalledProcessError:
        log.warning("no fixtures exported from %s", FIXTURES_CONTAINER_DIR)
        return 0
    return len(list(staging.glob("*.json")))


def mirror(source: Path, target: Path) -> tuple[int, int, int]:
    """Mirror source/*.json tree into target. Returns (added, updated, removed)."""
    src = {p.relative_to(source): p for p in source.rglob("*.json")}
    dst = {p.relative_to(target): p for p in target.rglob("*.json")} if target.is_dir() else {}
    added = updated = removed = 0
    for rel, s in src.items():
        d = dst.get(rel)
        if d is None:
            (target / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(s, target / rel)
            added += 1
        elif s.read_bytes() != d.read_bytes():
            shutil.copyfile(s, d)
            updated += 1
    for rel, d in dst.items():
        if rel not in src:
            d.unlink()
            removed += 1
    return added, updated, removed


def ensure_clean_branch(repo: Path, branch: str, pull: bool) -> None:
    current = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo).stdout.strip()
    if current != branch:
        raise RuntimeError(f"repository is on branch {current!r}, expected {branch!r}")
    if run(["git", "status", "--porcelain"], cwd=repo).stdout.strip():
        raise RuntimeError("repository has uncommitted changes; refusing to run")
    if pull:
        run(["git", "pull", "--ff-only", "origin", branch], cwd=repo)


def git_has_changes(repo: Path, subdir: str) -> bool:
    run(["git", "add", "-A", subdir], cwd=repo)
    return run(["git", "diff", "--cached", "--quiet"], cwd=repo, check=False).returncode != 0


def export(repo: Path, container: str, site: str, branch: str, push: bool, pull: bool, dry_run: bool) -> int:
    ensure_clean_branch(repo, branch, pull)
    rows = [r for r in read_ownership(repo / "src" / "ownership.csv")
            if r["owner"] == "git" and r["export"] == "export-json"]
    with tempfile.TemporaryDirectory(prefix="erpnext-export-") as tmp:
        staging = Path(tmp)
        count = export_json_docs(container, site, rows, staging / "config")
        fixture_count = export_fixtures(container, site, staging / "fixtures")
        if count + fixture_count == 0:
            raise RuntimeError("export produced no files; aborting to avoid wiping the mirror")
        added, updated, removed = mirror(staging, repo / "exports")
    log.info("exported %d config + %d fixture files: %d added, %d updated, %d removed",
             count, fixture_count, added, updated, removed)
    if not git_has_changes(repo, "exports"):
        log.info("no changes")
        return 0
    if dry_run:
        log.info("dry run: changes staged but not committed\n%s", run(["git", "status", "--short"], cwd=repo).stdout)
        run(["git", "reset", "--quiet", "exports"], cwd=repo)
        run(["git", "checkout", "--", "exports"], cwd=repo, check=False)
        run(["git", "clean", "-fdq", "exports"], cwd=repo)
        return 0
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    run(["git", "commit", "-m", f"chore(backup): erpnext config {stamp} (+{added} ~{updated} -{removed})"], cwd=repo)
    if push:
        run(["git", "push", "origin", branch], cwd=repo)
    log.info("committed%s", " and pushed" if push else "")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo", type=Path, default=DEFAULT_REPO, help="path of the git clone (env ERPNEXT_BACKUP_REPO)")
    p.add_argument("--container", default=DEFAULT_CONTAINER, help="backend container name (env ERPNEXT_CONTAINER)")
    p.add_argument("--site", default=DEFAULT_SITE, help="site name (env ERPNEXT_SITE)")
    p.add_argument("--branch", default=DEFAULT_BRANCH, help="branch to commit to (env ERPNEXT_BACKUP_BRANCH)")
    p.add_argument("--no-push", action="store_true", help="commit locally only")
    p.add_argument("--no-pull", action="store_true", help="skip git pull --ff-only before exporting")
    p.add_argument("--dry-run", action="store_true", help="show changes, commit nothing")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    lock_path = Path(tempfile.gettempdir()) / "erpnext_export.lock"
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        log.error("another export is running (lock %s)", lock_path)
        return 2
    try:
        os.write(lock_fd, str(os.getpid()).encode())
        return export(args.repo, args.container, args.site, args.branch, not args.no_push, not args.no_pull, args.dry_run)
    except subprocess.CalledProcessError as e:
        detail = "\n".join(part for part in (e.stdout or "", e.stderr or "") if part.strip())
        log.error("command failed (%d): %s\n%s", e.returncode, " ".join(e.cmd), detail.strip())
        return 1
    except (RuntimeError, ValueError, json.JSONDecodeError) as e:
        log.error("%s", e)
        return 1
    finally:
        os.close(lock_fd)
        lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
