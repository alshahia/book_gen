# Book Kit — Troubleshooting

## Install-time errors

### `Python X.Y detected` (FAIL on doctor)

The kit needs Python 3.8 or newer.

- macOS / Linux: `python3 --version`. Install from https://python.org or via
  your package manager (`brew install python`, `apt install python3`).
- Windows: `python --version` from cmd or PowerShell. Make sure the
  launcher is on PATH; the Microsoft Store stub sometimes hides the real
  install.

### `cannot write to <target>`

- macOS / Linux: pick a folder you own (`~/projects`, not `/opt`).
- Windows: right-click the parent folder → Properties → Security tab → make
  sure your user has Write permission. Or pick a folder under `%USERPROFILE%`.

### `only N MB free`

Free up disk space. Book Kit itself is ~600 KB but each book's research-log
+ outline + style-guide can add up. Recommend ≥ 200 MB free.

### `manifest.json missing — re-download the kit`

The kit ZIP was incomplete or corrupted. Re-download. Verify the SHA-256
checksum if the release channel publishes one.

### `target resolves to the kit root; refusing to install into self`

You're inside the unzipped kit folder. `cd` to the project you want to
install INTO, not the folder that contains `install.py`.

### `target is inside the kit root`

Same as above. Pick a sibling or parent folder.

### `existing Book Kit install detected`

A prior install is in the target folder. Use:

```sh
python install.py --upgrade    # refresh engine files, preserve user content
python install.py --uninstall  # remove engine files, preserve user content
```

If you ran plain `python install.py` (without `--upgrade`), the installer
overwrites unchanged engine files and backs up changed ones to `.bak.<sha>`.

## Runtime errors

### `opencode binary not found in PATH`

OpenCode is not installed or not on PATH.

- Install from https://opencode.ai.
- Verify with `opencode --version`.
- If using a non-default install location, add it to PATH.

### `opencode found but --version failed`

The binary exists but is broken (corrupt install, missing dependency). Re-install OpenCode.

### `git not found`

Optional. Only matters if you want to git-init the project. Install from
https://git-scm.com.

### `opencode config not found at <path>`

Book Kit installed fine, but OpenCode doesn't know which model provider to
use. Configure your provider in OpenCode's config (typically
`~/.config/opencode/config.json` on macOS/Linux or
`%APPDATA%\opencode\config.json` on Windows) before launching the pipeline.

### Master doesn't recognize "write a book" intent

Check that `opencode.jsonc` is in the project root and the `master` agent is
configured with `prompt_file: agents_manager/master/SKILL.md`. If you
upgraded OpenCode and the agent roster was wiped, re-run
`python install.py --upgrade`.

### Specialist writes to the wrong path

Each specialist has a `permission: "allow"` policy but a prose-enforced soft
wall. If a specialist went off-rails, check:

1. The dispatch prompt in `share/handoffs/00_user_task_<task-id>.md`.
2. The orchestrator's prompt override (book mode dispatch includes a
   `books/<slug>/**` boundary).
3. The specialist's own SKILL.md for the book-mode note.

If the orchestrator's prompt override is missing, that's a controller bug —
flag it.

### Chapter file is empty / has only the self-critique block

The `book-writer` skill requires the coder to write prose, then append a
self-critique block at the bottom. If only the block appears, the coder
bailed out before writing. Re-dispatch with a stronger prompt naming the
outline promises that must appear.

### Review is failing with "no `chub` citation"

If am-coder wrote against an external library/API/SDK without `chub get`,
am-review is enforcing the rule. Install chub (`npm install -g @aisuite/chub`
or `--with-chub` on a fresh install), then re-dispatch am-coder with the
citation requirement explicit.

## Idempotency / upgrade errors

### Second `python install.py` reports no skips

Check that `manifest.json` made it into the project. If the project's
manifest is missing or out of sync, the installer can't compare hashes.

Fix: re-run with `--upgrade` to refresh everything.

### `--upgrade` clobbered my `books/<slug>/`

Should not happen — `books/` is user-owned. If it did, look for `.bak.*`
files next to the clobbered files; the installer writes backups before
overwriting engine-owned files. Restore from `.bak.*` and report the bug.

### `--uninstall` left `.bak.*` files everywhere

By design — backups are not auto-removed. To clean up:

```sh
find . -name '*.bak.*' -type f -delete     # macOS/Linux
del /s *.bak.*                             # Windows cmd
```

## Smoke test failures

### `installer exit 0 (got 1)`

Run `python install.py --target <test> --no-doctor` manually to see the
full error.

### `engine CLAUDE.md overwritten on --upgrade` fails

The backup write may have failed (read-only filesystem, antivirus block).
Try with `--no-doctor` and inspect `.bak.*` files.

### `user-created books/<slug>/intake.md preserved` fails

Bug in the installer — `_is_protected` should match `books/` as
user-owned. Report with the full smoke test output.

## Still stuck?

1. Run `python scripts/doctor.py` — captures environment state.
2. Run `python install.py --check-only` — verifies manifest integrity.
3. Open an issue at https://github.com/anomalyco/opencode/issues with the
   doctor output and the install command you ran.