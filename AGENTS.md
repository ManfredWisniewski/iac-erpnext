# Instructions for AI agents

This repository is `iac-erpnext`. Read `+wit/development/README.md`, `+wit/development/AGENTS.md` and `+intent/` before making changes.

## Rules

The shared rules in `+wit/AGENTS.md` (*Shared rules* section) apply. Additionally:

- Never write credential values into this repository; `erpnext.wit/credentials.md` holds names only (D04). Secrets in authored JSON are `<ENV:VAR>` placeholders.
- Instance facts live in `erpnext.wit/facts.md`; look them up there, and record newly verified facts with a date.
- Files under `exports/` are written by `tools/erpnext_export.py` (D08); never edit them by hand.
- DocType ownership lives in `src/ownership.csv` (D03): `git` doctypes are applied from this repo and UI edits are overwritten — declare every DocType before authoring `config/` files for it.
- `tools/` MUST stay Python standard-library only (D05); the host has no virtualenv.
- Tools reach the site via `docker exec -u frappe <container>_backend bench …` on the host (D06) — never over HTTPS/REST (self-signed Traefik cert).
- Agents never run Ansible playbooks; `deploy/` holds proposals for the `aedar` repo — a human applies and runs them.
- `src/bootstrap/setup_wizard.json` args are pinned to `frappe/erpnext:v16.26.2` — re-verify `setup_complete` args on image upgrades (facts.md).
- Fixture and import-doc sync are upsert-only (D09): deletions need an explicit app patch, not file removal.

## Commands

```text
test:   python -m unittest discover -s tools -v
lint:   npx markdownlint-cli2 "**/*.md"
build:  python -m compileall tools app
dry:    python tools/erpnext_apply.py --dry-run
```
