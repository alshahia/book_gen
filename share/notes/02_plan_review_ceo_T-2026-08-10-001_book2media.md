# Plan Review — CEO Angle — T-2026-08-10-001 (book2media)

**Date:** 2026-08-10
**Sub-agent:** planning
**Angle:** plan-ceo (scope, ambition, Mode 1 vs Mode 2 framing)
**Plan reviewed:** `share/notes/02_plan_T-2026-08-10-001_book2media.md`

---

## Findings

### F1. Scope discipline is correct for v1 — Mode 1 only, Mode 2 explicitly deferred.

The plan ships the **minimum viable Phase 9**: five products per locale, but only Mode 1 (single static image + Ken Burns zoompan + waveform). Mode 2 (Flux per-scene images via ComfyUI) is explicitly deferred to a future task list. This is the right call for v1 because:

- Mode 2 requires ComfyUI migration (research R2 — Desktop can't be headless, bare OSS install is unvalidated).
- Mode 2 requires per-locale image-prompt translation (which is a Phase 2-style language problem we haven't solved yet).
- Mode 2 visual quality is the **product differentiator** for reels — shipping Mode 1 lets us validate the pipeline without betting the product on image generation.

### F2. The "10-star product" question

A book-publishing user who finishes writing a book today gets... text. With Phase 9 Mode 1, they get:
- An **audiobook** (the highest-leverage audio product for nonfiction).
- **Horizontal video** (YouTube-friendly, ~6 min per chapter — works for book trailers and content marketing).
- **Vertical reels** × 3 platforms (the highest-leverage short-form content for visibility).
- **Vertical trailer** (the marketing asset for launch day).

What's missing from "10-star": **auto-publish to platforms**. Today the plan produces files. A 10-star Phase 9 would auto-upload to YouTube Shorts / IG Reels / TikTok via their respective APIs. **This is correctly out of scope** for v1 (each platform's API requires OAuth, app review, and per-platform content policies — a separate, much bigger problem). **Recommendation: file as a v2 Phase 9.5 candidate.**

### F3. The reel product is correctly the most-spec'd product.

Research F6 documented the per-platform safe-zone + max duration matrix; the plan bakes the union safe-zone into T4T5. This is the **right level of platform-awareness** for v1 — neither too loose (single output, no platform knowledge) nor too tight (three different master renders per chapter).

### F4. The audiobook product is under-spec'd on chapter-marker metadata.

Apple Podcasts, Audible, and Spotify all index M4B chapter markers. The plan's T4T2 mentions "chapter markers + `chapters.txt` (ffmetadata format)" but doesn't specify the ffmetadata schema. A 10-star audiobook product would have:
- Per-chapter titles from `style-guide.md` (not just `ch-01`, `ch-02`)
- Per-chapter start times aligned to the actual chapter audio start (not all-zero)
- Optional per-chapter artwork (cover image cropped to 1:1)

**Recommendation:** add a T4T2 sub-requirement: "ffmetadata `title=` field reads from `books/<slug>/style-guide.md` `## Chapter titles` section if present." This is a 10-line addition that materially improves the audiobook product.

### F5. The translation-reuse mechanism is correctly designed but under-tested.

Adaptive translation reuse (Phase 9 reads `books/<slug>/source-map.md` if present, else runs LLM-based media-only translation per F12) is the **right architecture** for the book-kit ecosystem. But the plan has no validation: does Claude-translated Arabic prose sound natural when read aloud by `ar-SA-HamedNeural` (MSA-trained)? The research F12 noted this as "MEDIUM risk, untested." **Recommendation:** add a T5 sub-task "spot-check one Arabic reel — manual listen for prosody / diacritic mismatch — flag to user if `style-guide.md` `## Voice` notes dialectal but voice is MSA."

### F6. The biggest scope risk: shipping too much in Phase 4 instead of vertical-slicing.

Phase 4 has 5 tasks (T4T1-T4T5), each producing one product. That's **5 products to review in one phase**. If the smoke test (Phase 5) fails on product N, all 5 are blocked. **Recommendation:** if master pushes back, consider splitting Phase 4 into "Phase 4a: audiobook + reel (the highest-value products)" + "Phase 4b: horizontal video + trailer (lower value)." This is a real risk and the planner's note in `## Self-critique` flagged it.

---

## Recommendations (priority-ordered)

1. **Add T4T2 sub-requirement: ffmetadata `title=` from `style-guide.md`.** ~10 LOC, material audiobook improvement. **Blocker: no** (fits in T4T2).
2. **Add T5 sub-task: manual Arabic reel prosody spot-check.** ~1 hour wall-clock, no code. **Blocker: no.**
3. **Consider Phase 4 split (audiobook + reel) / (horizontal video + trailer) for review focus.** Conditional on master preference. **Blocker: no, but requires Phase re-bundle.**
4. **File Phase 9.5 (auto-publish to platforms) as a future task list.** No current action.

---

## Blockers

**None.** The plan is well-scoped for v1; the only open question is whether the user wants the Phase 4 split recommended in F6.

---

## Verdict

**PASS_WITH_WARN.** Scope is correct for v1; the recommendations are 10-star improvements, not plan-blocking fixes.
