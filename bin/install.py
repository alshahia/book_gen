#!/usr/bin/env python3
"""install.py — Convenience launcher for the in-repo installer.

This file is intentionally tiny.  Its only jobs:
  1. Print a friendly banner.
  2. Launch agents-manager.py (same dir) with --menu.
"""

import importlib.util
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
        sys.stderr.write(
            f"agents-manager.py not found next to install.py ({BIN_DIR})\n"
        )
        return 1
    # Inject "--menu" so the user gets the 5-option menu by default.
    sys.argv = [str(AM_PY), "--menu"] + sys.argv[1:]
    sys.path.insert(0, str(BIN_DIR))
    spec = importlib.util.spec_from_file_location("agents_manager_py", AM_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.main() or 0


if __name__ == "__main__":
    sys.exit(main())
