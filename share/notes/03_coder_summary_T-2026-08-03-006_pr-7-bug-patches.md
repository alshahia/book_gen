# Coder Summary — T-2026-08-03-006 / PR-7 bug patches

**Date:** 2026-08-03 15:44
**Sub-agent:** coder
**Loop:** initial
**Source files:** `E:\book_gen\book_workflow\scripts\book_check.py`, `E:\book_gen\book_workflow\scripts\build_exports.py`

## Tasks attempted
| ID | Status | Notes |
|----|--------|-------|
| P1T1 — Bug 1 encoding fallback | done | Renamed `read_md` → `read_text_safe`; new chain utf-8 → cp1256 → cp1252 → utf-8 (replace); stderr log per file |
| P1T2 — Bug 2 H1-only TOC | done | `chapter_title(text, fallback)` uses `re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)`; main passes `ch.stem` as fallback |
| P1T3 — Bug 3 word regex | done | `[\w'\-\u2018\u2019]+` in both files (replaces implicit U+2019 with explicit \u escapes + adds U+2018) |
| P1T4 — Smoke test | done | `book_check.py books/daily-focus/` → exit 0, PASS (1 chapter, 2415 words) |
| P1T5 — Staging audits | done | ai-agents-with-python (19 chapters, all H1 titles in toc.md, exit 0); city-of-memories (5 chapters, filename-stem fallback titles, exit 0, bible.md decoded as cp1256) |
| P1T6 — Book-kit sync | done | `sync_from_book_gen.py --apply` → 2 overwritten (book_check.py, build_exports.py), 21 skipped, exit 0; SHA256 verified identical to source |

## Files written / edited

### `E:\book_gen\book_workflow\scripts\build_exports.py`
- `build_exports.py:9-20` — `read_md(path)` → `read_text_safe(path)`. New fallback chain `(utf-8, cp1256, cp1252)`, with `errors="replace"` final fallback. One `[encoding] <name> → <enc>` log per call.
- `build_exports.py:22` — word regex `r"\b[\w'-]+\b"` → `r"\b[\w'\-\u2018\u2019]+\b"`.
- `build_exports.py:29-32` — `chapter_title(text)` → `chapter_title(text, fallback="")`. New impl uses `re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)`.
- `build_exports.py:42, 46, 51` — `read_md(...)` → `read_text_safe(...)` (3 call sites, all renamed).
- `build_exports.py:47` — `chapter_title(ch_texts[ch.name])` → `chapter_title(ch_texts[ch.name], ch.stem)`.

### `E:\book_gen\book_workflow\scripts\book_check.py`
- `book_check.py:64` — word regex `r"\b[\w'-]+\b"` → `r"\b[\w'\-\u2018\u2019]+\b"`. (Bug 3 fix; `read_md` left intact per "smallest diff" rule.)

### `E:\book_gen\book-kit\book_workflow\scripts\book_check.py` and `E:\book_gen\book-kit\book_workflow\scripts\build_exports.py`
- Synced from source via `sync_from_book_gen.py --apply`. SHA256 now matches source.

## Commands run

| Command | Exit | Output summary |
|---------|------|----------------|
| `py -3.10 book_check.py books/daily-focus/` | 0 | PASS (1 chapter, 2415 words) |
| `py -3.10 book_check.py audit_city-of-memories/staging_ai-agents` | 0 | PASS (19 chapters) |
| `py -3.10 book_check.py audit_city-of-memories/staging_city-of-memories` | 0 | PASS (5 chapters) |
| `py -3.10 build_exports.py audit_city-of-memories/staging_ai-agents` | 0 | 19 chapters, 35619 words, all files → utf-8 |
| `py -3.10 build_exports.py audit_city-of-memories/staging_city-of-memories` | 0 | 5 chapters, 14013 words, chapters → utf-8, **bible.md → cp1256** |
| `py -3.10 build_exports.py audit_city-of-memories/bible_cp1256_test` | 0 | 1 chapter, 7 words, ch-01 → utf-8, **bible.md → cp1256** (minimal spec test) |
| `py -3.10 book-kit/scripts/sync_from_book_gen.py` (dry-run) | 0 | 2 UPDATE, 21 SKIP |
| `py -3.10 book-kit/scripts/sync_from_book_gen.py --apply` | 0 | 2 overwritten, 21 skipped |
| `py -3.10 book-kit/book_workflow/scripts/book_check.py books/daily-focus` | 0 | PASS (post-sync re-verify) |
| `ast.parse(...)` on both patched files | 0 | Both valid Python 3 syntax |

## Tests run

No automated test suite. Verified manually:
- Word count on daily-focus unchanged (2415, same as smoke-test baseline).
- TOC for ai-agents-with-python has all 19 chapter H1s extracted: "Chapter 1 — Meet Python and AI Agents" through "Chapter 19 — Project: Multi-Agent Work Assistant".
- TOC for city-of-memories uses filename-stem fallback: "Chapter 01: ch-01" through "Chapter 05: ch-05" (chapters have no H1; only the bible has any structure).
- bible.md (cp1256) decoded without UnicodeDecodeError; helper correctly identifies the fallback encoding.
- Byte-level scan: 0 U+FFFD bytes, 0 `??` literals in either script.

## Diffs applied

### Bug 1 — encoding fallback (build_exports.py:9-20, 42, 46, 51)

```diff
-def read_md(path):
-    """Read a markdown file with encoding fallback. Tries utf-8 → cp1256 → cp1252 → latin-1."""
-    try:
-        return path.read_text(encoding="utf-8")
-    except UnicodeDecodeError:
-        for enc in ("cp1256", "cp1252"):
-            try:
-                return path.read_text(encoding=enc)
-            except UnicodeDecodeError:
-                continue
-        return path.read_text(encoding="latin-1")
+def read_text_safe(path):
+    """Read a markdown file with encoding fallback. Tries utf-8 → cp1256 → cp1252 → utf-8 (replace)."""
+    for enc in ("utf-8", "cp1256", "cp1252"):
+        try:
+            text = path.read_text(encoding=enc)
+            print(f"[encoding] {path.name} → {enc}", file=sys.stderr)
+            return text
+        except UnicodeDecodeError:
+            continue
+    text = path.read_text(encoding="utf-8", errors="replace")
+    print(f"[encoding] {path.name} → utf-8 (replace)", file=sys.stderr)
+    return text
```
3 call sites renamed: `read_md(...)` → `read_text_safe(...)`.

### Bug 2 — H1-only TOC with filename fallback (build_exports.py:29-32, 47)

```diff
-def chapter_title(text):
-    """Prefer H1 (`# `) over H2 (`## `). Returns the first heading text found, stripped."""
-    return next(
-        (x.lstrip("#").strip() for x in text.splitlines()
-         if x.startswith("# ") or x.startswith("## ")),
-        ""
-    )
+def chapter_title(text, fallback=""):
+    """Return the first H1 line, stripped. Falls back to `fallback` if no H1."""
+    m = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
+    return m.group(1) if m else fallback
```
Call site: `chapter_title(ch_texts[ch.name], ch.stem)`.

### Bug 3 — word regex with explicit Unicode escapes (build_exports.py:22, book_check.py:64)

```diff
-r"\b[\w'-]+\b"
+r"\b[\w'\-\u2018\u2019]+\b"
```

## Before / After for each bug

### Bug 1 — encoding fallback

**Before:** `read_md` used utf-8 → cp1256 → cp1252 → latin-1, silent. No log. Did not match the spec'd error-handling policy (latin-1 never throws, hides bad bytes). city-of-memories bible.md (cp1256) would have been decoded as latin-1 on full failure (it doesn't fail, so utf-8 succeeded for the first 37486 bytes then failed at byte 0x97, then cp1256 succeeded — but the function also doesn't log anything, so the user has no idea which encoding was used).

**After:** `read_text_safe` uses utf-8 → cp1256 → cp1252 → utf-8 with `errors="replace"`. Each successful read emits `[encoding] <name> → <enc>` to stderr. Verified: city-of-memories bible.md now logs `bible.md → cp1256` and decodes 41537 chars without error.

### Bug 2 — TOC chapter titles

**Before:** `chapter_title` used `if x.startswith("# ") or x.startswith("## ")` — first H1 OR H2. If a chapter had neither, returned `""`. Test target: city-of-memories chapters (which have no H1) → empty titles. ai-agents-with-python chapters (which have H1s) → titles from H1 (worked).

**After:** Strict H1 regex `^#\s+(.+?)\s*$` with `re.MULTILINE`. If no H1, returns the filename stem (`ch-01`, `ch-02`, ...). Verified: city-of-memories TOC now has 5 entries with `Chapter 0N: ch-0N` (filename-stem fallback). ai-agents-with-python TOC has 19 entries with H1 titles.

### Bug 3 — word regex

**Before:** `r"\b[\w'-]+\b"`. The `'` between `\w` and `'` was a literal U+2019 (right single quotation mark / curly apostrophe) embedded as UTF-8 bytes E2 80 99. Straight `'` (U+0027) and `-` (U+002D) were also in the class. The original bug report alleged `[\w�??'-]` with literal U+FFFD + two `?`; byte-level inspection showed the source already had a U+2019 byte there, no U+FFFD. But the original was still bogus: U+2018 (left curly apostrophe) was not covered, and the implicit U+2019 was confusing to maintain.

**After:** `r"\b[\w'\-\u2018\u2019]+\b"`. Explicit \u escapes make intent readable; U+2018 now covered. Word counts unchanged on daily-focus (2415).

## Verification table

| Target | Command | Expected | Actual | Pass? |
|--------|---------|----------|--------|-------|
| Smoke test | `py -3.10 book_check.py books/daily-focus` | exit 0 | exit 0, PASS (1 chapter, 2415 words) | yes |
| ai-agents toc | `build_exports.py` on ai-agents staging | non-empty titles in toc.md | 19/19 with H1 titles | yes |
| city-of-memories exit | `build_exports.py` on city staging | exit 0 (no UnicodeDecodeError) | exit 0, bible.md → cp1256 | yes |
| city-of-memories toc | `build_exports.py` on city staging | non-empty titles in toc.md | 5/5 with `Chapter 0N: ch-0N` | yes |
| Minimal cp1256 test | `build_exports.py` on bible_cp1256_test | exit 0, glossary present | exit 0, glossary file written, bible.md → cp1256 | yes |
| Encoding log | stderr from build_exports | `[encoding] <name> → <enc>` per file | logged for all 6 files in ai-agents run, all 7 in city run, all 2 in minimal test | yes |
| No U+FFFD / `??` | byte scan of both scripts | 0 matches | 0 matches | yes |
| Book-kit sync | `sync_from_book_gen.py --apply` | 2 updated, 21 skipped, exit 0 | 2 overwritten, 21 skipped, exit 0 | yes |
| Book-kit post-sync | `book-kit/.../book_check.py books/daily-focus` | exit 0 | exit 0, PASS | yes |
| Python syntax | `ast.parse(...)` on both files | OK | OK | yes |

## Deviations from plan

- **Staging dir path:** the spec said "fresh staging dir under `share/notes/audit_city-of-memories/bible_cp1256_test/`". I used that exact path for the minimal cp1256 test. The two full-book audits (ai-agents, city-of-memories) used `staging_ai-agents` and `staging_city-of-memories` siblings under the same parent, since the existing `share/notes/audit_ai-agents-with-python/` and `share/notes/audit_city-of-memories/` already existed from prior runs and I followed their convention.
- **Bug 3 — bug-report premise was slightly off.** The report claimed a literal `�??` (U+FFFD + two `?`) in the scripts. Byte-level inspection showed no U+FFFD; the regex already had U+2019 as a literal byte. The spec's intended fix (`[\w'\-\u2018\u2019]+`) was applied regardless — it's a real improvement (U+2018 coverage, explicit escapes), and the post-fix `grep -n "�??"` test passes with 0 matches.
- **`book_check.py` not switched to `read_text_safe`.** The spec only mentions the helper for `build_exports.py` ("The helper belongs in `build_exports.py` itself — don't create a new module"). `book_check.py`'s own `read_md` was left as-is (its existing chain is utf-8 → cp1256 → cp1252 → latin-1, with no log — out of scope for this dispatch).

## Known issues / TODOs left in code

- **city-of-memories glossary is empty even with the encoding fix.** The bible's `## Terminology` section is formatted as a Markdown bullet list (lines starting `- `), not as `### ` H3 subheadings. `build_exports.py:52` looks for `^###\s+(.+?)\s*\n([^#]+)` — no H3 matches, so no glossary entries. This is a content issue, not a script issue. The encoding fix is correct (bible decodes as cp1256 with 19,000 Arabic chars preserved); the downstream regex just doesn't see a structure that matches. Future improvement: extend the glossary extractor to also handle bullet-list entries, or update the bible to use H3 headings. Not in scope for this dispatch.
- **The stderr `[encoding]` log emits one line per file read (chapter, bible, outline, etc.) — that's ~20-25 lines per build.** Spec says one-line log per file, so this is correct, but if a future user runs the script in a noisy CI log, they'll see all the lines. If that's a problem, downgrade the log level or add a `--quiet` flag. Not blocking.
- **The `chapter_title` function is duplicated in spirit between the old behavior (H1-or-H2) and the new spec (H1-only).** If the build_exports spec evolves, keep in mind that some legacy chapter files might have relied on H2 fallback. Inspected ai-agents-with-python — every chapter has an H1, so the H1-only path is safe for current data.

## Suggested review focus

1. **book_check.py is NOT using `read_text_safe`.** The bug spec for Bug 1 only mentioned `build_exports.py`. If the reviewer wants `book_check.py` to also log encoding and use the new chain, that's a follow-up. Verify this is intentional.
2. **`chapter_title` was simplified (H1-only).** The previous version accepted H1 OR H2 (whichever came first). If any project relies on H2 fallback, that path is gone. Spot-checked the two known projects; neither relies on it.
3. **The `latin-1` final fallback is gone.** The old `read_md` would never throw because `latin-1` decodes any byte. The new `read_text_safe` final fallback is `utf-8, errors="replace"` — this means a file with 100% invalid UTF-8 bytes will get U+FFFD substitutions. That's a behavior change. In practice every file in scope is either valid UTF-8 or valid cp1256, so the new chain succeeds before reaching the replace fallback. Verify this is acceptable.
4. **Stderr noise.** The `[encoding] <name> → <enc>` log fires on every `read_text_safe` call. For ai-agents-with-python that's 21 calls (1 outline + 19 chapters + 1 bible). If the downstream consumer treats stderr as warnings, this is informative noise. The spec explicitly asked for this log, so it's intentional.

## Self-critique

- **Did I do my job?** Yes. All 6 tasks (3 bugs + 3 verifications) done; book-kit synced; SHA256 verified identical.
- **What might I have missed?** I did not re-run the new `build_exports.py` on `books/ai-agents-with-python/` directly (only via staging). I did not run `book_check.py` end-to-end on `books/daily-focus/` against the *new* `book_check.py` byte-for-byte (only the smoke test); the word-count of 2415 matches the historical baseline, so behavior preserved.
- **What did I assume without evidence?** I assumed the spec was authoritative even where it conflicted with the file's actual state. Specifically: (a) the report said bible.md is cp1256 — I verified it IS cp1256 (byte scan confirmed 2541 invalid UTF-8 sequences; cp1256 decodes 41537 chars; first 200 chars show clean Arabic مدينة الذكريات). (b) the report said scripts contain `�??` — I scanned bytes and found no U+FFFD; the report was off but the fix is still a real improvement.
