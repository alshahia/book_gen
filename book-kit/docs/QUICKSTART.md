# Book Kit — Quickstart (60 seconds)

The Book Kit is a portable, cross-platform ZIP that turns any folder on any
laptop into a long-form book-writing environment. Same 7-phase pipeline that
produced `books/daily-focus/ch-01.md` in the parent repo — now packaged for
sharing.

## 1. Unzip

```sh
unzip book-kit-0.1.0.zip -d my-book-project
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

In the OpenCode prompt, say:

```
write a book about productivity for new managers
```

Master loads the book-gen-orchestrator skill and walks you through 7 phases:

| Phase | What happens | User gate? |
|---|---|---|
| 0 — Intake | 9-field intake (title, audience, length, etc.) | yes (every field) |
| 1 — Skeleton | Chapter list + dependency tags | no |
| 2 — Research | Per-chapter research (parallel when independent) | no |
| 3 — Outline | Full chapter outline | **yes** |
| 4 — Style/voice | Tone, presentation, POV/tense | **yes** |
| 5 — Writing plan | LINEAR / PARALLEL / MIXED dispatch order | **yes** |
| 6 — Writing | One chapter at a time, 3-pass review per chapter | only on chapter add/remove |
| 7 — Review | Developmental → line → copy-edit (whole book) | only on review-fail escalation |

The pipeline pauses at each user gate. Confirm to advance.

## 4. Verify

```sh
python scripts/doctor.py    # re-runnable preflight check
python scripts/smoke_test.py # automated end-to-end install smoke
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
    research/SKILL.md
    planning/SKILL.md
    design/SKILL.md
    coder/SKILL.md
    review/SKILL.md
  book_workflow/book-agents/templates/   # 9 phase templates
  books/                          # YOUR MANUSCRIPTS LIVE HERE
  tasks/                          # task tracker files
  share/{notes,handoffs,reports}/ # inter-agent coordination
  docs/                           # QUICKSTART, ARCHITECTURE, etc.
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