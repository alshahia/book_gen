# Book Kit — Upgrade Guide

The kit ships a `.book-kit-version` marker in the project root after each
install. The installer uses the version to decide between fresh install,
upgrade, and no-op.

## Quick upgrade

```sh
# 1. Get the new ZIP (from the kit's release channel)
unzip book-kit-0.2.0.zip -d /tmp/book-kit-new

# 2. From inside the new kit, run the installer with --upgrade
cd /tmp/book-kit-new
python install.py --target /path/to/your/project --upgrade
```

That's it. Engine files are refreshed; your books, tasks, and share/ notes
stay exactly where you left them.

## What gets overwritten (engine-owned)

- `opencode.jsonc`
- `CLAUDE.md`
- `VERSION`
- `.gitattributes`
- `install.py`
- `manifest.json`
- `bin/book-kit`, `bin/book-kit.cmd`
- `scripts/*.py`
- `agents_manager/**/*.md`
- `book_workflow/book-agents/templates/*.md`
- `docs/*.md`

If you edited any of these directly (you probably shouldn't have), your
edit is backed up to `<original-name>.bak.<sha8>` before overwrite.

## What gets preserved (user-owned)

- `books/**` — every manuscript, intake, outline, style guide, chapter,
  bible entry, ledger row, review report.
- `tasks/**` — task tracker files.
- `share/notes/**` — inter-agent notes (research summaries, coder
  summaries, progress ledgers).
- `share/handoffs/**` — user task captures.
- `share/reports/**` — review outputs.

The installer creates these directories if they don't exist, but never
touches their contents.

## What if a file moved between versions?

If the new kit moves an engine file (e.g. `agents_manager/foo/SKILL.md`
becomes `agents_manager/bar/SKILL.md`), the old file at the old path is
left in place. The installer doesn't track deletions — it only writes
engine files declared in the new `manifest.json`.

Clean up stragglers manually:

```sh
# After upgrade, look for engine files the new manifest no longer ships:
diff <(cat manifest.json | python -c 'import sys,json; print("\n".join(e["path"] for e in json.load(sys.stdin)["engine_files"]))') \
     <(find . -type f \( -name 'SKILL.md' -o -name '*.py' \) | grep agents_manager)
```

Or simply re-run with `--uninstall` first, then `--upgrade` for a clean
state. But uninstall removes ALL engine files (including any user backups
you wanted to keep), so back those up first.

## What if you want to roll back?

The previous kit version's ZIP is on the release channel. Re-download it
and run with `--upgrade` to roll back. Engine files revert; user content
stays.

If you edited engine files between versions, those edits live in
`<name>.bak.<sha8>` files. Restore from backup if needed.

## Verifying an upgrade

After `--upgrade`:

```sh
cat .book-kit-version   # shows the new version + timestamp
python scripts/doctor.py # re-run preflight
python scripts/smoke_test.py  # full install smoke
```

All three should pass cleanly. The smoke test installs into a temp folder,
so your real project is untouched.

## Pre-upgrade checklist

Before upgrading a kit in a project with in-flight work:

- [ ] All chapters in progress have a `drafted` or better status in
      `books/<slug>/ledger.md`.
- [ ] No dispatch prompts in `share/handoffs/` are unprocessed.
- [ ] You have a snapshot of `books/<slug>/bible.md` (it should be
      append-only, so the kit upgrade shouldn't touch it, but verify).
- [ ] You have a git commit of the project (or a `tar`/zip backup) so you
      can roll back if the new kit breaks something unexpected.

## When to skip the upgrade

- You're mid-Phase-6 writing on a chapter. Wait until the chapter is
  `approved` and copy-edit pass is done. Upgrading mid-chapter can change
  specialist behavior and force a re-write.
- The kit's `agents_manager/book-gen-orchestrator/SKILL.md` changed
  significantly. Read the CHANGELOG entry before upgrading — if the
  orchestrator's protocol changed, you may need to restart the current
  book from Phase 3 (outline) onward.