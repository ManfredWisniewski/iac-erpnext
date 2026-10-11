---
name: intent
description: Produce or update the +intent/ documentation set (intent.md, decisions.md, tests.md) in a target repository from an approved implementation plan. Use when a plan is approved and a repo lacks or needs updated intent/decisions/acceptance criteria before implementation. Stage 3 of the WIT pipeline — research → plan → intent → implementation.
compatibility: Any WIT repository that carries `+intent/`. Templates live in `+wit/common/templates/common/+intent/`; format rules in `+wit/common/conventions/decisions.md` and `+wit/development/bestpractices/tests.md`.
metadata:
  scope: repository
  pipeline-stage: "3-intent"
  version: "0.1"
---

# Intent

Convert an approved plan into the repo's durable intent: `+intent/intent.md` (what/why/scope), `+intent/decisions.md` (numbered binding decisions), `+intent/tests.md` (A-numbered acceptance criteria). These files are what the `implementation` stage builds against — code follows intent, not the other way round.

## Inputs

- `plan` (required): approved plan document. If no plan exists, run `plan` first — never write intent from memory.
- `repo` (required): target repository receiving or updating `+intent/`.
- `decisions_input` (optional): results of the grilling rounds already held with the owner; otherwise generate the question list.

## Procedure

1. **Verify the plan is approved** (`Status:` field or owner confirmation). An unapproved plan yields a draft intent marked as such — nothing else.
2. **`intent.md`** — from `+wit/common/templates/common/+intent/intent.md`:
   - Purpose: what exists, who uses it, which problem it solves — taken from the plan, not re-invented.
   - Concepts: domain terms, defined once.
   - Scope: explicit in/out, including where out-of-scope concerns live instead.
   - Software projects: fill configuration, processing order, main workflows (input/output, matching, side effects, failure + retry behaviour), public functions, data/file formats, safety & preservation sections.
   - Non-goals and limitations: what the plan deliberately excludes.
   - Open items: point to `TASKS.md` and the `decisions.md` backlog — no invented answers.
3. **`decisions.md`** — per `+wit/common/conventions/decisions.md`:
   - `D01` records template initialisation (or the existing D-history is continued — **never renumber, never rewrite**; supersede with a new numbered decision or dated amendment).
   - One entry per settled decision: decision, alternatives considered, reason; grouped under topic headings; session date in the header.
   - Discussed-but-undecided ideas go to `## Backlog (not decided, parked)` — never silently dropped.
   - Unsettled questions: run grilling rounds (all questions with settled prerequisites, recommended answer each) until the owner resolves them.
4. **`tests.md`** — commands block (test/lint/build) plus `A01`, `A02`, … acceptance criteria: checkable, including negative cases for security-relevant paths; `## Not tested` states deliberate gaps.

## Rules

- Consistency over completeness: an unresolved decision is recorded as open, not papered over.
- If implementation later reveals the intent is wrong: amend `decisions.md` (dated) and update `intent.md`/`tests.md` **with or before** the code change — never code first.
- One authoritative home: content that belongs to `+wit`/`+wit` is referenced, not copied into `+intent/`.

## Completion criteria

`+intent/{intent,decisions,tests}.md` exist (or are updated), internally consistent with the approved plan; every open decision is listed in backlog or resolved by the owner; acceptance criteria are checkable.
