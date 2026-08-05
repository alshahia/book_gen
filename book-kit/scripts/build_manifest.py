#!/usr/bin/env python3
"""Regenerate book-kit/manifest.json from the current book-kit/ tree.

Walks the engine file allowlist, computes SHA-256 for each entry, and writes
a manifest the installer and build_zip.py both consume.

Stdlib only. Run from repo root: python book-kit/scripts/build_manifest.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

# ponytail: glob expansion so ENGINE_FILES can mix explicit paths and globs.
_GLOB_CHARS = ("*", "?", "[")

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT  # the book-kit/ tree itself
VERSION_FILE = KIT / "VERSION"
MANIFEST = KIT / "manifest.json"

# Engine-owned files: installer overwrites on upgrade (after warning).
ENGINE_FILES = [
    "opencode.jsonc",
    "CLAUDE.md",
    "VERSION",
    ".gitattributes",
    "install.py",
    "manifest.json",
    "README.md",
    "CONTRIBUTING.md",
    "bin/book-kit",
    "bin/book-kit.cmd",
    "bin/install-book-kit.bat",
    "scripts/doctor.py",
    "scripts/build_manifest.py",
    "scripts/build_zip.py",
    "scripts/smoke_test.py",
    "agents_manager/master/SKILL.md",
    "agents_manager/book-gen-orchestrator/SKILL.md",
    "agents_manager/book-writer/SKILL.md",
    "agents_manager/book-reviewer/SKILL.md",
    "agents_manager/research/SKILL.md",
    "agents_manager/planning/SKILL.md",
    "agents_manager/design/SKILL.md",
    "agents_manager/coder/SKILL.md",
    "agents_manager/review/SKILL.md",
    "book_workflow/scripts/*.py",
    "book_workflow/docs/*.md",
    "book_workflow/book-agents/templates/*.json",
    "book_workflow/book-agents/templates/*.md",
    "docs/QUICKSTART.md",
    "docs/ARCHITECTURE.md",
    "docs/TROUBLESHOOTING.md",
    "docs/UPGRADE.md",
]

# User-owned files: installer preserves with .userbak suffix if hash differs.
USER_FILES = [
    "books/",
    "tasks/",
    "share/notes/",
    "share/handoffs/",
    "share/reports/",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build() -> int:
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    entries = []
    missing = []
    # Expand glob entries (e.g. "book_workflow/scripts/*.py") into concrete
    # file paths. Non-glob entries pass through unchanged. Sort glob matches
    # so the manifest order is deterministic across builds.
    expanded: list[str] = []
    for rel in ENGINE_FILES:
        if any(c in rel for c in _GLOB_CHARS):
            for p in sorted(KIT.glob(rel)):
                if p.is_file():
                    expanded.append(p.relative_to(KIT).as_posix())
        else:
            expanded.append(rel)
    for rel in expanded:
        p = KIT / rel
        if not p.exists():
            missing.append(rel)
            continue
        entries.append(
            {
                "path": rel.replace("\\", "/"),
                "engine_owned": True,
                "sha256": sha256(p),
            }
        )

    user_entries = [{"path": u, "engine_owned": False} for u in USER_FILES]

    manifest = {
        "name": "book-kit",
        "version": version,
        "min_python": "3.8",
        "engine_files": entries,
        "user_files": user_entries,
    }

    # Bootstrap: include manifest.json in its own allowlist so the installer
    # can validate it on first run. Hash computed from the JSON we are about
    # to write (idempotent re-runs converge to the same sha).
    bootstrap = dict(manifest)
    bootstrap["engine_files"] = list(entries) + [
        {"path": "manifest.json", "engine_owned": True, "sha256": "PENDING"}
    ]
    rendered = json.dumps(bootstrap, indent=2, sort_keys=False) + "\n"
    pending_sha = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    bootstrap["engine_files"][-1]["sha256"] = pending_sha
    rendered = json.dumps(bootstrap, indent=2, sort_keys=False) + "\n"
    final_sha = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    if final_sha == pending_sha:
        manifest = bootstrap

    MANIFEST.write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    if missing:
        print(f"ERROR: {len(missing)} engine files missing:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        return 1

    print(f"manifest.json: {len(entries)} engine files, version {version}")
    return 0


if __name__ == "__main__":
    sys.exit(build())