---
name: tasks-prioritize
description: Re-orders open tasks in `+team/+tasks/` by priority, highest first, under consideration of the repository's `priorities.md`. Use when task files need ranking, when priorities change, or when the task backlog needs re-sequencing. No tag or metadata changes — ordering only.
metadata:
  version: "1.0.0"
---

# Tasks — Prioritize

## GOAL

Re-order all open tasks in `+team/+tasks/` so that each file lists tasks from highest priority at the top to lowest at the bottom, guided by the repository's `priorities.md`.

## TASK

Read `priorities.md` (repo root; stop and escalate if absent), collect every open task from `+team/+tasks/*.md` (`<persona>.md` and `backlog.md`, ignoring `*.history.md` and `README.md`), rank them against the priorities, and rewrite each file's `## Open` section in the new order.

## Steps

1. Read `priorities.md` — extract each active P-entry's *Looking for*, *Constraints*, *Horizon* and *Status*. Numbered order in the file is the rank order of the priorities themselves (P1 before P2).
2. Collect all open (`- [ ] #task`) lines from every file in `+team/+tasks/`, excluding `*.history.md`, `README.md` and the `## Done` section. Keep each task's full line (tags, dates, signifiers) and its sub-bullets attached.
3. Score each task against the priorities:
   - direct contribution to P1/P2 *Looking for* statements ranks highest;
   - a task serving an earlier P-entry beats one serving a later entry;
   - tasks serving no P-entry rank below all contributing tasks, ordered by effort (quick wins before large efforts);
   - existing due dates (📅) and blocks (⛔) act as tiebreakers — earlier due date first, blockers before blocked.
4. Rewrite each file's `## Open` section with tasks in the computed order — move whole task blocks (line + sub-bullets), change nothing else.
5. **Verify:** diff every edited file — the set of task lines must be identical before and after; no task dropped, duplicated, reworded or re-tagged.

## DONE WHEN

- Every task file's `## Open` section runs highest-to-lowest priority.
- Task content is byte-identical apart from order — the diff shows only moved blocks.
- `backlog.md` ordering follows the same ranking (unassigned, but comparable).
- Files the agent must not edit stay untouched — see RULES.

## RULES

- Prioritization means **re-ordering only**: no tags, no signifiers, no dates added, removed or changed.
- Never touch `*.history.md`, `README.md` or the `## Done` section.
- Respect task-file ownership (`+wit/common/conventions/tasks.md`): an agent reorders only its own persona file unless the owner explicitly assigned a repo-wide prioritization run.
- Keep sub-bullets attached to their task line when moving.
- Equal-ranked tasks keep their previous relative order (stable sort).
- If `priorities.md` is missing, empty or has no active entries, stop and report instead of guessing.

## REPORT

- Files reordered (list) and files skipped (with reason).
- Top 3 tasks per file after ranking, with the P-entry each serves.
- Tasks that matched no P-entry (bottom of each list) — flag count.
- Any conflicts: due date vs. priority rank, blocked tasks ranked above blockers.
