# Plan Review — Developer Experience Angle — T-2026-08-10-001 (book2media)

**Date:** 2026-08-10
**Sub-agent:** planning
**Angle:** plan-devex (developer-facing surface: manifest schema, providers.yaml, new scripts, invocation ergonomics)
**Plan reviewed:** `share/notes/02_plan_T-2026-08-10-001_book2media.md`

---

## Findings

### F1. The developer-facing surface is well-organized: manifest + yaml + 14 scripts.

Phase 9 adds the following dev surface:
- **1 manifest per book:** `books/<slug>/media-locale-manifest.json` (schema-validated by `validate_media_manifest.py`)
- **1 global config:** `agents_manager/book2media-orchestrator/providers.yaml`
- **14 new scripts in `book-kit/book_workflow/scripts/`:** check_tts_deps, check_edge_tts, check_whisper_deps, chunk_chapter, synthesize_chapter, transcribe_chapter, align_srt, srt_to_ass, install_amiri, assemble_audiobook, assemble_video_horizontal, assemble_video_trailer, assemble_reel, validate_media_manifest

That's a lot of scripts but each has a single clear purpose (per book-kit hardening rule: one script = one action). The CLI shapes should all be:

```sh
python <script>.py --book <dir> [--chapter ch-NN] [--locale <locale>] [--out <path>]
```

This is the established book-kit convention. **Good.**

### F2. Missing ergonomic feature: `--dry-run` on every script.

For a developer integrating Phase 9 into a new book project, the first thing they'll do is "what would this script produce?" Today, the answer is "run it and check `exports/`" — which is **destructive** (some scripts overwrite the output file).

The book-kit precedent is mixed: `pin_deps.py` and `bilingual_smoke.py` have `--dry-run`; `book_check.py` doesn't (it's read-only). The new media scripts should follow the destructive-script pattern.

**Recommendation:** every Phase 9 script that produces output should accept `--dry-run` (default: print the ffmpeg argv + the output path without running). This is a 5-line addition per script.

### F3. Missing ergonomic feature: `--from <product-id>` to skip already-done work.

The pipeline has 5 products × N chapters. If a developer runs Phase 9, hits a failure on chapter 3 of the audiobook, fixes it, and re-runs, they don't want to re-synthesize chapters 1-2 (each chapter is ~9 min of TTS + ~60 min of ASR for Arabic).

**Recommendation:** each Phase 9 script should accept `--from <chapter-id>` (skip chapters before this) and `--only <chapter-id>` (skip all other chapters). Default: process all chapters. The manifest's `skip: true` flag covers the per-product skip case.

### F4. The T2T2 edge-tts validator is a great DX touch — but it should be runnable as a pre-flight check.

`check_edge_tts.py` confirms voice reachability. A developer setting up Phase 9 for the first time will want to run this **before** kicking off the full pipeline. The plan's T2T2 task is to write the script, but the dispatch prompt to `am-coder` should explicitly require: "this script is invokable standalone as a pre-flight check; prints reachable voices with their network round-trip time."

**Recommendation:** T2T2 should also write `book-kit/docs/SCRIPTS.md` entry specifying the pre-flight usage pattern: "Run this once after install + before any TTS synthesis; if it exits non-zero, the offline-online boundary is broken."

### F5. The `install_amiri.py` script is a nice DX touch but should be idempotent.

The plan's T3T5 says: "Amiri font installer: download latest `.ttf` bundle, extract to `%LOCALAPPDATA%\fonts\Amiri\`." If a developer runs it twice, it should:
- (a) Skip the download if Amiri is already installed (check `fc-list` on Linux/macOS or registry on Windows).
- (b) Skip the extract if the target directory is populated.
- (c) Print "Amiri already installed at <path>" and exit 0.

**Recommendation:** T3T5 should be idempotent. Standard book-kit hardening rule.

### F6. The `validate_media_manifest.py` script needs a `--init` mode.

A developer creating their first `media-locale-manifest.json` for a new book has no scaffold. They'll hand-write the JSON, hit a schema validation error, fix it, hit another, fix it, etc.

**Recommendation:** add `--init` mode to `validate_media_manifest.py`: walks the book's `chapters/` directory, reads `intake.md` for the source locale, emits a stub manifest with one product per (locale × product-matrix) combination, all `skip: false`, all `voice` defaulted from `providers.yaml`. The developer edits the stub.

### F7. The `providers.yaml` resolution rules are under-documented.

The plan's T1T6 says: "Write `agents_manager/book2media-orchestrator/providers.yaml` global default with per-locale provider resolution rules; document resolution order per-book > global > built-in."

A developer reading `providers.yaml` needs to know:
- What is the resolution order when both per-book manifest and global yaml specify a voice?
- What is the built-in default for an unknown locale?
- What happens when the per-book manifest specifies `voice: ""` (empty)?
- What happens when the global yaml has a typo in the locale name?

**Recommendation:** T1T6 should include a `## Resolution rules` section in the yaml itself, with worked examples for each of the 4 cases above.

### F8. The `book_check.py` media-manifest gate (T1T7) needs clear UX when the manifest is missing.

Per review-eng F6: if `book_check.py` validates the manifest, but the manifest only exists at Phase 9, then running `book_check.py` at Phase 6/7/8 will fail with "missing manifest."

The plan's T1T7 says "Add `books/<slug>/media-locale-manifest.json` to book-check gate (mirror the existing `frozen-lines.json` HARD-gate pattern)." The `frozen-lines.json` pattern: `book_check.py` skips the check unless `--require-frozen-lines` is passed.

**Recommendation:** mirror exactly: `--require-media-manifest` flag, default-off. The `book2media-orchestrator` passes `--require-media-manifest` at Phase 9 only. This is the same recommendation as review-eng F6.

### F9. Error messages: the new scripts should produce structured error output, not stack traces.

A developer integrating Phase 9 will hit a few common errors:
- Missing Amiri font (T3T5 hasn't run)
- Voice unavailable (T2T2 fails)
- Manifest schema invalid (T1T7)
- Chapter audio not synthesized yet (T3T2 invoked before T2T4)

Each error should produce a one-line actionable message: "Amiri font not found. Run `python install_amiri.py` to install." — not a Python stack trace.

**Recommendation:** the new scripts should use a shared `book-kit/book_workflow/lib/errors.py` helper that maps known error conditions to actionable messages. This is a 30-LOC helper module + ~10 LOC per script.

### F10. Documentation discoverability.

After Phase 9 ships, a developer new to the project will want to find:
- "How do I add a new locale?" → TOOLKIT.md media section
- "How do I change the per-locale voice?" → providers.yaml + manifest schema
- "How do I skip a product?" → manifest `skip: true` field
- "What if I want to publish to YouTube?" → future Phase 9.5 (not in v1)

The plan's T6T1/T6T2 update TOOLKIT.md and SCRIPTS.md — good. **But** TOOLKIT.md is the canonical catalog and the new media scripts are 14 entries — that's a big section. **Recommendation:** create a new doc `book-kit/docs/MEDIA.md` that links into TOOLKIT.md but provides the higher-level "how do I…" narrative. ~200 LOC of markdown. This is the standard book-kit pattern (e.g., `TRANSLATION_MODE.md` is a higher-level doc that TOOLKIT.md links to).

---

## Recommendations (priority-ordered)

1. **F2: add `--dry-run` to every output-producing script** (~5 LOC each). **Blocker: no.**
2. **F3: add `--from` + `--only` chapter filters** (~10 LOC each). **Blocker: no.**
3. **F6: `validate_media_manifest.py --init` to scaffold a stub manifest.** **Blocker: no, high DX value.**
4. **F10: create `book-kit/docs/MEDIA.md` as a higher-level narrative doc.** **Blocker: no.**
5. **F9: shared `errors.py` helper for actionable error messages.** **Blocker: no.**
6. **F4/F5: T2T2 + T3T5 idempotency + pre-flight UX.** **Blocker: no.**
7. **F7: `## Resolution rules` section in `providers.yaml`.** **Blocker: no.**
8. **F8: `--require-media-manifest` flag on `book_check.py`** (same as eng F6). **Blocker: no.**

---

## Blockers

**None.** All findings are DX improvements; none block the plan.

---

## Verdict

**PASS_WITH_WARN.** Developer surface is well-organized; the 8 recommendations are quality-of-life improvements. F2 (`--dry-run`) and F3 (`--from`/`--only`) are the highest-impact because they affect every developer who runs Phase 9 more than once.
