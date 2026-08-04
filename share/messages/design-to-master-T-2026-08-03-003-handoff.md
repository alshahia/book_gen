# Design-to-master Handoff — T-2026-08-03-003

## Status

`DONE_WITH_CONCERNS`

Six staged template edits are ready under `share/design/T-2026-08-03-003/06_copy/templates/`. Master should copy them back to the original filenames in `book_workflow/book-agents/templates/`.

## Files

- `intake.edited.md` → `intake.md` (T12)
- `bible.edited.md` → `bible.md` (T13)
- `ledger.edited.md` → `ledger.md` (T14)
- `style-guide.edited.md` → `style-guide.md` (T15)
- `writing-plan.edited.md` → `writing-plan.md` (T16)
- `decisions-log.edited.md` → `decisions-log.md` (T17)
- Manifest: `share/design/T-2026-08-03-003/06_copy/manifest.md`
- Summary: `share/notes/02_plan_design_T-2026-08-03-003_book-gen-template-edits.md`

## Locked decisions

1. Additive sections only; source front matter and existing content order are preserved.
2. `style-guide.md` is the T1 contract for word-count windows, forbidden regexes, and frozen-line WHY references.
3. `bible.md` remains canonical for terminology/characters; T4 projects them to glossary/index.

## Concerns to route

- PR-1 `book_check.py` currently has no `bible.md` Updated-through footer parser; T13 documents the requested contract and surfaces the implementation gap.
- The scripts emit T1/T3/T4 results but do not write `ledger.md`; T14 assigns append ownership to the orchestrator.
- Confirm shared front/back matter starter checklists and beat-level placeholders before placement if these are not the desired canonical shapes.

## Do not

- Do not copy the `.edited.md` suffix to the destination.
- Do not edit the seven PR-2 templates under this task.
- Do not modify scripts or SKILL.md files under this design task.

## Open questions

See `99_handoff.md` and the per-template `## Open questions` sections.

STATUS: DONE_WITH_CONCERNS
