# Decisions Log — [Working Title]

Append-only record of why things changed. Answers "why isn't X included" without re-deriving it later.

---

### decision-001
Date: [date]
Phase: [e.g. Phase 3 — full outline]
What changed: [e.g. "ch-05 removed, merged into ch-04"]
Why: [reasoning]
User confirmed: [yes/no — reference checkpoint]

---

### decision-002
Date: [date]
Phase: [e.g. Phase 2 — research]
What changed: [contradiction resolution — "chose position B on X"]
Why: [reasoning, reference research-log.md#contradiction-001]
User confirmed: [yes/no]

## Stage-gate decisions

Append one entry at each phase boundary. Gate status records the T1/T3/T4 exit codes observed at that boundary.

| phase boundary | decision | date | rationale | gate status |
|---|---|---|---|---|
| 0→1 | [decision] | [date] | [rationale] | T1:— / T3:— / T4:— |
| 1→2 | [decision] | [date] | [rationale] | T1:— / T3:— / T4:— |
| 2→3 | [decision] | [date] | [rationale] | T1:— / T3:— / T4:— |
| 3→4 | [decision] | [date] | [rationale] | T1:— / T3:— / T4:— |
| 4→5 | [decision] | [date] | [rationale] | T1:— / T3:— / T4:— |
| 5→6 | [decision] | [date] | [rationale] | T1:— / T3:— / T4:— |
| 6→7 | [decision] | [date] | [rationale] | T1:— / T3:— / T4:— |
| 7→ship | [decision] | [date] | [rationale] | T1:— / T3:— / T4:— |

## Mechanical gates

- **Orchestrator — every stage boundary:** appends exactly one row to `## Stage-gate decisions`.
- **`book_check.py` (T1):** exit code is recorded for the boundary where chapter validation is run.
- **`strip_publish_annotations.py` (T3):** exit code is recorded for the boundary where clean export is run.
- **`build_exports.py` (T4):** exit code is recorded for the boundary where exports are assembled; T4 itself invokes T1 and T3.
- **User review:** the user reviews and signs off the decision and gate status before the next phase begins.

## Open questions

1. Should a boundary without a script run record `—`, `N/A`, or the last known exit code?
2. Does `7→ship` require a fresh T4 export after the final user sign-off?
3. Where should the user sign-off reference point to: checkpoint message, decisions-log entry, or both?
