# Design → Master — T-2026-08-03-002

## Audience

Master (placement in `book_workflow/book-agents/templates/`).

## Artifacts

- `share/design/T-2026-08-03-002/00_brief.md`
- `share/design/T-2026-08-03-002/06_copy/templates/operational-caps.md`
- `share/design/T-2026-08-03-002/06_copy/templates/frozen-lines.schema.json`
- `share/design/T-2026-08-03-002/06_copy/templates/preface.md`
- `share/design/T-2026-08-03-002/06_copy/templates/toc.md`
- `share/design/T-2026-08-03-002/06_copy/templates/glossary.md`
- `share/design/T-2026-08-03-002/06_copy/templates/exports-readme.md`
- `share/design/T-2026-08-03-002/06_copy/templates/tashkeel-policy.md`
- `share/notes/02_plan_design_T-2026-08-03-002_book-gen-templates.md`

## How to use

Copy the seven files from `share/design/T-2026-08-03-002/06_copy/templates/` into `E:\book_gen\book_workflow\book-agents\templates\`. Each file already carries a YAML front-matter block plus an `## Open questions` block. The JSON Schema uses a `$comment` header to carry the same metadata.

## Do not

- Do not modify the nine existing templates.
- Do not edit SKILL.md files.
- Do not run smoke tests yet — there are no script consumers bound to these templates.

## Top three open questions

1. Confirm the placement owner (master vs PR-3).
2. Confirm the JSON Schema `$id` host.
3. Confirm the post-PR index update strategy.

## Status

STATUS: DONE_WITH_CONCERNS
