# Impediment Log — iac-erpnext

> Purpose: Single, visible list of all blockers that prevent the team from delivering value.
> Owner: Manfred

## Active Impediments

| ID | Description | Impact | Affected Work | Reporter | Owner | Raised | Target | Status | Notes / Actions |
|----|-------------|--------|---------------|----------|-------|--------|--------|--------|-----------------|
| IMP-001 | ERPNext stack not deployed on devansible.wit — playbook runs are human-only | Major | A08–A11 (all live acceptance) | trurl | Manfred | 2026-10-11 | — | Open | host_vars proposal ready in `deploy/devansible-vars.erpnext.yml`; run devansible-docker_apps.yml, encrypt vault |
| IMP-002 | `erpnext_app_sources` bind-mount missing in wit.docker_apps | Major | P4 app delivery (option a) | trurl | Manfred | 2026-10-11 | — | Open | role change proposal in deploy/; alternative (b): separate app repo + `bench get-app` needs no role change |
| IMP-003 | `git pull --rebase` blocked by `submodule.recurse=true` + gitlink-touching commits | Minor | agent repo sync | trurl | Manfred | 2026-10-11 | — | Open | workaround `git -c submodule.recurse=false pull`; permanent fix = decide on convention (submodule.recurse=false) |

## Resolved / Closed Impediments

| ID | Description | Impact | Affected Work | Raised | Resolved | Root Cause / Learnings |
|----|-------------|--------|---------------|--------|----------|------------------------|
