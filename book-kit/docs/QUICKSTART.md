# Book Kit — Quickstart (60 seconds)

The Book Kit is a portable, cross-platform ZIP that turns any folder on any
laptop into a long-form book-writing environment powered by OpenCode + the
agents-manager multi-agent pipeline. Native books AND translations (Arabic,
etc.) ship first-class.

Same 7-phase pipeline that produced `books/daily-focus/ch-01.md` in the
parent repo — now packaged for sharing.

## 1. Unzip

```sh
unzip book-kit-1.0.0.zip -d my-book-project
cd my-book-project
```

On Windows: right-click → "Extract All" → pick your project folder → `cd` in
PowerShell or cmd. Three install paths are available after extracting:

| Path | When to use |
|---|---|
| `python install.py` (macOS / Linux / Windows + Python in PATH) | cross-platform, the canonical install command |
| `install.bat` (Windows, from inside the kit) | kit-root convenience wrapper around `python install.py` |
| `bin\install-book-kit.bat` (Windows, callable from anywhere) | detects already-unzipped mode and delegates; also accepts a `<zip>` arg for the unzip+install one-shot flow |

## 2. Install

```sh
python install.py
```

That's it. The installer is stdlib-only (no `pip`, no `npm` unless you pass
`--with-chub`). It:

- Runs a preflight check (Python version, OpenCode present, disk space,
  write permissions).
- Lays down engine files (skills, opencode.jsonc, CLAUDE.md, scripts).
- Creates user-owned folders (`books/`, `tasks/`, `share/`).
- Writes a `.book-kit-version` marker.
- Prints the next-step commands.

When run from inside the unzipped kit (`python install.py --target .`),
the installer detects that the kit files are already at the target and
runs in **install-in-place mode**: it skips the file-copy phase
(overwriting the kit onto itself would be destructive), SHA-verifies the
existing files against the manifest (warns on mismatch, doesn't fail —
the user may have edited files), and continues with workspace dirs +
marker + doctor. Use `--copy-anyway` to force the original copy-onto-self
behavior; use `--upgrade` to refresh engine files across kit versions.

Re-running `python install.py` is a no-op. Use `--upgrade` to refresh
engine files against a newer ZIP; `--uninstall` to remove cleanly.

## 3. Launch OpenCode and write a book

```sh
opencode
```

### Native book

In the OpenCode prompt, say:

```
write a book about productivity for new managers
```

### Translation book

```
translate agentic-design-patterns.pdf to Arabic
```

The orchestrator detects translation intent, prompts you for the extra 7
intake fields (§10 of `intake.md`), and runs the two-pass `book-reviewer`.

## 4. The 7 phases

Master loads the book-gen-orchestrator skill and walks you through:

| Phase | What happens | User gate? |
|---|---|---|
| 0 — Intake | 9-field intake (native) + 7-field §10 (translation) | **yes** — every field |
| 1 — Skeleton | Chapter list + dependency tags | no |
| 2 — Research | Per-chapter research (parallel when independent) | no |
| 3 — Outline | Full chapter outline + dependency graph | **yes** |
| 4 — Style/voice | Tone, presentation, POV/tense. Translation: tashkeel + freeze-code | **yes** |
| 5 — Writing plan | LINEAR / PARALLEL / MIXED dispatch order | **yes** |
| 6 — Writing | One chapter at a time. Translation: chunked-write + resume protocol | only on chapter add/remove |
| 7 — Review | Branch A (translation: 2-pass accuracy + consistency) OR Branch B (native: 3-pass dev → line → copy) | only on review-fail escalation |

The pipeline pauses at each user gate. Confirm to advance.

## 5. Verify

```sh
python scripts/doctor.py        # re-runnable preflight check
python scripts/smoke_test.py    # automated end-to-end install smoke

cd book-kit && py -m pytest tests/   # 63 pytest tests across all 7 scripts
```

## What's where

```
my-book-project/
  opencode.jsonc                  # 6-agent roster
  CLAUDE.md                       # project orientation
  .book-kit-version               # install marker
  agents_manager/
    master/SKILL.md
    book-gen-orchestrator/SKILL.md
    book-writer/SKILL.md
    book-reviewer/SKILL.md        # translation-mode two-pass review
    research/SKILL.md
    planning/SKILL.md
    design/SKILL.md
    coder/SKILL.md
    review/SKILL.md
  book_workflow/book-agents/templates/   # 18 phase templates + 1 JSON schema
  book_workflow/scripts/                  # 7 stdlib-only tools (book_check, bilingual_smoke, split_source, extract_figures, build_exports, poll_progress, fix_source_urls)
  book_workflow/tests/                    # 63 pytest tests for all scripts
  books/                          # YOUR MANUSCRIPTS LIVE HERE
  tasks/                          # task tracker files
  share/{notes,handoffs,reports}/ # inter-agent coordination
  docs/                           # QUICKSTART, ARCHITECTURE, WORKFLOW, TRANSLATION_MODE, SCRIPTS, TROUBLESHOOTING, UPGRADE
  scripts/                        # doctor, build_manifest, build_zip, smoke
  bin/                            # book-kit + book-kit.cmd wrappers
```

## Common flags

```sh
python install.py --target ../other-project   # install into a different folder
python install.py --check-only                # verify manifest, no writes
python install.py --upgrade                   # refresh engine files (forces copy mode)
python install.py --uninstall                 # remove engine, preserve user content
python install.py --with-chub                 # also install chub context-hub CLI
python install.py --no-doctor                 # skip preflight (debugging only)
python install.py --copy-anyway               # force copy mode even when target == kit root
```

See `docs/ARCHITECTURE.md` for the design rationale and `docs/TROUBLESHOOTING.md`
for common install failures.

## Translation workflow in 60 more seconds

If your book is a translation, the orchestrator will ask for 7 extra
intake fields:

1. `Is translation?` — yes
2. `Source root` — directory of source files (e.g. `source/`)
3. `Source-naming convention` — e.g. `ch-NN.txt`, `chapter-NN.pdf`
4. `Target slug pattern` — how chapter files are named in the target
5. `Tashkeel policy` — none / light / full (Arabic diacritics)
6. `Freeze code blocks` — yes/no (preserve source code verbatim)
7. `Source map filled` — yes/no (gates Phase 3)

Then in Phase 3 (outline), the orchestrator will REFUSE to advance past
the outline gate unless `source-map.md` is populated. Use
`book-kit/book_workflow/scripts/fix_source_urls.py` to clean pdftotext
artifacts in source files before generating the source map.

In Phase 6, large sources are split at H2 boundaries with
`split_source.py`. The writer's `.translate-progress.json` tracks which
parts are done so a session can resume mid-chapter.

In Phase 7, `book-reviewer/SKILL.md` runs twice: Pass 1 (accuracy vs.
source), Pass 2 (cross-chapter consistency). See
`agents_manager/book-reviewer/SKILL.md`.
