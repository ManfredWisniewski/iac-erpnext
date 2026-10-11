# Credentials on erpnext.devansible.wit

Credentials live in Ansible vault (`host_vars/devansible.wit/vault_erpnext.yml`) and in the local `.env` on the host clone — never in this repository. This file lists names only.

| Name | Kind | Where the value lives | Used by |
|------|------|-----------------------|---------|
| `ERPNext Administrator` | site admin password | `vault_erpnext.yml` (`erpnext_admin_password`) → `.env` `ERPNEXT_ADMIN_PASSWORD` | L1 bootstrap (`src/bootstrap/setup_wizard.json` `<ENV:>`) |
| `erpnext_db_root_password` | MariaDB root | `vault_erpnext.yml` | role `create-site` only; not used by tools |
| `ERPNEXT_SMTP_PASSWORD` | SMTP password for `WIT Notifications` Email Account | `.env` on host | `config/Email Account/` `<ENV:>` → post-import `set_value` |
| `Frappe API deploy` | future `api_key:api_secret` pair for a REST deploy user | vault | parked (decisions.md backlog) |

`.env` keys understood by the tools: `ERPNEXT_CONTAINER` (default `erpnext_backend`), `ERPNEXT_SITE` (default `frontend`), `ERPNEXT_ADMIN_PASSWORD`, `ERPNEXT_SMTP_PASSWORD`, `ERPNEXT_BACKUP_REPO`, `ERPNEXT_BACKUP_BRANCH`, `ERPNEXT_BACKUP_DIR`, `ERPNEXT_BACKUP_KEEP`.
