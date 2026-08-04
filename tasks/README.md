# Tasks Folder — Canonical Task Tracker

One markdown file per task id, e.g. `tasks/T-2026-06-28-001.md`. This file is the **single source of truth** for "what is in scope and where each task stands." The planning agent creates the rows. The coder and review agents update the same rows.

## Template

```markdown
# Task — T-YYYY-MM-DD-NNN

**Created:** YYYY-MM-DD HH:MM
**Title:** <short title>
**User task:** share/handoffs/00_user_task.md
**Plan:** share/notes/02_plan_high_<task-id>.md
**Phases:** share/notes/02_plan_phases_<task-id>.md

## Metrics
<!-- master stamps these; do not hand-edit -->

**Started:** YYYY-MM-DD HH:MM
**Closed:** —
**Phase timings:**
| Phase | Started | Ended | Duration | LOC written | WARNs |
|-------|---------|-------|----------|-------------|-------|
| 0 Ingest   | — | — | — | — | — |
| 1 Research | — | — | — | — | — |
| 2 Planning | — | — | — | — | — |
| 3 Build    | — | — | — | — | — |
| 4 Review   | — | — | — | — | — |
| 5 Next-steps (opt) | — | — | — | — | — |

**Loop counts:**
- Research re-entries: 0
- Planning re-entries: 0
- Fix-loops by phase: `{P1: 0, P2: 0, P3: 0, P4: 0, P5: 0, ...}`
- Fix-loops total: 0
- Fix-loops (review → coder): 0

**Files touched (deduplicated, from coder summaries):**
- (filled by master as coder reports come in)

## Task table

| ID | Phase | Task | Files expected | Status | Coder | Review |
|----|-------|------|----------------|--------|-------|--------|
| P1T1 | 1 | <imperative verb + object> | `path/to/file.ext` | todo | — | — |
| P1T2 | 1 | ... | ... | todo | — | — |
| P2T1 | 2 | ... | ... | todo | — | — |

## Status legend
- `todo` — not started
- `in_progress` — coder is on it
- `done` — coder finished AND review passed
- `warn` — coder finished, review has WARNs, not yet re-reviewed clean
- `fail` — coder finished, review FAILed, in fix loop
- `partial` — coder stopped mid-task
- `skipped` — explicitly deferred with reason

## Loop history
<!-- master appends one block per loop -->

### Loop 1 — YYYY-MM-DD HH:MM
- Phase: <1 | 2 | 3 | 4>
- Agent: <research | planning | coder | review>
- Artifact: <path>
- Outcome: <one-line>
- Next: <what happens next>

## Completion
<!-- master fills when all rows are done or accepted -->
**Closed:** YYYY-MM-DD
**Final commit / branch:** ...
**Last clean review:** share/reports/04_review_<task-id>_<phase>.md
**Open WARNs accepted by user:** <list or "none">

## Phase productivity (v0.7.0+)
<!-- Master fills at task close with a one-line summary per phase. -->
<!-- Sanity check, not a quality score. -->
| Phase | Wall-clock min | LOC | WARNs | LOC/WARN | Notes |
|-------|---------------|-----|-------|-----------|-------|
| 0 Ingest   | | | | | — |
| 1 Research | | | | | — |
| 2 Planning | | | | | — |
| 3 Build    | | | | | — |
| 4 Review   | | | | | — |
| 5 Next-steps (opt) | | | | | — |

**Cross-phase signal:** if any single phase trips `(LOC/WARN > 2× project median) OR (LOC > 1200 AND WARNs > 4)` without a documented split decision in `## Loop history`, the user should review whether the chunk-size protocol (v0.7.0+) is working.
```

## Optional flags (v0.6.0+)

These flags live in the task tracker header (on a `## Optional flags` block, set at Phase 0 Ingest by the master, after the `**Phase:**` line). Master sets them; sub-agents read-only:

- **`auto_accept_warns: bool`** (default `false`) — when `true`, master appends matches from the [triageable list](../agents_manager/SKILL.md#warn-auto-accept-triageable-list) to `share/notes/04_warns_register_<task-id>.md` with `[auto-accepted triageable]` tag, no user prompt.
- **`git_initialized: bool`** (default `false`) — set `true` when the user accepts the Phase 0 git-init prompt.
- **`phase_5_enabled: bool`** (default `false`) — when `true`, master enters Phase 5 at task close (auto-detects git vs non-git flavor).
- **`run_smoke_at_close: bool`** (default `true` when an API key was provided in Phase 0) — when `true`, master runs the project's `npm run smoke` (or equivalent) at Phase 4 review time.

## Design-task cross-reference (v0.9.0+)

When a design task is in scope, the master routes the design phase to `am-design` instead of (or in addition to) `am-research` + `am-planning`. Design artifacts land under `share/design/<task-id>/` with a tree-structured layout (see [`../share/README.md`](../share/README.md) for the full convention).

In the task table below, design tasks are tagged with a `[design]` prefix on the `Phase` column (e.g. `1.5 [design]`) and the `Files expected` column points at the design tree:

```
| ID        | Phase       | Task                                  | Files expected                                  |
|-----------|-------------|---------------------------------------|-------------------------------------------------|
| P1.5D-T1  | 1.5 [design]| Run 7-question discovery             | `share/design/<task-id>/00_brief.md`             |
| P1.5D-T2  | 1.5 [design]| Produce MOCK artifacts (mobile home)  | `share/design/<task-id>/04_mockups/mobile-home.html` |
| P1.5D-T3  | 1.5 [design]| Hand off to am-coder                  | `share/design/<task-id>/99_handoff.md`          |
```

The master reads `99_handoff.md` before dispatching `am-coder` — the handoff declares the next consumer and ships only the artifacts the coder needs.

## Rules for editing this file

- **Append-only on the `Loop history` and `## Metrics` sections.** Never delete a loop entry or a metric stamp.
- **The task table is updated in place.** Status flips, but the row itself stays.
- **One file per task id.** No cross-file references in the table.
- **No agent edits the `Completion` block except the master.**
- **Metrics are filled by the master only.** Sub-agents do not edit `## Metrics`; the master reads coder summaries and stamps the file.
- **Phase timings data is filled by the master at task close.** Sub-agents do not write `LOC written` or `WARNs` columns — master reads coder summaries + review reports + runs `find <scope> -name '*.ts*' -newer <phase_start_marker> | xargs wc -l` to count LOC. Mark `—` if data is unavailable.

## When to create a task file

The master creates this file at Phase 0, immediately after writing the user task capture. If the same logical task is reopened later, **append** to the existing file rather than creating a new one.

## Progress ledger (compaction safety)

The master maintains a separate append-only ledger per task at `share/notes/99_progress_<task-id>.md`. This is the master's recovery map when context is compacted mid-pipeline.

**Format** — one line per completed dispatch:

```
<phase> (<agent>) — <task-id> — <status-signal> (artifact: <path>; <one-line note>)
```

**Status signals:** DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED / <verdict-counts-for-review>.

**Example:**

```
Phase 0 (ingest)   — T-2026-06-28-001 — DONE (artifact: share/handoffs/00_user_task.md)
Phase 1 (research) — T-2026-06-28-001 — DONE (artifact: share/notes/01_research_T-2026-06-28-001.md)
Phase 2 (planning) — T-2026-06-28-001 — DONE (artifact: share/notes/02_plan_high_*.md; user-confirmed)
Phase 3 (coder P1) — T-2026-06-28-001 — DONE (artifact: share/notes/03_coder_summary_*.md)
Phase 4 (review P1) — T-2026-06-28-001 — 1 FAIL, 2 PASS (artifact: share/reports/04_review_*.md)
Phase 3 (coder P1 re-loop 1) — T-2026-06-28-001 — DONE (artifact: ...; fixed FAIL #1)
Phase 4 (review P1 re-loop 1) — T-2026-06-28-001 — 3 PASS, 0 FAIL (artifact: ...)
```

**Rules:**
- Append-only. Never delete entries.
- One line per dispatch. Keep it terse — the artifact is the truth, the ledger is the index.
- If the master session is compacted, recovery = read this file + `git log`, resume from the first phase not marked DONE.
- The ledger and the `## Loop history` block in this task file are related but distinct: the ledger is session-scope (master's memory); the loop history is task-scope (visible to all specialists).
