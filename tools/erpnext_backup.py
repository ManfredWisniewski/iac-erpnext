#!/usr/bin/env python3
"""Data-lane backup: bench backup --with-files on the ERPNext host.

Archives are binary (SQL dump + file tars) — they never enter Git (D12);
the Git mirror of configuration is erpnext_export.py. The newest backup set
is copied out of the container to ERPNEXT_BACKUP_DIR and older sets are
pruned beyond --keep.

`--config-only` runs the export tool instead of a data backup (D12 two lanes).

Runs via cron on the ERPNext host. Standard library only (D05).

Exit codes: 0 success, 1 failure, 2 already running.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BENCH_HOME = "/home/frappe/frappe-bench"

DEFAULT_CONTAINER = os.environ.get("ERPNEXT_CONTAINER", "erpnext_backend")
DEFAULT_SITE = os.environ.get("ERPNEXT_SITE", "frontend")
DEFAULT_BACKUP_DIR = Path(os.environ.get("ERPNEXT_BACKUP_DIR", "/opt/erpnext-backups"))
DEFAULT_KEEP = int(os.environ.get("ERPNEXT_BACKUP_KEEP", "14"))

# frappe backup files: <YYYYMMDD>_<HHMMSS>-<site>-<part>.<ext>
STAMP = re.compile(r"^(\d{8}_\d{6})-")

log = logging.getLogger("erpnext_backup")


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    log.debug("$ %s", " ".join(cmd))
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def docker_exec(container: str, command: str) -> subprocess.CompletedProcess[str]:
    return run(["docker", "exec", "-u", "frappe", container, "bash", "-lc", command])


def remote_backup_dir(site: str) -> str:
    return f"{BENCH_HOME}/sites/{site}/private/backups"


def list_backup_files(container: str, site: str) -> list[str]:
    result = docker_exec(container, f"ls -1 {remote_backup_dir(site)}")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def group_by_stamp(files: list[str]) -> dict[str, list[str]]:
    """Group backup file names by their leading timestamp; files without one are skipped."""
    groups: dict[str, list[str]] = {}
    for name in files:
        match = STAMP.match(name)
        if match:
            groups.setdefault(match.group(1), []).append(name)
    return groups


def newest_stamp(groups: dict[str, list[str]]) -> str:
    if not groups:
        raise RuntimeError("no backup files found after bench backup")
    return sorted(groups)[-1]


def backup(container: str, site: str, dest: Path, keep: int, dry_run: bool) -> int:
    if not dry_run:
        docker_exec(container, f"cd {BENCH_HOME} && bench --site {shlex.quote(site)} backup --with-files")
    groups = group_by_stamp(list_backup_files(container, site))
    stamp = newest_stamp(groups)
    log.info("backup set %s: %s", stamp, ", ".join(sorted(groups[stamp])))
    dest.mkdir(parents=True, exist_ok=True)
    for name in groups[stamp]:
        log.info("%s %s", "would copy" if dry_run else "copying", name)
        if not dry_run:
            run(["docker", "cp", f"{container}:{remote_backup_dir(site)}/{name}", str(dest / name)])
    dest_groups = group_by_stamp([p.name for p in dest.iterdir() if p.is_file()])
    for old in sorted(dest_groups)[: max(len(dest_groups) - keep, 0)]:
        for name in dest_groups[old]:
            log.info("pruning %s", dest / name)
            if not dry_run:
                (dest / name).unlink()
    return 0


def config_only() -> int:
    script = REPO_ROOT / "tools" / "erpnext_export.py"
    log.info("config-only: running %s", script)
    return run([sys.executable, str(script)], check=False).returncode


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--container", default=DEFAULT_CONTAINER, help="backend container name (env ERPNEXT_CONTAINER)")
    p.add_argument("--site", default=DEFAULT_SITE, help="site name (env ERPNEXT_SITE)")
    p.add_argument("--dest", type=Path, default=DEFAULT_BACKUP_DIR, help="archive dir outside Git (env ERPNEXT_BACKUP_DIR)")
    p.add_argument("--keep", type=int, default=DEFAULT_KEEP, help="backup sets to keep (env ERPNEXT_BACKUP_KEEP)")
    p.add_argument("--config-only", action="store_true", help="run erpnext_export.py instead of a data backup")
    p.add_argument("--dry-run", action="store_true", help="show what would run, change nothing")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if args.config_only:
        return config_only()
    lock_path = Path(tempfile.gettempdir()) / "erpnext_backup.lock"
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        log.error("another backup is running (lock %s)", lock_path)
        return 2
    try:
        os.write(lock_fd, str(os.getpid()).encode())
        return backup(args.container, args.site, args.dest, args.keep, args.dry_run)
    except subprocess.CalledProcessError as e:
        detail = "\n".join(part for part in (e.stdout or "", e.stderr or "") if part.strip())
        log.error("command failed (%d): %s\n%s", e.returncode, " ".join(e.cmd), detail.strip())
        return 1
    except RuntimeError as e:
        log.error("%s", e)
        return 1
    finally:
        os.close(lock_fd)
        lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
