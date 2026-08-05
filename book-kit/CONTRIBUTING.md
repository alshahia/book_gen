# Contributing to Book Kit

Thanks for using Book Kit. Feedback and contributions make it better for everyone.

This file covers four ways to help:

1. [Report a bug](#1-report-a-bug)
2. [Suggest an improvement](#2-suggest-an-improvement)
3. [Contribute code or docs](#3-contribute-code-or-docs)
4. [Report a translation-mode-specific issue](#4-translation-mode-issues)

If you only have a quick question, the issue tracker is still the right place — open an issue with the `question` label.

## Before you file anything

- **Check the docs first.** Most "bugs" are documented behavior. See `README.md`, `docs/QUICKSTART.md`, `docs/TROUBLESHOOTING.md`, and the per-script `--help` output.
- **Check existing issues.** Search [issues](../../issues) for your problem — duplicate reports slow triage.
- **Run the latest version.** Upgrade with `python install.py --upgrade` before filing. Bugs in old versions are usually already fixed.

## 1. Report a bug

Open an issue with the `bug` label. Include:

```markdown
## Bug report

### Environment
- Book Kit version: (run `cat .book-kit-version` in your project)
- OS: (Windows / macOS / Linux — include version)
- OpenCode version: (run `opencode --version`)
- Python version: (run `python --version`)

### What you did
(Exact steps. Numbered list. Include the command line + which phase.)

### What you expected
(One sentence. The expected behavior.)

### What happened
(One sentence. The actual behavior. Include the error output verbatim.)

### Artifacts
- Path to the chapter file (if relevant): `books/<slug>/chapters/ch-NN.md`
- Path to the script output: `share/reports/04_*.md` or stderr transcript
- Relevant config: (intake.md §10 fields, source-map.md row, frozen-lines.json entry)
```

**Do NOT include:**
- Secrets (API keys, account passwords)
- Personal data from your book content (paste only the relevant paragraph)
- Output larger than ~200 lines (link to a gist or attach as `.txt`)

**Bash vs PowerShell output:** PowerShell often wraps lines differently. If the error appeared in PowerShell, paste the PowerShell output, not a Bash re-creation.

## 2. Suggest an improvement

Open an issue with the `enhancement` label. Include:

```markdown
## Improvement suggestion

### Problem
(One paragraph. What hurts today? What can't you do?)

### Proposed solution
(One paragraph. What would make it better? Sketch the API/UX, don't write the code yet.)

### Alternatives considered
(Bullet list. Other ways you could solve the problem yourself.)

### Scope
- [ ] Pure docs change (no code)
- [ ] One script change
- [ ] Multiple scripts + orchestrator SKILL
- [ ] New skill or new template
```

The maintainers will route the suggestion to the appropriate specialist (research / design / planning) before any code is written. Most suggestions need a 5-question preflight before they're accepted.

## 3. Contribute code or docs

### Workflow

```
1. Fork the repo
2. Create a branch: git checkout -b feat/<short-name>  (or fix/, docs/, chore/)
3. Make your change (see "Coding conventions" below)
4. Run the local smoke tests:
     python scripts/test-dispatch-selection.py   # 4 dispatch scenarios + book_check
     python scripts/validate-frontmatter.py agents_manager/**/*.md
     python install.py --check-only             # manifest integrity
5. Open a pull request (see PR template below)
6. Wait for CI + review
```

### Coding conventions

- **Stdlib only.** No new pip/npm dependencies in the kit. Use what Python already provides.
- **One script change at a time.** Don't refactor + add a feature in the same PR.
- **Add `--self-check` to new scripts.** The smoke test depends on it.
- **Update templates when you change contracts.** If you add a field to `intake.md` §10, also update `agents_manager/book-gen-orchestrator/SKILL.md` and `books/README.md`.
- **English-only comments.** Variable names, comments, and commit messages. Prose is free-form (per your book's audience).

### PR template

```markdown
## What
(One sentence. What does this PR do?)

## Why
(One sentence. What problem does it solve? Link the issue.)

## How
(Bullet list of changes. Files touched. Lines moved.)

## Test
- [ ] `python scripts/test-dispatch-selection.py` passes
- [ ] `python scripts/validate-frontmatter.py` passes
- [ ] New behavior verified against `books/daily-focus/` (smoke test project)

## Backwards compatibility
- [ ] No breaking changes
- [ ] Breaking change (explain migration in PR body)
```

### Commit message style

```
<area>: <one-line summary>

<one-paragraph body explaining the why>

Affected: <file paths>
Fixes: <issue number>
```

Examples:
- `orchestrator: wire Phase 7 Branch A/B dispatch-selection for translation-mode`
- `scripts: add test-dispatch-selection.py smoke test`
- `docs: clarify source-map.md freeze_code semantics`

## 4. Translation-mode issues

Translation-mode projects use additional files (`source-map.md`, `.translate-progress.json`) and a different Phase 7 branch (2-pass `book-reviewer` instead of 3-pass dev/line/copy). When reporting issues in this mode, include:

```markdown
## Translation-mode report

### Trigger
(intake.md §10 `Is translation?` value + source-map.md `freeze_code` value)

### Source
- Source format: (PDF / EPUB / .md / .txt / other)
- Source extraction tool: (pdftotext / pdftohtml / custom)
- Source root path: (e.g. `source/`)

### Target
- Target slug: (e.g. `agentic-design-patterns-ar`)
- Target language + tashkeel policy: (e.g. Arabic, light tashkeel)
- Chapters translated: <count> (e.g. 12 of 29)

### Failure
- Which check failed: (source-ratio / missing-H2 / code-block-freeze / untranslated-English / glossary-drift / book-reviewer verdict)
- Path to the report: `share/reports/04_book-review_<task-id>_ch-<NN>_accuracy.md` or `_consistency.md`

### Sample
- One chapter failing: `books/<slug>/chapters/ch-NN.md`
- Corresponding source: `source/ch-NN.txt`
- source-map.md row: (the table row for that chapter)
```

If the failure involves **URL preservation** or **bolded-term preservation**, those checks live in `scripts/bilingual_smoke.py`. Include the smoke output verbatim.

## Triage process

After you file an issue:

1. **Labeling (1 day):** maintainer labels with `area/*` (orchestrator / script / docs / install), `severity/*` (critical / high / medium / low), and `type/*` (bug / enhancement / question).
2. **Reproduction (1–3 days):** maintainer (or `am-investigate` agent) reproduces on the canonical smoke-test project (`books/daily-focus/` for native, a synthetic translation project for translation-mode).
3. **Fix dispatch (3–7 days):** `master` dispatches to `am-coder` for code changes, or `am-design` for docs/SKILL changes.
4. **Review (1–3 days):** `am-review` validates against the same smoke-test project. Maintainer signs off.
5. **Release:** cherry-picked to the next kit release (`vX.Y.Z`). You get credited in the CHANGELOG.

## What NOT to do

- **Don't open PRs against this repo for your project's local tweaks.** Edit your local copy. The kit is portable; you own your instance.
- **Don't open issues for problems with your book's content.** Those go in your `books/<slug>/decisions-log.md`, not here.
- **Don't open issues asking the maintainers to translate your book.** This kit supports translation-mode, but the kit does not contain any translation work — that's your project's job.

## Maintainers

This kit ships from the `agents-manager` controller repo. The canonical issue tracker is [here](../../issues). Questions about the controller's pipeline belong in the controller's repo; questions about the kit's packaging, scripts, and templates belong here.

## License

By contributing, you agree your contributions are licensed under the same license as the kit (see `LICENSE` if present; otherwise the project's default).
