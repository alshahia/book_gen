#!/usr/bin/env python3
"""agents-manager CLI — Python UX layer.

Wraps the bash (Unix) and PowerShell (Windows) dispatchers.
This file: parses args, prompts, runs preflight. The dispatcher
handles file copies, manifest parsing, npx skill installs.

Stdlib only.  The bash + PowerShell dispatchers stay unchanged.
"""

import argparse
import platform
import subprocess
import sys
from pathlib import Path

VERSION = "0.11.0"
BIN_DIR = Path(__file__).parent.resolve()

IS_WINDOWS = platform.system() == "Windows"


# ────────────────────────── preflight ──────────────────────────


def check_python_version() -> None:
    if sys.version_info < (3, 7):
        sys.stderr.write(
            f"Python 3.7+ is required (you have {sys.version_info.major}."
            f"{sys.version_info.minor}).\n"
            "Install Python: https://www.python.org/downloads/\n"
        )
        sys.exit(1)


def check_dispatcher_exists() -> None:
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
    args = [str(a) for a in args]
    if IS_WINDOWS:
        dispatcher = BIN_DIR / "agents-manager.ps1"
        cmd = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(dispatcher),
        ] + args
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
    return line if line else (default or "")


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
        if not name:
            print("Cancelled (no skill name given).")
            return 0
        return dispatch(["skills", "remove", name, "--yes"])
    if sub == "update":
        return dispatch(["skills", "update", "--all", "--yes"])
    return 0


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
        if choice_str.lower() in ("q", "quit"):
            return 0
        if choice_str in actions:
            label, fn = actions[choice_str]
            print(f"\n-> {label}\n")
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
        description="agents-manager -- controller installer (Python UX layer)")
    p.add_argument("--version", action="version",
                   version=f"agents-manager {VERSION}")
    p.add_argument("--menu", action="store_true",
                   help="launch interactive menu")
    sub = p.add_subparsers(dest="command")

    # install
    p_install = sub.add_parser("install", help="install controller in a project")
    p_install.add_argument("target", nargs="?", default=".")
    p_install.add_argument("--git", choices=["auto", "skip", "prompt"],
                           default="auto")
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
    p_skills.add_argument("subcommand",
                          choices=["list", "add", "remove", "which", "update"])
    p_skills.add_argument("names", nargs="*")
    p_skills.add_argument("--all", action="store_true")
    p_skills.add_argument("--global", dest="scope",
                          action="store_const", const="global")
    p_skills.add_argument("--local",  dest="scope",
                          action="store_const", const="local")
    p_skills.add_argument("--both",   dest="scope",
                          action="store_const", const="both")
    p_skills.add_argument("--skip",   dest="scope",
                          action="store_const", const="skip")
    # --skills/--scope: takes a value (alias for --global|--local|--both|--skip)
    p_skills.add_argument("--skills", "--scope", dest="scope",
                          choices=["both", "global", "local", "skip"],
                          help="scope alias: both|global|local|skip")
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

    # version (subcommand form; --version flag also works)
    sub.add_parser("version", help="print version + manifest info")

    # help (subcommand form; --help flag also works)
    p_help = sub.add_parser("help", help="show full help")
    p_help.add_argument("topic", nargs="*",
                        help="optional subcommand to get help for")

    return p


# ────────────────────────── main ──────────────────────────


def main():
    check_python_version()
    check_dispatcher_exists()
    parser = build_parser()

    # No args → interactive menu.
    if len(sys.argv) == 1:
        return interactive_menu()

    args = parser.parse_args()

    # --menu or no subcommand → interactive menu.
    if args.command is None or getattr(args, "menu", False):
        return interactive_menu()

    # version / help subcommand → just dispatch to the underlying dispatcher
    # so it can print the canonical (and colorized) version / help text.
    if args.command == "version":
        return dispatch(["version"])
    if args.command == "help":
        topic = getattr(args, "topic", []) or []
        return dispatch(["help"] + list(topic))

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
