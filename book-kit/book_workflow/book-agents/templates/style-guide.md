# Style Guide — [Working Title]

Status: DRAFT | CONFIRMED

## Presentation
- Chapter length/rhythm: [short punchy sections vs. long discursive chapters]
- Structural devices: [subheadings, lists, callouts, recurring chapter-opening/closing conventions]

## Voice
- Reference points from intake: [specific traits to emulate, not wholesale imitation]
- Formality level: [value]
- Person: [first/second/third — and why]
- Pacing/rhythm notes: [value]

## POV & tense (fiction/hybrid only)
- POV: [first/third, single/multiple]
- Tense: [past/present]
- Notes on consistency across chapters: [value]

## Word-count windows

<!-- REQUIRED. If this section is absent or contains no numeric rows, book_check.py skips word-count enforcement. -->

| ch-NN | word-min | word-max | rationale |
|---|---:|---:|---|
| ch-NN | [minimum] | [maximum] | [why this window fits the chapter] |

## Forbidden patterns

<!-- REQUIRED. Add one regular expression per line. # comments are ignored by book_check.py. -->

```
# Example only: \\bTODO\\b
```

## Frozen lines

<!-- REQUIRED human-readable WHY list. Exact bytes and SHA256 hashes live in frozen-lines.json. -->

- `chapters/ch-NN.md:LINENUM` — [why this line is frozen]

---
Confirmation: user must confirm this guide before Phase 5 (writing plan) begins.

## Mechanical gates

- **`book_check.py` — Phase 6, every chapter completion:** consumes `## Word-count windows`, `## Forbidden patterns`, and `## Frozen lines`, then cross-checks the `frozen-lines.json` manifest. T1 is the primary consumer gate.
- **`build_exports.py` — Phase 5 export gate:** invokes `book_check.py` before assembling exports, so it indirectly enforces this guide.
- **`strip_publish_annotations.py` — no direct read:** clean-export stripping does not consume `style-guide.md`.
- The orchestrator runs T1 at every chapter completion through the book-writer skill.

## Open questions

1. Are word-count windows global defaults, or should every chapter have an explicit numeric row?
2. Which forbidden patterns are content rules versus temporary drafting markers?
3. Who can authorize a frozen-line change after the manifest is generated?
