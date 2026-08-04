# 02_plan_design_T-2026-08-03-002 — Book-gen templates

## Files staged

| Path | Lines | Contract |
|---|---:|---|
| `share/design/T-2026-08-03-002/06_copy/templates/operational-caps.md` | 37 | Per-chapter word caps and style overrides sourced from the bible or decisions log. |
| `share/design/T-2026-08-03-002/06_copy/templates/frozen-lines.schema.json` | 106 | JSON Schema (draft 2020-12) for the `frozen-lines.json` manifest consumed by `book_check.py` and `build_exports.py`. |
| `share/design/T-2026-08-03-002/06_copy/templates/preface.md` | 50 | LLM contract for the front-matter preface, gated by `book_check.py`. |
| `share/design/T-2026-08-03-002/06_copy/templates/toc.md` | 35 | Deterministic table of contents with `<!-- PAGE TBD -->` placeholders. |
| `share/design/T-2026-08-03-002/06_copy/templates/glossary.md` | 33 | Back-matter glossary projected from `bible.md` §Terminology. |
| `share/design/T-2026-08-03-002/06_copy/templates/exports-readme.md` | 40 | Exports README with deterministic provenance. |
| `share/design/T-2026-08-03-002/06_copy/templates/tashkeel-policy.md` | 42 | Arabic diacritics policy with per-chapter targets and refusal rule. |

<!-- ponytail: templates staged under share/design because book_workflow/book-agents/templates/ is outside the design write lane. -->

## Cross-reference table

| Template | Consumer |
|---|---|
| `operational-caps.md` | `book_check.py`, book-writer, am-review |
| `frozen-lines.schema.json` | `book_check.py`, `build_exports.py`, am-review |
| `preface.md` | am-design (LLM pass), `book_check.py`, `build_exports.py` |
| `toc.md` | `build_exports.py`, am-review |
| `glossary.md` | `build_exports.py`, am-review |
| `exports-readme.md` | `build_exports.py`, readers, am-review |
| `tashkeel-policy.md` | `book_check.py`, book-writer, am-review, master |

## Known gaps and questions

1. Destination is outside the am-design write lane; downstream master placement in `book_workflow/book-agents/templates/` is required.
2. JSON Schema `x-open-questions` mirrors the Markdown `## Open questions` for consistency.
3. Tashkeel policy is filled at Phase 3 (outline confirmation) per task spec.
4. No sibling template or script edits were made.
