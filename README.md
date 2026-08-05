# book_gen

[![Release v1.0.0](https://img.shields.io/badge/release-v1.0.0-blue)](https://github.com/ahmadmhmdsy/book_gen/releases/tag/v1.0.0)
[![Tests](https://img.shields.io/badge/tests-63%20passed-green)](book-kit/tests)
[![License MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **Write long-form books with multi-agent orchestration.** OpenCode + agents-manager + 7-phase pipeline + 7 scripts + 18 templates. Native books AND translations (Arabic, etc.) ship first-class.

This repo is a **book-generation system** built on top of the [agents-manager](https://github.com/ahmadmhmdsy/agents-manager) multi-agent orchestration kit. You give it "write a book about X" (or "translate book Y to Arabic") and it walks through 7 phases — intake, skeleton, research, outline, style, writing-plan, write+review — producing a complete manuscript at `books/<slug>/chapters/`.

## Quick start

### Native book

```sh
# 1. Install the book-kit into your project
git clone https://github.com/ahmadmahmoudsy/book_gen
cd book_gen/book-kit
python install.py

# 2. Launch OpenCode and ask
opencode
# > write a book about productivity for new managers
```

The orchestrator walks you through 7 phases. Each user gate pauses for your confirmation. See [`book-kit/docs/QUICKSTART.md`](book-kit/docs/QUICKSTART.md) for the full flow.

### Translation book (Arabic, etc.)

```sh
# Same install
opencode
# > translate agentic-design-patterns.pdf to Arabic
```

The orchestrator detects translation intent, prompts you for 7 extra intake fields (§10 in `intake.md`), and runs the **two-pass `book-reviewer`** for accuracy + consistency. See [Translation mode](#translation-mode) below.

### Portable ZIP

`book-kit/` ships as a portable ZIP — drop it on any laptop:

```sh
unzip book-kit-1.0.0.zip -d my-book-project
cd my-book-project
python install.py
```

## What you get

| Layer | What | Where |
|---|---|---|
| **Engine** | `agents-manager` orchestrator + 6 specialists | `agents_manager/` |
| **Book-gen specialization** | Orchestrator + writer + reviewer skills (translation-mode aware) | `agents_manager/book-{gen-orchestrator,writer,reviewer}/` |
| **Pipeline** | 7-phase book-gen flow (intake → skeleton → research → outline → style → writing-plan → write+review) | `book-kit/book_workflow/book-agents/` |
| **Templates** | 18 markdown + 1 JSON schema (intake, skeleton, outline, style-guide, source-map, glossary, …) | `book-kit/book_workflow/book-agents/templates/` |
| **Scripts** | 7 stdlib-only tools for translate/edit/validate/export | `book-kit/book_workflow/scripts/` |
| **Tests** | 63 pytest tests for all 7 scripts + self-checks | `book-kit/tests/` |
| **CI** | GitHub Actions: pytest on push | `.github/workflows/tests.yml` |

## The 7-phase pipeline

```
master → research → planning → design → master (writing-plan) → coder (per chapter) → review (whole book)
                                ↑                                       ↑
                                |                                       |
                                +─ bible.md append ─── ledger.md update ─┘
```

| Phase | What happens | User gate? |
|---|---|---|
| **0 — Intake** | Fill `intake.md`. Native books need 9 fields; translation-mode adds 7 more (§10). | **yes** — every field |
| **1 — Skeleton** | Chapter list with dependency tags | no |
| **2 — Research** | Per-chapter research (parallel when independent) | no |
| **3 — Outline** | Full chapter outline + dependency graph | **yes** |
| **4 — Style/voice** | Tone, presentation, POV/tense. For translations: tashkeel policy + freeze-code flag | **yes** |
| **5 — Writing plan** | LINEAR / PARALLEL / MIXED dispatch order | **yes** |
| **6 — Writing** | One chapter at a time. Translation-mode uses **chunked-write** + resume protocol (`split_source.py` + `.translate-progress.json`) | only on chapter add/remove |
| **7 — Review** | Branch A (translation: 2-pass `book-reviewer` accuracy + consistency) OR Branch B (native: 3-pass dev → line → copy) | only on review-fail escalation |

The pipeline pauses at each user gate. Confirm to advance. See [`book-kit/docs/WORKFLOW.md`](book-kit/docs/WORKFLOW.md) (in this release) for the full flow.

## Translation mode

Translation-mode is a first-class book-gen path at the controller level. Triggered when `intake.md §10` says "Is translation? = yes". Then:

1. **Source map** (`source-map.md`) binds each chapter to its source PDF, word-min/word-max, and required H2 sections.
2. **Chunked write** splits large sources at H2 boundaries (`split_source.py`) so the writer can resume mid-chapter via `.translate-progress.json`.
3. **Two-pass review**: `book-reviewer/SKILL.md` runs Pass 1 (accuracy vs. English source) and Pass 2 (cross-chapter glossary consistency) — never combined.
4. **Built-in tools** check the translation: `book_check.py` flags source-ratio misses, glossary drift, missing H2, fence balance, untranslated English; `bilingual_smoke.py` verifies every URL, bolded term, and H2 in source has a chapter counterpart.
5. **RTL export**: `build_exports.py` emits Arabic-Indic page numbers (٠١٢٣) and wraps the TOC in `<div dir="rtl">` when `style-guide.md` declares `rtl: true` or `language: ar`.
6. **Source URL cleanup**: `fix_source_urls.py` repairs `pdftotext` artifacts in source `.txt` files — 6 distinct patterns (page numbers, doubled segments, truncated fragments, etc.).

See [`book-kit/docs/TRANSLATION_MODE.md`](book-kit/docs/TRANSLATION_MODE.md) (in this release) for the full translation workflow.

## Built-in scripts

All 7 scripts are stdlib-only, idempotent, and ship with `--self-check` plus 63 pytest tests:

| Script | Purpose |
|---|---|
| `book_check.py` | Mechanical checks (fence balance, glossary drift, source-ratio, missing H2, tashkeel policy, frozen-line drift) |
| `bilingual_smoke.py` | URL / bold-term / H2 diff between chapter and source |
| `split_source.py` | Chunked-write: split source at H2 boundaries sized per protocol |
| `extract_figures.py` | Extract embedded PDF images via `pdfimages -png -p`, emit per-PDF manifest |
| `build_exports.py` | Emit TOC, glossary, index, README; RTL-aware; Arabic-Indic numerals |
| `poll_progress.py` | `--once` snapshot or `--watch` HTML dashboard; stuck detection (>30min in_progress) |
| `fix_source_urls.py` | Repair 6 pdftotext URL/line artifacts in `source/*.txt` |

See [`book-kit/docs/SCRIPTS.md`](book-kit/docs/SCRIPTS.md) (in this release) for flag references.

## Templates (18 markdown + 1 JSON schema)

The orchestrator produces these artifacts in `books/<slug>/`:

| File | Phase | Purpose |
|---|---|---|
| `intake.md` | 0 | 9 fields (native) + 7 fields (translation §10) |
| `skeleton.md` | 1 | Chapter list + dependency tags |
| `research-log.md` | 2 | Per-chapter research notes |
| `outline.md` | 3 | Full chapter outline + dependency graph |
| `style-guide.md` | 4 | Tone / voice / structure / translation tolerances |
| `writing-plan.md` | 5 | Dispatch order (LINEAR/PARALLEL/MIXED) |
| `bible.md` | 6 (append) | Terminology + characters (writer appends each chapter) |
| `ledger.md` | 6 (update) | Per-chapter status row |
| `decisions-log.md` | ongoing | Append-only architectural decisions |
| `source-map.md` | 0 (translation) | Per-chapter binding to source PDF + word bounds |
| `frozen-lines.json` | ongoing | Line-level SHA-256 freeze for canonical strings |
| `.translate-progress.json` | 6 (translation) | Resume ledger for chunked-write |
| `chapters/ch-NN-*.md` | 6 | The actual manuscript |
| + 5 more… | | |

## What's new in v1.0.0

**The first "ship the whole thing" release.** v1.0.0 reframes this repo as a book-gen deliverable (not just an agents-manager controller with a book specialization bolted on). Concretely:

1. **`fix_source_urls.py` promoted to kit** — was project-local at the translation project; now in `book-kit/book_workflow/scripts/`. Ships with 14 pytest tests covering all 6 fix patterns + idempotency + regressions.
2. **63 pytest tests across all 7 scripts** — replaces `--self-check` as the source of truth. Run with `cd book-kit && py -m pytest`.
3. **Top-level README reframed as book-gen** — quickstart leads with "write a book about X" / "translate book Y to Arabic", not agents-manager controller concepts.
4. **GitHub Actions CI** — `.github/workflows/tests.yml` runs the 63 tests on push.
5. **Book-gen-focused docs** — `book-kit/docs/QUICKSTART.md` updated to 15-field intake + Branch A/B review naming. New `book-kit/docs/WORKFLOW.md`, `TRANSLATION_MODE.md`, `SCRIPTS.md` (in this release).
6. **Version bumped 0.22.0 → 1.0.0** — signals "this is the deliverable, not a beta".

### What's still open

- `bin/promote.py` + `.book-kit/overrides/` for explicit script promotion — deferred to v1.1.0.
- 10 known complex pdftotext URL corruptions (page numbers glued without `/`, doubled mid-path segments, etc.) — `fix_source_urls.py` documents them but doesn't auto-fix; manual review per project.

## Under the hood

This repo wraps the **agents-manager** multi-agent kit. The controller at `agents_manager/` defines 6 specialists (master, research, planning, design, coder, review) plus 3 on-demand book-gen skills (orchestrator, writer, reviewer). The book-gen specialization is loaded on intent detection — see [`agents_manager/SKILL.md`](agents_manager/SKILL.md) for the full dispatch logic.

For agents-manager controller docs (flags, version history, install paths), see [`agents_manager/CHANGELOG.md`](agents_manager/CHANGELOG.md).

## Contributing

Bug reports, feature requests, and pull requests are welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md) for the workflow.

## License

MIT — see [`LICENSE`](LICENSE).
