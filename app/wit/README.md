# wit

WIT customisations for ERPNext — custom DocTypes, fixtures (Workflow, Custom
Field, Property Setter, Print Format, Email Template, Client/Server Script)
and the glue code that cannot be expressed as `config/` doclists.

Deployed as a bench app: the IaC repo clone on the host bind-mounts this
directory to `/home/frappe/frappe-bench/apps/wit` (plan P4 option a,
`deploy/devansible-vars.erpnext.yml`); `tools/erpnext_apply.py` runs
`install-app wit` + `bench migrate`.

Fixtures are exported by `tools/erpnext_export.py` — author changes in Desk
only for doctypes declared `git` in `src/ownership.csv`, then export;
this directory is mirrored to `exports/fixtures/` as the drift signal.
