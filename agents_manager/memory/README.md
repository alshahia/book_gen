---
title: Memory System
description: Three-scope memory schema (global / projects/<slug> / per-role semantic+episodic), entry lifecycle, and read/write protocol for agents-manager.
scope: canonical-schema
status: active
created: 2026-07-03
last_verified: 2026-07-03
---

# Memory System

> **Canonical source of truth.** This file defines the schema, lifecycle, and read/write protocol for the three-scope memory system. Per-role `notes/README.md` files are 2-line pointers to this file; do not duplicate schema content there.

## Overview

The agents_manager memory system has three scopes: `agents_manager/memory/global/` (cross-project facts, master-written), `agents_manager/memory/projects/<slug>/` (per-project knowledge, master-written), and `agents_manager/<role>/notes/{semantic,episodic}/` (per-role expertise, specialist-written). This README is the SINGLE source of truth for the schema and protocol — every per-role README links here.

## Three scopes

| Scope | Folder | Owner | When to read |
|-------|--------|-------|--------------|
| Global | `agents_manager/memory/global/` | master | Cross-project facts; first source on re-entry. |
| Project | `agents_manager/memory/projects/<slug>/` | master | Per-project knowledge; second source on re-entry. `<slug>` defaults to `basename $PWD`; override via `agents_manager/.active-project`. |
| Role | `agents_manager/<role>/notes/{semantic,episodic}/` | the specialist themselves | Per-role expertise; third source on re-entry. `episodic/<task-id>.md` for continuity on the same task; `semantic/` for curated insights. |

Read order on re-entry: **global → project → role** (highest-leverage first).

## File schema

Every memory entry is one `.md` file with frontmatter + body. One canonical template, three scopes:

```markdown
---
scope: global
topic: <short noun phrase>
status: active
superseded_by:
created: YYYY-MM-DD
last_verified: YYYY-MM-DD
---

## TL;DR

<one sentence>

## Context

<what prompted this entry>

## Insight

<the durable takeaway>

## Source

<where the insight came from — coder summary path, commit SHA, doc path>

## Verification

<how a future agent can re-verify — file path + line number>
```

Required frontmatter keys: `scope` (`global` | `project` | `role`), `topic`, `status` (`active` | `superseded`), `created`, `last_verified`. `tech_stack:` and `domain:` are **soft-required** (comma-separated; required on entries produced by `agents_manager/extract/SKILL.md`, optional on hand-written entries — used by the read-side soft filter below to prefer entries whose tags match the current task). `superseded_by:` is required only when `status: superseded`.

## Lifecycle

Memory is **append-only** by design. To supersede an entry: leave the original in place with `status: superseded` and add `superseded_by: <path-to-new-entry>`. Do not delete; do not edit the body of a superseded entry (only the frontmatter status flip).

Master sweeps at task close (Phase 5 when `phase_5_enabled: true`, otherwise Phase 4 close as part of `## Completion`) for entries with `last_verified` older than 90 days. Sweep is a flag-and-review mechanic — entries are flagged in `share/notes/04_warns_register_<task-id>.md`, NOT auto-deleted.

Update `last_verified` when an entry is cross-checked against its `Verification` source and still holds.

## Read-on-entry protocol

Each specialist reads on re-entry, in order:

1. `agents_manager/memory/global/*.md` — ≤200 lines total; read newest-first.
2. `agents_manager/memory/projects/<active-slug>/*.md` — ≤200 lines; same order.
3. `agents_manager/<this-role>/notes/semantic/*.md` — ≤200 lines; curated insights.
4. `agents_manager/<this-role>/notes/episodic/<task-id>.md` — past notes on the same task; skim for continuity.
5. **Optional soft filter (v0.15.0+):** if your current task declares `tech_stack:` or `domain:` tags, prefer memory entries whose own `tech_stack:` / `domain:` frontmatter matches. Specialist judgment, NOT a hard gate — unfiltered reading is still correct.

Master has a third source: `share/notes/99_progress_<task-id>.md` (existing progress-ledger convention), same 200-line cap.

**If a scope exceeds 200 lines**, grep by `topic:` keyword for the current task's keyword first, then read up to 200 lines of matches. Do not bulk-read oversized scopes.

## Write-on-exit protocol

Every specialist return summary gains exactly one of these two dispatch-contract lines:

- `Memory written: <path-to-entry.md>` — when a new entry was written.
- `No memory write: <reason>` — when no entry was written. Common reasons: `trivial` (status-check dispatch that didn't hit a `tasks/<id>.md` row), `durable-insight test failed` (the 3-question test below returned a `don't write`).

Master only GATES on the line being present for **substantive** dispatches (those that hit `tasks/<id>.md` rows). Trivial status checks can use `No memory write: trivial`.

## Durable-insight criteria

Write only if ALL of these hold:

- (a) **Would a different agent (or me, in 3 months) benefit from knowing this on re-entry?** (Yes → write.)
- (b) **Is it derivable from `share/notes/03_coder_summary_*.md` or source code?** (Yes → don't write; cite the source in your return summary instead.)
- (c) **Did I spend >30 seconds figuring it out, or did it contradict my prior expectation?** (Yes to either → write.)

Combined: write only if (a) AND (NOT b) AND (c).

## Size cap

≤20 lines per entry (including frontmatter and body). Why: keeps the per-scope 200-line read budget stable (each entry is one unit of cost), prevents bloat, and forces concision — a 20-line cap is a forcing function for "is this really the durable insight?"

## Secrets-free rule

Memory entries must NEVER name, quote, or reference a `share/notes/02_secrets_<task-id>.md` path or value. Reference the task id (`T-YYYY-MM-DD-NNN`) instead. Same rule as CHANGELOG entries (per locked design #13).

Rationale: memory persists across sessions and clones; a leaked secret path becomes a permanent foothold.

## No-write-into-templates

Do NOT write into `templates/<name>/memory/`. That's the template author's lane (see `agents_manager/assets/SKILL.md`). The agents_manager memory tree at `agents_manager/memory/` is for controller-internal specialist knowledge; the `templates/<name>/memory/` tree is for runtime-task playbook content shipped with each template. They are distinct and the memory scaffold explicitly fences `templates/<name>/memory/`.

## Cross-project scoping

When reading project-scope entries, grep by `scope: project` + active project slug before applying. Ignore semantic entries referencing a different project. Rationale: `scope: project` entries are bound to one project; cross-applying is a contamination risk (locked design R6).

For global-scope entries, no slug filter applies — global is intentionally cross-project.

## Validator

`scripts/validate-memory.sh` (ships in chunk 3 / P3.3) lints every `.md` under `agents_manager/memory/{global,projects}/` and `agents_manager/<role>/notes/{semantic,episodic}/`. Checks: frontmatter `--- ... ---` block closes; required keys (`scope`, `topic`, `status`, `created`, `last_verified`) present; `scope ∈ {global, project, role}`; `status ∈ {active, superseded}`; `created` and `last_verified` parse as YYYY-MM-DD; when `status: superseded`, `superseded_by:` resolves to an existing file.

Exit codes: `0` = no issues; `1` = at least one issue. Run after every write batch.

## Active project slug

Detection order:

1. If `agents_manager/.active-project` exists, parse its YAML frontmatter and use the `slug:` field.
2. Otherwise, default = `basename $PWD`.

YAML format for `.active-project`:

```yaml
---
slug: context_gen
aliases: [agents-manager, controller]
description: The agents_manager multi-agent orchestration controller
---
```

`slug:` is required and must match `^[a-z0-9_-]+$`. `aliases:` and `description:` are optional. The file itself is gitignored via the per-folder `agents_manager/.gitignore` (root `.gitignore` is in the v0.12.x fence zone and is not modified).

Operators only create the file when they need a non-default slug; the default works for the common case.

## See also

- `agents_manager/research/notes/README.md` — am-research per-role pointer (chunk 2).
- `agents_manager/planning/notes/README.md` — am-planning per-role pointer (chunk 2).
- `agents_manager/coder/notes/README.md` — am-coder per-role pointer (chunk 2).
- `agents_manager/review/notes/README.md` — am-review per-role pointer (chunk 2).
- `agents_manager/assets/notes/README.md` — am-assets per-role pointer + `branch-decisions.md` note (chunk 2).