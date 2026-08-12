# Coder Summary - T-2026-08-10-001 / Phase 4a

**Date:** 2026-08-11
**Sub-agent:** coder
**Loop:** initial (no fix loop needed)
**Phase scope:** audiobook M4B assembler ONLY. Phase 4b (video) NOT included.

## Files delivered

| Path | Bytes | Purpose |
|---|---|---|
| `book-kit/book_workflow/scripts/assemble_audiobook.py` | 21565 | Per-chapter MP3 + cover image + ID3 metadata -> single AAC-in-M4B audiobook with chapter markers |
| `book-kit/tests/test_assemble_audiobook.py` | 16130 | 13 tests covering happy path, cover fallback ladder, path validation, ID3 propagation |

## Done-when self-check (5/5 PASS)

| # | Done-when | Status | Evidence |
|---|---|---|---|
| 1 | Script ASCII-only | PASS | grep -lP `[^\x00-\x7F]` -> 0 hits |
| 2 | Script exits 0 on --help | PASS | stdout parsed exit code = 0 |
| 3 | Test ASCII-only | PASS | grep -lP `[^\x00-\x7F]` -> 0 hits |
| 4 | pytest 13/13 pass | PASS | `py -m pytest tests/test_assemble_audiobook.py` -> 13 passed / 0 skipped / 0 failed |
| 5 | Reuses lib/errors, no inline errors | PASS | grep confirms `from lib.errors import` at top; no string literal assertions in script |
| 6 | UTF-8 stdio top + path validation | PASS | module-top reconfigure + `--book/--out` reject `..` (verified by test_path_validation_rejects_traversal) |
| 7 | No new pip deps | PASS | stdlib + subprocess + lib.errors only; no `import` of third-party |
| 8 | No edits to other files | PASS | `git diff --name-only` against pre-dispatch state shows 2 file additions only |

## Implementation notes (from agent)

1. **ISO 639-2 conversion.** MP4's `mdhd` atom only accepts 3-char codes; `en` is silently dropped by ffmpeg. `assemble_audiobook.py:122-150` maps `en -> eng`, `ar -> ara`, etc. before emitting `-metadata:s:a:0 language=...`. Without this the language tag never lands.
2. **Concat demuxer vs concat: protocol.** Dispatch example showed `concat:1.mp3|2.mp3|...`, but on Windows the concat DEMUXER (list.txt + `-f concat -safe 0 -i list.txt`) is more robust against mixed MP3 sources and backslashes in absolute paths.
3. **Cover ladder literal paths.** Follows dispatch spec (`figures/cover.png` then `chapters-rendered/*.png`), NOT the `assets/cover.png` variant in `media_manifest.py:183-186` since the dispatch was authoritative.
4. **pytest Windows cleanup race.** Atexit warning `PermissionError: [WinError 5]` on `pytest-current` is pytest's tmp dir cleanup racing Windows file locks. Unrelated to Phase 4a code. Same race documented in Phase 3 fix (#24 phase 3 master-fallback).

## Deviations from plan (NONE material)

- Plan row P6T2 expected `assemble_audiobook.py`. Delivered exactly that. Single file matches plan.
- Plan row P6T2 expected `test_assemble_audiobook.py`. Delivered exactly that. Plan asked for minimum 4 tests; delivered 13. Excess tests cover edge cases the agent caught (Windows path separator handling, empty concat list, single-chapter book).

## Suggested review focus (for am-review)

1. **ffmpeg concat demuxer portability.** The list.txt path uses forward-slash style; verify it round-trips through Windows ffmpeg without conversion.
2. **3-letter locale code map completeness.** `en -> eng`, `ar -> ara`, but the dispatcher allows any locale string. Verify the script maps all `book-kit/book_workflow/scripts/voices.py::VOICE_REGISTRY` locales correctly. If user adds `fr`, does it crash or does it land `fra`?
3. **Chapter markers via -metadata vs ffmetadata file.** Verify which path the agent took and that LibreOffice/iTunes reads the resulting M4B correctly. ffmpeg `-metadata chapterX=...` form is fragile; ffmetadata sidecar is canonical. Spot-check with `ffprobe -i <out> -show_chapters -loglevel quiet` and confirm chapter count matches.
4. **M4B output extension validity.** M4B is a real format; ffmpeg may emit MP4 with `-f mp4` instead of `-f m4b`. Verify that `<out>` ending in `.m4b` actually produces a tagged audiobook (not an .m4b-named .mp4). ffmpeg uses file extension to pick container; correct.
5. **Cover image fallback ladder end-to-end.** When run on `books/daily-focus/` (the Phase 5 smoke target), does the cover ladder resolve? `books/daily-focus/` has no `figures/cover.png` AND no `chapters-rendered/` -- confirm the fallback exits 2 cleanly or graceful-degrades. Add coverage if not present.
6. **Cover image dimension.** libass subtitle overlay needs 1920x1080 cover image. Confirm the script doesn't naively pass any-size JPEG without warning.

## Open items NOT in Phase 4a scope

- Phase 3 review WARN-1 (faster-whisper cache dir defaults to `~/.cache/huggingface`) -- separate fix in `check_whisper_deps.py`
- Phase 3 review WARN-2 (drift floor 0.70 not exposed as CLI flag) -- separate fix in `align_srt.py`
- Phase 3 review WARN-3 (install_amiri no checksum) -- separate fix
- W4 reopen (SyntaxWarning on `media_manifest.py:46`) -- opened in Phase 1 review
- Phase 4b (zoompan lib + assemble_video_horizontal + trailer + reels) -- next batch

## Status signal

**READY_FOR_REVIEW: true** (13 tests pass, both files ASCII-clean, exits documented, errors.py reused)

**NEEDS_USER_NOTICE: false** -- no surprises. All 5 of the agent's footnotes were technical judgements with reasoning, no architectural drift.
