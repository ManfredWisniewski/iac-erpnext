---
name: research
description: Turn a task or open question into a durable, source-cited research brief. Use when a task starts with "research", when facts are missing before planning, or when a decision needs evidence. Produces `research/<subject>/YYYY-MM-DD-topic.md` following the +wit research-brief format. Stage 1 of the WIT pipeline — research → plan → intent → implementation.
compatibility: Any WIT repository. Briefs go to the owning `+wit` domain's `research/` (`development/`, `marketing/`, `business/`, `design/`) or to `+wit/common/research/` for cross-domain subjects; repo-local questions stay in the consuming repo. Requires network access for external sources; never put confidential material in queries.
metadata:
  scope: cross-repository
  pipeline-stage: "1-research"
  version: "0.1"
---

# Research

Produce a research brief a `plan` run can consume without re-doing lookups. **Facts are looked up, not guessed** (`+wit/AGENTS.md`, *Shared rules* section); everything unverifiable is labelled.

## Inputs

- `question` (required): the decision or unknown to resolve — from a `#task` line, a plan, or the owner.
- `scope` (optional): subjects, systems, repos to inspect. If absent, state assumed scope in the brief.
- `output` (optional): `+wit/<domain>/research/<subject>/` or `+wit/common/research/<subject>/` (default for reusable findings) or `<repo>/research/` for repo-local questions.
- `deadline/context` (optional): linked task or plan that consumes this.

## Procedure

1. **Frame**: write down the exact question, scope boundaries, and which decision or plan the answer feeds. If the question is ambiguous, list interpretations and pick the narrowest useful one — note the alternatives as limitations.
2. **Gather**: internal sources first (repo paths, `+intent/decisions.md`, existing briefs — cite path + revision), then external sources (cite URL + access date). Do not send confidential material in external queries.
3. **Label**: every finding is `certain` (verified against source) / `likely` (corroborated but unverified) / `guess` (inference). Distinguish "the document says X" from "X is true".
4. **Write** the brief in the +wit research-brief format (`+wit/common/research/README.md`):
   - header: date, author persona, status, question/scope, coverage claim;
   - executive summary;
   - findings — each with certainty label, source, access date;
   - implications for the consuming decision/plan;
   - limitations (what was *not* inspected);
   - next steps.
   Filename: `YYYY-MM-DD-<topic>.md` in a subject subdirectory (create `research/<subject>/` if needed).
5. **Close out**: link the brief from the triggering task/plan. Research contains no decisions — derived decisions belong in the consuming repo's `+intent/decisions.md`.

## Rules

- Contradictory sources: show both claims + provenance; do not silently pick one.
- Briefs may be removed when a different route is selected — before deleting a brief, add a summary entry (350 words or less, question + key findings + outcome) to the folder's `history.md` so the reasons stay documented.
- Coverage claims must match what was actually inspected — no "exhaustive" without evidence.
- No credentials, customer data, conversation logs or runtime state in the brief (`AGENTS.md`).
- Pseudonymise real persons (`Person-XXXX`).

## Completion criteria

Brief committed at the right location, follows the format, every finding labelled and sourced, coverage/limits stated, consuming task updated to reference it.
