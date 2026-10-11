# Changelog

All notable changes to this project are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) (`+wit/common/conventions/changelog.md`); versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `+intent/` intent, decisions and acceptance criteria from the approved plan `2026-10-11_plan-erpnext-iac.md` (D02–D12).
- `src/ownership.csv` DocType ownership matrix, `src/bootstrap/setup_wizard.json` (L1), `src/site_config.template.json` (L2).
- `app/wit` Frappe app skeleton: `Wit Note` seed DocType, fixtures list, seed approval workflow fixtures.
- `config/` L4 declared records: System/Selling/Buying/Stock/Accounts Settings, Letter Head, Email Account (sans password), Role Profile, Workspace.
- `tools/erpnext_apply.py` (L2→L1→L3→L4 apply, `--dry-run`, `<ENV:>` secrets lane), `tools/erpnext_export.py` (export-json + fixtures mirror, guard rails, secret masking), `tools/erpnext_backup.py` (bench backup archives + rotation) — stdlib-only, with unit tests.
- `erpnext.wit/` facts + credential names, `deploy/` aedar host_vars proposal, `.env.example`, `open-issues.md`.

## [<version>] - <YYYY-MM-DD>

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security
