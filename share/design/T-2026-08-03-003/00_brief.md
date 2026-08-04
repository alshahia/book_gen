# Design Brief — T-2026-08-03-003

## User task
Stage additive edits to six existing book-agent templates so PR-1 scripts and PR-2 templates form one coherent runtime contract. Master will place the staged files back into `book_workflow/book-agents/templates/`.

## 7-question discovery

| Question | Answer |
|---|---|
| Medium | Documentation/template artifacts; no visual mockup medium applies. Framework-agnostic Markdown. |
| Audience | Master/orchestrator, book-writer, am-coder, am-review, and human project maintainers. |
| Constraints | Preserve existing front matter and sections; additive edits only; terse/table-driven voice; scripts remain unchanged; stage only under `share/design/T-2026-08-03-003/06_copy/templates/`; do not edit source templates. |
| Artifact set | Six staged template edits, a change manifest, a cross-reference summary, and a handoff. |
| Mode set | WRITE + EXTEND: write machine-readable template contracts and extend existing templates without reordering their current content. |
| Scope tier | M / starter-set: six coordinated template contracts. |
| Success criteria | Six `.edited.md` files exist with required sections, each ends with `## Open questions`, each has a near-bottom `## Mechanical gates`, cross-references identify script consumers, and master receives a clear placement handoff. |

## Existing pattern scan

Existing templates and all seven PR-2 templates were read before production. No external component, framework, or library pattern is introduced; the existing terse, structured Markdown convention is extended.

## Assumptions

- `book_check.py` consumes the exact headings and formats specified in the dispatch.
- `build_exports.py` projects `bible.md` `## Terminology` and `## Characters` into glossary/index outputs.
- `strip_publish_annotations.py` has no template parser; its ledger entry is an orchestrator contract, not a direct script write.
- The staged `.edited.md` suffix is intentional and must be removed by master when placing the files.

## Open questions

1. Should master also update the six PR-2 templates with mechanical-gate sections, or remain within T12–T17 only?
2. Should `ledger.md` be updated by the orchestrator after each run, or should a later script own that write?
3. For non-Arabic books, should intake use the literal value `not applicable` or a checkbox state in the tashkeel field?
