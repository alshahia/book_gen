# Intake — [Working Title]

Status: DRAFT | CONFIRMED
Confirmed date: [date, only once every field below is user-approved]

## 1. Title / working title
[value]

## 2. Core idea / goal
[what the book is for, what the reader should leave with]

## 3. Category
Agent's initial guess: [Fiction / Nonfiction / Hybrid — with one-line reasoning]
User confirmation: [Fiction / Nonfiction / Hybrid]
Downstream toggles set by this answer:
- Bible tracks: [facts/terminology/claims] and/or [characters/plot/timeline/POV]
- Research focus: [fact-verification] and/or [inspiration/reference]
- Review includes continuity/plot checks: [yes/no]

## 4. Audience
[who's reading this, what they already know]

## 5. Tone / voice reference points
[comparable books, adjectives — specific traits to emulate, not "write like X" wholesale]

## 6. Target length
Options presented: [50–100 pages / ~5 chapters] · [5 chapters × ~25 pages] · [300+ pages / ~15–20 chapters]
User's choice: [value]
Approx. chapter count implied: [N]

## 7. Definition of done
Exit criteria for review loops: [e.g. "no unresolved developmental issues, max 2 line-edit passes per chapter"]

## 8. Exception-handling preferences
- If research is thin/contradictory on a topic: [policy]
- If the user is unresponsive at a checkpoint: [proceed-and-flag / hard-stop]

## 9. Fiction-specific (if category is Fiction/Hybrid)
Genre conventions researched: [structure norms, typical length, POV conventions found]
User's genre choice: [value]

## 10. Translation mode

> **Skip this section for native book-gen.** Fill it when the project translates an existing source work into another language.

- [ ] **Is translation?** — yes / no
- [ ] **Source root** — path under `source/` relative to project root (default: `source/`)
- [ ] **Source-naming convention** — `ch-NN.txt` (default) / `chapter-NN.txt` / `chapters/NN.md` / custom
- [ ] **Target slug pattern** — `ch-NN.md` (default) / `ch-NN-<slug>.md` / `chapters/NN-<title>.md`
- [ ] **Tashkeel policy** — [link to tashkeel-policy.md](./tashkeel-policy.md) (Arabic only) or `n/a`
- [ ] **Freeze code blocks** — yes (default for technical books) / no (for narrative translations)
- [ ] **Source map filled** — [link to source-map.md](./source-map.md) and confirm each row is set

Downstream effects when `Is translation?` is yes:

- Phase 1 dispatches `am-research` only when source-material contradictions surface; default is to use source verbatim.
- Phase 4 close regenerates `frozen-lines.json` from the source's code-block SHA256s (when freeze_code = yes).
- Phase 6 enforces the chunked-write protocol (`book-writer/SKILL.md` §Chunked-write protocol).
- `book_check.py` activates source-ratio, missing-H2, code-block-freeze, and untranslated-English checks (each gated by `source-map.md`).
- `books/<slug>/.translate-progress.json` is the resume ledger.

---

## 11. Operational caps
- [ ] Confirmed and linked: [operational-caps.md](./operational-caps.md)
- [ ] Chapters with caps or style overrides: [ch-NN, or none]
- [ ] Authorized source recorded in operational-caps.md: [bible.md / decisions-log.md entry]

## 12. Tashkeel policy
- [ ] [tashkeel-policy.md](./tashkeel-policy.md) applies and is filled at Phase 3
- [ ] Not applicable for this non-Arabic book
- Policy owner / confirmation: [user decision or decisions-log entry]

## 13. Front matter required
- [ ] Preface
- [ ] Table of contents
- [ ] Glossary
- [ ] Index

## 14. Back matter required
- [ ] Preface
- [ ] Table of contents
- [ ] Glossary
- [ ] Index

## 15. Frozen line policy
[free text — list which lines, if any, should be frozen from the start; include chapter path, line number, and why]

---
Approval log: each field above must show explicit user approval (pick-suggestion / free-text-edit / reject-and-retry) before status moves to CONFIRMED.

## Mechanical gates

- **Phase 0 — user:** fill and confirm the operational controls above before `intake.md` becomes `CONFIRMED`.
- **Phase 3 — orchestrator:** detect missing translation-mode, source-map, operational-cap, tashkeel, front-matter, back-matter, or frozen-line fields before the outline gate. When §10 `Is translation?` is yes, refuse to advance past Phase 3 without a populated `source-map.md`.
- **Scripts:** `book_check.py` reads `style-guide.md`, `tashkeel-policy.md`, `frozen-lines.json`, `source-map.md`, and `glossary.md`. It does **not** read `intake.md`; intake is consumed by master during Phase 0 and Phase 3.

## Open questions

1. Should the front-matter and back-matter checkbox lists be distinct project-specific lists rather than the shared four-item starter list?
2. For a non-Arabic book, should the tashkeel choice be `not applicable` only, or also require a policy file marked not applicable?
3. Should frozen lines be selected at Phase 0 or deferred until the first approved chapter?
