# Plan — book-kit v0.2.0 (translation-mode aware)

Owner: master · Status: ACTIVE · Slice in flight: **alpha**

## Origin

End-of-run feedback from a 29-file Arabic translation of "Agentic Design Patterns".
Six of eleven pain points were mechanical, three workflow, two production-grade.
The kit already shipped ~60% of the desired surface in skeleton form, but the
project was hand-rolled and never went through Phase 0 intake.

## Translation-mode routing decision

Phase 0 toggle inside `intake.md`. Single orchestrator
(`book-gen-orchestrator`) handles both native book-gen and translation-gen.

## Slice sequencing

### alpha (THIS SLICE)

- **A1** `book_workflow/scripts/book_check.py` — patch chapter regex; add fence-balance, required-H2, source-ratio, untranslated-English, glossary-drift checks
- **A2** `book_workflow/book-agents/templates/source-map.md` (new)
- **A3** `book_workflow/book-agents/templates/intake.md` — Phase 0 toggle patch
- **A4** `agents_manager/book-writer/SKILL.md` — chunked-write protocol
- **A5** `book_workflow/book-agents/templates/.translate-progress.schema.json` (new)
- **A6** `agents_manager/book-writer/SKILL.md` — resume protocol

### beta (after alpha)

- **B1** `agents_manager/book-reviewer/SKILL.md` (new skill, not new agent) — two-pass review
- **B2** `book_workflow/scripts/split_source.py` — H2-bounded source splitting
- **B3** `book_check.py` — wire split_source output into resume detection

### full (after beta)

- **F1** `book_workflow/scripts/extract_figures.py` — pdfimages wrapper
- **F2** `scripts/md2pdf.py` (project-local) — `<img>` insertion
- **F3** `book_workflow/scripts/build_exports.py` — RTL TOC + Arabic-Indic page numbers
- **F4** `book_workflow/scripts/poll_progress.py` — file watcher → `.dashboard.html`

## Smoke-test protocol

Runs against `E:\books_gen\Agentic Design Patterns translate to arabic\books\agentic-design-patterns-ar` before any alpha code lands:

1. Patch book_check.py with regex fix + new checks (A1).
2. Generate source-map.md (auto-derived from `source/` ↔ `chapters/`).
3. Run `py book_check.py` against the project.
4. Report per-check PASS/FAIL counts + first 20 failures per check.
5. Smoke report is the alpha acceptance test.

## Non-goals

- No new agent slot. Two new skills only.
- No new CLI tool. Extend book_check.py.
- No kit daemon. File-based progress + polling script.
- No second LLM for review pass.
- No rewrite of build_exports.py.

## Review gates

- Each alpha file gets one tiny assert-based self-check in `__main__`.
- Smoke test report must show real failures on the 29-file project.
- No new dependency. Stdlib only.
