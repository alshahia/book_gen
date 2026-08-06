# Plan — Book-Kit Tool Roadmap (T-2026-08-05-001)

**Created:** 2026-08-05 16:30
**Title:** book-kit tool roadmap — 18-phase sequential build
**Status:** Approved, in execution
**Total effort:** ~15 working days (sequential)
**Source:** User directive — analyze two agent recommendation lists (city-of-memories fiction + ai-agents-with-python technical), cross-reference against current book-kit v1.1.0 inventory, propose what to add with rationale. Then build, one tool at a time, in low-risk order.

## Confirmed Decisions

| Decision | Choice | Why |
|---|---|---|
| Exa integration | MCP primary + built-in `websearch: "allow"` (already wired at `https://mcp.exa.ai/mcp`) | Matches existing MCP pattern in `~/.config/opencode/opencode.json`; dual-wired covers both explicit-semantic-query and casual-search use cases |
| Firecrawl config location | Global `~/.config/opencode/opencode.json` (not project `opencode.jsonc`) | Consistency with Exa placement; project config has no MCP entries (all inherited from host) |
| Firecrawl MCP URL | `https://mcp.firecrawl.dev/v2/mcp-oauth` (remote, OAuth) | Provided by user; OAuth handles auth flow, no key in JSON |
| Firecrawl API key | `fc-919e9ffa4d82483b90dbfa434ec4fa46` (in `.env.local`) | Provided by user; keyless OAuth doesn't unlock full endpoint set per Path F docs |
| Brave | Dropped entirely | No free API key per user directive; YAGNI over stubbing |
| DuckDuckGo fallback | Thin Python wrapper (`scripts/duckduckgo_search.py` over `webfetch`) | Zero deployment cost, fits existing `webfetch` HTML paradigm, 30 lines |
| `.env.local` convention | Adopted as kit convention | Auto-gitignored by most toolchains; matches "never commit secrets" hard rule |
| Book-kg backing | SQLite (FTS5), not Neo4j/Dgraph | 5× faster to ship, identical query API surface, no infra cost |
| Build order | Lowest-risk first; dependencies flow forward; big-bets last | Avoids mid-build confusion, allows gates between phases |

## Master TODO (18 phases)

```
[ ] P1   book-kit: JSON Schema validation for frozen-lines + translate-progress                (0.25 d)
[ ] P2   book-kit: check_chapter.py per-beat prose enforcer                                    (1.5 d)
[ ] P3   book-kit: cross_ref.py + book_check integration                                       (0.5 d)
[ ] P4   book-kit: ledger.md gate checklist template + autogen helper                           (0.5 d)
[ ] P5   book-kit: bible.md rules-applicability table + check_chapter integration               (0.5 d)
[ ] P6   book-kit: gate_summary.py per-chapter gate artifact                                   (0.5 d)
[ ] P7   book-kit: index_reports.py + INDEX.md auto-regen                                      (0.5 d)
[ ] P8   book-kit: book_check.py cross-chapter continuity from bible.md                        (1.0 d)
[ ] P9   book-gen: multi-source web research (Exa + Firecrawl; DuckDuckGo fallback; .env.local) (0.5 d)
[ ] P10  book-kit: LanguageTool MCP + check_chapter.py --lang                                   (0.5 d)
[ ] P11  book-kit: render_mermaid.py figure renderer                                           (0.5 d)
[ ] P12  book-kit: md2pdf.py --book mode (cover, ToC, page numbers, metadata)                   (1.0 d)
[ ] P13  book-kit: visual_qa.py PyMuPDF page diagnostics                                       (1.0 d)
[ ] P14  book-kit: pin_deps.py + check_chapter.py --check-imports                              (1.0 d)
[ ] P15  book-kit: beat-boundary git snapshots (docs + orchestrator hook)                       (0.5 d)
[ ] P16  book-kit: visual-style samples directory (9 rendered examples)                         (1.0 d)
[ ] P17  book-kit: review-subagent budgeted runner (split + fallback protocol)                  (1.0 d)
[ ] P18  book-kit: book knowledge-graph MCP (SQLite + FastMCP)                                 (2.5 d)
```

Total: **15.0 working days**.

---

## Phase Details

### P1 — JSON Schema validation in `book_check.py` (0.25 d)

Add `jsonschema.validate()` for `frozen-lines.json` and `.translate-progress.json` at top of `book_check.py`. Skip silently if `jsonschema` not installed; emit `info: install jsonschema for schema validation` and continue. On validation error: emit `FAIL: schema: <path> <error>` and exit 2.

Tests: 2 in `tests/test_book_check.py` (valid → PASS; mutated schema → FAIL with field name).

Commit: `book-kit: JSON Schema validation for frozen-lines + translate-progress`

### P2 — `check_chapter.py` (1.5 d)

New script. Reuses tokenization from `book_check.py` (copy, don't import — keep scripts independent). CLI: `check_chapter.py <chapter.md> [--beat] [--json] [--config <style-guide.md>]`.

Checks (all return `CheckResult(name, status, evidence)`):
- `word_count_per_beat(chapter_md, window)` — split on H2/H3
- `banned_patterns(chapter_md, patterns)` — from `style-guide.md` `Forbidden patterns:`
- `quote_pair_balance(chapter_md)` — `«»` parity + per-paragraph balance
- `dialogue_own_line(chapter_md)` — paragraph containing `«…»` must not have narration
- `closing_hook(chapter_md, max_words=8)` — last sentence before `<!-- end-of-chapter -->` (or last sentence of file)
- `countdown(chapter_md, min_occurrences=1)` — only when chapter ≥ `countdown_from_chapter` (default 3; bible.md applicability table overrides)
- `arabic_punctuation(chapter_md)` — flag Latin `, ; ? !` outside code blocks; skip URL lines
- `sentence_length(chapter_md, target_median=22)` — warn if median > target

Output:
- `--json` → `{"chapter": "ch-03", "checks": [...]}` to stdout
- default → `reports/<task-id>/check_chapter_ch-NN.md`

Tests: `tests/test_check_chapter.py` — 8 fixtures (one per rule) + 1 happy-path + 1 no-end-of-chapter-mark.

Docs: update `docs/SCRIPTS.md` with new entry.

Commit: `book-kit: check_chapter.py per-beat prose enforcer`

### P3 — `cross_ref.py` (0.5 d)

New script. CLI: `cross_ref.py <books/<slug>/chapters/*.md>`. Patterns scanned:
- English: `[ch-0X]`, `(ch-NN.md#anchor)`, `the [A-Z][a-z]+ section`, `chapter N`
- Arabic: `الفصل [٠-٩0-9]+`, `الفصل [الأول|الثاني|...]`, `في الفصل`

Resolve to file + slugified H2/H3 anchor. Normalize Arabic numerals to ASCII. Emit `reports/<task-id>/cross_ref.md`:

```
## Broken: ch-03.md line 142 → ch-05.md#causes: no such anchor
## Resolved: 17/18 references
```

Wire into `book_check.py` as new check `cross_ref` (auto-run when `books/<slug>/chapters/` exists).

Tests: 4 fixtures (good, broken-anchor, broken-chapter, arabic-numerals).

Commit: `book-kit: cross_ref.py + book_check integration`

### P4 — `ledger.md` gate checklist template (0.5 d)

Append `## Gate checklist` section to `book-kit/book_workflow/book-agents/templates/ledger.md`:

```
| Rule | Status | Evidence |
| Word window | <status> | <count> words (window 600–750) |
| Countdown ≥1 | <status> | <N> occurrences |
| Closing hook ≤8 | <status> | <N> words |
| Frozen lines intact | <status> | <N>/<N> sha256 match |
| Banned-pattern scan | <status> | <N> occurrences |
| Cross-ref integrity | <status> | <N>/<N> resolved |
| Source ratio | <status> | <ratio> |
| Tashkeel ratio | <status> | <ratio> |
```

Add `scripts/render_ledger_check.py` to autogen the block from `check_chapter.py --json` + `book_check.py --json` output.

Update `book-gen-orchestrator/SKILL.md` Phase 6 to call `render_ledger_check.py`.

Tests: 1 fixture chapter → expected markdown table.

Commit: `book-kit: ledger.md gate checklist template + autogen helper`

### P5 — `bible.md` rules-applicability table (0.5 d)

Append `## Rule applicability` section to `book-kit/book_workflow/book-agents/templates/bible.md`:

```
| Rule | Applies from | Reason | Supersedes |
| Countdown ≥1 | ch-03 | Setup chapters 01–02 | — |
| Speaker tags | ch-05 | Style-guide amended YYYY-MM-DD | — |
```

In `check_chapter.py` (P2), parse `bible.md` if path in `--config` points to book root; skip rules per chapter. Hard-code `countdown_from_chapter=3` until P5 lands.

Tests: 2 (rule skipped + applied).

Update `docs/WORKFLOW.md` "mid-book rule change" section.

Commit: `book-kit: bible.md rules-applicability table + check_chapter integration`

### P6 — `gate_summary.py` (0.5 d)

New script. CLI: `gate_summary.py --book <books/<slug>/> --chapter ch-NN --review <share/reports/04_review_*.md>`.

Reads artifacts:
- `<book>/chapters/ch-NN.md` (word count + frozen-lines touched)
- `<book>/bible.md` (rules-applicability)
- `reports/<task-id>/check_chapter_ch-NN.md` (P2 output)
- `reports/<task-id>/book_check.json` (latest)
- `reports/<task-id>/04_review_<task>.md` (reviewer)

Emits `share/reports/02_gate_ch-NN_<task>.md`:

```
## Gate: ch-03 — APPROVED | FIX-LOOP-N | REJECTED
Word count: 712 (window 600–750) ✓
Book-check: PASS (1 warn: glossary_drift 79%)
Reviewer: PASS (0 critical, 1 high)
Frozen lines touched: 2 (lines 41, 88 — both intentional)
Open questions: 1
```

Status logic: `APPROVED` if all checks PASS and review has 0 HIGH/CRITICAL; `FIX-LOOP-N` if any FAIL; `REJECTED` if critical review issue.

Tests: 3 fixtures (approved, fix-loop, rejected).

Wire into `book-gen-orchestrator/SKILL.md` Phase 7.

Commit: `book-kit: gate_summary.py per-chapter gate artifact`

### P7 — `index_reports.py` (0.5 d)

New script. CLI: `index_reports.py [--regen]`. Scans `share/reports/` for files matching `0X_*.md` where X ∈ {0,1,2,3,4,5,6}. Group by phase prefix; emit `share/reports/INDEX.md`:

```
| Phase | File | Date | Status |
|---|---|---|---|
| 02 plan | 02_plan_T-2026-08-01-001.md | 2026-08-01 | — |
| 04 review | 04_review_T-2026-07-30-001_dev-ch01.md | 2026-07-30 | PASS |
```

Parse Status from common markers (`PASS`, `FAIL`, `APPROVED`, `FIX-LOOP`). Hook into `book-gen-orchestrator/SKILL.md` Phase 8 (post-pipeline).

Tests: 1 fixture with 5 dummy reports → expected INDEX.md.

Commit: `book-kit: index_reports.py + INDEX.md auto-regen`

### P8 — Continuity check in `book_check.py` (1.0 d)

Add `bible.md` parser: extract `## Continuity anchor` sections → `{keyword, quote, scope: ch-XX..ch-YY}`.

Add `_check_continuity(book_root, anchors)`:
- For each anchor, grep target chapters for keyword + quote adjacency
- Emit `Coin arc: ch-01 (introduced) → ch-03 (mentioned) → ch-05 (paid) — PASS|FAIL`

Add `coin_arc` detector: scan tracked motif (config in `style-guide.md` `Tracked motifs:` block) across chapters.

Tests: `tests/test_book_check_continuity.py` — 1 fixture 3-chapter where ch-03 omits motif → FAIL.

Update `docs/SCRIPTS.md` "book_check.py" section.

Commit: `book-kit: book_check.py cross-chapter continuity from bible.md`

### P9 — Multi-source web research pipeline (0.5 d)

1. Add `firecrawl` MCP to global `~/.config/opencode/opencode.json`:
   ```json
   "firecrawl": {
     "type": "remote",
     "url": "https://mcp.firecrawl.dev/v2/mcp-oauth",
     "enabled": true,
     "timeout": 31000
   }
   ```
   (Exa already wired; Brave dropped.)
2. Create `book-kit/.env.example` template. Create `E:\book_gen\.env.local` with `FIRECRAWL_API_KEY=fc-919e9ffa4d82483b90dbfa434ec4fa46`. Add `.env.local` to `.gitignore` if not present.
3. Create `scripts/duckduckgo_search.py` — thin wrapper over `webfetch` + `https://html.duckduckgo.com/html/?q=`. Returns `[{url, title, snippet}]`.
4. Create `scripts/parallel_search.py` — CLI: `parallel_search.py "<query>" [--max-results 10] [--fallback]`. Calls Exa + Firecrawl in parallel (Exa via built-in `websearch` permission + explicit MCP); `--fallback` flag triggers DuckDuckGo path.
5. Create `scripts/dedup_results.py` — URL canonicalization (strip `utm_*`, normalize trailing slash, lowercase host) + dedup.
6. Create `bin/check-search-keys.sh` — sources `.env.local`, prints masked status of `FIRECRAWL_API_KEY` (Exa needs no key).
7. Update `agents_manager/research/SKILL.md` `## Multi-source research protocol`:
   - Parallel `tool_use` block: `websearch` (built-in Exa) + `firecrawl` MCP + optional `exa` MCP for explicit semantic queries
   - Fallback: if primary union < 3 unique URLs → `webfetch` for known URLs → `duckduckgo_search.py` for new queries
   - Each layer logs to `share/notes/01_research_<task>_search-trail.md`
8. Update `docs/ARCHITECTURE.md` MCP diagram.

Tests: `tests/test_parallel_search.py` — 3 fixtures (primary OK, fallback triggered, dedup correctness).

Commit: `book-gen: multi-source web research pipeline (Exa + Firecrawl; DuckDuckGo fallback; .env.local)`

### P10 — LanguageTool MCP + `check_chapter.py --lang` (0.5 d)

Install LanguageTool MCP server (with Arabic language pack). Add MCP entry to `~/.config/opencode/opencode.json`.

Add `--lang` flag to `check_chapter.py` (P2): when set, runs LanguageTool on chapter text; emits `arabic_grammar` / `english_grammar` checks.

Tests: 1 valid + 1 planted Arabic grammar error.

Update `docs/SCRIPTS.md` "check_chapter.py --lang" section.

Commit: `book-kit: LanguageTool MCP + check_chapter.py --lang`

### P11 — `render_mermaid.py` (0.5 d)

`npm install -g @mermaid-js/mermaid-cli`. New script: `book-kit/book_workflow/scripts/render_mermaid.py`.

Scan `chapters/*.md` for `` ```mermaid ` blocks. For each block:
- Write to `figures/<slug>-ch-NN-mermaid-<idx>.mmd`
- Run `mmdc -i ... -o figures/<slug>-ch-NN-mermaid-<idx>.png -b transparent`
- Replace block in chapter with `![<caption>](figures/...png)` — write to `chapters-rendered/` mirror; do NOT mutate source

Emit `figures/mermaid-manifest.json` with `{chapter, index, source_hash, png_path}`.

Tests: 1 fixture chapter with 2 mermaid blocks → 2 PNGs + manifest.

Wire into `book-gen-orchestrator/SKILL.md` Phase 6 as pre-PDF step.

Commit: `book-kit: render_mermaid.py figure renderer`

### P12 — `md2pdf.py --book` mode (1.0 d)

Extend existing `book-kit/book_workflow/scripts/md2pdf.py`. Add `--book` mode:

- Read `<book>/toc.md` → list of chapters
- Assemble HTML: `cover.html` (from `style-guide.md` `cover_text` frontmatter) + `preface.html` + each chapter + `back-matter.html`
- Embed `@page { @bottom-right { content: counter(page); } }` in CSS bundle
- ToC page auto-linked from assembled HTML
- Metadata: `--title`, `--author`, `--isbn`, `--build-date` → emit as PDF metadata via Chrome's printToPDF options
- Paper size + fonts from `style-guide.md` frontmatter (`paper_size: B5`, `fonts: {body, display}`)

Tests: 1 fixture book with 3 chapters → PDF inspection (page count ≥ 5, page numbers visible, cover first).

Update `docs/SCRIPTS.md` "md2pdf.py --book" section.

Commit: `book-kit: md2pdf.py --book mode (cover, ToC, page numbers, metadata)`

### P13 — `visual_qa.py` PyMuPDF (1.0 d)

`pip install pymupdf`. New script: `book-kit/book_workflow/scripts/visual_qa.py`.

CLI: `visual_qa.py <book.pdf> --markers <markers.txt>`.

Per page:
- `page.get_pixmap(dpi=150).save("figures/<slug>-page-NN.png")`
- `page.get_text("dict")` → flag widow (last line of para < 1/3 page width) and orphan (first line of para at page bottom)
- Search for marker strings (from `--markers`, e.g. chapter titles) → emit page-number table

Emit `figures/visual-qa.md`:

```
| Page | Chapter | Markers | Widows | Orphans |
|---|---|---|---|---|
| 1 | cover | — | — | — |
| 5 | ch-01 | "..." | 0 | 0 |
```

Tests: 1 fixture 3-page PDF → expected row count + widow detection.

Wire into `book-gen-orchestrator/SKILL.md` Phase 7 as post-PDF check.

Commit: `book-kit: visual_qa.py PyMuPDF page diagnostics`

### P14 — `pin_deps.py` + `check_chapter.py --check-imports` (1.0 d)

`pip install uv`. New script: `book-kit/book_workflow/scripts/pin_deps.py`.

Walk `chapters/code/*/` for `requirements.txt` or `pyproject.toml`. Run `uv pip compile <input> -o <output>/uv.lock`; copy generated `uv.lock` next to source.

Emit `chapters/code/CH-DEP-STATUS.md` with `{chapter: "ch-07", packages: 12, lock_status: "pinned"}`.

Add `check_imports` to `check_chapter.py` (P2): for each `from X import Y` in code listings, verify `X` exists in chapter's `uv.lock` with pinned version.

Tests: 1 fixture with valid pinned dep → PASS; 1 with unpinned dep → FAIL.

Update `docs/SCRIPTS.md` "pin_deps.py" section.

Commit: `book-kit: pin_deps.py + check_chapter.py --check-imports`

### P15 — Beat-boundary git snapshots (0.5 d)

Create `docs/BEAT_GIT.md`:
- Convention: `git tag scope-book/ch-NN-beat-K` after each beat writes
- Why: diff per beat vs per stage catches regressions when a single beat's prose rewrite breaks a frozen line
- Recovery: `git diff scope-book/ch-03-beat-2 scope-book/ch-03-beat-3` to see beat-3's rewrite

Add `book-gen-orchestrator/SKILL.md` Phase 6 step: after each beat check, emit `git tag` only if book's `chapters/` is a git repo.

Add `bin/check-book-repo.sh` (1-line) that warns if `books/<slug>/.git` missing.

Update `docs/QUICKSTART.md` "first time setup" with `git init` step for book dir.

Commit: `book-kit: beat-boundary git snapshots (docs + orchestrator hook)`

### P16 — Visual-style samples (1.0 d)

Create `book-kit/examples/`:
- `dialogue-dense.html` / `dialogue-sparse.html` (PDF-rendered)
- `tashkeel-full.html` / `tashkeel-minimal.html` / `tashkeel-none.html`
- `separator-asterism.html` / `separator-blank.html` / `separator-ornament.html`
- `closing-hook-long.html` / `closing-hook-short.html`

Each file: small (~500 words) synthetic prose in relevant style choice. Render each to PDF; commit both `.html` and `.pdf` in `examples/`.

Add `docs/STYLE_DECISIONS.md` linking each sample to "when to use" rule.

Update `style-guide.md` template to reference samples.

Commit: `book-kit: visual-style samples directory (9 rendered examples)`

### P17 — Review-subagent budgeted runner (1.0 d)

Extend `book-kit/agents_manager/book-gen-orchestrator/SKILL.md` Phase 7:

**Splitting strategy:**
- Count chapter words; if > 2000, split into N review-chunks of ≤800 tokens each at H3 boundaries
- Each chunk gets compact prompt: "Review this 800-token slice for: [checklist]"; output capped at 400 tokens
- Concatenate findings; collapse duplicates

**Fallback protocol:**
- If `am-review` returns "output truncated" or empty, automatically retry with smaller chunk size (1500 → 1000 → 600 words)

Add `book-reviewer` invocation count to `gate_summary.py` (P6) output.

Tests: 1 fixture chapter with 3000 words → orchestrator runs 4 chunks → 1 consolidated review.

Commit: `book-kit: review-subagent budgeted runner (split + fallback protocol)`

### P18 — Book Knowledge-Graph MCP (2.5 d)

SQLite-backed (per decision above). Create `book-kit/mcp/book-kg/`:
- `server.py` — thin MCP server (FastMCP pattern)
- `indexer.py` — walks `books/<slug>/`, extracts chapters / beats / frozen-lines / motifs / characters / bible-anchors
- `query.py` — `trace_path`, `motifs_in_chapter`, `contradicts`, `references`
- `schema.sql` — table defs (see schema below)

Indexer inputs:
- `bible.md` → continuity anchors, characters, motifs (regex over `## Character` / `## Motif` sections)
- `chapters/*.md` → H2/H3 → beats; mentions of motifs/characters → `MENTIONS` edges
- `frozen-lines.json` → FROZEN_LINE nodes; line numbers → chapter → beat
- `outline.md` → chapter dep edges

Query API:
- `trace_path(motif="coin", ch=1..10)` → ordered timeline
- `contradicts(line="frozen-12")` → all chapter refs that disagree
- `references(chapter="ch-03")` → all cross-refs targeting ch-03

Wire into `~/.config/opencode/opencode.json` as `<name>book-kg</name>` MCP.

Update `book-gen-orchestrator/SKILL.md` Phase 3 (research) + Phase 7 (review) to use the graph.

Tests: `tests/test_book_kg.py` — 1 fixture 3-chapter book → expected edges count, trace_path returns 3 nodes in order.

Update `docs/ARCHITECTURE.md` "knowledge graph" section.

Commit: `book-kit: book knowledge-graph MCP (SQLite + FastMCP)`

---

## Book-KG SQL Schema (parallel design track)

```sql
CREATE TABLE books (
    id              INTEGER PRIMARY KEY,
    slug            TEXT UNIQUE NOT NULL,
    title           TEXT,
    root_path       TEXT NOT NULL,
    indexed_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    parser_version  TEXT
);

CREATE TABLE chapters (
    id              INTEGER PRIMARY KEY,
    book_id         INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    chapter_num     INTEGER NOT NULL,
    file_path       TEXT NOT NULL,
    title           TEXT,
    word_count      INTEGER,
    hash            TEXT,
    indexed_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(book_id, chapter_num)
);

CREATE TABLE beats (
    id              INTEGER PRIMARY KEY,
    chapter_id      INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    beat_num        INTEGER NOT NULL,
    level           INTEGER NOT NULL,
    heading         TEXT NOT NULL,
    start_line      INTEGER,
    end_line        INTEGER,
    word_count      INTEGER,
    UNIQUE(chapter_id, beat_num)
);

CREATE TABLE frozen_lines (
    id                      INTEGER PRIMARY KEY,
    book_id                 INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    line_id                 TEXT NOT NULL,
    quote                   TEXT NOT NULL,
    sha256                  TEXT NOT NULL,
    first_seen_chapter_num  INTEGER,
    note                    TEXT,
    UNIQUE(book_id, line_id)
);

CREATE TABLE frozen_line_occurrences (
    id              INTEGER PRIMARY KEY,
    frozen_line_id  INTEGER NOT NULL REFERENCES frozen_lines(id) ON DELETE CASCADE,
    chapter_id      INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    beat_id         INTEGER REFERENCES beats(id),
    line_number     INTEGER,
    context         TEXT
);

CREATE TABLE motifs (
    id              INTEGER PRIMARY KEY,
    book_id         INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    description     TEXT,
    UNIQUE(book_id, name)
);

CREATE TABLE motif_mentions (
    id              INTEGER PRIMARY KEY,
    motif_id        INTEGER NOT NULL REFERENCES motifs(id) ON DELETE CASCADE,
    chapter_id      INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    beat_id         INTEGER REFERENCES beats(id),
    line_number     INTEGER,
    context         TEXT
);

CREATE TABLE characters (
    id              INTEGER PRIMARY KEY,
    book_id         INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    description     TEXT,
    UNIQUE(book_id, name)
);

CREATE TABLE character_mentions (
    id              INTEGER PRIMARY KEY,
    character_id    INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    chapter_id      INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    beat_id         INTEGER REFERENCES beats(id),
    line_number     INTEGER,
    context         TEXT
);

CREATE TABLE continuity_anchors (
    id                      INTEGER PRIMARY KEY,
    book_id                 INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    keyword                 TEXT NOT NULL,
    quote                   TEXT,
    scope_start_chapter     INTEGER,
    scope_end_chapter       INTEGER,
    expected_state          TEXT,
    actual_state_summary    TEXT
);

CREATE TABLE chapter_refs (
    id                      INTEGER PRIMARY KEY,
    from_chapter_id         INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    to_chapter_id           INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    ref_type                TEXT,
    line_number             INTEGER,
    context                 TEXT
);

CREATE TABLE chapter_deps (
    id                      INTEGER PRIMARY KEY,
    chapter_id              INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    depends_on_chapter_id   INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    dep_type                TEXT
);

CREATE TABLE index_runs (
    id              INTEGER PRIMARY KEY,
    book_id         INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    started_at      TEXT NOT NULL,
    finished_at     TEXT,
    files_seen      INTEGER,
    error           TEXT
);

CREATE VIRTUAL TABLE search_index USING fts5(
    content,
    source_type UNINDEXED,
    source_id UNINDEXED,
    book_id UNINDEXED,
    tokenize='unicode61 remove_diacritics 2'
);
```

**Migration strategy:** versioned schema (`schema_version` table) so re-indexes never crash on old DBs. Indexer is idempotent: re-running drops nothing, only inserts missing rows + updates hashes.

---

## Per-Phase Gate (every phase must hit before next starts)

1. **Tests green** — `pytest book-kit/tests/ -v` for all touched scripts.
2. **Manual run** — one real folder (`books/daily-focus/` or a planted fixture).
3. **Linter pass** — `python -m py_compile` on new `.py`; `shellcheck` on new `.sh` (CRLF-normalize for Windows working tree).
4. **Frontmatter** — `python scripts/validate-frontmatter.py` on any new template.
5. **Docs** — `docs/SCRIPTS.md` and/or `docs/ARCHITECTURE.md` updated for new files.
6. **Commit** — atomic, message matches the TODO line.

---

## Timeline (cumulative)

| Phase | Tool | Days | Cum. |
|---|---|---|---|
| 1 | JSON Schema validation | 0.25 | 0.25 |
| 2 | check_chapter.py | 1.5 | 1.75 |
| 3 | cross_ref.py | 0.5 | 2.25 |
| 4 | ledger.md gate checklist | 0.5 | 2.75 |
| 5 | bible.md rules-applicability | 0.5 | 3.25 |
| 6 | gate_summary.py | 0.5 | 3.75 |
| 7 | reports INDEX.md | 0.5 | 4.25 |
| 8 | book_check.py continuity | 1.0 | 5.25 |
| 9 | Multi-source web research | 0.5 | 5.75 |
| 10 | LanguageTool MCP | 0.5 | 6.25 |
| 11 | mermaid CLI renderer | 0.5 | 6.75 |
| 12 | md2pdf.py --book | 1.0 | 7.75 |
| 13 | PyMuPDF visual_qa.py | 1.0 | 8.75 |
| 14 | pin_deps.py + uv | 1.0 | 9.75 |
| 15 | beat-boundary git | 0.5 | 10.25 |
| 16 | visual-style samples | 1.0 | 11.25 |
| 17 | review-subagent budgeted runner | 1.0 | 12.25 |
| 18 | book knowledge-graph MCP | 2.5 | 14.75 |

**Total: ~15 working days.**

---

## Out of Scope (explicitly punted)

| Item | Why punt |
|---|---|
| `tashkeel_audit.py` (separate script) | Already covered by `book_check.py` `tashkeel_ratio` check |
| `kilo_memory_recall` adapter | `memory` MCP already exists; orchestrator can call it with `novel.city.price_rules` keys |
| Notion/Google Docs MCP | Niche; only 1 user request in project history |
| Bibliography / version-stamp linter | Premature; only matters for technical books with versioned claims |
| Readability grader (Flesch-Arabic) | No validated Arabic Flesch; would be theater |
| `codebase-memory` for books | Replaced by book-kg (P18) — more domain-specific |
| Typst typesetter (List A) | Chrome headless is enough for 95% of users; Typst only if Arabic kashida justification becomes a real complaint |

---

## References

- Two source recommendation lists: `share/notes/audit_city-of-memories/` and `share/notes/audit_ai-agents-with-python/`
- Current kit inventory: `book-kit/` v1.1.0; existing scripts in `book-kit/book_workflow/scripts/`
- Host MCP config: `~/.config/opencode/opencode.json` (Exa already wired)
- Project MCP config: `E:\book_gen\opencode.jsonc` (no MCP entries — inherited from host)
- Book-Kit CLAUDE.md hard rules: 6 agents only (no am-assets/am-investigate/am-ship/am-health), max_fix_loops=3, no auto-commits