# Open issues — iac-erpnext

Everything that could not be completed or verified without a live instance or
owner input, collected on 2026-10-11 (implementing
`+wit/development/plans/erpnext/2026-10-11_plan-erpnext-iac.md`). Ordered by
phase; ✅ = done this session.

## P0 — Decisions & VM check

- ✅ Layer model, repo, site name recorded as `+intent/decisions.md` D02–D12
  (defaults chosen where the plan left them open — amend there, don't fork).
- ⬜ VM check on devansible.wit not possible from this session: run
  `free -g`, `df -h`, `docker ps`, confirm Traefik + DNS for
  `erpnext.devansible.wit` (plan wants ≥ 4 GB RAM / 15 GB disk).
- ⬜ Owner confirmation of D11 bootstrap identity (company WIT/WIT, COA
  `SKR03`, FY = calendar year, email `admin@wit.internal`).

## P1 — Stack up (aedar, human)

- ✅ `deploy/devansible-vars.erpnext.yml` — host_vars proposal ready.
- ⬜ Human: copy the block into `aedar/host_vars/devansible.wit/vars.yml`, run
  the play once to scaffold `vault_erpnext.yml`, `ansible-vault encrypt` it,
  re-run `devansible-docker_apps.yml`.
- ⬜ After deploy: fill `erpnext.wit/facts.md` "Open facts" (`bench version`,
  `list-apps`, container names).
- ⚠️ Do **not** click through the Desk setup wizard — L1 owns it.

## P2 — Facts + repo skeleton

- ✅ `erpnext.wit/{facts.md,credentials.md}`, `src/ownership.csv` v1,
  `+intent/` docs, `.env.example`.
- ⬜ `bench version` + live facts after P1.

## P3 — Bootstrap as code (L1+L2)

- ✅ `src/bootstrap/setup_wizard.json`, `src/site_config.template.json`,
  `erpnext_apply.py` with guarded fresh-site probe + file-injected secrets.
- ⬜ Live: verify `setup_complete` accepts the args on v16.26.2 — especially
  `chart_of_accounts: "SKR03"`, `domains`, `bank_account` (args are not a
  stable API; plan risk #1).
- ⬜ Live: confirm `bench --site frontend execute "frappe.db.count('Company')"`
  prints a bare integer (probe parsing).

## P4 — App + fixtures (L3)

- ✅ `app/wit` skeleton (`Wit Note` + seed approval workflow fixtures), option
  (a) bind-mount chosen (D10).
- ⬜ `wit.docker_apps` change needed: new var `erpnext_app_sources` rendering
  extra volume mounts in `templates/erpnext-compose.yml.j2` for
  backend/queue-*/scheduler services + `ls apps > sites/apps.txt` refresh
  (snippet in `deploy/devansible-vars.erpnext.yml`; germany/hrms tasks are
  the reference). Separate repo — needs its own session/decision.
- ⬜ Live: does the Workflow fixture auto-create `workflow_state` on `Wit Note`
  in v16? If not, add a Custom Field fixture.
- ⬜ Live: verify fixture doctype names on v16 (`Workflow Action Master` vs
  renamed equivalents) after first `export-fixtures`.

## P5 — Declared records + export/drift loop

- ✅ `config/` v1 (5 Singles, Letter Head, Email Account sans password,
  Role Profile, Workspace), `erpnext_export.py` + `erpnext_backup.py`.
- ⬜ Live: `import-doc` round-trip on hand-authored doclists — unknown-field
  tolerance and embedded-child handling to be validated field-by-field via
  first export diff.
- ⬜ Email Account is authored disabled (`enable_outgoing: 0`,
  `awaiting_password: 1`) as a safe default — set real SMTP values and flip
  flags once the mailbox exists; possible SMTP validation on save is an open
  verification item.
- ⬜ Naming Series not authored — v16 uses "Document Naming Settings"? Decide
  ownership after checking the live doctype list.
- ⬜ Cron on host for `erpnext_export.py` + `erpnext_backup.py` — deploy via
  aedar (n8n D09–D12 pattern); pending P1.

## P6 — Rebuild proof

- ⬜ Blocked on P1–P5 live: `erpnext_install: "remove"` → `"once"` → apply →
  empty exports diff (acceptance A11).

## P7 — Parked

- Users/roles beyond admin, Role/Role Profile fixture perf on v16, Authentik
  OIDC, `erpnext_germany`/`hrms`, custom `apps.json` image, REST deploy
  transport, production promotion, CI — see `+intent/decisions.md` backlog.

## Repo housekeeping

- `git pull --rebase` fails while local commits touch submodule gitlinks
  (`submodule.recurse=true` → "cannot rebase with locally recorded submodule
  modifications"). Workaround: `git -c submodule.recurse=false pull`. The
  +wit convention now recommends `submodule.recurse=false` — repo follows the
  init-script default `true`; decide once in aedar/`+intent` (backlog).
- `origin` has only the initial commit; `main`, `work`, `wip` + this branch's
  work need a first push by/with the owner.
