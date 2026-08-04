#!/usr/bin/env python3
"""Smoke test for the Book Kit installer.

Phase-0-only smoke: install into a temp project, validate the installer exit
code, validate the installed file tree, and verify that re-running the
installer reports idempotent behavior. Does NOT launch OpenCode (requires
a model provider + per-host setup).

Stdlib only. Run from the kit root: python scripts/smoke_test.py

Exit 0 = pass; non-zero = at least one assertion failed.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
INSTALL = KIT / "install.py"
EXPECTED_FILES = [
    "opencode.jsonc",
    "CLAUDE.md",
    "VERSION",
    ".gitattributes",
    "install.py",
    "manifest.json",
    ".book-kit-version",
    "agents_manager/master/SKILL.md",
    "agents_manager/book-gen-orchestrator/SKILL.md",
    "agents_manager/book-writer/SKILL.md",
    "agents_manager/research/SKILL.md",
    "agents_manager/planning/SKILL.md",
    "agents_manager/design/SKILL.md",
    "agents_manager/coder/SKILL.md",
    "agents_manager/review/SKILL.md",
    "book_workflow/book-agents/templates/intake.md",
    "book_workflow/book-agents/templates/skeleton.md",
    "book_workflow/book-agents/templates/research-log.md",
    "book_workflow/book-agents/templates/outline.md",
    "book_workflow/book-agents/templates/style-guide.md",
    "book_workflow/book-agents/templates/writing-plan.md",
    "book_workflow/book-agents/templates/bible.md",
    "book_workflow/book-agents/templates/ledger.md",
    "book_workflow/book-agents/templates/decisions-log.md",
    "books/",
    "tasks/",
    "share/notes/",
    "share/handoffs/",
    "share/reports/",
]


def _step(label: str) -> None:
    print(f"  [step] {label}")


def _assert(cond: bool, msg: str) -> None:
    if cond:
        print(f"    [OK]   {msg}")
    else:
        print(f"    [FAIL] {msg}")
        raise AssertionError(msg)


def run(cmd: list, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main() -> int:
    print("Book Kit smoke test")
    print(f"kit: {KIT}")
    print()

    tmp = Path(tempfile.mkdtemp(prefix="book-kit-smoke-"))
    try:
        target = tmp / "project"
        target.mkdir()
        _step(f"install into fresh target {target}")
        r = run([sys.executable, str(INSTALL), "--target", str(target), "--no-doctor"], KIT)
        _assert(r.returncode == 0, f"installer exit 0 (got {r.returncode})")
        if r.returncode != 0:
            print(r.stdout)
            print(r.stderr, file=sys.stderr)
            return 1

        _step("verify expected files present")
        for rel in EXPECTED_FILES:
            p = target / rel
            _assert(p.exists(), f"{rel} exists")

        _step("verify user-protected dir empty by default")
        books = target / "books"
        _assert(books.is_dir() and not any(books.iterdir()), "books/ exists and is empty")

        _step("re-run installer (idempotency)")
        r2 = run([sys.executable, str(INSTALL), "--target", str(target), "--no-doctor"], KIT)
        _assert(r2.returncode == 0, f"second install exit 0 (got {r2.returncode})")
        _assert("skip" in r2.stdout.lower(), "second install reported skip behavior")

        _step("user adds a book; rerun does not clobber")
        user_file = books / "my-book" / "intake.md"
        user_file.parent.mkdir(parents=True, exist_ok=True)
        user_file.write_text("# user content — do not touch\n", encoding="utf-8")
        r3 = run([sys.executable, str(INSTALL), "--target", str(target), "--no-doctor"], KIT)
        _assert(r3.returncode == 0, f"third install exit 0 (got {r3.returncode})")
        _assert(
            user_file.read_text(encoding="utf-8").startswith("# user content"),
            "user-created books/<slug>/intake.md preserved",
        )

        _step("--upgrade preserves user content, overwrites engine")
        engine_file = target / "CLAUDE.md"
        original = engine_file.read_text(encoding="utf-8")
        # Simulate user edit to CLAUDE.md (engine-owned)
        engine_file.write_text("USER EDITED\n", encoding="utf-8")
        r4 = run(
            [sys.executable, str(INSTALL), "--target", str(target), "--no-doctor", "--upgrade"],
            KIT,
        )
        _assert(r4.returncode == 0, f"--upgrade exit 0 (got {r4.returncode})")
        # Engine file should be restored to original
        _assert(
            engine_file.read_text(encoding="utf-8") == original,
            "engine CLAUDE.md overwritten on --upgrade",
        )
        _assert(
            any(target.glob("CLAUDE.md.bak.*")),
            "user edit backed up to CLAUDE.md.bak.*",
        )
        # User file still preserved
        _assert(
            user_file.read_text(encoding="utf-8").startswith("# user content"),
            "user-created books/<slug>/intake.md still preserved after --upgrade",
        )

        _step("--uninstall removes engine, preserves user content")
        r5 = run(
            [sys.executable, str(INSTALL), "--target", str(target), "--uninstall"],
            KIT,
        )
        _assert(r5.returncode == 0, f"--uninstall exit 0 (got {r5.returncode})")
        _assert(not (target / "opencode.jsonc").exists(), "opencode.jsonc removed")
        _assert(
            user_file.read_text(encoding="utf-8").startswith("# user content"),
            "user file still preserved after --uninstall",
        )

        print()
        print("SMOKE TEST: PASS")
        return 0
    except AssertionError as e:
        print()
        print(f"SMOKE TEST: FAIL — {e}")
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())