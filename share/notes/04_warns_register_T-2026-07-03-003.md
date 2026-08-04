# WARN register — T-2026-07-03-003

<!-- master creates this file at first review; subsequent reviews append -->

- Phase 3 (build) — MEDIUM — PROPOSED_PATCH.md Z3 evidence row says `1167 (post-v2-axis absorption in T-2026-07-03-003)` but our skeleton is 1133 lines (Measure-Object) or 1182 lines (wc -l) post-absorption, not 1167 — `agents_manager/upstream-contrib/PROPOSED_PATCH_v0.5.x_2026-07-01_cinematic-landing-template.md:173`
- Phase 3 (build) — MEDIUM — CHANGELOG.md L13 (v0.12.0 entry, pre-existing) carries the same `1167 lines` claim for our skeleton post-v2-axis absorption — `agents_manager/CHANGELOG.md:13`
- Phase 3 (build) — MEDIUM — PROPOSED_PATCH.md Z7 (G8_v2_axes_fold PENDING) says "skeleton extended ~271 LOC"; actual is +286 (wc -l) or +282 (Measure-Object) — `agents_manager/upstream-contrib/PROPOSED_PATCH_v0.5.x_2026-07-01_cinematic-landing-template.md`
- Phase 3 (build) — MEDIUM — agents_manager/SKILL.md:82 still says "9 memory files" — plan P3T8 fixed L72 but missed L82 in the same file — `agents_manager/SKILL.md:82`
- Phase 3 (build) — LOW — CHANGELOG v0.12.1 entry consistently uses "1183 lines" / "+~287 LOC" in 4 places (L86, L97, L139, L161); actual `wc -l` is 1182, extension is +286 — `agents_manager/CHANGELOG.md:86,97,139,161`
- Phase 3 (build) — LOW — AG3 gate description has latent ambiguity: proposal file SHA cannot match source after P3T4 edits (the post-apply state is expected to differ). The plan accommodates this; the gate language should be reworded in a future AG-gate review pass — out of scope here.
- Phase 3 (build) — LOW — §J matrix items #6 (function `set` not `setTheme`) and #7 (`.theme-toggle` class not `#theme-toggle` id) use different identifiers than the matrix spec; functionally equivalent, no runtime impact. Future plans can write §J more loosely.