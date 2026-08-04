#!/usr/bin/env python3
"""Preflight checks for the Book Kit installer.

Verifies the target environment can host the 7-phase book-gen pipeline.
Exit code 0 = all checks pass; 1 = at least one check failed (with a
single-line remediation hint per failure).

Stdlib only. Run from the unzipped kit: python scripts/doctor.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _ok(msg: str) -> None:
    print(f"  [OK]   {msg}")


def _warn(msg: str) -> None:
    print(f"  [WARN] {msg}")


def _fail(msg: str, hint: str) -> None:
    print(f"  [FAIL] {msg}")
    print(f"         hint: {hint}")


def check_python() -> bool:
    v = sys.version_info
    if (v.major, v.minor) >= (3, 8):
        _ok(f"Python {v.major}.{v.minor}.{v.micro}")
        return True
    _fail(
        f"Python {v.major}.{v.minor} detected",
        "install Python 3.8+ from https://python.org",
    )
    return False


def check_opencode() -> bool:
    if shutil.which("opencode") is None:
        _warn("opencode binary not found in PATH")
        _warn(
            "Book Kit requires OpenCode to launch agents; install it from "
            "https://opencode.ai before running the pipeline"
        )
        return True  # non-fatal — installer can still lay down files
    try:
        out = subprocess.run(
            ["opencode", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode == 0:
            version = (out.stdout or out.stderr).strip().splitlines()[0]
            _ok(f"opencode: {version}")
        else:
            _warn("opencode found but --version failed; will still try to install")
    except (subprocess.TimeoutExpired, OSError) as e:
        _warn(f"opencode probe error: {e}")
    return True


def check_git() -> bool:
    if shutil.which("git") is None:
        _warn("git not found — optional, only needed if you git-init the project")
        return True
    try:
        out = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode == 0:
            _ok((out.stdout or out.stderr).strip())
        else:
            _warn("git found but --version failed")
    except (subprocess.TimeoutExpired, OSError) as e:
        _warn(f"git probe error: {e}")
    return True


def check_write(target: Path) -> bool:
    try:
        target.mkdir(parents=True, exist_ok=True)
        probe = target / ".book-kit-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        _ok(f"write permission on {target}")
        return True
    except OSError as e:
        _fail(
            f"cannot write to {target}: {e}",
            "check folder permissions; on Windows, run as Administrator or pick a writable folder",
        )
        return False


def check_disk(target: Path) -> bool:
    try:
        usage = shutil.disk_usage(target)
        free_mb = usage.free // (1024 * 1024)
        if free_mb >= 200:
            _ok(f"disk space: {free_mb} MB free")
            return True
        _fail(
            f"only {free_mb} MB free on the target volume",
            "free up at least 200 MB; Book Kit + first book artifacts need ~50-100 MB",
        )
        return False
    except OSError as e:
        _warn(f"disk usage probe failed: {e}")
        return True


def check_existing_kit(target: Path) -> bool:
    manifest = target / "manifest.json"
    if manifest.exists():
        try:
            import json
            m = json.loads(manifest.read_text(encoding="utf-8"))
            version = m.get("version", "?")
            _warn(f"existing Book Kit install detected (version {version})")
            _warn("use --upgrade to refresh; --uninstall to remove cleanly")
        except (OSError, ValueError):
            _warn("manifest.json exists but unreadable; --upgrade may be needed")
    return True


def check_model_config() -> None:
    # ~/.config/opencode/config.json on Linux/macOS, %APPDATA%/opencode/config.json on Windows.
    if os.name == "nt":
        cfg = Path(os.environ.get("APPDATA", str(Path.home()))) / "opencode" / "config.json"
    else:
        cfg = Path.home() / ".config" / "opencode" / "config.json"
    if cfg.exists():
        _ok(f"opencode config: {cfg}")
    else:
        _warn(f"opencode config not found at {cfg}")
        _warn("configure your model provider in OpenCode before launching the pipeline")


def main() -> int:
    target = Path(os.environ.get("BOOK_KIT_TARGET", ".")).resolve()
    print(f"Book Kit doctor — target: {target}")
    print()

    results = [
        check_python(),
        check_opencode(),
        check_git(),
        check_write(target),
        check_disk(target),
        check_existing_kit(target),
    ]
    check_model_config()
    print()

    if all(results):
        print("all required checks passed.")
        return 0
    print("one or more required checks FAILED — see hints above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())