# Design Handoff — T-2026-08-03-003

## Status

`DONE_WITH_CONCERNS` — six staged additive template edits are complete. Master owns copying them into `book_workflow/book-agents/templates/`; the source templates were not edited.

## Next consumer

Master/orchestrator. Copy each file listed in `06_copy/manifest.md` to its destination using the original filename, then route the concerns to the appropriate PR/fix owner.

## Artifacts

- `share/design/T-2026-08-03-003/00_brief.md`
- `share/design/T-2026-08-03-003/06_copy/templates/intake.edited.md`
- `share/design/T-2026-08-03-003/06_copy/templates/bible.edited.md`
- `share/design/T-2026-08-03-003/06_copy/templates/ledger.edited.md`
- `share/design/T-2026-08-03-003/06_copy/templates/style-guide.edited.md`
- `share/design/T-2026-08-03-003/06_copy/templates/writing-plan.edited.md`
- `share/design/T-2026-08-03-003/06_copy/templates/decisions-log.edited.md`
- `share/design/T-2026-08-03-003/06_copy/manifest.md`
- `share/notes/02_plan_design_T-2026-08-03-003_book-gen-template-edits.md`
- `share/messages/design-to-master-T-2026-08-03-003-handoff.md`

## How to use this

Treat the six `.edited.md` files as staged replacements, not as new template names. Preserve the original filenames when placing them. After placement, the master should resolve the Open questions that affect policy, then have the next owner validate the runtime parser contracts against the exact headings and placeholders.

The scripts remain the source of mechanical behavior. The templates now expose the sections and recording formats those scripts/orchestrator are expected to consume. Do not infer that a script writes a template merely because the ledger documents its output; the orchestrator owns ledger append operations.

## Top 3 locked decisions

1. New sections are additive; existing front matter and existing content order are retained.
2. `style-guide.md` is the primary T1 contract for word counts, forbidden patterns, and human-readable frozen-line WHY references.
3. `bible.md` is the canonical source for terminology and characters; T4 projects those sections to glossary/index outputs.

## Open questions

1. `book_check.py` PR-1 does not currently parse `bible.md`'s `Updated through ch-NN` footer; master must decide whether this is a PR-4/controller follow-up or accepted documentation-only behavior.
2. The scripts emit T1/T3/T4 results but do not write `ledger.md`; master must confirm the orchestrator append implementation and ownership.
3. Confirm whether the shared front/back matter checklists and beat-level writing-plan placeholders are the desired canonical contract.

## Do-not list

- Do not edit the six source templates directly from this handoff; master owns placement.
- Do not copy the `.edited.md` suffix into the destination.
- Do not add mechanical-gate sections to the seven PR-2 templates under this task.
- Do not change `book_check.py`, `strip_publish_annotations.py`, or `build_exports.py` under this design task.

## Self-critique

- ✓ All six requested T12–T17 staged files exist under `share/design/T-2026-08-03-003/06_copy/templates/`.
- ✓ Existing source front matter and sections were read first and remain represented; no source template path was written.
- ✓ Each edited template has a near-bottom `## Mechanical gates` section and ends with `## Open questions`.
- ✓ `style-guide.md` uses the parser-compatible `## Word-count windows`, `## Forbidden patterns`, and `## Frozen lines` headings; forbidden patterns are comment-only by default so the starter template does not accidentally fail chapters.
- ✓ No external libraries, frameworks, APIs, visual mockups, or visual-fidelity claims were introduced; browser verification is not applicable.
- ⚠ The checked-in T1 script does not implement the requested Updated-through footer warning; this is surfaced above rather than silently claimed as active.
- ⚠ Ledger population is an orchestrator contract; the three scripts currently print results rather than editing the ledger.
- ✓ No `src/**`, application code, other specialist folders, or source template files were touched.

## Sources consulted

- `book_workflow/book-agents/templates/intake.md`
- `book_workflow/book-agents/templates/bible.md`
- `book_workflow/book-agents/templates/ledger.md`
- `book_workflow/book-agents/templates/style-guide.md`
- `book_workflow/book-agents/templates/writing-plan.md`
- `book_workflow/book-agents/templates/decisions-log.md`
- `book_workflow/book-agents/templates/skeleton.md`
- `book_workflow/book-agents/templates/research-log.md`
- `book_workflow/book-agents/templates/outline.md`
- `book_workflow/book-agents/templates/operational-caps.md`
- `book_workflow/book-agents/templates/frozen-lines.schema.json`
- `book_workflow/book-agents/templates/preface.md`
- `book_workflow/book-agents/templates/toc.md`
- `book_workflow/book-agents/templates/glossary.md`
- `book_workflow/book-agents/templates/exports-readme.md`
- `book_workflow/book-agents/templates/tashkeel-policy.md`
- `book_workflow/scripts/book_check.py`
- `book_workflow/scripts/strip_publish_annotations.py`
- `book_workflow/scripts/build_exports.py`

TASK-FILE-WAS-MISSING: created minimal task row from dispatch prompt

STATUS: DONE_WITH_CONCERNS
