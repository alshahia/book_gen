# Translation Mode

Translation-mode is a first-class book-gen path. Triggered when
`intake.md §10` says "Is translation? = yes". The orchestrator then runs
the **two-pass `book-reviewer`** (Branch A) instead of the standard
3-pass review (Branch B).

```
master → research (source-map) → planning (source binding) → design (RTL + tashkeel + freeze-code) → master → coder (chunked-write + .translate-progress.json) → book-reviewer (Pass 1 + Pass 2)
```

---

## §10 Intake — 7 translation fields

When the user signals translation intent, master prompts for these fields
in addition to the standard 9:

| # | Field | Example |
|---|---|---|
| 10 | `Is translation?` | `yes` |
| 11 | `Source root` | `source/` (relative to `books/<slug>/`) |
| 12 | `Source-naming convention` | `ch-NN.pdf` / `chapter-NN.txt` / `app-X.pdf` |
| 13 | `Target slug pattern` | `ch-NN-<slug>.md` / `app-<X>-<slug>.md` |
| 14 | `Tashkeel policy` | `none` / `light` / `full` (Arabic diacritics) |
| 15 | `Freeze code blocks` | `yes` (preserve source code verbatim) / `no` |
| 16 | `Source map filled` | `yes` (gates Phase 3 — see below) |

These go into the §10 block of `intake.md`. The orchestrator refuses to
advance past Phase 3 (outline) if `Is translation? = yes` but `Source map
filled = no`.

---

## Source map

**Path:** `books/<slug>/source-map.md`

Per-chapter binding to source file. Schema (parsed by `book_check.py`):

```markdown
| ch-01.md | source/ch-01.pdf | 1500 | 3000 | Overview, Method |
| ch-02.md | source/ch-02.pdf | 1200 | 2500 | Overview |
| app-a.md | source/appendix-a.pdf | 800 | 2000 | - Overview |
```

| Column | Meaning |
|---|---|
| 1 | Target chapter filename |
| 2 | Source file (relative to `source/`) |
| 3 | `word_min` — lower bound for chapter word count |
| 4 | `word_max` — upper bound |
| 5 | `required_h2` — comma-separated H2s the chapter must include (e.g. "Overview, Method") |

`book_check.py` reads this and flags:

- `missing_h2` — chapter lacks a required H2
- `source_ratio` — chapter word count outside ±40% of source word count
- `fence_balance` — unclosed code fences

---

## Chunked-write + resume

**Script:** `book-kit/book_workflow/scripts/split_source.py`

For sources >20 KB, the writer doesn't load the whole thing at once.
`split_source.py` splits at H2 boundaries sized per the chunked-write
protocol:

| Source size | Parts | Target part size |
|---|---|---|
| ≤ 20 KB | 1 | whole file |
| 20–50 KB | 2 | source_size / 2 |
| > 50 KB | ⌈size / 18 KB⌉ | 18 KB |

Each part is written to `<prefix>-part-N.txt`. A manifest sidecar
records part paths + byte counts.

**.translate-progress.json** tracks per-chapter resume state:

```json
{
  "chapters": {
    "ch-01.md": {
      "status": "in_progress",
      "parts_written": 2,
      "expected_parts": 3,
      "last_byte_offset": 18234,
      "last_line_number": 412,
      "session_id": "sess-2026-08-05-001",
      "started_at": "2026-08-05T10:00:00Z",
      "last_updated": "2026-08-05T10:45:00Z",
      "checksum": "sha256:...",
      "glossary_gaps": [],
      "notes": []
    }
  }
}
```

If the writer's session crashes, the next session reads this file and
resumes from `parts_written + 1`.

---

## Source URL cleanup

**Script:** `book-kit/book_workflow/scripts/fix_source_urls.py`

`pdftotext -layout` introduces 6 distinct artifacts in source `.txt`
files. Run this script BEFORE generating the source map so
`bilingual_smoke.py` doesn't flag false positives.

| Pattern | Example | Fix |
|---|---|---|
| Pure-digit line (page number) after URL | `https://example.com/foo` + `28` (next line) | Drop the digit line |
| Page number glued to URL on same line | `https://cloudskillsboost.google/6` | Strip trailing `/6` |
| Doubled last segment | `langgraphlanggraph` | → `langgraph` |
| Truncated URL split across lines | URL on 2 lines | Join them |
| Trailing `..` | `project..` | → `project.` |
| Trailing `/#` (empty fragment) | `marco-fago/#` | → `marco-fago/` |

10 known complex corruptions are NOT auto-fixed (high false-positive
risk). Documented in the script header.

```sh
python book-kit/book_workflow/scripts/fix_source_urls.py source/ --dry-run
python book-kit/book_workflow/scripts/fix_source_urls.py source/
```

---

## Two-pass review (Branch A)

**Skill:** `agents_manager/book-reviewer/SKILL.md`

When the orchestrator detects translation-mode (Branch A dispatch), it
instructs `am-review` to load `book-reviewer/SKILL.md` and run **two
separate dispatches**:

### Pass 1 — Accuracy vs. source

For each chapter, compare:
- All URLs in source present in chapter (verbatim or canonical extension)
- All required H2s present in chapter
- Word count within source-map bounds
- No content drops (no source H2 absent from chapter)

Output: `share/reports/04_book-review_ch-NN_pass1.md`

### Pass 2 — Cross-chapter consistency

For each chapter, compare:
- Glossary terms used consistently across all chapters
- Style-guide voice adherence (sentence length, formality)
- Bible terminology alignment

Output: `share/reports/04_book-review_ch-NN_pass2.md`

The two passes are NEVER combined — they look for different defect
classes and produce different reports. Master waits for both before
marking the chapter `approved`.

If `intake.md §10 = "Is translation? = yes"` but `source-map.md` is
missing, the orchestrator REFUSES to dispatch review and surfaces to
the user.

---

## RTL export

**Script:** `book-kit/book_workflow/scripts/build_exports.py`

When `style-guide.md` declares `rtl: true` or `language: ar`, the
exporter:

- Wraps the TOC in `<div dir="rtl">` so markdown renderers apply RTL flow
- Converts page numbers to Arabic-Indic digits (٠١٢٣٤٥٦٧٨٩)
- Prefixes chapter labels with `الفصل N:` instead of `Chapter NN:`

The heuristic fallback: if `style-guide.md` body is majority-Arabic
(>=30% Arabic codepoints in the first 500 visible chars) and no
explicit directive, treat as RTL/ar automatically.

---

## Output root

Translation projects use the same `books/<slug>/` layout. No special
directory for translation artifacts — the only translation-specific
files are `source-map.md` and `.translate-progress.json`.

The translation project at `books/agentic-design-patterns-ar/` (29
chapters, 800 KB Arabic manuscript) is a reference implementation. Its
`exports/SMOKE_REPORT.md` documents the v0.2.0 alpha + full release
validation against all 5 mechanical checks + all 5 bilingual checks.
