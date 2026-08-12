---
name: book2media-orchestrator
description: Drive the 8-phase book2media pipeline (orchestrator+manifest -> TTS Kokoro -> TTS edge-tts -> caption -> ffmpeg audiobook M4B -> ffmpeg video+reels -> smoke test -> docs+integration) by routing work through am-assets, am-coder, and am-review. Load when the user signals they want media produced from a book (Phase 9 of the book-gen pipeline) via the `--media` flag. Master invokes this skill at Phase 9 only.
allowed-tools: Read, Write (books/<slug>/**, share/notes/99_progress_<task-id>.md, share/handoffs/00_user_task_<task-id>.md, tasks/<id>.md), task (am-assets, am-coder, am-review), Bash (read-only)
triggers: --media, produce media, book2media, audiobook, m4b, video, reels, vertical trailer, Phase 9, media manifest
preamble-tier: 3
version: 0.1.0
---

# Book2Media Orchestrator

> **This is a skill, not a specialist.** There is no `opencode.jsonc` roster slot and no master dispatch route dedicated to book2media. Master loads this file when the user passes `--media` (or equivalent) at Phase 9 of the book-gen pipeline and drives the 8-phase pipeline by dispatching the existing am-assets, am-coder, and am-review specialists. The book-gen-orchestrator's Phase 8 (`build_exports`) must have completed and the user must have approved the media manifest produced in Phase 1 below before Phase 2 fires.

## Goal

Take an approved book (`books/<slug>/chapters/*.md` all `approved`) and produce five media products per locale (audiobook M4B, horizontal Mode-1 video, vertical trailer, vertical reel x 3 platforms), respecting per-locale provider resolution (per-book manifest wins over global `providers.yaml` wins over built-in defaults), adaptive translation reuse from `books/<slug>/source-map.md` when present, and the locale-correctness review gate (font + voice + RTL).

The orchestrator reuses the existing 3 specialists:

1. **am-assets** (media-manifest lane, parallel to cinematic-landing 4-branch tree) -- produces `books/<slug>/media-locale-manifest.json`.
2. **am-coder** (per Phase 9 sub-task) -- writes the TTS, caption, and ffmpeg scripts and runs them.
3. **am-review** (locale-correctness gate, parallel to the book-reviewer 2-pass dispatch) -- validates font + voice + RTL + per-platform loudness + manifest consistency.

No new agent is registered. No `opencode.jsonc` edit is required.

## Phase map (orchestration, not implementation)

| Phase | Output | Dispatched to | User gate? |
|---|---|---|---|
| 1 -- Orchestrator + Manifest | `books/<slug>/media-locale-manifest.json` (validated) | am-assets (manifest lane); am-coder (validator CLI if not already in book-kit) | yes (per-product locale + skip) |
| 2a -- TTS (Kokoro + registry) | `chapters/ch-NN-en.wav` (per-chapter English audio), chunk manifest | am-coder, am-review | no |
| 2b -- TTS (edge-tts + integration) | `chapters/ch-NN-ar.wav` (per-chapter Arabic audio), chunk manifest | am-coder, am-review | no |
| 3 -- Caption (faster-whisper) | `chapters/ch-NN-<locale>-words.json` + `ch-NN-<locale>.srt` + `ch-NN-<locale>.ass` (Amiri RTL) | am-coder, am-review | no |
| 4a -- ffmpeg audiobook M4B | `exports/audiobook-<locale>.m4b` (two-pass loudnorm, chapter markers) | am-coder, am-review | no |
| 4b -- ffmpeg video + reels | `exports/video-horizontal-m1-<locale>.mp4` + `video-vertical-trailer-<locale>.mp4` + `video-vertical-reel-<locale>-{yt,ig,tt}.mp4` | am-coder, am-review | no |
| 5 -- Smoke test (daily-focus ch-01) | `share/notes/05_smoke_T-2026-08-10-001.md` | am-coder, am-review | no |
| 6 -- Docs + integration | `book-kit/docs/TOOLKIT.md` + `book-kit/docs/SCRIPTS.md` + `book-kit/CLAUDE.md` + `book-kit/VERSION` + `book-kit/CHANGELOG.md` | am-coder | no |

Phase 1 has already landed in T-2026-08-10-001 (this task) -- the orchestrator SKILL.md, the providers.yaml default, the media_manifest.py validator, the am-assets lane amendment, the am-review locale-correctness gate amendment, and the book-gen-orchestrator line 348 amendment. Phases 2-6 ship in subsequent dispatches.

## Available tools (canonical reference)

The canonical tool catalog is `book-kit/docs/TOOLKIT.md` -- when this skill or any specialist needs to invoke a tool, look it up there first. The TOOLKIT file is the registry of record. Do not duplicate tool lists in agent SKILL.md files. If a tool is missing from TOOLKIT, add it there.

Per Phase 9, the following tools are added to the catalog (Phase 1 already landed in T-2026-08-10-001):

- `book-kit/book_workflow/scripts/media_manifest.py` -- validator + generator for `books/<slug>/media-locale-manifest.json`. Schema validation via `jsonschema`; provider resolution per three-tier rule. **Invoked directly via the script path** (NOT as a Python module) because `book-kit/` does not ship an `__init__.py` package marker.

## Phase 1 -- Orchestrator + Manifest (dispatch am-assets)

### Inputs

- Confirmed book at `books/<slug>/` with all chapters `approved` and `build_exports.py` already run (Phase 8 of book-gen).
- User's `--media` flag and any per-locale overrides from the user task.
- `agents_manager/book2media-orchestrator/providers.yaml` (global default registry, already written).
- `books/<slug>/source-map.md` (optional; present only when the book was generated in translation mode).

### Outputs

- `books/<slug>/media-locale-manifest.json` -- validated against the JSON Schema embedded in `book-kit/book_workflow/scripts/media_manifest.py` at L96-L145 (no standalone `.json` file). The manifest lists every product (audiobook M4B, video-horizontal-m1, video-vertical-trailer, video-vertical-reel) per locale with `tts_provider`, `voice`, `skip`, `translation_required`, and `cover_image_fallback_ladder`.
- `share/notes/03a_assets_phase9_<task-id>.md` -- am-assets work summary.
- `share/handoffs/03a_assets-to-coder-<task-id>.md` -- handoff to am-coder for Phase 2.

### Per-product schema (excerpt)

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

### Dispatch

1. `task(subagent_type="am-assets", prompt=...)` with the user task + per-locale hints + the providers.yaml path. am-assets reads the 4-branch decision tree at `agents_manager/assets/SKILL.md` retargeted for books (stills present only -> Mode 1; stills + video pipeline -> Mode 2 deferred; video file -> use as-is; nothing -> generate single cover image).
2. am-assets writes `books/<slug>/media-locale-manifest.json` and validates it via:

```sh
py -3 "<repo-root>/book-kit/book_workflow/scripts/media_manifest.py" validate \
    "books/<slug>/media-locale-manifest.json"
```

Exit codes: 0 = ok, 2 = schema/field error (emits a JSON-path line pointing at the offending field), 3 = `jsonschema` package absent (install hint surfaced to user), 4 = `providers.yaml` malformed.

### User gate (required)

Master presents the manifest to the user. The user may:

- Approve as-is.
- Override per-product voice via `voice: <new>` in the per-book manifest (wins over global default).
- Mark a product `skip: true` to drop it from the build.
- Add a locale not present in `providers.yaml` (master surfaces the rule: add the locale block to `providers.yaml` first, then re-run the validator).

### Exit criteria

- Manifest exists at the per-book path, validates exit 0 against the schema, every locale listed under `target_locales` has a matching entry in `providers.yaml` (case-sensitive), no product has empty `voice: ""` (empty-string handling rule per providers.yaml rule 2).
- Manifest's `cover_image_fallback_ladder` resolves to at least one existing file path on disk.

## Phase 2a -- TTS (Kokoro + registry, English)

### Inputs

- Phase 1 manifest (`source_locale` typically `en`, Kokoro path for English audiobook).
- `chapters/ch-NN.md` per chapter.
- Kokoro-82M (Apache-2.0) installed into the repo venv via `uv pip install kokoro-onnx`.

### Outputs

- `chapters/ch-NN-en.wav` (per-chapter English audio).
- `chapters/ch-NN-en.chunks.json` (`[{idx, h2, start_s, end_s, text_tokens}]`).
- Per-book `exports/audiobook-en.partial.m4b` (concatenated but not yet loudnorm-pass-2'd).

### Dispatch

am-coder runs the H2-driven chunker + Kokoro synthesis. Per SF2 the chunker reuses the P17 algorithm at `book-kit/book_workflow/scripts/chunk_chapter.py` (T2aT3) targeting <=400 tokens per chunk per Kokoro's goldilocks range. Synthesis script is `book-kit/book_workflow/scripts/synthesize_chapter.py` (T2aT4).

### Exit criteria

- `chunk_chapter.py --book books/<slug> --chapter ch-NN` emits the expected chunk count for that chapter.
- `synthesize_chapter.py --book books/<slug> --chapter ch-NN --locale en --voice af_heart` produces a non-empty `.wav` with duration within +/- 5% of expected.
- `pytest book-kit/tests/test_chunk_chapter.py book-kit/tests/test_synthesize_chapter.py` passes.

## Phase 2b -- TTS (edge-tts + integration, Arabic + translation reuse)

### Inputs

- Phase 1 manifest (Arabic products).
- If `books/<slug>/source-map.md` exists -> reuse the translated chapters already produced by book-gen's Branch A review (T2bT1).
- Else -> am-coder dispatches a one-shot translation pass to am-coder with `anthropic` SDK (T2bT2; chub-verified `anthropic/package --lang py`).

### Outputs

- `chapters/ch-NN-ar.wav` (per-chapter Arabic audio).
- `chapters/ch-NN-ar.chunks.json` (same shape as 2a).
- `chapters/ch-NN-ar.txt` (translated chapter prose; only if media-only translation ran).

### Exit criteria

- Arabic audio duration within +/- 5% of English audio duration (sentence-count heuristic; not enforced strictly).
- `edge-tts` voice reachability check passes: `check_edge_tts.py --voice ar-SA-HamedNeural` exits 0.

## Phase 3 -- Caption (faster-whisper + difflib alignment)

### Inputs

- `chapters/ch-NN-<locale>.wav` from Phase 2.
- `chapters/ch-NN.md` (English source) or `chapters/ch-NN-ar.txt` (translated Arabic source) for alignment.

### Outputs

- `chapters/ch-NN-<locale>-words.json` (`[{word, start, end, probability}]`).
- `chapters/ch-NN-<locale>.srt` (aligned to chapter text via `difflib.SequenceMatcher`).
- `chapters/ch-NN-<locale>.ass` (Amiri font, `WrapStyle=2`, `bidi=1` for Arabic).

### Why faster-whisper, not edge-tts word boundaries

Per SF2: edge-tts 7.2.8 emits `SentenceBoundary` only, no `WordBoundary` events for any language. The README's word-level SRT claim applies to older edge-tts versions. faster-whisper is canonical for ALL locales; `large-v3` for Arabic accuracy, `small` for English speed, `language=<locale>` set explicitly.

### Dispatch

am-coder runs `transcribe_chapter.py` -> `align_srt.py` -> `srt_to_ass.py`. Amiri font installed via `install_amiri.py` (Windows `%LOCALAPPDATA%\fonts\Amiri\`).

### Exit criteria

- Word JSON non-empty with median word duration < 0.8s.
- SRT cue count within +/- 10% of chapter sentence count.
- `.ass` `[V4+ Styles]` block contains the literal string `Amiri`.

## Phase 4a -- ffmpeg audiobook M4B

### Inputs

- Per-chapter `<locale>.wav` from Phase 2.
- `chapters/ch-NN.txt` (one chapter title per line) for the M4B chapter-marker track.

### Outputs

- `exports/audiobook-<locale>.m4b` (AAC 64k mono, M4B-native chapter markers, two-pass loudnorm with I=-19 LUFS / TP=-2 dBTP / LRA=11 for spoken-word listenability).

### Dispatch

am-coder runs `assemble_audiobook.py` (T4aT2). The voice-policy check rejects if the synthesized voice does not match the per-locale voice in the manifest.

### Exit criteria

- `ffprobe -show_chapters exports/audiobook-<locale>.m4b` reports one chapter per `ch-XX.md`.
- `ffmpeg -af loudnorm=...:print_format=json -f null -` reports integrated loudness within +/- 0.5 LU of -19.

## Phase 4b -- ffmpeg video + reels

### Inputs

- Per-chapter `<locale>.wav` + `<locale>.ass` from Phases 2 + 3.
- Cover image at the first entry of `cover_image_fallback_ladder` (resolved by am-assets in Phase 1).
- Per-platform loudnorm targets from `providers.yaml` `reels_targets:`.

### Outputs

- `exports/video-horizontal-m1-<locale>.mp4` (1920x1080, single cover + Ken Burns zoompan + waveform overlay).
- `exports/video-vertical-trailer-<locale>.mp4` (1920x1080, 60-90s teaser across all chapters).
- `exports/video-vertical-reel-<locale>-yt.mp4`, `...-ig.mp4`, `...-tt.mp4` (1080x1920 source render, three per-platform loudnorm outputs).

### Dispatch

am-coder runs `assemble_video_horizontal.py` (T4bT1 / T4T3), `assemble_video_trailer.py` (T4bT2 / T4T4), `assemble_reel.py` (T4bT3 / T4T5). The shared `lib/ffmpeg_zoompan.py` wraps the **critical supersample pattern** (`scale=8000:-1` BEFORE `zoompan` per F8 -- without the supersample, zoompan produces blurry output).

### Exit criteria

- Every reel non-empty.
- Per-platform loudnorm targets met per F8 (`yt`/`tt`: -14 LUFS / -1 dBTP; `ig`: -16 LUFS / -1.5 dBTP).
- Arabic reels show `ass=...:shaping=complex` in the ffmpeg argv (verify via `ffprobe` of the rendered file or the assembler's stderr log).

## Phase 5 -- Smoke test (daily-focus ch-01)

### Inputs

- The locked output spec from Phases 2-4 (audio + SRT + .m4b + reels).
- `books/daily-focus/ch-01.md` (the 2,465-word smoke-test reference chapter).

### Outputs

- `share/notes/05_smoke_<task-id>.md` with per-product pass/fail.

### Exit criteria

- Pass entries for: 1 audiobook per locale, 2 videos per locale, 6 reels per locale.
- Per-platform loudness targets met.
- No CRITICAL findings.
- Manual SRT cue spot-check passes for ch-01 (one cue per sentence, +/- 0.2s tolerance).

## Phase 6 -- Docs + integration

### Inputs

- All scripts shipped in Phases 2-4.
- `book-kit/docs/TOOLKIT.md`, `book-kit/docs/SCRIPTS.md`, `book-kit/CLAUDE.md`, `book-kit/VERSION`, `book-kit/CHANGELOG.md`.

### Outputs

- TOOLKIT.md Pipeline map gains a Phase 9 row + per-tool catalog entries for `media_manifest.py` + every new media-assembler script.
- SCRIPTS.md gains per-CLI entries for every new script.
- CLAUDE.md amends the "Book Kit ships ONLY 6 agents" rule to acknowledge `am-assets` dispatch at Phase 9 only.
- VERSION bumped to `1.3.0`.
- CHANGELOG.md gains a `## v1.3.0 -- <theme> (2026-08-10)` block.

### Exit criteria

- `python3 scripts/validate-frontmatter.py` exits 0.
- All 14 new scripts have an entry in TOOLKIT.md + SCRIPTS.md.
- `git diff book-kit/` shows only the dispatched files modified (no drift).

## State files (master + specialists, all under `books/<slug>/`)

- `media-locale-manifest.json` -- Phase 1 (am-assets writes; am-coder reads; am-review validates).
- `chapters/ch-NN-<locale>.wav` -- Phase 2 (am-coder).
- `chapters/ch-NN-<locale>.chunks.json` -- Phase 2 (am-coder).
- `chapters/ch-NN-<locale>-words.json` -- Phase 3 (am-coder).
- `chapters/ch-NN-<locale>.srt` -- Phase 3 (am-coder).
- `chapters/ch-NN-<locale>.ass` -- Phase 3 (am-coder).
- `exports/audiobook-<locale>.m4b` -- Phase 4a (am-coder).
- `exports/video-horizontal-m1-<locale>.mp4` -- Phase 4b (am-coder).
- `exports/video-vertical-trailer-<locale>.mp4` -- Phase 4b (am-coder).
- `exports/video-vertical-reel-<locale>-{yt,ig,tt}.mp4` -- Phase 4b (am-coder).
- `share/notes/03a_assets_phase9_<task-id>.md` -- Phase 1 (am-assets work summary).
- `share/handoffs/03a_assets-to-coder-<task-id>.md` -- Phase 1 (am-assets -> am-coder handoff).
- `share/reports/04_review_phase9_<task-id>.md` -- Phase 4 (am-review locale-correctness gate).
- `share/notes/05_smoke_<task-id>.md` -- Phase 5 (am-coder writes; am-review counter-signs).

## Boundaries (this skill, master enforces)

- Master CAN edit `books/<slug>/media-locale-manifest.json` directly for one-off overrides (voice, skip, locale addition).
- Master CANNOT write the manifest from scratch -- that is am-assets' lane. Master only edits an existing manifest the user has approved.
- Master CANNOT skip the Phase 1 user gate.
- Master CANNOT skip the am-review locale-correctness gate at Phase 4.
- Master MUST respect `max_fix_loops = 3` per phase's review loop (same rule as the controller's build/review cycle).
- Master MUST close the task when the user says "done" OR when all 6 phases land clean.

## Relationship to the existing agents_manager pipeline

- `book2media` runs AFTER the controller's book-gen pipeline completes (Phases 0-8 of book-gen must be `approved`). It does not nest inside the controller's research -> plan -> build -> review cycle.
- `book2media` does NOT use the controller's `share/notes/01_research_<id>.md` / `02_plan_high_<id>.md` / `03_coder_summary_<id>_<phase>.md` naming for its research/plan outputs (those were already produced during book-gen planning). It DOES use `share/notes/03_coder_summary_<task-id>_ph<N>.md` for per-phase coder summaries per the controller convention.
- `book2media` DOES use `share/notes/99_progress_<task-id>.md` for the master's recovery ledger.
- `book2media` DOES use `share/reports/04_review_<task-id>_phase9.md` for review outputs (suffixed to avoid collision with book-gen reviews).
- `book2media` uses `books/<slug>/**` for per-book artifacts (NOT `share/`).

## Smoke-test entry point

If the user asks for a Phase 9 smoke test (no real book), default to the `books/daily-focus/` skeleton from the book-gen Phase 7 smoke test:

- Chapter: `books/daily-focus/ch-01.md` (2,465 words).
- Manifest: stub with `audiobook-en`, `audiobook-ar`, `video-horizontal-m1-en`, `video-horizontal-m1-ar`, `video-vertical-reel-en`, `video-vertical-reel-ar` (skip trailer to keep wall-clock under 2 hours).
- Per-locale voice: English = `af_heart` (Kokoro); Arabic = `ar-SA-HamedNeural` (edge-tts).

After the smoke run, the user has a real `books/daily-focus/exports/` tree with 1 audiobook, 2 videos, 6 reels to inspect.

## ASCII policy

Every file this skill writes (or that the specialists write when invoked from this skill) MUST be ASCII-only. No em-dashes (use `-` or `--`), no curly quotes (use straight `"` and `'`), no box-drawing characters. The locale-correctness gate at Phase 4 validates ASCII-only on every text artifact produced (manifest + chunk JSONs + captions + ASR JSON + any markdown report).
