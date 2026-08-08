# Beat-Boundary Git Snapshots

After every beat write (the smallest prose unit within a chapter, typically
600-750 words), the orchestrator emits one git tag so we can diff a single
beat's rewrite without losing the chapter-level baseline. See
`book-kit/bin/check-book-repo.sh` for the gate.

## Convention

After each beat write completes (and the per-beat gate passes), the
orchestrator emits one git tag:

```
git tag scope-book/ch-NN-beat-K
```

where `NN` is the chapter number (zero-padded, e.g. `ch-03`) and `K` is
the beat number (1-indexed). Tags are emitted only when
`books/<slug>/chapters/` is a git repository; verify with
`book-kit/bin/check-book-repo.sh books/<slug>/`.

Tag format rationale:

- `scope-book/...` prefix scopes the tag namespace so it never collides
  with the project's own tags (`v0.1.0`, etc.) or with parallel book tags.
- `ch-NN` mirrors the chapter file naming used everywhere in the pipeline
  (`chapters/ch-NN.md`, `bible.md` rows, ledger rows, review bundles).
- `beat-K` is the beat number the writer writes in `books/<slug>/ledger.md`
  under the chapter's beats table.

## Why

A beat is a single prose unit within a chapter. Tags at beat boundaries
let us diff the per-beat rewrite without losing the chapter baseline:

- **Before a beat:** `git diff scope-book/ch-03-beat-2 scope-book/ch-03-beat-3`
  shows exactly what beat-3 changed. This catches "frozen-line drift": a
  single beat's rewrite accidentally changed a frozen line, breaking the
  SHA256 manifest that `book_check.py` enforces.
- **Across a stage:** `git diff scope-book/ch-03-beat-0 scope-book/ch-03`
  shows the whole chapter at gate time. This is the chapter-level diff
  we already had; the beat tags make it finer-grained.

## Recovery

- See beat-3's rewrite vs beat-2: `git diff scope-book/ch-03-beat-2 scope-book/ch-03-beat-3`
- See beat-3's rewrite vs the full chapter at gate time: `git diff scope-book/ch-03-beat-2 scope-book/ch-03`
- Roll back to beat-2's prose: `git checkout scope-book/ch-03-beat-2 -- books/<slug>/chapters/ch-03.md`
- List all beat tags for a chapter: `git tag --list 'scope-book/ch-03-beat-*'`

The orchestrator never deletes beat tags. They accumulate as a per-beat
audit trail; prune with `git tag -d scope-book/ch-NN-beat-K` only when a
chapter is fully `approved` AND you want a clean tag namespace.

## Setup

Before the first beat write, initialize the book's chapter directory as a
git repo:

```bash
cd books/<slug>
git init
git add chapters/
git commit -m "initial chapters import"
```

Then confirm the orchestrator will emit tags:

```bash
bash book-kit/bin/check-book-repo.sh books/<slug>/
# expected: books/<slug>/: git repo OK
```

If the script exits 1 with `WARNING: ... is not a git repo ...`, the
orchestrator will silently skip the tag and surface the warning. Either
run the setup steps above, or accept the no-tag path (beat diffs become
unavailable; the chapter-level diff still works via `git diff HEAD~N`).

## Related

- `agents_manager/book-gen-orchestrator/SKILL.md` Phase 6 -- the step
  that emits the tag after each beat gate passes.
- `book-kit/docs/QUICKSTART.md` "First time setup" -- where the
  per-book `git init` step lives in the install flow.
