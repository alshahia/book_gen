# Plan Review — Design Angle — T-2026-08-10-001 (book2media)

**Date:** 2026-08-10
**Sub-agent:** planning
**Angle:** plan-design (manifest schema ergonomics, am-assets lane integration, locale-correctness review gate)
**Plan reviewed:** `share/notes/02_plan_T-2026-08-10-001_book2media.md`

---

## Findings

### F1. The `media-locale-manifest.json` schema is clean and matches the cinematic-landing precedent.

Research F11 proposed the schema:
```json
{
  "source_locale": "en",
  "target_locales": ["en", "ar"],
  "products": [
    {"id": "audiobook-en", "locale": "en", "format": "audio/m4b",
     "tts_provider": "kokoro", "voice": "af_heart", "skip": false},
    {"id": "audiobook-ar", "locale": "ar", "format": "audio/m4b",
     "tts_provider": "edge-tts", "voice": "ar-SA-HamedNeural",
     "skip": false, "translation_required": true}
  ]
}
```

This is **good shape**:
- `source_locale` + `target_locales` is a clean way to express "what's the original book written in, what other locales are we generating."
- `products` array with per-product `skip` flag is the right level of granularity for a 5-product matrix.
- `translation_required` per-product is the right separation: some products (e.g., the audiobook for a target locale) need translation; others (e.g., the cover image) don't.

### F2. The schema has one missing field: `output_filename_template`.

For the reel product (Phase 4 T4T5), the three platform outputs need different filenames:
- YouTube Shorts: `reel-ch-NN-en-yt.mp4`
- Instagram Reels: `reel-ch-NN-en-ig.mp4`
- TikTok: `reel-ch-NN-en-tt.mp4`

The plan hardcodes these into `assemble_reel.py`. But the user may want different naming per brand (e.g., a publishing house wants `reel-ch-01-en-youtube.mp4` not `reel-ch-01-en-yt.mp4`). **Recommendation:** add an optional `output_filename_template` field per-product with placeholders like `{platform}`, `{locale}`, `{chapter}`.

Actually, this is borderline YAGNI. **Counter-recommendation:** keep filenames hardcoded for v1, surface as a v2 enhancement.

### F3. The schema has no retention policy field, but the plan mentions one.

Plan `## Self-critique` (R8 mitigation) says "Phase 1 T1T5 manifest includes `keep_until_shipped` retention field." But the schema in F11 doesn't have it. **Recommendation:** either add it to the schema (consistent with plan), or remove from plan. The retention policy is a real concern (5 products × 5 chapters × 2 locales = 50 files, ~10 GB) so the field belongs in the schema.

```json
{"id": "audiobook-en", "locale": "en", "format": "audio/m4b",
 "tts_provider": "kokoro", "voice": "af_heart", "skip": false,
 "retention": {"keep_until": "shipped", "auto_delete": true}}
```

### F4. The schema has no image-asset reference field, but Mode 1 needs one.

Mode 1 uses a **single static image** per chapter (the "cover image" for the video). Where does that image come from? The plan doesn't say. Options:
- (a) Auto-generate one cover image per book via Flux (gates Mode 1 on Flux availability — but research R2 says Flux isn't ready).
- (b) User provides one cover image at `books/<slug>/assets/cover.png`.
- (c) Reuse `books/<slug>/exports/cover.png` if the book was already exported (Phase 8 may produce a cover).

**Recommendation:** add a `cover_image` field per-product in the manifest, defaulting to a documented lookup order. This is a real gap because without a cover image, the video assembler has no input.

```json
{"id": "video-horizontal-m1-en", "locale": "en", "format": "video/mp4",
 "cover_image": "books/daily-focus/assets/cover.png",
 "tts_provider": "kokoro", "voice": "af_heart", "skip": false}
```

### F5. The am-assets media-manifest lane is well-scoped.

The plan's T1T3 says: "Amend `am-assets/SKILL.md` to add a 'media-manifest lane' parallel to the cinematic-landing 4-branch decision tree." This is the right shape — am-assets already owns the cinematic-landing manifest, so adding a second manifest shape is additive, not disruptive.

The research-recommended 4-branch retargeting (still images present + video pipeline → Mode 2; still images present only → Mode 1; video file present → use as-is; nothing present → generate single cover image via Flux) is the right decision tree for Phase 9.

But **the cinematic-landing manifest schema and the media-locale-manifest schema are different shapes**. The cinematic-landing manifest is asset-catalog-shaped (lists every image/video with its source). The media-locale-manifest is product-matrix-shaped (lists every output product with its provider). They're not the same schema. **Recommendation:** explicitly note in T1T3 that the media-manifest lane uses a different schema (`media-locale-manifest.schema.json`) and am-assets dispatches a different branch of the decision tree.

### F6. The am-review locale-correctness gate is well-scoped but under-specified.

The plan's T1T4 says: "font (Amiri present + RTL shaping), voice (single narrator per locale matches manifest), RTL (burn-in position within safe-zone), per-platform loudnorm compliance." Four checks — good.

- **Font check:** confirm Amiri is on the system + the burn-in ffmpeg filter chain references `Amiri` font name. Trivial: `fc-list | grep -i amiri` + grep the `ass` filter.
- **Voice check:** confirm the synthesized audio file's hash matches the manifest's voice field. Less trivial — needs a "voice signature" hash. **Recommendation:** simpler approach — assert that the synthesized audio duration matches the expected duration ±5% (per T2T4's smoke check), and that the per-chunk count matches T2T3's chunk count. If a different voice is used, the chunk durations will differ.
- **RTL check:** confirm `ass` filter used `shaping=complex` (visible in the ffmpeg argv). Or, more robustly: assert the burned-in `.mp4` file's first subtitle cue reads correctly when played in VLC.
- **Loudnorm check:** run `ffmpeg -af loudnorm=...:print_format=json -f null -` and compare against the platform target.

All four checks are implementable. **Recommendation:** T1T4 should produce a checklist file at `agents_manager/review/resources/locale-correctness-checklist.md` documenting the four checks + their acceptance criteria.

### F7. The cover-image question (F4) is also a design question.

Mode 1 ships with a single static image. The design review angle: this is **fine** for an audiobook (the user is listening, not watching), and **acceptable** for a horizontal video at the 6-min length (the user's eye forgives a static image if the narration is strong + there's waveform animation). But for **reels at <90s**, a static image is a **conversion killer** — every TikTok growth study shows first-3-second visual motion is the #1 driver of completion rate.

**Recommendation:** add a sub-task T4T5a: "Investigate adding a subtle background gradient loop + waveform overlay to make the reel cover visually less static. ~30 LOC." This is the single highest-impact Mode 1 improvement. (Or punt to Mode 2.)

---

## Recommendations (priority-ordered)

1. **F3: add `retention` field to the schema** (real concern, ~10 GB per book). **Blocker: no.**
2. **F4: add `cover_image` field to the schema** (real gap — the assembler has no input). **Blocker: yes — without this, T4T3/T4T4/T4T5 cannot ship.**
3. **F7: investigate gradient loop + waveform for reel** (highest-impact Mode 1 improvement). **Blocker: no, optional.**
4. **F6: produce `locale-correctness-checklist.md`** at the path above. **Blocker: no.**
5. **F2: defer `output_filename_template` to v2** (YAGNI). **Blocker: no.**
6. **F5: explicitly note the media-manifest uses a different schema than cinematic-landing.** **Blocker: no.**

---

## Blockers

**F4 — the `cover_image` field is a true gap.** Without a documented lookup order for the cover image, the Phase 4 assemblers cannot function. This must be added to the schema before T1T5 closes.

---

## Verdict

**PASS_WITH_WARN.** Schema is clean; F4 is a true gap that must close before Phase 4.
