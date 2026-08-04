---
name: book-reviewer
description: Two-pass review posture for am-review when invoked from the book-gen pipeline on a translation-mode project. Load when am-review receives a dispatch prompt that includes a books/<slug>/chapters/ch-NN.md path AND source-map.md. Pass 1 compares the chapter against its source line-by-line; Pass 2 checks cross-chapter consistency against glossary.md and style-guide.md. Replaces single-pass review with two specialized lenses.
allowed-tools: Read, Bash (read-only), grep, glob, Write (share/reports/04_book-review_<task-id>_ch-<NN>_<pass>.md, share/reports/04_book-review_<task-id>_consistency-glossary-drift.md, books/<slug>/ledger.md row update)
triggers: book chapter review, review chapter, translation review, two-pass review
preamble-tier: 3
version: 0.21.0
---

# Book-Reviewer Skill (Translation Mode)

> **This is a posture skill, not a specialist.** `am-review` loads this when the dispatch prompt is a translation-mode chapter review. It splits the single review call into two lenses: accuracy (does the chapter cover what the source covers?) and consistency (does it use the same terms as the rest of the book?). Master dispatches them as **separate invocations** — never combined into one call.

## When this skill applies

- Dispatch prompt contains `books/<slug>/chapters/ch-NN.md` AND `source-map.md` is present.
- Chapter is in `drafted` status (writer finished; review not yet started).

When the project is native book-gen (no source files), am-review falls back to the standard 3-pass posture (dev / line / copy) per the controller's review SKILL.md. This skill is translation-specific.

## Pass 1 — Accuracy vs. source

Compare the translated chapter against the corresponding source file (resolved via `source-map.md` → `source/<file>`).

### Inputs

- `books/<slug>/chapters/ch-NN.md` (translated prose)
- `books/<slug>/source/<source-filename>` (English source)
- `books/<slug>/source-map.md` (binding; word_min / word_max / required_h2 / freeze_code)
- `books/<slug>/style-guide.md` (translation rules: freeze code blocks, glossary-first introduction)

### Procedure

1. **Extract** the source's H2 sections (matches against `required_h2`).
2. **Extract** the source's code blocks (when `freeze_code = yes`). For each, compute SHA256 of the normalized body (strip leading/trailing whitespace, collapse internal runs of whitespace).
3. **Extract** the source's key claims**:
   - numbered/bulleted lists (preserve order)
   - bolded terms (likely proper-noun or product names)
   - URLs (verify preserved verbatim)
4. **Cross-check** the translated chapter:
   - every required H2 present? — missing → flag with line number.
   - every source code block present with matching SHA256? — missing or divergent → flag.
   - every URL preserved verbatim? — rewritten → flag.
   - every bolded term present (either in original form or in glossary's first-occurrence form)? — missing → flag.
5. **Sanity-check word-count parity**: actual translation word count vs. source word count. Translation typically runs 70–130% of source word count; below 50% suggests content was omitted; above 200% suggests scope was expanded.

### Output

Write findings to `share/reports/04_book-review_<task-id>_ch-<NN>_accuracy.md`. Format:

```markdown
# Accuracy review — ch-NN

**Verdict:** PASS | FAIL
**Word-count ratio:** 0.84 (target 2200–2900)

## Required-H2 coverage
- ✅ "Overview" — line 3
- ❌ "Implementation examples" — MISSING (was a required H2 per source-map.md)

## Code-block integrity
- ✅ block 1 SHA match
- ❌ block 2 — source SHA abc...; chapter SHA def...; line 145

## URL preservation
- ✅ https://arxiv.org/abs/2409.12917 — preserved verbatim
- ❌ https://python.langchain.com/docs/introduction/ → rewritten to /docs/intro

## Bolded-term preservation
- 8/9 preserved; "ReAct" missing → glossary drift candidate

## Word-count ratio
- 0.84 (within 0.7–1.3 band) — accept
```

The verdict is **FAIL** if any required H2 is missing, any code block SHA mismatches (when freeze_code=yes), any URL was rewritten, or the word-count ratio is outside band.

Master reads this file and either promotes the chapter to `dev-reviewed` (PASS) or dispatches am-coder to fix (FAIL).

## Pass 2 — Consistency (cross-chapter)

For the chapter under review, verify terminology + style consistency against `glossary.md` and `style-guide.md`. This is a single-chapter check **plus** a global accumulation.

### Inputs

- `books/<slug>/chapters/ch-NN.md`
- `books/<slug>/glossary.md` (canonical term pairs)
- `books/<slug>/style-guide.md` (frozen patterns, voice rules)
- `books/<slug>/chapters/*.md` (all other chapters — for cross-chapter usage)

### Procedure

1. **First-occurrence rule**: for each glossary term, does this chapter present it as `<Arabic> (<English>)` on first use? Flag any chapter that uses the Arabic form without the parenthetical English at first occurrence.
2. **Glossary drift**: identify any chapter that uses a non-canonical variant of a glossary term (e.g., "وكيل ذكاء اصطناعي" vs canonical "وكيل"). Flag the chapter + the variant.
3. **Untranslated English scan** (already in book_check.py, but reviewer cites line numbers): any English phrase ≥4 words that survives outside a code block — flag.
4. **Tashkeel policy**: if `tashkeel-policy.md` declares this chapter's ratio, verify measured ratio matches target within tolerance.
5. **Style consistency**:
   - heading levels: H2 only at section boundaries (no skipped levels within a chapter)
   - paragraph length: no single paragraph > 200 words (reviewer judgment)
   - reference section: present at chapter end when source has one
6. **Aggregate into glossary-drift report**: append a one-line row to `share/reports/04_book-review_<task-id>_consistency-glossary-drift.md` for each drift term × chapter pair. This file is the cross-chapter view that the daily-focus smoke test produced.

### Output

Write findings to `share/reports/04_book-review_<task-id>_ch-<NN>_consistency.md`. Format:

```markdown
# Consistency review — ch-NN

**Verdict:** PASS | FAIL

## Glossary first-occurrence
- ✅ "وكيل" introduced as "وكيل (Agent)" at line 12
- ❌ "RAG" used at line 47 without "الاسترجاع المعزز بالتوليد (RAG)" first-occurrence form

## Terminology drift
- ✅ all glossary terms used in canonical form
- ❌ line 89: "وكيل ذكي" used (non-canonical; glossary prefers "وكيل")

## Untranslated English
- 0 phrases outside code blocks

## Style guide
- ✅ heading levels consistent
- ❌ paragraph at line 134 exceeds 200 words

## Cross-chapter impact
- Appended 1 row to consistency-glossary-drift.md
```

The verdict is **FAIL** on any glossary first-occurrence violation, any terminology drift, any untranslated English phrase (when the style-guide sets untranslated-english-tolerance < ∞), any heading-level skip, or any paragraph > 200 words.

Master reads this file and either promotes the chapter to `line-edited` (PASS) or dispatches am-coder to fix (FAIL).

## What this skill explicitly forbids

- Combining both passes into a single invocation. Master dispatches two separate calls so each lens stays focused.
- Marking the chapter `approved` (that's the copy-edit pass after every chapter is approved).
- Editing the chapter yourself — dispatch back to am-coder for fixes.
- Editing any file outside `share/reports/04_book-review_*` and `books/<slug>/ledger.md` (master owns the ledger row update).
- Skipping the glossary-drift append, even on PASS — the cross-chapter file is the durable record.

## Mechanical gate

Both passes produce JSON-compatible verdicts (`PASS` / `FAIL`) plus structured findings. Master treats a missing review file as a failed review (timeout = failure, same as the controller's review contract).

## Self-check

This skill ships no `__main__`. Reviewers run `book_check.py` for mechanical gates; this skill is the prose-style overlay.
