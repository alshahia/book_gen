# Glossary — agents_manager

**Last verified:** 2026-07-04

Domain terms used in the agents_manager controller and adjacent repos. Quick lookup for am-research when reading plan files, decisions, and review reports.

## Controller primitives

- **master** — the orchestrator agent. Owns dispatching + Phase gates + task tracker. Never codes, plans, designs, or reviews directly.
- **specialist** — one of the 6 worker agents: am-research, am-planning, am-design, am-coder, am-review, am-assets. Each has its own folder under `agents_manager/`.
- **soft wall** — lane boundary enforced by prose (v0.5.0+), not by OpenCode's permission layer. Every agent has `permission: "allow"`; discipline is what keeps agents out of each other's folders.
- **dispatch** — one master-to-specialist handoff. Has a task id, a prompt, and an expected output artifact.
- **dispatcher** — the script that installs agents-manager into a target project. Three dialects: `bin/agents-manager` (bash), `bin/agents-manager.ps1` (PowerShell), `bin/agents-manager.py` (Python, recommended).
- **task id** — `T-YYYY-MM-DD-NNN`. One per `tasks/<id>.md`. Drives the tracker + phase log + per-task review verdicts.
- **handoff** — a cross-agent note in `share/messages/<from>-to-<to>-*.md`. Ad-hoc clarification between dispatches.

## Plan + research primitives

- **preflight** — the 5-question gate master runs before dispatching a specialist. Origin: `agents_manager/SKILL.md` orchestration protocol.
- **feasibility verdict** — the agent's `yes | partial | no` call at the end of a research file. Calibrated in v0.14.1 with `confidence: HIGH | MEDIUM | LOW`.
- **severity** — `low | medium | high`. Required for every risk in a research note (master gate).
- **NEEDS_USER_INPUT** — boolean flag in the research return summary. True when clarifying questions remain.
- **HANDOFF-TO-{PLANNING,DESIGN,CODER,MASTER}** — v0.14.1 handoff tokens. Returned when a task is mis-shaped for am-research (e.g. it's actually a coding task).

## Memory + verification

- **scope** — `global | project | role`. Tag on every memory entry (`agents_manager/memory/README.md`).
- **episodic note** — per-task research note at `agents_manager/research/notes/episodic/<task-id>.md`. Continues context across re-entries on the same task.
- **semantic note** — curated cross-task insight at `agents_manager/research/notes/semantic/<topic>.md`. Survives across tasks.
- **last_verified** — frontmatter date; sweep triggers when > 90 days old (master-driven, flag-only — no auto-delete).
- **verification-before-completion (G1)** — gate that requires evidence (file:line, command output) before claiming done.

## Pipeline + phases

- **pipeline** — research → plan → build → review, plus optional Phase 5 (next-steps menu).
- **phase** — numbered stage (0 Ingest → 5 Next-steps) inside a single task.
- **fix loop** — review-fail → coder-fix → re-review cycle. Capped at 3 (`max_fix_loops = 3`).
- **WARN register** — `share/notes/04_warns_register_<task-id>.md`. Auto-acceptable WARNs queued here, NOT auto-deleted.

---

last-verified: 2026-07-04