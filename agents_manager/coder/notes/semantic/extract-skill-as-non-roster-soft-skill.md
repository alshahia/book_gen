---
scope: role
topic: extract-skill-as-non-roster-soft-skill
status: active
created: 2026-07-04
last_verified: 2026-07-04
---

## TL;DR
A "skill without a roster slot" is a real pattern: `agents_manager/extract/` has
SKILL.md + rules.md but no `opencode.jsonc` agent and no master dispatch route.

## Insight
Any specialist loads it on demand. Its SKILL.md is validated by
`scripts/validate-frontmatter.py` in LENIENT mode (path lacks `/skills/`), so
only `description` is strictly required — `name`/`paths` are free. A non-standard
`paths:` frontmatter key (write-destination allowlist) is fine; document it in
the body. Env note: `python3` here lacks PyYAML; use `python` for yaml one-liners.
The stdlib validator itself needs explicit file args and crashes on
no-frontmatter files, so only pass frontmatter-bearing `.md` to it.

## Source
share/notes/03_coder_summary_T-2026-07-04-009_phase-3.1.md; scripts/validate-frontmatter.py:57-104
