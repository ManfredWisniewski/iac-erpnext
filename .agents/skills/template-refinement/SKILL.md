---
name: template-refinement
description: Review WIT templates for content overlap, duplication and collisions — the same section defined in several templates, contradictory variants, or references to files that do not exist. Use when templates drift, a new template type is added, or init-script copy behaviour changes. Produces an overlap report with proposed canonical sources; edits only after approval.
compatibility: Requires the `+wit` templates (`<domain>/templates/`, `common/templates/`) and the init scripts in `+wit/scripts/` at a recorded revision. Read-only by default; proposed edits go on the persona branch as PR.
metadata:
  scope: cross-repository
  review-type: overlap-collision
  version: "0.1"
---

# Template refinement

Templates are copied point-in-time into projects (wit-templates D03) — every duplicated block becomes N unmanaged copies downstream. This skill finds the duplication **before** it multiplies.

## Inputs

- `scope` (optional): template folders to compare; default all of `+wit` (`<domain>/templates/` for `development`, `marketing`, `business`, `design` plus `common/templates/` with `common/`, `persons/`, `+team/+tasks/`).
- `consumers` (optional): repositories to spot-check for drift against the templates.

## Procedure

1. **Copy semantics first**: read `common/templates/README.md` and `+wit/scripts/init-repo.{sh,bat}` — the copy order (domain folder first, then `common/templates/common/`, never overwrite) decides which twin wins. An intended override is not a collision; an undocumented one is.
2. **Pairwise overlap**: for files existing in both `common/` and a type folder (`README.md`, `AGENTS.md`), diff section by section. Record: identical blocks (maintenance hazard — edit in two places), divergent blocks that should be identical (drift), genuinely type-specific blocks (fine).
3. **Reference check**: every path/template name referenced in docs (`+team/README.md`, `common/templates/README.md`, `AGENTS.md` files) must resolve. List broken references.
4. **Normative duplication**: where a template restates normative text that also lives in `+wit/common/conventions/` (e.g. task format, requirement levels), the convention file is canonical — flag restatements that omit the reference or contradict it.
5. **Report**: table `#` | overlap/collision | locations | intended? (`yes/no/unclear`) | proposed canonical source | proposed merge/keep action | certainty. Deliberate replicas get a named upstream; unmanaged copies get a consolidation proposal.

## Rules

- Preserve unique content: "different" ≠ "duplicate". Type-specific variants that carry real differences are labelled *intentional*, not merged.
- Deleting or merging template content requires approval — the skill outputs proposals only.
- Check downstream: a template change does not propagate to existing repos (D03); note which consumer repos would need a manual sync.

## Completion criteria

Every file present in >1 template folder reviewed; every referenced path resolved or listed as broken; report filed in `+team/dominik/` with per-item proposed action; no template edited without approval.
