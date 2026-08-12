# MEDIA.md — book2media (Phase 9) how-to guide

> **When to use this doc:** you want to produce audio or video from a finished book. If you're still writing, see `QUICKSTART.md` first; this doc assumes `books/<slug>/` exists with `chapters/ch-NN.md` files.

This is the narrative companion to `book-kit/docs/TOOLKIT.md` (the catalog) and `book-kit/docs/SCRIPTS.md` (the per-tool CLI reference). Read TOOLKIT.md when you need to know what tools exist; read SCRIPTS.md when you need the exact flag shape; read this doc when you want a recipe for a specific outcome.

## 0. What Phase 9 produces

For every book + every locale you enable, Phase 9 produces 5 media products:

| Product | Format | Geometry | Per-locale? |
|---|---|---|---|
| Audiobook | M4B (AAC mono 44.1 kHz) | n/a (audio only) | yes (en + ar) |
| Horizontal video | MP4 (H.264 + AAC) | 1920 x 1080 | yes |
| Trailer (60-90s teaser) | MP4 (H.264 + AAC) | 1920 x 1080 | yes |
| Reel (YouTube Shorts) | MP4 (H.264 + AAC) | 1080 x 1920 | yes |
| Reel (Instagram Reels) | MP4 (H.264 + AAC) | 1080 x 1920 | yes |
| Reel (TikTok) | MP4 (H.264 + AAC) | 1080 x 1920 | yes |

A 19-chapter book with both EN and AR enabled produces 6 final MP4/M4B files per locale (1 audiobook + 1 horizontal + 1 trailer + 3 reel variants), so 12 total per book. Counting by product family, it's 5 families × 2 locales = 10 per book.

## 1. The 5-minute version: enable media for a finished book

```sh
# 1. Add a media-locale-manifest.json to your book
py -3 book-kit/book_workflow/scripts/media_manifest.py generate \
    --book books/<your-slug> \
    --providers providers.yaml \
    --out books/<your-slug>/media-locale-manifest.json

# 2. Validate the generated manifest
py -3 book-kit/book_workflow/scripts/media_manifest.py validate \
    books/<your-slug>/media-locale-manifest.json

# 3. Tell master to run Phase 9 with the --media flag
# (In a new session, just say: "produce media for <your-slug>")
```

Master will then dispatch `book2media-orchestrator` which walks Phases 1-6 of book2media in sequence. Each phase runs the relevant script (TTS, ASR, align, ffmpeg) per chapter per locale. Outputs land in `books/<your-slug>/exports/`.

## 2. "How do I..." recipes

### Add a new locale (e.g., Spanish)

`media-locale-manifest.json` has `source_locale` and `target_locales` arrays. Add `es` to `target_locales` and fill in per-product voice. The manifest schema will reject unknown voices; either pick from the built-in registry (Kokoro for en, edge-tts for everything else) or add a new voice to `providers.yaml` first.

For Spanish, edge-tts voices include `es-ES-ElviraNeural`, `es-MX-DaliaNeural`, etc. Update `media_tts.py` if the chunker needs to handle new language-specific tokenization; most languages Just Work because the chunker is H2-driven (structure-based) and the TTS provider handles pronunciation.

### Change the per-locale voice

Edit `media-locale-manifest.json` directly. The `voice` field is per-product. The validator will reject empty-string voices; use `skip: true` if you want to drop a product entirely.

If you want to change a global default (applies to all books that don't override), edit `providers.yaml`:

```yaml
locales:
  en:
    tts_provider: kokoro
    voice: af_heart
  ar:
    tts_provider: edge-tts
    voice: ar-SA-HamedNeural
```

### Skip a product

Set `skip: true` on the product in `media-locale-manifest.json`. The TTS/assembly lane will skip that product entirely without raising.

### Regenerate one product (e.g., audiobook only)

Re-run the relevant script directly:

```sh
py -3 book-kit/book_workflow/scripts/assemble_audiobook.py \
    --book books/<slug> --out books/<slug>/exports/<slug>-en.m4b --locale en
```

Each assembler is idempotent. Re-running overwrites the previous output. The `--self-check` flag (on audiobook) validates that the chapter count matches the input.

### Plan full-book wall-clock timing

The smoke report (`share/notes/05_smoke_T-2026-08-10-001.md`) has the per-product measurements. For a 19-chapter book at 4x supersample (default), expect:

- Audiobook: ~30 sec per chapter (no video render) = 10 min total
- Horizontal video: ~131 min per chapter = 41 hours
- Trailer: ~15 min once (whole-book teaser)
- Reel (single-platform): ~73 min per chapter = 23 hours
- Reel (3-platform via script): ~73 min per chapter (serial fan-out)

**Total per locale at default settings: ~64 hours wall-clock.** Halve with `scale_mult=2` (not yet CLI-reachable, see Deferred WARN F5). Cut to ~6-12 hours with NVENC.

### Switch the default video encoder to NVENC (when available)

Direct edit to `book-kit/book_workflow/scripts/ffmpeg_zoompan.py` and the assembler filter chains. Look for `VCODEC = "libx264"` and replace with `VCODEC = "h264_nvenc"`. Same for the `-preset` and `-crf` settings. The CLI flag for this is Deferred WARN F5; fix in a v1.3.1 polish dispatch.

### Translate a non-Arabic book to Arabic before producing media

Phase 9 reads `source-map.md` (translation mode) to reuse the translation. If `source-map.md` is absent, Phase 9 runs media-only translation per chapter. To enable translation mode for a book, see `book-kit/docs/TRANSLATION_MODE.md`.

### Force a specific product for one chapter only

The manifest has per-product fields but not per-chapter. For per-chapter overrides, either:
- Edit the manifest to set `skip: true` on the products you don't want, and re-run.
- Use the assembler scripts directly (see "Regenerate one product" above) with `--chapter ch-NN` instead of the full book.

### Add a new TTS provider

Edit `voices.py:VOICE_REGISTRY` to add the provider's defaults. Then update `media_tts.py:_dispatch_provider` to route to the new provider's CLI or SDK. Tests in `book-kit/tests/test_voices.py` will tell you what's missing.

### Add a new reel platform (e.g., LinkedIn)

1. Add the platform name to `_ALLOWED_PLATFORMS` in `assemble_reel.py`.
2. Add the platform's loudnorm I/TP and ASS alignment to `_PLATFORM_PROFILES`.
3. Add tests in `book-kit/tests/test_assemble_reel.py`.
4. Update `book-kit/docs/TOOLKIT.md` and `book-kit/docs/SCRIPTS.md` to document the new platform.

## 3. Debugging

### "Audio is empty" error from assemble_audiobook

The per-chapter MP3 didn't land or is zero-bytes. Check:
- `shares/audio/<slug>/ch-NN-<locale>.mp3` exists
- ffprobe the file: `ffprobe -v error -show_streams <path>` should report a valid audio stream
- Re-run `media_tts.py` if the file is missing

### "alignment drift X% exceeds threshold"

`align_srt.py` couldn't match the Whisper transcript to the chapter text. Common causes:
- Whisper hallucinated on a quiet segment (especially chapter titles). Re-run with `--from <previous-json>` to skip the hallucinated segment.
- The chapter was written in a different locale than the manifest claims. Check `media-locale-manifest.json:source_locale` matches the chapter's actual language.
- For genuine-Arabic with English tech terms: lower the threshold with `--drift-floor 0.50` (the default 0.70 is too strict for mixed-language content).

### "ffmpeg Cannot allocate memory" on reel render

3-platform fan-out OOMs on this hardware. Fix paths:
- Run single-platform: `--platforms yt` (3 separate runs is what the script does anyway under the hood now; the OOM was from a previous architecture that has been replaced).
- Free RAM before the run.
- Switch to NVENC (see above).

### "faster-whisper downloads 1.5GB on first run"

That's normal. The first ASR invocation downloads the model weights. Subsequent runs use the cache. To redirect the cache to your repo, use `--cache-dir <repo>/.cache/faster-whisper` on `check_whisper_deps.py`.

### "Schema validation fails on `products.0.voice: '' is not one of [...]`"

You have an empty-string voice. The validator rejects this. Either:
- Set `skip: true` to drop the product entirely.
- Set a valid voice id (use `voices.py --inspect` to see the full registry).

## 4. Performance & cost

### Wall-clock at default settings (4x supersample, 12-core CPU)

| Product | Per 60s clip | Per 700s chapter | Per 19-chapter book |
|---|---|---|---|
| Audiobook (no video) | 30 sec | 30 sec | 10 min |
| Horizontal 1920x1080 | 11.2 min | ~131 min | ~41 hours |
| Trailer 60-90s | n/a | ~15 min | 15 min |
| Reel 1080x1920 (single platform) | 6.2 min | ~73 min | ~23 hours |
| Reel 3-platform fan-out (serial) | 6.2 min | ~73 min | ~23 hours |

**Per-locale totals at default settings:** ~64 hours for 5 products.
**Per 2-locale book (en + ar):** ~128 hours (~5.3 days wall-clock).

### Escape hatches (in order of preference)

1. **`scale_mult=2`** (scale=4000:-1) — halves the supersample factor; ~2x faster wall-clock with slight quality loss. **NOT YET CLI-REACHABLE** (Deferred WARN F5; v1.3.1 polish).
2. **NVENC** (`-c:v h264_nvenc`) — ~5-10x faster on Nvidia GPUs. **NOT YET CLI-REACHABLE** (same F5).
3. **Split renders** — 5-min audio chunks per ffmpeg invocation. Implemented in `assemble_video_horizontal.py` for `--all` mode (one MP4 per chapter, then concat). Use this for long chapters.
4. **Lower `-preset`** from `medium` to `veryfast` (already done for smoke). 2-3x faster, slightly larger files.

### Cost of cloud TTS

If you choose a cloud TTS provider (e.g., Azure, Google, ElevenLabs) instead of Kokoro/edge-tts, expect $0.01-0.05 per chapter for a 700s narration. Phase 9 is local-only by default; cloud TTS requires changing `media_tts.py` and adding credentials to `providers.yaml`.

## 5. When to upgrade to Phase 9.5 (auto-publish)

Phase 9.5 is the planned auto-publish lane: YouTube API for Shorts, Instagram Graph API for Reels, TikTok API for TikTok. None of this is implemented yet. To enable auto-publish:
1. Get API credentials for each platform.
2. Add the credentials to `providers.yaml` under `publish:`.
3. Set `publish: true` on the relevant products in `media-locale-manifest.json`.
4. Master will dispatch the auto-publish scripts (to be written) at Phase 9.5.

Until then, all media products are produced locally and must be manually uploaded.

## 6. See also

- `book-kit/docs/TOOLKIT.md` — full tool catalog
- `book-kit/docs/SCRIPTS.md` — per-tool CLI reference
- `book-kit/docs/QUICKSTART.md` — 60-second kit install
- `book-kit/docs/TRANSLATION_MODE.md` — when translating a non-Arabic book to Arabic
- `share/notes/05_smoke_T-2026-08-10-001.md` — smoke test report with measurements
- `share/reports/04_review_T-2026-08-10-001_phase5.md` — Phase 5 review (PASS_WITH_WARN)
- `agents_manager/book2media-orchestrator/SKILL.md` — orchestrator's full 8-phase protocol
- `agents_manager/assets/SKILL.md` `## Media-manifest lane` — am-assets media manifest gate
- `agents_manager/review/SKILL.md` `## Locale-correctness gate` — am-review locale gate
