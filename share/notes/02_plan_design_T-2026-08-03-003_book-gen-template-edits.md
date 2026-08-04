# Design Summary — T-2026-08-03-003 — Book-gen template edits

## File table

| T-number | Staged file path | Destination filename |
|---|---|---|
| T12 | `share/design/T-2026-08-03-003/06_copy/templates/intake.edited.md` | `book_workflow/book-agents/templates/intake.md` |
| T13 | `share/design/T-2026-08-03-003/06_copy/templates/bible.edited.md` | `book_workflow/book-agents/templates/bible.md` |
| T14 | `share/design/T-2026-08-03-003/06_copy/templates/ledger.edited.md` | `book_workflow/book-agents/templates/ledger.md` |
| T15 | `share/design/T-2026-08-03-003/06_copy/templates/style-guide.edited.md` | `book_workflow/book-agents/templates/style-guide.md` |
| T16 | `share/design/T-2026-08-03-003/06_copy/templates/writing-plan.edited.md` | `book_workflow/book-agents/templates/writing-plan.md` |
| T17 | `share/design/T-2026-08-03-003/06_copy/templates/decisions-log.edited.md` | `book_workflow/book-agents/templates/decisions-log.md` |

## Per-file summary

- **T12 / intake.md:** adds linked operational caps and tashkeel policy fields, front/back matter checklists, and a free-text frozen-line policy; records Phase 0 user confirmation and Phase 3 orchestrator detection.
- **T13 / bible.md:** retains and marks `## Terminology` and `## Characters` as required, adds `## Updated through ch-NN`, and records T4/T1 consumption contracts.
- **T14 / ledger.md:** extends the chapter table with `T1-exit`, `T3-exit`, `frozen-intact`, and `tashkeel-ratio`; adds an append-only gate log with the requested line format.
- **T15 / style-guide.md:** adds the optional-enforcement word-count table, comment-tolerant forbidden-regex fence, frozen-line WHY list, and T1/T4 gate contract.
- **T16 / writing-plan.md:** adds per-beat T1 exit requirements and a six-step frozen-line amendment protocol with master/user checkpoint ownership.
- **T17 / decisions-log.md:** adds eight phase-boundary rows from `0→1` through `7→ship`, with T1/T3/T4 exit-code status and user sign-off.

## Cross-reference table

| Section added | Template | Consumer / enforcement | Phase |
|---|---|---|---|
| Operational caps | `intake.md` | Orchestrator detects completion; `operational-caps.md` is the runtime caps source | Phase 0 / Phase 3 gate |
| Tashkeel policy link | `intake.md` | Orchestrator confirms policy selection; `book_check.py` reads `tashkeel-policy.md` | Phase 3 / Phase 6 |
| Front/back matter required | `intake.md` | Orchestrator validates required artifact selection | Phase 3 gate |
| Frozen line policy | `intake.md` | Orchestrator seeds `style-guide.md` / `frozen-lines.json` decisions | Phase 0 / Phase 3 |
| `## Updated through ch-NN` | `bible.md` | `book_check.py` intended staleness warning | Phase 6 |
| `## Terminology` | `bible.md` | `build_exports.py` glossary projection | Phase 5 |
| `## Characters` | `bible.md` | `build_exports.py` index projection | Phase 5 |
| T1/T3 result columns | `ledger.md` | Orchestrator records `book_check.py` and `strip_publish_annotations.py` results | Phase 6 / export |
| Mechanical gate log | `ledger.md` | Orchestrator appends gate entries | Per chapter gate |
| `## Word-count windows` | `style-guide.md` | `book_check.py` | Phase 6 |
| `## Forbidden patterns` | `style-guide.md` | `book_check.py` outside fenced code content | Phase 6 |
| `## Frozen lines` | `style-guide.md` | `book_check.py` plus `frozen-lines.json` | Phase 6 |
| Mechanical gates per beat | `writing-plan.md` | Book-writer runs `book_check.py` | Phase 6 / beat exit |
| Frozen-line amendment protocol | `writing-plan.md` | Writer + master + user checkpoint | Any amendment during Phases 5–6 |
| Stage-gate decisions | `decisions-log.md` | Orchestrator records T1/T3/T4 exit status; user signs off | Every boundary |

## Known gaps / questions for user

1. The checked-in `book_check.py` currently parses `style-guide.md`, `tashkeel-policy.md`, and `frozen-lines.json`, but does not parse `bible.md`'s Updated-through footer; T13 documents the intended contract without changing PR-1 code.
2. `book_check.py`, `strip_publish_annotations.py`, and `build_exports.py` emit results but do not directly write `ledger.md`; T14 makes the orchestrator's append step explicit.
3. Intake currently uses shared starter checklists for front and back matter; master may want project-specific lists before copying.
4. The new `writing-plan.md` contract assumes beat-level identifiers even though the original template only had chapter-level dispatch rows.
5. User must resolve the Open questions in each staged file before destination placement if they affect runtime parsing or gate policy.
