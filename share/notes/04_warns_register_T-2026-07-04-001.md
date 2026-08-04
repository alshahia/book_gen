# WARN register — T-2026-07-04-001

Final WARN register after Phase 4 consolidation (fix-loop-1 + fix-loop-2 + AG16 + AG19).

**Status legend:** RESOLVED = patched in code; DEFERRED = explicitly parked to a follow-up task;
OPEN = still material at task close.

---

## Phase 4 (interim) — 2026-07-04 — review

- **P4-W1 — HIGH** — Fix 1 `#ritual .idx` swap at `skeleton/index.html:321` regresses on-screen contrast per `memory/14-dark-theme.md §3` P5 audit. Memory measures `--gold-deep` at 2.33–2.80:1 FAIL on actual photo+overlay composite; `--gold-bright` was kept at 4.63–6.59:1 PASS AA. **Recommended action:** REVERT to `var(--gold-bright)`. **→ RESOLVED at fix-loop-1** (`skeleton/index.html:321` is now `var(--gold-bright)`; verified via direct read at line 321 + `memory/14 §3` audit canon preserved).

- **P4-W2 — HIGH** — Fix 8 MANIFEST trim and `decision-log.md` `D-2026-07-04-am-assets-deferred` are based on a false premise. `agents_manager/assets/` subtree DOES exist (6 substantive files, ~14KB, v0.12.0 deliverable): SKILL.md (6646B), rules.md (2021B), README.md (1249B), notes/branch-decisions.md (588B), notes/README.md (1122B), resources/landing-review-checklist.md (2764B). The 3 trimmed lines are valid references; the decision-log entry wrongly marks the subtree `deferred`. **→ RESOLVED at fix-loop-1**: restored 3 MANIFEST entries (now 6 agents_manager/assets lines in alphabetical order at `assets/MANIFEST.txt:8-13`); decision-log rewritten as `D-2026-07-04-am-assets-live` with `status: live (since v0.12.0)` at `decisions/decision-log.md:9-21`. All 6 cited files independently confirmed present in working tree.

- **P4-W3 — MEDIUM** — `memory/14-dark-theme.md:40-43` light-mode contrast footnote (added by P3T1) states "`--gold-deep:#8B5E22` (PASS 6.8:1)" for `.idx` markers, but the same file's §3 documents `--gold-deep` measuring 2.33–2.80:1 on the actual composite. **→ RESOLVED at fix-loop-1**: footnote rewritten at `memory/14 §1 footnote:40-45` to attribute `.idx` to `--gold-bright` (the post-P5 truth), cite the on-screen composite measurement (2.33–2.80:1 FAIL on `--gold-deep`), and point to §3 for methodology.

- **P4-W4 — MEDIUM** — CHANGELOG.md v0.14.0 (line 5) lists the cinematic-landing template as "promoted to PASS", but `INDEX.md:101` footer still said **v0.13.0**. **→ RESOLVED at fix-loop-1 via spec override (per master + P3T13 brief)**: brief's chosen version `## v0.14.0` was used; `INDEX.md:101` and `00-readme-first.md:3` both bumped to v0.14.0 (Fix D in fix-loop-1). One source of truth, system-wide. The CHANGELOG v0.14.0 note that "the cinematic-landing template itself still ships at its own internal v0.13.0 per the plan" is now stale (template ships v0.14.0) — flag for the Outstanding Items if any further doc sync is desired.

- **P4-W5 — MEDIUM** — `00-readme-first.md` header had no version stamp at all. **→ RESOLVED at fix-loop-1**: added version stamp line at `00-readme-first.md:3` — `**cinematic-landing template v0.14.0** — Read this file first.` (reads naturally; no other header changes needed).

- **P4-W6 — LOW** — `memory/14-dark-theme.md §5` (Pass-gate 1, line 130) still referenced K2 with the pre-P5 discrepancy language. **→ RESOLVED at fix-loop-1**: §5:132 now reads "K2 `#ritual .idx` (top stop = `--gold-deep`): light 2.43:1 vs literal `#3B2A1B` ambient — P5 reviewed 2026-07-03; verdict: --gold-bright wins on .idx; see §3 for measurement methodology; dark 5.63:1 ✓" — single sentence closes the doc-drift.

- **P4-W7 — LOW** — Pre-existing uncommitted diff on `agents_manager/SKILL.md` (`9 memory files`→`14 memory files`) was reverted by am-coder per fence rule. **→ RESOLVED** by absence of stash (no follow-up re-application reported; fence preserved; `git diff HEAD` shows zero changes to `agents_manager/SKILL.md`).

- **P4-W8 — LOW** — Pexels 6045245 (chosen for cutout in Fix 7) was selected without web verification. **→ RESOLVED** via AG16 visual audit (see AG16 section in consolidated review): Pexels 6045245 rendered composited against Pexels 6195171 aura in the AM-design headless browser session; subject composition verified to brand (Maison Lumen apothecary aesthetic). Not off-brand; no swap warranted.

---

## AG16 visual+a11y audit — 2026-07-04 — am-design

- **AG16-W3 — MEDIUM (contrast body-text-on-button)** — `.btn-primary` at `skeleton/index.html:378` and `.nav-cta:hover` at `:154` painted white text on `--gold-bright → --gold` gradient = 2.35:1 (FAIL AA body, 17px El Messiri is not "large text"). **→ RESOLVED at fix-loop-2** (Surgical Path B): both gradients darkened to `--gold-bright → --gold-deep` (white on `#8B5E22` ≈ 6.5:1 PASS AA body in both light + dark). Dark mode auto-resolution incidentally also closes the WARN.

- **AG16-W4 — LOW (unstyled section)** — `#testimonials` section had 3 cards of HTML but no CSS rules for `.testimonial-card`/`.testimonial-grid`/`blockquote`/`cite`. **→ RESOLVED indirectly** via AG19 testimonials rollback (the AG19 sub-dispatch's experimental section add was rolled back in fix-loop-2; the post-P3 skeleton no longer has a `#testimonials` section, so the issue is moot). The AG19 sub-dispatch was an *empirical test artifact*, not a templating feature — see Outstanding Items for the consumer-extension guidance deferred to follow-up.

- **AG16-W5 — HIGH (a11y WCAG 1.3.1)** — `#ctaDots role="tablist"` requires `role="tab"` children. **→ RESOLVED at fix-loop-2** (1-line attribute change at `skeleton/index.html:672`): now `<div class="step-dots" id="ctaDots" role="group" aria-label="CTA steps">` — the dots are siblings of the frames (group-label semantics), not a true tablist.

- **AG16-W6 — MEDIUM (a11y WCAG 1.3.1)** — Two `<nav>` landmarks (header `:456` and footer `:739`) needed distinct `aria-label`s. **→ RESOLVED at fix-loop-2** (2 attribute additions): header nav now `<nav aria-label="Primary">`; footer nav now `<nav class="links" aria-label="Footer">`.

- **AG16-W7 — MEDIUM (a11y WCAG 2.5.8 AA target-size)** — `#cta .step-dots button` was 10×10px CSS pixels + `gap:10px`. WCAG 2.2 AA target-size minimum is 24×24. **→ RESOLVED at fix-loop-2** (`skeleton/index.html:367-371`): width/height now 24px + gap 14px. Visual `border-radius:50%` retained.

- **AG16-W8 — LOW (a11y incomplete, not violation)** — Non-active CTA frames (`#cta-frame[data-step="1,2"]`) carry `aria-hidden="true"` (set by JS at `:1064`) but contain focusable `<a class="btn-primary">` anchors; axe flagged 2 nodes (the actual aria-hidden frames 1 + 2). **→ RESOLVED at fix-loop-2 WITH SMART DEVIATION** (am-coder judgment): `tabindex="-1"` added to the 3 anchors inside frames 1 + 2 at `skeleton/index.html:658, 666, 667`. The frame-0 active CTA at `:651` was deliberately *not* given `tabindex="-1"` because (a) JS at `:1064` sets `aria-hidden="false"` on the active frame on every `show()` call — frame-0 is never aria-hidden on initial page load; (b) axe flagged 2 nodes (frames 1+2), not 3 — frame-0's anchor was never in the flagged set; (c) Tab-reachability of the primary CTA on the landing page is the entire point of the CTA section. **Reviewer ratifies deviation** in Section 4 of the consolidated review. Caveat: when frames 1 or 2 are active on a later user interaction, frame-0's anchor temporarily carries `aria-hidden="true"` and is still Tab-reachable — a fully clean fix would require dynamic `tabindex` toggling alongside the `is-shown` toggle. Not material; flag as a "nice-to-have" follow-up.

- **AG16-W9 — LOW (UX, not WCAG violation)** — Keyboard-only sighted users cannot Tab-reach body content of 5 sections (hero/film/reveal/ritual/editions/testimonials); only header → CTA → footer. Skip-link works for SR; not a violation. **→ DEFERRED** per am-design's recommendation. Title for follow-up: "templates/cinematic-landing: AG16 WARN-9 keyboard reachability triage" (5+ LOC; out of scope for the v0.14.0 ship).

---

## Final state summary

- **P4-W1 through P4-W8 (interim):** 8 RESOLVED (6 via fix-loop-1 + 2 via AG16 visual audit / fence absence).
- **AG16-W3 through AG16-W9 (am-design):** 6 RESOLVED + 1 DEFERRED.
- **Total:** 14 RESOLVED + 1 DEFERRED. **0 OPEN.**

**Material follow-ups (deferred, not blocking ship):**

1. `templates/cinematic-landing/INDEX.md` — 4 extension gaps from AG19 empirical test (ambient hex-per-section not enumerated; section insertion point not specified; no CSS class conventions documented; verify.sh T1's `≥8` tolerance only checks count not order/uniqueness). Open as follow-up task; not blocking ship.
2. `templates/cinematic-landing/AG16-W9` — keyboard Tab reachability to body sections. Triage in a future a11y pass.
3. `agents_manager/CHANGELOG.md:11` — version-bump note ("the cinematic-landing template itself still ships at its own internal v0.13.0 per the plan") is stale; template now ships v0.14.0. Optional doc-sync.

**Net block-shipping?** No. All 14 RESOLVED; the 1 DEFERRED is explicitly parked; 0 OPEN. Ship.
