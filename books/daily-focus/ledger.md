# Chapter Ledger — Daily Focus: A practical guide to building a personal productivity system

One row per chapter. Orchestrator and reviewers read this instead of re-reading chapter content to check status.

| Chapter | Status | Depends on | Word count | Dev review | Line edit | Notes |
|---|---|---|---|---|---|---|
| ch-01 | approved | independent | 2,465 | pass | pass | Dev PASS_WITH_WARN (1 LOW, fixed via surgical edit at line 59) + line edit PASS. Smoke-test target complete. Self-critique HTML block at ch-01.md:87-94 is for orchestrator/reviewer handoff only — strip at publish time (per line-edit review note). |
| ch-02 | skipped | ch-01 | - | - | - | Stub for smoke test (not dispatched per user-confirmed Phase 6/7 scope) |
| ch-03 | skipped | ch-01, ch-02 | - | - | - | Stub for smoke test (not dispatched per user-confirmed Phase 6/7 scope) |
| ch-04 | skipped | ch-01, ch-02, ch-03 | - | - | - | Stub for smoke test (not dispatched per user-confirmed Phase 6/7 scope) |
| ch-05 | skipped | ch-01, ch-02, ch-03, ch-04 | - | - | - | Stub for smoke test (not dispatched per user-confirmed Phase 6/7 scope) |

Status values, in order: `planned` → `drafted` → `dev-reviewed` → `line-edited` → `approved`

Smoke-test scope (per intake exception-handling + user-confirmed in Phase 6/7 gate):
- ch-01 is fully written + reviewed (dev + line passes complete → `approved`)
- ch-02–05 are stubbed with `skipped` ledger status (writer agent not dispatched)
- Whole-book copy-edit pass is skipped (its review surface requires every chapter at `approved`)

Rules:
- Only `approved` chapters count toward the whole-book copy-edit pass.
- Removing/reordering an `approved` chapter requires a user checkpoint.
- Adding a new chapter row always requires a user checkpoint.
- An `in-progress` (not yet `drafted`) chapter can be freely revised without a checkpoint, within approved scope.
- `skipped` is a smoke-test-only state for chapters outside the smoke scope; it is not a normal pipeline status.
