# WARN register — T-2026-07-03-001

Append-only log of WARN-level findings from am-review on this task. Each entry:
`<phase> — <severity> — <one-line description> — <path:line>`

---

- P3T1 — MEDIUM — `mix-blend-mode` heuristic in skeleton triggers "should not appear" but actual hard rule from `memory/02-scroll-film-canvas.md:46` is "not on GSAP-transformed elements"; the 4 occurrences (`.multiply`, `#grain`, `#hero .specular`, `.ed-card .pic img`) are all on explicitly non-GSAP-transformed elements with rationale comments. False positive. — `templates/cinematic-landing/skeleton/index.html` (CSS lines ~83, ~131, ~225, ~283)

---

## Notes on this register

- The single WARN above is also captured in `share/reports/04_review_T-2026-07-03-001.md` under "Cross-cutting findings" — the register exists for the consolidated user-facing WARN log at task close.
- No FAIL-level findings; no follow-up fixes required before user can ship.
- Optional LOW-level follow-ups (em-dash drift, missing `04-locale-handoff.md`, missing mid-session `change` listener, skeleton wc-l discrepancy) are out-of-scope observations and are tracked in the review report's "Out-of-scope observations" section, not in this register.
