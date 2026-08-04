# Book Kit

A portable, cross-platform ZIP that turns any folder on any laptop into a
long-form book-writing environment powered by OpenCode + the agents-manager
multi-agent pipeline.

Drop `book-kit-<version>.zip` into a project, unzip, run one command, open
OpenCode, say "write a book about X" — same 7-phase pipeline that produced
`books/daily-focus/ch-01.md` in this repo.

## Quick start (60 seconds)

```sh
# 1. Unzip into your project (any folder on any OS)
unzip book-kit-0.1.0.zip -d my-book-project
cd my-book-project

# 2. Install (Python 3.8+, stdlib only — no pip, no npm)
python install.py                # macOS / Linux
#   or, on Windows:
install.bat                       # kit-root convenience wrapper
bin\install-book-kit.bat          # same flow, callable from anywhere

# 3. Launch OpenCode and say "write a book about productivity"
opencode
# > write a book about productivity
```

When run from inside the unzipped kit, `install.py` detects that the kit
files are already at the target and runs in **install-in-place mode**:
skips the file-copy phase, verifies each file's SHA against the manifest,
and continues with workspace dirs + the `.book-kit-version` marker + doctor
preflight. Use `--copy-anyway` to force the original copy-onto-self
behavior; use `--upgrade` to refresh engine files across kit versions.

The installer is idempotent, dry-run-able (`--check-only`), and reversable
(`--uninstall`). See `docs/QUICKSTART.md` for the full walkthrough.

## What's in the kit

| Path | Purpose |
|---|---|
| `install.py` | Cross-platform Python installer (stdlib only) |
| `opencode.jsonc` | Minimal agent roster: master + 5 specialists |
| `CLAUDE.md` | Project orientation for OpenCode sessions |
| `agents_manager/` | 7 engine skills: orchestrator, writer, master, 5 specialists |
| `book_workflow/book-agents/templates/` | 9 book-phase templates (intake, outline, etc.) |
| `books/` | Workspace seed — your manuscripts live here |
| `share/` | Inter-agent communication (`notes/`, `handoffs/`, `reports/`) |
| `tasks/` | Task tracker files |
| `scripts/` | `doctor.py`, `build_manifest.py`, `build_zip.py`, `smoke_test.py` |
| `bin/` | `book-kit` (bash), `book-kit.cmd` (Windows) wrappers |
| `docs/` | QUICKSTART, ARCHITECTURE, TROUBLESHOOTING, UPGRADE |
| `manifest.json` | File allowlist + SHA-256 checksums |

## What's intentionally NOT in the kit

- Full `agents-manager` controller (only book-relevant skills ship)
- `am-assets`, `am-investigate`, `am-ship`, `am-health` (never dispatched in book mode)
- OpenCode binary, MCP servers, `chub`, model credentials
- Git history

See `docs/ARCHITECTURE.md` for the design rationale and `docs/UPGRADE.md` for
how to refresh an existing install.

## Building the ZIP from source

```sh
python scripts/build_manifest.py    # regenerate manifest.json + checksums
python scripts/build_zip.py         # produce dist/book-kit-<version>.zip
```

## License

MIT — same as the parent repo.