# Design brief — T-2026-08-03-002

## Discovery

| Question | Answer |
|---|---|
| Medium | Print / Markdown publishing workflow |
| Audience | Master, am-coder, and deterministic Python scripts |
| Constraints | Markdown prose templates; JSON Schema draft 2020-12; Arabic-aware policy; terse contracts; no script or sibling-template edits |
| Artifact set | Seven publishing-policy and front/back-matter templates |
| Mode set | SYSTEMIZE, WRITE |
| Scope tier | starter-set (7 templates) |
| Success criteria | Every requested contract is represented, cross-referenced, and ready for downstream placement in `book_workflow/book-agents/templates/` |

## Assumptions

- Existing sibling templates establish concise placeholder-driven voice.
- The JSON Schema uses `$comment` and `x-open-questions` because YAML front matter and Markdown headings would invalidate JSON.
- Existing-pattern scan: no; this is an extension of a local template system.

## Constraint note

The requested destination is outside the am-design write lane. Artifacts are staged under this design tree for the next consumer to place.
