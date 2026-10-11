---
name: plan
description: Develop an implementation plan from completed research. Use when a research brief exists and a task needs architecture, ownership, phases and open owner questions before any code or intent.md. Produces a versioned plan document (reference format: +wit/development/plans/payload/). Stage 2 of the WIT pipeline — research → plan → intent → implementation.
compatibility: Any WIT repository. Requires the research input to exist first — if it does not, run the `research` skill instead of guessing.
metadata:
  scope: cross-repository
  pipeline-stage: "2-plan"
  version: "0.1"
---

# Plan

Turn research into a reviewable implementation plan. A plan is a **proposal**: decisions are made by humans via grilling rounds (`+wit/common/conventions/decisions.md`), never silently by the agent.

## Inputs

- `research` (required): path(s) to the research brief(s) the plan builds on.
- `goal` (required): what should exist after implementation — from the `#task` or owner instruction.
- `constraints` (optional): budget, deadlines, existing systems that must be respected (check `+intent/decisions.md` of affected repos first — decisions are binding).
- `output` (optional): `+wit/<domain>/plans/<topic>/YYYY-MM-DD_plan-<topic>.md` for cross-repo plans; `<repo>/plans/` or the task's stated location otherwise.

## Procedure

1. **Read inputs fully**: the research brief(s), affected repos' `+intent/` (decisions are binding — deviate only via amendment), and the current state of what will change.
2. **Structure the plan** (reference: `+wit/development/plans/payload/2026-09-29_plan-payload-website.md`):
   - header: date, author persona, status (`proposal`, versioned on owner feedback);
   - `Input:` line listing research + inspected sources;
   - **Architecture**: one diagram (```text block) showing components, data flow, and where automation/humans sit;
   - **Ownership/SSOT table**: which repo/system owns which concern — one authoritative home per concern, no unmanaged copies;
   - numbered sections answering the concrete questions (Q1, Q2, …) an implementer or the owner would ask — connections, auth, sequencing, data flow;
   - **phases**: smallest useful order of work with dependencies;
   - **rollback/drift**: what to revert, known divergence from current state;
   - **open questions**: every unresolved decision listed explicitly, each with a recommended answer.
3. **Grill, don't guess** (decisions.md convention): facts are looked up by the agent; *decisions* are asked of the human in rounds — every question whose prerequisites are settled, with a recommended answer per question. Iterate the plan until no open question remains.
4. **Status**: keep `Status: proposal` until the owner approves. A plan never authorises implementation by itself.

## Rules

- One owner per concern — if the plan creates a second source of truth, redesign it (or flag as deliberate replica with named upstream + refresh).
- Preserve existing information: plan for migration, not overwrite.
- External sends, production changes, deletions: explicitly marked as human-gated (D03/D04).
- No invented cost/effort numbers; label estimates `guess`.

## Completion criteria

Plan committed at the right location, every owner question answered or listed as open with a recommendation, affected `+intent/decisions.md` constraints checked, status `proposal` pending human approval.
