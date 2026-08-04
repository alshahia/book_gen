# Prior Decisions — agents_manager

**Last verified:** 2026-07-04

Pointer + index to the decision logs that bound current behavior. When a research note or plan proposes a change, check here first for the lock-in rationale.

## Where decisions live

| Path | Author | Scope | Lifetime |
|------|--------|-------|----------|
| `agents_manager/CHANGELOG.md` | master | per-version (v0.1.0 → current) | permanent (append-only) |
| `share/notes/99_decisions.md` | master | per-task locked decisions | per-task (closure) |
| `share/handoffs/00_user_task_<task-id>.md` "Decisions" block | master | per-task Phase-0 defaults | per-task |
| `agents_manager/research/notes/semantic/*.md` "Source" block | am-research | cross-task research insights | durable until superseded |
| `templates/<name>/memory/*.md` | template author | template playbook | template-version-bound |

## Read order on re-entry

1. `agents_manager/CHANGELOG.md` latest entry first — gives the current contract.
2. `share/notes/99_decisions.md` (if present) — most recent locked decisions for the active task.
3. The active task's user-task capture "Decisions" block — Phase-0 defaults master picked when ambiguities were unresolved.

## Why this matters for research

A "new" finding may already be locked. Always grep `share/notes/99_decisions.md` and the latest CHANGELOG entry before recommending a change. If a decision contradicts your finding, your job is to surface the conflict in the **What we don't know** section (with a clarifying question) — NOT to silently override.

## Index of locked decisions relevant to am-research

- **v0.14.0 (T-2026-07-04-001)** — master promotes to v0.14.0. Adds task tracker schema refinements; no specialist behavior change. Source: `agents_manager/CHANGELOG.md` (latest entry).
- **v0.13.0 (earlier)** — three-scope memory system ships. Frontmatter schema enforced at `agents_manager/memory/README.md`. Source: `agents_manager/memory/README.md` L31-46.
- **v0.11.0 (earlier)** — `--global/--local/--both/--skip` flags on `skills add`. Default scope = `both`. Source: dispatcher code in `bin/agents-manager*`.
- **v0.9.0 (earlier)** — `am-design` never writes `src/**`; reference implementations are `am-coder`'s job. Source: `AGENTS.md` Hard rules.

## Decision hygiene

- Decisions are append-only. To reverse: write a NEW decision entry that supersedes; never edit the old one.
- `superseded_by:` frontmatter field is the formal link (memory entries only; decisions use the CHANGELOG entry chain).
- A research note that contradicts a locked decision must flag it explicitly — see `rules.md` rule 2 (honesty).

---

last-verified: 2026-07-04