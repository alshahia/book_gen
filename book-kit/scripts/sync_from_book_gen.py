#!/usr/bin/env python3
"""Sync book_gen/ source-of-truth paths to book-kit/.

Stdlib only. Default = dry-run; pass --apply to write.

Source-of-truth root:    E:\\book_gen
Book-kit (distribution): E:\\book_gen\\book-kit

Exits:
  0 = success (also when some source files are absent)
  1 = I/O error during a copy
  2 = invalid args (source-root or kit-root not a directory)
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

# Source-to-kit file pairs. Order is preserved in the output table.
# Strings with glob chars (*, ?, [) expand via Path.glob on the source side;
# the kit side is the parent directory. Glob patterns with no matches yield
# zero rows (a missing-or-empty source dir is not an error).
FILE_PAIRS: list[tuple[str, str]] = [
    # Explicit file-to-file mirrors.
    ("agents_manager/book-gen-orchestrator/SKILL.md",
     "agents_manager/book-gen-orchestrator/SKILL.md"),
    ("agents_manager/book-writer/SKILL.md",
     "agents_manager/book-writer/SKILL.md"),
    # Directory mirrors.
    ("book_workflow/book-agents/templates/*",
     "book_workflow/book-agents/templates/"),
    ("book_workflow/scripts/*.py",
     "book_workflow/scripts/"),
    ("book_workflow/docs/*.md",
     "book_workflow/docs/"),
]

CHUNK = 65536


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def short_sha(s: str, n: int = 12) -> str:
    return s[:n] if len(s) > n else s


def expand_pairs(src_root: Path, kit_root: Path):
    """Yield (rel_kit_path, src_path, kit_path) for every matched source file."""
    for src_pat, kit_pat in FILE_PAIRS:
        is_glob = any(ch in src_pat for ch in "*?[")
        if is_glob:
            src_parent = src_root / Path(src_pat).parent.as_posix()
            if not src_parent.is_dir():
                continue
            kit_subdir = kit_root / kit_pat
            for src in sorted(src_parent.glob(Path(src_pat).name)):
                if src.is_file():
                    yield (kit_subdir / src.name).relative_to(kit_root).as_posix(), src, kit_subdir / src.name
        else:
            src = src_root / src_pat
            kit = kit_root / kit_pat
            yield kit.relative_to(kit_root).as_posix(), src, kit


def sync_one(src: Path, kit: Path, apply: bool) -> tuple[str, str, str, str]:
    """Returns (action, src_sha, kit_sha, note)."""
    if not src.exists():
        return ("MISSING", "-", "-", "source absent")
    src_sha = sha256(src)
    if not kit.exists():
        note = "created" if apply else "would create"
        if apply:
            kit.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, kit)
        return ("COPY", src_sha, "-", note)
    kit_sha = sha256(kit)
    if src_sha == kit_sha:
        return ("SKIP", src_sha, kit_sha, "in sync")
    note = "overwritten" if apply else "would overwrite"
    if apply:
        shutil.copy2(src, kit)
    return ("UPDATE", src_sha, kit_sha, note)


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync book_gen/ to book-kit/.")
    ap.add_argument("--apply", action="store_true",
                    help="Write changes (default = dry-run).")
    ap.add_argument("--source-root", default=r"E:\book_gen",
                    help="Source-of-truth root (default: E:\\book_gen).")
    ap.add_argument("--kit-root", default=r"E:\book_gen\book-kit",
                    help="Book-kit root (default: E:\\book_gen\\book-kit).")
    args = ap.parse_args()

    src_root = Path(args.source_root)
    kit_root = Path(args.kit_root)
    if not src_root.is_dir():
        print(f"ERROR: source-root not a directory: {src_root}", file=sys.stderr)
        return 2
    if not kit_root.is_dir():
        print(f"ERROR: kit-root not a directory: {kit_root}", file=sys.stderr)
        return 2

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] source={src_root}  kit={kit_root}")
    header = f"{'STATUS':<8}  {'KIT PATH':<58}  {'SRC SHA':<14}  {'KIT SHA':<14}  NOTE"
    print(header)
    print("-" * len(header))

    counts = {"COPY": 0, "UPDATE": 0, "SKIP": 0, "MISSING": 0}
    try:
        for rel, src, kit in expand_pairs(src_root, kit_root):
            action, src_sha, kit_sha, note = sync_one(src, kit, args.apply)
            counts[action] += 1
            print(f"{action:<8}  {rel:<58}  {short_sha(src_sha):<14}  {short_sha(kit_sha):<14}  {note}")
    except OSError as e:
        print(f"ERROR: I/O failure during sync: {e}", file=sys.stderr)
        return 1

    print("-" * len(header))
    summary = f"{counts['COPY']} copied, {counts['UPDATE']} updated, {counts['SKIP']} skipped"
    if counts["MISSING"]:
        summary += f", {counts['MISSING']} missing-source"
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
