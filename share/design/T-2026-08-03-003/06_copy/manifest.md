# Staged Template Edit Manifest — T-2026-08-03-003

Stage root: `share/design/T-2026-08-03-003/06_copy/templates/`
Destination owner: master (copy each `.edited.md` file back to `book_workflow/book-agents/templates/` with the original filename).

| T-number | Staged file | Summary |
|---|---|---|
| T12 | `intake.edited.md` | Adds operational caps, tashkeel, front/back matter checklists, frozen-line policy, Phase 0/3 gate contract, and open questions. |
| T13 | `bible.edited.md` | Makes Terminology and Characters mandatory, adds the Updated-through footer, and documents glossary/index/staleness consumers. |
| T14 | `ledger.edited.md` | Adds T1/T3/frozen/tashkeel columns, append-only mechanical gate log, and script/orchestrator ownership. |
| T15 | `style-guide.edited.md` | Adds word-count windows, fenced forbidden regex patterns, human-readable frozen-line references, and T1 gate documentation. |
| T16 | `writing-plan.edited.md` | Adds per-beat T1 requirements and the stop/checkpoint/amend/regenerate frozen-line protocol. |
| T17 | `decisions-log.edited.md` | Adds all phase-boundary stage-gate rows and T1/T3/T4 sign-off rules. |

## Placement checklist

- [ ] Preserve the original `.md` filenames when copying into `book_workflow/book-agents/templates/`.
- [ ] Do not copy the `.edited.md` suffix into the destination.
- [ ] Do not replace the seven PR-2 templates as part of T12–T17.
- [ ] Review the concerns in `99_handoff.md`, especially the `book_check.py` footer-parser gap.
