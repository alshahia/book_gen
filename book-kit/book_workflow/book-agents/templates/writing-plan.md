# Writing Plan — [Working Title]

Mode: LINEAR | PARALLEL | MIXED
Reasoning: [explicit user instruction, or dependency-tag-based reasoning]

## Execution order

1. **Group A (parallel-safe)**: ch-01, ch-02 — tagged independent
2. **Group B (linear)**: ch-03 → ch-04 — ch-04 depends_on ch-03

Each chapter dispatched one at a time (or one per parallel group), finished and saved before the next starts.

## Per-chapter dispatch reference

| Chapter | Outline entry | Research entries | Status |
|---|---|---|---|
| ch-01 | outline.md#ch-01 | entry-001, entry-004 | planned |
| ch-02 | outline.md#ch-02 | entry-002 | planned |
| ch-03 | outline.md#ch-03 | entry-003, entry-005 | planned |

## Mechanical gates per beat

For every beat sub-section in the chapter plan, record the T1 requirement before marking that beat `drafted`.

| Chapter | Beat sub-section | T1-exit requirement | Beat status |
|---|---|---|---|
| ch-NN | beat-NN | `book_check.py` exit `0` | planned |

### Per-beat contract

#### ch-NN — beat-NN
- T1-exit required: `0`.
- Mark `drafted` only after the writer runs `book_check.py` for the chapter and records the result in `ledger.md`.
- If T1 is non-zero, keep the beat out of `drafted` status and surface the failure to the master.

## Frozen-line amendment protocol

If a frozen line must change:

1. **STOP** writing and do not update the line as a local exception.
2. Surface the requested change to master with the chapter path, line number, current text, proposed text, and rationale.
3. Master triggers the user checkpoint before any amendment proceeds.
4. After approval, amend `style-guide.md`'s human-readable WHY list.
5. Regenerate `frozen-lines.json` with the new line hash and authorization source.
6. Writer resumes only after the manifest is regenerated, then reruns `book_check.py` and records the new gate result.

---
Confirmation: user must confirm this plan before any writer agent is dispatched.

## Mechanical gates

- **`book_check.py` — Phase 6, every beat exit:** writer runs T1 through the book-writer skill; exit `0` is required before the beat is marked `drafted`.
- **`strip_publish_annotations.py` and `build_exports.py` — no direct read:** these scripts run later at clean-export/export gates and do not consume `writing-plan.md`.
- The orchestrator owns status changes and ledger updates after the writer reports the gate result.

## Open questions

1. Is a beat the same unit as a chapter section, or should the project define a separate beat identifier?
2. Should T1 run against the whole book or a chapter path at each beat exit?
3. Does a frozen-line amendment require a new user checkpoint when the approved wording is restored verbatim?
