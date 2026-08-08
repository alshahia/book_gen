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

### Continuity check (P8)

In addition to the per-chapter checks above, `book_check.py` runs two
cross-chapter continuity detectors that read the book's narrative ledger
files. Both are fail-fast: any missing motif or anchor contributes to
the FAIL verdict and emits a `Coin arc:` / `Motif arc:` line on stderr.

**`## Continuity anchor` (from `bible.md`)** — each row is a tracked
motif that must persist across the chapters named in `Scope`. Rows use
the format `| Keyword | Quote | Scope |` with `Scope` written as
`ch-XX..ch-YY` (the chapter separator accepts ASCII `-` or en-dash
U+2013 per WARN #19 inheritance). The `Quote` cell may include
surrounding ASCII / smart quotes; both styles are stripped before
matching.

```sh
## bible.md
## Continuity anchor

| Keyword | Quote | Scope |
|---|---|---|
| silver coin | "glinted in the morning light" | ch-01..ch-05 |
| locket | the locket her mother left her | ch-02..ch-04 |
```

**`## Tracked motifs` (from `style-guide.md`)** — each bullet under the
section is a motif name. Trailing `:<reason>` text after the name is
stripped. The detector scans every `chapters/ch-*.md` (sorted) for the
substring (case-insensitive).

```sh
## style-guide.md
## Tracked motifs

- silver coin: introduced ch-01, paid ch-05
- compass
```

**Arc labels per chapter:** `(introduced)` for the first hit, `(paid)`
for the last, `(mentioned)` for middle hits, `(solo)` for single-chapter
arcs, `(missing)` when the keyword is absent. Stderr output (Unicode
em-dash):

```
Coin arc: ch-01 (introduced) -> ch-03 (mentioned) -> ch-05 (paid) - PASS
Motif arc: ch-01 (introduced) -> ch-02 (mentioned) -> ch-03 (paid) - PASS
```

**JSON payload:** the top-level payload gains two new keys when chapters
exist:

| Key | Shape |
|---|---|
| `continuity` | `[{keyword, quote, scope, arc, status, chapters_missing}, ...]` |
| `coin_arc` | `[{motif, arc, status, chapters_missing}, ...]` |

The `summary.checks` block also gains `continuity` and `coin_arc`
counters (count of FAIL rows each).

**Stdlib-only.** No new dependencies. Forces UTF-8 stdio before any
`Coin arc:` / `Motif arc:` print so non-ASCII arrow + em-dash chars
do not crash on Windows-cp1256 hosts (P4 #15 / P5 #22 inheritance).
Missing `bible.md` or missing `## Continuity anchor` section degrades
silently to an empty `continuity` list — same fall-through as the
existing `glossary_terms` / `parse_style_guide_tolerances` helpers.

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

### check_chapter.py --lang

- Flag: `--lang <ar|en>`
- Behavior: runs LanguageTool grammar check after the existing 8 checks
- Output: adds `arabic_grammar` or `english_grammar` row to JSON
- Requires: LanguageTool MCP server (configured in `~/.config/opencode/opencode.json`)

The grammar pass is **additive and opt-in** — without `--lang` the script
behaves exactly as before (8 rows). The row's status is `PASS` when the server
reports zero matches, `FAIL` otherwise (evidence carries the issue count plus
the first three messages with their offsets and rule ids). If the MCP server
can't be reached — Node absent, offline, first-run download failed — the row is
`WARN`, not `FAIL`: an optional external dependency must never block a chapter
that passes the eight built-in rules.

**MCP entry** (in `~/.config/opencode/opencode.json`, outside this repo):
```json
"languagetool": {
  "type": "local",
  "command": ["npx", "-y", "@goncalomb/languagetool-mcp"],
  "enabled": false,
  "timeout": 60000
}
```
The package downloads the LanguageTool server and the requested language pack
(`ar` / `en`) on first call, so the first run is slow. **Java 17+ is required**
on the host -- LanguageTool is a JVM service.

> **DEFERRED (P10):** `@goncalomb/languagetool-mcp` is not published on the
> npm registry -- `npm view @goncalomb/languagetool-mcp` returns **404 Not
> Found** (independently verified). The tool name this script calls
> (`check_text`) is therefore unverified against a live server. The MCP entry
> ships with `enabled: false` until the package name resolves.
>
> Behaviour while disabled:
> - The script's `--lang ar` / `--lang en` row **degrades to `WARN`** whenever
>   the MCP server is unreachable (transport failure, missing package, Node
>   absent, offline host). An optional external dependency must never block a
>   chapter that passes the eight built-in rules.
> - `--lang` is **safe to pass** in the meantime: it adds the grammar row but
>   cannot turn a passing chapter into a `FAIL`.
> - The entry uses opencode's `McpLocalConfig.command` array form
>   (`["npx", "-y", "..."]`) per the published schema
>   (`$defs.McpLocalConfig.command` is `array<string>`; there is **no** `args`
>   property).
>
> Re-enabling: once the package name, tool name, arguments, and Arabic pack
> support are verified live, flip the single `"enabled": false` → `true` and
> restart the MCP host. No code change is required.
>
> Closest published alternative is `@dpesch/languagetool-mcp-server`, but it
> targets the LanguageTool **Pro API** (needs an API key; no local JVM; no
> auto-downloaded Arabic pack) -- a materially different deployment shape,
> and therefore not a drop-in replacement.

```sh
# Arabic grammar pass on top of the eight prose rules
python check_chapter.py chapters/ch-03.md --config style-guide.md \
    --lang ar --json | jq '.checks[] | select(.name=="arabic_grammar")'
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

### Book mode (P12)

Assembles a whole book into a single PDF: cover, preface, auto-linked table of
contents, every chapter in `toc.md` order, and back-matter. Paper size and
fonts come from the book's `style-guide.md` frontmatter and page numbers appear
in the bottom-right corner (suppressed on the cover). Designed for the
orchestrator's Phase 6 dispatch (see `agents_manager/book-gen-orchestrator/SKILL.md`).

**Usage:**
```sh
python md2pdf.py --book <book-root> [--toc REL] [--style-guide REL]
                 [--out REL] [--html-only]
                 [--title T] [--author A] [--isbn I] [--build-date D]
```

**Flags:**
| Flag | Default | Purpose |
|---|---|---|
| `--book DIR` | — | Book root; reads `toc.md` and `style-guide.md` relative to it. |
| `--toc REL` | `toc.md` | Table-of-contents file, relative to the book root. |
| `--style-guide REL` | `style-guide.md` | Style guide supplying `paper_size`, `fonts`, `cover_text`, and metadata frontmatter. |
| `--out REL` | `exports/book.html` (`--html-only`) or `exports/book.pdf` | Output path, relative to the book root. `--book` mode refuses paths that escape the book root (no `..` components, no absolute paths elsewhere). |
| `--html-only` | false | Stop after the assembled HTML; no Chrome/Edge needed. Use to defer PDF rendering when the browser is missing. |
| `--title / --author / --isbn / --build-date` | — | Book metadata. Overrides the style guide's frontmatter when both are present (handy for per-edition builds). |

**Behavior:**
- The document is assembled in this order: cover `--page-break-after` -> preface (optional, `preface.html`/`preface.md`/`front-matter.html`/`front-matter.md`) -> `<nav class="book-toc">` with one `<a href="#<slug>">` per chapter -> chapters (toc.md order) -> back-matter (optional).
- Section ids are derived from the chapter filename: `ch-01.md` -> `id="ch-01"`. Duplicate slugs get a numeric suffix.
- Page numbers come from `DEFAULT_CSS + @page { @bottom-right { content: counter(page); } }`, with the cover suppressed via `@page :first { @bottom-right { content: "" } }`.
- Head metadata (`<title>`, `<meta name="author">`, `<meta name="isbn">`, `<meta name="identifier" content="urn:isbn:...">`, `<meta name="dcterms.created">`, `<meta name="paper-size">`) is written so Chrome carries it into the PDF.
- A missing `toc.md`, an empty chapter list, or any toc entry pointing at a missing file is a graceful `BookError` (exit 2). Chrome/Edge missing while `--html-only` is *not* set exits 3 (deferred rendering).
- The P11 `chapters-rendered/` mirror is preferred when present so rendered mermaid figures reach the PDF instead of raw fences.

**Frontmatter shape (style-guide.md):**
```yaml
---
paper_size: B5         # A4, A5, B5, B6, Letter, US-Letter, Legal or raw "210mm 297mm"
fonts:
  body: Cairo
  display: Amiri
cover_text: |
  My Book
  A second cover line
title: My Book
author: Author Name
isbn: 978-0-00-000000-0
build_date: 2026-08-08
---
```

**Exit codes (book mode):** 0 = success, 2 = input error (missing toc, missing chapter, `--out` escapes the book root), 3 = browser missing and `--html-only` not set.

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

---

## duckduckgo_search.py (P9)

Thin DuckDuckGo HTML scraper. Used as the third-tier fallback in the
multi-source research pipeline when both Exa and Firecrawl return
fewer than three unique URLs. Talks to
`https://html.duckduckgo.com/html/?q=...` (server-rendered, no JS)
via `urllib.request` and parses `result__a` / `result__snippet`
classes with stdlib regexes.

**Usage:**
```sh
python duckduckgo_search.py "<query>" [--max-results N]
```

**Output:** JSON list `[{"url", "title", "snippet"}, ...]` to stdout.

**Importable as a library:**
```python
from duckduckgo_search import duckduckgo_search
results = duckduckgo_search("python testing", max_results=10)
```

**Behavior on failure:** any network error (DNS, timeout, non-2xx,
captcha) writes one line to stderr and returns `[]`. The parent
pipeline never crashes on a flaky DDG response.

**Exit codes:** 0 = JSON written, 2 = argparse / network error
unrecoverable from the CLI side.

**Stdlib-only.** No new dependencies. Forces UTF-8 stdio at module load
before any argparse construction or output (WARN #15 / #22 inheritance).

---

## parallel_search.py (P9)

Orchestrator that merges Exa + Firecrawl result lists and, with the
`--fallback` flag, appends DuckDuckGo results when the dedup'd
primary union has fewer than three unique URLs. The agent invokes
the MCP layers (they require OAuth + LLM-side tool calls), writes each
layer's JSON list to a temp file, then calls this CLI with the file
paths. The CLI handles dedup, source tagging, fallback dispatch, and
the search-trail audit log.

**Usage:**
```sh
python parallel_search.py "<query>" [--max-results N] [--fallback]
    [--exa-results <path>] [--firecrawl-results <path>]
    [--task <task-id>]
```

**Layer contract:** each `--exa-results` / `--firecrawl-results` path
points to a JSON file containing `[{"url", "title", "snippet"}, ...]`.
Missing files are treated as empty (graceful degradation).

**Source tagging:** every result dict gets a `source: "exa" | "firecrawl" | "ddg"`
field so the downstream consumer can attribute coverage.

**Fallback rule:** when `--fallback` is set and the dedup'd primary union
has fewer than 3 unique URLs, the script invokes
`duckduckgo_search.py` as a subprocess and appends the tagged results.

**Search trail:** one line per layer is appended to
`share/notes/01_research_<task>_search-trail.md` in the form
`layer=exa|firecrawl|ddg results=N query="..."`. The trail is the audit
record of which layer produced which results.

**Importable for tests:**
```python
from parallel_search import parallel_search
results = parallel_search(query, max_results=10, fallback=True,
                          exa_fn=..., firecrawl_fn=..., ddg_fn=...)
```

**Exit codes:** 0 = JSON written.

**Stdlib-only.** No new dependencies. Forces UTF-8 stdio at module load
before any argparse construction or output (WARN #15 / #22 inheritance).

---

## dedup_results.py (P9)

URL canonicalization + dedup for multi-source search results. Each
result is rewritten to its canonical URL form, then duplicates are
collapsed to the first occurrence. Source tags (`source: "exa" |
"firecrawl" | "ddg"`) are preserved through the round-trip.

**Usage:**
```sh
python dedup_results.py results.json   # file input
python dedup_results.py -              # read from stdin
```

**Output:** JSON list `[{"url", "title", "snippet", "source"}, ...]` to stdout.

**Importable as a library:**
```python
from dedup_results import canonicalize, dedup
canon = canonicalize("HTTPS://Example.COM/Article?utm_source=foo")
# -> "https://example.com/Article"
unique = dedup(results_list)
```

**Canonicalization rules (verbatim from plan §P9):**
- lowercase scheme + host
- strip `utm_*` query parameters (`utm_source`, `utm_medium`,
  `utm_campaign`, `utm_term`, `utm_content`, `utm_id`)
- normalize trailing slash on the path (collapse `/path/` -> `/path`;
  the root `/` is preserved for forward compatibility)
- preserve everything else verbatim (other query params, fragment)

**Dedup:** by canonical URL; first occurrence wins.

**Exit codes:** 0 = JSON written, 2 = bad JSON or input is not a list.

**Stdlib-only.** No new dependencies. Forces UTF-8 stdio at module load
before any argparse construction or output (WARN #15 / #22 inheritance).

---

## check-search-keys.sh (P9)

Bash helper that prints masked status of search-provider API keys and
exits non-zero when a required key is missing. Sources `.env.local`
silently (walks up from the script's directory until it finds one).

**Usage:**
```sh
bash book-kit/bin/check-search-keys.sh
```

**Output:**
```
env source: /path/to/.env.local
FIRECRAWL_API_KEY: set (last 4: 4fa46)
EXA_API_KEY: missing (last 4: —) [optional]
```

**Masking rule (WARN #14 inheritance):** the script NEVER echoes the
full key. When set, only the last 4 characters are printed; when
missing, the script prints `—` (em-dash).

**Required vs optional:**
- `FIRECRAWL_API_KEY` - required. Exit code 1 if missing or empty.
- `EXA_API_KEY` - optional (Exa is OAuth-wired; the key is an override
  only). Missing does not affect the exit code.

**Exit codes:** 0 = all required keys set; 1 = at least one required
key is missing.

**Stdlib-only** (bash + `printf` + `tail`). No new dependencies.

---

## render_mermaid.py (P11)

Pre-PDF figure renderer. Scans `<book>/chapters/*.md` for fenced `mermaid`
blocks, renders each one to a PNG via `mmdc`, and writes a mirrored copy of
every chapter under `chapters-rendered/` with each block replaced by an
`![caption](figures/....png)` image link. **The source chapters are never
mutated.** Wired into the orchestrator's Phase 6 as a pre-PDF step (see
`agents_manager/book-gen-orchestrator/SKILL.md`).

**External dependency (required):**
```sh
npm install -g @mermaid-js/mermaid-cli
```

**Usage:**
```sh
python render_mermaid.py --book books/<slug>/ [--slug <slug>]
                         [--figures-dir figures] [--out chapters-rendered]
                         [--manifest figures/mermaid-manifest.json]
                         [--chapter ch-NN.md]
```

**Flags:**
| Flag | Default | Behavior |
|---|---|---|
| `--book` | (required) | Book root; must contain a `chapters/` directory. |
| `--slug` | book root dir name | Prefix for generated figure filenames. |
| `--figures-dir` | `figures` | Where `.mmd` sources and `.png` renders land. Resolved under `--book`. |
| `--out` | `chapters-rendered` | Mirrored chapter directory. Resolved under `--book`. |
| `--manifest` | `figures/mermaid-manifest.json` | Manifest path. Resolved under `--book`. |
| `--chapter` | all `*.md` | Render a single chapter file name instead of the whole book. |

**Per-block artifacts:** `figures/<slug>-<ch-NN>-mermaid-<idx>.mmd` (block
source) and `figures/<slug>-<ch-NN>-mermaid-<idx>.png` (render, produced with
`-b transparent`).

**Manifest:** a JSON list of `{chapter, index, source_hash, png_path}`, sorted
by `(chapter, index)`. `source_hash` is the sha256 of the block source, so an
unchanged book re-renders to a byte-identical manifest.

**Caption resolution (first match wins):**
1. A `%% caption: <text>` directive on any line inside the mermaid block.
2. The nearest preceding markdown heading in the chapter.
3. `Figure <idx>`.

**Path validation (P4 #14 / P6 inheritance):** `--figures-dir`, `--out` and
`--manifest` are all resolved relative to `--book`. Any value containing a
`..` component, or any absolute path that does not resolve under the book
root, is refused with exit 2 before a single byte is written.

**Subprocess contract:** `mmdc` is invoked array-form as
`["mmdc", "-i", <mmd>, "-o", <png>, "-b", "transparent"]` with `check=True,
capture_output=True`. Never `shell=True`. A non-zero `mmdc` exit surfaces the
captured stderr in the error message.

**Missing `mmdc` behavior:** resolved via `shutil.which("mmdc")` at CLI entry.
A warning always goes to stderr with the install hint. Then:
- at least one mermaid block found -> exit 3, nothing written;
- no mermaid blocks found -> empty manifest written, exit 0 (a book with no
  diagrams must not break the pre-PDF pipeline).

**Malformed input:** an opening ` ```mermaid ` fence with no matching close
raises a handled error (exit 2). All chapters are parsed before any write, so
one malformed block leaves the figures and mirror directories untouched rather
than half-written.

**Exit codes:** 0 = rendered (or nothing to render), 2 = input error (missing
book root, no `chapters/`, malformed block, path outside book root, `mmdc`
render failure), 3 = `mmdc` required but not installed.

**Stdlib-only** on the Python side. No new Python dependencies. Forces UTF-8
stdio at module load before any argparse construction or output (WARN #15 /
#22 inheritance).
