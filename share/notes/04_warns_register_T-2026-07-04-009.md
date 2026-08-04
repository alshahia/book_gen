# WARN register — T-2026-07-04-009

**Date:** 2026-07-04
**Sub-agent:** review (am-review)
**Task:** extract-to-template v0.15.0 — build review
**Format:** per `agents_manager/SKILL.md:195`

---

## Phase 3.1 — 2026-07-04 — PASS_WITH_WARN

- P3.1 — LOW — extract/SKILL.md step 2 enumerates only PF-1..PF-5 inline; PF-6 (placeholder/trigger hygiene) and PF-7 (memory schema) are reflected in subsequent steps but not labeled with their PF-* codes in the step-2 list — `agents_manager/extract/SKILL.md:82-86` (cosmetic cross-reference; substantive coverage in steps 4-6).
- P3.1 — LOW — `paths:` in `agents_manager/extract/SKILL.md:4-7` frontmatter is a project-specific extension (not standard Anthropic Skills schema); documented in the file's "Non-standard frontmatter note" callout at `agents_manager/extract/SKILL.md:12-20`. Forward-looking only; no production-impact today.

## Phase 3.2 — 2026-07-04 — PASS_WITH_WARN

- P3.2 — LOW — `agents_manager/memory/README.md:3` adds `description:` frontmatter field on the README itself (validator-compliance fix on descriptive metadata, NOT a memory-entry schema change). Per coder's reading: dispatch rule "do NOT add any frontmatter fields OTHER than `tech_stack:` and `domain:`" applies to memory-entry frontmatter, not the README's own frontmatter. Acceptable deviation; surfaced for transparency.
- P3.2 — LOW — `agents_manager/SKILL.md:408` "4-option" → "5-option" is a factual correction required by the addition of option 5. The 4 existing option entries (lines 409-412) are byte-identical to HEAD (verified em-dash U+2014 preserved). Acceptable; required by content change.

---

## Auto-accept triageable status

No WARNs in this build are auto-acceptable per `agents_manager/SKILL.md:373-388` — the 5 new W-extract-* categories proposed in synthesis v2 are NOT on the auto-accept list and remain deferred to v0.15.x. All WARNs in this register are LOW severity / cosmetic / acceptable-as-is; no user action required.

---

## Resolution (2026-07-04, fix-loop)

- **W1 — RESOLVED** via re-labeling of step 2 in `agents_manager/extract/SKILL.md` to enumerate PF-1..PF-7 explicitly with a pointer to steps 4-5 for PF-6 and PF-7.
- **W2 — RESOLVED** via removal of `paths:` from `agents_manager/extract/SKILL.md` YAML frontmatter; the path list now lives in the body under a new "Files this skill reads/writes" section. The "Non-standard frontmatter note" callout is retired. Frontmatter now matches standard Anthropic Skills schema (`name` + `description`).
- **W3 — RESOLVED** via tightened `description:` wording on `agents_manager/memory/README.md:3` to enumerate the 3-scope schema explicitly.
- **W4 — ACCEPTED** with no code change — the "4-option"→"5-option" factual correction is correct as-is and required by the addition of option 5. Documented per am-review's assessment at `share/reports/04_review_T-2026-07-04-009_p3-2.md:53-54`.