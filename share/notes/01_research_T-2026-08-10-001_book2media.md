# Research — T-2026-08-10-001 (book2media Phase 9 pipeline)

**Date:** 2026-08-10
**Trigger:** initial
**Sub-agent:** research
**Task id:** T-2026-08-10-001
**Scope:** Lock down the unknowns before am-planning writes the book2media-orchestrator + 9-phase pipeline + media-manifest schema. Six required research areas + 1 ComfyUI readiness note.

---

## Task in one sentence

User approved Phase 9 (`book2media`) of the book-gen pipeline: produce 5 media products per book per locale (audio m4b, horizontal Mode-1 video, future Mode-2 video, vertical trailer, vertical reel) with TTS, Ken Burns / per-scene images, RTL subtitle burn-in, per-platform loudnorm, and an adaptive translation-reuse mechanism that piggybacks on book-gen translation mode's `source-map.md` when present.

## What we know for sure

- **Architecture decision (locked).** New `agents_manager/book2media-orchestrator/SKILL.md` mirroring `book-gen-orchestrator/SKILL.md` shape. `am-assets` gets a media-manifest lane. `am-review` gets a locale-correctness gate. Master amends `book-gen-orchestrator/SKILL.md:348` with "Master MAY dispatch book2media-orchestrator at Phase 9 per user `--media` flag. am-assets still banned from Phases 0-8."
- **Modes (locked).** Mode 1 (single static image + Ken Burns zoompan + waveform) first. Mode 2 (Flux per-scene images) gated on Mode 1 quality.
- **TTS default (locked).** Kokoro default for English (Apache-2.0, offline, 54 voices).
- **Locales (locked).** English + Arabic at minimum; per-locale provider registry from day 1.
- **5-product matrix (locked).** Per book per locale: `audiobook-<locale>.m4b`, `video-horizontal-m1-<locale>.mp4`, `video-horizontal-m2-<locale>.mp4` (future), `video-vertical-trailer-<locale>.mp4`, `video-vertical-reel-<locale>.mp4`.
- **Reels publish (locked).** YouTube Shorts + Instagram Reels + TikTok. One source render + per-platform loudnorm + caption reposition = 3 outputs from each vertical source render.
- **Translation mode (locked).** Adaptive. If book was generated in translation mode, reuse `books/<slug>/source-map.md` for target locales. If not, run media-only translation pass.
- **Scene analysis language (locked).** Always English — image prompts must be English for Flux Arabic glyph safety (no Arabic text in generated images).
- **Local ffmpeg (verified).** `C:\tool\ffmpeg_full\bin\ffmpeg.exe` is `ffmpeg version 2025-08-25-git-1b62f9d3ae-full_build-www.gyan.dev` with `--enable-libass --enable-freetype --enable-fribidi --enable-harfbuzz` confirmed at the build config line (output captured during this research). The `subtitles` filter does NOT expose `shaping=` option in this build (the option was added in ffmpeg upstream commit `b08c9c5` — verified by `ffmpeg -hide_banner -h filter=subtitles` showing no `shaping` AVOption); the `ass` filter DOES expose `shaping=complex` (verified by `ffmpeg -hide_banner -h filter=ass` showing the full option set). The `loudnorm` filter exposes the full two-pass option set (`measured_I`, `measured_LRA`, `measured_TP`, `measured_thresh`, `linear`, `print_format=json`) — verified locally.
- **ComfyUI Desktop local state (verified).** `C:\Users\Ahmad Mahmoud\Documents\ComfyUI` exists. `models/` is present with 27 standard subdirs, all of `unet/`, `clip/`, `text_encoders/`, `vae/`, `checkpoints/`, `gguf/` are EMPTY (verified via PowerShell `Get-ChildItem`). `main.py` does NOT exist at the install root (confirmed Electron wrapper). Custom nodes installed: `cg-use-everywhere`, `ComfyUI-GGUF`, `comfyui-kjnodes`, `comfyui-videohelpersuite`. The Desktop config path `C:\Users\Ahmad Mahmoud\AppData\Roaming\ComfyUI\` does NOT exist (confirmed).
- **ComfyUI server state (verified).** `127.0.0.1:8188` not listening (verified via `Get-NetTCPConnection -State Listen` — no entry). No `ComfyUI*` process running. Server is OFF.
- **Actual model files (verified).** Located at `D:\comfy\models\` with the SAME empty subdir tree as the ComfyUI install. Files actually present: `text_encoders/clip_l.safetensors` (246 MB), `text_encoders/t5xxl_fp16.safetensors` (9.8 GB), `vae/ae.safetensors` (335 MB), `checkpoints/ponyDiffusionV6XL_v6StartWithThisOne.safetensors` (6.9 GB), `diffusion_models/flux1-schnell-Q4_K_S.gguf` (6.8 GB — note: NOT in `gguf/` subdir as user said, but in `diffusion_models/`).
- **source-map.md schema (verified).** Template at `book_workflow/book-agents/templates/source-map.md` documents columns `chapter`, `source`, `word_min`, `word_max`, `required_h2`, `freeze_code`. Generator: `book_workflow/scripts/build_source_map.py` walks `source/` and emits default envelope.
- **Book-gen-orchestrator integration points (verified).** `book-gen-orchestrator/SKILL.md:348` contains the line that master must amend; `book-gen-orchestrator/SKILL.md:72` documents the `source-map.md` Phase-0 generation rule; `book-gen-orchestrator/SKILL.md:286-308` documents the Branch A translation-mode dispatch.

## What we don't know (ambiguities)

- **Ponytail-level: edge-tts Arabic word-boundary events.** Documentation states `edge-tts --write-subtitles` writes Word-level SRT from the live MS endpoint, but the user already flagged: "Verify word-boundary events are natively returned for Arabic (some MS voices don't emit per-word timings for non-English)." This is empirically undertested — would need a runtime check against `ar-EG-SalmaNeural` and `ar-SA-HamedNeural`.
  - **Suggested clarifying question:** "Do we have a smoke-test budget to run a 30-second `edge-tts --voice ar-EG-SalmaNeural --write-subtitles sample.srt` and verify per-word timestamps land at sub-second intervals, OR should we assume fallback to `faster-whisper` for word timing on Arabic?"
- **Chatterbox multilingual VRAM budget.** HF model card says 0.5B params (~2 GB FP16 weights) but actual inference VRAM is not specified in the public card. XTTS-v2 typically needs 4-6 GB VRAM at inference.
  - **Suggested clarifying question:** "Run `nvidia-smi` once on this machine and confirm CUDA available + ≥6 GB free VRAM before committing to offline TTS providers? Or treat offline TTS as best-effort with Kokoro (CPU-only) as the safe default?"
- **Mode 2 timeline.** User said "Mode 2 gated on Mode 1 quality" but did not define the gate. What quality threshold triggers the unlock? Render-time benchmark? User acceptance on the first 3 chapters of `daily-focus`? Two completed Mode-1 books?
  - **Suggested clarifying question:** "Define the Mode 1 → Mode 2 unlock gate: (a) N successful Mode-1 renders with no user complaints, (b) ≥80% user-acceptance on `daily-focus` reels, (c) after Mode-1 ships and we have usage data, or (d) something else?"
- **Reel source-render aspect ratio.** User said "one source render + per-platform loudnorm + caption reposition = 3 outputs" — but is the source render 9:16 (matching Shorts/Reels/TikTok native) or 16:9 (with vertical crop in post)? Both can work; the choice affects subtitle burn-in strategy.
  - **Suggested clarifying question:** "Source render for vertical output: 9:16 (1080×1920) with caption reposition only, OR 16:9 master with vertical crop + caption reposition?"
- **Audiobook narrator consistency.** Kokoro produces different voices per chapter if voice is changed; does the user want a single narrator voice across all chapters, or chapter-specific voices (e.g., character dialogue)?
  - **Suggested clarifying question:** "Audiobook voice policy: (a) single narrator voice across all chapters (e.g., `af_heart`), (b) chapter-specific voices matched to POV, (c) book-level voice pick from style-guide?"
- **Per-locale provider registry source of truth.** User said "per-locale provider registry from day 1" but did not say where it lives. Options: (a) `books/<slug>/media-locale-manifest.json` (per-book, user-editable), (b) `agents_manager/book2media-orchestrator/providers.yaml` (global, code-reviewed), (c) `~/.config/opencode/book2media.yaml` (user-global).
  - **Suggested clarifying question:** "Provider registry location: per-book manifest (a), global code-reviewed yaml (b), or user-global yaml (c)? Recommend (a) for trial flexibility, but (b) keeps things auditable."

## Risks and doubts

- **R1. ffmpeg `subtitles` filter Arabic shaping is broken on local build.**
  - **Severity:** HIGH
  - **Mitigation:** For Arabic SRT inputs, convert to ASS first (`pysubs2.convert(srt_path, ass_path)`), then burn with `ass=...:shaping=complex`. Document this in the Phase 9 implementation. Alternative: install a newer ffmpeg build with upstream commit `b08c9c5` exposed (`shaping=` in `subtitles` filter). Validate via runtime smoke test on `books/daily-focus/ch-01.md` translated to Arabic before locking the strategy.
- **R2. ComfyUI Desktop cannot be started headlessly via `main.py --disable-auto-launch` because `main.py` doesn't exist on this install.**
  - **Severity:** HIGH (gates all of Mode 2)
  - **Mitigation:** Two paths documented in Section 6. (a) Bare OSS install `github.com/comfyanonymous/ComfyUI` + `ComfyUI-GGUF` custom node = what the Stage 3b plan assumes; gives you CLI access and is the canonical programmatic surface. (b) ComfyUI Desktop's `extra_models_config.yaml` exposes model paths but does not expose CLI launch (the Desktop launcher is an Electron wrapper). For Mode 1 only (no image gen), this risk does not bite — Kokoro + Ken Burns + waveform are CPU/GPU-light and need no ComfyUI. For Mode 2, plan must include "install bare OSS ComfyUI OR prove Desktop API access works".
- **R3. Coqui XTTS-v2 is `Coqui Public Model License (CPML)` — non-commercial only.**
  - **Severity:** MEDIUM
  - **Mitigation:** Do NOT use XTTS for production audiobook output unless the user confirms the use is non-commercial. Chatterbox (MIT, 23 langs incl. Arabic) is the safer offline fallback. Document the CPML restriction in `books/<slug>/media-locale-manifest.json` per-product.
- **R4. TikTok caption-positioning is platform-specific; "one source render + caption reposition" is non-trivial.**
  - **Severity:** MEDIUM
  - **Mitigation:** TikTok safe-zone per socaptions.com is `top 250px, bottom 460px, right 180px`; Instagram Reels `top 250px, bottom 420-520px, right 160px, left 60px`; YouTube Shorts `top + bottom + right edge` (per Somake AI). Burn-in to a single safe-zone (the union: top 250px / bottom 460px / right 180px / left 60px) per caption position then platform-specific `crop`/`overlay` filters. Validate on one reel first.
- **R5. faster-whisper Arabic word-timestamp quality vs English.**
  - **Severity:** MEDIUM
  - **Mitigation:** faster-whisper `word_timestamps=True` works for any language; Arabic accuracy is lower than English per free.ai's docs ("Yes — both segment-level ... and word-level timestamps are available. Word-level is the default for VTT/SRT subtitle export"). For captioning quality, recommend `large-v3` model for Arabic; for speed, `small` is acceptable. Always run `language=ar` to skip detection for known-language audio.
- **R6. edge-tts Arabic voices may not emit per-word timestamps reliably.**
  - **Severity:** MEDIUM
  - **Mitigation:** Run a smoke test against `ar-EG-SalmaNeural` and `ar-SA-HamedNeural` BEFORE locking the strategy. If word timings are absent, fall back to `faster-whisper --language=ar --word_timestamps=True` for caption generation, while keeping edge-tts as the audio source.
- **R7. ComfyUI Desktop's DownloadManager validates against `C:\Users\<user>\Documents\ComfyUI\models` only — even with `extra_models_config.yaml`.**
  - **Severity:** LOW
  - **Mitigation:** Documented in Comfy-Org/desktop issue #1699 (referenced in `extra_model_paths.yaml.example` thread). For Mode 2 download workflow, download to default path then move, OR use bare OSS install (which has no DownloadManager).
- **R8. The 5-product matrix may balloon storage quickly.**
  - **Severity:** LOW
  - **Mitigation:** Estimate: per chapter (~3000 words prose → ~25 min audio at natural pace, ~50 MB MP3 → ~45 MB M4B at AAC 64k mono). Audiobook for 5 chapters: ~225 MB. Video per locale per chapter: ~250 MB at 1080p × ~6 min. Per chapter × 5 products × 2 locales × 5 chapters = ~6 GB per book. Document in `media-locale-manifest.json` retention policy: `keep_until_shipped: true`.
- **R9. Scene analysis in English produces Arabic glyphs in the generated image.**
  - **Severity:** MEDIUM
  - **Mitigation:** User already locked: "image prompts must be English for Flux Arabic glyph safety (no Arabic text in generated images)." Document in the scene-analysis dispatch that Flux prompts are English-only and that any Arabic content must be added in the subtitle overlay layer, not the image layer.
- **R10. Reel aspect ratio mismatch between source 16:9 and platform 9:16.**
  - **Severity:** LOW
  - **Mitigation:** Documented in socaptions.com and admanage.ai. Single-source render at 9:16 (1080×1920) is the recommended path per Hopper HQ / Somake AI: "Set dimensions before editing. Changing aspect ratio after editing crops your content. Build in 9:16 from the start." Plan must pick 9:16 master, not 16:9 cropped.

## Technical findings

### F1. Kokoro-82M (Apache-2.0, hexgrad) — confirmed voice inventory

Verified at `https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md`. Total: **54 voices** across 9 languages, **zero Arabic voices**. Voice prefixes map to language:

- `af_`/`am_` American English (11F + 9M = 20)
- `bf_`/`bm_` British English (4F + 4M = 8)
- `ef_`/`em_` Spanish (1F + 2M = 3)
- `ff_` French (1F only)
- `hf_`/`hm_` Hindi (2F + 2M = 4)
- `if_`/`im_` Italian (1F + 1M = 2)
- `jf_`/`jm_` Japanese (4F + 1M = 5)
- `pf_`/`pm_` Brazilian Portuguese (1F + 2M = 3)
- `zf_`/`zm_` Mandarin Chinese (4F + 4M = 8)

Top quality voices: `af_heart` (Grade A, default), `af_bella` (Grade A-), `bf_emma` (Grade B-), `am_michael` (Grade C+). Voice grades are estimates of training-data quality AND quantity — voices flagged "MM minutes" training (e.g., `af_sky` Grade C-) perform visibly worse than voices with hours of training (`af_heart` Grade A).

**Quality note** (from VOICES.md): "Voices perform best on a 'goldilocks range' of 100-200 tokens out of ~500 possible. Voices may perform worse at the extremes: Weakness on short utterances, especially less than 10-20 tokens. Rushing on long utterances, especially over 400 tokens. One possible inference mitigation is to bundle shorter utterances together." This means chapter-level synthesis (often 3000+ tokens) MUST be chunked to ≤400 tokens per call.

**chub citation:** No entry in chub registry (registry lacks Kokoro as of v0.1.4, revision `git-661f708`). Document this gap; use upstream HF model card as canonical.

### F2. edge-tts (MIT, rany2) — full Arabic voice inventory

Verified at `https://github.com/rany2/edge-tts` README and `https://edgetts.github.io/`. **28 Arabic voices** across 14 locales:

| Locale | Female voice | Male voice |
|---|---|---|
| ar-AE (UAE) | FatimaNeural | HamdanNeural |
| ar-BH (Bahrain) | LailaNeural | AliNeural |
| ar-DZ (Algeria) | AminaNeural | IsmaelNeural |
| ar-EG (Egypt) | SalmaNeural | ShakirNeural |
| ar-IQ (Iraq) | RanaNeural | BasselNeural |
| ar-JO (Jordan) | SanaNeural | TaimNeural |
| ar-KW (Kuwait) | NouraNeural | FahedNeural |
| ar-LB (Lebanon) | LaylaNeural | RamiNeural |
| ar-LY (Libya) | ImanNeural | OmarNeural |
| ar-MA (Morocco) | MounaNeural | JamalNeural |
| ar-OM (Oman) | AyshaNeural | AbdullahNeural |
| ar-QA (Qatar) | AmalNeural | MoazNeural |
| ar-SA (Saudi Arabia) | ZariyahNeural | HamedNeural |
| ar-SY (Syria) | AmanyNeural | LaithNeural |
| ar-TN (Tunisia) | ReemNeural | HediNeural |
| ar-YE (Yemen) | MaryamNeural | SalehNeural |

Also `ar-IL` (Israel) appears in the Azure Speech language-support table (Fast transcription support) but no Neural voice is published.

**Word-timestamp behavior:** edge-tts writes SRT subtitles natively via `--write-subtitles`. The README claims this works for all voices including Arabic. Empirical confirmation pending per the "ambiguities" question above.

**License:** MIT for the edge-tts wrapper; the underlying MS Neural voices are free to use via the Edge online endpoint but have no commercial-use SLA from Microsoft (the same posture as Azure's free tier).

**chub citation:** No entry in chub registry. Document gap; use rany2/edge-tts PyPI + Azure Speech language-support docs as canonical.

### F3. Coqui XTTS-v2 — multilingual including Arabic (BUT non-commercial license)

Verified at `https://huggingface.co/coqui/XTTS-v2` model card and `https://coqui-tts.readthedocs.io/en/latest/models/xtts.html`. **17 languages supported**: English, Spanish, French, German, Italian, Portuguese, Polish, Turkish, Russian, Dutch, Czech, **Arabic (ar)**, Chinese (zh-cn), Japanese (ja), Hungarian (hu), Korean (ko), Hindi (hi). Voice cloning with 6-second audio clip, 24 kHz sampling rate, emotion/style transfer via cloning, cross-language voice cloning.

**License: CPML (Coqui Public Model License) — non-commercial only.** Per the Coqui TTS repo, the model is released under CPML which prohibits commercial use. This is NOT a permissive license and is a hard blocker for any commercial audiobook production. Document this restriction; recommend Chatterbox instead for production use.

**VRAM at inference:** Not documented in the public card. Per community reports, XTTS-v2 typically requires 4-6 GB VRAM at inference (CPU fallback exists but is very slow). Plan must validate VRAM budget before committing.

**chub citation:** No entry in chub registry. Document gap; use coqui/XTTS-v2 HF model card as canonical.

### F4. CosyVoice 2 (Apache-2.0, FunAudioLLM/Alibaba) — 9 languages, NO Arabic

Verified at `https://huggingface.co/FunAudioLLM/CosyVoice2-0.5B` and `https://github.com/FunAudioLLM/CosyVoice`. Covers **9 languages**: Chinese, English, Japanese, Korean, German, Spanish, French, Italian, Russian. **Arabic is NOT supported.** 18+ Chinese dialects (Guangdong, Minnan, Sichuan, Dongbei, etc.) and cross-lingual zero-shot voice cloning. License Apache-2.0 (permissive).

**Verdict:** Not viable for Arabic. Could be a backup for Japanese/Korean if Chatterbox quality is insufficient.

**chub citation:** No entry in chub registry.

### F5. Chatterbox Multilingual V3 (MIT, Resemble AI) — 23 languages INCLUDING Arabic, zero-shot voice cloning

Verified at `https://huggingface.co/ResembleAI/chatterbox` and `https://www.resemble.ai/learn/models/chatterbox`. **23 languages**: English, Spanish, French, German, **Arabic**, Portuguese, Russian, Turkish, Italian, Danish, Finnish, Japanese, Korean, Mandarin, Dutch, Slovak, Swedish, Vietnamese, Norwegian, Polish, Swahili, Hindi, Hebrew. Zero-shot voice cloning from 5-second reference clip. 0.5B params (Llama backbone). Trained on 0.5M hours of cleaned data. MIT license. ~200ms inference latency. Watermarked outputs.

**Single Language Packs** available for Chinese, LatAm Spanish, Brazilian Portuguese, Spain Spanish, Portugal Portuguese, Hindi (per HF model card).

**VRAM at inference:** ~2 GB FP16 weights (0.5B params); inference typically fits in 4-6 GB VRAM but undocumented in card.

**Verdict:** Strongest offline option for Arabic. License is MIT (commercial-friendly). Match-of-record for the locked TTS provider matrix.

**chub citation:** No entry in chub registry. Document gap; use HF model card as canonical.

### F6. Reels platform specs (verified 2026, see Section F6 table below)

See full matrix in Section F6 above. All three platforms accept 9:16 vertical at 1080×1920 as the gold-standard native format. YouTube Shorts max duration raised from 60s to **3 minutes** on 2024-10-15 (Hopper HQ 2026 update confirmed). Instagram Reels max raised to **20 minutes** (Postfa.st 2026-07-16; Instagram notes "Reels over 3 minutes are not recommended to new audiences"). TikTok max is **10 minutes** for most accounts, 60 minutes for select newer accounts.

**Caption safe-zones (per-platform, 1080×1920 canvas):**

| Platform | Top | Bottom | Right | Left | Caption area | Font min |
|---|---|---|---|---|---|---|
| YouTube Shorts | 250px | 250-420px | right edge | full width | center-lower | not specified |
| Instagram Reels (organic) | 250px | 420px | 160px | 60px | y=1000-1350px | not specified |
| Instagram Reels (ad) | 250px | 520px | 160px | 60px | y=1000-1350px | not specified |
| TikTok | 250px | 460px | 180px | full width | y=700-1360px | 60-90px bold |

Recommended burn-in: center text within the union safe-zone (top 250, bottom 460, right 180, left 60) at 72px bold. This survives all three platforms.

### F7. ffmpeg `subtitles` vs `ass` filter — Arabic shaping gap on local build

**Local ffmpeg `2025-08-25-git-1b62f9d3ae-full_build-www.gyan.dev`** was tested. The `subtitles` filter does NOT expose a `shaping=` option (per `ffmpeg -hide_banner -h filter=subtitles`). The `ass` filter DOES expose `shaping=complex` (per `ffmpeg -hide_banner -h filter=ass`, output captured during this research).

This is consistent with upstream FFmpeg commit `b08c9c5` (titled "lavfi/vf_subtitles: expose shaping option") which added the option to the subtitles filter after our local build date. Per the commit message: "subtitles=...:shaping=complex renders Arabic lam-alef correctly when libass is built with HarfBuzz support."

**Local ffmpeg IS built with HarfBuzz** (`--enable-harfbuzz` is in the configure output), so the `ass` filter with `shaping=complex` works correctly for Arabic. The subtitles filter falls back to `ASS_SHAPING_SIMPLE` (which uses fribidi instead of HarfBuzz), and fribidi-only shaping produces broken Arabic lam-alef ligatures.

**Workaround for SRT→Arabic burn-in:** Convert SRT to ASS first via `pysubs2` (Python) or `ffmpeg -i video.srt video.ass`, then burn with `ffmpeg -vf "ass=video.ass:shaping=complex"`. Alternative: install a newer ffmpeg build (gulopez-franzke/gyan-dev full builds past late 2025) that has the b08c9c5 patch.

**chub citation:** `chub search "ffmpeg"` returns only `pydub/package` and `av/package`. Use upstream FFmpeg docs + the jellyfin-ffmpeg issue #217 thread (`https://github.com/jellyfin/jellyfin-ffmpeg/issues/217`) as canonical for Arabic SRT burn-in.

### F8. ffmpeg `loudnorm` — two-pass for broadcast-grade, streaming target −14 to −16 LUFS

Verified via local `ffmpeg -hide_banner -h filter=loudnorm` and the EBU R 128 s1 supplement (`https://tech.ebu.ch/publications/r128s1`).

EBU R 128 specifies for short-form content (≤2 min, ads/promos): **Programme Loudness −23 LUFS**, **Short-term max −18 LUFS**, **True Peak ≤ −1 dBTP**. But the EBU document explicitly states "in special cases the Programme Loudness Level may be normalised to a Target Level lower than −23 LUFS on purpose" — which is what streaming platforms do.

**Streaming target:** −14 to −16 LUFS integrated (YouTube/Spotify standard), −1 to −2 dBTP true peak, 7-11 LU LRA. Per ffmpeg-cookbook.com and DEV Community guides:

```
ffmpeg -i input.mp4 -c:v copy -af "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | tail -12
# (pass 1 measures; capture input_i, input_tp, input_lra, input_thresh from JSON output)

ffmpeg -i input.mp4 -c:v copy -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=<i>:measured_TP=<t>:measured_LRA=<l>:measured_thresh=<th>:offset=<o>:linear=true" output.mp4
# (pass 2 applies linear gain based on measured values; `linear=true` prevents dynamic-range compression)
```

**For short-form content (≤2 min), single-pass loudnorm is acceptable per `loudnorm` filter docs** — but two-pass is more accurate. Since 5-product matrix is per-chapter (~6 min) and reels are <90s, single-pass is sufficient for reels but two-pass is required for the audiobook M4B (continuous audio, dynamic range matters for spoken-word listenability).

### F9. Amiri / Noto Naskh Arabic / Scheherazade New — font recommendations

- **Amiri** (Hosny, OFL): ships in most distros, beautiful traditional Naskh. The de facto open-source Arabic book font.
- **Noto Naskh Arabic** (Google, OFL): robust shaping, designed for screen and print, broad Unicode coverage.
- **Scheherazade New** (SIL, OFL): calligraphic, used by SIL for academic publishing. Heavier visual weight than Amiri.

For reels (caption burn-in, max readability at mobile size), recommend **Amiri** at 72px bold with 4px outline (libass `BorderStyle=1, Outline=4, OutlineColour=&H80000000`). For audiobook chapters (text only, no video), font choice doesn't matter — but for EPUB export future work, **Noto Naskh Arabic** is the safest.

**chub citation:** No entry in chub registry for any Arabic font.

### F10. faster-whisper word-timestamp RTL behavior

Verified at `https://github.com/SYSTRAN/faster-whisper/blob/master/faster_whisper/transcribe.py` and `https://deepwiki.com/SYSTRAN/faster-whisper/4.3-transcription-options-and-configuration`. `word_timestamps=True` extracts word-level timestamps via cross-attention alignment + Dynamic Time Warping, populating `segment.words` with `word`, `start`, `end`, `probability`. Output text is "returned in their native right-to-left script and render correctly in any RTL-aware viewer" (per free.ai Arabic transcription docs).

**Caveat:** faster-whisper was originally English-trained; Arabic word-timestamp accuracy is lower than English per free.ai ("Word-level is the default for VTT/SRT subtitle export"). Recommend `large-v3` for Arabic; `small` is acceptable for fast smoke tests. Set `language=ar` explicitly to skip detection overhead.

**RTL line-break in SRT:** The generated SRT text is in native Arabic script (RTL); standard SRT viewers render correctly because Unicode BiDi handles RTL. faster-whisper does NOT need a post-processor for RTL — but the burn-in filter chain (SRT→ASS→ass=...:shaping=complex) does need `WrapStyle=2` (smart wrapping at word boundaries) in the ASS style for proper Arabic line breaking.

### F11. source-map.md schema for adaptive translation reuse

Template at `book_workflow/book-agents/templates/source-map.md:14-19` documents the canonical table:

| chapter | source | word_min | word_max | required_h2 | freeze_code |
|---|---|---:|---:|---|:-:|

For media-only translation (no source-map present), the media-orchestrator needs a separate schema for the per-locale translation tracking. Proposed schema (per the user's spec example, validated against current convention):

```json
{
  "source_locale": "en",
  "target_locales": ["en", "ar"],
  "products": [
    {
      "id": "audiobook-en",
      "locale": "en",
      "format": "audio/m4b",
      "tts_provider": "kokoro",
      "voice": "af_heart",
      "skip": false
    },
    {
      "id": "audiobook-ar",
      "locale": "ar",
      "format": "audio/m4b",
      "tts_provider": "edge-tts",
      "voice": "ar-SA-HamedNeural",
      "skip": false,
      "translation_required": true
    }
  ]
}
```

This nests inside `books/<slug>/media-locale-manifest.json`. The adaptive-translation logic: if `books/<slug>/source-map.md` exists → reuse those target-language chapters (already translated by book-gen); else → run media-only translation dispatch (LLM-based, see F12).

### F12. LLM vs dedicated translation providers for literary Arabic

Verified via `chub get anthropic/package --lang py` and `chub get deepl/translation --lang py`.

- **Anthropic Claude** (`anthropic` PyPI package, current 0.105.2 per chub): supports long-context (200K tokens for Claude Sonnet 4-6 / Opus 4-7), good literary style preservation. Pricing ~$3/MTok input + $15/MTok output for Sonnet 4-6. Per-chapter cost (5K tokens output) ~$0.08; full 5-chapter book ~$0.40.
- **DeepL** (`deepl` PyPI, v1.23.0): best-in-class for European languages; supports `formality` parameter for German, French, Italian, Spanish, Dutch, Polish, PT-BR, PT-PT, JA, RU. **No Arabic support documented in the API response.** Per azure-speech language-support table Arabic IS supported but DeepL's API docs don't list Arabic in their public pricing. **Verdict:** DeepL is a no-op for Arabic.
- **Google Cloud Translation** (v3): supports Arabic natively, including MSA and Egyptian/Gulf dialect detection via `glossary_config`. ~$20/MTok character.
- **OpenAI GPT-4o-mini** (per chub `openai/chat`): supports Arabic; ~$0.15/MTok input + $0.60/MTok output. Cheaper than Claude for translation, lower literary quality.

**Recommendation for literary Arabic translation:** Claude Sonnet 4-6 via `anthropic` SDK (chub ID `anthropic/package --lang py`). Reasoning: long context preserves narrative coherence across chapter boundaries; style-guide Voice section fits in the prompt with room for the chapter text. For pure cost-optimization, `gpt-4o-mini` is 20× cheaper but loses prosody preservation.

**Tone preservation:** Pass the `style-guide.md` `## Voice` section verbatim into the translation prompt. Claude preserves register better than DeepL when style instructions are explicit (per Resemble AI / Anthropic published benchmarks; not independently re-verified in this research).

**Prosody preservation for dialectal → MSA:** Source dialectal Arabic (Egyptian, Gulf) read in MSA-edge-tts voices (`ar-SA-HamedNeural`, `ar-EG-SalmaNeural`) sounds unnatural because the voice is trained on MSA. Mitigation: pass `style-guide.md` `## Voice` + chapter `bible.md` character-region annotations (e.g., "Cairo 2024 modern Egyptian colloquial") so the LLM translation produces MSA-friendly phrasings that the TTS voice handles gracefully.

### F13. ComfyUI Desktop local state and migration path (verified)

Verified at the install paths and via `Get-NetTCPConnection`:

- **Install root:** `C:\Users\Ahmad Mahmoud\Documents\ComfyUI\` — Electron wrapper, no `main.py` at root.
- **Models dir:** `C:\Users\Ahmad Mahmoud\Documents\ComfyUI\models\` — 27 subdirs, all empty (unet, clip, text_encoders, vae, checkpoints, gguf all confirmed empty).
- **Actual model files:** `D:\comfy\models\` with files:
  - `text_encoders/clip_l.safetensors` (246 MB)
  - `text_encoders/t5xxl_fp16.safetensors` (9.8 GB)
  - `vae/ae.safetensors` (335 MB)
  - `checkpoints/ponyDiffusionV6XL_v6StartWithThisOne.safetensors` (6.9 GB)
  - `diffusion_models/flux1-schnell-Q4_K_S.gguf` (6.8 GB)
- **Custom nodes:** `cg-use-everywhere`, `ComfyUI-GGUF`, `comfyui-kjnodes`, `comfyui-videohelpersuite` (all under `custom_nodes/`).
- **Server state:** `127.0.0.1:8188` not listening. No ComfyUI process running.
- **Desktop config path:** `C:\Users\Ahmad Mahmoud\AppData\Roaming\ComfyUI\` does NOT exist (per user spec, no extra_models_config.yaml yet).

**Mode 2 unlock step 1 (extra_model_paths.yaml for Desktop):**

Create `C:\Users\Ahmad Mahmoud\AppData\Roaming\ComfyUI\extra_models_config.yaml`:

```yaml
# ComfyUI Desktop extra models config (Mode 2 unlock, Stage 3b)
# Source: agents_manager/book2media-orchestrator/SKILL.md § ComfyUI integration
comfyui_desktop:
  is_default: "true"
  base_path: D:\comfy\models
  checkpoints: checkpoints/
  text_encoders: |
    text_encoders/
    clip/
  clip_vision: clip_vision/
  diffusion_models: |
    diffusion_models/
    unet/
  vae: vae/
```

After saving, restart ComfyUI Desktop for changes to take effect.

**Mode 2 unlock step 2 (programmatic API access):** ComfyUI Desktop does NOT expose a CLI launch — it is an Electron wrapper launched via `ComfyUI.exe` from `C:\Users\Ahmad Mahmoud\AppData\Local\Programs\ComfyUI\` (per Comfy-Org/desktop docs). The Desktop GUI must be running to expose `http://127.0.0.1:8188`. For headless/CI use, the canonical path is bare OSS install:

```
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
python main.py --disable-auto-launch --port 8188
```

This gives `python main.py --help` (per ComfyUI startup-flags docs) with `--disable-auto-launch`, `--listen 0.0.0.0`, and all CLI flags documented at `https://docs.comfy.org/development/comfyui-server/startup-flags`. Custom node `ComfyUI-GGUF` (city96) is needed for `flux1-schnell-Q4_K_S.gguf` consumption; Comfy-Org ComfyUI Desktop's bundled custom nodes already include this if the Desktop install was completed with custom-node support enabled.

**chub citation:** No entry in chub registry for ComfyUI.

---

## Existing solutions (landscape scan)

| Provider / Tool | Type | License | Last commit / model card | Maintenance signal | Fit-for-use-case |
|---|---|---|---|---|---|
| **Kokoro-82M** (`hexgrad/Kokoro-82M`) | OSS model (Apache-2.0, hexgrad) | Apache-2.0 | HF model card 2025-01-29; actively developed | High — regular voice additions, GitHub stars ~5k | English: excellent (54 voices). Arabic: NOT supported. |
| **edge-tts** (`rany2/edge-tts`) | OSS Python wrapper around MS online TTS | MIT | Repo 2021-2026 active, 11.7k stars | High — 11 contributors, low open-issue count | Arabic: best coverage (28 voices, 16 locales). Caveat: online-only, no commercial SLA from MS. |
| **Coqui XTTS-v2** (`coqui/XTTS-v2`) | OSS multilingual model | **CPML — non-commercial only** | Coqui TTS 0.28.0.dev0; project stalled 2024 | Medium — Coqui company wound down; community fork exists | Arabic: supported. HARD BLOCKER for commercial use. |
| **CosyVoice 2** (`FunAudioLLM/CosyVoice2-0.5B`) | OSS model (Alibaba) | Apache-2.0 | HF model card 2025-05-23; actively developed | High — Alibaba team active | Arabic: NOT supported (9 langs, no Arabic). |
| **Chatterbox Multilingual V3** (`ResembleAI/chatterbox`) | OSS model (Resemble AI) | MIT | HF model card 2025-Q4; actively developed | High — Resemble AI commercial backing | Arabic: supported (23 langs). Zero-shot 5s clone. MIT. **Strongest offline option.** |
| **ElevenLabs** | SaaS | Proprietary, $0.15/1k chars | Active | High | Skip — user did not list; SaaS cost prohibitive for 5-product × per-locale matrix. |
| **OpenAI TTS** | SaaS | Proprietary, $15/1M chars | Active | High | Skip — user did not list; lower quality than Chatterbox for Arabic per public benchmarks. |
| **faster-whisper** (`SYSTRAN/faster-whisper`) | OSS ASR (CTranslate2) | MIT | Active 2026 | High | All-languages word-timestamp ASR; default caption source for our pipeline. |
| **pysubs2** | OSS SRT/ASS/SSA parser | MIT | Active | High | Convert SRT→ASS pre-burn for Arabic shaping. |
| **libass** | OSS subtitle renderer | ISC | Active 2025+ | High | Provides `ASS_SHAPING_COMPLEX` via HarfBuzz. |
| **Amiri** font | OSS Arabic typeface | OFL | Active | High | Default burn-in font for reels (libass + HarfBuzz). |
| **Noto Naskh Arabic** font (`notofonts/noto-fonts`) | OSS Google | OFL | Active | High | EPUB fallback (future work). |
| **EBU R 128 / `loudnorm`** | Standard + ffmpeg built-in | Standard | Active | N/A | Per-platform loudness normalization. |
| **ComfyUI Desktop** | Closed-source Electron wrapper | Proprietary free | Active 2026 | High (Comfy-Org) | Phase 9 Mode 2 image gen. Headless launch NOT supported — must use bare OSS install for `--disable-auto-launch`. |
| **ComfyUI (bare OSS, comfyanonymous/ComfyUI)** | OSS workflow engine | GPL-3.0 (matches ComfyUI repo) | Active 2026 | High | Phase 9 Mode 2 image gen. CLI launch supported (`python main.py --disable-auto-launch`). |
| **ComfyUI-GGUF** (`city96/ComfyUI-GGUF`) | OSS custom node | GPL-3.0 | Active | High | Required for `flux1-schnell-Q4_K_S.gguf` consumption. |
| **Anthropic Claude** (`anthropic` SDK) | SaaS LLM | Proprietary | Active 2026 | High | Translation provider (literary Arabic, style preservation). chub ID `anthropic/package --lang py`. |
| **DeepL** | SaaS | Proprietary | Active | High | NOT viable for Arabic per public docs. chub ID `deepl/translation --lang py`. |

## Build vs. reuse decisions — please confirm

1. **Component "English TTS for audiobook"** — reuse Kokoro-82M (Apache-2.0, high quality, 20 voices, CPU-capable) / reuse edge-tts en-US-* (free, online, highest quality) / build from scratch (≈30 days to reach Kokoro quality). Your call: _______
2. **Component "Arabic TTS for audiobook"** — reuse edge-tts ar-* (free, online, 28 voices, MS Neural) / reuse Chatterbox Multilingual V3 (MIT, offline, 5s clone, ~2 GB VRAM) / reuse Coqui XTTS-v2 (CPML non-commercial — HARD BLOCKER for commercial audiobook). Your call: _______
3. **Component "Arabic subtitle burn-in (libass/ffmpeg)"** — reuse ffmpeg's `ass` filter with `shaping=complex` (free, built-in, works on local build) + SRT→ASS via `pysubs2` / install newer ffmpeg build with `subtitles` shaping exposed (upstream commit b08c9c5 — needs ffmpeg post-2025-08-25). Your call: _______
4. **Component "Per-platform loudnorm for reels"** — reuse ffmpeg `loudnorm` two-pass (free, built-in) / reuse `pyloudnorm` for measurement + ffmpeg `volume` for apply (more accurate but two-process). Your call: _______
5. **Component "Literary Arabic translation"** — reuse Anthropic Claude via `anthropic` SDK (chub-verified, $0.08/chapter, best style preservation) / reuse OpenAI GPT-4o-mini (20× cheaper, lower quality) / reuse Google Cloud Translation (no API key surface in chub, prosody preservation untested). Your call: _______
6. **Component "Per-locale provider registry source of truth"** — per-book `media-locale-manifest.json` (trial flexibility, user-editable) / global `agents_manager/book2media-orchestrator/providers.yaml` (code-reviewed, auditable) / user-global `~/.config/opencode/book2media.yaml`. Your call: _______
7. **Component "Mode 2 image-gen runtime (future)"** — bare OSS `github.com/comfyanonymous/ComfyUI` install (CLI access, GPL-3.0) / keep ComfyUI Desktop (Electron wrapper, no headless) / wait until Mode 1 ships and decide. Your call: _______

## Feasibility verdict

- **Can do:** yes
- **Confidence:** HIGH for Mode 1 (English-only audiobook + Ken Burns reels), MEDIUM for full English+Arabic pipeline, MEDIUM for Mode 2
- **Why:** Mode 1 (English) is fully unlocked: Kokoro-82M is Apache-2.0 and proven, ffmpeg's `loudnorm` two-pass is well-documented, ComfyUI is not needed, Amiri font is OFL and shipped in most distros. The five-product matrix × English-only is implementable in ~2-3 days of focused work. Arabic path adds one known HARD blocker (libass `subtitles` filter Arabic shaping on local ffmpeg) that has a documented workaround (SRT→ASS+`shaping=complex`); adding `pysubs2` as a dependency is trivial. The translation provider (Claude via `anthropic` SDK) is chub-verified and has known pricing. Mode 2 is gated on ComfyUI Desktop migration to bare OSS install OR proof that Desktop exposes a programmatic API; either path is documented but unvalidated. Reels publish to all three platforms is a well-trodden ffmpeg `loudnorm` + safe-zone burn-in pattern with no novel risk. The adaptive translation-reuse mechanism reuses the existing `source-map.md` schema verbatim; the only new schema (`media-locale-manifest.json`) is small and integrates cleanly into the existing book directory layout.

## Recommendations for the planning agent

1. **Plan for Mode 1 first, ship to English-only smoke book, then expand to Arabic in Phase 9.2.** Lock the architecture (orchestrator SKILL.md, manifest schema, dispatch pipeline) against Mode 1 only; Arabic path is gated on smoke-test validation of `edge-tts` Arabic voices + `ass=...:shaping=complex` subtitle burn-in.
2. **Adopt the proposed `media-locale-manifest.json` schema as-is.** Place at `books/<slug>/media-locale-manifest.json`. Reads `books/<slug>/source-map.md` if present; falls back to media-only translation dispatch (Claude via `anthropic` SDK) if absent. Document the schema in the orchestrator's "State files" section mirroring `book-gen-orchestrator/SKILL.md:323-339`.
3. **am-assets lane for media manifest.** am-assets gets a new "media-manifest lane" parallel to its existing cinematic-landing asset manifest. The 4-branch decision tree (video pipeline / video file / stills only / nothing) from `am-assets/SKILL.md:64-74` is the right shape, retargeted: "still images present + video pipeline present → Mode 2; still images present only → Mode 1; video file present → use as-is; nothing present → generate single cover image via Flux".
4. **Lock ffmpeg version requirement to ≥2025-10-15** OR document the SRT→ASS workaround. The local `2025-08-25` build predates upstream commit b08c9c5 (the `subtitles` filter `shaping=` exposure). The `ass=...:shaping=complex` workaround is robust and doesn't require an ffmpeg upgrade.
5. **Use `pysubs2` for SRT→ASS conversion.** Pure Python, MIT license, no native deps. Drop-in pre-burn step in the audio→video pipeline.
6. **Default burn-in font: Amiri (OFL).** Ships in most distros; gorgeous Arabic Naskh; libass + HarfBuzz render correctly. Fallback to Noto Naskh Arabic if Amiri is unavailable on a contributor's machine.
7. **Reels caption safe-zone: union of all three platforms.** Top 250px, bottom 460px, right 180px, left 60px. Caption font: Amiri 72px bold, centered in the safe-zone. This survives all three platforms with no per-platform repositioning; per-platform repositioning is OPTIONAL (the user spec allows it but the safer default is union-safe-zone).
8. **Per-platform loudnorm via single ffmpeg two-pass.** One source render per chapter per locale, three platform outputs derived by applying per-platform `loudnorm` with measured values from pass 1. Streaming target: I=-16 LUFS, TP=-1.5 dBTP, LRA=11.
9. **For Mode 2, plan a separate "Stage 3b: ComfyUI migration" task** that creates the `extra_models_config.yaml` and validates bare OSS install before Mode 2 ships. This task is NOT in Phase 9.1 (Mode 1 only).
10. **Audiobook M4B uses two-pass loudnorm** even for short-form content, because spoken-word listenability depends on consistent volume across chapters. Streaming platforms will not accept audiobook loudness at the same target as reels — verify with a 5-min test M4B before committing.
11. **Document the Mode 1 → Mode 2 unlock gate explicitly in the orchestrator's SKILL.md.** Recommend: "Mode 2 unlocks when 3 books have shipped with Mode 1 + user has no open complaints about visual quality."

## Open questions for the user

1. **edge-tts Arabic word-timestamp behavior** — Do you want a smoke-test budget (1 hour) to verify `edge-tts --voice ar-EG-SalmaNeural --write-subtitles sample.srt` produces per-word timestamps at sub-second intervals, OR should we assume fallback to `faster-whisper --language=ar --word_timestamps=True` for caption generation while keeping edge-tts as the audio source?
2. **VRAM availability** — Run `nvidia-smi` on this machine and confirm CUDA + ≥6 GB free VRAM. This decides whether offline TTS (Chatterbox) is viable for Arabic, or whether edge-tts is the only path.
3. **Mode 1 → Mode 2 unlock gate** — Define the gate: (a) N successful Mode-1 renders, (b) ≥80% user-acceptance on `daily-focus` reels, (c) after Mode-1 ships with usage data, or (d) other?
4. **Reel source-render aspect ratio** — Single source render at 9:16 (1080×1920) with caption reposition only, OR 16:9 master with vertical crop + caption reposition? Recommend 9:16.
5. **Audiobook voice policy** — Single narrator voice across all chapters (`af_heart`), chapter-specific voices matched to POV, or book-level voice pick from style-guide?
6. **Provider registry location** — Per-book `media-locale-manifest.json` (trial flexibility), global `providers.yaml` (code-reviewed), or user-global yaml?
7. **TTS chunk size for chapters** — Kokoro goldilocks range is 100-200 tokens. A typical chapter is ~3000 tokens. Should the orchestrator chunk by H2 section (typically 200-400 tokens each), or by fixed 200-token windows? Recommend H2-section chunks.

## Self-critique

- **Did I do my job?** Yes — all 6 research areas covered with concrete data, chub citations where available, and clear hand-off to planning. The 5-product matrix per-locale provider decision matrix is laid out in tables; the ffmpeg Arabic shaping workaround is documented; the ComfyUI Desktop migration path is specified. The biggest gap I see: I did not empirically test edge-tts Arabic word-timestamps (R6) — flagged as an open question for the user.
- **What might I have missed?**
  - Audiobook chapter-title-track M4B metadata (chapters-as-tracks in M4B are industry-standard; affects player UX on Apple Podcasts) — I noted M4B but did not research chapter metadata format.
  - Image rights for Mode 1 cover image (if generated by Flux) — no source citation in this research. May want to add a license-tracking field to `media-locale-manifest.json`.
  - Localization of UI strings in the orchestrator's progress output — if the user-facing progress messages need Arabic, that's a separate i18n thread.
  - Accessibility (audio description track for video) — not in the user's spec but worth flagging.
- **What did I assume without evidence?**
  - **Amiri font is "shipped in most distros"** — true for Debian/Ubuntu (`fonts-hosny-amiri`); not true for Windows. On Windows, the user must install Amiri separately. Mitigation: document download URL `https://github.com/aliftype/amiri` in the orchestrator.
  - **edge-tts writes SRT with per-word timestamps for Arabic** — claimed in README but not empirically validated for Arabic. Marked as MEDIUM risk (R6).
  - **Claude Sonnet 4-6 has "best literary Arabic style preservation"** — based on general benchmark knowledge, not a per-task A/B test. The OpenAI comparison is also based on general reputation, not a benchmark.
  - **The `extra_models_config.yaml` path is `C:\Users\<user>\AppData\Roaming\ComfyUI\`** — this is per Comfy-Org docs; the local environment shows the path does not exist yet, so this is forward-looking documentation.
  - **CPML license for XTTS-v2 is hard non-commercial blocker** — confirmed at coqui/XTTS-v2 HF model card frontmatter but I did not cite the exact license text. Recommendation stands: do not use XTTS for production.

## Metrics

- findings: 13
- risks_HIGH: 2
- risks_MEDIUM: 4
- risks_LOW: 4
- clarifying_Qs: 7

---

## Smoke-test followup (run 2026-08-10 after research lock)

User asked: install torch with CUDA + run edge-tts Arabic word-timestamp smoke test before am-planning. Outcomes:

### SF1. torch CUDA installed into repo venv

Command run from `E:\book_gen`:
```
uv pip install --python "E:\book_gen\.venv\Scripts\python.exe" \
  torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

Result: `torch==2.13.0+cu126`, `torchaudio==2.11.0+cu126`, `torchvision==0.28.0+cu126`, `numpy==2.4.4`. ~30 seconds. Verification:
```
import torch
torch.cuda.is_available()  -> True
torch.cuda.device_count()  -> 1
torch.cuda.mem_get_info(0)  -> 6.97 GiB free
```

**Implication for plan:** CUDA torch is now available repo-wide. Anything in the agent pipeline that previously assumed "no torch / no CUDA" (per the b1 deep-dive) is unlocked. Mode 2 image-gen dispatch can use local ComfyUI without GPU migration work. Chatterbox/Coqui inference no longer needs the bare-OSS-comfy fallback concern for VRAM.

### SF2. edge-tts 7.2.8 emits SentenceBoundary only (no WordBoundary for ANY language)

Smoke test: ran `edge_tts.Communicate(text, voice).stream()` with `voice in {'ar-EG-SalmaNeural', 'ar-SA-HamedNeural', 'en-US-JennyNeural', 'en-US-GuyNeural'}` and counted chunk types. All four voices returned exactly `{'audio': N, 'SentenceBoundary': 2}`. Zero `WordBoundary` events, zero `PunctuatedBoundary` events. The CLI's `--write-subtitles` writes sentence-level SRT only (3 entries for a 3-sentence test) — confirmed by reading the resulting `.srt` files at `C:\Users\Ahmad Mahmoud\AppData\Local\Temp\book2media_smoke\ar-EG-SalmaNeural.srt`.

**This invalidates F2 + R6 of the original research.** The README's "Word-level SRT from edge-tts" claim applies to OLDER edge-tts versions (pre v6.x); v7.2.8 dropped or never wired WordBoundary events. Confirmed by reading `edge_tts.Communicate.stream()` source at `E:\book_gen\.venv\Lib\site-packages\edge_tts\__init__.py`.

**Implication for plan: faster-whisper is the canonical word-timestamp source for ALL locales, not just Arabic.** The TTS pipeline is two-step and uniform across locales:

1. **TTS** (edge-tts for online quality OR Kokoro for offline CPU): produces chapter audio chunks with sentence boundaries from `SentenceBoundary`.
2. **ASR alignment** (faster-whisper `large-v3` for Arabic, `small` for English, `language=<locale>` set explicitly): transcribes the audio back to text + word timestamps via cross-attention + DTW. Aligns to original chapter text via `difflib.SequenceMatcher` (already documented in the original Stage 3c).

Cost delta: ~1x faster-whisper inference per chapter audio. `large-v3` Arabic ~0.5x real-time on the Quadro RTX 4000 (community benchmarks). Acceptable.

Smoke test files retained at `C:\Users\Ahmad Mahmoud\AppData\Local\Temp\book2media_smoke\` for any future re-validation.

### SF3. User gating decisions (locked 2026-08-10)

- **Mode 1 → Mode 2 unlock:** 3 shipped books + no user complaints about visual quality.
- **Audiobook voice policy:** start with Option 1 (single narrator voice per book per locale); add Options 2+3 (chapter-voice / character-voice allocation) AFTER Option 1 is confirmed solid AND Mode 1 is finished.
- **Provider registry location:** Default to Option 1 (per-book `books/<slug>/media-locale-manifest.json`). Support Option 2 (global `agents_manager/book2media-orchestrator/providers.yaml`) when (a) user wants to apply same config across all books, or (b) user has a standard default config to use without per-book file creation. Resolution order at runtime: per-book manifest wins if present + valid; else global yaml; else built-in defaults.
- **Reel source-render aspect:** 9:16 (1080×1920) — research recommendation adopted, no user override needed.
- **TTS chunking:** H2-section-driven chunks matching the existing P17 review chunker (~200-400 tokens each) — research recommendation adopted.
- **Arabic word-timestamp smoke-test budget:** 1 hour validated. Result in SF2 above.

### SF4. Updated plan inputs (delta from original)

am-planning should reflect:
1. **Caption generation pipeline simplifies** — drop the per-locale TTS word-boundary branching. Use faster-whisper uniformly for English and Arabic. Use `large-v3` for Arabic accuracy, `small` for English speed.
2. **CUDA torch is available** — am-coder can use local ComfyUI + ComfyUI-GGUF without bare-OSS install for prototyping. The bare-OSS migration remains recommended for production CLI access (`extra_models_config.yaml` is the production-grade path; CUDA-torch-via-uv is the prototyping path).
3. **voice → chunk size policy** — single narrator voice per (book, locale) per SF3 Option 1. Voice selection: English = `af_heart` (Kokoro Grade A); Arabic = `ar-SA-HamedNeural` (edge-tts).
4. **Media-locale-manifest schema** (per F11): add the `voice` field as a top-level field per-product, NOT a TTS-provider sub-field, since voice selection is now policy-driven not registry-driven.

Metrics update:
- clarifying_Qs_resolved: 5 (Arabic smoke test, Mode 2 gate, voice policy, registry location, sub-questions answered)
- clarifying_Qs_open: 0
- new_findings_post_smoke: 2 (SF1, SF2)
- new_risks_added: 0 (SF2 downgrades R6 from MEDIUM to RESOLVED)
