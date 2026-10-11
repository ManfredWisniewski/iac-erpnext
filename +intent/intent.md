# Intent: `iac-erpnext`

## Purpose

`iac-erpnext` provides a declarative, Git-versioned way to **set up and configure an ERPNext site**: bootstrap (setup wizard), site config keys, system/domain settings, customisations, workflows, users — applied reproducibly, with an export path that detects UI drift. The container deployment (L0) is a solved prerequisite owned by `aedar`/`wit.docker_apps`; this repository owns configuration state, not containers.

Source plan: `+wit/development/plans/erpnext/2026-10-11_plan-erpnext-iac.md` (approved by owner instruction 2026-10-11); research: `+wit/research/development/erpnext/2026-10-11-erpnext-iac-feasibility.md`. The model follows the `wit-iac-n8n` pattern (Git → instance tools, export mirror, credentials by name).

State:

- Target instance: ERPNext `frappe/erpnext:v16.26.2` on `devansible.wit` (192.168.2.80), deployed by `wit.docker_apps` (`tasks/app-erpnext.yml`); site `frontend` behind self-signed Traefik.
- Used by: agents and humans applying/exporting site configuration; the IaC repo clone lives on the ERPNext host.
- Problem solved: ERPNext configuration created via Desk clicks is unversioned and unrepeatable; this repo makes a fresh stack rebuild to a fully configured site from Git alone.

## Concepts

- **Layer model (L0–L5)**: L0 infra (aedar, out of scope here); L1 bootstrap (`setup_complete` on a fresh site); L2 `site_config.json` non-secret keys; L3 custom app + fixtures (`bench migrate`); L4 declared DocType records (`bench import-doc`); L5 business data (never Git, `bench backup`).
- **Ownership**: every DocType is declared `git` (written from Git, UI edits overwritten), `ui` (excluded from exports) or `data` (business data) in `src/ownership.csv` — the core design artefact.
- **Fresh site**: a site where no `Company` exists; only there may the setup wizard run.
- **Drift**: difference between `exports/` (nightly site export) and `config/`+`app/` (declared state); reviewed by a human, never auto-reverted.

## Scope

- In scope: `tools/` (apply/export/backup), `src/` (bootstrap args, site-config template, ownership matrix), `app/wit` (Frappe app with DocTypes and fixtures), `config/` (declared L4 doclist JSON), `exports/` (tool-written mirror), `erpnext.wit/` (facts + credential names), `deploy/` (host-side snippets for `aedar`).
- Out of scope: container/infra changes (`aedar`, `wit.docker_apps` — deliverables are proposals in `deploy/`); business data; running Ansible playbooks (always human); REST transport (documented alternative, not built).

## Software projects

### Configuration

- `src/ownership.csv` — `doctype,owner(git|ui|data),export(fixtures|export-json|none),apply_order,secret_fields`; `#` comment lines ignored. `apply_order` orders L4 `import-doc` runs (parents before children); `secret_fields` lists top-level fields masked on export and set from env after import.
- `src/bootstrap/setup_wizard.json` — args dict for `setup_complete`; values `<ENV:VAR>` are substituted from `.env`/environment at apply time (never committed resolved).
- `src/site_config.template.json` — non-secret `site_config.json` keys; `<ENV:VAR>` substitution applies.
- `config/<DocType>/<name>.json` — doclist files (JSON list of doc dicts, children embedded) in `export-json` format.
- `exports/` — written only by `tools/erpnext_export.py` (D08); never hand-edited.

### Processing order (apply)

1. `set-config` every key from `src/site_config.template.json` (L2).
2. Probe `frappe.db.count('Company')`; if `0`, run `setup_complete` with the substituted bootstrap args (L1) — skipped otherwise (idempotent).
3. `install-app wit` if missing from `list-apps`, then `bench migrate` (L3 fixtures + schema).
4. `import-doc` per `config/` file ordered by `apply_order`, then post-import `frappe.client.set_value` for every `<ENV:>` placeholder found (secrets lane).

### Main workflows

- **Apply** (`tools/erpnext_apply.py`): Git → site; `--dry-run` prints the ordered plan; idempotent (upserts, guarded bootstrap, migrate no-ops).
- **Export/drift** (`tools/erpnext_export.py`): site → `exports/`; guard rails: lock file, clean branch on `ERPNEXT_BACKUP_REPO`, abort on empty export, commit `chore(backup): …` only on change, optional push/pull.
- **Backup** (`tools/erpnext_backup.py`): `bench backup --with-files` → dated archives outside Git, `--keep N` rotation; `--config-only` runs the export tool instead.
- All three run on the host via `docker exec -u frappe <container>_backend` (self-signed Traefik cert; D12).

### Public functions

- `read_ownership(path)` — parse `ownership.csv` into row dicts (all tools).
- `substitute_env(value)` — resolve `<ENV:VAR>` placeholders; raises on missing env var.
- `docker_exec(container, command)` / `bench(site, args)` — command builders (apply, export, backup).
- `mask_secrets(doclist, secret_fields)` — replace declared secret fields with `<REDACTED>` (export).

### Data and file formats

- Doclist JSON: `[{"doctype": ..., "name": ..., ...fields, "child_table": [{"doctype": "Child DT", ...}]}]` — `export-json`/`import-doc` round-trip format (verified against frappe `version-16`: `export_json` strips `modified_by/creation/owner/idx/lft/rgt` and child meta keys).
- Fixtures: `<app>/<app>/fixtures/<doctype>.json`, same doclist format, written by `export-fixtures`, imported by `migrate`.
- `<ENV:VAR_NAME>` — secret placeholder in authored JSON; `<REDACTED>` — export mask for declared secret fields.

### Safety and preservation

- Secrets never enter Git: `.env` is git-ignored; bootstrap args travel into the container as a temp file, never on the command line; `site_config.json` is never committed (template only).
- Exports are append/overwrite mirrors inside `exports/` only; a failed or empty export aborts before touching the repo.
- `import-doc` and fixtures are upsert-only: removing a record from Git does not delete it on the site (documented limitation, teardown = explicit patch).
- `erpnext_export.py`/`erpnext_backup.py` refuse to run on a dirty repo or wrong branch.

## Tests and verification

Acceptance criteria and test commands: `tests.md`.

## Non-goals and limitations

- No full-state mirroring: L5 data and UI-owned doctypes are not represented.
- Deletions are not propagated (upsert-only); no auto-revert of UI drift — export diff is a review signal.
- `Role`/`User` ownership is deferred (fixture perf history); only admin user exists in v1.
- Single instance (`devansible.wit`); production promotion parked.

## Open items

Open tasks: `+team/+tasks/trurl.md`. Unresolved design decisions: `decisions.md`, section "Backlog". Live-verification blockers: `open-issues.md`.
