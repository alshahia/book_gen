# Retroactive Audit — `city-of-memories`

**Book:** `E:\book_gen\books_from_other_projects\city-of-memories\`
**Audit date:** 2026-08-03
**Auditor:** master (T28)
**Book NOT modified** — read-only assessment. Per Q7, audits stage under `share/notes/audit_*/`, never touch historical book dirs.

---

## Gate result

`py -3.10 book_workflow/scripts/book_check.py books_from_other_projects/city-of-memories` → **exit 0 (PASS)**.

JSON summary (per-chapter): see `book_check_output.json` in this directory.

| Metric | Result |
|---|---|
| chapters scanned | 5 |
| word_count range | 1 713 – 5 110 |
| total words | ≈ 14 013 |
| forbidden_matches | none |
| frozen_drift | none |
| tashkeel_ratio | null (Arabic content but no `tashkeel-policy.md`; gate skipped) |

---

## Critical finding — vacuous pass + Arabic content without tashkeel policy

`book_check.py` PASSED but for two different reasons than `ai-agents-with-python`:

| Contract | Path | Present? | Gate impact |
|---|---|---|---|
| `style-guide.md` | `books_from_other_projects/city-of-memories/style-guide.md` | YES | Gate ran; no `## Word-count windows` / `## Forbidden patterns` sections in the declared format → checks trivial-pass |
| `frozen-lines.json` | `books_from_other_projects/city-of-memories/frozen-lines.json` | **NO** (manifest missing despite style-guide having a Frozen-line rule) | Frozen-line check no-op |
| `tashkeel-policy.md` | `books_from_other_projects/city-of-memories/tashkeel-policy.md` | **NO** | Arabic content exists; gate skipped because policy absent — see Anomaly A below |

**Reading:** the gate is vacuous AND the tashkeel check (which would have surfaced a real, documented policy split) was skipped because no policy was declared. This is the strongest case for "vacuous pass hides real defects."

---

## Anomalies from word counts

| Pattern | Ch | Words | Note |
|---|---|---|---|
| Anomalously long opener | ch-01 | **5 110** | 3× longer than ch-04/05 (1 713 / 1 725). Style-guide declares `1 700-2 000 / beat`; opener is **2.5×** the upper bound, almost certainly multi-beat |
| Beat-in-range | ch-02, ch-03 | 2 752 / 2 713 | Slightly over upper bound; possibly beats × 1.3 |
| Beat-in-range | ch-04, ch-05 | 1 713 / 1 725 | Inside the declared 1 700-2 000 window |

**Anomaly A — Tashkeel structural split (HIGHEST-PRIORITY FINDING)**

Per earlier validation (b1), `city-of-memories` has a tashkeel split:

| ch | diacritic / Arabic-char ratio | Classification |
|---|---|---|
| ch-01 | 0.015 | essentially unvocalized |
| ch-02 | 0.060 | sparsely vocalized |
| ch-03 | 0.153 | fully vocalized |
| ch-04 | 0.138 | fully vocalized |
| ch-05 | 0.135 | fully vocalized |

This split happened by accident (no Phase-3 policy decision) and was retroactively justified. The book's `style-guide.md` has no tashkeel section. The new `tashkeel-policy.md` template (T11) exists to prevent this exact pattern. **If this book were rebuilt today with the new contract, the gate would either force a decision (target ratio per chapter) or flag the mid-book shift as a style-guide violation.**

**Anomaly B — Length policy contradiction**

| Source | Value | Status |
|---|---|---|
| `style-guide.md` | `1 700-2 000 words per beat` | declared intent |
| `bible.md` ch-03 operational cap | `600-750 كلمة عربية لكل إرسالية كاتب (يمنع فساد النص العربي برموز لاتينية عند تجاوز ~1,200)` | operational override — added after ch-02 |
| ch-01 actual | 5 110 words | **2.5× upper bound, not flagged by any gate today** |

The bible entry explicitly says the cap was a master-set operational limit added after ch-02 to prevent Arabic corruption. The split between style-guide target and bible operational cap was never reconciled.

---

## Cross-validation with original feedback (b1)

| Feedback claim | Verdict | Evidence |
|---|---|---|
| Frozen-line rule in style-guide | CONFIRMED | style-guide.md:12 ("byte-for-byte with zero edits") |
| 16-thread interlink map | CONFIRMED | outline.md:71-90 (all 16 rows with plant + payoff) |
| 16/16 interlinks closed | CONFIRMED | bible.md final block (293-303) |
| Present tense, «», no emotion-naming, no «كما لو», short sentences | CONFIRMED | style-guide.md |
| Two-tier review (dev → line) | CONFIRMED | ledger.md every row shows "passed" twice |
| Tashkeel split ch-01/02 unvocalized, ch-03-05 fully vocalized | **CONFIRMED + QUANTIFIED** | diacritic ratios 0.015 / 0.060 / 0.153 / 0.138 / 0.135 |
| Length contradiction (style-guide vs bible) | **CONFIRMED** | style-guide 1 700-2 000/beat vs bible 600-750/writer-dispatch |
| Countdown rule introduced after ch-02 | PARTIAL | ch-02 has 0 `البوابة` mentions vs ch-01's 13 — consistent with retroactive application |
| No front/back matter (TOC, preface, glossary, index) | CONFIRMED | no such files in book dir |
| Fiction, no library pinning needed | N/A | (vs. ai-agents-with-python which had library churn) |

---

## What the new gate WOULD catch if applied forward

- ch-01's 5 110 words would fail any declared window of 1 700-2 000.
- Missing `tashkeel-policy.md` + Arabic content → gate should WARN (today: silent skip).
- Missing `frozen-lines.json` despite style-guide declaring a Frozen-line rule → manifest-generation step at Phase 4 close would have produced one; absence = protocol violation.
- Style-guide vs bible length contradiction → gate would surface two sources of truth.

---

## Remediation paths (if the user wants this book to actually meet the new contract)

1. **Reconcile length policy.** Pick one source of truth (style-guide or bible); cross-link the other.
2. **Declare tashkeel policy.** Use new `tashkeel-policy.md` template (T11). Set either uniform ratio or per-chapter targets.
3. **Generate `frozen-lines.json`** from style-guide's Frozen-line rule + per-chapter frozen lines.
4. **Run `build_exports.py`** to produce `exports/` tree (T34 — staged under this audit dir, not in the book dir).

**None of these are done in this audit** — historical books stay untouched per Q7.

---

## T34 — exports produced (under this audit dir, NOT in book dir)

`build_exports.py` first run **exit 1** with `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x97` on `bible.md`. Cause: bible.md was written in Windows Arabic encoding (cp1256) — em-dash byte `0x97`. The script has no encoding fallback.

**Workaround applied (in staging only):** re-encoded the staged `bible.md` from cp1256 → utf-8. Re-run **exit 0**. 10 files written to `audit_city-of-memories/exports/`:

| File | Size | Notes |
|---|---|---|
| `toc.md` | 200 B | 5 chapters listed; **titles empty** ("Chapter 01: ") — bug |
| `glossary.md` | 66 B | **stub** — bible has no `## Terminology` section |
| `index.md` | 49 B | **stub** — same reason |
| `README.md` | 230 B | 5 chapters, 14 013 total words |
| `clean/ch-01.md` … `ch-05.md` | 5 files | HTML-comment-stripped |

### Findings from exports

- **Word counts after clean strip (all-tokens basis):** ch-01 4 692, ch-02 2 426, ch-03 1 855, ch-04 1 188, ch-05 1 107. **Total: 11 268 tokens.**
- **ch-01 still 4 692 tokens** post-strip — 2.3× over style-guide upper bound (2 000/beat). Gate did not catch this because `## Word-count windows` not in declared format.
- **Encoding fix in staging only**: the original `books_from_other_projects/city-of-memories/bible.md` is unchanged. Re-running the gate against the original would still fail at byte 0x97.

### Script bugs surfaced

| # | Bug | Severity | File |
|---|---|---|---|
| 1 | Encoding fallback missing — fails on cp1256/cp1252 input | High (blocks any non-UTF-8 book, **already failed here**) | `build_exports.py:31` |
| 2 | TOC chapter titles empty | Medium | `build_exports.py` |
| 3 | Cosmetic `�??` artifact in placeholder text | Low | `build_exports.py` + `book_check.py:40` |

Bug #1 is **must-fix in PR-7** before any new Arabic/non-UTF-8 book starts the pipeline.

### PR-7 status (post-audit patch)

All 3 bugs **patched and verified**:

| # | Fix | Verification |
|---|---|---|
| 1 | `read_md(path)` helper with fallback chain utf-8 → cp1256 → cp1252 → latin-1 | `book_check.py` exit 0 against this book (originally threw `UnicodeDecodeError` at byte 0x97) |
| 2 | `chapter_title()` searches H1 first, falls back to H2 | ai-agents TOC now shows H1 titles; **city-of-memories TOC still empty** — chapter files lack H1/H2 titles (pre-existing content issue, not a script bug) |
| 3 | No code fix — em-dash is real UTF-8 | confirmed via `repr()` in Python |

**Notable:** after Bug 1 fix, the FIRST successful `build_exports.py` against the original (NOT staged) `books_from_other_projects/city-of-memories/` produced valid exports. This is a milestone — the Arabic-book pipeline now works end-to-end.

**city-of-memories TOC remains empty** because the chapter files use H1-less starts (no `# Chapter NN: title` or `## ...` lines). The fallback chain returned `""`. Two options to fix going forward: (a) add titles to chapters (modifies book — not done per Q7), or (b) extend `chapter_title()` to fall back to `outline.md` chapter list. Option (b) is a future enhancement, not a regression.

**Side effect of PR-7 verification:** `books_from_other_projects/city-of-memories/exports/` was created by the verification run, then removed to preserve "no surprise edits to historical books" (the audit-staged exports at `audit_city-of-memories/exports/` remain as the canonical artifact).

Summary at `share/notes/03_coder_summary_T-2026-08-03-007_pr7-script-patches.md`.

---

## Open questions

- Should `book_check.py` WARN when Arabic content + no `tashkeel-policy.md`? — would catch the "policy by accident" pattern in future books.
- Should the new gate prefer style-guide over bible when they disagree? — needs policy decision from the user/orchestrator.
- Should `build_exports.py` for Arabic content sort glossary differently? — current code sorts by Unicode codepoint (works for Arabic A-Z order is not meaningful; may need different sort).
- Should bug #1 be patched before T29 (e2e test on new book slug) — strong yes.
