# Book Kit Changelog

All notable changes to the Book Kit. Newest on top.

The Book Kit is the portable book-gen deliverable in this repo. It bundles
the agents-manager controller + book-gen specialization + 21 scripts + 19
templates + tests + docs. Native books AND translations AND media (Phase 9)
ship first-class.

## v1.3.0 — book2media Phase 9 (2026-08-12)

The Phase 9 "book2media" lane is now in the kit. Master loads
`agents_manager/book2media-orchestrator/SKILL.md` and dispatches a
sub-pipeline that produces 5 media products per book per locale
(audiobook M4B + horizontal video + 60-90s trailer + reel × 3 platforms).
Validated end-to-end against `books/daily-focus/ch-01.md` in both English
and Arabic; 8 valid artifacts on disk after smoke.

### What's new

1. **Phase 9 orchestrator + manifest schema** —
   `agents_manager/book2media-orchestrator/SKILL.md` (8 phases:
   1 Orchestrator+Manifest, 2a TTS-Kokoro, 2b TTS-edge-tts,
   3 Caption, 4a Audiobook, 4b Video, 5 Smoke, 6 Docs).
   `am-assets` gains a `## Media-manifest lane` section
   (4 branches: Mode 1, Mode 2 deferred, use-as-is, generate-cover).
   `am-review` gains a `## Locale-correctness gate` section.
   `book-gen-orchestrator/SKILL.md:348` amended to permit
   `book2media-orchestrator` at Phase 9 only.

2. **13 new scripts in `book-kit/book_workflow/scripts/`:**
   - `voices.py` (14.4 KB) — per-locale TTS voice registry, three-tier resolution
   - `media_tts.py` (28.7 KB) — H2-driven chunker + per-locale TTS dispatcher
   - `check_whisper_deps.py` (10.9 KB) — faster-whisper dependency check
   - `transcribe_chapter.py` (14.0 KB) — faster-whisper ASR with word timestamps
   - `align_srt.py` (23.0 KB) — difflib alignment + `normalize_arabic()` + `--drift-floor`
   - `srt_to_ass.py` (9.1 KB) — pysubs2 SRT to ASS with Amiri RTL
   - `install_amiri.py` (9.5 KB) — Amiri font installer
   - `assemble_audiobook.py` (44.4 KB) — M4B with two-pass loudnorm + voice-policy + self-check
   - `ffmpeg_zoompan.py` (7.4 KB) — shared Ken Burns library
   - `assemble_video_horizontal.py` (27.5 KB) — Mode-1 1920x1080 video
   - `assemble_video_trailer.py` (31.8 KB) — 60-90s teaser
   - `assemble_reel.py` (35.7 KB) — 3-platform 1080x1920 with serial fan-out
   - `media_manifest.py` (already shipped, 29.4 KB) — schema validator + generator
3. **2 new shared library files in `book-kit/book_workflow/lib/`:**
   - `tts_events.py` (18.5 KB) — TTS event-format helpers
   - `errors.py` (6.5 KB) — `MediaPipelineError` + `HINTS` dict (6 keys)
4. **321 pytest tests pass / 1 xfail / 0 fail** across the full book-kit
   suite (was 252/1/0 in v1.2.0). 12 new test files added; net +69 tests.
5. **TTS lane:** Kokoro 0.9.4 for English (default voice `af_heart`),
   edge-tts 7.2.x for Arabic (default voice `ar-SA-HamedNeural`).
   Voice field is per-product in the manifest; empty-string `voice: ""`
   is rejected (use `skip: true` to drop a product).
6. **Caption lane:** faster-whisper 1.2.1 (model `large-v3` for ar,
   `small` for en) + pysubs2 1.8.1 + Amiri font family (5 weights).
   Per-locale model selection via `MODEL_FOR_LOCALE` in
   `transcribe_chapter.py:78`.
7. **Audiobook lane:** M4B with two-pass loudnorm (I=-19 LUFS, TP=-2 dBTP,
   LRA=11), embedded cover PNG, ID3 metadata, ISO 639-2 language tags
   (`en -> eng`, `ar -> ara`), voice-policy enforcement, `--self-check`
   chapter-count validation.
8. **Video lane:** 4x supersample Ken Burns (`scale=8000:-1` ->
   `zoompan` -> `scale=1920:1080`) kills judder. Libass HarfBuzz shaping
   on every burn-in path (`ass=...:shaping=complex`).
9. **Reel lane:** two-step serial architecture (shared base render +
   per-platform ffmpeg applies loudnorm + ASS alignment + vignette).
   Peak memory bounded by ONE libx264 encoder at a time.
   4:2:0 chroma (`yuv420p`) for fan-out safety.
10. **Three-tier provider resolution (enforced):** per-book
    `media-locale-manifest.json` > global `providers.yaml` > built-in
    registry. `media_manifest.py validate` exits 2 on any empty-string
    voice.
11. **Smoke-tested on `books/daily-focus/ch-01.md`:** 8/8 artifacts
    ffprobe-verified (M4B EN+AR, horizontal EN+AR, reel EN+AR, plus
    direct-ffmpeg EN+AR). 60s clip level; full 700s chapter at 4x
    supersample = ~131 min estimated wall-clock. Documented escape
    hatches: `scale_mult=2` (~4x faster, slight quality loss), NVENC
    (~5-10x faster on Nvidia GPUs).
12. **TOOLKIT.md** — Phase 9 Pipeline map corrected (was 8 placeholder
    names from the v1.2.0-era plan), 12 new tool catalog sections added
    (TTS lane, Caption lane, ffmpeg assembly lane, shared lib).
    Total tool catalog sections: 23.
13. **SCRIPTS.md** — per-tool CLI entries for all 13 new scripts +
    2 lib files. Each entry: invocation shape, flags, behavior,
    exit codes, hardening notes. ~24 KB added.
14. **CLAUDE.md** — Phase 9 dispatch rule added; `am-assets` row in
    per-agent output-paths table; book2media reading-order step.
15. **MEDIA.md** — new narrative doc covering "how do I" flows:
    add a new locale, change per-locale voice, skip a product,
    regenerate one product, plan full-book timing.

### Known limits (deferred to v1.3.1 polish)

- **W1** `check_whisper_deps.py:283` defaults `--cache-dir` to
  `~/.cache/huggingface` (notebook-leak risk). Trivial fix.
- **W3** `install_amiri.py` has no SHA256SUMS verification.
- **W4** SyntaxWarning on `media_manifest.py:46`.
- **F4** Locale-mismatch threshold is 0.30 in code, 0.50 in dispatch
  (doc drift). Either raise to 0.50 or expose `--locale-mismatch-ratio`.
- **F5** Escape hatches (`scale_mult`, `VCODEC`, `VPRESET`) are
  plumbing-level constants. Phase 6 must expose `--scale-mult`,
  `--vcodec`, `--vpreset` so they're user-reachable. 700s chapter
  render is not viable without these or switching to NVENC.
- **LOW** Reel per-platform single-pass loudnorm (was acceptable per
  plan; two-pass is the v1.3.1 target).
- **HINTS** in `lib/errors.py` is a module-level mutable dict; freeze
  with `MappingProxyType` or document as const before exposing it
  as a public API.

### Reference implementation

`books/daily-focus-smoke/exports/` has 8 valid media artifacts:
- `daily-focus-smoke-en.m4b` (11.44 MB, 1 chapter, 702s, AAC mono 44.1kHz)
- `daily-focus-smoke-ar.m4b` (13.43 MB, 1 chapter, 862s, AAC mono 44.1kHz)
- `horizontal-en-clip.mp4` (1.08 MB, 1920x1080 h264, 61.57s)
- `horizontal-ar-clip.mp4` (1.02 MB, 1920x1080 h264, 61.50s)
- `reel-en-clip-yt.mp4`, `reel-en-clip-ig.mp4`, `reel-en-clip-tiktok.mp4`
  (each 2.9 MB, 1080x1920 h264 yuv420p, 61.57s)
- `reel-test-direct.mp4` (2.37 MB, direct ffmpeg, 1080x1920)

Smoke report: `share/notes/05_smoke_T-2026-08-10-001.md`.
Phase 5 review: `share/reports/04_review_T-2026-08-10-001_phase5.md` (PASS_WITH_WARN).

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
