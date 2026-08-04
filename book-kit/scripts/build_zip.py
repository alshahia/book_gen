#!/usr/bin/env python3
"""Assemble book-kit-<version>.zip from the manifest allowlist.

Reads manifest.json, pulls each engine_file from the kit tree, normalizes
EOL per the .gitattributes rules, and writes a deterministic ZIP to dist/.

Stdlib only. Run from repo root: python book-kit/scripts/build_zip.py
"""

from __future__ import annotations

import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT  # the book-kit/ tree is the build source
MANIFEST = KIT / "manifest.json"
VERSION = KIT / "VERSION"
DIST = ROOT.parent / "dist"  # E:\book_gen\dist
GITATTRIBUTES = KIT / ".gitattributes"

# Mirror of .gitattributes: (glob, eol). Sorted longest-first.
EOL_RULES: list[tuple[str, str]] = [
    ("*.md", "lf"),
    ("*.json", "lf"),
    ("*.jsonc", "lf"),
    ("*.yaml", "lf"),
    ("*.yml", "lf"),
    ("*.py", "lf"),
    ("*.sh", "lf"),
    ("*.ps1", "crlf"),
    ("*.cmd", "crlf"),
    ("*.bat", "crlf"),
    ("install-book-kit.bat", "crlf"),
]


def normalize_eol(content: bytes, rel: str) -> bytes:
    target = None
    for pattern, eol in EOL_RULES:
        if _glob_match(pattern, rel):
            target = eol
            break
    if target is None:
        return content
    text = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if target == "crlf":
        text = text.replace(b"\n", b"\r\n")
    return text


def _glob_match(pattern: str, rel: str) -> bool:
    import fnmatch
    return fnmatch.fnmatch(rel, pattern)


def build() -> int:
    if not MANIFEST.exists():
        print("ERROR: run build_manifest.py first", file=sys.stderr)
        return 1
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    version = VERSION.read_text(encoding="utf-8").strip()

    DIST.mkdir(parents=True, exist_ok=True)
    out_path = DIST / f"book-kit-{version}.zip"

    # All kit files live under a "book-kit/" prefix inside the ZIP so the
    # archive always unpacks into a self-contained subdirectory. Without
    # this, unzipping into a project puts install.py at the project root
    # and the installer refuses to run ("target resolves to the kit root").
    zip_prefix = "book-kit"

    files_added = 0
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for entry in manifest["engine_files"]:
            rel = entry["path"]
            src = KIT / rel
            if not src.exists():
                print(f"ERROR: missing {rel}", file=sys.stderr)
                return 1
            data = normalize_eol(src.read_bytes(), rel)
            zf.writestr(f"{zip_prefix}/{rel}", data)
            files_added += 1

        # Empty user-owned dirs preserved via .gitkeep, also wrapped
        for entry in manifest["user_files"]:
            rel = entry["path"].rstrip("/")
            keep = KIT / rel / ".gitkeep"
            if keep.exists():
                zf.writestr(f"{zip_prefix}/{rel}/.gitkeep", keep.read_bytes())
                files_added += 1

        # Top-level pointer so users can find docs from the extraction root
        zf.writestr(
            f"{zip_prefix}/START_HERE.md",
            (
                "# Book Kit\n\n"
                f"This folder is the Book Kit v{version}.\n\n"
                "To install into a project, run from THIS folder:\n\n"
                "    py book-kit\\install.py\n\n"
                "Or on Windows, double-click `bin\\install-book-kit.bat`.\n"
                "See `book-kit/docs/QUICKSTART.md` for the full walkthrough.\n"
            ).encode("utf-8"),
        )
        files_added += 1

    print(f"wrote {out_path} ({files_added} entries, version {version})")
    return 0


if __name__ == "__main__":
    sys.exit(build())