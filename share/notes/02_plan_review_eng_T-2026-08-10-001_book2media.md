# Plan Review — Engineering Angle — T-2026-08-10-001 (book2media)

**Date:** 2026-08-10
**Sub-agent:** planning
**Angle:** plan-eng (architecture, data flow, edge cases, tests, performance)
**Plan reviewed:** `share/notes/02_plan_T-2026-08-10-001_book2media.md`

---

## Findings

### F1. ffmpeg filter graphs are correct in shape; two open questions on edge cases.

The plan invokes three filter patterns I want to walk through:

**Pattern A — Ken Burns supersample.** `scale=8000:-1` BEFORE `zoompan=d=...:s=1920x1080:fps=30`. Research F8 + community benchmark confirm this is the right pattern. The `scale=8000:-1` line is in T4T1's `supersample_zoompan()` helper.

- **Edge case:** for a 30-minute horizontal chapter at 30 fps, the `scale=8000:-1` step allocates `8000 × 4500` × 3 channels × 4 bytes = **432 MB per frame** at peak. ffmpeg's `scale` filter buffers frames internally — at 30 fps × 30 minutes = 54,000 frames × 432 MB = **23.3 TB of allocator churn** if not careful. Mitigation: `scale` allocates per-frame, garbage-collects; the actual RSS is bounded by ffmpeg's max filter-thread pool (default 8 frames in-flight). Realistic RSS: ~3.5 GB. **Still HIGH.** Should be benchmarked in Phase 5 smoke test; if 4× supersample is too memory-heavy, fall back to 2× (4000 px).
- **Action:** T4T1 should accept a `--supersample-factor` flag (default 4, override 2 if memory-constrained).

**Pattern B — Two-pass loudnorm for audiobook M4B.** Pass 1: `ffmpeg -i input.wav -af "loudnorm=I=-19:TP=-2:LRA=11:print_format=json" -f null -`; Pass 2: apply with `measured_*` from JSON. This is correct per F8.

- **Edge case:** the measured pass requires the audio to be at the same sample rate as the final output (the plan correctly uses `.wav` as the intermediate). What if the user re-renders with different voice speed (e.g., 1.2x)? The measured values become stale. Mitigation: T4T2 should re-measure on every invocation (no caching of `measured_I` across runs).
- **Edge case:** two-pass loudnorm is **non-deterministic** in the sense that the measured JSON depends on the exact input audio. If the input `.wav` changes by even 1 sample, the measured values shift. T4T2's `--self-check` should run the two-pass against a known fixture and assert the integrated loudness is within ±0.5 LU of -19.

**Pattern C — SRT→ASS→ass=...:shaping=complex.** Correct per F7. The `pysubs2` SRT→ASS conversion adds `WrapStyle=2` for Arabic word-boundary line breaking.

- **Edge case:** `pysubs2` defaults to `\N` for forced line breaks; some players don't honor `WrapStyle=2`. The plan should specify the player-target list (VLC, mpv, ffmpeg's `ass=...` filter all honor `WrapStyle=2`; QuickTime does not).
- **Edge case:** `shaping=complex` requires libass built with HarfBuzz (verified at F7 — local ffmpeg has `--enable-harfbuzz`). What if a contributor runs the pipeline on a machine with libass-only (no HarfBuzz)? Mitigation: T4T4/T4T5 should add a runtime check `ffmpeg -hide_banner -h filter=ass | grep -q shaping` and exit 1 with an install hint.

### F2. faster-whisper alignment via `difflib.SequenceMatcher` is correct but under-specified.

The plan's T3T3 says: "use `difflib.SequenceMatcher` to align word timestamps to original chapter text." That's correct in principle. But the **implementation has 3 distinct strategies**, and the plan doesn't specify which:

- **Strategy 1 — Word-level align:** match ASR-transcribed words to original-prose words 1:1. Works when ASR transcribes exactly what was synthesized (TTS output → faster-whisper). Since TTS is deterministic per voice, this should work, but Arabic diacritics can cause drift.
- **Strategy 2 — Sentence-level align:** group ASR words into sentences (by `.`, `?`, `!`), align each sentence to the corresponding original sentence.
- **Strategy 3 — Chunk-level align:** reuse the T2T3 chunk boundaries; align each chunk's ASR words to the chunk's original text.

**Strategy 3 is the safest** because the TTS chunker and the ASR chunks share the same boundary. **Recommendation:** T3T3 must implement Strategy 3 (or document why Strategy 1/2 was chosen). Currently under-specified.

### F3. The audio→video pipeline has a wall-clock risk that the plan doesn't quantify.

Per the smoke test caveat in `## Self-critique` item 4: faster-whisper `large-v3` on Arabic is benchmarked ~0.5x realtime on a Quadro RTX 4000. For a 30-min chapter audio: ~60 min of ASR. For a 5-chapter book in 2 locales: ~10 hours of ASR alone.

TTS synthesis (edge-tts online) is ~0.3x realtime (faster than realtime). For 30-min chapter audio: ~9 min of TTS per chapter.

ffmpeg assembly (Phase 4): ~5-10 min per product. For 5 products × 5 chapters × 2 locales = ~50 products, ~5-8 hours.

**Total wall-clock for a 5-chapter Arabic book: ~25 hours** (mostly ASR). The plan's Phase 5 smoke test (1 day wall-clock) only validates ch-01 — the user needs to know that a full book is ~25 hours, not 1 day.

**Recommendation:** add a T5 sub-task "estimate full-book wall-clock from ch-01 measurements and surface to user."

### F4. M4B chapter-marker format is under-specified (CEO F4 flagged this too — it's a real engineering gap).

`ffmetadata` chapter format is documented in ffmpeg's man page. The format is:

```ini
;FFMETADATA1
title=Chapter 1: The Hook
[CHAPTER]
TIMEBASE=1/1000
START=0
END=1320000
title=Chapter 1: The Hook
[CHAPTER]
TIMEBASE=1/1000
START=1320000
END=2640000
title=Chapter 2: ...
```

The plan says T4T2 emits "chapter markers + `chapters.txt` (ffmetadata format)" but doesn't specify whether `title=` is set. **Recommendation:** T4T2 must set `title=` from `books/<slug>/style-guide.md` `## Chapter titles` if present, else fallback to `ch-NN`.

### F5. The plan correctly defers Mode 2 but leaves no upgrade path.

ComfyUI migration (R2) is deferred. The plan ships Mode 1 only. **But** there's no `share/notes/02_plan_T-FUTURE_mode2-comfyui.md` placeholder for the deferred work. If master asks "where's Mode 2?" in 3 months, the answer is "find the F2/F13 references in the research note." **Recommendation:** add a single-line "FUTURE WORK" pointer in `share/notes/02_plan_T-2026-08-10-001_book2media.md` referencing research F2/F13/R2.

### F6. The `book_check.py` media-manifest gate (T1T7) has a circular-dep risk.

If `book_check.py` validates `media-locale-manifest.json`, but `media-locale-manifest.json` is only generated at Phase 9 (after Phases 6/7/8), then running `book_check.py` at Phase 6/7/8 will fail with "missing manifest."

**Mitigation per the user's prompt:** "Add `books/<slug>/media-locale-manifest.json` to book-check gate (mirror the existing `frozen-lines.json` HARD-gate pattern)" — `frozen-lines.json` is also Phase 4 close, but `book_check.py` treats it as optional except at the gate it enforces. So the pattern is: skip the check unless `--require-media-manifest` is passed at Phase 9.

**Recommendation:** T1T7 must add `--require-media-manifest` as a default-off flag; `book2media-orchestrator` passes `--require-media-manifest` at Phase 9 only.

---

## Recommendations (priority-ordered)

1. **T4T1: add `--supersample-factor` flag** (default 4, allow 2 for memory-constrained machines). **Blocker: no.**
2. **T3T3: specify alignment strategy (Strategy 3 — chunk-level align).** **Blocker: no, but currently under-specified.**
3. **T4T2: specify ffmetadata `title=` source.** **Blocker: no.**
4. **T4T4/T4T5: add runtime HarfBuzz check** for libass-without-HarfBuzz machines. **Blocker: no.**
5. **T5: add full-book wall-clock estimation sub-task** based on ch-01 measurements. **Blocker: no.**
6. **Add a one-line "FUTURE WORK: Mode 2 ComfyUI" pointer in the plan file.** **Blocker: no.**
7. **T1T7: `--require-media-manifest` flag, default-off.** **Blocker: no.**

---

## Blockers

**None.** All findings are recommendations for tightening existing tasks; none require plan restructuring.

---

## Verdict

**PASS_WITH_WARN.** Engineering shape is correct; the 7 recommendations are sharpening, not blocking. The M4B chapter-marker spec (F4) and the alignment-strategy spec (F2) are the two most important to lock down before Phase 4 starts.
