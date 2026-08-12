# CLAUDE.md — Book Kit

This repo is a **portable book-writing environment** powered by OpenCode and the agents-manager multi-agent pipeline. 7 specialist agents are defined in `opencode.jsonc` (master + research + planning + design + coder + review + assets). Walls are enforced by prose (every agent has `permission: "allow"`).

**Working in this repo:** when the user says "write a book" or any book-gen trigger, master loads `agents_manager/book-gen-orchestrator/SKILL.md` and drives the 7-phase pipeline (intake → skeleton → research → outline → style → writing-plan → per-chapter write → review). When the user passes the `--media` flag, master additionally loads `agents_manager/book2media-orchestrator/SKILL.md` and dispatches a Phase 9 lane to produce 5 media products per book per locale (audiobook M4B + horizontal video + trailer + reel × 3 platforms). For all other multi-step work, master dispatches the 5 specialists directly per the standard pipeline.

## Pipeline (book-gen shape)

```
master -> am-research -> am-planning -> am-design -> master (writing-plan) -> am-coder (per chapter, with book-writer skill) -> am-review (review passes)
                                       ^                                              ^
                                       |                                              |
                                       +-- bible.md append <------- ledger.md update -+
```

### Phase 9 (book2media) -- only with `--media` flag

```
master (--media) -> book2media-orchestrator -> am-assets (Phase 1 manifest gate) -> am-coder (Phases 2-4) -> am-review (locale gate)
                                                                                       |
                                                                                       v
                                                                            books/<slug>/exports/
                                                                            (audiobook-en.m4b, horizontal-en.mp4, trailer-en.mp4, reel-en-yt.mp4, reel-en-ig.mp4, reel-en-tiktok.mp4, ...)
```

- **master** orchestrates ONLY. Never codes, plans, designs, or reviews directly.
- **Specialists never spawn other specialists.** Only master orchestrates.
- All inter-agent communication goes through files in `share/`. No out-of-band chat.
- Book artifacts live in `books/<slug>/**` (not `share/`). `share/` is for inter-agent coordination.
- Per-book files: `intake.md`, `skeleton.md`, `research-log.md`, `outline.md`, `style-guide.md`, `writing-plan.md`, `bible.md`, `ledger.md`, `decisions-log.md`, `source-map.md` (translation-mode only), `frozen-lines.json`, `.translate-progress.json` (translation-mode only), `chapters/ch-XX.md`.
- Phase 9 additions: `media-locale-manifest.json` (per-book media config), `exports/*.m4b` + `exports/*.mp4` (assembled media), `figures/cover.png` + `figures/media-video-manifest.json` (assets + video manifest).

## Auto-routing

- **Book intent** ("write a book", "book about X", "draft a guide on Y") -> master loads `agents_manager/book-gen-orchestrator/SKILL.md`.
- **Media intent** ("produce audiobook", "make video", "reel", "media") + `--media` flag -> master additionally loads `agents_manager/book2media-orchestrator/SKILL.md` and dispatches at Phase 9 (after Phase 8 build_exports).
- **Multi-step code work** -> master dispatches specialists directly.
- **Single-step work** (quick edit, one-off question) -> do it directly. No master needed.

## User gates (book-gen pauses for confirmation)

- Phase 0 (intake fields — §10 translation-mode fields appear only when user signals translation intent) — every field needs explicit confirmation.
- Phase 3 (outline contradictions + dependency graph; refuses to advance without populated `source-map.md` when §10 `Is translation? = yes`) — last gate before writing.
- Phase 4 (style-guide confirmation) — gates voice adoption.
- Phase 5 (writing-plan) — gates dispatch order.

Phase 7 review = **Branch A** (translation-mode: 2-pass `book-reviewer` accuracy + consistency) OR **Branch B** (native: 3-pass dev → line → copy). **Copy-edit only when ALL chapters `approved`** — skipped on partial runs.

Phase 9 has no user gate; am-assets gate is the manifest schema, am-review gate is the locale-correctness check.

## Hard rules

- **Do NOT commit unless explicitly asked.** Project convention; commits are user-driven.
- **Do NOT skip the review phase** because "it looks fine."
- **Do NOT accept the first review report without reading it.**
- **max_fix_loops = 3.** Cap on review -> fix -> re-review cycles; surface to user after.
- **Do NOT edit `agents_manager/<role>/SKILL.md`** unless explicitly redesigning the kit.
- **Book Kit ships ONLY 7 agents.** No `am-investigate`, `am-ship`, `am-health` -- book-gen never dispatches them. `am-assets` is shipped as the media-manifest gatekeeper for book2media Phase 9 only; book-gen Phases 0-8 still do not dispatch it (amended 2026-08-11 for Phase 9).

## Per-agent output paths

| Agent | Primary output destination |
|---|---|
| master | `share/handoffs/`, `share/notes/99_progress_*.md`, `tasks/` |
| am-research | `books/<slug>/research-log.md` (in book mode) or `share/notes/01_research_*.md` |
| am-planning | `books/<slug>/skeleton.md`, `books/<slug>/outline.md`, `tasks/<id>.md` |
| am-design | `books/<slug>/style-guide.md` |
| am-coder | `books/<slug>/chapters/ch-NN.md` + `bible.md` (append) + `ledger.md` (row update); in Phase 9 also: `books/<slug>/chapters/ch-NN-{en,ar}.mp3` + `books/<slug>/chapters/ch-NN-{en,ar}.srt` + `books/<slug>/chapters/ch-NN-{en,ar}.ass` + `books/<slug>/exports/{audiobook,horizontal,trailer,reel-*}-{en,ar}.{m4b,mp4}` |
| am-review | `share/reports/04_book-review_*.md` (in book mode); in Phase 9 also: `share/reports/04_review_*.md` for each Phase 2-5 media leg |
| am-assets (Phase 9 only) | `books/<slug>/media-locale-manifest.json` (manifest validation + generation), `books/<slug>/figures/cover.png` (cover asset gate) |

## Task tracking

- ID format: `T-YYYY-MM-DD-NNN`. One file per id in `tasks/`.
- Book tasks: `T-YYYY-MM-DD-NNN-book-<slug>.md`.
- Media tasks: `T-YYYY-MM-DD-NNN-book2media-<slug>.md`.
- Phase log + sub-task rows live in `tasks/<id>.md`.

## Reading order for a new session

1. `CLAUDE.md` (this file) — top-level orientation.
2. `opencode.jsonc` — agent roster.
3. `agents_manager/book-gen-orchestrator/SKILL.md` if book intent suspected.
4. `agents_manager/book2media-orchestrator/SKILL.md` if `--media` flag set and book has reached Phase 8.
5. `agents_manager/<role>/SKILL.md` for any specialist you dispatch.
6. `share/notes/02_plan_*.md` + `tasks/<id>.md` — current in-flight work.
7. `books/<slug>/intake.md` — current book state.
8. `books/<slug>/media-locale-manifest.json` — current media config (if Phase 9 in flight).

## Publish-time strip

For external publication of any chapter, strip the `<!-- Self-critique -->` block at the bottom — it exists for the orchestrator/reviewer handoff only.

## Upgrading the kit

Re-run `python install.py --upgrade` against a newer ZIP. User-owned files (`books/**`, `tasks/**`, user-created `share/**`) are preserved; engine files are overwritten after warning. See `docs/UPGRADE.md` for the full policy.