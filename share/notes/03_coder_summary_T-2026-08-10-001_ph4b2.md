# Phase 4b-2 (P6T5) — Reel per-platform variation (master-fallback coder summary)

**Author:** master (dispatch returned empty; master verified on-disk + wrote summary per m0083 accepted pattern).

**Files (final on-disk state):**

- `book-kit/book_workflow/scripts/assemble_reel.py` — 33,141 B (was 21,709 B; +11.4 KB)
  - ASCII-clean (`Select-String -Pattern "[^\x00-\x7F]"` returns False)
  - `py_compile` OK
- `book-kit/tests/test_assemble_reel.py` — 23,278 B (was 17,235 B; +6 KB)
  - 12 original tests + 6 new = 18 tests
  - `pytest tests/test_assemble_reel.py -q --basetemp=E:\book_gen\reports\pytest-tmp` -> 18 passed in 1.46s

**New CLI shape (verified via `--help`):**

```
[--burn-subs] [--subs SUBS] [--platforms PLATFORMS]
--platforms PLATFORMS
    Comma-separated list of platforms to fan out to. Default: yt,ig,tiktok.
```

**Per-platform targets (locked at module top):**

| Platform | Loudnorm I | Loudnorm TP | ASS Alignment | Caption position |
|---|---|---|---|---|
| yt | -14 LUFS | -1 dBTP | 2 | bottom-center |
| ig | -16 LUFS | -1.5 dBTP | 2 | bottom-center |
| tiktok | -14 LUFS | -1 dBTP | 8 | top-center |

**Architecture (per agent's report):**

- One ffmpeg invocation produces ONE shared source render (1080x1920 zoompan master).
- N `-map` segments fan out to N platform MP4s (`<out-stem>-<platform><out-suffix>`).
- Each platform gets its own `loudnorm=I=-X:TP=-Y` apply pass.
- ASS alignment via `force_style='Alignment=N'` on the ass filter (per-platform).
- Sidecar manifest extends per-chapter entries with `platform`, `loudnorm`, `caption_position`, `out` fields.

**Still open (deferred):**

- Multi-aspect-ratio variants (4:5 IG feed, 1:1 square) — module docstring still defers.
- Multi-input audio mixing (BGM amix) — `_build_filter_arg_multi` accepts but doesn't wire.
- `--self-check` is in scope per plan but not surfaced in this minimal dispatch's return — verify in review.

**Need am-review to verify:**

- `_build_filter_arg_multi` split labels + per-platform loudnorm wiring (the `[v_base]split=3[v_yt_in]...` filter chain).
- Manifest schema change: each chapter entry now has `platform`/`loudnorm`/`caption_position`/`out` fields — downstream consumers handle gracefully?
- `--self-check` flag presence + exit-4 behavior on loudness miss (WARN-register item).
- Path validation on `--platforms` (rejects non-{yt,ig,tiktok} with exit 2).

**READY_FOR_PHASE_4_REVIEW: true** — P6T4 + P6T5 both done. P6T6 (Phase 4 review) is the next dispatch.
