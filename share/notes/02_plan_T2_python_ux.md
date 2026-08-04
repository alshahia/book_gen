# Plan: Python UX layer (Track T2 — REVISED for Option C)

**Task**: T-2026-07-01-001.B
**Track**: T2 of T-2026-07-01-001 (revised: Python instead of cmd.exe)
**Master's task tracker**: `tasks/T-2026-07-01-001.md`
**Decision**: Option C — Python UX, keep bash + PowerShell dispatchers

## Goal

Add a Python UX layer that wraps the existing `bin/agents-manager` (bash) and `bin/agents-manager.ps1` (PowerShell) dispatchers. Python handles:

- Argument parsing (subcommands + flags)
- Interactive 5-option menu
- Prompts with default values
- Pre-flight checks (Python version, target dir writable)
- Pass-through dispatch to the right dispatcher based on OS

The bash + PowerShell dispatchers stay unchanged (T1 work is preserved).

## Files to create

| File | LOC | Purpose |
|---|---|---|
| `bin/agents-manager.py` | ~400 | Full CLI dispatcher (mirrors `agents-manager.ps1` subcommands) |
| `bin/install.py` | ~80 | Convenience launcher: runs `agents-manager.py --menu` + prints banner |
| `bin/agents-manager.sh` | 5 | Unix shim → `python3 bin/agents-manager.py "$@"` |
| `bin/agents-manager.cmd` | 5 | Windows shim → `python bin\agents-manager.py %*` |
| `bin/install.sh` | 5 | Unix shim → `python3 bin/install.py "$@"` |
| `bin/install.cmd` | 5 | Windows shim → `python bin\install.py %*` |

Total: ~500 LOC of which ~80 are shims.

## Files NOT to edit (this track)

- `bin/agents-manager` (T1 done, unchanged)
- `bin/agents-manager.ps1` (T1 done, unchanged)
- `bin/standalone-installer/**` (Track T5)
- `README.md`, `bin/README.md`, `docs/INSTALL.md` (Track T3)
- `.gitattributes`, release workflow, CHANGELOG, version bump (Track T4)

## Architecture

```
┌─────────────────────────────────────┐
│  bin/install.cmd (or .sh) shim      │   <- 5 LOC
│  ↓ python install.py                │
├─────────────────────────────────────┤
│  bin/install.py                     │   <- 80 LOC launcher
│  • ASCII banner                     │
│  • If --menu flag → menu()          │
│  • Else → run agents-manager.py    │
├─────────────────────────────────────┤
│  bin/agents-manager.py              │   <- 400 LOC dispatcher CLI
│  • argparse subcommands:            │
│    install, update, check, skills,  │
│    doctor, uninstall, version, help │
│  • Interactive --menu mode          │
│  • Prompts with defaults            │
│  • Preflight: Python 3.6+,          │
│    target dir writable              │
│  • Dispatch to OS-specific:         │
│    Windows → agents-manager.ps1     │
│    Unix    → agents-manager         │
└─────────────────────────────────────┘
```

## `bin/agents-manager.py` design

```python
#!/usr/bin/env python3
"""agents-manager CLI — Python UX layer.

Wraps the bash (Unix) and PowerShell (Windows) dispatchers.
This file: parses args, prompts, runs preflight. The dispatcher
handles file copies, manifest parsing, npx skill installs.
"""
import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

VERSION = "0.11.0"
BIN_DIR = Path(__file__).parent.resolve()
SRC_DIR = BIN_DIR.parent
SCRIPT_DIR = BIN_DIR

IS_WINDOWS = platform.system() == "Windows"

# ────────────────────────── preflight ──────────────────────────

def check_python_version():
    if sys.version_info < (3, 6):
        sys.stderr.write(
            f"Python 3.6+ is required (you have {sys.version_info.major}."
            f"{sys.version_info.minor}).\n"
            "Install Python: https://www.python.org/downloads/\n"
        )
        sys.exit(1)

def check_dispatcher_exists():
    if IS_WINDOWS:
        d = BIN_DIR / "agents-manager.ps1"
    else:
        d = BIN_DIR / "agents-manager"
    if not d.exists():
        sys.stderr.write(
            f"Dispatcher not found: {d}\n"
            "Re-install agents-manager or check bin/ directory.\n"
        )
        sys.exit(1)

# ────────────────────────── dispatch ──────────────────────────

def dispatch(args):
    """Run the bash or PowerShell dispatcher with the given arg list."""
    if IS_WINDOWS:
        dispatcher = BIN_DIR / "agents-manager.ps1"
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
               "-File", str(dispatcher)] + args
    else:
        dispatcher = BIN_DIR / "agents-manager"
        cmd = [str(dispatcher)] + args
    print(f"$ {' '.join(cmd)}")
    return subprocess.call(cmd)

# ────────────────────────── prompts ──────────────────────────

def prompt(message, default=None):
    suffix = f" [{default}]" if default is not None else ""
    sys.stdout.write(f"{message}{suffix}: ")
    sys.stdout.flush()
    try:
        line = input()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(130)
    line = line.strip()
    return line if line else default

def confirm(message, default=True):
    suffix = " [Y/n]" if default else " [y/N]"
    while True:
        sys.stdout.write(f"{message}{suffix}: ")
        sys.stdout.flush()
        try:
            line = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(130)
        if not line:
            return default
        if line in ("y", "yes"):
            return True
        if line in ("n", "no"):
            return False

def choice(message, options, default=None):
    """Pick one of N options by number or exact text match."""
    print(f"{message}:")
    for i, opt in enumerate(options, 1):
        marker = " (default)" if default and opt == default else ""
        print(f"  {i}) {opt}{marker}")
    while True:
        sys.stdout.write(f"Choice [1-{len(options)}]: ")
        sys.stdout.flush()
        try:
            line = input().strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(130)
        if not line and default is not None:
            return default
        try:
            idx = int(line)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        except ValueError:
            if line in options:
                return line
        print(f"Please enter a number 1-{len(options)} or one of: {', '.join(options)}")

# ────────────────────────── menu ──────────────────────────

BANNER = """
================================================
  agents-manager {ver}
================================================

Pick an action:
  1) Install the controller in a project
  2) Update an existing install
  3) Check / verify an install
  4) Manage skills (list / add / remove / update)
  5) Uninstall the controller
  Q) Quit
"""

def menu_install():
    target = prompt("Target directory", default=".")
    git_mode = choice("Git mode (init if missing)",
                      ["auto", "skip", "prompt"], default="auto")
    scope = choice("Skill installation scope",
                   ["both", "global", "local", "skip"], default="both")
    if confirm("Dry-run preview first?", default=False):
        rc = dispatch(["install", target, "--git", git_mode,
                       "--skills", scope, "--dry-run", "--yes"])
        if rc != 0:
            return rc
    if not confirm(f"Install agents-manager into {target}?", default=True):
        print("Cancelled.")
        return 0
    return dispatch(["install", target, "--git", git_mode,
                     "--skills", scope, "--yes"])

def menu_update():
    if confirm("Check for updates first (no install)?", default=True):
        rc = dispatch(["update", "--check"])
        if rc != 0:
            return rc
        if not confirm("Apply the update?", default=True):
            return 0
    return dispatch(["update", "--yes"])

def menu_check():
    target = prompt("Target directory to check", default=".")
    return dispatch(["check", target])

def menu_skills():
    sub = choice("Skills action",
                 ["list", "add", "remove", "update", "back"],
                 default="list")
    if sub == "back":
        return 0
    if sub == "list":
        return dispatch(["skills", "list"])
    if sub == "add":
        scope = choice("Scope",
                       ["both", "global", "local", "skip"],
                       default="both")
        return dispatch(["skills", "add", "--all", f"--{scope}", "--yes"])
    if sub == "remove":
        name = prompt("Skill name to remove")
        return dispatch(["skills", "remove", name, "--yes"])
    if sub == "update":
        return dispatch(["skills", "update", "--all", "--yes"])

def menu_uninstall():
    target = prompt("Target directory to uninstall", default=".")
    if not confirm(f"Uninstall agents-manager from {target}?", default=False):
        print("Cancelled.")
        return 0
    return dispatch(["uninstall", target, "--yes"])

def interactive_menu():
    print(BANNER.format(ver=VERSION))
    actions = {
        "1": ("Install", menu_install),
        "2": ("Update", menu_update),
        "3": ("Check", menu_check),
        "4": ("Skills", menu_skills),
        "5": ("Uninstall", menu_uninstall),
    }
    while True:
        choice_str = prompt("Choice [1-5 / Q]", default="1")
        if choice_str.lower() in ("q", "quit", ""):
            return 0
        if choice_str in actions:
            label, fn = actions[choice_str]
            print(f"\n→ {label}\n")
            rc = fn()
            if rc != 0:
                print(f"\n(Step exited with code {rc})")
            print()
            if not confirm("Return to menu?", default=True):
                return rc
        else:
            print(f"Invalid choice: {choice_str}")

# ────────────────────────── argparse ──────────────────────────

def build_parser():
    p = argparse.ArgumentParser(
        prog="agents-manager.py",
        description="agents-manager — controller installer (Python UX layer)")
    p.add_argument("--version", action="version", version=f"agents-manager {VERSION}")
    p.add_argument("--menu", action="store_true",
                   help="launch interactive menu")
    sub = p.add_subparsers(dest="command")

    # install
    p_install = sub.add_parser("install", help="install controller in a project")
    p_install.add_argument("target", nargs="?", default=".")
    p_install.add_argument("--git", choices=["auto", "skip", "prompt"], default="auto")
    p_install.add_argument("--skills", "--scope",
                           choices=["both", "global", "local", "skip"],
                           default="both")
    p_install.add_argument("--dry-run", action="store_true")
    p_install.add_argument("--yes", "-y", action="store_true")

    # update
    p_update = sub.add_parser("update", help="update existing install")
    p_update.add_argument("--check", action="store_true")
    p_update.add_argument("--yes", "-y", action="store_true")

    # check
    p_check = sub.add_parser("check", help="verify an install")
    p_check.add_argument("target", nargs="?", default=".")

    # skills
    p_skills = sub.add_parser("skills", help="manage skills")
    p_skills.add_argument("subcommand", choices=["list", "add", "remove", "which", "update"])
    p_skills.add_argument("names", nargs="*")
    p_skills.add_argument("--all", action="store_true")
    p_skills.add_argument("--global", dest="scope", action="store_const", const="global")
    p_skills.add_argument("--local",  dest="scope", action="store_const", const="local")
    p_skills.add_argument("--both",   dest="scope", action="store_const", const="both")
    p_skills.add_argument("--skip",   dest="scope", action="store_const", const="skip")
    p_skills.add_argument("--yes", "-y", action="store_true")

    # doctor
    p_doctor = sub.add_parser("doctor", help="diagnose + fix issues")
    p_doctor.add_argument("target", nargs="?", default=".")
    p_doctor.add_argument("--fix", action="store_true")
    p_doctor.add_argument("--yes", "-y", action="store_true")

    # uninstall
    p_uninst = sub.add_parser("uninstall", help="remove controller")
    p_uninst.add_argument("target", nargs="?", default=".")
    p_uninst.add_argument("--yes", "-y", action="store_true")

    return p

# ────────────────────────── main ──────────────────────────

def main():
    check_python_version()
    check_dispatcher_exists()
    parser = build_parser()

    # If no args, launch menu.
    if len(sys.argv) == 1:
        return interactive_menu()

    args = parser.parse_args()

    if args.command is None or getattr(args, "menu", False):
        return interactive_menu()

    # Translate Python flags to dispatcher flags.
    dispatch_args = [args.command]
    if args.command == "install":
        dispatch_args += [args.target, "--git", args.git,
                          "--skills", args.skills]
        if args.dry_run:
            dispatch_args.append("--dry-run")
        if args.yes:
            dispatch_args.append("--yes")

    elif args.command == "update":
        if args.check:
            dispatch_args.append("--check")
        if args.yes:
            dispatch_args.append("--yes")

    elif args.command == "check":
        dispatch_args.append(args.target)

    elif args.command == "skills":
        dispatch_args.append(args.subcommand)
        dispatch_args += args.names
        if args.all:
            dispatch_args.append("--all")
        if args.scope:
            dispatch_args.append(f"--{args.scope}")
        if args.yes:
            dispatch_args.append("--yes")

    elif args.command == "doctor":
        dispatch_args.append(args.target)
        if args.fix:
            dispatch_args.append("--fix")
        if args.yes:
            dispatch_args.append("--yes")

    elif args.command == "uninstall":
        dispatch_args.append(args.target)
        if args.yes:
            dispatch_args.append("--yes")

    return dispatch(dispatch_args)

if __name__ == "__main__":
    sys.exit(main() or 0)
```

## `bin/install.py` design (80 LOC)

```python
#!/usr/bin/env python3
"""install.py — Convenience launcher for the in-repo installer.

This file is intentionally tiny. Its only jobs:
  1. Print a friendly banner.
  2. Launch agents-manager.py (same dir).
"""
import sys
from pathlib import Path

BIN_DIR = Path(__file__).parent.resolve()
AM_PY = BIN_DIR / "agents-manager.py"

BANNER = """
================================================
  agents-manager installer
================================================

This launcher runs the Python UX layer (agents-manager.py)
which in turn calls the bash or PowerShell dispatcher.
"""

def main():
    print(BANNER)
    if not AM_PY.exists():
        sys.stderr.write(f"agents-manager.py not found next to install.py ({BIN_DIR})\n")
        return 1
    # Inject "--menu" so the user gets the 5-option menu.
    sys.argv = [str(AM_PY), "--menu"] + sys.argv[1:]
    sys.path.insert(0, str(BIN_DIR))
    # Import and run agents-manager.py's main()
    import importlib.util
    spec = importlib.util.spec_from_file_location("agents_manager_py", AM_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.main() or 0

if __name__ == "__main__":
    sys.exit(main())
```

## Shim files

### `bin/agents-manager.sh` (5 LOC, LF)

```bash
#!/usr/bin/env bash
# agents-manager CLI shim (Unix) — defers to Python
exec python3 "$(dirname "${BASH_SOURCE[0]}")/agents-manager.py" "$@"
```

### `bin/agents-manager.cmd` (5 LOC, CRLF)

```bat
@echo off
REM agents-manager CLI shim (Windows) — defers to Python
python "%~dp0agents-manager.py" %*
exit /b %errorlevel%
```

### `bin/install.sh` (5 LOC, LF)

```bash
#!/usr/bin/env bash
# agents-manager installer shim (Unix) — defers to Python
exec python3 "$(dirname "${BASH_SOURCE[0]}")/install.py" "$@"
```

### `bin/install.cmd` (5 LOC, CRLF)

```bat
@echo off
REM agents-manager installer shim (Windows) — defers to Python
python "%~dp0install.py" %*
exit /b %errorlevel%
```

## Acceptance criteria (this track)

1. `python3 bin/agents-manager.py --version` → prints `agents-manager 0.11.0`.
2. `python3 bin/agents-manager.py` (no args) → interactive menu.
3. `python3 bin/agents-manager.py install . --skills local --yes` → shells to bash or PowerShell dispatcher with correct args.
4. `python3 bin/agents-manager.py skills list` → runs dispatcher.
5. `bin/install.sh` (Unix) → launches Python installer with menu.
6. `bin/install.cmd` (Windows, double-click) → launches Python installer with menu.
7. `python3 bin/install.py` → same as `python3 bin/agents-manager.py --menu`.
8. `python -m py_compile bin/agents-manager.py bin/install.py` → exits 0.
9. Existing `bin/agents-manager` and `bin/agents-manager.ps1` unchanged; T1 gates still pass.
10. Path with spaces in TARGET arg → handled by `shlex.quote` or manual quoting in dispatcher's argv list (no shell interpolation in `subprocess.call(cmd)`).

## Edge cases to handle

- Python 3.6 missing → preflight prints install recipe, exits 1.
- Python launcher on Windows (`py` vs `python`) → check `python` first, fall back to `py` if `python` not found.
- Target dir doesn't exist → prompt to create; user accepts → `Path(target).mkdir(parents=True)` (note: dispatcher will also handle).
- Target dir is a file → error before dispatching.
- User sends `Ctrl+C` during a prompt → `KeyboardInterrupt` → exit 130.
- Dispatcher exits non-zero → `dispatch()` returns that code; Python exits with it.

## Quality gates

```bash
# Python syntax:
python3 -m py_compile bin/agents-manager.py bin/install.py

# Optional (Python stdlib):
python3 -m unittest discover -s tests/

# Regression — bash dispatcher still lints:
shellcheck bin/agents-manager

# Regression — PowerShell dispatcher still lints:
pwsh -NoProfile -Command "Invoke-ScriptAnalyzer -Path bin/agents-manager.ps1 -Severity Warning,Error"
```

## Output (am-coder must produce)

1. The 6 new files written to `bin/`.
2. `share/notes/03_coder_summary_T-2026-07-01-001_B.md` with:
   - Tasks attempted table (B.1-B.6)
   - Files written (path + LOC)
   - py_compile output + smoke test results
   - Deviations from plan
   - Self-critique

## Reference (read before editing)

- `bin/agents-manager.ps1` — subcommand + flag shape to mirror
- `bin/agents-manager` (bash) — flag equivalence table
- T1 changes in both dispatchers: `--skills|--scope` already wired (don't duplicate)