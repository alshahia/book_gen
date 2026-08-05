# CLAUDE.md — Book Kit

This repo is a **portable book-writing environment** powered by OpenCode and the agents-manager multi-agent pipeline. 6 specialist agents are defined in `opencode.jsonc` (master + research + planning + design + coder + review). Walls are enforced by prose (every agent has `permission: "allow"`).

**Working in this repo:** when the user says "write a book" or any book-gen trigger, master loads `agents_manager/book-gen-orchestrator/SKILL.md` and drives the 7-phase pipeline (intake → skeleton → research → outline → style → writing-plan → per-chapter write → review). For all other multi-step work, master dispatches the 5 specialists directly per the standard pipeline.

## Pipeline (book-gen shape)

```
master -> am-research -> am-planning -> am-design -> master (writing-plan) -> am-coder (per chapter, with book-writer skill) -> am-review (review passes)
                                       ^                                              ^
                                       |                                              |
                                       +-- bible.md append <------- ledger.md update -+
```

- **master** orchestrates ONLY. Never codes, plans, designs, or reviews directly.
- **Specialists never spawn other specialists.** Only master orchestrates.
- All inter-agent communication goes through files in `share/`. No out-of-band chat.
- Book artifacts live in `books/<slug>/**` (not `share/`). `share/` is for inter-agent coordination.
- Per-book files: `intake.md`, `skeleton.md`, `research-log.md`, `outline.md`, `style-guide.md`, `writing-plan.md`, `bible.md`, `ledger.md`, `decisions-log.md`, `source-map.md` (translation-mode only), `frozen-lines.json`, `.translate-progress.json` (translation-mode only), `chapters/ch-XX.md`.

## Auto-routing

- **Book intent** ("write a book", "book about X", "draft a guide on Y") -> master loads `agents_manager/book-gen-orchestrator/SKILL.md`.
- **Multi-step code work** -> master dispatches specialists directly.
- **Single-step work** (quick edit, one-off question) -> do it directly. No master needed.

## User gates (book-gen pauses for confirmation)

- Phase 0 (intake fields — §10 translation-mode fields appear only when user signals translation intent) — every field needs explicit confirmation.
- Phase 3 (outline contradictions + dependency graph; refuses to advance without populated `source-map.md` when §10 `Is translation? = yes`) — last gate before writing.
- Phase 4 (style-guide confirmation) — gates voice adoption.
- Phase 5 (writing-plan) — gates dispatch order.

Phase 7 review = **Branch A** (translation-mode: 2-pass `book-reviewer` accuracy + consistency) OR **Branch B** (native: 3-pass dev → line → copy). **Copy-edit only when ALL chapters `approved`** — skipped on partial runs.

## Hard rules

- **Do NOT commit unless explicitly asked.** Project convention; commits are user-driven.
- **Do NOT skip the review phase** because "it looks fine."
- **Do NOT accept the first review report without reading it.**
- **max_fix_loops = 3.** Cap on review -> fix -> re-review cycles; surface to user after.
- **Do NOT edit `agents_manager/<role>/SKILL.md`** unless explicitly redesigning the kit.
- **Book Kit ships ONLY 6 agents.** No `am-assets`, `am-investigate`, `am-ship`, `am-health` — book-gen never dispatches them.

## Per-agent output paths

| Agent | Primary output destination |
|---|---|
| master | `share/handoffs/`, `share/notes/99_progress_*.md`, `tasks/` |
| am-research | `books/<slug>/research-log.md` (in book mode) or `share/notes/01_research_*.md` |
| am-planning | `books/<slug>/skeleton.md`, `books/<slug>/outline.md`, `tasks/<id>.md` |
| am-design | `books/<slug>/style-guide.md` |
| am-coder | `books/<slug>/chapters/ch-NN.md` + `bible.md` (append) + `ledger.md` (row update) |
| am-review | `share/reports/04_book-review_*.md` (in book mode) |

## Task tracking

- ID format: `T-YYYY-MM-DD-NNN`. One file per id in `tasks/`.
- Book tasks: `T-YYYY-MM-DD-NNN-book-<slug>.md`.
- Phase log + sub-task rows live in `tasks/<id>.md`.

## Reading order for a new session

1. `CLAUDE.md` (this file) — top-level orientation.
2. `opencode.jsonc` — agent roster.
3. `agents_manager/book-gen-orchestrator/SKILL.md` if book intent suspected.
4. `agents_manager/<role>/SKILL.md` for any specialist you dispatch.
5. `share/notes/02_plan_*.md` + `tasks/<id>.md` — current in-flight work.
6. `books/<slug>/intake.md` — current book state.

## Publish-time strip

For external publication of any chapter, strip the `<!-- Self-critique -->` block at the bottom — it exists for the orchestrator/reviewer handoff only.

## Upgrading the kit

Re-run `python install.py --upgrade` against a newer ZIP. User-owned files (`books/**`, `tasks/**`, user-created `share/**`) are preserved; engine files are overwritten after warning. See `docs/UPGRADE.md` for the full policy.