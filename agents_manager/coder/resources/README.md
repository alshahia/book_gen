# Coder Resources

Repo-specific conventions, build/test commands, and reusable snippets.

## What to put here

- `build-commands.md` — exact commands to build, lint, format, test
- `code-style.md` — naming, imports, error handling patterns
- `test-patterns.md` — how to add a test in this repo (file location, naming, fixtures)
- `snippets/` — copy-paste-safe code snippets for repetitive work

## Reuse over reinvention

Before writing any code:
1. Read `notes/` — your last summary. Match the patterns you used.
2. Read `AGENT_temp.md` § Key Commands and § Tech Stack at the repo root.
3. If a pattern is unclear, read one adjacent existing file and mimic.

## On first invocation per repo

The very first time you run on a new repo, populate:
- `build-commands.md` (run the build once, capture the working command)
- `code-style.md` (read 3 representative files, note the conventions)
- `test-patterns.md` (run the existing tests once, capture the command)

These notes are your future self's shortcut.
