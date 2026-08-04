# WARN register — T-2026-07-04-002

<!-- Bootstrapped by T-2026-07-04-003 / T2 (no-op confirmation dispatch) per
     share/notes/README.md §04 naming convention. T-2026-07-04-002 had not
     previously created its own Phase 4 WARN register; T-003's WARN-9
     status is the file's first content. Master can extend the header at
     any later Phase 4 review pass for T-2026-07-04-002 itself.

     Format reference: share/notes/04_warns_register_T-2026-07-04-001.md -->

**Status legend:** RESOLVED = patched in code; DEFERRED = explicitly parked to a follow-up task;
OPEN = still material at task close.

---

## T-2026-07-04-003 WARN-9 status — 2026-07-04 — am-coder (T2 confirmation)

- **WARN-9 — LOW (UX, not WCAG violation)** — Keyboard-only sighted users cannot Tab-reach body content of 5 sections (hero/film/reveal/ritual/editions); only header → CTA → footer. Skip-link works for SR; not a violation. **→ DEFERRED (permanent at v0.14.0).**

  **Decision:** 5 accept-as-design / 0 fix / 0 skip-link / 0 focus-receiver *delta*. The focus-receiver pattern (`<section ... tabindex="-1">`) is already applied to all 5 sections.

  **Existing state confirmed by am-coder grep (2026-07-04, T2 re-read):**

  | Section   | Section-level `tabindex="-1"`? | Source line                       |
  |-----------|--------------------------------|-----------------------------------|
  | hero      | YES                            | `templates/cinematic-landing/skeleton/index.html:472` |
  | film      | YES (+ `aria-keyshortcuts="PageDown PageUp"`) | `:513`              |
  | reveal    | YES                            | `:594`                            |
  | ritual    | YES                            | `:621`                            |
  | editions  | YES                            | `:683`                            |

  **Triage source:** `share/reports/04_design_T-2026-07-04-003_triage.md` (am-design, T1, 2026-07-04) — all 5 rows return `none` for markup delta.

  **Rationale pointer:** `templates/cinematic-landing/memory/13-keyboard-nav.md:11` designates **PageDown/PageUp** as the canonical section-traversal mechanism. `memory/13:118` explicitly forbids `tabindex="0"` on sections (would put every section into the Tab order, breaking the focus-order contract). The section-level `tabindex="-1"` is the focus-receiver pattern (programmatic-focus target) and is already in place on all 5 sections. The PageDown/PageUp listener at `skeleton/index.html:1182` targets the section element, so even if a `<h2>` carried `tabindex="-1"`, focus would still land on the section — adding it would be pure redundancy, not a fix. Skipped alternate remedies: (a) 5 skip-links would add 5 off-screen links without making the 5 sections Tab-reachable (skip-links add a stop at the START of the next cycle, not in the middle); (b) `<h2 tabindex="-1">` would be additive markup with no behavior change.

  **verify.sh contract preserved:** 8/8 PASS (`bash templates/cinematic-landing/tests/verify.sh` from repo root, 2026-07-04, T2 re-run; no source edit, no test regression). `templates/cinematic-landing/skeleton/index.html` and `templates/cinematic-landing/tests/verify.sh` untouched by this dispatch.

  **Reopen criterion:** if a Tab-only user persona is added to the documented keyboard contract, reopen this WARN with a focus-receiver pattern. Closing the Tab-only gap would require either (a) `tabindex="0"` on sections (forbidden by `memory/13:118`; would need a contract amendment), or (b) a Tab-walking alternative (e.g., arrow-key roving among the 5 section stops) explicitly out-of-scope per `tasks/T-2026-07-04-003.md:25-26`.
