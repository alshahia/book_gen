# Coder Summary — T-2026-08-03-007 / PR-7 script patches

**Date:** 2026-08-03
**Sub-agent:** coder
**Loop:** initial
**Source:** T34 retroactive audit on `books_from_other_projects/city-of-memories`

## Tasks attempted

| ID | Status | Notes |
|----|--------|-------|
| P1T1 (Bug 1) | done | Added `read_md(path)` fallback helper to both scripts; replaced 8 hardcoded `encoding="utf-8"` reads on `.md` files. Kept `.json` reads as utf-8 (we author those). |
| P1T2 (Bug 2) | done | Replaced H2-only title extraction with `chapter_title()` that prefers H1 (`# `) over H2 (`## `). Also cached `ch_texts` dict so each chapter is read once instead of 3x. |
| P1T3 (Bug 3) | done (no code change) | Verified em-dash in `glossary.md` is real U+2014, not corrupted. PowerShell `Get-Content` display noise only. No code change needed. |
| P1T4 (verify) | done | All 6 verification steps pass; outputs captured below. |

## Files written / edited

- `E:\book_gen\book_workflow\scripts\book_check.py` — edited
  - `:12-22` — added `read_md(path)` helper (utf-8 → cp1256 → cp1252 → latin-1)
  - `:28` — `style_data` uses `read_md(path)` instead of `path.read_text(encoding="utf-8")`
  - `:45` — `policy()` uses `read_md(path)`
  - `:62` — chapter loop uses `read_md(file)`
  - `:57` — `frozen-lines.json` still uses `encoding="utf-8"` (we author the JSON, by spec)
- `E:\book_gen\book_workflow\scripts\build_exports.py` — edited
  - `:9-19` — added identical `read_md(path)` helper
  - `:28-34` — added `chapter_title(text)` helper; prefers H1 over H2
  - `:44` — outline.md uses `read_md`
  - `:46-51` — chapter loop reads each chapter once into `ch_texts` dict; calls `chapter_title(ch_texts[ch.name])`
  - `:53` — bible.md uses `read_md`
  - `:65` — index scan uses `ch_texts[ch.name]` (cached)
  - `:72` — total word count uses `ch_texts[ch.name]` (cached)
- `E:\book_gen\books_from_other_projects\city-of-memories\exports\` — created (5 files: `toc.md`, `glossary.md`, `index.md`, `README.md`, `clean/`)
- `E:\book_gen\book-kit\book_workflow\scripts\book_check.py` — overwritten by sync
- `E:\book_gen\book-kit\book_workflow\scripts\build_exports.py` — overwritten by sync

## Commands run

| # | Command | Exit | Output excerpt |
|---|---------|------|----------------|
| 1 | `py -3.10 book_workflow\scripts\book_check.py books_from_other_projects\city-of-memories` | 0 | `book_check: PASS (5 chapters)` — JSON shows 5 chapters, all `frozen_intact: true`, no `forbidden_matches`, `tashkeel_ratio: null` (no Arabic tashkeel chars in chapters). Word counts: 5110, 2752, 2713, 1713, 1725. |
| 2 | `py -3.10 book_workflow\scripts\build_exports.py books_from_other_projects\city-of-memories` | 0 | `{"chapters": 5, "deliverables": [...], "t1_exit": 0, "t3_exit": 0, "total_words": 14013}`. Created `books_from_other_projects/city-of-memories/exports/` for the first time. |
| 3 | `py -3.10 book_check.py books\ai-agents-with-python` | 0 | `book_check: PASS (19 chapters)` — regression clean. |
| 4 | `py -3.10 build_exports.py books\ai-agents-with-python` | 0 | `{"chapters": 19, ..., "total_words": 35619}` — regression clean. |
| 5 | diff `audit_ai-agents-with-python/exports/toc.md` vs new `books/ai-agents-with-python/exports/toc.md` | n/a | Before (audit): `Chapter 01: Start with Python` (H2 selected). After: `Chapter 01: Chapter 1 — Meet Python and AI Agents` (H1 now selected per spec). Bug 2 fix confirmed. |
| 6 | `py -3.10 book-kit\scripts\sync_from_book_gen.py --apply` | 0 | `0 copied, 2 updated, 21 skipped`. The 2 updates were `book_check.py` and `build_exports.py` (overwritten with the new SHAs). 21 SKIPs = already in sync. Matches expected "2 COPY/UPDATE". |

## Bug 3 verification

Ran the prescribed Python check:

```python
import pathlib
g = pathlib.Path(r"E:\book_gen\share\notes\audit_ai-agents-with-python\exports\glossary.md").read_text(encoding="utf-8")
print(repr(g))
```

Output:
```
'# Glossary\n\n[No terminology entries yet — populate bible.md]\n'
```

The em-dash is U+2014 (`\u2014`), not U+FFFD (`\ufffd`). The `�??` artifact only appeared in PowerShell `Get-Content` output because PowerShell's default console code page is not UTF-8 on this Windows host. **No code fix needed for Bug 3 — the strings in `build_exports.py:37,47` are correct UTF-8 em-dashes (U+2014).**

## Deviations from plan

- The `city-of-memories` chapters have NO H1 or H2 heading at all (first line is raw Arabic prose). The new `chapter_title()` helper returns `""` for them, so the new `toc.md` shows `Chapter 01: ` (empty title) for all 5 chapters. This is a pre-existing book-content issue (the writer agent didn't insert the H1), not a script bug. The spec for the bug fix is correct per the documented chapter format (`# Chapter 01: title`); the Arabic book pre-dates that format. Documented for `city-of-memories` retro-fit but **not in scope** for PR-7.
- The new `toc.md` for `books/ai-agents-with-python` shows `Chapter 01: Chapter 1 — Meet Python and AI Agents` — the "Chapter 1" prefix is redundant with the script's `Chapter {int(n):02d}` prefix. This is a content redundancy (the H1 in `ch-01.md` says `Chapter 1 — ...`), not a script bug. Each chapter's H1 is the full chapter heading including its own numeric prefix.
- The pre-existing `outline = read_md(...)` read on line 44 is still unused — that's a pre-existing dead read, not in scope for PR-7.

## Known issues / TODOs left in code

- `city-of-memories` chapters lack H1 titles — `exports/toc.md` will show empty titles until the writer agent retro-adds them. **MEDIUM** — UX issue for the first Arabic book to successfully build exports.
- `outline.md` is read on `build_exports.py:44` but never used. Dead read (8KB wasted on large outlines). **LOW** — pre-existing, not in scope.
- The two scripts each carry an identical `read_md` helper (≥10 lines duplicated). Pre-approved per the spec ("duplicate the helper in both files — keeps each script standalone"). If a third script needs the same fallback, promoted to a shared util.

## Suggested review focus

- `book_check.py:12-22` and `build_exports.py:9-19` — confirm the encoding fallback chain is correct (cp1256 first because Arabic is the failure case; cp1252 as a Western European fallback; latin-1 as the universal hammer).
- `build_exports.py:28-34` — confirm `chapter_title()` ordering: H1 (`# `) is checked before H2 (`## `), and `x.startswith("# ")` correctly excludes H3-H6 from the match (note the trailing space — `#abc` won't match).
- `build_exports.py:46-51, 65, 72` — confirm the `ch_texts` dict is the only place chapters are read; grep for any remaining `ch.read_text(encoding=` or `(root / "chapters" / ch.name).read_text(` to verify the cache is comprehensive.
- `build_exports.py:59` — em-dash in `[No terminology entries yet — populate bible.md]` is U+2014 (verified via `repr()`); if PowerShell display artifacts reappear, that's a console issue, not a file issue.

## Self-critique

- **Did I do my job?** Yes. Three bugs addressed, all six verification steps pass, no scope creep.
- **What might I have missed?**
  - Did not add a test for `read_md()` — the helper is testable in isolation but no test framework is wired for these scripts. Pre-existing scripts had no tests either.
  - Did not verify that `books_from_other_projects/city-of-memories/style-guide.md` and `tashkeel-policy.md` actually exist (the bug was triggered by `bible.md`, but the other files could also be cp1256). The patch handles them transparently, so no separate check needed.
- **What did I assume without evidence?**
  - Assumed cp1256 vs cp1252 ordering doesn't matter for the Arabic book. Verified: `bible.md` first bytes are `\xe2\x80\x94` (utf-8 em-dash) followed by Arabic utf-8, so utf-8 succeeds for `bible.md`. The chapters are cp1256 (PowerShell display shows `�` chars). The fallback order handles both correctly.
  - Assumed the spec's formula `[Chapter {int(n):02d}: {title}]` is the production format. Not modified — out of scope.
