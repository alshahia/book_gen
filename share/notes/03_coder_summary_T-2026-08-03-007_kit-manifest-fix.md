# Coder Summary — T-2026-08-03-007 / kit-manifest-fix

**Date:** 2026-08-03
**Sub-agent:** coder
**Loop:** initial
**Task:** Fix `book-kit/scripts/build_manifest.py` ENGINE_FILES allowlist so 6 PR-2 templates are picked up by the `*.md` glob.

## Tasks attempted

| ID | Status | Notes |
|----|--------|-------|
| T-2026-08-03-007 | done | Replaced 9 explicit template entries with `book_workflow/book-agents/templates/*.md` glob; manifest now reports 46 files; ZIP rebuilt with 16 templates. |

## Files written / edited

- `book-kit/scripts/build_manifest.py:49` — **edited** — ENGINE_FILES allowlist. Removed 9 explicit `book_workflow/book-agents/templates/*.md` entries (old lines 49-57); added `"book_workflow/book-agents/templates/*.md"` glob after the `*.json` glob (new line 52). Final allowlist line block (lines 49-52):
  ```
  "book_workflow/scripts/*.py",
  "book_workflow/docs/*.md",
  "book_workflow/book-agents/templates/*.json",
  "book_workflow/book-agents/templates/*.md",
  ```
- `book-kit/manifest.json` — **regenerated** by `build_manifest.py`. 46 engine files (was 40). SHA256 of `scripts/build_manifest.py` entry will reflect the new content (`5c1d1656...` → see new manifest).
- `dist/book-kit-0.1.0.zip` — **rebuilt** by `build_zip.py`. 51 entries (46 engine + 4 `.gitkeep` + 1 `START_HERE.md`).

## Before vs after allowlist (ENGINE_FILES lines 49-57)

**Before (9 explicit + 1 glob = 10 entries covering 10 files):**
```
    "book_workflow/book-agents/templates/intake.md",
    "book_workflow/book-agents/templates/skeleton.md",
    "book_workflow/book-agents/templates/research-log.md",
    "book_workflow/book-agents/templates/outline.md",
    "book_workflow/book-agents/templates/style-guide.md",
    "book_workflow/book-agents/templates/writing-plan.md",
    "book_workflow/book-agents/templates/bible.md",
    "book_workflow/book-agents/templates/ledger.md",
    "book_workflow/book-agents/templates/decisions-log.md",
    "book_workflow/scripts/*.py",
    "book_workflow/docs/*.md",
    "book_workflow/book-agents/templates/*.json",
```

**After (1 md glob + 1 json glob = 2 entries covering 16 files):**
```
    "book_workflow/scripts/*.py",
    "book_workflow/docs/*.md",
    "book_workflow/book-agents/templates/*.json",
    "book_workflow/book-agents/templates/*.md",
```

The 6 missing PR-2 templates (`operational-caps.md`, `preface.md`, `toc.md`, `glossary.md`, `exports-readme.md`, `tashkeel-policy.md`) are now picked up by the `*.md` glob.

## Commands run

- `py -3.10 book-kit/scripts/build_manifest.py` — exit 0. **Output: `manifest.json: 46 engine files, version 0.1.0`** (was 40, +6 templates).
- `py -3.10 book-kit/scripts/build_zip.py` — exit 0. **Output: `wrote E:\book_gen\dist\book-kit-0.1.0.zip (51 entries, version 0.1.0)`**.
- `Expand-Archive ... -DestinationPath ...\kit-verify` — exit 0. Extracted to `E:\Users\AHMADM~1\AppData\Local\Temp\opencode\kit-verify`.
- `Get-FileHash -Algorithm SHA256` against manifest entries vs disk for the 3 patched scripts.

## Tests run

None. Task is a manifest-allowlist edit; no test framework exists for this script. Self-verification via re-running the build script + cross-checking SHAs and ZIP contents.

## Verification table

| Check | Expected | Actual | Result |
|---|---|---|---|
| `build_manifest.py` exit | 0 | 0 | PASS |
| Manifest engine_files count | 46 | 46 | PASS |
| `book_workflow/book-agents/templates/` entries | 16 (15 .md + 1 .json) | 16 | PASS |
| New templates included | operational-caps, preface, toc, glossary, exports-readme, tashkeel-policy | all 6 present | PASS |
| `book_workflow/scripts/` entries | 3 | 3 | PASS |
| `book_workflow/docs/` entries | 2 | 2 | PASS |
| SHA256 book_check.py match (manifest vs disk) | match | match | PASS |
| SHA256 build_exports.py match (manifest vs disk) | match | match | PASS |
| SHA256 strip_publish_annotations.py match (manifest vs disk) | match | match | PASS |
| `build_zip.py` exit | 0 | 0 | PASS |
| ZIP path | `E:\book_gen\dist\book-kit-0.1.0.zip` | as expected | PASS |
| ZIP engine entries (post-extract) | 46 | 46 | PASS |
| ZIP template files in `book-kit/book_workflow/book-agents/templates/` | 16 | 16 | PASS |
| ZIP docs in `book-kit/book_workflow/docs/` | 2 | 2 | PASS |
| ZIP scripts in `book-kit/book_workflow/scripts/` | 3 | 3 | PASS |

**Script SHA match details (full hex):**

| Path | Manifest SHA256 | Disk SHA256 | Match |
|---|---|---|---|
| `book_workflow/scripts/book_check.py` | `6fa0dc42af41f692e5e675e5e4c9bf381c2e289b509776eaf8d61a8ac64e6277` | `6FA0DC42AF41F692E5E675E5E4C9BF381C2E289B509776EAF8D61A8AC64E6277` | YES |
| `book_workflow/scripts/build_exports.py` | `7babc2ad785d89683d46d92c3f14977b558d38bf6fc7eee24991375f85e4750f` | `7BABC2AD785D89683D46D92C3F14977B558D38BF6FC7EEE24991375F85E4750F` | YES |
| `book_workflow/scripts/strip_publish_annotations.py` | `38fbb73f7d58fa7d40ff8cdcc3e5ea481517a7ff74d02c4406b813b6cb562f3e` | `38FBB73F7D58FA7D40FF8CDCC3E5EA481517A7FF74D02C4406B813B6CB562F3E` | YES |

## Deviations from plan

- **Task prompt mentioned a possible second file at `book_workflow/scripts/build_manifest.py`.** Verified there is no such file — `E:\book_gen\book_workflow\scripts\` contains only `book_check.py`, `build_exports.py`, `strip_publish_annotations.py`. The only `build_manifest.py` is `E:\book_gen\book-kit\scripts\build_manifest.py`, which is the source of truth for the sync mirror. No second file needed editing.

## Known issues / TODOs left in code

- **None.** The task is a 2-line allowlist edit; all scope items completed.

## Suggested review focus

- `book-kit/scripts/build_manifest.py:49-52` — confirm the final 4-line block has the correct glob order: `*.py` → `*.md` (docs) → `*.json` (templates) → `*.md` (templates, new). The glob expansion is order-independent (KIT.glob sort), but readability is smoother if both `templates/` globs sit together.
- `book-kit/manifest.json` — confirm the `scripts/build_manifest.py` entry now has a new SHA256 (the old `5c1d1656...` was for the un-patched file; re-run produced the new SHA).

## Self-critique

- **Did I do my job?** Yes. 2-line edit, regenerated manifest, rebuilt ZIP, verified all 16 templates + 3 scripts + 2 docs, SHA-matched the 3 patched scripts.
- **What might I have missed?** The task spec said "46 files inside" the ZIP at step 4. Actual ZIP has 51 entries (46 engine + 4 `.gitkeep` + 1 `START_HERE.md`). The 46 number is the manifest's engine_files count, not the ZIP entry count — `build_zip.py` always adds the 4 `.gitkeep` shims and the `START_HERE.md` pointer regardless of manifest size. This is pre-existing behavior, not a regression.
- **What did I assume without evidence?** I assumed the task's mention of a mirror `book_workflow/scripts/build_manifest.py` was a mis-reference (the file does not exist). Verified directory listing before editing.
- **Memory written:** none (no durable insight — this is a one-off glob fix any future agent can derive in 30 seconds from the file structure).
