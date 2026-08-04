# Writing Plan — Daily Focus: A practical guide to building a personal productivity system

Mode: **LINEAR** (sequential, one chapter at a time)

Reasoning: skeleton declares a strict cumulative dependency chain — every chapter after ch-01 depends on every prior chapter. Reversing any edge would force the writer to reference a chapter's concrete move (morning routine, deep-work block, shutdown review, weekly cadence) before that move has been installed. Phase 3 outline preserved this graph. The intake did not explicitly specify linear or parallel; the dependency graph decides LINEAR.

Smoke-test scope: per `intake.md` exception-handling + user-confirmed scope (T-2026-07-30-001 question 4), only **ch-01** is fully written + reviewed end-to-end. ch-02–ch-05 are stubbed with `skipped` ledger status to demonstrate the per-chapter dispatch contract without burning the full budget on the smoke run. Copy-edit pass (whole-book) is skipped — its review surface requires every chapter at `approved` and the smoke run leaves ch-02–05 unbuilt.

---

## Execution order

### Phase 6 — Writing (1 fully written + 4 stubbed)

1. **ch-01 — Shape the Day Before It Starts** — fully written by `am-coder` in `book-writer` mode
2. **ch-02 — Protect One Deep-Work Block** — stub file noting "skipped — see ledger"
3. **ch-03 — Close the Day Cleanly** — stub file noting "skipped — see ledger"
4. **ch-04 — Run the System by the Week** — stub file noting "skipped — see ledger"
5. **ch-05 — Repair the System After a Bad Week** — stub file noting "skipped — see ledger"

One chapter dispatched at a time. Each writer dispatch receives only: the chapter's outline entry + `bible.md` (current state) + `style-guide.md` + the `research-log.md` entries tagged `used_in: ch-NN` for this chapter + the prior chapter's prose if any (for ch-01: nothing; for ch-02–05: stubs in the smoke run, but in a full run each writer would see all prior `approved` chapters).

### Phase 7 — Review (dev + line for ch-01 only; copy-edit skipped)

1. **Pass 1 — Developmental review** of ch-01 — `am-review`. Verifies: chapter serves its outline entry + book goal (per `intake.md`); doesn't contradict `bible.md`; doesn't break continuity (n/a — nonfiction); has nothing missing that the outline promised. Updates ledger row ch-01 from `drafted` → `dev-reviewed`.
2. **Pass 2 — Line edit** of ch-01 — `am-review`, separate invocation. Verifies: prose quality + voice consistency against `style-guide.md`. Updates ledger row ch-01 from `dev-reviewed` → `line-edited` → `approved` (single transition since pass 3 is per-chapter cumulative at the agent's discretion; copy-edit is the whole-book pass).
3. **Pass 3 — Copy edit (whole-book)** — **SKIPPED** for smoke run; would normally run after every chapter is `approved`. Per `intake.md` exception policy, do not run partial-manuscript copy edits.

---

## Per-chapter dispatch reference

| Chapter | Outline entry | Research entries (used_in) | Ledger status (start) | Dispatch target |
|---|---|---|---|---|
| ch-01 | `outline.md#ch-01` | entry-001, 002, 003, 006, 008, 012, 014 (and 1–2 cross-refs) | `planned` | am-coder (book-writer mode) |
| ch-02 | `outline.md#ch-02` | entry-004, 005, 007, 010, 011 | `skipped` | master (stub file) |
| ch-03 | `outline.md#ch-03` | entry-013, 015, 017, 019 | `skipped` | master (stub file) |
| ch-04 | `outline.md#ch-04` | entry-009, 016, 018, 020, 022 | `skipped` | master (stub file) |
| ch-05 | `outline.md#ch-05` | entry-021, 023, 024, 025, 026 | `skipped` | master (stub file) |

(Research-entry IDs are illustrative; final per-chapter used_in tags are in `research-log.md` after Phase 2 consolidation.)

---

## Sequential gate enforcement

Per `book-gen-orchestrator` SKILL + master protocol:
- A chapter still `drafted` (not yet `approved`) in the ledger can be freely revised by its writer within approved scope, without a user checkpoint.
- A chapter already `approved` that needs removal/reordering → requires a user checkpoint.
- **Adding** a new chapter at any point → always requires a user checkpoint.
- The smoke run ends with ch-01 in `approved` status + ch-02–05 in `skipped` status. A follow-up run for the full book would resume from ch-02 without re-running Phases 0–5 unless the user wants outline/style revisions.

---

Confirmation: user is informed at the close of each phase dispatch; this plan does not introduce a separate user gate (Phase 5 has no required checkpoint in the book-workflow spec — only Phases 0, 3, and 4 do).
