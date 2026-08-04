# Research — T-YYYY-MM-DD-NNN (gold-standard exemplar)

**Date:** YYYY-MM-DD
**Trigger:** initial
**Sub-agent:** research

> This file is a **synthetic exemplar** of the canonical 8-section research output. All task-specific details (task id, dates, libraries) are placeholders. No real `path:line` references to user files appear here — citations point at this file's own sections (e.g. `§Technical findings`) or at generic external docs. Use this as the gold-standard template when filling a real research note; see `agents_manager/research/SKILL.md` §What you must produce for the authoritative template.

## Task in one sentence

<restate the user's task in your own words — show you understood it>

**Example:** Add a CSV-export feature to the CLI so users can dump a report's rows to a file instead of the terminal. The user already approved the CSV format in chat; the deliverable is a new subcommand wired into the existing CLI dispatcher.

## What we know for sure

- <bullet of confirmed facts about the task, codebase, environment>
- Cite paths as `relative/path:line` so the planning agent can find them.
- One bullet per fact; do not merge multiple facts into a single bullet.

**Example bullets:**
- The CLI dispatcher lives at `src/cli/<name>.py` (entrypoint) and routes subcommands via a registry in `src/cli/registry.py`.
- The existing report-printer writes rows to `sys.stdout` via the `print_row(row)` helper, which accepts a `Row` dataclass and a `WriteTarget`.
- The user task captures the desired CSV columns as `id,name,created_at,status` (see user-task handoff, message-id `m-2026-07-04-002`).
- Python `csv.writer` is already in use in two unrelated scripts (not vendored — stdlib import).

## What we don't know (ambiguities)

- <bullet — each must be answerable by the user or by reading docs>
  - **Suggested clarifying question:** "<exact question to ask the user>"

**Example bullets:**
- Output filename: should it default to `<report-id>.csv` or be required as a positional arg?
  - **Suggested clarifying question:** "Default filename — auto-derived from the report id, or always explicit?"
- Encoding: UTF-8 with or without BOM? Excel on Windows prefers BOM; everything else prefers no BOM.
  - **Suggested clarifying question:** "CSV encoding — UTF-8 (no BOM, web-friendly) or UTF-8-with-BOM (Excel-friendly)?"
- Should `--output` overwrite an existing file silently or refuse with a non-zero exit?
  - **Suggested clarifying question:** "Overwrite policy — silent, refuse, or prompt?"

## Risks and doubts

- <bullet — things that could derail the task>
  - **Severity:** low | medium | high
  - **Mitigation:** <how to reduce or handle>

**Example bullets:**
- The existing `print_row(row)` helper does not have a `csv` mode — wiring a new writer alongside risks two parallel printers drifting apart.
  - **Severity:** medium
  - **Mitigation:** Refactor `print_row` to take a `Format` enum (`table | csv | json`) and dispatch internally; one source of truth for row formatting.
- The CLI's `--output` flag is parsed by an upstream argparse parser that silently coerces `~` to the home dir; a CSV path like `~/reports/x.csv` may bypass an overwrite-check that the team wants.
  - **Severity:** low
  - **Mitigation:** Document the path-expansion behavior in the subcommand's `--help` text; do not add a separate guard.

## Technical findings

- <bullet — concrete things discovered by reading code, docs, or running tools>
- Cite paths as `relative/path:line` so the planning agent can find them.

**Example bullets:**
- The CLI registry at `src/cli/registry.py` registers subcommands via a decorator; adding a new one is a 5-line change.
- The `Report` model at `src/models/report.py` exposes `report.rows` as a `Sequence[Row]`; the CSV writer can iterate this directly without buffering.
- The `Row` dataclass is frozen; CSV writer must materialize values via the existing `Row.to_dict()` helper to avoid mutating.

## Feasibility verdict

- **Can do:** yes | partial | no
- **Confidence:** HIGH | MEDIUM | LOW (v0.14.1 calibration)
- **Why:** <one short paragraph citing the confidence driver>

**Example:**
- **Can do:** yes
- **Confidence:** HIGH
- **Why:** The row-formatting refactor + CSV subcommand are both contained in `src/cli/` and `src/models/`. Stdlib `csv.writer` covers the encoding question; the existing dispatcher decorator handles registration. Three ambiguities remain (filename default, encoding, overwrite policy) but each is one-sentence-answerable by the user.

## Recommendations for the planning agent

- <bullet — concrete suggestions the planner should consider>
- Frame as suggestions, not decisions — `rules.md` rule 1 says you investigate, you do not decide.

**Example bullets:**
- Group the refactor (Phase A) and the new subcommand (Phase B) into one P3 dispatch so the coder's diff is reviewable as a unit; they touch the same files.
- Defer the `--output` overwrite-policy question to the user via the master preflight, not the research note — research should not block on it.
- The encoding question (UTF-8 vs UTF-8-BOM) is the highest-impact ambiguity; recommend master resolve it before Phase 3 starts.

## Open questions for the user

- <numbered list, ready to copy-paste to the user. If empty, write "None — proceed to planning.">

**Example:**
1. CSV filename — default to `<report-id>.csv` or always require a positional arg?
2. CSV encoding — UTF-8 (no BOM) or UTF-8-with-BOM?
3. `--output` overwrite policy — silent, refuse, or prompt?

If the user has already answered any of these in chat, drop the corresponding question here and note "answered by user at <message-id>" in the **What we know for sure** section.

## Self-critique

- **Did I do my job?** <yes/partial/no — what would have been better?>
- **What might I have missed?** <bullets — blind spots, sources not checked>
- **What did I assume without evidence?** <bullets — call out anything inferred>

**Example:**
- **Did I do my job?** Yes — surfaced three ambiguities that change the plan, two risks with severity, and a HIGH-confidence feasibility call backed by direct reads of the CLI registry and Row model.
- **What might I have missed?**
  - Did not check whether the project has a CHANGELOG convention that would require a `## Unreleased` entry for new CLI flags.
  - Did not read the test suite to confirm the existing dispatcher has a per-subcommand test harness the coder can extend.
- **What did I assume without evidence?**
  - Assumed Python `csv.writer` is acceptable for the encoding. Verified stdlib availability; did not check whether the team's lint rules forbid `csv` module imports (some style guides prefer `csv` re-exported via a project wrapper).
  - Assumed the user wants a separate subcommand rather than a `--format csv` flag on the existing report command. Both shapes are valid; the user's chat message was ambiguous on this.

---

last-verified: 2026-07-04