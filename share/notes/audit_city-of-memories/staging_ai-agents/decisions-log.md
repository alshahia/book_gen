# Decisions Log — AI Agents with Python

Append-only record of why things changed. Answers "why isn't X included" without re-deriving it later.

---

### decision-001
Date: 2026-08-01
Phase: Phase 3 — outline (user gate)
What changed: One new chapter (ch-08 "How Agents Work: A Toy Agent from Scratch") inserted before the smolagents introduction. Old ch-08..ch-18 renumbered to ch-09..ch-19. New ch-09 (formerly ch-08) opens with a short "Why Use a Framework" intro that compares the toy agent to smolagents before the framework code appears.
Why: User requested that the foundation of how AI agents work be solidified before introducing the smolagents framework. The new ch-08 unpacks the agent loop in plain Python (no smolagents) so the next chapter's framework introduction lands on a concrete mental model rather than abstract magic. The renumbering shifts all subsequent chapter numbers by one. The book is now 19 chapters (was 18), still within the 15–20 chapter range from intake.
User confirmed: yes (T-2026-08-01-001 Phase 3 user gate)

---

### decision-002
Date: 2026-08-01
Phase: Phase 4 — style guide (user gate)
What changed: All 18 brief-corrections and 25 inline age-risks from the research-log are documented in the style guide as binding constraints on the writer. Specifically: (1) tool returns are NOT auto-coerced (ch-10 entry-077); (2) Jinja template keys are inner names, not nested paths (ch-15 entry-145); (3) `Model` is the abstract base, `ApiModel` is the abstract API subclass (ch-16 entry-155). Numbers and provider names kept directional in the prose.
Why: The chapter briefs were drafted from chub research (smolagents 1.24.0) and the installed venv runs smolagents 1.26.0. Where the two diverged, the writer must follow verified-install behavior, not the brief wording. The user confirmed the style guide as a whole (6 confirmation points).
User confirmed: yes (T-2026-08-01-001 Phase 4 user gate)

---
