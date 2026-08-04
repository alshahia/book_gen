---
name: book-writer
description: Prose-writing posture for am-coder when invoked from the book-gen pipeline. Load when am-coder receives a book-mode dispatch prompt (the prompt includes a books/<slug>/ path + a chapter outline entry + bible.md + style-guide.md). Replaces code-writing posture with chapter-writing posture: one chapter per invocation, stay within the approved outline, never mark own work approved.
allowed-tools: Read, Write (books/<slug>/chapters/, books/<slug>/bible.md, books/<slug>/ledger.md), grep, glob
triggers: book chapter dispatch, write chapter, draft chapter, prose-writing mode
preamble-tier: 3
version: 0.21.0
---

# Book-Writer Skill

> **This is a posture skill, not a specialist.** `am-coder` loads this when the dispatcher is the book-gen orchestrator. The skill changes am-coder's working lens from "implement assigned code tasks" to "draft one book chapter per invocation." All other boundaries (file scope, no agents_manager edits, no source-code writes outside `books/<slug>/`) stay the same.

## What changes vs. am-coder's default posture

| Default am-coder | book-writer mode |
|---|---|
| Reads `share/notes/02_plan_*.md` + `tasks/<id>.md` rows | Reads `books/<slug>/outline.md` + the chapter's entry + `books/<slug>/bible.md` + `books/<slug>/style-guide.md` + the chapter's slice of `books/<slug>/research-log.md` |
| Writes code files | Writes prose markdown to `books/<slug>/chapters/ch-NN.md` |
| Writes `share/notes/03_coder_summary_<id>_<phase>.md` | Writes a short note inline at the top of the chapter file (`<!-- Written by am-coder @ <timestamp> via book-writer skill; chapter status: drafted -->`), then updates `ledger.md` to `drafted` |
| Tests run by executing build/test commands | No test run; instead, self-check against the chapter's outline entry (does each promised element appear in the draft?) + the style guide (does voice/presentation match?) |
| Verifies `path:line` evidence for downstream review | Same — chapter's outline promises should appear at specific line ranges the reviewer can cite |

## Read order (mandatory)

1. `books/<slug>/bible.md` — established facts, terminology, voice rules; treat as ground truth; do not contradict.
2. The chapter's entry in `books/<slug>/outline.md` — your scope. Do not write content for any other chapter.
3. The chapter-specific slice of `books/<slug>/research-log.md` — only entries tagged `used_in: ch-NN`. Not the full log.
4. `books/<slug>/style-guide.md` — presentation + voice + (fiction/hybrid) POV/tense.

## Write order (mandatory)

1. Draft `books/<slug>/chapters/ch-NN.md`. Save before you exit. In-progress is fine if you've covered the chapter's outline promises.
2. Append any new facts/voice rules/characters this chapter introduces to `books/<slug>/bible.md` (append, never rewrite existing entries).
3. Update `books/<slug>/ledger.md`: mark `ch-NN` row → `drafted`. Add word count. Do NOT mark `approved` — that's am-review's call.
4. **Mechanical gate (mandatory):** run `python3 book_workflow/scripts/book_check.py books/<slug>/`. Exit 0 required before saving the chapter file as `drafted`. If exit ≠ 0, STOP — surface failure to master with the per-chapter line evidence (the script reports `ch-NN:line_number` on failure). Do NOT mark `drafted` until the gate passes.

## While writing

- Stay within the chapter's outline entry. If the chapter genuinely needs to expand beyond what was outlined (e.g., the outline underspecified a scene), STOP and flag to master instead of expanding unilaterally. Outline scope changes are a user-checkpoint trigger.
- Match voice and presentation exactly per the style guide. The line-edit pass exists to catch voice drift, but don't rely on it — get it right the first time.
- If the bible conflicts with what this chapter needs, flag it. Don't silently override the bible.
- If a fact you need isn't in the bible AND isn't in the research log AND isn't obvious common knowledge, flag it as a gap. Don't invent.
- For fiction: keep continuity with characters, timeline, and POV per bible. The line-edit and developmental passes will catch breaks.

## Frozen lines + word windows (mechanical contract)

Two non-negotiable mechanical checks run on every chapter draft via `book_check.py`:

1. **Frozen lines** — every line declared in `books/<slug>/frozen-lines.json` must byte-match its SHA256. The manifest is generated at Phase 4 close by master; do not edit it yourself.
   - If a frozen line genuinely must change: STOP, surface to master. Master triggers a user checkpoint. Style-guide amended → manifest regenerated → then you proceed. Never silently rewrite a frozen line.
2. **Word windows** — chapter word count must fall inside the range declared in style-guide.md `## Word-count windows` for that chapter, OR the `operational-caps.md` override if one exists for this chapter. If outside the range, do not extend to hit the minimum — surface to master; the window exists for a reason.

Both checks are HARD gates: `book_check.py` exit ≠ 0 means the chapter is not drafted. Review-pass acceptance cannot compensate for a failed mechanical gate.

## What this skill explicitly forbids

- Writing more than one chapter per invocation. If the next chapter is short, dispatch a separate invocation.
- Inventing facts not in the bible or research log. Flag the gap, don't fill it from training data.
- Marking the chapter `approved` in `ledger.md`. am-review does that.
- Reviewing or approving your own work. (Even if the chapter looks clean, the orchestrator dispatches am-review separately. Self-approval defeats the lens separation.)
- Removing or reordering an `approved` chapter. Flag the structural change to master.
- Editing any file outside `books/<slug>/chapters/`, `books/<slug>/bible.md`, `books/<slug>/ledger.md`. (If you need to update another book state file, flag it.)
- Editing `agents_manager/**`, `opencode.jsonc`, `CLAUDE.md`, or the controller's `tasks/README.md` / `share/README.md`. Same boundaries as default am-coder.

## What this skill permits (overrides am-coder default)

- Writing prose markdown is treated as "writing source files" — am-coder's default boundary permits this; nothing in this skill reduces that permission.
- Chapter files can be larger than am-coder's typical code chunk (prose chapters are 2,000-5,000 words). The reviewer's per-chapter pass expects a single file to review.
- Self-check is prose-style, not test-style: re-read the chapter and verify every promise from the outline entry appears at least once in the prose. No `npm test`, no `pytest`. Just an editorial pass.

## Self-critique block (write at end of chapter file)

Append at the bottom of every chapter file before saving:

```
<!--
Self-critique (book-writer skill):
- Outline coverage: <which outline promises are present, which were skipped>
- Voice match: <one-line assessment against style-guide>
- Bible consistency: <any new facts added to bible this chapter>
- Open questions for am-review: <issues the reviewer should look at first>
-->
```

The orchestrator + am-review read this block. It's not optional — it's the handoff signal.
