# Scripts — flag reference

All 21 scripts + 2 lib files live in `book-kit/book_workflow/scripts/`
and `book-kit/book_workflow/lib/`. They're stdlib-only, idempotent, and
ship with `--self-check` plus 321 pytest tests across 33 test files
(`cd book-kit && py -m pytest tests/`). v1.3.0 added 13 new scripts +
2 new lib files for the book2media (Phase 9) lane.

---

## media_manifest.py

Validates and generates `books/<slug>/media-locale-manifest.json` (Phase 9 of the book-gen pipeline). The manifest is the per-book registry of media products (audiobook M4B, video-horizontal-m1, video-vertical-trailer, video-vertical-reel) per locale. This is the script am-assets invokes at Phase 1 dispatch (book2media-orchestrator) and the script `book_check.py` may invoke as part of the Phase 9 gate once the media-manifest HARD-gate is wired in.

**Invocation shape (canonical):**

The script runs as a direct file (NOT a Python module - `book-kit/` does not ship `__init__.py`, so `book_workflow.scripts.media_manifest` is not importable). On Windows use `py -3`; on Unix use `python3`.

**Usage:**

```sh
# Validate a manifest against the JSON Schema
py -3 "<repo-root>/book-kit/book_workflow/scripts/media_manifest.py" validate <manifest-path>

# Generate a stub manifest from a book's chapters + global providers.yaml
py -3 "<repo-root>/book-kit/book_workflow/scripts/media_manifest.py" generate \
    --book <slug-dir> \
    --providers providers.yaml \
    --out media-locale-manifest.json \
    --source-locale en
```

**Subcommands:**

| Subcommand | Purpose | Required flags | Optional flags |
|---|---|---|---|
| `validate` | schema-checks the manifest against the JSON Schema embedded in `book-kit/book_workflow/scripts/media_manifest.py` at L96-L145 (no standalone `.json` file) | `<manifest-path>` (positional) | -- |
| `generate` | builds a stub manifest from the book's chapters, the global `providers.yaml`, and an optional `--source-locale` default | `--book`, `--providers`, `--out` | `--source-locale` (default: `en`) |

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | success (validate or generate) |
| 2 | input error (schema/field error, file not found, path escapes book root) |
| 3 | missing dependency (`jsonschema` package absent) |
| 4 | providers.yaml malformed |

**Behavior on schema error:**

The validate subcommand emits a JSON-path line on schema error pointing at the offending field, e.g.:

```
products.0.voice: '' is not one of ['af_heart', 'bf_emma', ...]
```

The exit code is 2 in this case. The script does NOT mutate the manifest -- validation is read-only.

**Three-tier provider resolution (enforced):**

The validator enforces the resolution rule (per-book manifest wins, `providers.yaml` next, built-in defaults last) and rejects empty-string `voice: ""` in the per-book manifest (use `skip: true` to drop a product, never an empty voice string).

**See also:** `book-kit/docs/TOOLKIT.md` `### Media manifest` section, `agents_manager/book2media-orchestrator/SKILL.md` Phase 1, `agents_manager/assets/SKILL.md` `## Media-manifest lane (book2media Phase 9)`.

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
                            [--lang <ar|en>] [--check-imports]
```

**Flags:**
| Flag | Default | Purpose |
|---|---|---|
| `<chapter>` (positional) | — | Chapter markdown to check (e.g. `chapters/ch-03.md`) |
| `--config PATH` | (none) | Path to `style-guide.md` — adds frontmatter overrides for `Beat window:`, `Forbidden patterns:` (CSV), `Countdown tokens:` (CSV). Falls back to script defaults (600-750 window, no forbidden patterns, `["بقي", "لم يبق"]` countdown tokens). |
| `--json` | false | Emit `{"chapter": "ch-NN", "checks": [{name, status, evidence}]}` to stdout instead of writing the markdown report. |
| `--task ID` | `unknown` | Task id used in the markdown report's filename + metadata header. |
| `--report-dir DIR` | `reports` | Directory prefix; markdown report is written to `<DIR>/<task-id>/check_chapter_<chapter>.md`. |
| `--lang <ar\|en>` | (none) | Append a `arabic_grammar` / `english_grammar` row via LanguageTool MCP. See `### check_chapter.py --lang` below. |
| `--check-imports` | false | Append a `check_imports` row that walks Python fenced code blocks for `from X import Y` and verifies each `X` is pinned in `<book>/chapters/code/ch-NN/uv.lock`. See `### check_chapter.py --check-imports` below. |

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

### check_chapter.py --check-imports

- Flag: `--check-imports`
- Behavior: walks every Python fenced code block in the chapter for
  `from X import Y` lines and verifies the top-level package `X` is
  pinned in `<book>/chapters/code/ch-NN/uv.lock`.
- Output: adds a `check_imports` row to the JSON / markdown report.
- Requires: `pin_deps.py` (P14) to have run first so `uv.lock` exists.

The rule is **additive and opt-in** -- without `--check-imports` the
script behaves exactly as before (8 rows). When the flag is set:

| Situation | Row status |
|---|---|
| No Python imports in the chapter's code listings | `PASS` ("no Python imports in code listings") |
| `uv.lock` missing for `ch-NN` (pin_deps.py not yet run) | `PASS` with skip evidence (the rule never turns an unpinned chapter into a `FAIL`) |
| Every imported package appears in `uv.lock` | `PASS` ("all N import(s) verified against uv.lock") |
| At least one imported package is missing from `uv.lock` | `FAIL` (evidence lists the missing names, up to 8) |

Package names are matched case-insensitively (PyPI canonical casing).
Top-level segments only -- `from package.sub.module import x` matches
`package`, not `package.sub.module`. Dunder names like `__future__` are
ignored. The chapter number is read from the filename (`ch-NN.md`), so
chapter files outside that pattern (`introduction.md`, `preface.md`,
`app-*.md`) skip the rule with PASS evidence.

The rule looks up `<book>` by walking up from the chapter file: when
the chapter is at `<book>/chapters/ch-NN.md`, `<book>` is the parent of
`chapters/`. The chapter number drives the lock path
(`<book>/chapters/code/ch-NN/uv.lock`); the `chapters/code/` segment is
hard-coded (it matches the `pin_deps.py` default).

```sh
# Per-chapter gate with the check_imports row appended
python check_chapter.py chapters/ch-07.md --check-imports --json \
    | jq '.checks[] | select(.name=="check_imports")'
```

---

## pin_deps.py (P14)

Per-chapter-code dependency pinner. Walks `<book>/chapters/code/ch-NN/`
looking for `requirements.txt` or `pyproject.toml`, runs
`uv pip compile <input> -o <output>/uv.lock` (uv 0.7+), copies the
generated `uv.lock` next to the input, and emits
`<book>/chapters/code/CH-DEP-STATUS.md` with a per-chapter row
`{chapter, packages, lock_status}`. Designed to run before
`check_chapter.py --check-imports` so the lock file the check consults
is already on disk.

**External dependency (required):**
```sh
pip install uv
```

**Usage:**
```sh
python pin_deps.py --book books/<slug>/ [--code-dir chapters/code]
```

**Flags:**
| Flag | Default | Behavior |
|---|---|---|
| `--book` | (required) | Book root; the `--code-dir` is resolved relative to this. |
| `--code-dir` | `chapters/code` | Code directory under the book root. Refuses any value with a `..` component or that escapes `--book` (P4 #14 / P6 inheritance). |

**Input preference per chapter:** when both `pyproject.toml` and
`requirements.txt` exist in the same chapter dir, `pyproject.toml` wins
(more expressive; matches the project's own metadata conventions).
Neither file present -> the chapter gets `lock_status: missing_input` and
the script moves on.

**Subprocess contract:** `uv pip compile` is invoked array-form as
`["uv", "pip", "compile", <input>, "-o", <output>, "--quiet"]` with
`capture_output=True, text=True, timeout=120`. Never `shell=True`. A
non-zero exit surfaces the captured stderr in the status row evidence
(truncated to 500 chars).

**uv missing:** when `uv` is not on PATH, every chapter with a dep file
gets `lock_status: uv_missing` (the script never crashes; the surfaced
state is the missing binary). stderr prints one line per chapter with
the install hint.

**Lock format:** `uv pip compile` 0.7.x writes `uv.lock` in
requirements.txt-style (`name==version` lines). The script counts
those lines for the `packages` column; the count includes transitive
deps (e.g. `requests` pulls in `urllib3`, `certifi`, `idna`,
`charset-normalizer`).

**Status table format:**
```
| Chapter | Packages | Lock status |
| --- | --- | --- |
| ch-07 | 12 | pinned |
| ch-09 | 0 | uv_missing |
```

When `chapters/code/` is empty or absent, the file is still written
with a single placeholder row (`| -- | -- | -- |`) so the file is
non-empty and re-runs are byte-stable.

**Exit codes:** 0 = status file written, 2 = input error (book root
missing, `--code-dir` escapes `--book`).

**Forces UTF-8 stdio** at module load before any argparse construction
or output (WARN #15 / #22 inheritance).

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
`ledger.md`, plus the latest `04_review_*.md`, and renders a 6-field
gate summary (`Word count`, `Book-check`, `Reviewer`, `Reviewer invocations`,
`Frozen lines touched`, `Open questions`) into `share/reports/<task>/02_gate_ch-NN_<task>.md`.
The `Reviewer invocations` field (P17) records how many times the
book-reviewer sub-agent was invoked for the chapter (1 by default; N when
the orchestrator splits the chapter into chunks or runs the fallback ladder).
Wired into the orchestrator's Phase 7 (see `agents_manager/book-gen-orchestrator/SKILL.md`).

**Usage:**
```sh
python gate_summary.py --book books/<slug>/ --chapter ch-NN \
                       --review share/reports/04_review_<task>_P<N>.md
                       [--task T-YYYY-MM-DD-NNN] [--reports-dir <path>]
                       [--out <path-under-book>] [--loop N]
                       [--reviewer-invocations N] [--window LO-HI]
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

---

## visual_qa.py (P13)

Post-PDF page diagnostics for a rendered book. Walks every page with PyMuPDF,
saves a PNG of each page at dpi=150, counts widow/orphan candidates from the
text layout, and emits a page-number table of marker-string matches (e.g.
chapter titles). Wired into the orchestrator's Phase 7 as the post-PDF check
that runs after `md2pdf.py --book` finishes (see
`agents_manager/book-gen-orchestrator/SKILL.md`).

**External dependency:**
```sh
pip install pymupdf
```
The script imports the package as `pymupdf as fitz` so it works on
PyMuPDF >= 1.28 where the top-level `fitz` module is deprecated. The alias
covers older releases too because both names expose the same API surface.

**Usage:**
```sh
python visual_qa.py <book.pdf> [--markers FILE]
                     [--out PATH] [--figures-dir DIR] [--slug NAME]
```

**Flags:**
| Flag | Default | Behavior |
|---|---|---|
| `<pdf>` (positional, required) | — | Rendered book PDF to scan. |
| `--markers` | (none) | UTF-8 file with one marker per line (chapter titles). Blank lines and `#` comments are ignored. When omitted, the Markers column is `--` for every page. |
| `--out` | `<pdf-parent>/figures/visual-qa.md` | Output markdown path. Resolved under the PDF parent directory; refuses paths with `..` or that escape the parent (P4 #14 / P6 inheritance). |
| `--figures-dir` | `<pdf-parent>/figures` | Where the page PNGs land. Same path-under-parent enforcement as `--out`. |
| `--slug` | `<pdf-stem>` | Prefix for rendered PNG filenames. |

**Per-page artifacts:** `<figures-dir>/<slug>-page-NN.png` (dpi=150, NN
zero-padded so the directory sorts the same as the PDF page order).

**Marker search:** `page.search_for(marker)` is run per page; the Markers
column lists every marker that produced at least one hit, comma-separated.
The Chapter column uses the first matching marker as the chapter label
(`cover` for page 1 with no matches; `--` for any other unmatched page).

**Widow/orphan heuristic (page-level, not typesetting-perfect):**
- **widow** — last line of a text block in the top 20 percent of the page
  whose width is strictly less than one third of the page width.
- **orphan** — first line of a text block in the bottom 20 percent of the
  page.

A future P13.x can swap in a paragraph-reconstruction algorithm when the
project needs higher fidelity; today these flags catch the gross cases that
are easy to miss in a final read-through.

**Emitted markdown:**
```
| Page | Chapter | Markers | Widows | Orphans |
| --- | --- | --- | --- | --- |
| 1 | cover | -- | 0 | 0 |
| 2 | ch-01 | "Chapter 1" | 0 | 0 |
| 5 | ch-02 | "Chapter 2" | 1 | 0 |
```
Missing-data cells use ASCII `--` (never U+2014 em-dash per the P13 gate).

**Exit codes:** 0 = diagnostics written, 2 = input error (PDF not found,
malformed `--markers`, `--out` or `--figures-dir` outside the PDF parent
directory, PyMuPDF cannot open the PDF).

**Forces UTF-8 stdio** at module load before any argparse construction or
output (WARN #15 / #22 inheritance).

---

## voices.py

TTS voice registry with three-tier resolution (per-book manifest > global `providers.yaml` > built-in defaults). Used by `media_tts.py` and any Phase 2 dispatch that needs a voice for a given `(book, locale, tts_provider)` triple.

**Invocation shape:** import as a module or use `py -3 voices.py <cmd>` for ad-hoc inspection. The script ships an `--inspect` subcommand that prints the full registry and exits 0.

**Public API:**

| Function | Returns | Notes |
|---|---|---|
| `resolve_voice(book, locale, tts_provider)` | `str` (voice id) | Three-tier lookup. Raises `MediaPipelineError(voice_unavailable, exit=2)` if no voice found in any tier. |
| `list_voices(locale, tts_provider)` | `list[str]` | All voices available for the locale/provider. Empty list if provider unknown. |
| `VOICE_REGISTRY` | `dict` | Built-in defaults; read-only. Kokoro: `af_heart`, `am_michael`, `bf_emma`, `bm_george`, ...; edge-tts: `en-US-JennyNeural`, `en-US-GuyNeural`, `ar-SA-HamedNeural`, `ar-EG-SalmaNeural`, ... |

**Exit codes (when run as a script):** 0 = success, 2 = unknown provider/locale.

**Three-tier resolution (enforced):**
1. Per-book `media-locale-manifest.json` `products[].voice` field (authoritative).
2. Global `providers.yaml` per-locale `voice` default.
3. Built-in `VOICE_REGISTRY` (last-resort defaults).

**See also:** `book-kit/docs/TOOLKIT.md` `### voices.py` section, `media_tts.py` for the synthesis path.

---

## media_tts.py

H2-driven chunker + per-locale TTS dispatcher. Splits a chapter into H2-aligned chunks and synthesizes one MP3 per chunk via Kokoro (en default) or edge-tts (ar default). Emits a TTS manifest consumed by `transcribe_chapter.py`.

**Invocation shape (canonical):**

```sh
py -3 "<repo-root>/book-kit/book_workflow/scripts/media_tts.py" \
    --book <slug-dir> \
    --chapter ch-NN \
    --locale en|ar \
    --out <path-to-mp3> \
    [--tts-provider kokoro|edge-tts]
```

**Flags:**

| Flag | Required | Purpose |
|---|---|---|
| `--book` | yes | Book root (e.g., `books/<slug>`) |
| `--chapter` | yes | Chapter id (e.g., `ch-01`) |
| `--locale` | yes | `en` or `ar` (manifest is per-locale) |
| `--out` | yes | Output MP3 path (must resolve under book root) |
| `--tts-provider` | no | Override the manifest's provider (otherwise resolved from `voices.resolve_voice`) |

**Behavior:**
- Chunker: H2-aligned, ~200-400 tokens per chunk. Falls back to paragraph splitting if a chunk is still too long, then to word-window splitting as last resort.
- Re-runs are idempotent: same chapter + same manifest + same voice = byte-identical output (verified in v1.3.0 smoke).
- H2-driven chunks matching `gate_summary.py` P17 chunker for symmetry.

**Exit codes:** 0 = success, 2 = input error, 3 = missing dep (kokoro/edge-tts), 4 = TTS provider failed.

**See also:** `book-kit/docs/TOOLKIT.md` `### media_tts.py` section, `voices.py` for voice resolution.

---

## check_whisper_deps.py

Verifies `faster-whisper` is installed; reports the available ASR models and the Hugging Face cache directory. Exits 3 with an actionable install hint if the package is missing.

**Invocation shape:**

```sh
py -3 "<repo-root>/book-kit/book_workflow/scripts/check_whisper_deps.py" \
    [--language en|ar] \
    [--self-check] \
    [--cache-dir <path>] \
    [--device cuda|cpu]
```

**Flags:**

| Flag | Required | Purpose |
|---|---|---|
| `--language` | no | Hint which model to prefer (en=small, ar=large-v3). Default: auto |
| `--self-check` | no | Print version + device + cache-dir; exit 0 |
| `--cache-dir` | no | Override HF cache dir (default: `~/.cache/huggingface` -- known leak, see Deferred WARN W1) |
| `--device` | no | `cuda` or `cpu` (default: auto-detect) |

**Exit codes:** 0 = deps OK, 3 = missing dep (emits install hint via `lib/errors.py`).

**See also:** `book-kit/docs/TOOLKIT.md` `### check_whisper_deps.py` section.

---

## transcribe_chapter.py

Runs faster-whisper on a chapter's MP3 with `word_timestamps=True`. Writes a JSON with per-word `{word, start, end, probability}` entries consumed by `align_srt.py`.

**Invocation shape:**

```sh
py -3 "<repo-root>/book-kit/book_workflow/scripts/transcribe_chapter.py" \
    --book <slug-dir> \
    --chapter ch-NN \
    --locale en|ar \
    --out <words-json-path> \
    --mp3 <audio-path> \
    [--dry-run] \
    [--from <words-json-path>] \
    [--only <N>]
```

**Flags:**

| Flag | Required | Purpose |
|---|---|---|
| `--book` | yes | Book root |
| `--chapter` | yes | Chapter id |
| `--locale` | yes | `en` or `ar` |
| `--out` | yes | Output words JSON path (must resolve under book root) |
| `--mp3` | yes | Input audio MP3 path |
| `--dry-run` | no | Print the plan without invoking the model |
| `--from` | no | Resume from a previous JSON (skip already-transcribed segments) |
| `--only` | no | Only transcribe the first N segments |

**Model selection** (configurable via `MODEL_FOR_LOCALE` in source): `ar -> large-v3`, `en -> small`.

**Exit codes:** 0 = success, 2 = input error, 3 = missing dep (faster-whisper), 4 = runtime error.

**See also:** `book-kit/docs/TOOLKIT.md` `### transcribe_chapter.py` section, `align_srt.py` for downstream alignment.

---

## align_srt.py

Aligns faster-whisper word timestamps against the canonical chapter text via `difflib.SequenceMatcher` at chunk granularity. Emits an SRT with one cue per matched segment.

**Invocation shape:**

```sh
py -3 "<repo-root>/book-kit/book_workflow/scripts/align_srt.py" \
    --book <slug-dir> \
    --chapter ch-NN \
    --locale en|ar \
    --words-json <words-json-path> \
    --out <srt-path> \
    [--drift-floor <float>]
```

**Flags:**

| Flag | Required | Purpose |
|---|---|---|
| `--book` | yes | Book root |
| `--chapter` | yes | Chapter id |
| `--locale` | yes | `en` or `ar` |
| `--words-json` | yes | Input words JSON (from `transcribe_chapter.py`) |
| `--out` | yes | Output SRT path |
| `--drift-floor` | no | Minimum match ratio (default: 0.70); below this, raises exit 4 |

**Arabic normalization (`normalize_arabic`):** strips diacritics (U+0610-U+061A, U+064B-U+065F, U+0670, U+06D6-U+06DC, U+06DF-U+06E4, U+06E7-U+06E8, U+06EA-U+06ED) and normalizes alef/yaa/tatweel. Genuine-Arabic chapters align cleanly through tashkil/alef-form variants.

**Latin detection:** if the chapter text has > 30% Latin characters and the locale is non-English, the script drops the drift floor to 0.0 and emits a translation-pending warning. SRT is still emitted (fragmentary cues); full fix is to translate the chapter before re-aligning.

**Exit codes:** 0 = aligned, 2 = input error, 4 = drift above floor (or translation-pending case).

**See also:** `book-kit/docs/TOOLKIT.md` `### align_srt.py` section, `srt_to_ass.py` for downstream ASS conversion.

---

## srt_to_ass.py

Converts an SRT to an ASS subtitle file using `pysubs2`. For Arabic: forces `WrapStyle=2` + `\an2` alignment + Amiri font. For English: default sans-serif. The ASS file is what the video assemblers consume via libass `ass=...:shaping=complex`.

**Invocation shape:**

```sh
py -3 "<repo-root>/book-kit/book_workflow/scripts/srt_to_ass.py" \
    --in <srt-path> \
    --out <ass-path> \
    --locale en|ar \
    [--font-size <int>]
```

**Flags:**

| Flag | Required | Purpose |
|---|---|---|
| `--in` | yes | Input SRT path |
| `--out` | yes | Output ASS path |
| `--locale` | yes | Source locale: `en` or `ar` (chooses WrapStyle + font) |
| `--font-size` | no | Subtitle font size in points (default: 24) |

**Exit codes:** 0 = success, 2 = input error, 3 = missing Amiri font (emits install hint via `lib/errors.py`).

**Prerequisite:** Amiri installed via `install_amiri.py`; `pysubs2==1.8.1` in venv.

**See also:** `book-kit/docs/TOOLKIT.md` `### srt_to_ass.py` section.

---

## install_amiri.py

Downloads the Amiri font family (Regular, Italic, Bold, BoldItalic, Quran) from the official GitHub release. Idempotent: skips download if `EXPECTED_MIN_FONTS=5` are already at `--target-dir`.

**Invocation shape:**

```sh
py -3 "<repo-root>/book-kit/book_workflow/scripts/install_amiri.py" \
    [--target-dir <font-dir>] \
    [--verify] \
    [--force]
```

**Flags:**

| Flag | Required | Purpose |
|---|---|---|
| `--target-dir` | no | Install dir (default: `%LOCALAPPDATA%\fonts` on Windows, `~/.fonts` on Unix) |
| `--verify` | no | Check existing install; exit 0 if >= 5 fonts present |
| `--force` | no | Re-download even if installed |

**Exit codes:** 0 = success (or verified), 2 = input error, 3 = download/extract failed (emits hint).

**Note:** No SHA256SUMS verification on the zip (Deferred WARN W3 — fix in a v1.3.1 polish dispatch).

**See also:** `book-kit/docs/TOOLKIT.md` `### install_amiri.py` section.

---

## assemble_audiobook.py

Concatenates per-chapter MP3s into a single M4B audiobook with chapter markers, ID3 metadata, embedded cover PNG, and two-pass loudnorm (I=-19 LUFS, TP=-2 dBTP, LRA=11).

**Invocation shape:**

```sh
py -3 "<repo-root>/book-kit/book_workflow/scripts/assemble_audiobook.py" \
    --book <slug-dir> \
    --out <m4b-path> \
    --locale en|ar \
    [--cover <png-path>] \
    [--no-loudnorm] \
    [--self-check]
```

**Flags:**

| Flag | Required | Purpose |
|---|---|---|
| `--book` | yes | Book root |
| `--out` | yes | Output M4B path (must resolve under book root) |
| `--locale` | yes | `en` or `ar` (matches synthesized voice manifest) |
| `--cover` | no | Cover PNG (overrides fallback ladder) |
| `--no-loudnorm` | no | Skip both loudnorm passes |
| `--self-check` | no | Assert chapter count matches input |

**Cover fallback ladder:** `figures/cover.png` -> `chapters-rendered/*.png` (first match). If all tiers missing, raises exit 2.

**Voice policy:** if the manifest voice differs from the synthesized voice, raises `MediaPipelineError(voice_unavailable, exit=2)`. (This is a sanity check; the synthesis should have used the same voice.)

**Language tag:** uses ISO 639-2 (`en -> eng`, `ar -> ara`) since ffmpeg's MP4 `mdhd` atom only accepts 3-char codes.

**Exit codes:** 0 = success, 2 = input error, 3 = missing dep (ffmpeg), 4 = self-check fail or ffmpeg runtime error.

**See also:** `book-kit/docs/TOOLKIT.md` `### assemble_audiobook.py` section.

---

## ffmpeg_zoompan.py

Shared Ken Burns library. Library only -- no CLI. Exports `compute_zoompan_filter`, `supersample_zoompan_filterchain`, and `ZOOM_DEFAULT_30S_NATURAL`.

**Public API:**

| Function | Returns | Notes |
|---|---|---|
| `compute_zoompan_filter(width, height, audio_duration, scale_mult=4)` | `3-tuple[str, str, str]` | Returns `(scale_in, zoompan, scale_out)` -- the three filter segments to be joined with commas for ffmpeg's `-vf` flag. scale_in is `scale={W*scale_mult}:-1`, scale_out is `scale={W}:{H}`, zoompan is the per-frame expression. |
| `supersample_zoompan_filterchain(target_w, target_h, dur_s, scale_mult=4)` | `3-tuple[str, str, str]` | Same shape as above, with defaults tuned for the assembly pipeline. Callers join with commas for the final `-filter_complex` argv. |
| `ZOOM_DEFAULT_30S_NATURAL` | `tuple` | `(1.0, 1.08, "0", "ih/2-ih/(2*zoom)")` for 1.0x -> 1.08x zoom over 30s |

**Why 4x supersample:** the canonical Ken Burns trick to kill zoompan judder. Renders at 8000x4500 then downsamples to 1920x1080. Documented escape hatches (`scale_mult=2` for ~4x faster, NVENC for ~5-10x faster) are plumbing-level constants -- not yet CLI-reachable (Deferred WARN F5 from Phase 5 review).

**Imported by:** `assemble_video_horizontal.py`, `assemble_video_trailer.py`. Never invoked directly.

**See also:** `book-kit/docs/TOOLKIT.md` `### ffmpeg_zoompan.py` section.

---

## assemble_video_horizontal.py

Renders a 1920x1080 Mode-1 video from a single static cover + Ken Burns zoompan + audio + optional burned subs + optional BGM. Per-chapter loop or whole-book loop via `--all`.

**Invocation shape:**

```sh
py -3 "<repo-root>/book-kit/book_workflow/scripts/assemble_video_horizontal.py" \
    --book <slug-dir> \
    --chapter ch-NN | --all \
    --out <mp4-path> \
    --audio <mp3-path> \
    [--cover <png-path>] \
    [--burn-subs --subs <ass-path>] \
    [--bgm <audio-path>]
```

**Flags:**

| Flag | Required | Purpose |
|---|---|---|
| `--book` | yes | Book root |
| `--chapter` or `--all` | yes (one) | One chapter id, or `--all` for whole book |
| `--out` | yes | Output MP4 path |
| `--audio` | yes | Per-chapter MP3 (single chapter) or chapter list (whole book) |
| `--cover` | no | Cover image (overrides fallback ladder) |
| `--burn-subs` | no | Burn the ASS subtitle file (requires `--subs`) |
| `--subs` | with `--burn-subs` | ASS subtitle path |
| `--bgm` | no | Background-music audio path |

**Behavior:**
- Filter chain: `supersample_zoompan_filterchain(1920, 1080, audio_dur)` + optional `ass=...:shaping=complex` + optional `amix=...[v]` + final `vignette=PI/4[v]`.
- Per-chapter loop emits one MP4 per chapter; whole-book loop emits a single concatenated MP4.
- Sidecar manifest at `<book>/figures/media-video-manifest.json` with `{chapters: [...], codec, width, height}`.

**Performance:** ~11x realtime at 4x supersample (e.g., 60s clip = 11.2 min wall). Full 700s chapter = ~131 min estimated.

**Exit codes:** 0 = success, 2 = input error, 3 = missing dep (ffmpeg), 4 = ffmpeg runtime error.

**See also:** `book-kit/docs/TOOLKIT.md` `### assemble_video_horizontal.py` section.

---

## assemble_video_trailer.py

Builds a single 60-90s teaser from the whole book. Clip-selection pass picks the first ~12 chunks by 1500-char budget across all chapters, with proportional per-chapter audio windows. Otherwise mirrors `assemble_video_horizontal.py`.

**Invocation shape:** same as `assemble_video_horizontal.py` (without `--chapter`; whole-book only).

**Behavior:**
- Clip selection: budget = 1500 chars per chunk; pick the first chunks across chapters that fit the 60-90s target.
- Audio windows: proportional per-chapter allocation; concatenated with crossfade.
- Output: single 1920x1080 MP4 at the requested path.

**Performance:** ~11x realtime for 60-90s; ~10-15 min wall per trailer.

**Exit codes:** 0 = success, 2 = input error, 3 = missing dep (ffmpeg), 4 = ffmpeg runtime error.

**See also:** `book-kit/docs/TOOLKIT.md` `### assemble_video_trailer.py` section.

---

## assemble_reel.py

Renders a 1080x1920 vertical reel and fans out to 3 platform-specific MP4s (YouTube Shorts, Instagram Reels, TikTok). Uses a two-step serial architecture: render shared base video to a temp file, then per-platform ffmpeg applies loudnorm + ASS alignment + vignette.

**Invocation shape:**

```sh
py -3 "<repo-root>/book-kit/book_workflow/scripts/assemble_reel.py" \
    --book <slug-dir> \
    --chapter ch-NN \
    --out <base-mp4-path> \
    --audio <mp3-path> \
    [--cover <png-path>] \
    [--burn-subs --subs <ass-path>] \
    [--bgm <audio-path>] \
    [--platforms yt,ig,tiktok]
```

**Flags:**

| Flag | Required | Purpose |
|---|---|---|
| `--book` | yes | Book root |
| `--chapter` | yes | Chapter id (single chapter per reel) |
| `--out` | yes | Base output MP4 (gets `-yt`, `-ig`, `-tiktok` suffixes) |
| `--audio` | yes | Per-chapter MP3 |
| `--cover` | no | Cover image (overrides fallback ladder) |
| `--burn-subs` | no | Burn the ASS subtitle file (requires `--subs`) |
| `--subs` | with `--burn-subs` | ASS subtitle path |
| `--bgm` | no | Background-music audio path |
| `--platforms` | no | Comma-separated platform list (allowed: `yt,ig,tiktok`; default: all three) |

**Per-platform loudnorm and caption positioning:**

| Platform | I (LUFS) | TP (dBTP) | ASS alignment | Position |
|---|---|---|---|---|
| YouTube Shorts | -14 | -1 | 2 | bottom-center |
| Instagram Reels | -16 | -1.5 | 2 | bottom-center |
| TikTok | -14 | -1 | 8 | top-center |

**Two-step serial architecture:**
1. Render shared base video to `<out>-base.mp4` (one ffmpeg invocation, no audio, no per-platform filter).
2. For each platform, run a small ffmpeg that reads the base video + audio and applies per-platform loudnorm + ASS alignment + vignette.

Peak memory bounded by ONE libx264 encoder at a time.

**Known limits:**
- 4:4:4 chroma replaced with 4:2:0 (`yuv420p`) for fan-out safety (Phase 5 Bug #3 fix).
- Per-platform loudnorm is single-pass (one render + per-platform apply). Two-pass is acceptable per plan and currently deferred.

**Exit codes:** 0 = success, 2 = input error, 3 = missing dep (ffmpeg), 4 = ffmpeg runtime error.

**See also:** `book-kit/docs/TOOLKIT.md` `### assemble_reel.py` section.

---

## lib/tts_events.py

TTS event-format helpers. Library only -- no CLI. Translates raw TTS event streams (WordBoundary, SentenceBoundary) into a uniform format consumable by downstream captioning.

**Public API:**

| Function | Returns | Notes |
|---|---|---|
| `TTSEventCollector` | class | Stateful collector for TTS event streams |
| `collect_sentence_offsets` (async) | `list[tuple]` | Collects sentence-level offsets from a TTS stream |
| `sentence_offsets_to_srt` | `str` | Converts offsets to SRT format |
| `get_provider_event_format(provider)` | `str` | Returns `'ms-windows'` for edge-tts, `'kokoro-v0.9'` for Kokoro |

**Imported by:** am-coder when wiring TTS event collectors into a TTS provider.

**Note:** HINTS in `lib/errors.py` are mutable dicts; freeze with `MappingProxyType` or document as const before exposing them as a public API (WARN from Phase 2b review; trivial fix in a v1.3.1 polish).

**See also:** `book-kit/docs/TOOLKIT.md` `### lib/tts_events.py` section.

---

## lib/errors.py

Actionable error hints. Library only -- no CLI. Defines `MediaPipelineError(Exception)` carrying `.hint` + `.exit_code`; `raise_actionable(error_kind, **ctx)` raises; `format_hint(error_kind, **ctx)` returns without raising.

**Public API:**

| Function | Returns | Notes |
|---|---|---|
| `MediaPipelineError` | exception class | Carries `.hint` (str) and `.exit_code` (int) |
| `raise_actionable(error_kind, **ctx)` | raises | Convenience wrapper that formats the hint and raises |
| `format_hint(error_kind, **ctx)` | `str` | Returns the formatted hint without raising |
| `HINTS` | `dict` | 6 keys: `missing_amiri_font`, `voice_unavailable`, `schema_invalid`, `audio_empty`, `comfyui_not_running`, `unsupported_locale` |

**HINTS dict (6 keys):**

| Key | Exit code | Default message |
|---|---|---|
| `missing_amiri_font` | 3 | "Amiri font not found. Run: install_amiri.py" |
| `voice_unavailable` | 4 | "Voice not registered for {locale} via {provider}" |
| `schema_invalid` | 2 | "Manifest schema invalid: {detail}" |
| `audio_empty` | 4 | "Audio file is empty or zero-duration" |
| `comfyui_not_running` | 3 | "ComfyUI server not reachable at 127.0.0.1:8188" |
| `unsupported_locale` | 2 | "Locale {locale} not supported by any TTS provider" |

**Imported by:** every Phase 2-4 script for uniform error reporting.

**See also:** `book-kit/docs/TOOLKIT.md` `### lib/errors.py` section.

