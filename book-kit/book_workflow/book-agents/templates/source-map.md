---
template: source-map
purpose: Bind each target chapter to its source file + per-chapter operational envelope (word-count window, required H2 sections, code-block freeze policy). Required for translation-mode projects; ignored by `book_check.py` for native book-gen.
phase: intake
consumers: [book_check.py, book-writer, am-review, master]
---

# Source Map — [Working Title]

> **Translation-mode only.** Skip this template for native book-gen (no source files exist). When the Phase-0 `Is translation?` toggle is set, master copies this file from the template and the writer reads it on every dispatch.

## Bindings

| chapter | source | word_min | word_max | required_h2 | freeze_code | source_ratio_override | glossary_drift_exempt |
|---|---|---:|---:|---|:-:|:-:|:-:|
| `ch-NN-<slug>.md` | `source/ch-NN.txt` | [min] | [max] | [comma-list, optional] | yes | - | no |
| `introduction.md` | `source/introduction.txt` | [min] | [max] | [comma-list, optional] | yes | - | no |
| `app-X-<slug>.md` | `source/app-X.txt` | [min] | [max] | [comma-list, optional] | yes | - | no |

Columns:

- **chapter** — target filename as it appears under `chapters/`. With or without slug suffix; `book_check.py` matches either.
- **source** — path under `source/`, relative to project root. The source may be a `.txt`, `.md`, or extracted PDF text.
- **word_min / word_max** — operational word-count envelope for the translation. `book_check.py` flags out-of-window chapters.
- **required_h2** — comma-separated H2 titles that MUST appear in the target. `book_check.py` flags missing sections (catches mid-write truncation).
- **freeze_code** — if `yes`, fenced code blocks must be byte-identical to the source's code blocks (after stripping comments and re-flowing whitespace). `book_check.py` verifies by sha256 of the normalized code-block bodies.
- **source_ratio_override** *(optional, v1.1.0+)* — per-chapter override on the global `source_ratio` tolerance from `style-guide.md` frontmatter. Accepts a fraction (e.g. `0.50`) or percentage (e.g. `50%`). Use `-` (or omit) to inherit the global tolerance.
- **glossary_drift_exempt** *(optional, v1.1.0+)* — `yes` skips the glossary-drift check for this chapter. Use sparingly: only when a chapter legitimately doesn't reference a high-usage glossary term (e.g. intro/overview chapters, agent-to-agent communication).

## Generation rule

This file may be hand-authored OR auto-generated from the `source/` folder. The smoke-test generator at `book_workflow/scripts/build_source_map.py` walks `source/` and emits a default envelope (word_min = 50% of source word count, word_max = 180% of source word count, required_h2 empty, freeze_code = yes). Master runs this generator when the toggle is set and no `source-map.md` exists yet.

## Naming inconsistencies

The source folder may use non-1:1 naming (e.g., `chapter-01.txt` paired with `ch-01.md`). The bindings table is the authority — never derive it from filenames alone.

## Source

- Authorized by: [intake.md](./intake.md) §`Is translation?` + source-root field
- Reference: [decisions-log.md](./decisions-log.md) entry naming source-root convention

## Open questions

1. Should `freeze_code` be `yes` by default, or per-chapter opt-in?
2. Should `word_min`/`word_max` be derived from source word count or set by the user?
3. Should out-of-window failures warn at first run and hard-fail on the second run (to allow intentional expansions)?

## Mechanical gates

- **`book_check.py`** — reads `## Bindings` table; uses it for source-ratio, missing-H2, and code-block-freeze checks.
- **Master** — re-runs `build_source_map.py` whenever `source/` is updated and no `source-map.md` exists yet.
- **Writer** — does NOT edit this file; flags missing entries to master.
