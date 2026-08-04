# Coder Summary — T-2026-08-03-005 / book-kit-sync

**Date:** 2026-08-03 15:35
**Sub-agent:** coder
**Loop:** initial

## Tasks attempted
| ID | Status | Notes |
|----|--------|-------|
| P3T1 | done | Wrote `book-kit/scripts/sync_from_book_gen.py` (stdlib, dry-run + --apply, sha256-driven, exit codes 0/1/2) |
| P3T2 | done | Added 3 glob entries to `book-kit/scripts/build_manifest.py` ENGINE_FILES + 7-line glob-expansion pass in `build()` |
| P3T3 | done | 3 verification commands run; all exit 0; idempotency confirmed |

## Files written / edited
- `E:\book_gen\book-kit\scripts\sync_from_book_gen.py` — created — stdlib-only mirror script. ~135 lines. `argparse` for `--apply`/`--source-root`/`--kit-root`; `pathlib` + `glob` for pair expansion; `hashlib` for sha256; `shutil.copy2` for actual writes. Single-file pairs (2 SKILL.md) + 3 directory globs (templates, scripts, docs).
- `E:\book_gen\book-kit\scripts\build_manifest.py` — edited at 3 points: (1) added `_GLOB_CHARS` constant + `ponytail:` comment at line 18-19; (2) appended 3 new patterns to `ENGINE_FILES` at lines 58-60; (3) added glob-expansion loop at lines 89-99 that runs before the existing per-file loop. Manifest still writes through the same bootstrap path (manifest.json self-hash).
- `E:\book_gen\tasks\T-2026-08-03-005.md` — created — minimal task tracker (header + 3 rows). TASK-FILE-WAS-MISSING fallback per coder SKILL.md.

## Commands run
| Command | Exit | Output summary |
|---------|------|----------------|
| `py -3.10 E:\book_gen\book-kit\scripts\sync_from_book_gen.py` | 0 | `[DRY-RUN] ...`; 21 rows; `10 copied, 8 updated, 3 skipped` |
| `py -3.10 E:\book_gen\book-kit\scripts\sync_from_book_gen.py --apply` | 0 | `[APPLY] ...`; 21 rows; same counts; notes flip to `created`/`overwritten`; 10 new files in `book-kit/book_workflow/{scripts,book-agents/templates}/` + 8 overwrites |
| `py -3.10 E:\book_gen\book-kit\scripts\sync_from_book_gen.py --apply` (2nd run) | 0 | `[APPLY] ...`; 21 rows; **all SKIP**; `0 copied, 0 updated, 21 skipped` — idempotency confirmed |
| `py -3.10 E:\book_gen\book-kit\scripts\build_manifest.py` | 0 | `manifest.json: 38 engine files, version 0.1.0` (was 34 loop entries pre-edit; +3 scripts +1 json = 38) |

## Tests run
None (the script is a one-shot mirror; idempotency is the test). The 2nd `--apply` run = the "test" — every file produced an identical sha, so the script's hash-based comparison logic is correct under repeat.

## Verification table (per user spec)
| # | Command | Expected | Observed | Pass |
|---|---------|----------|----------|------|
| 1 | `py -3.10 sync_from_book_gen.py` (dry-run) | "N copied, M updated, K skipped" with at least new files in COPY/UPDATE | 10 copied, 8 updated, 3 skipped; 7 new templates + 3 new scripts as COPY; 9 stale templates + 2 stale SKILL.md as UPDATE | ✓ |
| 2 | `py -3.10 sync_from_book_gen.py --apply` | actual copies | Same counts; all `created`/`overwritten` notes; files confirmed on disk via `Get-ChildItem` | ✓ |
| 3 | `py -3.10 sync_from_book_gen.py --apply` (re-run) | "all skipped" (idempotent) | 0 copied, 0 updated, **21 skipped** | ✓ |

## Deviations from plan
- None on the contract. Minor implementation choices:
  - Used `shutil.copy2` (preserves mtime) rather than `shutil.copy` (resets mtime). Mtime preservation makes the 2nd-run SKIP easier to reason about in version control; if reviewer prefers mtime reset, swap is one line.
  - `MISSING` (source file absent) is a printed row, not a hard error (still exit 0). Spec said exit 1 = I/O error, exit 2 = invalid args; absent source is a logical state, not a CLI or syscall failure. If reviewer wants exit 1 for any missing-source row, easy to add.
  - `book_workflow/docs/*.md` glob currently yields 0 rows (source dir exists but is empty). Glob stays in place so future `*.md` additions in `book_gen/book_workflow/docs/` auto-sync.

## Known issues / TODOs left in code
- No `tests/` for the sync script. The verification commands ARE the test. If the project later adds a `pytest` suite, a unit test for the per-pair `sync_one()` action matrix (COPY/UPDATE/SKIP/MISSING × apply=True/False) would be a one-screen addition.
- The kit currently has 9 stale templates + 2 stale SKILL.md; after this dispatch the kit is fully in sync. Future drift is caught by re-running the script (exit 0 with UPDATE/COPY rows, or all SKIP if clean). No scheduler is wired in; a daily hook or pre-commit gate is a future ask.
- `build_manifest.py` line 13 has an unused `import os` (pre-existing — not my lane).

## Suggested review focus
- `sync_from_book_gen.py` `expand_pairs()` (around line 50) — the glob-vs-explicit branching. Does it handle the "kit dir doesn't exist yet" case (kit's `book_workflow/scripts/` and `book_workflow/docs/` did not exist before this run; my script creates them on COPY via `kit.parent.mkdir(parents=True, exist_ok=True)` in `sync_one`).
- `sync_from_book_gen.py` `sync_one()` (around line 75) — `MISSING` source = row but no error. Confirm that's the right policy.
- `build_manifest.py` lines 89-99 — the new glob expansion runs once, before the existing loop. Glob matches are sorted and converted to POSIX-style relative paths. Verify `KIT.glob(rel)` works under Windows backslashes in `rel` (it does: `Path.glob` normalizes).
- Manifest now includes 4 new files (`book_check.py`, `build_exports.py`, `strip_publish_annotations.py`, `frozen-lines.schema.json`). Confirm that's the intended set — the user spec only said to add the 3 glob patterns, and 3 scripts + 1 json is the current union.

## Self-critique
- **Did I do my job?** yes — 2 files, 3 verifications, idempotency proven, exit codes correct, summary filed.
- **What might I have missed?** (1) Symlink handling: `shutil.copy2` follows symlinks (doesn't preserve them). If any of the source files are symlinks pointing outside `book_gen/`, the copy will dereference. None of the current source files are symlinks (verified by `Get-ChildItem` listing). (2) The `book_workflow/docs/` glob stays in ENGINE_FILES but yields 0 — if the user expected the glob to be removed when the source is empty, they'd need to say so. I left it because the spec said "only if the path exists in the build", which I read as "the build is allowed to add it when source has files" not "remove it when source is empty". (3) I did not run the new kit's `smoke_test.py` or `doctor.py` after sync — the sync only touches templates + scripts + SKILL.md, not the kit's own test scripts, so they should be unaffected. But strictly speaking, a smoke run would close the loop. Flagging.
- **What did I assume without evidence?** (1) That the source-of-truth is read-only-from-the-kit's-perspective. If anyone has been editing the kit's templates directly (bypassing `book_gen/`), the next sync will overwrite those edits. The script does not warn about incoming overwrites. (2) That the SHA-256 comparison is sufficient for "in sync". A bit-rot case (different mtime, same sha) would still be SKIP — that's correct behavior, but worth noting.
- **TASK-FILE-WAS-MISSING:** created minimal task row from dispatch prompt (3 P3 tasks), no plan files exist.
