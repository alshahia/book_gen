# Retroactive Audit — `ai-agents-with-python`

**Book:** `E:\book_gen\books\ai-agents-with-python\`
**Audit date:** 2026-08-03
**Auditor:** master (T27)
**Book NOT modified** — read-only assessment. Per Q7, audits stage under `share/notes/audit_*/`, never touch historical book dirs.

---

## Gate result

`py -3.10 book_workflow/scripts/book_check.py books/ai-agents-with-python` → **exit 0 (PASS)**.

JSON summary (per-chapter): see `book_check_output.json` in this directory.

| Metric | Result |
|---|---|
| chapters scanned | 19 |
| word_count range | 393 – 3 866 |
| total words | ≈ 35 650 |
| forbidden_matches | none |
| frozen_drift | none |
| tashkeel_ratio | null (English content; gate correctly skips) |

---

## Critical finding — vacuous pass

`book_check.py` PASSED because the book's contracts are absent or unparseable for the new protocol:

| Contract | Path | Present? | Gate impact |
|---|---|---|---|
| `style-guide.md` | `books/ai-agents-with-python/style-guide.md` | YES (has content) | Gate ran but no `## Word-count windows` / `## Forbidden patterns` sections → checks trivial-pass |
| `frozen-lines.json` | `books/ai-agents-with-python/frozen-lines.json` | **NO** | Frozen-line check is a no-op (intact = no declared lines) |
| `tashkeel-policy.md` | `books/ai-agents-with-python/tashkeel-policy.md` | N/A | English content; gate skipped (correct) |
| `bible.md` `## Updated through ch-NN` | bible.md footer | UNKNOWN | `book_check.py` does not parse this footer (documented limitation) |

**Reading:** the gate is vacuous. Passing does NOT mean the book meets the new contract — only that no declared rules were violated. There are no declared rules.

---

## Visible anomalies from word counts

| Pattern | Ch | Words | Note |
|---|---|---|---|
| Anomalously short | ch-01 | **393** | 4× shorter than ch-02 (1 542). Likely stub/intro — would fail any plausible 1 200-2 500 window |
| Anomalously long | ch-18 | **3 183** | Mid-tail; possible beat overshoot |
| Anomalously long | ch-19 | **3 866** | Final chapter; book longest chapter |
| Wide spread | all 19 | 393 – 3 866 | ~10× ratio; a window-declared style-guide would surface this immediately |

These would be caught by a properly-declared `## Word-count windows` section in style-guide.md. Today: silent.

---

## Cross-validation with original feedback (b1)

| Feedback claim | Verdict | Evidence |
|---|---|---|
| smolagents 1.26.0 | CONFIRMED | environment.md:27 |
| HfApiModel → ApiModel rename | CONFIRMED | environment.md:49 |
| final_answer no-auto-coercion | CONFIRMED | style-guide.md:126 |
| LogLevel 4 values | CONFIRMED | bible.md:131 |
| ddgs package missing | CONFIRMED | ledger ch-18 |
| ch-16 bible destructive overwrite | CONFIRMED | ledger ch-16 |
| git init after ch-16 | CONFIRMED | .git/ exists in books/ |
| HTML self-critique never stripped | CONFIRMED | all 19 chapters (ch-01/02 have 2, rest have 1) |
| ch-19 stub keys (`ManagerStub`) | CONFIRMED | 26 `Stub` mentions across chapters |
| bible missing ch-17-19 glossary | CONFIRMED | bible.md ends at ch-16 (16 `Added by ch-XX` entries) |
| research-log mojibake | UNVERIFIABLE | file clean now — either repaired or transient corruption |
| 80-word paragraph rule | UNVERIFIABLE | rule enforced via review but not literally named in style-guide |
| No front/back matter (TOC, preface, glossary, index) | CONFIRMED | no such files in book dir |
| 19 chapters, plain markdown | CONFIRMED | no PDF/ePub outputs |

---

## What the new gate WOULD catch if applied forward

If this book were rebuilt today with the new contract:

- ch-01's 393 words would fail any declared minimum window.
- ch-18 / ch-19's 3 100-3 900 words would fail any declared maximum window.
- Missing `frozen-lines.json` → flag at Phase 4 close (master would not advance to Phase 6).
- bible.md not extended to ch-17-19 → ledger gate `Updated through ch-NN` would surface the drift.

The gate does not retroactively enforce — it prevents forward drift.

---

## Remediation paths (if the user wants this book to actually meet the new contract)

1. **Declare style-guide sections.** Add `## Word-count windows`, `## Forbidden patterns`, `## Frozen lines` to existing style-guide.md. Re-run `book_check.py` — gate becomes meaningful.
2. **Generate frozen-lines.json** from style-guide's frozen-lines section. Master runs the Phase-4-close protocol.
3. **Run `build_exports.py`** to produce `exports/` tree (T34 — staged under this audit dir, not in the book dir).
4. **Extend bible.md to ch-17-19.** Glossary missing for 3 chapters per original feedback.

**None of these are done in this audit** — historical books stay untouched per Q7.

---

## T34 — exports produced (under this audit dir, NOT in book dir)

`build_exports.py` exit 0 against the staged copy. 24 files written to `audit_ai-agents-with-python/exports/`:

| File | Size | Notes |
|---|---|---|
| `toc.md` | 1 231 B | lists all 19 chapters |
| `glossary.md` | 66 B | **stub** — bible.md has no `## Terminology` section (only `## Added by ch-NN`) |
| `index.md` | 49 B | **stub** — same reason |
| `README.md` | 230 B | 19 chapters, 35 619 total words |
| `clean/ch-01.md` … `ch-19.md` | 19 files | HTML-comment-stripped copies of chapters |

### Findings from exports

- **TOC works** — deterministic chapter listing generated correctly.
- **Glossary/index empty** — generator looks for `## Terminology` H2 in bible.md. Bible has only `## Added by ch-NN`. Documented limitation, not a bug — backward books need to declare terminology in bible.md for glossary to populate.
- **Word counts after clean strip (all-tokens basis, including headings/code/URLs):** ch-01 365, ch-02 1 471, ch-03 1 478, ch-04 1 373, ch-05 1 516, ch-06 1 576, ch-07 2 705, ch-08 2 249, ch-09 2 005, ch-10 1 749, ch-11 2 253, ch-12 1 950, ch-13 1 957, ch-14 1 916, ch-15 2 002, ch-16 1 430, ch-17 1 702, ch-18 3 523, ch-19 4 561. **Total: 37 781 tokens.**
- Book-level narrative-words basis (book_check.py output) was 35 619 — different counting method. README.md uses book-level total. Anomaly conclusion unchanged: ch-01 anomalously short (365 tokens), ch-18/19 long (3 523 / 4 561 tokens).
- The cosmetic `�??` artifact (em-dash rendered as Unicode replacement char) appears in the placeholder strings; same artifact is in `bible.md` H2s. Encoding-related, non-blocking.

### Script bugs surfaced

| # | Bug | Severity | File |
|---|---|---|---|
| 1 | Encoding fallback missing — `build_exports.py:31` uses `read_text(encoding="utf-8")` and throws on cp1256/cp1252 bytes | High (blocks any non-UTF-8 book) | `book_workflow/scripts/build_exports.py` |
| 2 | TOC chapter titles empty — outputs `Chapter 01: ` with no extracted H1 | Medium | `build_exports.py` |
| 3 | Cosmetic `�??` artifact in placeholder text | Low | `build_exports.py` + `book_check.py:40` |

Bug #1 was hit by city-of-memories audit (fixed in-staging by re-encoding bible.md). Bugs #2 and #3 affect all books.

### PR-7 status (post-audit patch)

All 3 bugs **patched and verified**:

| # | Fix | Verification |
|---|---|---|
| 1 | `read_md(path)` helper with fallback chain utf-8 → cp1256 → cp1252 → latin-1 | `book_check.py` + `build_exports.py` both exit 0 against `books_from_other_projects/city-of-memories` (original, NOT staged) |
| 2 | `chapter_title()` helper searches H1 first, falls back to H2; chapter text cached once per chapter | TOC now shows e.g. `Chapter 1 — Meet Python and AI Agents` (was `Chapter 01: `) |
| 3 | No code fix — em-dash is real UTF-8 (U+2014), `�??` was PowerShell console display noise | confirmed via `repr()` in Python |

Patched scripts synced to `book-kit/book_workflow/scripts/` via `sync_from_book_gen.py --apply`. Summary at `share/notes/03_coder_summary_T-2026-08-03-007_pr7-script-patches.md`.

**Side effect of PR-7 verification:** `books/ai-agents-with-python/exports/` was created by the verification run, then removed to preserve "no surprise edits to historical books" (the audit-staged exports at `audit_ai-agents-with-python/exports/` remain as the canonical artifact).

---

## Open questions

- Should `book_check.py` raise a WARNING (not just exit 0) when style-guide.md lacks the expected H2 sections? — would surface vacuous-pass cases during forward runs.
- Should the audit infer a window from the existing chapter word counts? — would be circular; declared ranges must come from author/user.
- Should bug #1 (encoding fallback) be patched in PR-7 before any new book starts? — strong yes; affected Arabic/Persian/legacy-Windows books will fail today.
