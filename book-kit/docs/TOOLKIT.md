# Book-Kit Toolkit Reference

> **Single source of truth for every script and template the kit ships.** When an agent (or master) needs to invoke a tool, find it here first. This document is the canonical registry; do not duplicate tool lists in agent SKILL.md files - point to this file instead.

## Conventions

- All paths are repo-root-relative. Run from the repo root.
- `python3` is the canonical interpreter. On Windows use `py -3`.
- ASCII-only on all newly written code (inherited rule from P1-P18 hardening decisions).
- UTF-8 stdio force is at module TOP of every script (before `argparse`).
- Path validation: every `--out` / `--book` / `--code-dir` / `--figures-dir` flag rejects paths outside its configured root with a clear error.

## How to use this file

1. Find your phase in the **Pipeline map** below.
2. Find the tool you need in the **Tool catalog** (sorted by phase).
3. Read the tool's own docstring + entry in `book-kit/docs/SCRIPTS.md` for the canonical CLI shape.
4. If the tool is new (added in T-2026-08-05-001), the plan section is in `share/notes/02_plan_T-2026-08-05-001_book-kit-roadmap.md`.

## Pipeline map (which tools run when)

```
Phase 0 (intake)        - (no scripts; master + intake.md)
Phase 1 (skeleton)      - (no scripts; am-planning + skeleton.md)
Phase 2 (research)      - duckduckgo_search, parallel_search, dedup_results (P9)
                         - book-kg indexer (P18; indexer.py)
Phase 3 (outline)       - (no scripts; am-planning + outline.md)
Phase 4 (style)         - (no scripts; am-design + style-guide.md)
Phase 5 (writing plan)  - (no scripts; master)
Phase 6 (writing)       - book_check.py        (P1 + P3 + P8; mandatory gate)
                         - check_chapter.py    (P2 + P5 + P10 + P14; per-beat prose enforcer)
                         - pin_deps.py         (P14; code listings)
                         - render_mermaid.py   (P11; pre-PDF figure render)
                         - render_ledger_check.py (P4; ledger.md autogen)
                         - book-kg indexer     (P18; re-run on chapter write)
                         - bash check-book-repo.sh (P15; beat-boundary tags)
Phase 7 (review)        - gate_summary.py     (P6 + P17; per-chapter gate artifact)
                         - book-kg query tools (P18; trace_path, motifs_in_chapter, contradicts, references)
                         - check_chapter.py --check-imports (P14)
Phase 8 (post-pipeline) - md2pdf.py --book    (P12; PDF build)
                         - visual_qa.py        (P13; post-PDF page diagnostics)
                         - index_reports.py    (P7; share/reports/INDEX.md)
Translation-mode only   - build_source_map.py (translation intake)
                         - split_source.py     (chunked-write protocol)
                         - fix_source_urls.py  (URL cleanup before source-map)
                         - extract_figures.py  (PDF figure extraction)
                         - poll_progress.py    (file-watcher dashboard)
                         - bilingual_smoke.py  (RTL/smoke test)
                         - build_exports.py    (RTL TOC + Arabic-Indic numbering)
                         - strip_publish_annotations.py (publish-time strip)
```

## Tool catalog

### Validation

#### `book_check.py` - mandatory book-wide gate (P1 + P3 + P8)

**Path:** `book-kit/book_workflow/scripts/book_check.py`

**Purpose:** Hard gate that runs on every chapter completion. Word count, frozen-line integrity, tashkeel ratio, source-ratio (translation mode), cross-chapter continuity (from `bible.md`), coin-arc tracking (from `style-guide.md`).

**Use when:** After every chapter write (Phase 6) and at every stage boundary.

**Exit codes:** 0 = pass, non-zero = fail with line numbers in evidence.

**Key flags:**
- `--book <dir>` - book root (required)
- `--json` - emit machine-readable output (consumed by `gate_summary.py` and `render_ledger_check.py`)
- `--task <id>` - for JSON-caching across runs (P9)

**Decision rule:** If exit != 0, master does NOT advance to next chapter or next phase. Surface failure to writer; loop on fix.

**See also:** `book-kit/docs/SCRIPTS.md` `## book_check.py` section.

---

#### `check_chapter.py` - per-beat prose enforcer (P2 + P5 + P10 + P14)

**Path:** `book-kit/book_workflow/scripts/check_chapter.py`

**Purpose:** 8 (now 9 with `--check-imports`) per-beat checks: word count, banned patterns, quote pair balance, dialogue on own line, closing hook, countdown rule, Arabic punctuation, sentence length, plus optional `--lang ar|en` grammar (P10, deferred - npm package unresolved) and `--check-imports` (P14, code listings).

**Use when:** After every beat write within a chapter, before saving as `drafted`.

**Key flags:**
- `--config <book-or-style-guide>` - points to a book root OR `style-guide.md` for `Rule applicability` table (P5)
- `--lang ar|en` - grammar check (deferred; degrades to WARN when MCP unreachable)
- `--check-imports` - verify code listings against `uv.lock` (P14; requires `pin_deps.py` to have run first)
- `--json` - emit machine-readable output

**See also:** `book-kit/docs/SCRIPTS.md` `## check_chapter.py` section.

---

#### `cross_ref.py` - cross-reference integrity (P3)

**Path:** `book-kit/book_workflow/scripts/cross_ref.py`

**Purpose:** Validates that every cross-reference in the book (`ch-NN` mentions, character name mentions) actually exists. Reports broken/resolved/total counts. Wired into `book_check.py` as one of its checks.

**Use when:** Runs as part of `book_check.py`; rarely called standalone.

---

### Book structure

#### `render_ledger_check.py` - ledger.md gate-checklist autogen (P4)

**Path:** `book-kit/book_workflow/scripts/render_ledger_check.py`

**Purpose:** Reads `check_chapter.py --json` + `book_check.py --json` output and replaces the `## Gate checklist` block in `<book>/ledger.md` in place. Idempotent (no duplicate rows on re-run).

**Use when:** After every chapter write (Phase 6 post-write hook).

**Key flags:**
- `--book <dir>` - book root (required)
- `--chapter ch-NN` - chapter ID (required)
- `--out <path>` - output ledger path (must resolve under book root)

**See also:** `book-kit/docs/SCRIPTS.md` `## render_ledger_check.py` section.

---

#### `gate_summary.py` - per-chapter gate artifact (P6 + P17)

**Path:** `book-kit/book_workflow/scripts/gate_summary.py`

**Purpose:** Reads chapter file + bible + check_chapter report + book_check.json + review report. Emits `share/reports/<task>/02_gate_ch-NN_<task>.md` with a 6-field canonical block (Word count, Book-check, Reviewer, Reviewer invocations, Frozen lines touched, Open questions) and a status line (APPROVED / FIX-LOOP-N / REJECTED).

**Use when:** Phase 7 pre-review (per chapter).

**Key flags:**
- `--book <dir>` - book root (required)
- `--chapter ch-NN` - chapter ID (required)
- `--review <path>` - review report path (optional; can be stub on first pass)
- `--task <id>` - task ID (required)
- `--reviewer-invocations N` - count of reviewer calls (P17; set by master after split + fallback)

**Exit codes:** 0 = APPROVED, 1 = FIX-LOOP-N or REJECTED, 2 = input error.

**See also:** `book-kit/docs/SCRIPTS.md` `## gate_summary.py` section.

---

#### `index_reports.py` - share/reports/INDEX.md auto-regen (P7)

**Path:** `book-kit/book_workflow/scripts/index_reports.py`

**Purpose:** Scans `share/reports/` for files matching `0X_*.md` where X in {0,1,2,3,4,5,6,7}. Groups by phase prefix; emits `share/reports/INDEX.md` with columns (Phase | File | Date | Status).

**Use when:** Phase 8 (post-pipeline) and after any new review/report artifact lands.

**Key flags:**
- `--reports-dir <dir>` - reports directory (default: `share/reports/`)
- `--out <path>` - output INDEX.md path (must resolve under reports-dir)
- `--regen` - regenerate (idempotent; same input = same output byte-stable)

**See also:** `book-kit/docs/SCRIPTS.md` `## index_reports.py` section.

---

### Research & language

#### `duckduckgo_search.py` + `parallel_search.py` + `dedup_results.py` - multi-source web research (P9)

**Paths:**
- `book-kit/book_workflow/scripts/duckduckgo_search.py` (thin Python wrapper around `html.duckduckgo.com/html/?q=...`)
- `book-kit/book_workflow/scripts/parallel_search.py` (CLI for parallel MCP tool calls; consumes pre-fetched JSON)
- `book-kit/book_workflow/scripts/dedup_results.py` (canonicalize URLs, dedupe by canonical form)

**Purpose:** Free-text web search via DuckDuckGo. No API key required. Used as fallback when Exa/Firecrawl MCPs are unavailable.

**Use when:** Phase 2 research when the master wants to add an MCP-free search option. The LLM (am-research) is responsible for calling Exa/Firecrawl MCPs in parallel and writing results to temp files; the Python scripts only post-process the JSON.

**Key env:** `FIRECRAWL_API_KEY` in `book-kit/.env.local` (gitignored; see `book-kit/.env.example`).

**See also:** `book-kit/docs/ARCHITECTURE.md` -Multi-source research MCPs (P9)- section.

---

#### `check_chapter.py --lang` - LanguageTool grammar check (P10, deferred)

**Path:** `book-kit/book_workflow/scripts/check_chapter.py --lang ar|en`

**Purpose:** Optional grammar check via LanguageTool MCP. Degrades to WARN when MCP unreachable (npm package `@goncalomb/languagetool-mcp` returns 404; closest alternative `@dpesch/languagetool-mcp-server` requires LanguageTool Pro API key). Safe-degradation is the design - never blocks a passing chapter.

**Status:** DEFERRED until upstream package resolves. MCP entry in `~/.config/opencode/opencode.json` ships with `enabled: false`. Re-enable is a single keystroke.

**See also:** `book-kit/docs/SCRIPTS.md` -check_chapter.py --lang- section.

---

### Rendering

#### `render_mermaid.py` - figure renderer (P11)

**Path:** `book-kit/book_workflow/scripts/render_mermaid.py`

**Purpose:** Scans `chapters/*.md` for `` ```mermaid ` blocks. For each block: writes to `figures/<slug>-ch-NN-mermaid-<idx>.mmd`, invokes `mmdc -i ... -o ... -b transparent` (mermaid-cli), replaces the block in `chapters-rendered/` mirror with `![<caption>](figures/...png)`. Emits `figures/mermaid-manifest.json` with `{chapter, index, source_hash, png_path}`.

**Use when:** Phase 6 pre-PDF step (after chapter gate, before PDF build).

**Prerequisite:** `npm install -g @mermaid-js/mermaid-cli` (not in this env at time of writing; document in script's runtime check).

**Behavior when `mmdc` absent:** exit 3 when blocks exist (raw fence must not reach PDF); exit 0 with empty manifest when no blocks.

**See also:** `book-kit/docs/SCRIPTS.md` `## render_mermaid.py (P11)` section.

---

#### `md2pdf.py --book` - full-book PDF build (P12)

**Path:** `book-kit/book_workflow/scripts/md2pdf.py`

**Purpose:** Extends the existing per-chapter PDF builder with a `--book` mode. Reads `<book>/toc.md` for chapter list; assembles cover (from `style-guide.md` cover_text) + preface + chapters + back-matter HTML; embeds `@page { @bottom-right { content: counter(page); } }` CSS; emits PDF with metadata (title, author, isbn, build-date). Paper size + fonts from `style-guide.md` frontmatter.

**Use when:** Phase 8 PDF build.

**Key flags:**
- `--book <dir>` - book root (required for book mode)
- `--html-only` - emit assembled HTML without invoking Chrome (useful for debugging)
- `--out <path>` - output PDF path
- `--title`, `--author`, `--isbn`, `--build-date` - PDF metadata
- `--paper-size`, `--fonts` - from style-guide frontmatter

**Behavior when Chrome absent:** exit 3 if `--book` is requested; exit 0 with `--html-only`. Chrome at `C:\Program Files\Google\Chrome\Application\chrome.exe` is the canonical path on Windows; `where.exe` does not see Program Files - use `Test-Path` instead.

**See also:** `book-kit/docs/SCRIPTS.md` `## md2pdf.py` + `### Book mode (P12)` section.

---

#### `visual_qa.py` - post-PDF page diagnostics (P13)

**Path:** `book-kit/book_workflow/scripts/visual_qa.py`

**Purpose:** Renders each PDF page to PNG at 150 DPI. Detects widows (last line of para < 1/3 page width) and orphans (first line of para at page bottom). Searches for marker strings (chapter titles) and emits a page-number table. Writes `figures/visual-qa.md`.

**Use when:** Phase 8 post-PDF check (after `md2pdf.py --book`).

**Key flags:**
- `<book.pdf>` - input PDF (required)
- `--markers <file>` - chapter titles / section markers (one per line, `#` comments stripped)
- `--figures-dir <dir>` - output PNG directory
- `--out <path>` - output visual-qa.md path

**Prerequisite:** `pip install pymupdf` (or `pymupdf` already installed in env).

**See also:** `book-kit/docs/SCRIPTS.md` `## visual_qa.py (P13)` section.

---

### Build hygiene

#### `pin_deps.py` - code-listing dependency pinner (P14)

**Path:** `book-kit/book_workflow/scripts/pin_deps.py`

**Purpose:** Walks `chapters/code/*/` for `requirements.txt` or `pyproject.toml`. Runs `uv pip compile <input> -o <output>/uv.lock`; copies generated `uv.lock` next to source. Emits `chapters/code/CH-DEP-STATUS.md` with `{chapter, packages, lock_status}`.

**Use when:** Phase 6 for technical books with code listings (before `check_chapter.py --check-imports`).

**Prerequisite:** `pip install uv` (uv 0.7.18+ installed in most envs).

**See also:** `book-kit/docs/SCRIPTS.md` `## pin_deps.py (P14)` section.

---

### Workflow

#### `check-book-repo.sh` - beat-boundary git tag gate (P15)

**Path:** `book-kit/bin/check-book-repo.sh`

**Purpose:** 1-line POSIX guard. Warns if `books/<slug>/.git` is missing. Master calls this before emitting `git tag scope-book/ch-NN-beat-K`. On exit 0, tag is emitted; on exit 1, the orchestrator surfaces the stderr warning and offers the `git init` one-liner.

**Use when:** After every beat write in Phase 6.

**See also:** `book-kit/docs/BEAT_GIT.md` (the convention + recovery flow).

---

### Samples

#### `book-kit/examples/` - visual-style reference (P16)

**Path:** `book-kit/examples/`

**Files:** 10 HTML + 10 PDF samples covering: `dialogue-dense` / `dialogue-sparse`, `tashkeel-full` / `tashkeel-minimal` / `tashkeel-none`, `separator-asterism` / `separator-blank` / `separator-ornament`, `closing-hook-long` / `closing-hook-short`.

**Purpose:** Visual reference for style decisions. Each sample is the SAME 430-word Arabic prose at different style choices - diffing two samples shows the choice and nothing else.

**See also:** `book-kit/docs/STYLE_DECISIONS.md` (Use when / Avoid when for each sample) and `book-kit/book_workflow/book-agents/templates/style-guide.md` (templates reference the samples).

---

### Knowledge graph

#### `book-kit/mcp/book-kg/` - SQLite-backed book knowledge graph (P18)

**Path:** `book-kit/mcp/book-kg/` (5 files: `__init__.py`, `schema.sql`, `indexer.py`, `query.py`, `server.py`)

**Purpose:** Per-book SQLite database (`.book-kg.db`) that indexes chapters / beats / frozen-lines / motifs / characters / bible-anchors / continuity-anchors / chapter-refs / chapter-deps. FastMCP server exposes 4 query tools: `trace_path(motif, ch_start, ch_end)`, `motifs_in_chapter(chapter)`, `contradicts(line)`, `references(chapter)`. FTS5 search index with `unicode61 remove_diacritics 2` tokenizer (Arabic tashkeel-aware).

**Use when:**
- Phase 2 (research): indexer populates DB; trace_path shows motif timeline.
- Phase 6 (writing): re-run indexer after each chapter write to keep mentions current.
- Phase 7 (review): reviewer calls `motifs_in_chapter` + `contradicts` + `references` to validate continuity.

**Key files:**
- `indexer.py` - `python book-kit/mcp/book-kg/indexer.py books/<slug> [--db <path>]`
- `server.py` - FastMCP server (wire as `<name>book-kg</name>` in `~/.config/opencode/opencode.json`)
- `schema.sql` - 14 tables + FTS5; idempotent (UNIQUE constraints on dedup tables)

**Env:** `BOOK_KG_DB` (default: `<book>/.book-kg.db`).

**See also:** `book-kit/docs/ARCHITECTURE.md` -Book knowledge graph (P18)- section.

---

### Translation-mode only

These scripts only run when the book is translating an existing source work (intake Section 10 = yes). See `book-kit/docs/TRANSLATION_MODE.md` for the full flow.

- `build_source_map.py` - generate `source-map.md` from `source/` directory
- `split_source.py` - chunked-write protocol (H2-bounded source splitting)
- `fix_source_urls.py` - URL cleanup before source-map generation
- `extract_figures.py` - `pdfimages` wrapper
- `poll_progress.py` - file-watcher dashboard (`.dashboard.html`)
- `bilingual_smoke.py` - RTL/smoke test (Arabic rendering)
- `build_exports.py` - RTL TOC + Arabic-Indic page numbers
- `strip_publish_annotations.py` - publish-time strip (HTML-comment self-critique blocks)

---

## How agents should reference this file

When an agent's SKILL.md needs to mention a tool:
- DO: `See \`book-kit/docs/TOOLKIT.md\` for the canonical catalog. This agent uses \`book_check.py\` and \`check_chapter.py\` (gate tools).`
- DO NOT: Re-list all 18 tools in your agent's SKILL.md. That creates drift when tools are added/removed.

When in doubt, link to this file with the relevant tool name as anchor.

## Adding a new tool

When P19+ ships:
1. Implement + test the script per the 7-gate process.
2. Add a row to the **Pipeline map** + a section in the **Tool catalog** of this file.
3. Update the agent SKILL.md that needs awareness (link here, not a re-list).
4. Update `book-kit/docs/SCRIPTS.md` with the per-tool entry (this file is the registry; SCRIPTS.md is the per-tool CLI reference).
5. Bump the kit version in `book-kit/VERSION` (engine-owned).
