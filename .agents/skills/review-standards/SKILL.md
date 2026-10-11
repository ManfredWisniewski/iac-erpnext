---
name: review-standards
description: Review WIT template repositories to find standards that exist only as practice but are not defined, or conventions that repos no longer follow. Use periodically or when a template/convention change lands. Produces a findings table — gaps with evidence and a proposed canonical home — for human decision.
compatibility: Requires checkouts of `wit-templates` (with `+wit-*` members initialised) and access to the `+wit` domains. Read-only; proposes, never changes.
metadata:
  scope: cross-repository
  review-type: standards-coverage
  version: "0.1"
---

# Review standards

Small audit: which rules are *practised* but not *written*, and which *written* rules are not practised. Output is a findings list for the owner — the skill does not create or edit standards.

## Inputs

- `scope` (optional): which member repos/domains to cover; default all `wit-*` under `wit-templates` (`wit-common`, `wit-agents`) including the `+wit` domains (`development/`, `marketing/`, `business/`, `design/`, `common/`).
- `reference` (optional): conventions baseline; default `+wit/common/conventions/` and `+wit-agents/` at the inspected revision.

## Procedure

1. **Inventory**: list the member repos (`wit-common`, `wit-agents`) and the `+wit` domains (`development/`, `marketing/`, `business/`, `design/`, `common/`), their `README.md`/`AGENTS.md`/`+intent/` (or domain `decisions.md`/`tests.md`) and template content. Record the inspected revision per repo.
2. **Map practice → definition**: for each recurring pattern found in ≥2 places (file layouts, frontmatter, skill format, doc headers, hooks, ignore rules), locate the document that defines it. No definition → standards gap.
3. **Map definition → practice**: for each convention MUST/SHOULD, check whether member repos and current template output actually follow it. Violation → conformance gap (distinguish "not yet rolled out" from "contradicted").
4. **Report**: findings table — `#`, gap, evidence (path + revision), certainty label, proposed canonical home, proposed action (`define` / `migrate` / `remove`). Deduplicate against known open items (check `+team/dominik/` and the member repos' `+intent/` backlog first).

## Rules

- Findings only — the owner decides which gaps deserve a standard.
- A missing standard is a *gap*, not automatically a defect: report whether the pattern occurs once (leave it) or recurs (candidate).
- Do not edit any reviewed repository.

## Completion criteria

All in-scope member repos inspected with revisions recorded; every recurring undocumented pattern and every unfollowed convention listed with evidence; findings table filed in `+team/dominik/`.
