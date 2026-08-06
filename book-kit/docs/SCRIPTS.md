# Scripts — flag reference

All 9 scripts live in `book-kit/book_workflow/scripts/`. They're
stdlib-only, idempotent, and ship with `--self-check` plus 89 pytest
tests (`cd book-kit && py -m pytest tests/`).

---

## book_check.py

Mechanical checks on a book's chapters. Runs as the gate before
`build_exports.py` (which fails if `book_check.py` fails unless
`--force` is passed).

**Usage:**
```sh
python book_check.py <project-root>
```

**Checks:**
| Check | Source | Failure |
|---|---|---|
| `fence_balance` | all `.md` in `chapters/` | unclosed triple-backtick fences |
| `forbidden_patterns` | `style-guide.md` §Forbidden | regex match in prose |
| `frozen_lines` | `frozen-lines.json` | line SHA-256 mismatch |
| `glossary_drift` | `glossary.md` + all chapters | chapter missing term used by ≥80% of others (per-chapter exemption via `source-map.md` `glossary_drift_exempt`) |
| `missing_h2` | `source-map.md` required_h2 | required H2 absent |
| `source_ratio` | `source-map.md` word bounds + global tolerance from `style-guide.md` frontmatter | chapter outside ±tolerance of source word count (per-chapter override via `source-map.md` `source_ratio_override`) |
| `tashkeel` | `tashkeel-policy.md` | diacritic ratio outside tolerance |
| `untranslated_english` | prose outside fences, tolerance from `style-guide.md` frontmatter | >tolerance Latin words |
| `word_window` | `style-guide.md` §Word-count windows | chapter outside min/max |

**Tolerances:** the `source_ratio`, `untranslated_english`, and
`glossary_drift` thresholds can be overridden two ways:

1. **Project-wide**: in `style-guide.md` frontmatter:
   ```yaml
   tolerances:
     untranslated_english: 0.30
     source_ratio: 0.40
     stuck_threshold_min: 30
   ```
   Missing keys fall back to the script defaults (0.30 / 0.40 / 30).

2. **Per-chapter**: in `source-map.md` row columns
   `source_ratio_override` (e.g. `0.50`) and `glossary_drift_exempt`
   (`yes` to skip the drift check for that chapter).

**Exit codes:** 0 = pass, 1 = at least one failure.

---

## check_chapter.py

Per-chapter prose enforcer. Runs eight rule-based checks against a single
chapter file and emits a JSON payload (default) or a markdown report
(`--json` not set). Designed to be invoked per chapter during writing /
pre-publish gates.

**Usage:**
```sh
python check_chapter.py <chapter.md> [--config <style-guide.md>]
                            [--json] [--task <task-id>] [--report-dir DIR]
```

**Flags:**
| Flag | Default | Purpose |
|---|---|---|
| `<chapter>` (positional) | — | Chapter markdown to check (e.g. `chapters/ch-03.md`) |
| `--config PATH` | (none) | Path to `style-guide.md` — adds frontmatter overrides for `Beat window:`, `Forbidden patterns:` (CSV), `Countdown tokens:` (CSV). Falls back to script defaults (600-750 window, no forbidden patterns, `["بقي", "لم يبق"]` countdown tokens). |
| `--json` | false | Emit `{"chapter": "ch-NN", "checks": [{name, status, evidence}]}` to stdout instead of writing the markdown report. |
| `--task ID` | `unknown` | Task id used in the markdown report's filename + metadata header. |
| `--report-dir DIR` | `reports` | Directory prefix; markdown report is written to `<DIR>/<task-id>/check_chapter_<chapter>.md`. |

**Checks (all return `CheckResult(name, status, evidence)`):**
| Check | Source | Failure / Warn rule |
|---|---|---|
| `word_count_per_beat` | H2/H3 split, frontmatter `Beat window: lo - hi` (default 600-750) | FAIL if any beat < 0.5*lo or > 1.5*hi; WARN if any beat in `[0.5*lo, lo) ∪ (hi, 1.5*hi]`; else PASS |
| `banned_patterns` | style-guide frontmatter `Forbidden patterns: <csv>` (or `## Forbidden patterns` code block) | FAIL on any regex match outside code fences |
| `quote_pair_balance` | prose | FAIL if `«` count ≠ `»` count; WARN if any single paragraph has both an opener and a closer (suggests bad nesting) |
| `dialogue_own_line` | prose | WARN if a paragraph mixes narration with `«…»` on the same line (closing punctuation alone is OK) |
| `closing_hook` | last prose paragraph before `<!-- end-of-chapter -->` marker, falling back to last paragraph of file | FAIL if last paragraph > 8 words (configurable via `max_words`) — strict short-imperative convention |
| `countdown` | filename `ch-NN` ≥ 3 (hard-coded until P5), `Countdown tokens:` (CSV) | FAIL if fewer than 1 occurrence; chapters before the threshold are skipped (PASS-with-skip-evidence) |
| `arabic_punctuation` | prose | FAIL on any Latin `, ; ? !` (period excluded) on a line that contains Arabic characters; URL lines + code fences skipped |
| `sentence_length` | prose | WARN if median sentence word-count > 22 (configurable via `target_median`) |

**Exit codes:** 0 if no FAIL, 1 if any FAIL, 2 if the input file is missing.

**Tokenization is local.** `word_count`, `read_md`, `outside`, and the
`FENCE` regex are copied verbatim from `book_check.py` rather than
imported across script boundaries — both scripts must stay runnable
standalone. Keep them in sync if either is updated.

**Use it like:**
```sh
# Per-chapter pre-gate (writes markdown report under reports/<task>/)
python check_chapter.py chapters/ch-03.md \
    --config style-guide.md \
    --task T-2026-08-05-001

# Same, but JSON for pipelines
python check_chapter.py chapters/ch-03.md \
    --config style-guide.md --json | jq '.checks[] | select(.status=="FAIL")'
```

---

## bilingual_smoke.py

URL / bold-term / H2 diff between chapter and source. The translation
content-coverage check.

**Usage:**
```sh
python bilingual_smoke.py <project-root> [--out FILE]
```

**Findings per chapter:**
| Finding | Meaning |
|---|---|
| `urls.missing` | URL in source but not in chapter at all |
| `urls.rewritten` | URL in source changed to a different URL in chapter |
| `urls.source_truncated` | Source URL is a prefix of chapter URL (chapter has canonical full URL — source-extraction bug) |
| `bold_terms.expected_translation` | Bolded term in source prose correctly translated to Arabic (informational) |
| `h2.missing_in_chapter` | Source H2 absent in chapter |
| `h2.extra_in_chapter` | Chapter H2 not in source |

Writes JSON report to `--out` or stdout. Exit 0 always (informational).

---

## split_source.py

Chunked-write source sizer. Splits a source file at H2 boundaries per
the protocol:

| Source size | Parts | Target part size |
|---|---|---|
| ≤ 20 KB | 1 | whole file |
| 20–50 KB | 2 | source_size / 2 |
| > 50 KB | ⌈size / 18 KB⌉ | 18 KB |

**Usage:**
```sh
python split_source.py <source> [--parts N] [--out DIR] [--prefix PREFIX]
```

**Outputs:**
- `<prefix>-part-N.txt` — one file per part
- `<prefix>-manifest.json` — sidecar with `{source, source_bytes, n_parts, parts: [{part, path, bytes}]}`

Falls back to paragraph boundaries if source has no H2s.

---

## extract_figures.py

Wraps poppler's `pdfimages -png -p`. Extracts embedded images from a
PDF as PNGs and emits a manifest.

**Usage:**
```sh
python extract_figures.py <pdf> [--out DIR] [--slug SLUG]
```

**Outputs:**
- `figures/<slug>-page-<N>-<idx>.png` — extracted images
- `figures/<slug>-manifest.json` — `{pdf, slug, figures: [{page, num, type, width, height, path}]}`

Requires `pdfimages` on PATH (poppler 0.86+). Stdlib `subprocess` for the
call.

---

## build_exports.py

Builds TOC, glossary, index, and README for the book. RTL-aware with
Arabic-Indic numerals when the style-guide declares RTL or Arabic.

**Usage:**
```sh
python build_exports.py <project-root> [--force]
```

**Outputs:**
- `exports/toc.md` — TOC with chapter titles + page placeholders
- `exports/glossary.md` — terminology sorted case-insensitive
- `exports/index.md` — term → chapter:line hits
- `exports/README.md` — build manifest + deliverables list
- `exports/manifest.json` — if `frozen-lines.json` exists at root

`--force` skips the `book_check.py` gate (useful for development builds
where you want to see partial output).

---

## poll_progress.py

Watch a book's chapter state and emit a progress dashboard.

**Usage:**
```sh
python poll_progress.py <project-root> [--once | --watch] [--interval N]
```

**Modes:**
- `--once` — print snapshot to stdout, exit
- `--watch` — loop every `--interval` seconds (default 15), update `<root>/exports/.dashboard.html`

**Reads `.translate-progress.json`** if present. Stuck detection: any
chapter with `status in (in_progress, partial)` and `last_updated > N
min ago` is flagged `stuck`. Threshold `N` defaults to 30 and is
configurable via `style-guide.md` frontmatter `tolerances.stuck_threshold_min`.

Glob covers `ch-*.md`, `app-*.md`, `introduction.md`, `preface.md`.

---

## fix_source_urls.py

Repair 6 distinct `pdftotext` artifacts in source `.txt` files.

**Usage:**
```sh
python fix_source_urls.py <source-dir> [--dry-run]
python fix_source_urls.py --self-check
```

**Fixes:**
| Pattern | Detection | Action |
|---|---|---|
| Pure-digit line after URL | `^\d+$` immediately after URL line | Drop the digit line |
| `/N` glued to URL | `https?://.../(d{1,3})$` | Strip the trailing `/N` |
| URL split across lines | URL line + URL-fragment line | Join them |
| Doubled last segment | `wordword` at end of URL | Strip the second copy |
| Trailing `..` | URL ending with `..` | Trim to single `.` |
| Trailing `/#` | URL ending with `/#` | Strip the `#`, keep the `/` |

**Known NOT auto-fixed** (10 documented edge cases — manual review):
- Page numbers glued without `/` separator (e.g. `arxiv.org/abs/1707.0634712`)
- Doubled segments not at end of URL (e.g. `databases/databases`)
- Two URLs concatenated (e.g. `arxiv.org/pdf/...https://github.com/...`)
- Concatenated adjacent path lines (e.g. `rankingsapi/v1/...`)

Idempotent. Self-check covers all 6 patterns + regressions + idempotency.

---

## md2pdf.py

Render Arabic Markdown chapters to RTL PDF via HTML + Chrome/Edge
headless. Used in the build chain after `extract_figures.py` to produce
print-ready PDFs with embedded figure images.

**Usage:**
```sh
python md2pdf.py <md-file> [<md-file> ...] [--out DIR] [--css FILE] [--figures-manifest FILE] [--keep-html]
```

**Flags:**
| Flag | Default | Purpose |
|---|---|---|
| `<files>` (positional, ≥1) | — | Markdown chapter files to render |
| `--out DIR` | `exports/pdf` | Output directory for PDFs |
| `--css FILE` | (none) | Path to extra CSS appended to the bundled RTL stylesheet |
| `--figures-manifest FILE` | (none) | Path to a manifest from `extract_figures.py`. When provided, the script scans each chapter for `> **الشكل N:**` blockquote placeholders and prepends the matching figure `<img>` in order of appearance. |
| `--keep-html` | false | Also write intermediate HTML files to `<out>/html/` for debugging |

**Behavior:**
- Default CSS declares `direction: rtl` on `<body>`, sets Arabic fonts (Cairo / Sakkal Majalla / Segoe UI), and uses `LTR` + `unicode-bidi: embed` for `<pre>`/`<code>` blocks.
- Chrome is auto-discovered: `$CHROME_PATH`, then common install paths for Google Chrome + Microsoft Edge.
- Figure insertion is sequential: chapter placeholders 1, 2, 3… map to manifest figures in order. Placeholders beyond the manifest count stay verbatim. Extra manifest figures (no matching placeholder) are dropped.

**Requires:**
- `markdown-it-py` (`pip install markdown-it-py`)
- Chrome or Edge installed (one of the auto-discovered paths)

**Exit codes:** 0 = success, 1 = missing input files / Chrome not found / subprocess failure.

---

## gate_summary.py

Per-chapter gate artifact emitter. Reads the P2 `check_chapter` output,
the P3 `book_check.py` output, the book's `frozen-lines.json` and
`ledger.md`, plus the latest `04_review_*.md`, and renders a 5-field
gate summary (`Word count`, `Book-check`, `Reviewer`, `Frozen lines
touched`, `Open questions`) into `share/reports/<task>/02_gate_ch-NN_<task>.md`.
Wired into the orchestrator's Phase 7 (see `agents_manager/book-gen-orchestrator/SKILL.md`).

**Usage:**
```sh
python gate_summary.py --book books/<slug>/ --chapter ch-NN \
                       --review share/reports/04_review_<task>_P<N>.md
                       [--task T-YYYY-MM-DD-NNN] [--reports-dir <path>]
                       [--out <path-under-book>] [--loop N] [--window LO-HI]
```

**Inputs:**
| Source | Purpose |
|---|---|
| `<book>/chapters/ch-NN.md` | Word count (regex-based, like `check_chapter.py`) |
| `<book>/frozen-lines.json` | Per-chapter frozen-line manifest (optional) |
| `<book>/ledger.md` | Counts `## Open questions` numbered items |
| `<reports>/<task>/check_chapter_ch-NN.md` (or `.json`) | P2 check payload (any/all rules can be FAIL) |
| `<reports>/<task>/book_check.json` | P3 cross-chapter payload |
| `<reports>/<task>/04_review_<task>.md` | am-review output (counts `### CRITICAL` / `### HIGH` headers) |

**Output:** `share/reports/<task>/02_gate_ch-NN_<task>.md` (overridable via `--out <path>`; the override must resolve under `--book` — defensive guard against misconfigured CI).

**Status logic (verbatim from plan §P6):**
- `APPROVED` — all checks PASS and review has 0 HIGH/CRITICAL
- `FIX-LOOP-N` — any check FAIL or any review HIGH (N = `--loop` arg, default 1)
- `REJECTED` — review has any `### CRITICAL` header

**Exit codes:** 0 = APPROVED, 1 = FIX-LOOP-N or REJECTED, 2 = input error (missing review, missing chapter, `--out` outside `--book`, invalid `--window`).

**Review parsing:** case-sensitive top-of-line `^### CRITICAL$` and `^### HIGH$` headers; sub-issues are every other `^### ` header (case-insensitive on sub-issues; only the exact severity strings are skipped).

**Stdlib-only.** No new dependencies. Forces UTF-8 stdio at the top of the module so `--help` doesn't crash on Windows-cp1256 terminals (P4 #15 / P5 #22 inheritance).

---

## index_reports.py

Builds a deterministic markdown index for the shared phase reports. Scans only
top-level files named `00_*.md` through `08_*.md`, silently skips malformed
names, groups rows by phase prefix, and sorts dates descending within each
phase.

**Usage:**
```sh
python index_reports.py [--regen] [--reports-dir <path>]
```

**Modes:**
| Mode | Behavior |
|---|---|
| default | Print generated `INDEX.md` content to stdout; write nothing. |
| `--regen` | Write generated content to `<reports-dir>/INDEX.md`. The output path is resolved and verified to be directly under the reports directory before writing. |

**Status priority (first match wins in the first 200 lines):**
1. First supported token in a fenced `verdict` block: `PASS`, `FAIL`, `APPROVED`, `FIX-LOOP`, `REJECTED`, or `READY_FOR_REVIEW`.
2. `[auto-accepted triageable]` marker → `PASS_WITH_WARN`.
3. Next token on a `Verdict:` line.
4. First data-cell value under a markdown table's `Status` column.
5. `—` when no status signal exists.

**Date:** first `YYYY-MM-DD` in the filename, otherwise the first such date in
the report's first 30 lines, otherwise `—`.

**Empty directory:** emits the table header followed by `No reports found`.
Re-running `--regen` with unchanged inputs is byte-identical. The generated
`INDEX.md` is not re-indexed because it does not match the phase filename
pattern.

**Exit codes:** 0 = rendered or regenerated, 2 = output-path/write error.

**Stdlib-only.** No new dependencies. Forces UTF-8 stdio at module load before
any argparse construction or output.
