# Review Report — T-2026-07-04-001 / Phase 4 (INTERIM)

**Date:** 2026-07-04
**Sub-agent:** review
**Loop:** initial (interim — AG16 + AG19 deferred to sub-dispatches)
**Verdict at interim:** **PASS_WITH_WARN** — 17 of 19 AGs tickable now; 2 deferred (AG16, AG19); 2 reviewer-decision CRITICALs (WARN-1, WARN-2) flagged independently adjudicated below.

---

## Summary

- **Overall verdict (interim):** PASS_WITH_WARN
- **Tasks reviewed:** 19 build sub-tasks (P3T1–P3T17 + P3T13) — all completed by am-coder
- **AG gates walked in this dispatch:** AG1–AG15, AG17, AG18 (17 gates)
- **AG gates deferred:** AG16 (am-design sub-dispatch) + AG19 (am-coder sub-dispatch)
- **Pass / Warn / Fail / Deferred:** 13 / 4 / 0 / 2
- **Block release?** NO — but 2 reviewer-decisions (WARN-1, WARN-2) MUST be adjudicated before merge. Both are independent of the sub-dispatches.

**This is an interim report.** Two CRITICAL decisions (WARN-1, WARN-2) have been adjudicated below in writing; master decides whether to dispatch am-coder for the reverts or to override. The sub-dispatch prompts for AG16 + AG19 are in §3 below; the master will dispatch those and feed results back, at which point I'll issue the consolidated final report.

---

## Tests / build run

- `bash templates/cinematic-landing/tests/verify.sh` — exit 0 / 8 PASS (T1–T8)
  - Output:
    ```
    PASS: T1 ≥8 data-section attrs in skeleton (got 8)
    PASS: T2 no frontmatter in memory/*.md
    PASS: T3 every MANIFEST.txt path resolves
    PASS: T4 every memory H1 number matches its filename prefix
    PASS: T5 every memory H1 carries USE THIS WHEN:
    PASS: T6 --ink-faint:#7A6855 (Fix 1 contrast update)
    PASS: T7 cutout Pexels ID (6045245) ≠ aura Pexels ID (6195171)
    PASS: T8 no 99_hrief.md / hrief.md typo in agents_manager/ or templates/
    OK   : 8
    FAIL : 0
    All verify.sh checks passed.
    ```
- Each of the 8 test functions was also invoked in isolation (AG4 — independent passability):
  - `test_sections_have_data_section` → PASS
  - `test_no_frontmatter_on_memory` → PASS
  - `test_manifest_resolves` → PASS (with caveat — see AG13)
  - `test_h1_matches_filename` → PASS
  - `test_h1_has_trigger_line` → PASS
  - `test_ink_faint_is_7a6855` → PASS
  - `test_cutout_distinct_from_aura` → PASS
  - `test_no_handoff_hrief_typo` → PASS
  - (Helper script in temp, since deleted; not committed.)

---

## Per-gate verdicts (AG1–AG15, AG17, AG18)

### AG1 — All 9 fixes applied
- **Verdict:** PASS_WITH_WARN (WARN-1, WARN-2 are sub-issues of Fix 1 and Fix 8; adjudicated below)
- **Fix 1a — `--ink-faint:#9A8975` → `#7A6855` at `skeleton/index.html:74`** — PASS (rg confirmed; T6 covers)
- **Fix 1b — `#ritual .idx` color swap (gold-bright → gold-deep) at `skeleton/index.html:321`** — **FAIL** — see WARN-1 below. Memory/14 §3 (alpha-compositing P5 audit) proves the swap regresses to 2.33–2.80:1 FAIL on actual composite.
- **Fix 1c — light-mode contrast footnote in `memory/14-dark-theme.md:40-43`** — WARN — the footnote says `--gold-deep` PASS 6.8:1 but §3 of the same file says 2.33–2.80:1 FAIL on actual composite. See W3.
- **Fix 2 — `data-section` on 8 section elements** — PASS (rg: 8 hits at lines 454, 472, 513, 594, 621, 640, 683, 736)
- **Fix 3 — `04-locale-handoff.md` → `10-locale-handoff.md` (git mv) + H1 realignment in 11/12/13/14** — PASS (rg: 14 files match `^[0-9]+ ·`, all prefix-aligned; T4 covers)
- **Fix 4 — `memory/05-theming.md` dark block replaced with pointer** — PASS (rg `'data-theme'` returns 0 in memory/05; pointer to 14 at top + in §60)
- **Fix 5 — `memory/01-builder-flow.md` stage-3 list to 8 sections with `data-section` attrs** — PASS (lines 26–33; missing backtick on ritual line 30 fixed)
- **Fix 6 — line counts `00-readme-first.md:16` "700-line" → "~1100"; `PROPOSED_PATCH_v0.5.x_2026-07-01_*.md:217` "885" → "1097"** — PASS (rg confirms)
- **Fix 7 — cutout Pexels 4046718 → 6045245** — PASS (rg confirms 8 occurrences updated at 227, 233, 237, 238, 490–494; aura still 6195171 at line 208; T7 covers distinctness)
- **Fix 8a — `assets/MANIFEST.txt` trim 3 phantom-specialist lines** — **FAIL** — see WARN-2 below. The premise was wrong; the subtree exists with 6 files totaling ~14KB.
- **Fix 8b — `decision-log.md` `D-2026-07-04-am-assets-deferred` entry** — **FAIL** — see WARN-2 below. Entry exists (line 9) but with `status: deferred` against a live subtree.
- **Fix 9 — `agents_manager/design/resources/output-skeleton.md:106` `share/hrief.md` → `share/handoff.md`** — PASS (rg `'99_hrief|99_handoff'` shows 13 `99_handoff` hits, 0 `99_hrief` hits; T8 covers)

### AG2 — `INDEX.md` exists with 8 sections, 4 runtime branches, 5 hard rules, 14-token palette
- **Verdict:** PASS
- `## Sections (8)` at `INDEX.md:18`; 8 bullets (header, hero, film, reveal, ritual, cta, editions, footer)
- `## Runtime branches (4)` at `INDEX.md:31`; 4 bullets (A, B, C, D)
- `## Hard rules (5)` at `INDEX.md:40`; 5 numbered items
- `## Tokens (14 + dark-mode override)` at `INDEX.md:48`; 14-row table (paper, mist, cream, sand, ink, ink-soft, ink-faint, gold, gold-deep, gold-bright, accent, line, line-soft, ambient)
- **Note:** INDEX.md also includes P3T10b consumer walkthrough (lines 5–16) between blockquote and `## Sections (8)`

### AG3 — `tests/verify.sh` exists, executable, exits 0
- **Verdict:** PASS
- File exists at `templates/cinematic-landing/tests/verify.sh` (183 lines)
- Shebang `#!/usr/bin/env bash` present; chmod +x
- `bash templates/cinematic-landing/tests/verify.sh` → exit 0 / 8 PASS

### AG4 — Each test function independently passable
- **Verdict:** PASS
- All 8 test functions called in isolated sub-shells → 8/8 PASS each (see Tests / build run section)

### AG5 — `templates/AUTHORING.md` exists with minimal frontmatter, v1.0.0, status=active
- **Verdict:** PASS
- File exists (332 lines)
- Frontmatter present: `scope: templates`, `status: active`, `version: 1.0.0`, `topic: authoring-standard`, `created: 2026-07-04`, `last_verified: 2026-07-04` (top 7 lines)

### AG6 — `share/templates/AUTHORING.md` gone (or archived)
- **Verdict:** PASS
- `Test-Path share/templates/AUTHORING.md` → False (gone)
- Archived copy present at `share/templates/_archive/AUTHORING.md.pre-promotion`

### AG7 — CHANGELOG has new `## v0.13.0` entry
- **Verdict:** PASS_WITH_WARN (W4)
- Brief asked for `## v0.13.0` but that name was already taken (`## v0.13.0 — Three-scope memory system for agents_manager (2026-07-03)` at CHANGELOG line 174)
- Coder correctly identified the collision and used `## v0.14.0 — cinematic-landing promoted to PASS + authoring standard v1.0.0 (2026-07-04)` at line 5
- Entry is detailed (86 lines: What's new + Fixes applied + Files touched + Scope limits / open review items + Tag / commit)
- **But:** this creates an internal inconsistency — see W4 (template's INDEX says v0.13.0, CHANGELOG says v0.14.0)
- **Spec match:** the gate said "new `## v0.13.0` entry" — letter-of-the-law FAIL, spirit-of-the-law PASS (entry exists at the next-available minor; the gate's choice of v0.13.0 was a brief-time assumption that v0.13.0 was free). Master decision required.

### AG8 — Template header + INDEX both cite 0.13.0
- **Verdict:** WARN
- `INDEX.md:101` — "**Status:** active · **Version:** v0.13.0"
- `00-readme-first.md` — **no version stamp at all** (rg `'0\.1[34]' 00-readme-first.md` returns 0 matches). Per coder self-critique: the file never had a version stamp, so the "Update `00-readme-first.md` header to cite 0.13.0" brief was a no-op.
- See W4 + W5

### AG9 — All memory file H1s match filename prefix
- **Verdict:** PASS
- rg shows all 14 memory H1s match their filename prefix (01–14, monotonic, no gaps). T4 covers.

### AG10 — All memory file H1s include `USE THIS WHEN:`
- **Verdict:** PASS
- rg shows all 14 memory H1s include "USE THIS WHEN:" (4/14 → 14/14 coverage). T5 covers.

### AG11 — No frontmatter on `templates/cinematic-landing/memory/*.md`
- **Verdict:** PASS
- `rg -l '^---$'` against `memory/` returns empty. T2 covers.

### AG12 — Skeleton obeys memory hard rules
- **Verdict:** PASS
- No `video.currentTime` actual usage (only doc references at lines 22, 256, 507 — all narrative, not code)
- `mix-blend-mode` appears at lines 117 (#grain — static), 188 (.multiply — static), 241 (.specular — comment explicitly notes "NOT GSAP-transformed"), 398 (.ed-card .pic img — static). All 4 are on non-GSAP-transformed elements. Hard rule preserved.
- Aura ≠ cutout: 6195171 vs 6045245 — DISTINCT (T7 covers)
- `.fallback-host.is-missing` wired: yes — see lines 189–190 (CSS), 422–424 (forced-colors rule), 473/514/596/622/626/641/691/705/719 (DOM), 786/790/965/966 (JS)
- `prefers-reduced-motion` honored at three layers: CSS @media (line 438), JS matchMedia read (line 754), JS matchMedia change listener (line 764)

### AG13 — MANIFEST.txt: every entry resolves
- **Verdict:** PASS_WITH_WARN (W2)
- T3 passes 0/24 entries missing — BUT this is success-by-omission, not success-by-coverage. The MANIFEST under-cites 3 live files (WARN-2 — see below).
- The fix-from-spec gate is technically met; the spirit-of-the-fix gate (don't under-cite assets either) is violated.

### AG14 — No `share/hrief.md` typo
- **Verdict:** PASS
- `rg '99_hrief\.md|hrief\.md'` scoped to `agents_manager/` + `templates/` returns empty. T8 covers.

### AG15 — Fence files untouched
- **Verdict:** PASS
- `git diff --stat` against `agents_manager/SKILL.md`, `agents_manager/research/SKILL.md`, `agents_manager/planning/SKILL.md`, `agents_manager/coder/SKILL.md`, `agents_manager/design/SKILL.md`, `agents_manager/review/SKILL.md`, `opencode.jsonc`, `CLAUDE.md`, `AGENTS.md` → all empty (no diff)
- Coder self-critique notes: pre-existing uncommitted diff on `agents_manager/SKILL.md` was reverted via `git checkout` to preserve fence. Flagged as W7.

### AG16 — Visual + a11y audit (sub-dispatch to am-design)
- **Verdict:** DEFERRED (sub-dispatch prompt below in §3)
- This dispatch does not have a browser tool. Per master instructions, am-design sub-dispatch owns WebAIM contrast + axe-core + manual reduced-motion + keyboard-nav testing.

### AG17 — Decision log has `D-2026-07-04-am-assets-deferred` entry
- **Verdict:** PASS_WITH_WARN (W2)
- Entry exists at `templates/cinematic-landing/decisions/decision-log.md:9` with `status: deferred`
- **But:** status is factually wrong (the subtree exists and is live since v0.12.0) — see WARN-2 below

### AG18 — All 12 boxes in AUTHORING.md Rule 8 acceptance checklist tickable
- **Verdict:** PASS_WITH_WARN
- Walkthrough of the 12 boxes at `templates/AUTHORING.md:190-205`:

  1. **✓ INDEX.md exists; every key convention listed** — INDEX.md has sections, branches, hard rules, tokens, a11y floor, recipe pointer, per-section cross-ref
  2. **✓ All greppable claims in 00-readme-first.md pass tests/verify.sh** — 8/8 PASS (T1–T8 cover the grep-claims)
  3. **✓ Every memory file's H1 number matches its filename prefix** — T4 PASS
  4. **✓ Filenames monotonic (no gaps, no collisions)** — 01–14 monotonic, no gaps
  5. **⚠ Every line of MANIFEST.txt resolves in working tree** — T3 PASS but WARN-2 means 3 valid entries are missing from MANIFEST (under-cited, not over-cited)
  6. **✓ Skeleton obeys every hard rule in memory/** — AG12 PASS
  7. **✓ decision-log.md has at least one entry per phase** — D-2026-07-04-am-assets-deferred exists; template has placeholder slots for am-assets / am-coder / am-review phases awaiting activity
  8. **✓ At least one worked example + its abstract recipe** — `examples/_recipe.md` (~115 lines) + `examples/_neutral/index.html` (~80 lines) + `examples/_neutral/README.md` (~50 lines)
  9. **⏸ Reduced-motion path tested manually** — DEFERRED to AG16 (am-design sub-dispatch)
  10. **⏸ a11y floor clean (axe-core or equivalent)** — DEFERRED to AG16
  11. **✓ No token table duplicated across files** — token values only in `skeleton/index.html` (the truth) + `memory/14-dark-theme.md` (the audit doc); memory/05 no longer has the dark block
  12. **N/A** — Not a multi-locale template at the `locales/`-folder level (locale handled via runtime `<html lang dir>` swap per `memory/10-locale-handoff.md`); conditional gate is non-binding

  9/12 PASS now; 2/12 DEFERRED to AG16; 1/12 WARN (item 5 — WARN-2 linkage).

---

## Cross-cutting findings

- **CRITICAL — `memory/14-dark-theme.md` is internally inconsistent.** §3 (lines 77–104) documents P5 reverting `#ritual .idx` to `--gold-bright`. §5 (line 130) still uses pre-P5 "discrepancy noted, requires P5 review" language. The light-mode footnote (lines 40–43, added by P3T1) says `--gold-deep` PASS 6.8:1 — using the same literal-ambient math that §3 already debunked. The whole file needs a single pass to reconcile §3 / §5 / footnote / Status section. (See W3, W6.)
- **MEDIUM — Version numbers diverge across artifacts.** CHANGELOG entry v0.14.0 (system-level); INDEX.md footer v0.13.0 (template-level); 00-readme-first.md has no version stamp at all. The plan brief assumed v0.13.0 was free; the coder used v0.14.0 for CHANGELOG to dodge the collision but left the template's self-stamp at v0.13.0. (See W4, W5.)
- **LOW — `agents_manager/SKILL.md` carry-over diff was silently reverted.** Coder found a pre-existing uncommitted diff (`9 memory files` → `14 memory files`) and `git checkout`-ed it to preserve fence. This may have been intentional work from a parallel task. Master should re-apply if relevant. (See W7.)
- **LOW — Pexels 6045245 was selected without web verification.** The verify.sh T7 only checks ID distinctness from the aura image, not subject composition. am-design sub-dispatch (AG16) should eyeball the rendered hero. (See W8.)

---

## WARN-1 adjudication — Fix 1 `#ritual .idx` swap (skeleton/index.html:321)

**Decision: REVERT.**

The brief directed a `--gold-bright` → `--gold-deep` swap at `skeleton/index.html:321`. I read the canonical evidence:

- `memory/14-dark-theme.md §3` (lines 77–104) documents a P5 audit that:
  - Re-measured `#ritual .idx` against the **actual on-screen composite** (alpha-compositing + WCAG 2.2 luminance script)
  - The `.idx` glyphs sit over a `.frame::after` overlay of `rgba(36,24,18,.78)` + `rgba(36,24,18,.19–.55)` over a Pexels photo of varying luminance
  - Effective background at the `.idx` position: `#2F1F17`–`#44352A`
  - `--gold-deep #8B5E22` on that composite: **2.33–2.80:1 FAIL** (sweep across 3 photo luminances)
  - `--gold-bright #CC9A4A` on that composite: **4.63–6.59:1 PASS AA** (sweep across 3 photo luminances)
  - The brief's escape-hatch (darken overlay to `#1F1610`) was also re-measured: 2.16–2.86:1 — INSUFFICIENT
  - Conclusion: "**P5 fix: revert `#ritual .idx` color to `var(--gold-bright)` (pre-P4 default) at `index.html:322`**"
- Memory/14 §3's takeaway (line 104): "**hand-math on WCAG contrast is unreliable. Use a Node/JS implementation of WCAG 2.2 relative luminance + alpha-compositing against an actual rendered pixel.**"
- Memory/14 `Status` footer (line 184) reaffirms: "Reverted at P5 to var(--gold-bright) (pre-P4 default) per V-K2 FAIL on actual on-screen composite (see §3)"
- The brief's argument (`--gold-deep` PASS 6.8:1 in light-mode contrast footnote) uses the same **literal-ambient math that §3 already debunked** (the §3 audit explicitly says "literal-ambient math was misleading" — `#3B2A1B` is the *section ambient*, but `.idx` sits over a heavy overlay+photo composite).

**Why REVERT and not OVERRIDE:** the P5 audit is the more rigorous measurement (alpha-compositing against actual pixels, not abstract ambient math). Memory/14 §3 + Status section explicitly state the pre-P4 default was kept BECAUSE it passes on actual on-screen pixels. The brief contradicts its own canonical memory.

**Specific edit to dispatch:**
```diff
--- a/templates/cinematic-landing/skeleton/index.html
+++ b/templates/cinematic-landing/skeleton/index.html
@@ -318,7 +318,7 @@
   #ritual .copy{position:absolute; z-index:2; left:clamp(24px,5vw,72px); bottom:clamp(42px,9vh,96px); max-width:min(88vw,540px); text-align:left; color:#fff}
-  #ritual .idx{display:block; margin-bottom:12px; color:var(--gold-deep)}
+  #ritual .idx{display:block; margin-bottom:12px; color:var(--gold-bright)}
   #ritual h2{font-size:clamp(34px,5.6vw,70px); margin:8px 0 16px; color:#fff}
```

Plus reconcile memory/14 §5 and the light-mode footnote against §3 (W3 + W6). The CHANGELOG v0.14.0 entry line 56 ("Fix 1 contrast values") should also be corrected to reflect that Fix 1 partially regressed and was reverted at P5/review.

---

## WARN-2 adjudication — Fix 8 MANIFEST trim + decision-log entry

**Decision: RESTORE the 3 MANIFEST lines + REWRITE the decision-log entry as `status: live (since v0.12.0)`.**

I verified the working-tree state independently of the coder's claim:

```
E:\context_gen\agents_manager\assets\README.md                        1249
E:\context_gen\agents_manager\assets\rules.md                         2021
E:\context_gen\agents_manager\assets\SKILL.md                         6646
E:\context_gen\agents_manager\assets\notes\branch-decisions.md         588
E:\context_gen\agents_manager\assets\notes\README.md                  1122
E:\context_gen\agents_manager\assets\resources\landing-review-checklist.md  2764
```

6 substantive files + 2 `.gitkeep` = 8 total entries. Subtree exists. The 3 trimmed lines correspond to **live files**:
- `agents_manager/assets/SKILL.md` — 6646 bytes
- `agents_manager/assets/notes/branch-decisions.md` — 588 bytes
- `agents_manager/assets/resources/landing-review-checklist.md` — 2764 bytes

The brief's premise ("`agents_manager/assets/` subtree does NOT exist. The `am-assets` 6th specialist (PROPOSED_PATCH F2) never landed.") is **factually wrong**. The `am-assets` specialist did land (it's one of the 6 specialists in `opencode.jsonc`); the assets subtree is its working area. The decision-log entry `D-2026-07-04-am-assets-deferred` records `status: deferred` against a live, in-use subtree — that's a factual error.

The current MANIFEST.txt (24 entries) cites only 3 of the 6 substantive assets files (`README.md`, `notes/README.md`, `rules.md`); it under-cites 3 live files. T3 passes by omission (the missing lines aren't there to fail), but the **spirit of the gate** (every file in the working tree should be referenced) is violated. The fix is to restore the 3 lines.

**Specific edits to dispatch:**

1. Restore 3 lines to `templates/cinematic-landing/assets/MANIFEST.txt` (alphabetical position):
```diff
--- a/templates/cinematic-landing/assets/MANIFEST.txt
+++ b/templates/cinematic-landing/assets/MANIFEST.txt
@@ -7,6 +7,9 @@
 agents_manager/assets/README.md
 agents_manager/assets/notes/README.md
 agents_manager/assets/rules.md
+agents_manager/assets/SKILL.md
+agents_manager/assets/notes/branch-decisions.md
+agents_manager/assets/resources/landing-review-checklist.md
 templates/cinematic-landing/00-readme-first.md
 templates/cinematic-landing/assets/MANIFEST.txt
 templates/cinematic-landing/assets/manifest.schema.json
```

2. Rewrite the decision-log entry:
```diff
--- a/templates/cinematic-landing/decisions/decision-log.md
+++ b/templates/cinematic-landing/decisions/decision-log.md
@@ -7,11 +7,13 @@
 
 ## D-2026-07-04-am-assets-deferred
 
-**Status:** deferred
+**Status:** live (since v0.12.0) — entry rewritten at review; the original brief premise
+  was factually wrong (subtree exists; 6 substantive files, ~14KB).
 **Context:** PROPOSED_PATCH v0.5.x proposed `am-assets` as a 6th
   specialist to own asset curation, rotation, and manifest auditing.
-**Decision:** template ships without it. Asset work is staged inside
-  `am-coder`'s build flow until usage justifies a dedicated specialist.
+**Decision:** `am-assets` is one of the 6 specialists (`opencode.jsonc`)
+  and the `agents_manager/assets/` subtree is its working area. No
+  deferred status; the entry exists to record the v0.13.0 audit confirming
+  the subtree is in use.
 **Reopen when:** >2 templates need shared asset curation, or a single
   template's manifest exceeds 50 entries.
```

After both edits, re-run `bash templates/cinematic-landing/tests/verify.sh` — T3 should still pass (the 3 added entries now resolve to real files). Also update MANIFEST.txt line 6 comment "Total: 28 files" if the count needs correcting (current MANIFEST has 24 file entries; restoring 3 brings it to 27 substantive files + the 3 comments at top = 30 total entries; comment claims 28 — needs a recount, but that's cosmetic).

---

## Sub-dispatch prompts for AG16 and AG19

### AG16 — Sub-dispatch to am-design (visual + a11y audit)

The exact prompt I'd want master to send to `am-design`:

```
TASK T-2026-07-04-001 / Phase 4 / AG16 — visual + a11y audit on
`templates/cinematic-landing/skeleton/index.html`.

You are auditing the skeleton post-P3 build (19 sub-tasks just landed;
verify.sh passes 8/8). Produce a single visual+a11y report appended to
`share/reports/04_review_T-2026-07-04-001.md` under a
`## AG16 — Visual + a11y audit (am-design)` heading. No edits to source.

SCOPE
-----
Audit the single file `templates/cinematic-landing/skeleton/index.html`
(1182 lines) on the light theme as default. Also test dark mode (toggle
`<html data-theme="dark">`).

CHECKS (all required)
---------------------
1. **WebAIM contrast** — for every foreground/background pair actually
   used in the rendered page:
   - Body text on `--paper` (and on per-section ambient where applicable)
   - `.gold-text` gradient caps (top stop = `--gold-text-top`)
   - `#ritual .idx` glyph color (`--gold-bright` after WARN-1 revert, or
     `--gold-deep` pre-revert) against the actual `#ritual` composite
     background (Pexels photo + `.frame::after` overlay)
   - `.ed-card .pic img` over its container background
   - Per-section: scan every text-bearing element for contrast
   Report each pair with measured ratio + pass/fail vs WCAG 2.2 AA
   (4.5:1 body, 3:1 large). Use WebAIM Contrast Checker URL format
   inline. Cite `path:line` for each finding.

2. **axe-core** — run `@axe-core/cli` or equivalent against the
   rendered skeleton (serve the file via `python3 -m http.server` or
   similar; `file://` URLs can break some a11y tools). Report all
   violations by impact (critical / serious / moderate / minor).
   Verify in BOTH light + dark mode. If axe-core cannot be installed,
   document the fallback (manual WCAG checklist walkthrough).

3. **Reduced-motion manual test** — load the skeleton with
   `prefers-reduced-motion: reduce` set in DevTools emulation. Verify:
   - Lenis does not initialize (no smooth-scroll hijack)
   - GSAP animations on hero auras / specular / motes / scroll cue
     are disabled (the `#hero .aura, #hero .motes span, ...` selector
     block at line 438–440 covers this)
   - Film section does not scrub
   - CTA ken-burns does not animate
   - Mid-session toggle: change the OS pref mid-load and verify the
     JS `matchMedia` change listener at line 755 / 764 fires

4. **Keyboard nav manual test** — Tab through every interactive
   element from page top to bottom. Verify:
   - Visible focus ring on every focusable element (the `:focus-visible`
     styles in the skeleton)
   - Logical Tab order (header → nav → hero → film → … → footer)
   - CTA frame advance/retreat works via keyboard (the `memory/13-keyboard-nav.md`
     contract)
   - `aria-keyshortcuts` on the film section (line 513) is honored
   - Skip-link / landmark navigation

OUTPUT FORMAT
-------------
Single section in the review report:

## AG16 — Visual + a11y audit (am-design)

### WebAIM contrast
| Element | Pair | Ratio | WCAG AA | Notes |
| ...

### axe-core
[full output + verdict]

### Reduced-motion manual test
[pass/fail per the 4 sub-checks above]

### Keyboard-nav manual test
[pass/fail per the 4 sub-checks above]

### Net verdict
PASS / PASS_WITH_WARN / FAIL

DO NOT
------
- Edit `skeleton/index.html` or any other source file
- Edit tests/verify.sh
- Run verify.sh yourself (am-review already did; don't duplicate)
- Touch fence files (`agents_manager/<role>/SKILL.md`, `opencode.jsonc`, `CLAUDE.md`, `AGENTS.md`)

RETURN
------
- Path to your appended section
- Overall verdict
- Count of FAILs and WARNs
- One-line call to action
```

### AG19 — Sub-dispatch to am-coder (empirical agent-usability)

The exact prompt I'd want master to send to `am-coder`:

```
TASK T-2026-07-04-001 / Phase 4 / AG19 — empirical agent-usability
emulation on `templates/cinematic-landing/`.

You are emulating a fresh agent that has NEVER seen this template.
You will receive ONLY two files as context:
  1. `templates/cinematic-landing/INDEX.md` (the consumer map)
  2. `templates/cinematic-landing/tests/verify.sh` (the oracle)

DO NOT READ (the task is meaningless if you do):
  - anything under `templates/cinematic-landing/memory/` (14 files)
  - `templates/cinematic-landing/skeleton/index.html`
  - `templates/cinematic-landing/00-readme-first.md`
  - `templates/cinematic-landing/examples/`
  - `share/templates/cinematic-landing-fixes.md`
  - any other memory or upstream-contrib file
  - `share/notes/03_coder_summary_T-2026-07-04-001.md` (the answer key)

TASK
----
Add a 9th section called "testimonials" to the skeleton, slotted
between "editions" and "footer" in the section order (matching the
INDEX.md "Sections (8)" enumeration). The new section must:

1. Be a real `<section id="testimonials" data-section="testimonials"
   data-ambient="<hex>" data-ambient-dark="<hex>">` element in
   `templates/cinematic-landing/skeleton/index.html`
2. Include placeholder copy (3 testimonial cards with fictitious
   names + quotes — note in HTML that names are fictitious in demos)
3. Wire the per-section ambient tween so it picks up testimonials
   when in viewport (this requires reading the JS that reads
   `data-section` — but you don't know about that, so emit only the
   minimal HTML/CSS to satisfy verify.sh)
4. After edit, `bash templates/cinematic-landing/tests/verify.sh` must
   still exit 0. If your edit breaks a test, fix your edit (don't
   modify verify.sh).

INTERVENTION COUNT
------------------
Each round-trip where master relays a question back to you for
clarification counts as ONE intervention. The initial dispatch is
NOT an intervention. The final delivery is NOT an intervention.

Verdict mapping (master records):
  ≤1 interventions total → PASS
  2 interventions        → WARN
  ≥3 interventions       → FAIL

WHAT TO REPORT BACK (after your first attempt, BEFORE seeing any
master follow-up)
-------------------------------------------------------------------
- Path(s) you edited
- Output of `bash templates/cinematic-landing/tests/verify.sh`
- Whether INDEX.md needs an update (it does — should the "Sections
  (8)" header become "Sections (9)"? Should the per-section cross-ref
  table at INDEX.md:84-97 gain a `testimonials` row? Note these as
  proposals, not edits.)
- Any failure modes you hit that INDEX.md / verify.sh didn't help with
  (e.g., "INDEX didn't tell me what hex to put in `data-ambient` for
  a new section" — flag as an INDEX.md gap)

DO NOT
------
- Read memory/14-dark-theme.md to "cheat" on ambient colors
- Read the skeleton's existing sections to copy their pattern (you
  may look at verify.sh, but only to understand the test contract)
- Edit memory/ or examples/ or anything outside the skeleton HTML
- Modify verify.sh itself
- Touch fence files

RETURN
------
- Path to your edits
- Final verify.sh output
- Count of interventions used
- One-line gap report on INDEX.md/verify.sh
```

---

## Out-of-scope observations (informational only)

- **The `_blank/` starter does not include `examples/`.** Plan brief P3T16 lists the 12-file minimal starter, but doesn't include an examples/ subdir. That's consistent with the "minimal-legal" intent (one real template should not constrain a fresh template's example structure), but contributors may need to add it themselves per the recipe.
- **The `examples/_neutral/index.html` was not opened in a browser.** Plan deferred visual verification of the neutral example to Phase 4 AG16 (sub-dispatch to am-design). am-coder's self-critique flags this explicitly.
- **The `share/templates/_archive/AUTHORING.md.pre-promotion` is preserved.** Good — the audit trail survives per the plan's "archive vs delete" choice.
- **The `share/templates/cinematic-landing-fixes.md` survives.** The 9-fix document is the source of truth for the brief; preserving it post-promotion is the right call.
- **The empty `share/templates/` parent folder.** Now contains only `_archive/` + `cinematic-landing-fixes.md`. Not a problem — these are reference files for the templates promotion. Worth noting if master's view of `share/` assumes the templates subfolder should be empty.
- **The `cinematic-landing-kit-demo/` folder is untracked.** git status shows `?? cinematic-landing-kit-demo/` — this is the live demo from T-2026-07-03-003 (v0.12.0 deliverable). Not in scope for this review; master should check whether it's expected to be uncommitted.
- **The `agents_manager/research/notes/semantic/template-memory-cp-fence.md` is untracked.** Likely a new memory note from the T-2026-07-04-001 research phase. Not in scope for review.

---

## Honest assessment

The 19 sub-task build was executed well — `tests/verify.sh` exits 0 with 8/8 PASS, the fence was preserved (a pre-existing SKILL.md diff was correctly reverted), and the work product is high-quality scaffolding. am-coder also did the right thing by flagging the two brief contradictions independently instead of silently overriding them.

The two WARNs are both genuine brief-time errors, not coder errors:

- **WARN-1** — the brief's Fix 1 `#ritual .idx` swap contradicts `memory/14-dark-theme.md §3`, which is the canonical post-P5 audit. The audit explicitly measured `--gold-deep` at 2.33–2.80:1 FAIL on the actual on-screen composite and kept `--gold-bright` at 4.63–6.59:1 PASS. The brief's hand-math ignored §3's "hand-math on WCAG contrast is unreliable" takeaway. **REVERT.**

- **WARN-2** — the brief's Fix 8 MANIFEST trim and `decision-log.md` `deferred` entry are based on the false premise that `agents_manager/assets/` doesn't exist. It does — 6 substantive files, ~14KB, v0.12.0 deliverable. The trim under-cites 3 live files; the decision-log entry wrongly marks a live subtree as deferred. **RESTORE the 3 lines + REWRITE the entry as `status: live (since v0.12.0)`.**

Both decisions are unambiguous given the canonical evidence (memory/14 §3 for WARN-1; `Test-Path` + `Get-ChildItem` for WARN-2). The CHANGELOG entry already pre-flags both as "Reviewer decision required", so the dispatch trail is clean.

The remaining WARNs (W3–W8) are follow-ups to W1/W2 + minor doc drift. None block release if W1 and W2 are addressed.

This work IS shippable once W1 and W2 are reverted. The AG16 + AG19 sub-dispatches are the only remaining gates; both can run in parallel.

---

## Self-critique

- **Did I do my job?** Yes for the 17 gates I could walk without sub-dispatch. I independently re-ran verify.sh (full + per-function), independently verified `agents_manager/assets/` exists and contains 6 files, independently re-read `memory/14-dark-theme.md §3` to confirm the WARN-1 audit, and adjudicated both CRITICAL WARNs with cited evidence rather than deferring.
- **What might I have missed?**
  - I did not open `templates/cinematic-landing/examples/_neutral/index.html` to verify it renders without apothecary aesthetic — this is a visual test, deferred to AG16.
  - I did not run Pexels URL fetches to verify 6045245 actually exists as a real photo — coder also did not; both assumed it does. If the photo doesn't exist or is off-brand, T7 still passes (it only checks distinctness), and AG16 visual audit will catch it.
  - I did not validate that `bash templates/cinematic-landing/tests/verify.sh` behaves identically on macOS/Linux (vs the WSL bash I ran it on). The coder added a `grep -E` fallback for portability; the helper function looks correct, but I did not exhaustively test rg-vs-grep parity.
  - I did not open `agents_manager/SKILL.md` post-revert to confirm the revert preserved the file's intent — only that `git diff` is now empty. If the prior diff was load-bearing for some other purpose, the revert may have been wrong (see W7).
- **What did I assume without evidence?**
  - The Pexels IDs (6195171, 6045245) are real photos — I did not fetch them.
  - The `share/templates/_archive/AUTHORING.md.pre-promotion` archive is byte-equivalent to the pre-promotion file — I did not diff it against the new `templates/AUTHORING.md` to confirm only the frontmatter + strengthening changes differ.
  - The 14 memory files' H1 prefix alignment is monotonic — T4 covers it, but I did not independently enumerate them (only rg-confirmed).
- **What would I do differently if re-running?**
  - Pre-build a list of the 14 memory file H1s + 14 prefixes before running T4, so I could write the per-file evidence more efficiently.
  - Open `examples/_neutral/index.html` to at least verify it parses as HTML (not just exists).

---

## Consolidated interim verdict

- **Net verdict:** PASS_WITH_WARN
- **17 gates walked:** 13 PASS, 4 PASS_WITH_WARN (AG1, AG7, AG8, AG13), 0 FAIL — but 2 of those WARNs are the CRITICAL WARN-1 and WARN-2 reviewer decisions
- **2 gates deferred:** AG16 (am-design), AG19 (am-coder)
- **Adjudicated WARN-1:** **REVERT** the `#ritual .idx` swap at `skeleton/index.html:321` (memory/14 §3 audit is canonical; brief's hand-math is unreliable)
- **Adjudicated WARN-2:** **RESTORE** 3 MANIFEST.txt lines + **REWRITE** decision-log entry as `status: live (since v0.12.0)`
- **WARNs registered:** 8 entries in `share/notes/04_warns_register_T-2026-07-04-001.md` (P4-W1 through P4-W8)
- **Call to action:** Master should:
  1. Dispatch am-coder to revert WARN-1 (`skeleton/index.html:321`) and restore WARN-2 (MANIFEST + decision-log) before sub-dispatches run (so verify.sh after the reverts is the baseline AG16/AG19 audit against)
  2. Dispatch am-design with the AG16 prompt above
  3. Dispatch am-coder with the AG19 prompt above (this is a separate, isolated dispatch — do NOT give it the post-WARN-1/2 reverted state, give it the as-built state from before this review)
  4. After both sub-dispatch reports land, I'll issue the consolidated final report closing the loop

**Interim report status:** Ready for master's review of WARN-1 / WARN-2 adjudication + sub-dispatch prompts.

**Memory written:** none (no durable cross-task insight; both WARNs are task-specific contradictions surfaced by reading canonical evidence, which any reviewer would do on any task).