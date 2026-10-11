# Decision records — `iac-erpnext`

*Session date: 2026-10-11. Format per `+wit/common/conventions/decisions.md`; requirement levels per `+wit/common/specifications.md`.*

## Template source

- **D01 Initialised as a `development` project with `+wit/scripts/init-repo`** from the `+wit` templates (revision `7120036`, 2026-10-04). The copied files are point-in-time and owned by this project (wit-templates D03).

## Scope and configuration model

- **D02 Five-layer configuration model L0–L5** (alternatives: full-state mirroring; fixtures-only). Site state is split by ownership: L0 infra (aedar/`wit.docker_apps`), L1 bootstrap via `setup_complete`, L2 `site_config.json` keys, L3 app + fixtures via `bench migrate`, L4 declared DocType records via `import-doc`, L5 data out of Git. ERPNext state is inherently split between code (Git-able) and data (DB-only) — layering makes the boundary explicit (plan "Configuration model").
- **D03 DocType ownership matrix in `src/ownership.csv`** (alternatives: implicit convention; per-file headers). Every owned/configured DocType is classified `git`, `ui` or `data` with export mode and apply order — one artefact drives both `erpnext_apply.py` ordering and `erpnext_export.py` drift detection.
- **D04 Secrets never in Git** (n8n D04-analog). Authored JSON carries `<ENV:VAR>` placeholders substituted from `.env`/environment at apply time; `site_config.json` (contains `db_password`) is never committed — only `src/site_config.template.json`. Secret doc fields are masked to `<REDACTED>` in exports and set post-import via `frappe.client.set_value`.
- **D05 Tools are Python standard-library only** (n8n D09-analog; the host has no virtualenv) and run on the ERPNext host.
- **D06 Transport is `docker exec -u frappe <container>_backend bench …`** (alternatives: REST API from outside). The Traefik cert is self-signed and the host already runs the backend container; REST stays a documented alternative (n8n D16-analog).
- **D07 Site name `frontend`** (alternative: `erpnext.devansible.wit`). Role default `erpnext_site_name` already creates `frontend`; renaming adds churn without value.
- **D08 `exports/` is a tool-written mirror, never hand-edited**; commits happen only on change (`chore(backup): …`), same guard rails as `n8n_backup.py` (clean branch, lock file, abort on empty export).
- **D09 Upsert-only semantics accepted** (alternative: custom delete propagation). Fixture sync and `import-doc` do not delete records removed from Git; teardown is an explicit app patch/`delete_doc`. Documented limitation, not silent.

## Repository and delivery

- **D10 Repository `iac-erpnext`; the Frappe app `wit` lives inside it at `app/wit`** (alternatives: separate app repo + `bench get-app`; baked image via `apps.json`). Bind-mount into the bench `apps/` directory gives the tightest dev loop on the test VM (plan recommendation a); production delivery may later switch to a repo + `get-app` or a custom image.
- **D11 Bootstrap company identity: WIT test values** (name `WIT`, abbr `WIT`, Germany, EUR, timezone `Europe/Berlin`, chart of accounts `SKR03`, fiscal year calendar year). Test-instance values; the owner may amend `src/bootstrap/setup_wizard.json` — the COA template name is verified against v16 on first live run.
- **D12 Backup: two lanes** (plan D09-analog). `erpnext_backup.py` produces `bench backup --with-files` archives outside Git (rotation 14, RTO same-day / RPO 24 h for the test instance); `erpnext_export.py` on host cron produces the config mirror into `exports/`. Cron deployment via `aedar` host vars.

## Backlog (not decided, parked)

- REST-based deploy transport (D16-analog; needs cert/token story).
- Owning `Role`/`Role Profile` via fixtures (historical migrate perf issues — verify on v16 before adding) and `User` as `git` doctype.
- Authentik OIDC setup (recipe exists in role README); `erpnext_germany`/`hrms` apps on the site.
- Custom image via `apps.json` for production; production host promotion; CI pipeline.
- Naming Series doctype name on v16 ("Document Naming Settings"?), Workspace JSON schema — authored files pending first live `export-json` comparison.
- `erpnext_app_sources` role extension in `wit.docker_apps` for the bind-mount (proposal in `deploy/`).
- `submodule.recurse` repo setting vs the +wit convention "submodule.recurse=false" — repo currently follows init-script default (`true`); pulls with unpushed gitlink-touching commits hit git's rebase guard (use `git -c submodule.recurse=false pull`).
