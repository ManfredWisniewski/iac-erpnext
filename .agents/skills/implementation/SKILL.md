---
name: implementation
description: Implement code or content changes from a repository's +intent/ documentation. Use when intent.md, decisions.md and tests.md define the work and the task is to build it. Enforces the WIT gates — persona branch + worktree, lint/test before report, PR for human merge. Stage 4 of the WIT pipeline — research → plan → intent → implementation.
compatibility: Any WIT repository with `+intent/`. Requires own persona branch in own worktree (`+wit/common/conventions/git-worktrees.md`); must run parallel-safe (D02).
metadata:
  scope: repository
  pipeline-stage: "4-implementation"
  gate: human-merge
  version: "0.1"
---

# Implementation

Build what `+intent/` defines. If the intent does not cover the work, **stop** — the gap is an intent problem, not a licence to improvise; feed it back through `intent`/`plan`.

## Inputs

- `repo` (required): target repository.
- `scope` (required): which part of `+intent/` this run implements — reference the task in `TASKS.md` where one exists.
- `tests` (optional): which `A##` criteria this run must satisfy; default: all criteria touching the changed surface.

## Procedure

1. **Verify branch and worktree** (`git status --short --branch`, `git branch --show-current`): own persona branch, never `main`/`work`/`wip` (`repo-setup.md`). Init required submodules (`git submodule update --init`).
2. **Read before writing**: `README.md`, `AGENTS.md`, `+intent/{intent,decisions,tests}.md`, and the relevant `+wit/<domain>` conventions/best-practices. Decisions in `decisions.md` are binding.
3. **Implement the smallest increment** that satisfies the stated scope. Follow existing conventions over personal preference; match code style, naming, directory layout.
4. **Deviation protocol**: if reality contradicts `intent.md`/`decisions.md`, stop changing code, record a dated amendment or new D-number **first**, then implement against the amended intent. Silent deviation is the anti-pattern this pipeline exists to prevent.
5. **Verify**: run the commands block from `tests.md`/`AGENTS.md` (lint at minimum: `npx markdownlint-cli2 "**/*.md"` where configured). Check each relevant `A##` criterion; report what was run, what passed, what could not run and why.
6. **Close out**: update `TASKS.md` (done items get `✅ YYYY-MM-DD`), commit on the persona branch with a scoped conventional message, integrate to `wip` only if conflict-free (`git push . HEAD:wip`) — otherwise escalate. Merges to `work`/`main` are human-only.

## Rules

- Never commit secrets, customer data, conversation logs, runtime state; pseudonymise persons (`Person-XXXX`).
- External sends and production deploys: always human (D04). This skill never merges, never deploys.
- Parallel-safe: assume other agents work in the same repo concurrently — scoped commits, no broad refactors beyond the task.
- Failing tests are reported, not worked around; an `A##` that cannot pass is escalated with evidence.

## Completion criteria

Scope implemented, verification commands run and reported per criterion, deviations recorded in `decisions.md` before/with the change, `TASKS.md` updated, work committed on the persona branch and (conflict-free) integrated into `wip`; PR/merge left to humans.
