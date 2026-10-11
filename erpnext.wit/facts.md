# Facts: ERPNext on devansible.wit

Verified facts about the ERPNext instance. Update when the instance changes; record the date of verification. No secrets.

| Fact | Value | Verified |
|------|-------|----------|
| Host | `devansible.wit` (192.168.2.80) | 2026-10-11 |
| Public URL | `https://erpnext.devansible.wit` (Traefik, self-signed cert) | 2026-10-11 |
| Image | `frappe/erpnext:v16.26.2` | 2026-10-11 (role `wit.docker_apps` defaults) |
| MariaDB image | `mariadb:11.8` | 2026-10-11 (role defaults) |
| Redis image | `redis:6.2-alpine` | 2026-10-11 (role defaults) |
| Site name | `frontend` | 2026-10-11 (role default `erpnext_site_name`, D07) |
| Container pattern | `erpnext_backend`, `erpnext_frontend`, `erpnext_websocket`, `erpnext_db`, `erpnext_redis-queue`, `erpnext_redis-cache`, `erpnext_queue-*`, `erpnext_scheduler`, `erpnext_configurator` | 2026-10-11 (compose template) |
| Bench home in container | `/home/frappe/frappe-bench` | 2026-10-11 (compose template) |
| Host paths | sites `/opt/containers/erpnext/sites`, logs `/opt/containers/erpnext/logs`, db `/opt/containers/erpnext/mariadb`, redis-queue `/opt/containers/erpnext/redis-queue` | 2026-10-11 (role defaults) |
| Secrets | `host_vars/devansible.wit/vault_erpnext.yml` (`erpnext_db_root_password`, `erpnext_admin_password`), scaffolded by `wit_generate_secrets` | 2026-10-11 (role `app-erpnext.yml`) |
| Installed apps on site | `frappe`, `erpnext` (+ `wit` after first apply) | pending A09 |
| Deployed | not yet — playbook run pending (P1) | — |

## Open facts to verify (first live session)

- `bench version` output (frappe + erpnext exact versions).
- `export-json` output shape per owned doctype (field sets in `config/`).
- `chart_of_accounts` value `SKR03` accepted by `setup_complete` on v16.
- `workflow_state` custom field auto-created by the seed `Workflow` fixture.
- Whether Email Account `save`/`import-doc` triggers SMTP validation.
- RAM/disk headroom on devansible.wit (stack ≈ 10 containers; plan wants ≥ 4 GB RAM / 15 GB disk).
