# Book Kit Changelog

All notable changes to the Book Kit. Newest on top.

The Book Kit is the portable book-gen deliverable in this repo. It bundles
the agents-manager controller + book-gen specialization + 8 scripts + 19
templates + tests + docs. Native books AND translations ship first-class.

## v1.1.0 — smoke debt cleared + tolerances configurable (2026-08-05)

The 5 v0.2.0 smoke findings that lingered are now closed: hardcoded
tolerances moved to `style-guide.md` frontmatter, per-chapter overrides
landed in `source-map.md`, and `md2pdf.py` is promoted to the kit.
`book_check.py` against the 29-chapter Arabic translation project now
returns 0 failures.

### What's new

1. **`md2pdf.py` promoted to kit** — was project-local at
   `E:\books_gen\Agentic Design Patterns...\scripts\md2pdf.py`. Now in
   `book-kit/book_workflow/scripts/`. Converts Arabic Markdown to RTL
   PDF via Chrome/Edge headless, with optional `--figures-manifest` to
   embed extracted figures before italic `> **الشكل N:**` placeholders.
   Idempotent + self-check + 8 pytest tests.
2. **`book_check.py` reads tolerances from `style-guide.md` frontmatter** —
   `untranslated_english`, `source_ratio`, `stuck_threshold_min` move
   out of hardcoded constants. Missing keys fall back to defaults.
   The YAML-frontmatter parser is minimal (no PyYAML dependency).
3. **Per-chapter overrides in `source-map.md`** — two new columns:
   `source_ratio_override` (e.g. `0.50`) and `glossary_drift_exempt`
   (`yes`/`no`). The kit's `source-map.md` template now ships with
   these columns, and `book_check.py` honors them. The Arabic
   translation project uses them for ch-05/ch-20 (lower source-ratio
   band) and intro/ch-15/app-b (exempt from glossary drift).
4. **6 new pytest tests for the new behavior** — tolerance parsing
   (4 tests covering no-file, partial override, percentage, malformed
   value) and source-map parsing (2 tests for ratio override + exempt
   columns). Total pytest count: **77** (was 63).
5. **`docs/SCRIPTS.md` documents `md2pdf.py`** — new section with
   usage, flags, behavior, requirements. Updated test count and script
   count (8 scripts).
6. **`build_manifest.py` allowlist updated** — `tests/*.py`,
   `pytest.ini`, `docs/WORKFLOW.md`, `docs/TRANSLATION_MODE.md`,
   `docs/SCRIPTS.md` now in the engine-files list. Total engine files
   tracked: 71.

### Reference implementation

The `agentic-design-patterns-ar` translation project now has 0
failures from `book_check.py` and 0 missing URLs from
`bilingual_smoke.py`. See its updated `exports/SMOKE_REPORT.md` for
the per-chapter override rationale and the v0.3.0 → v1.1.0 resolution
table.

### What's still open

- `bin/promote.py` + `.book-kit/overrides/` — explicit script
  promotion mechanism. Deferred to v1.2.0.
- 10 known complex pdftotext URL corruptions documented in
  `fix_source_urls.py` but not auto-fixed (manual review per project).

## v1.0.0 — book-gen deliverable (2026-08-05)

**The first "ship the whole thing" release.** v1.0.0 reframes this repo
as a book-gen deliverable (not just an agents-manager controller with a
book specialization bolted on). The user-facing README is now book-gen
first; agents-manager is the underlying engine, documented second.

### What's new

1. **`fix_source_urls.py` promoted to kit** — was project-local at
   `E:\books_gen\Agentic Design Patterns...\scripts\fix_source_urls.py`.
   Now in `book-kit/book_workflow/scripts/`. Repairs 6 distinct
   `pdftotext` artifacts in source `.txt` files: pure-digit page-number
   lines, `/N` glued page numbers, doubled last segments, truncated URL
   splits across lines, trailing `..`, trailing `/#`. Idempotent +
   self-check + 14 pytest tests.
2. **63 pytest tests across all 7 scripts** — replaces `--self-check`
   as the source of truth. Run with `cd book-kit && py -m pytest`.
   Breakdown:
   - `test_fix_source_urls.py` — 14 tests
   - `test_book_check.py` — 12 tests
   - `test_split_source.py` — 7 tests
   - `test_extract_figures.py` — 4 tests
   - `test_poll_progress.py` — 10 tests
   - `test_build_exports.py` — 9 tests
   - `test_bilingual_smoke.py` — 7 tests
3. **Top-level README reframed as book-gen** — quickstart leads with
   "write a book about X" / "translate book Y to Arabic". The 7-phase
   pipeline is the headline. agents-manager is the "Under the hood"
   section.
4. **`book-kit/docs/QUICKSTART.md` updated** — 15-field intake (was 9),
   Branch A vs Branch B review naming, translation-mode quickstart
   section.
5. **New docs: `WORKFLOW.md`, `TRANSLATION_MODE.md`, `SCRIPTS.md`** —
   the operational guide for each phase, the translation extension,
   and the flag reference for all 7 scripts.
6. **GitHub Actions CI** — `.github/workflows/tests.yml` runs the 63
   pytest tests on push + a matrix `--self-check` job across all
   scripts. Python 3.8–3.12.
7. **`manifest.json` updated** — new sha256s for `pytest.ini`, 9 test
   files, 4 doc files, `fix_source_urls.py`. Total engine files
   tracked: 50+.
8. **Version bumped 0.22.0 → 1.0.0** — signals "this is the
   deliverable, not a beta".

### What's still open

- `bin/promote.py` + `.book-kit/overrides/` — explicit script
  promotion mechanism. Deferred to v1.1.0.
- 10 known complex pdftotext URL corruptions (page numbers glued
  without `/` separator, doubled mid-path segments, glued-URL pairs,
  concatenated adjacent path lines) — `fix_source_urls.py` documents
  them but doesn't auto-fix; manual review per project.
- The kit's `book_check.py` translation-specific checks (source-ratio,
  glossary drift, missing H2, code-block-freeze) are still
  project-aware. They're gated on `source-map.md` presence — without
  it, only base checks run.

### Reference implementation

The `agentic-design-patterns-ar` translation project (29 chapters,
800 KB Arabic manuscript) is the v0.2.0 / v1.0.0 reference. Its
`exports/SMOKE_REPORT.md` documents the validation. Bilingual smoke
URL flags went from 21 (pre-fix) to 10 (post-fix) after the v0.2.0 work
that landed `fix_source_urls.py`.

## v0.22.0 — translation-mode wired into orchestrator (2026-08-05)

Adapter release. Mirrors the controller v0.22.0 changes into the kit.
See `agents_manager/CHANGELOG.md` for the full description.

## v0.2.0 — translation-mode + mechanical review (full release) (2026-08-04)

Full release. Promotes v0.2.0-alpha to v0.2.0 with four production-grade
features: `extract_figures.py`, RTL TOC, Arabic-Indic page numbers, live
progress dashboard. Validated against the 29-file `agentic-design-patterns-ar`
project. See `books/agentic-design-patterns-ar/exports/SMOKE_REPORT.md`.

## v0.2.0-alpha — translation-mode + mechanical review (2026-08-04)

First-class translation support. 5 new checks in `book_check.py`,
`bilingual_smoke.py`, `split_source.py`. Source-extraction bugs noted as
follow-up (`fix_source_urls.py` later resolved these in v1.0.0).
