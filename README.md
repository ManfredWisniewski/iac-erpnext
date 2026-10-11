# iac-erpnext

Declarative, Git-versioned setup and configuration for the ERPNext site on `devansible.wit` — same IaC pattern as `wit-iac-n8n`: Git is the desired state for configuration, tools apply it through `docker exec … bench`, and a nightly export mirrors owned doctypes back into `exports/` as the drift signal.

Container deployment (L0) is owned by `aedar`/`wit.docker_apps`; this repo owns configuration state (L1–L4). Business data never enters Git (L5, `bench backup` archives).

## Layout

```text
src/ownership.csv                doctype → git|ui|data, export mode, apply order, secret fields
src/bootstrap/setup_wizard.json  L1 — setup_complete args (<ENV:> placeholders)
src/site_config.template.json    L2 — non-secret site_config keys
app/wit/                         L3 — Frappe app (DocTypes, hooks.py fixtures)
config/<DocType>/<name>.json     L4 — declared doclist records (import-doc)
exports/                         tool-written mirror (never hand-edit)
tools/erpnext_apply.py           Git → site apply (L2 → L1 → L3 → L4), --dry-run
tools/erpnext_export.py          site → exports/ mirror + commit on change
tools/erpnext_backup.py          bench backup --with-files → archive dir, rotation
erpnext.wit/                     instance facts + credential names (no secrets)
deploy/                          proposed aedar host_vars (P1) + app bind-mount (P4a)
```

## Usage (on the ERPNext host)

```sh
cd /opt/iac-erpnext && cp .env.example .env   # fill values, never commit
python tools/erpnext_apply.py --dry-run       # show the ordered plan
python tools/erpnext_apply.py                 # apply Git -> site (idempotent)
python tools/erpnext_export.py --dry-run -v   # show drift without committing
python tools/erpnext_backup.py                # data backup to $ERPNEXT_BACKUP_DIR
```

Unit tests run anywhere (no instance needed): `python -m unittest discover -s tools -v`.

## Docs

- Intent, decisions, acceptance criteria: `+intent/`
- Plan: `+wit/development/plans/erpnext/2026-10-11_plan-erpnext-iac.md`
- Feasibility research: `+wit/research/development/erpnext/2026-10-11-erpnext-iac-feasibility.md`
- Open issues / live-verification blockers: `open-issues.md`
