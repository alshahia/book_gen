# Review Resources

Review checklists, common-pitfall lists, and project-specific things to watch for.

## What to put here

- `checklist.md` — the standing per-task checklist you run every time
- `common-pitfalls.md` — known footguns in this repo / stack
- `security-checklist.md` — auth, input validation, secrets, deps
- `perf-checklist.md` — N+1 queries, allocations on hot paths, missing indexes

## Per-invocation routine

For each assigned task, in order:

1. **Spec match** — re-read the task row in `tasks/<task-id>.md`. Does the code do exactly that?
2. **Existence** — is the file at `Files expected` actually created/edited? Open it.
3. **Correctness** — read the changed lines + 10 lines of context. Trace the logic.
4. **Edge cases** — empty input, None/null, large input, concurrent, error paths.
5. **Tests** — is there a test? Does it run? Does it actually exercise the new code?
6. **Style** — match with the file's neighbors. Linter/formatter run?
7. **Secrets / security** — any hardcoded creds, SQL injection, XSS, path traversal?
8. **Scope** — did the coder touch files outside `Files expected`?

If any step fails → verdict is at least `WARN`.

## On first invocation per repo

Populate `common-pitfalls.md` and `security-checklist.md` based on the first 3 reviews. Patterns repeat.
