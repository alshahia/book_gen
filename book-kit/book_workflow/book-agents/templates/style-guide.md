# Style Guide — [Working Title]

Status: DRAFT | CONFIRMED

## Presentation
- Chapter length/rhythm: [short punchy sections vs. long discursive chapters]
- Structural devices: [subheadings, lists, callouts, recurring chapter-opening/closing conventions]
- Visual-style samples: see `book-kit/examples/` (10 rendered HTML + PDF pairs) and `book-kit/docs/STYLE_DECISIONS.md` for the "when to use" rule behind each dialogue-density, tashkeel, separator, and closing-hook choice.

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

## Tolerances (v1.1.0+)

`book_check.py` reads these YAML-frontmatter values at runtime. Missing
keys fall back to the script defaults shown below. Per-chapter overrides
live in `source-map.md` (columns `source_ratio_override` and
`glossary_drift_exempt`).

```yaml
---
tolerances:
  untranslated_english: 0.30   # <30% latin words outside code fences
  source_ratio: 0.40            # target word count within ±40% of source word count
  stuck_threshold_min: 30       # flag chapters updated > N min ago with status in_progress
---
```

---

Confirmation: user must confirm this guide before Phase 5 (writing plan) begins.

## Mechanical gates

- **`book_check.py` — Phase 6, every chapter completion:** consumes `## Word-count windows`, `## Forbidden patterns`, and `## Frozen lines`, then cross-checks the `frozen-lines.json` manifest. Reads tolerances from the YAML frontmatter of THIS file (v1.1.0+). T1 is the primary consumer gate.
- **`build_exports.py` — Phase 5 export gate:** invokes `book_check.py` before assembling exports, so it indirectly enforces this guide.
- **`strip_publish_annotations.py` — no direct read:** clean-export stripping does not consume `style-guide.md`.
- The orchestrator runs T1 at every chapter completion through the book-writer skill.

## Open questions

1. Are word-count windows global defaults, or should every chapter have an explicit numeric row?
2. Which forbidden patterns are content rules versus temporary drafting markers?
3. Who can authorize a frozen-line change after the manifest is generated?
4. When should a chapter declare `glossary_drift_exempt: yes` vs. just include the missing term naturally in the prose?