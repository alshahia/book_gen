# bin/ — agents-manager scripts

**v0.10.0+ entry point: `agents-manager` (bash) / `agents-manager.ps1` (PowerShell).** All other scripts in this folder (`install.sh`, `install.ps1`, `check.sh`, `check.ps1`, `update.sh`, `update.ps1`) are now thin shims that defer to the unified dispatcher. See [`agents-manager`](#agents-manager-unix--macos--wsl--v0100-) below.

## `agents-manager` (Unix / macOS / WSL) — v0.10.0+

Unified CLI for installing, verifying, updating, and linting an `agents-manager` controller, plus managing required skills (global `~/.agents/skills/<name>/` and controller-local `<target>/.agents/skills/<name>/`).

```bash
agents-manager                                       # interactive wizard
agents-manager install [TARGET] [--git M] [--yes] [--dry-run]
agents-manager update [--check] [--yes]
agents-manager check [TARGET]
agents-manager doctor [TARGET] [--fix]
agents-manager uninstall [TARGET] [--yes]
agents-manager skills list [--required-only|--installed-only|--missing-only]
agents-manager skills add <name>...|--all [--global|--local|--both|--skip] [--yes]
agents-manager skills remove <name> [--yes]
agents-manager skills which <name>
agents-manager skills update <name>...|--all [--yes]
agents-manager release [zip|all] [<args>...]
agents-manager lint [PATH]
agents-manager version
agents-manager help [<subcommand>]
```

Subcommands, in summary:
- `install` — install the controller in a target directory (delegates internally).
- `update` — check for and apply upstream updates (delegates to `update.sh` until the v0.10.x update logic ports).
- `check` — verify the 6 controller files + required skills from `bin/skills-manifest.json`.
- `doctor` — diagnose common issues (controller files, required skills, tooling, git state). `--fix` auto-runs missing installs.
- `uninstall` — remove the 6 controller files from a target directory.
- `skills` — manage required skills:
  - `list [--required-only|--installed-only|--missing-only]` — show status of every skill in the manifest.
  - `add <name|--all>` — run the manifest's `install_cmd` for one or all missing skills. Default scope is `both` (honors per-skill source: global-source skills go to `~/.agents/skills/`, local-source skills go to `<target>/.agents/skills/`). Pass `--global`, `--local`, or `--skip` to override.
  - `remove <name>` — remove a `global` skill (currently obra/superpowers-only).
  - `which <name>` — show where a skill is installed (or "missing" + the install command).
  - `update <name|--all>` — run the manifest's `update_cmd` for one or all global skills.
- `release [zip|all]` — wraps `release-zip.sh` / `release-zip-all.sh`.
- `lint [PATH]` — wraps `lint-design.sh`.
- `version` / `help` — info.

Global flags: `--yes` / `-y` (skip prompts), `--no-color` (disable ANSI colors).

Forwarded flags (e.g. `--git auto`, `--dry-run`) differ by subcommand; see `agents-manager help <subcommand>`.

Backward compatibility: all the legacy `bash bin/install.sh ...` / `.\bin\install.ps1 ...` invocations still work via the shim layer.

## `agents-manager.ps1` (Windows PowerShell + pwsh) — v0.10.0+

PowerShell mirror of `agents-manager`. Same subcommands; PascalCase flags (e.g. `-Git auto`, `-Yes`, `-DryRun`).

```powershell
.\agents-manager.ps1                                    # interactive wizard
.\agents-manager.ps1 install . -Git auto -Yes
.\agents-manager.ps1 doctor . -Fix
.\agents-manager.ps1 skills add -All -Yes
.\agents-manager.ps1 update -Check
.\agents-manager.ps1 help install
```

`skills add` accepts `-Global`, `-Local`, `-Both`, or `-Skip` (default `-Both`); same semantics as the bash `--global/--local/--both/--skip`.

---

## Python UX (v0.11.0+)

Cross-platform wrapper layer on top of the bash / PowerShell dispatchers. Useful when you want a single invocation that works on either platform, an interactive 5-option menu without shell quirks, or a friendlier `--help` / `--version` surface.

### `agents-manager.py` — Python dispatcher

```bash
python3 bin/agents-manager.py install . --yes         # cross-platform install
python3 bin/agents-manager.py doctor . --fix
python3 bin/agents-manager.py skills add --all --yes
python3 bin/agents-manager.py --help
python3 bin/agents-manager.py --menu                  # interactive 5-option menu
python3 bin/agents-manager.py --version
```

Stdlib only (no `pip install`). Parses args + prompts for menu choices, then dispatches to `bin/agents-manager` (Unix) or `bin/agents-manager.ps1` (Windows). All dispatcher logic stays in the bash / PowerShell files — the Python layer is a thin wrapper.

### `install.py` — wizard launcher

```bash
python3 bin/install.py        # prints banner + launches agents-manager.py --menu
python3 bin/install.py --help
```

Tiny launcher (~40 LOC). Its only job is to print a friendly banner and invoke `agents-manager.py --menu` so users can double-click it from Explorer / Finder.

### Shims (cross-platform entry points)

| File | OS | What it does |
|---|---|---|
| `bin/agents-manager.sh` | Unix | shim → `python3 bin/agents-manager.py "$@"` |
| `bin/agents-manager.cmd` | Windows | shim → `python bin/agents-manager.py %*` |
| `bin/install.sh` | Unix | shim → `python3 bin/install.py` |
| `bin/install.cmd` | Windows | shim → `python bin/install.py` |

The `.sh` / `.cmd` shims let users invoke `agents-manager` or `install` from `bin/` regardless of OS, picking the right Python interpreter automatically. All four are 1–3 lines and defer entirely to the Python files.

### `skills add` scope flag (v0.11.0+)

| Flag (bash / PowerShell) | Meaning |
|---|---|
| `--global` / `-Global` | install to `~/.agents/skills/<name>/` (user-level, via `npx`) |
| `--local` / `-Local` | install to `<target>/.agents/skills/<name>/` (project-local) |
| `--both` / `-Both` (default) | honor per-skill source: global-source skills → `~/.agents/`, local-source skills → `<target>/.agents/` |
| `--skip` / `-Skip` | skip skills entirely (controller install only) |

Default `both` matches v0.10.0's implicit behavior — no breaking change for existing users. The interactive wizard prompts for scope before running `cmd_skills add --all`.

---

## Standalone installer — v0.11.0+

A self-contained bootstrapper in `bin/standalone-installer/` for users who don't already have a local checkout. Downloads the latest release ZIP, extracts it, runs the bundled installer against the target, and cleans up — all in one command. Cross-platform, stdlib only.

| File | OS | What it does |
|---|---|---|
| `bin/standalone-installer/install.py` | any | full bootstrap (~250 LOC, stdlib only) |
| `bin/standalone-installer/install.sh` | Unix | shim → `python3 install.py "$@"` |
| `bin/standalone-installer/install.cmd` | Windows | shim → `python install.py %*` |

Quick usage (see [`bin/standalone-installer/README.md`](standalone-installer/README.md) for the full flag set):

```bash
# Default: latest release, install into current directory
./bin/standalone-installer/install.sh            # Unix
.\bin\standalone-installer\install.cmd           # Windows (double-click works)

# Pin a version + target + scope
./bin/standalone-installer/install.sh --version v0.11.0 --target ~/projects/foo --skills both --yes

# One-liner remote install (curl-pipe)
curl -fsSL https://raw.githubusercontent.com/ahmadmhmdsy/agents-manager/main/bin/standalone-installer/install.sh | bash
```

Flags: `--target DIR`, `--version TAG`, `--repo ORG/REPO`, `--git MODE`, `--skills SCOPE`, `--yes`, `--dry-run`, `--help`.

---

# Legacy shims (v0.9.x compat — all defer to `agents-manager`)

## `install.sh` (Unix / macOS / WSL) — shim

```bash
bash bin/install.sh [TARGET] [--dry-run] [--uninstall] [--yes] [--git <auto|prompt|skip>]
```

- `TARGET` — path to the project where the controller should be installed. Defaults to `.` (current directory).
- `--dry-run` — print what would change without writing anything.
- `--uninstall` — remove the controller files from `TARGET` (with confirmation prompt unless `--yes`).
- `--git <auto|prompt|skip>` — how to handle git init when `TARGET` is not yet a git repo. Default `auto` (zero-knowledge friendly): runs `git init` + initial commit automatically. `prompt` asks Y/n. `skip` never touches git. See [`docs/INSTALL.md`](../docs/INSTALL.md) § Git initialization.

Copies 2 files + 4 directories from the agents-manager checkout into `TARGET`:

- `opencode.jsonc`
- `CLAUDE.md`
- `agents_manager/`
- `share/`
- `tasks/`
- `.agents/skills/mavis-team/`

Existing files are **skipped** (not overwritten). Re-running is safe. After install, the script also writes a starter `.gitignore` in `TARGET` if one isn't present, with sensible entries for secrets and runtime artifacts. If `--git auto` (default) and `TARGET` isn't already a git repo, the script also runs `git init` + an initial commit (skipped silently if the `git` CLI isn't on `PATH`).

## `install.ps1` (Windows PowerShell 5.1+ and 7+)

```powershell
.\bin\install.ps1 [-Target <path>] [-DryRun] [-Uninstall] [-Yes] [-Git <auto|prompt|skip>]
```

Same flags as the bash version, but with PowerShell's standard `-DryRun` / `-Uninstall` / `-Yes` (PascalCase) naming. `-Git` accepts `auto`, `prompt`, or `skip`; default is `auto` (zero-knowledge friendly).

## `check.sh` (Unix / macOS / WSL)

```bash
bash bin/check.sh [TARGET]
```

Verifies that:

- All 6 controller files exist at `TARGET`
- All 9 required user-level skills are installed in `~/.agents/skills/`

Prints `OK` / `MISS` for each. Exits non-zero if anything is missing. Lists the `npx skills add` command for any missing skill.

## `check.ps1` (Windows PowerShell)

```powershell
.\bin\check.ps1 [-Target <path>]
```

Same checks, PowerShell-flavoured output.

## `update.sh` (Unix / macOS / WSL)

```bash
bash bin/update.sh [--check] [--yes|-y] [--from <ver>] [--target <ver>]
```

Fetches the latest `agents-manager` release from GitHub, compares to your installed version (read from `agents_manager/CHANGELOG.md`), and applies the upgrade by overwriting the 6 controller paths after backing up your current install.

- `--check` — print local vs. remote version + the new CHANGELOG excerpt. Exit 0 if up-to-date, exit 1 if a newer version exists, exit 2 on network error.
- `--yes`, `-y` — apply the upgrade without prompting (for CI / scripted use).
- `--from <ver>` — override the local version detection (useful after partial upgrades).
- `--target <ver>` — pin to a specific version instead of "latest".

Default behavior: print version info, show what will change, prompt `[yes/no]`. On yes: creates `.agents-manager-backup-<timestamp>/`, downloads the release ZIP, extracts the 6 paths, runs `bin/check.sh`, prints what changed.

## `update.ps1` (Windows PowerShell)

```powershell
.\bin\update.ps1 [-Check] [-Yes] [-From <ver>] [-Target <ver>]
```

PowerShell parity. Same flags (`-Check` / `-Yes` PascalCase).

## `lint-design.sh` (Unix / macOS / WSL) — v0.9.0+

```bash
bash bin/lint-design.sh [PATH]
```

Advisory linter for `am-design` output. Flags two things in mockup HTML:

- Inline hex color codes outside `:root` and `[data-theme]` blocks (so design tokens stay centralized)
- Emoji (so copy decks can grep cleanly)

Default path is `examples/`. Exits `0` if clean, `1` if violations found, `2` if path doesn't exist. **Does not block CI** — `lint-design` CI job is advisory only.

PowerShell parity is not shipped (advisory linters rarely need Windows). If you want it, the script is bash-only and 99 lines; port if needed.

## `release-zip.sh` (Unix / macOS / WSL) — maintainer only

```bash
bash bin/release-zip.sh <tag> [--out <path>]
```

Builds `agents-manager-vX.Y.Z.zip` from a git tag's tree using `git archive`. Includes only the 7 paths that ship in a release: `opencode.jsonc`, `CLAUDE.md`, `agents_manager/`, `share/`, `tasks/`, `.agents/skills/mavis-team/`, `bin/` (bin/ is included so Option B / "download a ZIP" users can run the installer from the extracted folder).

After build, validates the ZIP contains all expected paths and the two installer scripts. Exits non-zero with a clear message if anything is missing.

Most users won't run this manually — `.github/workflows/release.yml` runs it on every `v*` tag push. Use this script when:

- Backfilling releases for old tags (`bin/release-zip-all.sh` for that)
- Validating locally before pushing a tag
- Building a ZIP for an offline install (e.g. air-gapped environment)

## `release-zip.ps1` (Windows PowerShell) — maintainer only

```powershell
.\bin\release-zip.ps1 -Tag <tag> [-Out <path>]
```

PowerShell mirror of `release-zip.sh`. Uses `[System.IO.Compression.ZipFile]` (built into .NET — no external `zip` CLI needed). Same validation logic. Requires Git for Windows' `bash.exe` on PATH for the `git archive | tar -x` step.

## `release-zip-all.sh` (Unix / macOS / WSL) — maintainer only

```bash
bash bin/release-zip-all.sh [--out <dir>]
```

Loop helper. Builds ZIPs into `<out>` (default `./dist/`) for **every** local `v*` tag. Prints a per-tag summary. Used for the one-time backfill that created all the historical GitHub Releases.

Does **not** call `gh release create` — pair it with a separate loop for that:

```bash
for tag in $(git tag -l 'v*' --sort=v:refname); do
  gh release create "$tag" \
    --title "$tag" \
    --notes-file <(extract_changelog_entry "$tag") \
    --target "$(git rev-parse "$tag")" \
    "dist/agents-manager-${tag}.zip"
done
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success (all OK) |
| 1 | sanity check failed (target missing, source not an agents-manager checkout, etc.) |
| 2 | some controller files / skills missing (check script) or newer version available (update --check) |
| 3 | user declined confirmation (--uninstall, update prompt) |
| 4 | network error during update (GitHub unreachable, ZIP malformed) |
| 5 | active pipeline detected (update refused to avoid mid-pipeline corruption) |

## What these scripts do NOT do

- They do **not** install the 9 required user-level skills (run `npx skills add` manually — see `README.md`).
- They do **not** modify `opencode.jsonc` permission globs for nested installs. agents-manager installs at the project root only.
- They do **not** delete user-modified files. Existing controller files are **skipped** to protect your edits (unless `update.sh` is overwriting them, in which case a backup is created first).
- `update.sh` does **not** touch user-level skills (`~/.agents/skills/`). It only updates the 6 controller paths. Run `npx skills add` for any new skill requirements after upgrading.