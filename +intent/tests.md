# Tests and acceptance criteria — `iac-erpnext`

*Format per `+wit/development/bestpractices/tests.md`. Criteria are numbered `A01`, `A02`, ... and never renumbered.*

## Commands

```text
test:   python -m unittest discover -s tools -v
lint:   npx markdownlint-cli2 "**/*.md"
build:  python -m compileall tools app
```

`tools/` are Python standard-library only (D05); tests mock `docker exec` — no live instance required. `python tools/erpnext_apply.py --dry-run` validates the authored `src/`/`config/` files without a site.

## Acceptance criteria

### A01 Repository structure

- `README.md`, `AGENTS.md`, `+team/+tasks/README.md`, `+team/+tasks/backlog.md`, `+intent/{intent,decisions,tests}.md`, `.gitignore`, `.markdownlint-cli2.jsonc` exist at the root.
- Branches `main`, `work`, `wip` and submodules `+wit`, `+wit-agents` exist per `+wit/common/conventions/repo-setup.md`.

### A02 Ownership matrix

- `src/ownership.csv` parses; every row has `owner` ∈ {`git`, `ui`, `data`} and `export` ∈ {`fixtures`, `export-json`, `none`}; `git`+`export-json` rows carry an integer `apply_order`; `secret_fields` lists only fields present in the authored `config/` JSONs.

### A03 Apply tool (offline)

- `python tools/erpnext_apply.py --dry-run` prints the ordered plan (L2 → L1 probe → L3 → L4) without executing commands.
- Unit tests pass: env substitution incl. missing-var failure; apply ordering by `apply_order`; secret `<ENV:>` extraction; `set-config` `-p` selection for non-string values; fresh-site probe parsing.

### A04 Export tool (offline + guard rails)

- `python tools/erpnext_export.py --dry-run` runs on a clean repo on the configured branch and refuses on a dirty tree or wrong branch.
- Unit tests pass: secret fields masked to `<REDACTED>`; mirror sync add/update/remove; abort on empty export; no commit without changes.

### A05 Backup tool (offline)

- Unit tests pass: backup file groups by timestamp prefix; `--keep N` rotation removes oldest groups; `--config-only` delegates to the export tool.

### A06 No secrets in Git (negative case)

- `git grep -n "password"` across `config/`, `src/`, `exports/` shows only `<ENV:…>` placeholders / `<REDACTED>` masks — never a value.
- `src/site_config.template.json` contains no `db_password`/`encryption_key` values.

### A07 Frappe app skeleton

- `app/wit` follows `bench new-app` layout (`pyproject.toml`, `wit/hooks.py`, `wit/modules.txt`, module dir `wit/wit/`); `hooks.py` declares the v1 fixture list; seed DocType `Wit Note` JSON parses and carries `module: "Wit"`; seed workflow fixtures parse.

### A08 Live: bootstrap (blocked until P1 stack exists — manual)

- On the fresh stack, `erpnext_apply.py` runs L2 → L1 → L3 → L4; Desk login lands on home (wizard skipped); Company/COA/Fiscal Year exist.
- Second run is a clean no-op.

### A09 Live: app + fixtures (manual)

- `wit` appears in `bench --site frontend list-apps`; `Wit Note` is usable in Desk; the seed approval workflow offers Approve/Reject.

### A10 Live: config + drift round-trip (manual)

- `erpnext_export.py` produces `exports/` JSON matching declared `config/` on owned doctypes; a UI edit on a `git` doctype shows up as an export diff (drift signal).

### A11 Live: rebuild proof — the IaC acceptance test (manual)

- `erpnext_install: "remove"` → `"once"` → `erpnext_apply.py` yields a fully configured site from Git alone with zero UI steps; post-export `exports/` diff is empty.

## Not tested

- Live bench behaviour (A08–A11) — blocked until the stack is deployed on `devansible.wit` (aedar, human-run playbook). Command lines are built from verified v16 CLI signatures (`export-json`, `import-doc`, `set-config -p`, `execute --kwargs`), not from a live run.
- `import-doc` acceptance of hand-authored doclists (children meta fields, unknown-field tolerance) — first live apply validates.
- Email Account/Workspace field sets on v16 — conservative subsets authored; export diff will surface drift.
