# 00 — User task

**Task id**: T-2026-07-01-001
**Date**: 2026-07-01
**Channel**: user → master (orchestration)

## Verbatim user request (final)

> "Approve and execute" (preceded by full plan approval across 4 exchanges: T1 dispatcher + T2 in-repo .cmd + T3 docs + T4 release + T5 standalone installer)

## Locked decisions

1. **Hybrid UX (revised)**: Python becomes the user-facing entry point (CLI + interactive menu). Bash + PowerShell dispatchers stay as the heavy lifting (they already passed shellcheck + PSScriptAnalyzer after T1). Python wraps them via thin shims.

   **Why Python over original cmd + PowerShell plan**: sub-agents struggled to write three shell dialects simultaneously. Python is one dialect, ~600 LOC vs ~860 LOC for the original plan, and the UX (argparse subcommands, interactive menus, prompts) is dramatically cleaner.

2. **Python UX entry points**:
   - `bin/agents-manager.py` — full CLI dispatcher (mirrors `agents-manager.ps1` subcommands: install/update/check/skills/doctor/uninstall/version/help/wizard)
   - `bin/install.py` — convenience launcher with the 5-option menu (calls `agents-manager.py --menu` under the hood; same file, different mode)

3. **Thin shims** (5 LOC each, just `python3 script.py "$@"`):
   - `bin/agents-manager.sh` — Unix
   - `bin/agents-manager.cmd` — Windows
   - `bin/install.sh` — Unix
   - `bin/install.cmd` — Windows
   - `bin/standalone-installer/install.sh` — Unix
   - `bin/standalone-installer/install.cmd` — Windows

4. **Standalone installer**:
   - `bin/standalone-installer/install.py` — Python bootstrap (~250 LOC)
   - Downloads latest release from GitHub API → extracts → runs bundled `install.py install`
   - macOS/Linux/Windows covered by one Python file + tiny shims.

5. **Cross-cutting decisions**:
   - Skills scope override (`--skills {global,local,both,skip}`) is preserved (T1 already added it to both bash + PowerShell dispatchers). Python entry points expose the same flag.
   - Default scope = `both`.
   - Python 3.6+ required (f-strings, type-annotated function signatures).
   - Stdlib only — no third-party deps for the installer.
   - When Python is missing on Windows, installer prints one-line install recipe and exits 1.

6. **README banner**: a single `curl | bash` one-liner is the recommended path for everyone. The `install.cmd` shim is the "double-click for Windows users who don't know PowerShell OR Python" option.

## Scope

In scope (per tracks T1–T5 in master's plan, revised for Python):
- T1 — already done: bash + PowerShell dispatchers gained `--scope` override.
- T2 (revised) — Python UX layer:
  - `bin/agents-manager.py` (~400 LOC) — full CLI dispatcher
  - `bin/install.py` (~80 LOC) — menu launcher (or merge into agents-manager.py with `--menu` flag)
  - `bin/agents-manager.sh` (5 LOC shim)
  - `bin/agents-manager.cmd` (5 LOC shim)
  - `bin/install.sh` (5 LOC shim)
  - `bin/install.cmd` (5 LOC shim)
- T3 — docs:
  - `README.md` Quick install banner (now single one-liner)
  - `bin/README.md` — Python as primary, shims as convenience
  - `docs/INSTALL.md` — Python UX section, install recipe for missing Python
- T4 — release plumbing:
  - `.gitattributes`: `*.cmd text eol=crlf`, `*.bat text eol=crlf`, `*.py text eol=lf` (lf default; shims are the .cmd)
  - `.github/workflows/release.yml`: extend ZIP inclusion check
  - `bin/release-zip.ps1`: parity extension
  - `agents_manager/CHANGELOG.md`: v0.11.0 entry
  - VERSION bump
- T5 — standalone:
  - `bin/standalone-installer/install.py` (~250 LOC Python)
  - `bin/standalone-installer/install.sh` (5 LOC shim)
  - `bin/standalone-installer/install.cmd` (5 LOC shim)
  - `bin/standalone-installer/README.md`

Out of scope:
- Windows CI runner (no native Python linter on Linux runners without `python -m py_compile`).
- Edits to `agents_manager/` controller internals.
- New third-party dependencies.
- Auto-commits (per project convention; explicit ask required).

## Acceptance criteria

1. All dispatcher `--scope` behavior preserved (T1 gates already passed).
2. `python bin/agents-manager.py install . --skills local --yes` → mavis-team copied locally, no npx calls for non-bundled skills.
3. `python bin/agents-manager.py install . --skills both --yes` → matches default behavior (mavis-team local, obra global).
4. `python bin/agents-manager.py --menu` (or `bin/install.py`) → 5-option menu.
5. `bin/install.cmd` (double-click) → menu appears via Python.
6. `bin/agents-manager.cmd install . --yes` → full dispatcher works.
7. Standalone installer downloads the latest release from GitHub API.
8. README banner: `curl -fsSL https://...install.sh | bash` works end-to-end.
9. `python -m py_compile` passes on all .py files (zero syntax errors).
10. shellcheck still passes on `bin/agents-manager` (T1 gate, must not regress).
11. PSScriptAnalyzer still passes on `bin/agents-manager.ps1` (T1 gate, must not regress).

## Risk register

- R1: Python missing on Windows (rare but possible). → standalone + in-repo installer preflight checks and prints one-line install recipe.
- R2: Python version < 3.6 → preflight checks `$PYTHON_VERSION >= (3, 6)`, friendly error.
- R3: Sub-agent cancellation reoccurs → track per-track; if cancelled, master writes summary from on-disk diff (proven pattern from T1).
- R4: `npx` fetch failure for global-level skills when `--scope local` requested → handled by dispatcher (T1 already covers).
- R5: GitHub API rate limit on standalone installer → handled by `--version` pin + clear error.
- R6: User runs install.cmd from a folder with spaces → handled by quoting in shims.

## Source of truth

Master's detailed plan: in conversation history (5 turns: discovery → question → full T1-T4 plan → question → full T1-T5 plan → Option C pivot).

This file is the canonical handoff into the agents_manager pipeline.