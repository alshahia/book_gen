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
Phase 9 (book2media)    - media_manifest.py    (Phase 1; validator + generator)
                         - voices.py           (Phase 2a; TTS voice registry, per-locale)
                         - media_tts.py        (Phase 2b; H2-driven chunk + synthesize)
                         - check_whisper_deps.py (Phase 3; faster-whisper deps)
                         - transcribe_chapter.py (Phase 3; faster-whisper ASR)
                         - align_srt.py        (Phase 3; difflib alignment + normalize_arabic)
                         - srt_to_ass.py       (Phase 3; pysubs2 Amiri RTL)
                         - install_amiri.py    (Phase 3; font install)
                         - assemble_audiobook.py (Phase 4a; M4B two-pass loudnorm)
                         - ffmpeg_zoompan.py   (Phase 4b; shared Ken Burns lib)
                         - assemble_video_horizontal.py (Phase 4b; Mode-1 1920x1080)
                         - assemble_video_trailer.py (Phase 4b; 60-90s teaser)
                         - assemble_reel.py    (Phase 4b; 3-platform 1080x1920)
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

### Media manifest

#### `media_manifest.py` - media-locale-manifest validator + generator (Phase 9)

**Path:** `book-kit/book_workflow/scripts/media_manifest.py`

**Purpose:** Validates and generates `books/<slug>/media-locale-manifest.json` (Phase 9 of the book-gen pipeline). The manifest is the per-book registry of media products (audiobook M4B, video-horizontal-m1, video-vertical-trailer, video-vertical-reel) per locale, with per-product `tts_provider`, `voice`, `skip`, `translation_required`, and `cover_image_fallback_ladder` fields. The script enforces the three-tier provider resolution rule (per-book manifest wins, `providers.yaml` next, built-in defaults last).

**Invocation shape (canonical):**

```
py -3 "<repo-root>/book-kit/book_workflow/scripts/media_manifest.py" validate <manifest-path>
py -3 "<repo-root>/book-kit/book_workflow/scripts/media_manifest.py" generate --book <slug-dir>
```

**Why direct-file invocation, not module form:** `book-kit/` does not ship `__init__.py`, so the Python `book_workflow.scripts.media_manifest` import path does not work. The script runs standalone via the direct-file path above. This is the same pattern as every other book-kit script (see `book_check.py`, `check_chapter.py`, etc.).

**Subcommands:**

- `validate <manifest-path>` -- schema-checks the manifest against the JSON Schema embedded in `book-kit/book_workflow/scripts/media_manifest.py` at L96-L145 (no standalone `.json` file). Exits 0 on success. On schema error, emits a JSON-path line (e.g. `products.0.voice: <message>`) and exits 2.
- `generate --book <slug-dir> --providers providers.yaml --out media-locale-manifest.json [--source-locale en]` -- generates a stub manifest from the book's `chapters/`, the global `providers.yaml`, and the optional `--source-locale` default. Use this to bootstrap a manifest at Phase 1 dispatch; the user fills in per-product overrides afterwards.

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | success (validate or generate) |
| 2 | input error (schema/field error, file not found, path escapes book root) |
| 3 | missing dependency (`jsonschema` package absent) |
| 4 | providers.yaml malformed |

**See also:** `agents_manager/book2media-orchestrator/SKILL.md` Phase 1 (media-manifest lane), `agents_manager/assets/SKILL.md` Media-manifest lane section, `book-kit/docs/SCRIPTS.md` `## media_manifest.py` section.

---

### TTS (text-to-speech, Phase 2a + 2b)

#### `voices.py` - per-locale TTS voice registry (Phase 2a)

**Path:** `book-kit/book_workflow/scripts/voices.py`

**Purpose:** Three-tier voice resolution (per-book manifest > global `providers.yaml` > built-in registry). Resolves a TTS voice for a given `(book, locale, tts_provider)` triple, lists available voices for a locale, and surfaces the built-in registry for inspection. The voice field is mandatory per product in the media-locale-manifest schema (no empty-string `voice: ""` allowed); use `skip: true` to drop a product.

**Use when:** am-coder at Phase 2 dispatch; every TTS call resolves voice through this registry.

**Key API:**
- `resolve_voice(book, locale, tts_provider)` -- returns the voice id string
- `list_voices(locale, tts_provider)` -- returns list of voice ids for that provider
- `VOICE_REGISTRY` -- built-in defaults per provider (kokoro, edge-tts)

**Built-in defaults:**
- kokoro + en -> `af_heart` (Kokoro Grade A)
- edge-tts + ar -> `ar-SA-HamedNeural`
- See source for full table.

**See also:** `book-kit/docs/SCRIPTS.md` `## voices.py` section.

---

#### `media_tts.py` - per-chapter audio synthesis (Phase 2b)

**Path:** `book-kit/book_workflow/scripts/media_tts.py`

**Purpose:** H2-driven chunker + per-locale TTS dispatcher. Splits a chapter into H2-aligned chunks (~200-400 tokens each) and synthesizes one MP3 per chunk. Dispatches to Kokoro (en default) or edge-tts (ar default) based on the media-locale-manifest; falls back through three-tier resolution. Emits a TTS manifest alongside each chapter's audio: `books/<slug>/chapters/ch-NN-words.json` consumed by `transcribe_chapter.py`.

**Use when:** Phase 2 dispatch (TTS lane).

**Key flags:**
- `--book <dir>` - book root (required)
- `--chapter ch-NN` - chapter id (required)
- `--locale en|ar` - locale code (required)
- `--out <path>` - output MP3 path (must resolve under book root)
- `--tts-provider kokoro|edge-tts` - overrides manifest if set

**Prerequisite:** `uv pip install kokoro==0.9.4 edge-tts==7.2.3` into `.venv`.

**See also:** `book-kit/docs/SCRIPTS.md` `## media_tts.py` section, `book-kit/book_workflow/lib/tts_events.py` (event-format helpers for boundary metadata).

---

### Caption (Phase 3)

#### `check_whisper_deps.py` - faster-whisper dependency check (Phase 3)

**Path:** `book-kit/book_workflow/scripts/check_whisper_deps.py`

**Purpose:** Verifies that `faster-whisper` is installed and importable; reports the available ASR models (small, medium, large-v3) and the Hugging Face cache directory. Exits 3 if the package is missing; emits an actionable install hint via `lib/errors.py`.

**Use when:** Before any Phase 3 dispatch (caption pipeline). am-coder calls this at the top of every caption leg.

**Key flags:**
- `--language en|ar` - hint which ASR model to prefer (ar=large-v3, en=small)
- `--self-check` - emit version + device + cache-dir info; exit 0
- `--cache-dir <path>` - override the HF cache directory (default: `~/.cache/huggingface`)
- `--device cuda|cpu` - force device (default: auto-detect)

**Note:** The default `--cache-dir` of `~/.cache/huggingface` is a known leak (Deferred WARN W1 — fix in a v1.3.1 polish dispatch). For notebook work, pass `--cache-dir <repo>/.cache/faster-whisper`.

**Prerequisite:** `uv pip install faster-whisper==1.2.1`.

**See also:** `book-kit/docs/SCRIPTS.md` `## check_whisper_deps.py` section.

---

#### `transcribe_chapter.py` - faster-whisper ASR with word timestamps (Phase 3)

**Path:** `book-kit/book_workflow/scripts/transcribe_chapter.py`

**Purpose:** Runs faster-whisper on a chapter's audio MP3 with `word_timestamps=True`. Writes a JSON with per-word `{word, start, end, probability}` entries. Per-locale model selection: `ar -> large-v3`, `en -> small` (configurable via `MODEL_FOR_LOCALE`).

**Use when:** Phase 3 caption pipeline (after `media_tts.py` produces audio).

**Key flags:**
- `--book <dir>` - book root
- `--chapter ch-NN` - chapter id
- `--locale en|ar` - locale code
- `--out <path>` - output words JSON path
- `--mp3 <path>` - input audio MP3 path
- `--dry-run` - print the plan without running
- `--from <path>` - resume from a previous JSON
- `--only <N>` - only transcribe the first N segments

**See also:** `book-kit/docs/SCRIPTS.md` `## transcribe_chapter.py` section.

---

#### `align_srt.py` - difflib SequenceMatcher SRT alignment (Phase 3)

**Path:** `book-kit/book_workflow/scripts/align_srt.py`

**Purpose:** Aligns faster-whisper word timestamps against the canonical chapter text using `difflib.SequenceMatcher` at chunk granularity. Emits an SRT with one cue per matched text segment. Includes `normalize_arabic()` to strip diacritics (U+0610-U+061A, U+064B-U+065F, U+0670, U+06D6-U+06DC, U+06DF-U+06E4, U+06E7-U+06E8, U+06EA-U+06ED) and normalize alef/yaa/tatweel for genuine-Arabic alignment. Detects Latin text in non-English locales and drops the drift floor with a translation-pending warning.

**Use when:** Phase 3 caption pipeline (after `transcribe_chapter.py` produces a words JSON).

**Key flags:**
- `--book <dir>` - book root
- `--chapter ch-NN` - chapter id
- `--locale en|ar` - locale code
- `--words-json <path>` - input words JSON
- `--out <path>` - output SRT path
- `--drift-floor <float>` - minimum match ratio (default: 0.70); below this, raises exit 4

**Exit codes:** 0 = aligned, 2 = input error, 4 = drift above floor.

**See also:** `book-kit/docs/SCRIPTS.md` `## align_srt.py` section.

---

#### `srt_to_ass.py` - pysubs2 SRT to ASS with Amiri RTL (Phase 3)

**Path:** `book-kit/book_workflow/scripts/srt_to_ass.py`

**Purpose:** Converts an SRT to an ASS subtitle file using `pysubs2`. For Arabic: forces `WrapStyle=2` + `\an2` alignment + Amiri font. For English: uses the default sans-serif. The ASS file is what the video assemblers consume via libass `ass=...:shaping=complex`.

**Use when:** Phase 3 caption pipeline (after `align_srt.py` produces an SRT).

**Key flags:**
- `--in <srt-path>` - input SRT
- `--out <ass-path>` - output ASS
- `--locale en|ar` - source locale (required, chooses WrapStyle + font)
- `--font-size <int>` - subtitle font size in points (default: 24)

**Prerequisite:** Amiri font installed via `install_amiri.py`; `pysubs2==1.8.1` in venv.

**See also:** `book-kit/docs/SCRIPTS.md` `## srt_to_ass.py` section.

---

#### `install_amiri.py` - Amiri font installer (Phase 3)

**Path:** `book-kit/book_workflow/scripts/install_amiri.py`

**Purpose:** Downloads the Amiri font family (Regular, Italic, Bold, BoldItalic, Quran) from the official GitHub release. Idempotent (skips download if `EXPECTED_MIN_FONTS=5` are already at `--target-dir`). Exits 3 if download fails; emits an actionable hint.

**Use when:** Before any Phase 3 Arabic caption work. Run once per host.

**Key flags:**
- `--target-dir <path>` - install dir (default: `%LOCALAPPDATA%\fonts` on Windows, `~/.fonts` on Unix)
- `--verify` - check existing install; exit 0 if >= 5 fonts present
- `--force` - re-download even if installed

**Note:** No SHA256SUMS verification on the zip (Deferred WARN W3 — fix in a v1.3.1 polish dispatch).

**See also:** `book-kit/docs/SCRIPTS.md` `## install_amiri.py` section.

---

### ffmpeg assembly (Phase 4)

#### `assemble_audiobook.py` - M4B assembler with two-pass loudnorm (Phase 4a)

**Path:** `book-kit/book_workflow/scripts/assemble_audiobook.py`

**Purpose:** Concatenates per-chapter MP3s into a single M4B audiobook with chapter markers, ID3 metadata (title, author, language ISO 639-2), and embedded cover PNG. Two-pass loudnorm (I=-19 LUFS, TP=-2 dBTP, LRA=11) brings the assembled audio to streaming-platform targets. `--self-check` validates chapter count matches input. Voice-policy enforcement raises exit 2 when the manifest voice differs from the synthesized voice.

**Use when:** Phase 4a dispatch (audiobook lane).

**Key flags:**
- `--book <dir>` - book root
- `--out <path>` - output M4B path
- `--locale en|ar` - locale code
- `--cover <path>` - cover image (overrides fallback ladder)
- `--no-loudnorm` - skip both loudnorm passes
- `--self-check` - assert chapter count matches input

**Cover fallback ladder:** `figures/cover.png` -> `chapters-rendered/*.png` (first match). If all tiers missing, raises exit 2.

**Exit codes:** 0 = success, 2 = input error, 3 = missing dep (ffmpeg), 4 = self-check fail.

**Performance:** 30s wall for a 700s chapter (no video render); two-pass loudnorm adds ~5s.

**See also:** `book-kit/docs/SCRIPTS.md` `## assemble_audiobook.py` section.

---

#### `ffmpeg_zoompan.py` - shared Ken Burns library (Phase 4b)

**Path:** `book-kit/book_workflow/scripts/ffmpeg_zoompan.py`

**Purpose:** Library (not a CLI). Exports `compute_zoompan_filter(width, height, audio_duration, scale_mult=4)` and `supersample_zoompan_filterchain(width, height, audio_duration, scale_mult=4)`. The 4x supersample (`scale=8000:-1` -> `zoompan` -> `scale=1920:1080`) is the canonical Ken Burns trick to kill zoompan judder. Default `ZOOM_DEFAULT_30S_NATURAL = (1.0, 1.08, "0", "ih/2-ih/(2*zoom)")` for natural 1.0x to 1.08x zoom over 30s. Imported by `assemble_video_horizontal.py` and `assemble_video_trailer.py`; not invoked directly.

**Use when:** Shared library; never invoked standalone. Imported by every video assembler.

**Performance:** 4x supersample = ~11x realtime at 1920x1080. Documented escape hatches: `scale_mult=2` (scale=4000:-1) for ~4x faster renders with slight quality loss; NVENC (`-c:v h264_nvenc`) for ~5-10x faster on Nvidia GPUs. **These are plumbing-level constants — not yet CLI-reachable** (Deferred WARN F5 from Phase 5 review; fix in a v1.3.1 polish dispatch).

**See also:** `book-kit/docs/SCRIPTS.md` `## ffmpeg_zoompan.py` section.

---

#### `assemble_video_horizontal.py` - Mode-1 landscape video (Phase 4b)

**Path:** `book-kit/book_workflow/scripts/assemble_video_horizontal.py`

**Purpose:** Renders a 1920x1080 Mode-1 video from a single static cover + Ken Burns zoompan + audio + optional burned subs (libass `ass=...:shaping=complex`) + optional BGM (amix). Per-chapter loop: one MP4 per chapter, then a final concat. Emits `figures/media-video-manifest.json` sidecar.

**Use when:** Phase 4b dispatch (horizontal video lane).

**Key flags:**
- `--book <dir>` - book root
- `--chapter ch-NN | --all` - one chapter or the whole book
- `--out <path>` - output MP4 path
- `--audio <path>` - per-chapter MP3
- `--cover <path>` - cover image (overrides fallback ladder)
- `--burn-subs` + `--subs <ass>` - burn subtitles
- `--bgm <path>` - background music

**Performance:** ~11x realtime at 4x supersample (e.g., 60s clip = 11.2 min wall). Full 700s chapter = ~131 min estimated. Use `scale_mult=2` escape hatch (not yet CLI-reachable) or switch to NVENC.

**Exit codes:** 0 = success, 2 = input error, 3 = missing dep (ffmpeg), 4 = ffmpeg runtime error.

**See also:** `book-kit/docs/SCRIPTS.md` `## assemble_video_horizontal.py` section.

---

#### `assemble_video_trailer.py` - 60-90s teaser (Phase 4b)

**Path:** `book-kit/book_workflow/scripts/assemble_video_trailer.py`

**Purpose:** Builds a single 60-90s teaser from the whole book. Clip-selection pass picks the first ~12 chunks by 1500-char budget across all chapters, with proportional per-chapter audio windows. Otherwise mirrors `assemble_video_horizontal.py` (1920x1080, Ken Burns, libass, BGM).

**Use when:** Phase 4b dispatch when the user wants a teaser.

**Key flags:** same as `assemble_video_horizontal.py`.

**Performance:** ~11x realtime for 60-90s; ~10-15 min wall per trailer.

**See also:** `book-kit/docs/SCRIPTS.md` `## assemble_video_trailer.py` section.

---

#### `assemble_reel.py` - vertical 1080x1920 reel, 3 platforms (Phase 4b)

**Path:** `book-kit/book_workflow/scripts/assemble_reel.py`

**Purpose:** Renders a 1080x1920 vertical reel and fans out to 3 platform-specific MP4s: YouTube Shorts (I=-14/TP=-1, bottom-center captions), Instagram Reels (I=-16/TP=-1.5, bottom-center), TikTok (I=-14/TP=-1, top-center). Uses a two-step serial architecture: render shared base video to a temp file (one ffmpeg, no audio, no per-platform filter), then per-platform ffmpeg applies loudnorm + ASS alignment + vignette. Peak memory bounded by ONE libx264 encoder at a time.

**Use when:** Phase 4b dispatch (vertical reel lane).

**Key flags:**
- `--book <dir>` - book root
- `--chapter ch-NN` - chapter id
- `--out <path>` - base output MP4 (gets `-yt`, `-ig`, `-tiktok` suffixes)
- `--audio <path>` - per-chapter MP3
- `--cover <path>` - cover image (overrides fallback ladder)
- `--burn-subs` + `--subs <ass>` - burn subtitles
- `--bgm <path>` - background music
- `--platforms yt,ig,tiktok` - comma-separated platform list (default: all three)

**Performance:** ~6x realtime single-platform. Multi-platform fan-out runs serially after a single base render.

**Known limits:**
- 4:4:4 chroma replaced with 4:2:0 (`yuv420p`) for fan-out safety (Phase 5 Bug #3 fix).
- Per-platform loudnorm is single-pass (one render + per-platform apply). Two-pass is acceptable per plan and currently deferred.

**See also:** `book-kit/docs/SCRIPTS.md` `## assemble_reel.py` section.

---

### Shared library code (Phase 2b / Phase 3)

#### `lib/tts_events.py` - TTS event-format helpers

**Path:** `book-kit/book_workflow/lib/tts_events.py`

**Purpose:** Library. Translates raw TTS event streams (WordBoundary, SentenceBoundary) into a uniform format consumable by downstream captioning. Public API: `TTSEventCollector`, `collect_sentence_offsets` (async), `sentence_offsets_to_srt`, `get_provider_event_format` (returns `'ms-windows'` for edge-tts, `'kokoro-v0.9'` for Kokoro).

**Use when:** Imported by am-coder when wiring TTS event collectors into a TTS provider.

**Note:** HINTS in `lib/errors.py` are mutable dicts; freeze with `MappingProxyType` or document as const before exposing them as a public API (WARN from Phase 2b review; trivial fix in a v1.3.1 polish).

**See also:** `book-kit/docs/SCRIPTS.md` `## lib/tts_events.py` section.

---

#### `lib/errors.py` - actionable error hints

**Path:** `book-kit/book_workflow/lib/errors.py`

**Purpose:** Library. Defines `MediaPipelineError(Exception)` carrying `.hint` + `.exit_code`; `raise_actionable(error_kind, **ctx)` raises; `format_hint(error_kind, **ctx)` returns without raising. The `HINTS` dict has 6 keys: `missing_amiri_font`, `voice_unavailable`, `schema_invalid`, `audio_empty`, `comfyui_not_running`, `unsupported_locale`.

**Use when:** Every Phase 2-4 script imports `format_hint` and `raise_actionable` for uniform error reporting.

**See also:** `book-kit/docs/SCRIPTS.md` `## lib/errors.py` section.

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
