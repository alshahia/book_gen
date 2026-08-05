---
name: book-gen-orchestrator
description: Drive the 7-phase book-writing workflow (intake → skeleton → research → outline → style → writing-plan → per-chapter writing → 3-pass review) by routing work through existing agents_manager specialists in book-mode. Load when the user says "write a book", "book about X", "draft a novel", "help me write a guide on Y", or any phrase indicating they want to produce a long-form multi-chapter manuscript with agent help. Master invokes this skill; it then dispatches am-planning, am-research, am-design, am-coder (via book-writer), and am-review per phase.
allowed-tools: Read, Write (books/<slug>/**, share/notes/99_progress_<task-id>.md, share/handoffs/00_user_task_<task-id>.md, tasks/<id>.md), task (am-planning, am-research, am-design, am-coder, am-review), Bash (read-only)
triggers: write a book, book about, draft a book, novel, nonfiction book, help me write, I want to publish, book on, book gen, book generation, write me a book
preamble-tier: 3
version: 0.21.0
---

# Book-Gen Orchestrator

> **This is a skill, not a specialist.** There is no `opencode.jsonc` roster slot and no master dispatch route dedicated to book-gen. Master loads this file when the user's intent is "write a book" and drives the 7-phase pipeline by dispatching the existing 5 specialists in book-mode.

## Goal

Take a user from "I want to write a book about X" to one or more drafted, multi-pass-reviewed chapters — without inventing a new agent topology. Reuse `am-planning`, `am-research`, `am-design`, `am-coder`, `am-review` exactly as they exist. The only new surface area is:

1. **This skill** — phase routing + template-pointer logic.
2. **`book-writer` skill** (`agents_manager/book-writer/SKILL.md`) — prose-writing posture for `am-coder` when invoked from a book-gen dispatch.
3. **`books/<slug>/`** — per-book project directory at the repo root.
4. **Book-workflow templates** — already at `book_workflow/book-agents/templates/` (intake, skeleton, research-log, outline, style-guide, writing-plan, bible, ledger, decisions-log). Master and specialists read from there.

## Phase map (orchestration, not implementation)

| Phase | Output | Dispatched to | Template | User gate? |
|---|---|---|---|---|
| 0 — Intake | `books/<slug>/intake.md` | master (uses question tool) | `book_workflow/book-agents/templates/intake.md` | yes (each field) |
| 1 — Skeleton | `books/<slug>/skeleton.md` | `am-planning` | `book_workflow/book-agents/templates/skeleton.md` | no (scaffolding) |
| 2 — Research | `books/<slug>/research-log.md` | `am-research` (parallel per skeleton row) | `book_workflow/book-agents/templates/research-log.md` | only on material contradictions at Phase 3 |
| 3 — Outline | `books/<slug>/outline.md` | `am-planning` | `book_workflow/book-agents/templates/outline.md` | **yes** (last gate before writing) |
| 4 — Style/voice | `books/<slug>/style-guide.md` (+ `frozen-lines.json` at close) | `am-design` then master | `book_workflow/book-agents/templates/style-guide.md` | yes |
| 5 — Writing plan | `books/<slug>/writing-plan.md` | **master directly** (reads outline + dep tags) | `book_workflow/book-agents/templates/writing-plan.md` | yes |
| 6 — Writing | `books/<slug>/chapters/ch-NN.md` (+ bible + ledger update) | `am-coder` with `book-writer` skill loaded | — | only on chapter add/remove/reorder |
| 7 — Review (per chapter) | ledger status update | `am-review` (3 separate invocations: dev / line / copy — OR 2-pass `book-reviewer` for translation mode when `source-map.md` present) | — | only on review-fail escalation |

## Phase 0 — Intake (master does this itself)

Use the question tool. The intake has 15 fields per `book_workflow/book-agents/templates/intake.md`. Field-by-field:

1. **Title / working title** — free text (suggest one based on user's prompt if obvious)
2. **Core idea / goal** — free text
3. **Category** — infer best guess first, present 3 options: Fiction / Nonfiction / Hybrid (with one-line reasoning per option)
4. **Audience** — free text with example
5. **Tone/voice reference points** — examples after category known
6. **Target length** — present 3 concrete options: "50–100 pages / ~5 chapters", "5 chapters × ~25 pages", "300+ pages / ~15–20 chapters" — bias toward small unless asked otherwise
7. **Definition of done** — exit criteria for review loops
8. **Exception-handling preferences** — research thin/contradictory policy; unresponsive-at-checkpoint policy (proceed-and-flag vs hard-stop)
9. **Fiction-specific** (only if category is Fiction/Hybrid) — genre conventions research
10. **Translation mode** (only when user signals translation intent — "translate X to Arabic", "translate this PDF", etc.) — see §10 of intake template. When `Is translation? = yes`, master copies `source-map.md` template and runs `build_source_map.py` against `source/` before Phase 3.
11–15. **Operational caps / Tashkeel policy / Front matter / Back matter / Frozen line policy** — see intake template.

Every field needs explicit user confirmation. Do not mark intake `CONFIRMED` until every field is approved. Save the confirmed intake to `books/<slug>/intake.md` using the template at `book_workflow/book-agents/templates/intake.md`.

After intake is confirmed:
- Create `tasks/T-<date>-NNN-book-<slug>.md` with the canonical task-tracker schema (`tasks/README.md`).
- Write `share/handoffs/00_user_task_T-<date>-NNN.md` capturing the user's literal request.
- Start `share/notes/99_progress_T-<date>-NNN.md` (master's recovery ledger).
- **Translation-mode only:** copy `book_workflow/book-agents/templates/source-map.md` to `books/<slug>/source-map.md` and run `python3 book_workflow/scripts/build_source_map.py books/<slug>/` to scaffold it. Master re-runs the generator when `source/` updates and no `source-map.md` exists.

## Phase 1 — Skeleton (dispatch am-planning)

Dispatch `am-planning` with:
- task id + intake path + the skeleton template path
- instruction: read intake.md + skeleton template; produce `books/<slug>/skeleton.md` (chapter list + depends_on tags); do not produce full summaries yet
- boundary reminder: write ONLY to `books/<slug>/skeleton.md`; do NOT propose the full outline; do NOT write prose

Update `99_progress_<task-id>.md` with: `Phase 1 (skeleton) — DONE — artifact: books/<slug>/skeleton.md`.

## Phase 2 — Research (dispatch am-research in parallel)

If the skeleton has N chapters with `independent` tags, run `am-research` per chapter in **parallel** (all in one message). If chapters have `depends_on`, run sequentially.

Per chapter dispatch: am-research gets intake + the chapter's skeleton row + research-log template. Produces entries in `books/<slug>/research-log.md` (append per chapter, separated by `## chapter-0X` headers).

Each `am-research` prompt boundary: write ONLY to `books/<slug>/research-log.md` under the assigned chapter heading; do NOT propose an outline; flag material contradictions, do NOT resolve them; ≤1 direct quote per source.

When all chapter-research dispatches complete, update progress ledger.

## Phase 3 — Outline (dispatch am-planning)

Dispatch `am-planning` with: intake + skeleton + research-log + outline template. Produces `books/<slug>/outline.md`.

**Required user gate.** Present outline to user. If material contradictions surfaced in research, present them now. Do NOT advance past Phase 3 without explicit `CONFIRMED`.

Update progress ledger with confirmation status.

## Phase 4 — Style/voice (dispatch am-design)

Dispatch `am-design` with: intake (esp. tone/voice references) + outline + style-guide template. Produces `books/<slug>/style-guide.md` with two sections: **Presentation** and **Voice**.

For fiction/hybrid category: also cover POV + tense.

**Required user gate.** Present style guide to user. Update progress ledger.

## Phase 4 close — frozen-lines.json (master does this directly)

After the user confirms the style-guide, master generates the frozen-line manifest:

- Read `books/<slug>/style-guide.md` `## Frozen lines` section (per-chapter line refs).
- Compute SHA256 of each declared line (against the chapter file if it exists; sentinel hash if not).
- Write `books/<slug>/frozen-lines.json` per `book_workflow/book-agents/templates/frozen-lines.schema.json`.
- See `book_workflow/docs/frozen-lines-spec.md` for the full lifecycle (generation, enforcement, amendment protocol).

This is a HARD gate: `am-coder` cannot mark a chapter `drafted` without `book_check.py` exiting 0 against this manifest.

## Phase 5 — Writing plan (master does this directly)

Read `books/<slug>/outline.md` (depends_on tags). Produce `books/<slug>/writing-plan.md` per template:
- If user explicitly said linear or parallel in intake → use that.
- Otherwise: `independent` chapters → parallel-safe groups; chapters with `depends_on` → linear in dep order.
- One chapter at a time per writer invocation. Even parallel groups are dispatched one group at a time.
- Mode: `LINEAR | PARALLEL | MIXED` with explicit reasoning.

**Required user gate.** Present writing plan to user. Update progress ledger.

## Phase 6 — Writing (dispatch am-coder with book-writer skill)

For each chapter (or each independent parallel group):

1. Dispatch `am-coder` with a book-mode prompt. The prompt must include:
   - The chapter's outline entry
   - `books/<slug>/bible.md` (cumulative facts/voice/characters)
   - `books/<slug>/style-guide.md`
   - The chapter-specific entries from `books/<slug>/research-log.md` (only that chapter's, not the full log)
   - Instruction to load the `book-writer` skill (the prose-writing posture)
2. `am-coder` writes the chapter to `books/<slug>/chapters/ch-NN.md`.
3. `am-coder` appends new facts/details to `books/<slug>/bible.md` (append, never rewrite).
4. `am-coder` updates `books/<slug>/ledger.md` to mark the chapter `drafted`.

Boundary reminders for am-coder:
- write ONLY to `books/<slug>/chapters/`, `books/<slug>/bible.md`, `books/<slug>/ledger.md`
- do NOT write prose for any chapter not in your dispatch prompt
- do NOT mark a chapter `approved` — that's am-review's call
- do NOT invent facts not in the bible or research-log

## Phase 7 — Review (dispatch am-review)

### Branch A — Translation mode (intake §10 `Is translation? = yes` AND `source-map.md` present)

For each `drafted` chapter, load `agents_manager/book-reviewer/SKILL.md` and dispatch `am-review` **twice** (separate invocations — never combined):

1. **Pass 1 — Accuracy** — source H2 coverage, code-block SHA256 integrity (when `freeze_code = yes`), URL preservation, bolded-term preservation, word-count parity. Verdict against the per-chapter envelope in `source-map.md`. Update ledger to `accuracy-reviewed` (PASS) or dispatch fix (FAIL). Report: `share/reports/04_book-review_<task-id>_ch-<NN>_accuracy.md`.
2. **Pass 2 — Consistency** — glossary first-occurrence rule, terminology drift, untranslated-English scan, tashkeel ratio (when Arabic), heading-level + paragraph-length style consistency, cross-chapter glossary-drift accumulation. Update ledger to `consistency-reviewed`. Report: `share/reports/04_book-review_<task-id>_ch-<NN>_consistency.md`. Cross-chapter drift ledger: `share/reports/04_book-review_<task-id>_consistency-glossary-drift.md`.

When every chapter is `consistency-reviewed`, run a single whole-book copy-edit pass (same lens as Branch B step 3).

### Branch B — Native book-gen (default)

For each `drafted` chapter, run three **separate** am-review invocations (never combined):

1. **Developmental** — does the chapter serve its outline? contradictions vs. bible? (fiction) continuity/timeline/POV? Verdict against ledger exit criteria. Update ledger to `dev-reviewed` only after issues are resolved (dispatch a fix back to am-coder if needed).
2. **Line edit** — prose quality + voice consistency against style-guide. Respect the revision-pass cap from intake's "definition of done". Update ledger to `line-edited`.
3. **Copy edit** — single whole-book pass once **every** chapter is `approved`. Grammar, formatting, terminology consistency at book scale. Update ledger to `approved`.

### Dispatch selection (master applies at Phase 7 start)

- Read `books/<slug>/intake.md` §10 `Is translation?`. If `yes` AND `books/<slug>/source-map.md` exists → Branch A.
- Otherwise → Branch B.
- If `Is translation? = yes` but `source-map.md` is missing → refuse to advance; surface to user (this is the Phase 3 gate's job to catch, but Phase 7 re-checks).

Each pass writes its findings to `share/reports/04_book-review_<task-id>_ch-<NN>_<pass>.md`. Ledger is updated by master after each pass (master reads the review verdict, updates the row).

## State files (master-owned, all under `books/<slug>/`)

- `intake.md` — Phase 0 (master writes)
- `skeleton.md` — Phase 1 (am-planning)
- `research-log.md` — Phase 2 (am-research)
- `outline.md` — Phase 3 (am-planning)
- `style-guide.md` — Phase 4 (am-design)
- `writing-plan.md` — Phase 5 (master)
- `bible.md` — cumulative, append-only (am-coder appends after each chapter)
- `ledger.md` — one row per chapter (am-coder writes status, master updates after review)
- `decisions-log.md` — append-only (any agent can append; mostly master for phase changes)
- `chapters/ch-NN.md` — the prose itself (am-coder)
- `source-map.md` — Phase 0 (translation-mode only; master copies template + runs `build_source_map.py` generator when `source/` exists)
- `frozen-lines.json` — Phase 4 close (master writes; SHA256 manifest of style-guide frozen lines; enforced by `book_check.py`)
- `.translate-progress.json` — Phase 6 (translation-mode only; book-writer appends per-part per the chunked-write + resume protocol; schema in `book_workflow/book-agents/templates/.translate-progress.schema.json`)
- `exports/` — Phase 5b (master runs `book_workflow/scripts/build_exports.py`; toc + glossary + index + clean chapters + manifest)
- `reviews/ch-NN-<pass>.md` — review outputs (am-review; OR kept in `share/reports/` for agents_manager consistency)

## Boundaries (this skill, master enforces)

- Master CAN edit `books/<slug>/**` directly for state files (intake, ledger, writing-plan, decisions-log).
- Master CANNOT write chapter prose (`books/<slug>/chapters/*.md`) — that is always `am-coder`'s lane, even when the chapter is one paragraph long.
- Master CANNOT skip user-confirmation gates (intake field-by-field, outline, style-guide, writing-plan).
- Master CANNOT resolve material research contradictions — those surface to the user at Phase 3.
- Master MUST respect `max_fix_loops = 3` per chapter's review loop (same rule as the controller's build/review cycle).
- Master MUST NOT dispatch non-book-gen agents (no `am-assets` — books don't have a video asset pipeline; no `am-investigate` unless the user reports a bug).
- Master MUST close the task when the user says "done" or when every chapter is `approved` AND the copy-edit pass is clean.

## Relationship to the existing agents_manager pipeline

- `book-gen` runs **alongside** the controller's research→plan→build→review pipeline, not inside it. Do not invoke `am-planning`'s `02_plan_high_<id>.md` / `02_plan_phases_<id>.md` templates — book-gen uses its own templates at `book_workflow/book-agents/templates/`.
- Book-gen does NOT use the controller's `share/notes/01_research_<id>.md` / `02_plan_high_<id>.md` / `03_coder_summary_<id>_<phase>.md` naming. Book artifacts live in `books/<slug>/**`.
- Book-gen DOES use `share/notes/99_progress_<task-id>.md` for the master's recovery ledger (same file, same format).
- Book-gen DOES use `share/handoffs/00_user_task_<task-id>.md` to capture the user's literal request (same file, same format).
- Book-gen DOES use `share/reports/04_book-review_<task-id>_ch-<NN>_<pass>.md` for review outputs (suffixed to avoid collision with controller reviews of the same task id).

## Smoke-test entry point

If the user asks for a smoke test (no real book), default to a 3-chapter nonfiction title with a clearly bounded topic. Suggested defaults for the smoke test:

- Title: `Daily Focus` (working title — change freely)
- Category: Nonfiction (simplifies — no character/plot continuity)
- Audience: professionals new to productivity systems
- Length: 5 chapters × ~25 pages (the smallest option that still demonstrates the pipeline)
- Definition of done: "no unresolved developmental issues; max 2 line-edit passes per chapter"
- Exception policy: proceed-and-flag (default)
- Auto-fill intake, run all 7 phases, write only Chapter 1 (the others get stub chapters + ledger rows marked `skipped` for the smoke run).

After the smoke run, the user has a real `books/daily-focus/` skeleton + Chapter 1 prose + 2 review reports to inspect.
