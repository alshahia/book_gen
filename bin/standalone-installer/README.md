# Standalone installer (T5)

Self-contained bootstrapper for **agents-manager**. One Python file plus
three tiny shims give you a single `install.sh` / `install.cmd` /
`install.py` that downloads the latest release, extracts it, runs the
bundled installer against your target, and cleans up.

> Re-run this anytime to upgrade. It's safe.

## Files in this directory

| File | Purpose | Style |
|---|---|---|
| `install.py`  | Full Python bootstrap (cross-platform, stdlib only) | LF |
| `install.sh`  | Unix shim → `python3 install.py "$@"`         | LF  |
| `install.cmd` | Windows shim → `python install.py %*`         | CRLF |
| `README.md`   | This file                                   | LF |

## Supported OS matrix

| OS | Python | Invocation | Notes |
|---|---|---|---|
| Windows 10/11 | 3.7+ | `install.cmd` (double-click works) or `python install.py` | needs `python` on PATH (or `py` launcher) |
| macOS 12+     | 3.7+ | `./install.sh` or `python3 install.py`             | bash + python3 in `/usr/bin` is fine |
| Linux (any)   | 3.7+ | `./install.sh` or `python3 install.py`             | Ubuntu 20.04+, Debian 11+, Fedora 34+ ship 3.7+ |

> **Why no native binaries?** One Python file (~250 LOC) covers every OS.
> The two shims (3 lines each) make it double-clickable from Explorer /
> Finder. No Rust, no Go, no per-OS release artifact.

## Usage

```bash
# Default: latest release, install into current directory.
./install.sh                                    # Unix
install.cmd                                     # Windows

# Pin a version.
./install.sh --version v0.10.1
install.cmd --version v0.10.1

# Choose a target and skip confirmations.
./install.sh --target ~/projects/foo --yes
install.cmd --target C:\projects\foo --yes

# Preview only - no actual changes.
./install.sh --dry-run

# Custom repo (fork / staging).
./install.sh --repo myfork/agents-manager --version v0.10.1
```

### Flags

| Flag            | Default                     | Notes |
|-----------------|-----------------------------|-------|
| `--target DIR`  | `.` (CWD)                   | directory to install into; must exist or have writable parent |
| `--version TAG` | `latest`                    | release tag e.g. `v0.10.1`; `latest` queries GitHub Releases |
| `--repo ORG/REPO` | `ahmadmhmdsy/agents-manager` | any GitHub repo with `agents-manager-v*.zip` assets |
| `--git MODE`    | `auto`                      | one of `auto`, `skip`, `prompt` |
| `--skills SCOPE`| `both`                      | one of `global`, `local`, `both`, `skip` |
| `--yes` / `-y`  | off                         | skip the `Proceed?` confirmation |
| `--dry-run`     | off                         | pass `--dry-run` through to the bundled installer |
| `--help`        | -                           | prints usage + banner preview |

## What it does (phases)

0. **Banner** - prints `agents-manager standalone installer` + ASCII rule.
1. **Preflight** - checks Python ≥ 3.7, network reachability
   (HEAD `https://api.github.com`), target writable.
2. **Fetch** - `GET https://api.github.com/repos/<repo>/releases/latest`
   (or `/releases/tags/<v>` for pinned versions).
3. **Download** - streams the matching `agents-manager-vX.Y.Z.zip` asset.
4. **Extract** - unzips to a `tempfile.mkdtemp` staging dir.
5. **Dispatch** - runs the bundled `bin/install.cmd` (Windows) or
   `bin/install.sh` (Unix) with `install <target> --git ... --skills ...`.
6. **Cleanup** - `finally: shutil.rmtree(tmpdir)` even on Ctrl+C.

## Preflight recipes

If something fails, each error prints **one** actionable recipe:

| Symptom | Recipe |
|---|---|
| Python too old | `https://www.python.org/downloads/` |
| No network | check connection, or set `HTTPS_PROXY` |
| 404 on release tag | list tags: `https://github.com/<repo>/releases/tag/<tag>` |
| 403 on API | rate limit — wait a few minutes, or pin `--version` |
| Target not writable | pick a folder with write permission (or a writable parent) |
| Missing `git` | `https://git-scm.com/downloads` (warn, not fatal) |
| Missing `npx` | `https://nodejs.org/` (warn, only matters for global skills) |

## One-liner remote install (curl-pipe)

The shims allow this end-to-end flow:

```bash
# Unix:
curl -fsSL https://raw.githubusercontent.com/ahmadmhmdsy/agents-manager/main/bin/standalone-installer/install.sh | bash

# Windows (PowerShell):
iex (irm https://raw.githubusercontent.com/ahmadmhmdsy/agents-manager/main/bin/standalone-installer/install.cmd)
```

(T4 release-plumbing is responsible for publishing these on GitHub
Releases; this README assumes they exist.)

## Design notes

- **Stdlib only.** `urllib.request`, `zipfile`, `tempfile`, `argparse`,
  `subprocess`. Zero `pip install` required.
- **One error → one recipe.** Every `sys.exit(1)` path prints a single,
  user-actionable fix before exiting. No `traceback`s.
- **Re-run safe.** Idempotent: download → temp → run bundled → delete
  temp. No partial state in `~/.cache/`.
- **No background processes.** All work is synchronous; the user can
  Ctrl+C and the `finally` block cleans the temp dir.

## See also

- `bin/install.py` (T2 in-repo launcher — sibling, ~40 LOC)
- `bin/agents-manager.py` (T2 Python CLI — runs after extraction)
- `share/notes/02_plan_T5_standalone_python.md` (plan)
