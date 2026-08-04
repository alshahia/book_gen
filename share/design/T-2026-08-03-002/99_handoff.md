# Handoff — T-2026-08-03-002

## Audience

Master (placement), am-coder, am-review, downstream script authors.

## Artifacts

- `share/design/T-2026-08-03-002/00_brief.md` — discovery answers.
- `share/design/T-2026-08-03-002/06_copy/templates/operational-caps.md`
- `share/design/T-2026-08-03-002/06_copy/templates/frozen-lines.schema.json`
- `share/design/T-2026-08-03-002/06_copy/templates/preface.md`
- `share/design/T-2026-08-03-002/06_copy/templates/toc.md`
- `share/design/T-2026-08-03-002/06_copy/templates/glossary.md`
- `share/design/T-2026-08-03-002/06_copy/templates/exports-readme.md`
- `share/design/T-2026-08-03-002/06_copy/templates/tashkeel-policy.md`
- `share/notes/02_plan_design_T-2026-08-03-002_book-gen-templates.md` — file table, contracts, gaps.

## What to do with it

Place the seven files at `E:\book_gen\book_workflow\book-agents\templates\`. The directory is outside the am-design write lane, so master or a script-writer owns the copy.

## Do not

- Do not modify the existing nine sibling templates; this dispatch is additive.
- Do not edit `book_workflow/scripts/`; PR-1 already shipped those.
- Do not edit SKILL.md files; PR-4 owns the controller update.

## Self-critique

- All seven templates expose the contract section names requested.
- Cross-references point at sibling templates via relative paths.
- Every template ends with `## Open questions`.
- Frozen-lines schema includes descriptions, examples, and a `$comment` header for the metadata that YAML would normally carry.
- Tashkeel policy captures the Phase 3 default and the mid-Phase 5-6 refusal rule.

## Open questions

1. Confirm placement responsibility (master vs PR-3 owner).
2. Confirm the JSON Schema registry path or replace with a local file URI.
3. Confirm whether the existing nine templates need an updated index after these additions.

## Status

STATUS: DONE_WITH_CONCERNS — destination `book_workflow/book-agents/templates/` is outside the am-design write lane; templates are staged under `share/design/T-2026-08-03-002/06_copy/templates/`.
